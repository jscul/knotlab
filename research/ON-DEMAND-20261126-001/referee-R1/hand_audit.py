"""Reconstruct the hand-built starts and compare every possible reach."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, pairwise
import json
from pathlib import Path
import resource
import subprocess
from time import perf_counter

from engine_audit import ROOT, STUDY, file_sha, holdings_growth, join_groups
from growth import Roster, grow


FREEZE = 'de892a09d6'
HORIZON = 8
FULL_CAP = 3000
LAWS = ('nae', 'parity')


@dataclass(frozen=True)
class Case:
    chain: int
    appendage: str
    added: int
    pairs: tuple

    def frozen_name(self):
        return f'{self.appendage}, path of {self.chain}, surplus {self.added}'

    def describe(self):
        return {'shared distinctions in the chain before the end pattern': self.chain,
                'end pattern': self.appendage, 'surplus per knot': self.added}


def fixtures():
    for length in (2, 4, 6, 8):
        chain = tuple(pairwise(range(length + 1)))
        a, b, c, d, e = range(length, length + 5)
        triple = tuple(combinations((a, b, c), 2))
        choices = {
            'a triple': triple,
            'two triples sharing a knot': triple + tuple(combinations((c, d, e), 2)),
            'four touching pairwise': tuple(combinations((a, b, c, d), 2)),
            'a triple at both ends': triple + tuple(combinations((0, d, e), 2)),
        }
        for appendage, end in choices.items():
            for added in (0, 1):
                yield Case(length, appendage, added, chain + end)


def holdings(pairs, sizes):
    stars = [[] for _ in sizes]
    owners = {}
    for d, (a, b) in enumerate(pairs):
        stars[a].append(d)
        stars[b].append(d)
        owners[d] = a, b
    for knot, size in enumerate(sizes):
        while len(stars[knot]) < size:
            next_distinction = len(owners)
            owners[next_distinction] = (knot,)
            stars[knot].append(next_distinction)
    return stars, owners


def make_start(case):
    number = 1 + max(max(pair) for pair in case.pairs)
    shared = Counter(k for pair in case.pairs for k in pair)
    stars, owners = holdings(case.pairs, [shared[k] + 1 for k in range(number)])
    groups = join_groups(stars, owners, range(number))
    demand = Counter(k for group in groups for k in group)
    sizes = [max(3, shared[k] + demand[k]) + case.added for k in range(number)]
    stars, owners = holdings(case.pairs, sizes)
    return Roster.from_graph(sizes, case.pairs), stars, owners


def write_counter(counter):
    return sorted((item, n) for item, n in counter.items())


def measure_regions(roster, full, horizon, law):
    by_region = defaultdict(list)
    reach = {}
    for reader in roster.loose:
        steps = roster.steps_from(reader)
        regions = [frozenset(k for k, d in steps.items() if d <= r) for r in range(max(steps.values()) + 1)]
        reach[reader] = regions
        for count, region in enumerate(regions):
            by_region[region].append((reader, count))
    complete = frozenset(roster.loose)
    full_views = {reader: full.views(reader, horizon) for reader in roster.loose}
    comparisons = {}
    end_counts = Counter()
    for region, pairs in by_region.items():
        if region == complete:
            rollout = full
        else:
            rollout = grow(roster.restrict(region), horizon, law)
        end_counts[rollout.end] += 1
        for reader, count in pairs:
            view = rollout.views(reader, horizon)
            first_difference = next((i for i in range(horizon) if view[i] != full_views[reader][i]), None)
            if first_difference is None:
                measurements = {'first different round': horizon + 1}
            else:
                theirs = full_views[reader][first_difference]
                here = view[first_difference]
                measurements = {
                    'first different round': first_difference + 1,
                    'counts agree in that round': sum(here[0].values()) == sum(theirs[0].values()),
                    'first reading agrees in that round': here[0] == theirs[0],
                    'full first reading': write_counter(theirs[0]),
                    'region first reading': write_counter(here[0]),
                    'full reading with parents': write_counter(theirs[1]),
                    'region reading with parents': write_counter(here[1]),
                    'region end': rollout.end,
                    'region shortages [demand, loose]': rollout.shortages,
                }
            comparisons[reader, count] = measurements
    return comparisons, reach, end_counts


def split_details(stars, owners, active, region, full_groups):
    splits = [group for group in full_groups if len(group) >= 3 and set(group) & region and not set(group) <= region]
    region_groups = join_groups(stars, owners, sorted(region))
    full_uses = Counter(k for group in full_groups for k in group)
    region_uses = Counter(k for group in region_groups for k in group)
    all_split_members = {k for group in splits for k in group if k in region}
    gains = [k for k in sorted(all_split_members) if full_uses[k] > region_uses[k]]
    return {
        'split groups of at least three': splits,
        'inside and outside counts of those groups': sorted((len(set(g) & region), len(set(g) - region)) for g in splits),
        'all kept members of split groups gain offshoots': bool(splits) and set(gains) == all_split_members,
        'kept members of split groups gaining offshoots': gains,
        'new first-round groups inside the region': sorted(set(region_groups) - set(full_groups)),
        'first-round groups retained': sorted(set(region_groups) & set(full_groups)),
        'region live knots': sorted(region), 'all live knots': sorted(active),
    }


def as_presentation(stars, owners, region):
    # Leave the outside knots as dead holders of their original shared distinctions.
    # Give each undersized dead holder three places shared with a new dead knot.
    result = [[d for d in star if len(owners[d]) == 2 or k in region] for k, star in enumerate(stars)]
    next_distinction = len(owners)
    for knot in range(len(stars)):
        if knot not in region and len(result[knot]) < 3:
            filler = list(range(next_distinction, next_distinction + 3))
            result[knot].extend(filler)
            result.append(filler)
            next_distinction += 3
    return result


def witness(case, law, roster, stars, owners, region, reader, t, least, agreeing, downstream, full_groups):
    short_stars = as_presentation(stars, owners, region)
    short_roster = Roster.from_holdings(short_stars)
    assert short_roster == roster.restrict(region)
    first = downstream['first different round']
    holdings_full, _, _ = holdings_growth(stars, law, first, reader=reader)
    holdings_cut, holds_end, _ = holdings_growth(short_stars, law, first, reader=reader)
    matched = len(holdings_full) == first and holdings_full[:first - 1] == holdings_cut[:first - 1]
    assert matched and write_counter(holdings_full[-1][0]) == downstream['full first reading']
    assert write_counter(holdings_full[-1][1]) == downstream['full reading with parents']
    cut_first, cut_second = holdings_cut[first - 1] if len(holdings_cut) == first else (Counter(), Counter())
    assert write_counter(cut_first) == downstream['region first reading']
    assert write_counter(cut_second) == downstream['region reading with parents']
    return {'start': case.describe(), 'starting holdings': stars, 'shared pairs': case.pairs,
            'places': list(map(len, stars)), 'steps to each live knot in the joins map': roster.steps_from(reader),
            'reader knot': reader, 'read through round': t, 'least successful reach': least,
            'successful reaches up to the full reader set': agreeing, 'knots within t + 1 steps': sorted(region),
            'explicit holdings of short start': short_stars,
            'full and cut views verified from holdings': True,
            'first-round group changes': split_details(stars, owners, roster.loose, region, full_groups),
            'holdings growth end in the cut by the first differing round': holds_end, **downstream}


def read_case(case, law, roster, stars, owners):
    result = Counter()
    result['starts'] = 1
    full = grow(roster, HORIZON, law, cap=FULL_CAP)
    if full.end == 'stall':
        result['stalls'] = 1
        return result, {}, [], [], [], {}, full.end
    horizon = len(full.rows) if full.end == 'cap' else HORIZON
    result['eligible starts'] = 1
    result['live readers'] = len(roster.loose)
    result['full growth actually produced rounds'] = len(full.rows)
    result['largest full round birth count'] = max(map(len, full.rows), default=0)
    result['full growths cut by the per-round cap'] = full.end == 'cap'
    result['full growths closed'] = full.end == 'closed'
    cases, reaches, ends = measure_regions(roster, full, horizon, law)
    split_types = Counter()
    first_differences = Counter()
    strict_errors = []
    minima_errors = []
    failed_reach = []
    full_groups = join_groups(stars, owners, roster.loose)
    complete = frozenset(roster.loose)
    for reader in sorted(roster.loose):
        regions = reaches[reader]
        last = len(regions) - 1
        for t in range(1, horizon + 1):
            selected = min(t, last)
            successor = min(t + 1, last)
            from_start = cases[reader, selected]
            next_step = cases[reader, successor]
            agreeing = [s for s in range(last + 1) if cases[reader, s]['first different round'] > t]
            least = min(agreeing, default=None)
            accurate = from_start['first different round'] > t
            adequate = next_step['first different round'] > t
            result['eligible reader-round pairs'] += 1
            result['within t + 1 agrees'] += adequate
            result['within t agrees'] += accurate
            result['least successful reach is at most t'] += least is not None and least <= t
            result['least successful reach is exactly t + 1'] += least == t + 1
            result['no successful reach in the reader set'] += least is None
            result['within t + 1 checks a strict subset of the live roster'] += regions[successor] != complete
            result['within t checks a strict subset of the live roster'] += regions[selected] != complete
            if least is None or least > t:
                minima_errors.append([case.frozen_name(), law, reader, t, least, last])
            if not adequate:
                failed_reach.append(witness(case, law, roster, stars, owners, regions[successor], reader, t,
                                            least, agreeing, next_step, full_groups))
            if accurate:
                continue
            detail = split_details(stars, owners, roster.loose, regions[selected], full_groups)
            first_only = {key: value for key, value in from_start.items()
                          if key not in ('full reading with parents', 'region reading with parents')}
            strict_errors.append({'start': case.describe(), 'reader knot': reader, 'read through round': t,
                                  'least successful reach': least, 'additional step returns the full roster':
                                      regions[successor] == complete, **first_only, **detail})
            result['within t disagrees despite some smaller successful reach'] += least is not None and least < t
            result['within t failures with a split first-round group of at least three'] += bool(
                detail['split groups of at least three'])
            result['within t failures with any split-group member gaining offshoots'] += bool(
                detail['kept members of split groups gaining offshoots'])
            result['within t failures with every kept split-group member gaining offshoots'] += detail[
                'all kept members of split groups gain offshoots']
            result['within t failures repaired in a strict subset of the whole roster'] += (
                adequate and regions[successor] != complete)
            result['within t failures with the same total births at the first difference'] += from_start[
                'counts agree in that round']
            result['within t failures with just the parent reading different at first'] += from_start[
                'first reading agrees in that round']
            first_differences[from_start['first different round']] += 1
            split_types[tuple(detail['inside and outside counts of those groups'])] += 1
    diagnostic = {'first difference at each round': dict(first_differences),
                  'split compositions [kept, omitted]': write_counter(split_types)}
    return result, diagnostic, minima_errors, strict_errors, failed_reach, ends, full.end


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    limit = 2 << 30
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    start_time = perf_counter()
    cases = list(fixtures())
    archive = STUDY / 'handtest.json'
    saved = json.loads(archive.read_text())
    saved_history = subprocess.check_output(['git', 'show', f'{FREEZE}:{archive.relative_to(ROOT)}'], cwd=ROOT)
    assert saved_history == archive.read_bytes()
    file_list = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', FREEZE, str(STUDY.relative_to(ROOT))],
                                        cwd=ROOT, text=True).splitlines()
    document = {'pilot': args.pilot, 'full growth cap in births per round': FULL_CAP,
                'frozen hand-test data SHA-256': file_sha(archive), 'original growth horizon': HORIZON,
                'recorded keys': sorted(saved), 'freeze files about exploration': [p for p in file_list if 'explor' in p],
                'starts': []}
    counts = {law: Counter() for law in LAWS}
    ends = {law: Counter() for law in LAWS}
    minima_errors = []
    strict_errors = {law: [] for law in LAWS}
    failed_reach = {law: [] for law in LAWS}
    laws_agree = 0
    if args.pilot:
        cases = [c for c in cases if c.appendage == 'four touching pairwise'
                 and ((c.chain == 4 and not c.added) or (c.chain == 8 and c.added))]
    for case in cases:
        began = perf_counter()
        roster, stars, owners = make_start(case)
        output = {'start': case.describe(), 'places': list(map(len, stars)), 'shared pairs': case.pairs, 'laws': {}}
        minima = {}
        exact_failures = {}
        for law in LAWS:
            result, diagnostic, least_errors, strict, missed, region_ends, full_end = read_case(
                case, law, roster, stars, owners)
            maxima = result.pop('largest full round birth count', 0)
            counts[law].update(result)
            counts[law]['largest full round birth count'] = max(counts[law]['largest full round birth count'], maxima)
            ends[law].update(region_ends)
            minima_errors.extend(least_errors)
            strict_errors[law].extend(strict)
            failed_reach[law].extend(missed)
            minima[law] = [r[2:] for r in least_errors]
            exact_failures[law] = [(r['reader knot'], r['read through round']) for r in strict]
            output['laws'][law] = {'counts': result, 'region ends': dict(region_ends),
                                   'whole growth end': full_end, **diagnostic}
        laws_agree += minima['nae'] == minima['parity'] and exact_failures['nae'] == exact_failures['parity']
        output['seconds'] = round(perf_counter() - began, 4)
        document['starts'].append(output)
        if args.pilot:
            print(f'{case.frozen_name()}: {output["seconds"]}s', flush=True)
    document['counts by law'] = counts
    document['regional end counts by law'] = ends
    document['starts with identical least-reach and exact-t failure cases under both laws'] = laws_agree
    document['first 30 least-reach failures match the frozen archive'] = minima_errors[:30] == saved['differ (first 30)']
    document['exact-t+1 disagreement witnesses by law'] = failed_reach
    document['exact-t disagreement details by law'] = strict_errors
    if not args.pilot:
        assert document['first 30 least-reach failures match the frozen archive']
        for law in LAWS:
            assert counts[law]['least successful reach is at most t'] == saved['tally'][f'{law} / the knots within t steps suffice']
            assert counts[law]['least successful reach is exactly t + 1'] == saved['tally'][f'{law} / the knots within t + 1 steps needed']
    document['total seconds'] = round(perf_counter() - start_time, 4)
    args.output.write_text(json.dumps(document, indent=2) + '\n')


if __name__ == '__main__':
    main()
