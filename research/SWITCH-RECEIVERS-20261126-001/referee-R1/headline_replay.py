"""Regrow the cap-of-three census and compare its counts and birth descriptions."""

import argparse
from collections import Counter, defaultdict
from functools import cache
import gzip
from itertools import permutations
import json
from pathlib import Path
import random
from time import perf_counter

from census import (KNOT_LIMIT, PAIRS, ROUND_LIMIT, SENDERS, Panel, alternating, band,
                    first_difference, first_present, parse_start, sender_classes, sha256)
import growth


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'receivers_runs.jsonl.gz'
STEPS = (3, 2, 4, 5)
SEED = 20261126
LAW = 'CAP-3'
TWO_LOOSE = 'g3:22@0'
REFERENCE = 'n3:g7:122@0'


def archive():
    by_step = defaultdict(list)
    with gzip.open(SOURCE, 'rt') as stream:
        for row in map(json.loads, stream):
            if row['law'] == LAW:
                panel = Panel.read(row)
                by_step[panel.d].append(panel)
    for d in STEPS:
        by_step[d].sort(key=lambda p: p.name)
        assert len({p.name for p in by_step[d]}) == len(by_step[d]) == 646
    return by_step


def regenerate(panel):
    return {s: growth.grow(panel.name, s, panel.d, LAW, rounds=ROUND_LIMIT, bound=KNOT_LIMIT) for s in SENDERS}


def audit(panel, traces, check):
    ends = {s: len(trace) for s, trace in traces.items()}
    signatures = {s: tuple(row.own_signature for row in trace) for s, trace in traces.items()}
    shorts = {s: tuple(row.own_short for row in trace) for s, trace in traces.items()}
    common = min(ends.values())
    pair_firsts = {(a, b): first_difference(signatures[a], signatures[b]) for a, b in PAIRS}
    count_pair_firsts = {
        (a, b): first_difference(tuple(row.own_births for row in traces[a]),
                                 tuple(row.own_births for row in traces[b]))
        for a, b in PAIRS
    }
    is_late = lambda first: first is not None and first > 2 * panel.d

    def no_short_before(first, senders):
        return all(not any(shorts[s][:first - 1]) for s in senders)

    for s, trace in traces.items():
        check(s, 'recorded rounds', ends[s], panel.lengths[s])
        check(s, 'final knots', trace[-1].knots, panel.knots[s])
        for field, actual, saved in [('own birth counts', tuple(row.own_births for row in trace), panel.births[s]),
                                     ('own short counts', shorts[s], panel.shorts[s])]:
            for r, (grown, prior) in enumerate(zip(actual, saved), 1):
                check(s, field, grown, prior, r)
        check(s, 'stub first difference', first_difference(signatures[s], signatures['stub']),
              panel.stored_stub_firsts[s])
    check(None, 'all-five window', common, panel.common)
    check(None, 'sender classes', sender_classes(tuple(signatures[s][:common] for s in SENDERS)), panel.stored_classes)
    pair_first = first_present(pair_firsts.values())
    common_first = pair_first if pair_first is not None and pair_first <= common else None
    check(None, 'all-five first difference', common_first, panel.stored_first)
    if common_first is not None and panel.stored_first is not None:
        check(None, 'prior own shortness', not no_short_before(common_first, SENDERS),
              not panel.no_prior_short(panel.stored_first))
    common_switch = is_late(common_first) and no_short_before(common_first, SENDERS)
    witness_pairs = [pair for pair, first in pair_firsts.items() if is_late(first) and no_short_before(first, pair)]
    pair_switch = is_late(pair_first) and any(pair_firsts[pair] == pair_first for pair in witness_pairs)
    if common_switch:
        from_panel_first = [s for s in SENDERS if alternating(shorts[s][common_first - 1:])]
        from_stub_first = [s for s in SENDERS
                           if (r := first_difference(signatures[s], signatures['stub'])) is not None
                           and alternating(shorts[s][r - 1:min(ends[s], ends['stub'])])]
    else:
        from_panel_first = from_stub_first = []
    return {
        'common first': common_first, 'pairwise first': pair_first,
        'pairwise firsts with comparison horizon': {
            ' and '.join(pair): [first, min(ends[s] for s in pair)] for pair, first in pair_firsts.items()},
        'pairs with different firsts from structure and counts': sum(
            pair_firsts[pair] != count_pair_firsts[pair] for pair in PAIRS),
        'common switch': common_switch, 'switch by earliest pair': pair_switch,
        'eligible late pairs': len(witness_pairs),
        'eligible late pair firsts': {' and '.join(pair): pair_firsts[pair] for pair in witness_pairs},
        'alternating from panel first': from_panel_first, 'alternating from own contrast with stub': from_stub_first,
    }


def relabeled_signature(rows, root_labels, intern):
    @cache
    def key(name):
        if name.parents:
            term = (tuple(sorted(key(parent) for parent in name.parents)), name.ordinal)
        else:
            term = ((), root_labels[name.ordinal])
        return intern.setdefault(term, len(intern))

    result = tuple(tuple(sorted((key(knot), fresh, places) for knot, fresh, places in row.own_signature))
                   for row in rows)
    key.cache_clear()
    return result


def first_round_evidence(traces):
    evidence = {}
    for name, cells in sorted(traces.items()):
        groups = defaultdict(list)
        for (d, sender), rows in sorted(cells.items()):
            first = rows[0]
            births = tuple(sorted((tuple(sorted(parent.ordinal for parent in knot.parents)), fresh, places)
                                  for knot, fresh, places in first.own_signature))
            groups[first.own_members, first.own_short, births].append((d, sender))
        evidence[name] = [{'sender and step cells': tested, 'own members': members, 'own short': short,
                           'own births': [{'starting parents': parents, 'fresh distinctions': fresh,
                                           'total places': places} for parents, fresh, places in births]}
                          for (members, short, births), tested in groups.items()]
    return evidence


def compare_receivers(traces):
    """Check one start relabeling across all recorded senders and steps."""
    if REFERENCE not in traces:
        return {}
    reference = traces[REFERENCE]
    intern = {}
    ref_codes = {key: relabeled_signature(rows, (0, 1, 2), intern) for key, rows in reference.items()}
    out = {}
    for name, cells in sorted(traces.items()):
        if name == REFERENCE:
            continue
        parsed = parse_start(name)
        if parsed is None:
            continue
        _, loose, site = parsed
        common = set(cells) & set(reference)
        if not common:
            continue
        candidate_maps = [mapping for mapping in permutations(range(len(loose))) if mapping[site] == 0]
        matching = [list(mapping) for mapping in candidate_maps if all(
            relabeled_signature(cells[key], mapping, intern) == ref_codes[key] for key in common)]
        out[name] = {'comparable sender and step cells': len(common),
                     'root relabelings matching every rebuilt birth description': matching,
                     'all total-knot traces exactly one greater': all(
                         [r.knots for r in cells[key]] == [1 + r.knots for r in reference[key]] for key in common),
                     'all receiver-descended birth counts agree': all(
                         [r.receiver_inclusive_births for r in cells[key]] ==
                         [r.receiver_inclusive_births for r in reference[key]] for key in common),
                     'all own-members counts agree after the first round': all(
                         [r.own_members for r in cells[key][1:]] ==
                         [r.own_members for r in reference[key][1:]] for key in common)}
    return out


def pilot(by_step, seed, sample_size):
    rng = random.Random(seed)
    measures = []
    for d in STEPS:
        panels = by_step[d]
        random_panels = rng.sample(panels, sample_size)
        start_time = perf_counter()
        for panel in random_panels:
            regenerate(panel)
        sample_seconds = perf_counter() - start_time
        stress = [next(p for p in panels if p.name == REFERENCE), max(panels, key=lambda p: sum(p.knots.values()))]
        start_time = perf_counter()
        for panel in stress:
            regenerate(panel)
        measures.append({'d': d, 'seeded receiver panels': sample_size, 'sample seconds': round(sample_seconds, 3),
                         'stress and reference seconds': round(perf_counter() - start_time, 3),
                         'projected full seconds': round(sample_seconds * len(panels) / sample_size, 2)})
    print(json.dumps({'seed': seed, 'pilot': measures,
                      'projected seconds': round(sum(m['projected full seconds'] for m in measures), 2)}, indent=2))


def replay(by_step, steps, complete, sample_size, seed):
    rng = random.Random(seed)
    signature_traces = defaultdict(dict)
    differences = []
    output = {'source': SOURCE.name, 'source sha256': sha256(SOURCE), 'growth sha256': sha256(HERE / 'growth.py'),
              'law': LAW, 'seed': seed, 'round limit': ROUND_LIMIT, 'knot limit': KNOT_LIMIT,
              'comparison': 'Strict own birth descriptions use starting knot labels, recursive parent names, '
                            'birth ordinals, fresh counts and total places. Comparisons use the full descriptions.',
              'steps': {}, 'archive differences': differences}
    for d in steps:
        panels = by_step[d]
        if complete and d not in complete:
            panels = sorted(rng.sample(panels, sample_size), key=lambda p: p.name)
        started = perf_counter()
        checks, common_bands, pair_bands, measures = Counter(), Counter(), Counter(), Counter()
        hits, pair_only = {}, []
        late_after_earlier = {}
        for number, panel in enumerate(panels, 1):
            traces = regenerate(panel)

            def check(sender, field, grown, saved, r=None):
                checks[field] += 1
                if grown != saved:
                    differences.append({'d': d, 'receiver': panel.name, 'sender': sender, 'field': field,
                                        'round': r, 'grown': grown, 'archive': saved})

            result = audit(panel, traces, check)
            common_bands[band(result['common first'], d)] += 1
            pair_bands[band(result['pairwise first'], d)] += 1
            measures['pair first differences missed by all-five window'] += (
                result['pairwise first'] is not None and result['common first'] is None)
            measures['pairs with different firsts from structure and counts'] += (
                result['pairs with different firsts from structure and counts'])
            measures['receivers with any eligible late pair'] += result['eligible late pairs'] > 0
            measures['eligible late pairs'] += result['eligible late pairs']
            measures['switches by earliest pair'] += result['switch by earliest pair']
            if result['switch by earliest pair'] and not result['common switch']:
                pair_only.append(panel.name)
            if result['eligible late pairs'] and not result['switch by earliest pair']:
                late_after_earlier[panel.name] = {'earliest first': result['pairwise first'],
                                                'later pairs': result['eligible late pair firsts']}
            if result['common switch']:
                hits[panel.name] = result
                for sender, trace in traces.items():
                    signature_traces[panel.name][d, sender] = trace
            if number % 100 == 0:
                print(f'{d} steps: {number} of {len(panels)} receiver panels', flush=True)
        output['steps'][d] = {'receiver panels rebuilt': len(panels), 'receiver panels not rebuilt': 646 - len(panels),
                              'receiver IDs when sampled': [p.name for p in panels] if len(panels) != 646 else None,
                              'sender run count': len(panels) * len(SENDERS), 'checks': checks,
                              'common first difference bands': common_bands, 'pairwise first difference bands': pair_bands,
                              'pair measures': measures, 'pair-only switches': pair_only, 'switches': hits,
                              'earlier first difference with some eligible late pairs': late_after_earlier,
                              'switches with alternating arm from panel first': sum(
                                  bool(case['alternating from panel first']) for case in hits.values()),
                              'switches with two-loose sender alternating from its own contrast': sum(
                                  TWO_LOOSE in case['alternating from own contrast with stub'] for case in hits.values()),
                              'switches with any sender alternating from its own contrast': sum(
                                  bool(case['alternating from own contrast with stub']) for case in hits.values()),
                              'elapsed seconds': round(perf_counter() - started, 3)}
        print(f'{d} steps: finished {len(panels)} receiver panels', flush=True)
    output['structure of switch receivers compared with three-knot reference'] = compare_receivers(signature_traces)
    output['first-round birth descriptions of switch receivers'] = first_round_evidence(signature_traces)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', type=int, metavar='PANELS_PER_STEP')
    parser.add_argument('--steps', type=int, choices=STEPS, nargs='+', default=STEPS)
    parser.add_argument('--complete', type=int, choices=STEPS, nargs='+',
                        help='Rebuild all receivers for these steps and a uniform sample for the other selected steps.')
    parser.add_argument('--sample-otherwise', type=int, default=20)
    parser.add_argument('--seed', type=int, default=SEED)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    by_step = archive()
    if args.pilot is not None:
        pilot(by_step, args.seed, args.pilot)
        return
    output = replay(by_step, args.steps, args.complete, args.sample_otherwise, args.seed)
    if args.output is not None:
        args.output.write_text(json.dumps(output, indent=2) + '\n')
    print(len(output['archive differences']), 'archive differences')


if __name__ == '__main__':
    main()
