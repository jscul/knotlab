"""Recount the closed census and, when supplied, compare its two launch originals."""

import argparse
import ast
import gzip
import hashlib
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


CENSUS = Path(__file__).resolve().parents[1] / 'census'
JOINS = {'meeting': 'a meeting', 'share': 'a shared distinction'}
RATIONS = {'ORD': 'ordinary count', 'CAP-3': 'cap of three', 'FLOOR1': 'just enough for three'}
TREATMENTS = {'CANCEL-WAIT': 'waits', 'CANCEL-RETIRE': 'retires', 'CANCEL-OFFSHOOT': 'offshoots'}
CLASS_ORDER = ('none', 'constant', 'fixed step', 'faster', 'other')
CASE_FIELDS = set('i j A B join law rounds ended knots short joint reads seconds'.split())
READ_FIELDS = {'last kept', 'last joined', 'stub', 'own births', 'marks'}
WAITING_SHARE = ('share', 'ORD', 'CANCEL-WAIT')


def sited_starts():
    # The four labelled meeting patterns of one to three knots used in the archive.
    forms = [
        (1, 1, set()),
        (3, 2, {(0, 1)}),
        (6, 3, {(0, 1), (0, 2)}),
        (7, 3, {(0, 1), (0, 2), (1, 2)}),
    ]
    names = []
    starts_by_size = Counter()
    for ordinary_id, knot_count, overlaps in forms:
        knots = range(knot_count)
        symmetries = [
            ordering for ordering in itertools.permutations(knots)
            if {tuple(sorted((ordering[u], ordering[v]))) for u, v in overlaps} == overlaps
        ]
        degrees = [sum(knot in pair for pair in overlaps) for knot in knots]
        for loose in itertools.product(range(4), repeat=knot_count):
            if not any(loose) or min(degree + count for degree, count in zip(degrees, loose)) < 3:
                continue
            recodings = [tuple(loose[v] for v in perm) for perm in symmetries]
            if loose != min(recodings):
                continue
            starts_by_size[knot_count] += 1
            preserved = [perm for perm, recoding in zip(symmetries, recodings) if recoding == loose]
            for site in knots:
                if site == min(perm[site] for perm in preserved):
                    names.append((f'g{ordinary_id}:{"".join(map(str, loose))}@{site}', knot_count))
    return names, dict(starts_by_size)


def load(path, limit):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rb') as source:
        return [(line, json.loads(line)) for line in itertools.islice(source, limit)]


def pair(row):
    return row['i'], row['j']


def treatment(row):
    return row['join'], *row['law']


def case_key(row):
    return *pair(row), *treatment(row)


def round_counts(values, rounds):
    return len(values) == rounds and all(type(value) is int and value >= 0 for value in values)


def check_case(row, starts):
    assert set(row) == CASE_FIELDS, (case_key(row), set(row))
    i, j = pair(row)
    assert type(i) is int and type(j) is int and 0 <= i <= j < len(starts), pair(row)
    (a_name, a_knots), (b_name, b_knots) = starts[i], starts[j]
    assert (row['A'], row['B']) == (a_name, b_name), pair(row)
    join, ration, handling = treatment(row)
    assert join in JOINS and ration in RATIONS and handling in TREATMENTS, case_key(row)
    rounds = row['rounds']
    assert type(rounds) is int and 1 <= rounds <= 10, case_key(row)
    assert row['ended'] in {'rounds', 'knots'}, case_key(row)
    assert type(row['knots']) is int, case_key(row)
    assert (row['knots'] > 1500) == (row['ended'] == 'knots'), case_key(row)
    if row['ended'] == 'rounds':
        assert rounds == 10, case_key(row)
    assert math.isfinite(row['seconds']) and row['seconds'] >= 0, case_key(row)
    assert round_counts(row['short'], rounds) and round_counts(row['joint'], rounds), case_key(row)
    assert set(row['reads']) == {'A', 'B'}, case_key(row)
    births = [row['joint']]
    for reading, mark_count in zip((row['reads']['A'], row['reads']['B']), (b_knots, a_knots)):
        assert set(reading) == READ_FIELDS, case_key(row)
        assert all(type(reading[field]) is int for field in ('last kept', 'last joined')), case_key(row)
        assert 0 <= reading['last kept'] <= reading['last joined'] <= rounds, case_key(row)
        assert round_counts(reading['own births'], rounds), case_key(row)
        assert len(reading['marks']) == mark_count, case_key(row)
        assert all(len(mark) == 2 for mark in reading['marks']), case_key(row)
        for comparison in itertools.chain((reading['stub'],), itertools.chain.from_iterable(reading['marks'])):
            assert comparison is None or (type(comparison) is int and 1 <= comparison <= rounds), case_key(row)
        births.append(reading['own births'])
    total = a_knots + b_knots + (join == 'meeting')
    for short, *made in zip(row['short'], *births):
        assert short <= total, case_key(row)
        assert total <= 1500, case_key(row)
        total += sum(made)
    assert row['knots'] == total, case_key(row)


def partition(lines, starts):
    cases, lost = {}, {}
    for _, row in lines:
        if 'reads' in row:
            check_case(row, starts)
            key = case_key(row)
            assert key not in cases, key
            cases[key] = row
        else:
            assert set(row) == {'i', 'j', 'not run', 'why'}, row
            key = pair(row)
            assert key not in lost, key
            assert 0 <= row['i'] <= row['j'] < len(starts), key
            assert type(row['not run']) is int and 1 <= row['not run'] <= 18, row
            assert isinstance(row['why'], str), row
            lost[key] = row
    return cases, lost


def last_short(row):
    return max((r for r, count in enumerate(row['short'], 1) if count), default=0)


def growth(row):
    tail = row['joint'][-4:]
    changes = [b - a for a, b in itertools.pairwise(tail)]
    if tail[-1] == 0:
        return 'none', None
    if len(tail) != 4:
        return 'other', None
    first, middle, last = changes
    if first == middle == last >= 0:
        return ('constant' if not first else 'fixed step'), first
    if 0 < first <= middle <= last and first < last:
        return 'faster', None
    return 'other', None


def last_kept(row):
    return max(reading['last kept'] for reading in row['reads'].values())


def slow(row):
    return growth(row)[1] is not None and last_kept(row) == row['rounds']


def hearing(rows):
    own, joint = Counter(), Counter()
    for row in rows:
        for read in row['reads'].values():
            for own_round, joint_round in read['marks']:
                own['none' if own_round is None else own_round] += 1
                joint['none' if joint_round is None else joint_round] += 1
    return own, joint


def exposure(rows):
    per_round = {}
    for target in range(7, 11):
        at_risk = 0
        cases_at_risk = 0
        witnessed_horizon = 0
        witnessed_cases = 0
        for row in rows:
            if row['rounds'] < target:
                continue
            in_case = observed_in_case = 0
            for reading in row['reads'].values():
                for own, joint in reading['marks']:
                    if own is not None and own < target:
                        continue
                    in_case += 1
                    # A first difference at this round or later certifies that both growths were compared this far.
                    observed_in_case += max(own or 0, joint or 0) >= target
            at_risk += in_case
            cases_at_risk += bool(in_case)
            witnessed_horizon += observed_in_case
            witnessed_cases += bool(observed_in_case)
        per_round[str(target)] = {
            'unmarked growths reaching round': sum(row['rounds'] >= target for row in rows),
            'cases with a mark that could still be at risk, upper bound from records': cases_at_risk,
            'marks that could still be at risk, upper bound from records': at_risk,
            'cases whose first differences certify an at-risk mark comparison this far': witnessed_cases,
            'at-risk marks whose first differences certify comparison this far': witnessed_horizon,
        }
    return per_round


def census_table(rows_by_law):
    result = []
    for join, ration, handling in itertools.product(JOINS, RATIONS, TREATMENTS):
        cases = rows_by_law[join, ration, handling]
        readings = [reading for case in cases for reading in case['reads'].values()]
        own, joint = hearing(cases)
        mark_count = own.total()
        own_made, joint_made = own.copy(), joint.copy()
        own_made.pop('none', None)
        joint_made.pop('none', None)
        result.append({
            'join': join,
            'ration': ration,
            'treatment': handling,
            'cases': len(cases),
            'a knot short': sum(last_short(case) > 0 for case in cases),
            'readings': len(readings),
            'differ from with a stub': sum(read['stub'] is not None for read in readings),
            'marks': mark_count,
            'heard by own': own_made.total(),
            'latest own': max(own_made, default=None),
            'heard by joint': joint_made.total(),
            'latest joint': max(joint_made, default=None),
            'kept in the last round': sum(
                reading['last kept'] == case['rounds'] for case in cases for reading in case['reads'].values()
            ),
            'growth': dict(Counter(growth(case)[0] for case in cases)),
            'slow': sum(map(slow, cases)),
        })
    return result


def compare_published(table, forecast, rows, lost):
    published_json = json.loads((CENSUS / 'census_table.json').read_text())['table']
    markdown = (CENSUS / 'census_table.md').read_text()
    table_lines = [line for line in markdown.splitlines() if line.startswith('|')]
    published_md = [[cell.strip() for cell in line[1:-1].split('|')] for line in table_lines[2:]]
    expected_md = []
    for row in table:
        expected_md.append([
            JOINS[row['join']], RATIONS[row['ration']], TREATMENTS[row['treatment']], str(row['cases']),
            str(row['a knot short']), f"{row['differ from with a stub']} of {row['readings']}",
            f"{row['heard by own']} of {row['marks']} ({row['latest own']})",
            f"{row['heard by joint']} of {row['marks']} ({row['latest joint']})",
            str(row['kept in the last round']),
            ' / '.join(str(row['growth'].get(label, 0)) for label in CLASS_ORDER), str(row['slow']),
        ])

    def footer(pattern):
        return re.search(pattern, markdown, re.MULTILINE).groups()

    ordinary = forecast['ordinary meeting']
    ord_share = forecast['ordinary share slow']
    lost_count = sum(row['not run'] for row in lost.values())
    own, late_examples = footer(r'^1\. marks first heard by own knots after round 6: (\d+) (.*)$')
    joint, exposure, cases = footer(
        r'^   by the joint descent after round 6: (\d+) ; cases read to round 7 or further: (\d+) of (\d+)$'
    )
    differing, pairs = footer(r'^2\. a meeting under the ordinary count: .*: (\d+) of (\d+)$')
    short, differing_without_short = footer(r'^   pairs with a knot short there: (\d+) ; .*: (\d+)$')
    slow_groups, = footer(r'^3\. pairs with a slow case, by join and ration: (.*)$')
    slow_example_pairs, = footer(r'^   shared distinction, ordinary count: (.*)$')
    slow_steps, = footer(r'^   their growth and step: (.*)$')
    floor_last, = footer(r'^4\. just enough for three: cases by the last round with a kept join: (.*)$')
    recorded, planned, marked_lost, lost_pairs, lost_reasons = footer(
        r'^cases read: (\d+) of (\d+) ; not run: (\d+) in (\d+) pairs (.*)$'
    )
    rounds_hist, ended_hist = footer(r'^rounds read: (.*) ; ended by: (.*)$')
    return {
        'JSON table matches every cell': published_json == table,
        'Markdown table matches every cell': published_md == expected_md,
        'Markdown footer comparisons': {
            'prediction 1': (
                int(own) == forecast['marks first heard after round 6']['own']
                and ast.literal_eval(late_examples) == []
                and int(joint) == forecast['marks first heard after round 6']['joint']
                and int(exposure) == sum(r['rounds'] >= 7 for r in rows)
                and int(cases) == len(rows)
            ),
            'prediction 2': tuple(map(int, (differing, pairs, short, differing_without_short))) == (
                ordinary['pairs with different own births against stub'], ordinary['pairs'],
                ordinary['pairs with a short knot'], ordinary['pairs with different own births against stub and no short knot'],
            ),
            'prediction 3': (
                ast.literal_eval(slow_groups) == forecast['slow pairs by join and ration']
                and ast.literal_eval(slow_example_pairs) == ord_share['first forty slow pairs in roster order']
                and {f'{kind}, {step}': count for (kind, step), count in ast.literal_eval(slow_steps).items()}
                == ord_share['last increment across cases counted as slow']
            ),
            'prediction 4': ast.literal_eval(floor_last) == forecast['cases by last kept join under just enough for three'],
            'totals': (
                tuple(map(int, (recorded, planned, marked_lost, lost_pairs)))
                == (len(rows), len(rows) + lost_count, lost_count, len(lost))
                and ast.literal_eval(lost_reasons) == Counter(r['why'] for r in lost.values())
                and ast.literal_eval(rounds_hist) == Counter(r['rounds'] for r in rows)
                and ast.literal_eval(ended_hist) == Counter(r['ended'] for r in rows)
            ),
        },
    }


def predictions(cases, lost):
    ordinary_meeting = [r for r in cases if treatment(r)[:2] == ('meeting', 'ORD')]
    slow_pairs = defaultdict(set)
    ordinary_share_slow = defaultdict(set)
    positive_step_pairs = set()
    for row in cases:
        if not slow(row):
            continue
        join, ration, handling = treatment(row)
        slow_pairs[join, ration].add(pair(row))
        if (join, ration) == ('share', 'ORD'):
            ordinary_share_slow[pair(row)].add(handling)
            if growth(row)[0] == 'fixed step':
                positive_step_pairs.add(pair(row))
    treatment_counts = Counter(
        tuple(key for key in TREATMENTS if key in value) for value in ordinary_share_slow.values()
    )
    cases_by_name = {pair(row): (row['A'], row['B']) for row in cases}
    waiting_only = sorted(key for key, value in ordinary_share_slow.items() if value == {'CANCEL-WAIT'})
    short_decline = Counter(
        last_kept(row) for row in cases if treatment(row)[1] == 'FLOOR1'
    )
    own, joint = hearing(cases)
    return {
        'marks first heard after round 6': {
            'own': sum(count for round_num, count in own.items() if round_num != 'none' and round_num > 6),
            'joint': sum(count for round_num, count in joint.items() if round_num != 'none' and round_num > 6),
        },
        'ordinary meeting': {
            'pairs': len({pair(r) for r in ordinary_meeting}),
            'pairs with different own births against stub': len({
                pair(r) for r in ordinary_meeting if any(v['stub'] is not None for v in r['reads'].values())
            }),
            'pairs with a short knot': len({pair(r) for r in ordinary_meeting if last_short(r)}),
            'pairs with different own births against stub and no short knot': len({
                pair(r) for r in ordinary_meeting if not last_short(r)
                and any(v['stub'] is not None for v in r['reads'].values())
            }),
        },
        'slow pairs by join and ration': {
            f'{join}, {ration}': len(pairs) for (join, ration), pairs in sorted(slow_pairs.items())
        },
        'ordinary share slow': {
            'pairs by exact set of treatments with a slow case': {
                ', '.join(TREATMENTS[name] for name in keys): count for keys, count in sorted(treatment_counts.items())
            },
            'pairs slow where only waiting was slow': [cases_by_name[key] for key in waiting_only],
            'pairs with positive fixed step as forecast': len(positive_step_pairs),
            'pairs absent from the union with a waiting case not run': len(lost.keys() - ordinary_share_slow.keys()),
            'first forty slow pairs in roster order': [cases_by_name[key] for key in sorted(ordinary_share_slow)[:40]],
            'last increment across cases counted as slow': {
                f'{label}, {step}': count for (label, step), count in sorted(Counter(
                    growth(row) for row in cases if treatment(row)[:2] == ('share', 'ORD') and slow(row)
                ).items())
            },
        },
        'cases by last kept join under just enough for three': dict(sorted(short_decline.items())),
    }


def launch_provenance(first, rest, merged, starts, full):
    first_cases, first_not_run = partition(first, starts)
    rest_cases, rest_not_run = partition(rest, starts)
    first_counts = Counter(pair(r) for r in first_cases.values())
    first_complete = {key for key, count in first_counts.items() if count == 18}
    from_first = [line for line, r in first if pair(r) in first_complete]
    reconstructed = from_first + [line for line, _ in rest]
    merged_bytes = [line for line, _ in merged]
    duplicate_keys = (first_cases.keys() & rest_cases.keys())
    different_replay = 0
    for key in duplicate_keys:
        a, b = first_cases[key].copy(), rest_cases[key].copy()
        a.pop('seconds')
        b.pop('seconds')
        different_replay += a != b
    rest_pairs = {pair(r) for _, r in rest}
    first_bytes = b''.join(line for line, _ in first)
    rest_bytes = b''.join(line for line, _ in rest)
    if full:
        assert first_complete.isdisjoint(rest_pairs)
        expected_pairs = set(itertools.combinations_with_replacement(range(len(starts)), 2))
        assert first_complete | rest_pairs == expected_pairs
        assert reconstructed == merged_bytes
    return {
        'first launch': {
            'sha256': hashlib.sha256(first_bytes).hexdigest(),
            'rows': len(first), 'cases': len(first_cases), 'not-run notices': len(first_not_run),
            'complete pairs kept': len(first_complete),
            'other pairs represented': sorted({pair(r) for _, r in first} - first_complete),
            'lines kept': len(from_first), 'lines superseded': len(first) - len(from_first),
            'not-run notices by reason and count': [
                {'i': i, 'j': j, 'count': row['not run'], 'reason': row['why']}
                for (i, j), row in first_not_run.items()
            ],
        },
        'second launch': {
            'sha256': hashlib.sha256(rest_bytes).hexdigest(),
            'rows': len(rest), 'cases': len(rest_cases), 'not-run notices': len(rest_not_run),
            'pairs rerun': len(rest_pairs & (set(first_counts) | first_not_run.keys())),
            'pairs first reported': len(rest_pairs - (set(first_counts) | first_not_run.keys())),
            'pairs with rows': len(rest_pairs),
            'cases recovered in the eight incomplete pairs': sum(
                pair(row) in first_not_run and key not in first_cases for key, row in rest_cases.items()
            ),
            'gaps remaining in the original incomplete pairs': sum(
                row['not run'] for key, row in rest_not_run.items() if key in first_not_run
            ),
            'gaps among the newly reported pairs': sum(
                row['not run'] for key, row in rest_not_run.items() if key not in first_not_run
            ),
        },
        'common case keys in the launch originals': len(duplicate_keys),
        'common cases that differ besides runtime': different_replay,
        'merged decompressed sha256': hashlib.sha256(b''.join(merged_bytes)).hexdigest(),
        'complete first-launch pairs followed by every second-launch row match merged bytes': reconstructed == merged_bytes,
    }


def audit(lines, starts, starts_by_size, full):
    cases, lost = partition(lines, starts)
    pairs = list(itertools.combinations_with_replacement(range(len(starts)), 2))
    expected = set(itertools.product(pairs, itertools.product(JOINS, RATIONS, TREATMENTS)))
    missing = sorted((*ij, *law) for ij, law in expected if (*ij, *law) not in cases)
    if full:
        gaps = Counter((i, j) for i, j, *_ in missing)
        assert gaps == Counter({key: r['not run'] for key, r in lost.items()})
        assert all(tuple(m[2:]) == WAITING_SHARE for m in missing)
        assert all(row['why'] == 'the clock' for row in lost.values())
    rows = list(cases.values())
    rows_by_law = defaultdict(list)
    for row in rows:
        rows_by_law[treatment(row)].append(row)
    own, joint = hearing(rows)
    table = census_table(rows_by_law)
    forecast = predictions(rows, lost)
    at_risk = exposure(rows)
    at_risk_by_law = {', '.join(law): exposure(subset)['7'] for law, subset in rows_by_law.items()}
    return {
        'mode': 'full recount' if full else 'timed prefix',
        'starts by number of knots': starts_by_size,
        'sited starts by number of knots': dict(Counter(knot_count for _, knot_count in starts)),
        'pairs planned': len(pairs),
        'cases planned': len(expected),
        'cases recorded and schema checked': len(cases),
        'unmarked growth stop rounds': dict(sorted(Counter(r['rounds'] for r in rows).items())),
        'unmarked growth stop reasons': dict(Counter(r['ended'] for r in rows)),
        'cases stopping before round 7': [
            {'starts': [r['A'], r['B']], 'join': r['join'], 'law': r['law'], 'knots': r['knots'],
             'ending': r['ended']} for r in rows if r['rounds'] < 7
        ],
        'cases not run': [
            {'starts': [starts[i][0], starts[j][0]], 'i': i, 'j': j, 'join': join,
             'law': [ration, handling], 'reason': lost[i, j]['why'], 'marks not run': starts[i][1] + starts[j][1]}
            for i, j, join, ration, handling in missing if (i, j) in lost
        ],
        'marks planned': sum(starts[i][1] + starts[j][1] for (i, j), _ in expected),
        'marks recorded': own.total(),
        'own first difference by round': dict(own),
        'joint first difference by round': dict(joint),
        'last short round by law': {
            ', '.join(law): dict(sorted(Counter(map(last_short, subset)).items()))
            for law, subset in rows_by_law.items()
        },
        'cases short in round 1 by law': {
            ', '.join(law): sum(bool(row['short'][0]) for row in subset) for law, subset in rows_by_law.items()
        },
        'last kept join by law': {
            ', '.join(law): dict(sorted(Counter(map(last_kept, subset)).items()))
            for law, subset in rows_by_law.items()
        },
        'comparisons after round 6': at_risk,
        'comparisons in round 7 by law': at_risk_by_law,
        'table': table,
        'published table comparison': compare_published(table, forecast, rows, lost) if full else None,
        'predictions': forecast,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first', type=Path, help='first launch original')
    parser.add_argument('--rest', type=Path, help='second launch original')
    parser.add_argument('--limit', type=int, help='read a timed prefix from each archive')
    parser.add_argument('--output', type=Path, help='write the recount as JSON')
    args = parser.parse_args()
    if (args.first is None) != (args.rest is None):
        parser.error('--first and --rest are used together')
    starts, starts_by_size = sited_starts()
    lines = load(CENSUS / 'census_runs.jsonl.gz', args.limit)
    result = audit(lines, starts, starts_by_size, args.limit is None)
    if args.first:
        result['launch provenance'] = launch_provenance(
            load(args.first, args.limit), load(args.rest, args.limit), lines, starts, args.limit is None
        )
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    else:
        print(json.dumps({
            'mode': result['mode'],
            'cases recorded and schema checked': result['cases recorded and schema checked'],
            'marks recorded': result['marks recorded'],
        }))


if __name__ == '__main__':
    main()
