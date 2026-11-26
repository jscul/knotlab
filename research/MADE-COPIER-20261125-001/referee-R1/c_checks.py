"""Reproduce the disclosed gate and controls, audit renaming and trace the equal-form case.

Run from the repository root with the workspace interpreter and -B.
Use --part for an individual check and --pilot to time representative prefixes.
"""

import argparse
import itertools
import json
import random
import resource
import time
from collections import Counter, defaultdict
from decimal import Decimal, localcontext

import networkx as nx

from c_checks_growth import State, events, grow, initial_sides, start_from_counts
from c_checks_records import (ATLAS, DATA, HERE, RAW, ROOT, census, counterexamples, gate_calls,
                              fisher, lines, r7, r8, read_json)


LIST = read_json(DATA / 'cases_c.json')
CASES = LIST['cases']
STARTS = {r['id']: r for r in read_json(DATA / 'starts_c.json')['starts']}
DESIGNS = read_json(ROOT / 'research' / 'MADE-COPIER-20261125-001A' / 'starts.json')['designs']
KINDS = ('BN', 'BY', 'BX', 'BM', 'BT')


def base(c, rounds=6, bound=300, take='MET'):
    if c.get('design'):
        rows = tuple(map(frozenset, DESIGNS[c['design']]['stars']))
        start = State(rows, ((),) * len(rows), (0,) * len(rows), ('start',) * len(rows))
    else:
        e = STARTS[c['start']]
        start = start_from_counts(ATLAS[e['g']], e['loose'])
    return [start] + grow(start, 0, rounds, bound, c, random.Random(c['generator']), take=take)


def follow(ref, c, kind, index, rounds, bound, take):
    seed = f"{c['generator']}|{kind}|{c['s']}|{index}"
    state = ref
    if kind in ('BX', 'BY'):
        state = ref.bar(c[kind[1]])
    states = grow(state, c['s'], rounds, bound, c, random.Random(seed),
                  initial_sides(ref, c), kind in ('BM', 'BT'), kind == 'BT', take)
    return events(ref, states, c), seed, c['s'] + len(states)


def scratch_pairs(state):
    parts = state.roster.parts
    graph = nx.Graph()
    graph.add_nodes_from(range(len(parts)))
    seen = {}
    for i, part in enumerate(parts):
        for u in part:
            for d in state.places[u]:
                if d in seen:
                    graph.add_edge(i, seen[d])
                seen[d] = i
    classes = {i: group for group, values in enumerate(nx.connected_components(graph)) for i in values}
    pairs = [(x, y) for i, x in enumerate(parts[:8]) if all(state.made[u] for u in x)
             for j, y in enumerate(parts[:8]) if i != j and classes[i] != classes[j]]
    return pairs[:8]


def gate(pilot):
    source = list(lines(RAW / 'gate_R0_cases.jsonl'))
    by_seed = defaultdict(list)
    for ix, c in enumerate(CASES):
        by_seed[c['generator']].append(ix)
    summary = Counter()
    X_barred = Counter()
    at_round = Counter()
    corrections = {'equal_form': [], 'X_barred_any_descent': []}
    suspect = {}
    for row in (source[:3] if pilot else source):
        seed = row['key'][0]
        selected = by_seed[seed]
        cfg = CASES[selected[0]]
        hist = base(cfg)
        found = []
        for s in range(1, min(5, len(hist) - 1)):
            for X, Y in scratch_pairs(hist[s]):
                summary['ordered_pairs'] += 1
                c = dict(cfg, X=X, Y=Y, s=s, reading='values')
                _, meet, first, after = events(hist[s], hist[s + 1:], c)
                for rd in ('form', 'formany_X', 'both', 'vA', 'vX'):
                    if rd in after:
                        found.append((s, X, Y, rd, meet, first[rd], after[rd]))
                        summary[f'found_{rd}'] += 1
        other = [(c['s'], tuple(c['X']), tuple(c['Y']), c['reading'], c['meet'],
                  c['round_met_any'], c['round_met']) for c in row['cases_found']]
        assert sorted(found) == sorted(other), seed
        summary['disclosed_growths'] += 1
        counts_raw = {(e['s'], tuple(e['X']), tuple(e['Y'])): e for e in row['listed']}
        for ix in selected:
            c = CASES[ix]
            ref = hist[c['s']]
            same, meet, _, after = events(ref, hist[c['s'] + 1:], c)
            rd = 'vA' if c['reading'] == 'values' else ('formany_X' if same else 'form')
            assert c['meeting_round'] == meet and c['round_met'] == after[rd]
            saved = counts_raw[c['s'], tuple(c['X']), tuple(c['Y'])]
            assert same == saved['same_form'] and rd == saved['reading']
            if same:
                corrections['equal_form'].append({'index': ix, 'start': c['start'], 'reading': c['reading']})
            at_round[c['s']] += 1
            bars = Counter()
            for k in ('BY', 'BX'):
                for i in range(20):
                    (_, _, first, _), _, _ = follow(ref, c, k, i, 6, 300, 'MET')
                    summary['disclosed_barred_continuations'] += 1
                    if k == 'BY':
                        bars['Y_barred'] += rd in first
                    else:
                        own = 'Yown_val' if c['reading'] == 'values' else 'Yown_form'
                        bars['X_barred_Y_own'] += own in first
                        bars['X_barred_any_descent'] += 'yform_any' in first
            assert bars['Y_barred'] == saved['Y_barred_met_of_20'] == c['Y_barred_met_of_20']
            assert bars['X_barred_Y_own'] == saved['X_barred_Y_own_of_20']
            assert bars['X_barred_any_descent'] == saved['X_barred_two_of_Y_form_any_descent_of_20']
            if bars['X_barred_Y_own'] != c['X_barred_Y_own_of_20']:
                assert c['reading'] == 'form' and c['X_barred_Y_own_of_20'] == bars['X_barred_any_descent']
                corrections['X_barred_any_descent'].append(ix)
            if c['reading'] == 'form':
                X_barred['records_with_any_descent'] += bars['X_barred_any_descent'] > 0
                X_barred['records_with_Y_only_descent'] += bars['X_barred_Y_own'] > 0
                X_barred['distinct_form_records_with_Y_only_descent'] += not same and bars['X_barred_Y_own'] > 0
                X_barred['events_of_any_descent'] += bars['X_barred_any_descent']
                X_barred['events_of_Y_only_descent'] += bars['X_barred_Y_own']
            if ix == 87:
                suspect = {'index': ix, 's': c['s'], 'start': c['start'], 'X': c['X'], 'Y': c['Y'],
                           'X_form': ref.roster.form(c['X']).signature,
                           'Y_form': ref.roster.form(c['Y']).signature,
                           'meeting_round': meet, 'looser_reading_first_after_meeting': after[rd],
                           'eligible_form': 'form' in after, 'barred_counts': bars}
            summary['disclosed_entries'] += 1
    admissible = [i for i, c in enumerate(CASES) if c['reading'] == 'form']
    chosen = sorted(random.Random('C|R0b|ten').sample(admissible, 10))
    without = sorted(random.Random('C|R0b|ten').sample([i for i in admissible if i != 87], 10))
    assert without == chosen == LIST['R0b']['negative_control_sample']['indices']
    return {'counts': summary, 'disclosed_records_by_round': at_round,
            'X_barred_for_disclosed_form_records': X_barred, 'corrections': corrections, 'disclosed_suspect': suspect,
            'controls_chosen_with_and_without_87': chosen, 'planted_index': LIST['R0b']['planted_case_pair']['index']}


def scratch_values(pilot):
    rows = []
    reported = read_json(RAW / 'gate_R0.json')['values_comparisons']['rows']
    for spec, case in zip(LIST['values_confirmations'], reported, strict=True):
        ix = [i for i, c in enumerate(CASES) if c['reading'] == 'values'][spec['values_case_index']]
        c = CASES[ix]
        ref = base(c, c['s'])[c['s']]
        record = {}
        for kind in KINDS[:4]:
            count = Counter()
            for i in range(1000, 1005 if pilot else 2000):
                (_, meet, first, after), _, _ = follow(ref, c, kind, i, 6, 300, 'MET')
                count['n'] += 1
                count['meet'] += meet is not None
                for rd in ('vA', 'vX', 'Yown_val'):
                    count[f'{rd}_any'] += rd in first
                    count[f'{rd}_after'] += rd in after
            record[kind] = count
        if not pilot:
            here = case['here']
            assert here['nothing_barred_met_after_meeting'] == record['BN']['vA_after']
            assert here['nothing_barred_met_at_any_round'] == record['BN']['vA_any']
            assert here['Y_barred_met'] == record['BY']['vA_any']
            assert here['X_barred_Y_own'] == record['BX']['Yown_val_any']
            assert here['masked_met'] == record['BM']['vA_any']
            assert here['values_both_from_X_only'] == {'nothing barred after the meeting': record['BN']['vX_after'],
                                                      'masked': record['BM']['vX_any']}
            assert all(here[k] == v for k, v in spec.items() if k in here and k != 'continuations')
            assert all(record[k]['n'] == spec['continuations'] for k in KINDS[:4])
            assert all(here['meetings'][k] == v['meet'] for k, v in record.items())
        rows.append({'source_index': ix, 'start': c['start'], 'counts': record})
    return rows


def prepared_control(row):
    if row['type'] == 'case':
        return dict(CASES[row['index']]), 'MET'
    ration, treatment, _, take, parity, _ = row['law'].split('/')
    design = row['design']
    cfg = dict(DESIGNS[design], design=design, ration=ration, treatment=treatment,
               knot_law=parity, reading='values',
               generator=f'C|A|{design}|{ration}|{treatment}|{take}|parity|0')
    return cfg, take


def controls(pilot):
    recorded = read_json(RAW / 'controls_R0b.json')['controls']
    records = []
    for j, row in enumerate(recorded):
        cfg, take = prepared_control(row)
        ref = base(cfg, cfg['s'], 500, take)[cfg['s']]
        X, Y = ref.roster.form(cfg['X']), ref.roster.form(cfg['Y'])
        assert X.matches(Y) == row['same_form']
        if row['group'] == 'machinery':
            rates = []
            for lo, hi, label in ((0, 100, 'at 100'), (100, 1100, 'at 1,000')):
                hits = []
                for kind in ('BN', 'BY'):
                    n = min(hi - lo, 3) if pilot else hi - lo
                    hit = sum('Yown_val' in follow(ref, cfg, kind, i, 8, 500, take)[0][2]
                              for i in range(lo, lo + n))
                    hits.append(hit)
                p = fisher(hits[0], n, hits[1], n)
                if not pilot:
                    assert row[label]['nothing barred'] == [hits[0], n] and row[label]['Y barred'] == [hits[1], n]
                    assert row[label]['pass'] == (p <= 0.01)
                with localcontext() as prec:
                    prec.prec = 12
                    p_text = str(Decimal(p.numerator) / Decimal(p.denominator))
                rates.append({'n': n, 'nothing_barred': hits[0], 'Y_barred': hits[1],
                              'p_decimal': p_text, 'passes': p <= 0.01})
            records.append({'name': row['name'], 'group': 'machinery', 'stages': rates})
            continue
        if row['group'] == 'planted' and row['arm'] != 1:
            continue     # The three arms have identical unplanted histories and placement coins.
        arms = (1, 2, 3) if row['group'] == 'planted' else (None,)
        if arms != (None,):
            assert not X.matches(Y) and Y.signature == (((1, 0), (1, 0)), (2,))
            assert LIST['R0b']['planted_case_pair']['parent of placed members'] in cfg['X']
        outputs = {arm: {'name': recorded[j + arm - 1]['name'] if arm else row['name'],
                         'group': row['group'], 'same_form': row['same_form'], 'stages': []} for arm in arms}
        for lo, hi in ((0, 100), (100, 1100)):
            if lo and not any('readings_at_1000' in recorded[j + (arm or 1) - 1] for arm in arms):
                break
            count = {arm: defaultdict(dict) for arm in arms}
            n = min(hi - lo, 4) if pilot else hi - lo
            kinds = KINDS if lo else KINDS[:3]
            for kind in kinds:
                for rd in row['readings']:
                    for arm in arms:
                        count[arm][rd][kind] = 0
                for i in range(lo, lo + n):
                    (_, meet, first, after), seed, end_round = follow(ref, cfg, kind, i, 8, 500, take)
                    # The added parts share nothing with original parts. Both have form Y,
                    # every member has its parent in X, and they are never grown further.
                    placed = (row['group'] == 'planted' and (meet or 4) <= end_round
                              and random.Random(seed + '|PLANT').random() < 0.5)
                    for arm in arms:
                        plant = placed and (arm == 2 or (arm == 1 and kind == 'BN'))
                        for rd in row['readings']:
                            if kind == 'BX':
                                own = 'Yown_val' if rd == 'vX' else 'Yown_form'
                                success = own in first
                            elif kind == 'BN':
                                success = rd in after or (plant and meet is not None)
                            else:
                                success = rd in first or plant
                            count[arm][rd][kind] += success
            for arm in arms:
                expected = recorded[j + (arm or 1) - 1]
                for rd, by_kind in count[arm].items():
                    ps = {k: fisher(by_kind['BN'], n, by_kind[k], n) for k in kinds if k != 'BN'}
                    passed = all(ps[k] <= 0.01 for k in (('BY', 'BX', 'BT') if lo else ('BY', 'BX')))
                    side = expected['readings_at_1000' if lo else 'readings_at_100'][rd]
                    if not pilot:
                        for k in kinds:
                            key = {'BN': 'q1', 'BY': 'q0', 'BX': 'qY', 'BM': 'qM', 'BT': 'qT'}[k]
                            assert side['rates'][key] == by_kind[k], (expected['name'], rd, k, side, by_kind)
                        verdict = side['confirmation']['confirmed'] if lo else side['first_stage']['passes_at_100']
                        assert passed == verdict
                    outputs[arm]['stages'].append({'reading': rd, 'n': n, 'counts': by_kind, 'pass': passed})
        records.extend(outputs.values())
    return records


def trace(pilot):
    c = CASES[87]
    target = [r for r in read_json(RAW / 'Rcond.json')['cases']
              if r['run'] == 'R6' and r['confirmation']['confirmed']]
    out = {}
    compare = []
    matched_main = {}
    cap_check = Counter()
    target_pair_counts = []
    def pair_id(pair):
        return tuple(pair['X']), tuple(pair['Y'])
    for stem in ('R1a', 'R1b', 'R1c', 'R1d', 'R1d_beyond_quarter', 'R2', 'R5', 'R6'):
        stream = lines(RAW / (stem + '.jsonl.gz'))
        records = Counter(growths=0, same_start=0, same_seed=0, same_pair=0)
        for row in (itertools.islice(stream, 100) if pilot else stream):
            records['growths'] += 1
            if row.get('start') == c['start']:
                records['same_start'] += 1
                if row.get('seed') == c['generator']:
                    records['same_seed'] += 1
                    for pair in row.get('pairs', []):
                        if all(pair[k] == c[k] for k in ('s', 'X', 'Y')):
                            records['same_pair'] += 1
                            assert pair['same_form'] and 'form' not in pair['after']
                    assert not any(all(e[k] == c[k] for k in ('s', 'X', 'Y')) and e['reading'] == 'form'
                                   for e in row.get('cases', []))
            if stem in ('R1a', 'R1b'):
                if row.get('n_start') in (3, 4):
                    by_s = defaultdict(list)
                    for pair in row['pairs']:
                        by_s[pair['s']].append(pair_id(pair))
                    matched_main[row['seed']] = by_s
                for case in target:
                    if row.get('seed') == case['seed']:
                        pairs = [p for p in row['pairs'] if all(p[k] == case[k] for k in ('s', 'X', 'Y'))]
                        entries = [p for p in row['cases'] if all(p[k] == case[k] for k in ('s', 'X', 'Y', 'reading'))]
                        compare.append({'start': case['start'], 'run': stem, 's': case['s'],
                                        'pair_present': bool(pairs), 'form_case_present': bool(entries),
                                        'passes_at_100': any(p['first_stage']['passes_at_100'] for p in entries)})
            if stem == 'R6':
                full = defaultdict(list)
                for pair in row['pairs']:
                    full[pair['s']].append(pair_id(pair))
                for s_text, (read, possible, _) in row['pair_rounds'].items():
                    s = int(s_text)
                    pairs = sorted(full[s])
                    assert read == possible == len(pairs)
                    retained = pairs
                    if read > 8:
                        rng = random.Random(f"{row['seed']}|P|{s}")
                        retained = sorted(rng.sample(pairs, 8))
                    if row['seed'] in matched_main:
                        assert sorted(matched_main[row['seed']][s]) == retained
                        cap_check['overlapping_growth_rounds'] += 1
                        cap_check['over_eight_with_exact_sample_reproduced'] += read > 8
                    for case in target:
                        if case['seed'] == row['seed'] and case['s'] == s:
                            target_pair_counts.append({'start': case['start'], 'round': s, 'eligible_pairs': read,
                                                       'retained_by_eight_pair_rule': pair_id(case) in retained,
                                                       'main_growth_was_run': row['seed'] in matched_main})
        out[stem] = records
    for stem in ('R3', 'Rcond'):
        cases = read_json(RAW / (stem + '.json'))['cases']
        out[stem] = {'rows': len(cases), 'same_start': sum(row['start'] == c['start'] for row in cases),
                     'same_seed': sum(row['seed'] == c['generator'] for row in cases)}
    return {'disclosed_equal_form_trace': out, 'every_pair_confirmations_in_main_runs': compare,
            'every_pair_confirmations_cap_check': target_pair_counts, 'actual_pair_samples': cap_check,
            'every_pair_confirmations': [{'start': e['start'], 's': e['s'], 'law': e['law']} for e in target]}


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--part', choices=['records', 'gate', 'values', 'controls', 'trace', 'all'], default='all')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1800 * 1024 ** 2, 1800 * 1024 ** 2))
    tasks = {'records': lambda: {'renaming': counterexamples(), 'gate_samples': gate_calls(),
                                 'census': census(25 if args.pilot else None),
                                 'R7': r7(), 'R8': r8()},
             'gate': lambda: gate(args.pilot), 'values': lambda: scratch_values(args.pilot),
             'controls': lambda: controls(args.pilot), 'trace': lambda: trace(args.pilot)}
    for name, f in tasks.items():
        if args.part not in (name, 'all'):
            continue
        t = time.perf_counter()
        result = f()
        print(f'{name} {time.perf_counter() - t:.3f}s', flush=True)
        if not args.pilot:
            (HERE / ('c_checks_' + name + '.json')).write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
