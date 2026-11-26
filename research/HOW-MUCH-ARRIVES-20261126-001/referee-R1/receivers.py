"""Recount and independently regrow the 24 setting B preparations.

Build the sited starts from the earlier written records. Implement complete
rounds from RING-IN-BALANCE definitions, with no taking and not-all-equal.
After construction only the number of loose distinctions and the meetings
between knots enter the growth law. Multiple shared distinctions between
the same two knots count toward places and give one meeting. Own births have
only ancestors in the near pattern. Match names by exact recursive keys.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import combinations
import json
from pathlib import Path
import resource
from time import perf_counter

import networkx as nx


HERE = Path(__file__).resolve().parent
RECORD = HERE.parent
RESEARCH = RECORD.parent
READINGS = ('name', 'sig0', 'sig1')
ROUNDS = 16
KNOT_LIMIT = 3000
SOURCE = 'source'
RECEIVER = 'g7:122@0'
TWO = 'g3:22@0'
THREE = 'g1:3@0'
STUB = 'stub'
STARTS = {
    SOURCE: [(0, 1, 2, 9, 10, 11), (0, 1, 3), (4, 5, 12, 13, 14),
             (6, 7, 15, 16, 17), (2, 3, 4, 6, 18, 19, 20),
             (7, 8, 21, 22), (5, 8, 23, 24)],
    RECEIVER: [(0, 1, 3), (0, 2, 4, 5), (1, 2, 6, 7)],
    TWO: [(0, 1, 2), (0, 3, 4)],
    THREE: [(0, 1, 2)],
    STUB: [()],
}
PAIRS = {
    'two against three': (THREE, TWO),
    'two against the stub': (STUB, TWO),
    'three against the stub': (STUB, THREE),
}
PILOT = {('B1', 'ORD', 2), ('B1', 'REC-ONE-FEWER', 1),
         ('B2', 'ORD', 5), ('B2', 'CAP-3', 4)}


def lines(path):
    with gzip.open(path, 'rt') as stream:
        yield from (json.loads(line) for line in stream)


def holders_of(stars):
    holders = defaultdict(list)
    for knot, places in enumerate(stars):
        for distinction in places:
            holders[distinction].append(knot)
    return holders


def joined(receiver, sender, d, mark=None):
    near = STARTS[receiver]
    far = STARTS[sender]
    next_distinction = 1 + max(x for places in near for x in places)
    stars = [list(places) for places in near]
    stars.extend([x + next_distinction for x in places] for places in far)
    roles = ['A'] * len(near) + ['B'] * len(far)
    next_distinction = 1 + max(x for places in stars for x in places)
    link_knots = range(len(stars), len(stars) + d - 1)
    stars.extend([] for _ in link_knots)
    roles.extend('link' for _ in link_knots)
    route = (0, *link_knots, len(near))
    for left, right in zip(route, route[1:]):
        common = list(range(next_distinction, next_distinction + 3))
        stars.append(common)
        roles.append('spent')
        stars[left].extend((common[0], next_distinction + 3))
        stars[right].extend((common[1], common[2], next_distinction + 4))
        next_distinction += 5
    if mark is not None:
        stars[len(near) + mark].append(next_distinction)
    assert all(len(knot) >= 3 for knot in stars)
    return stars, roles


def holdings(stars):
    meetings = [set() for _ in stars]
    loose = Counter()
    for knots in holders_of(stars).values():
        if len(knots) == 1:
            loose[knots[0]] += 1
        else:
            a, b = knots
            meetings[a].add(b)
            meetings[b].add(a)
    return meetings, loose


def groups(members, meetings):
    met = {frozenset(near & members) for near in meetings if len(near) >= 2}
    met = {group for group in met if len(group) >= 2}
    joined_pairs = {tuple(sorted(pair)) for group in met for pair in combinations(group, 2)}
    if not joined_pairs:
        return []

    by_knot = defaultdict(list)
    for group in met:
        for knot in group:
            by_knot[knot].append(group)
    joinable = nx.Graph()
    joinable.add_edges_from(joined_pairs)
    big = []
    for maximal in nx.find_cliques(joinable):
        if len(maximal) < 3:
            continue
        candidate = frozenset(maximal)
        probe = min(candidate, key=lambda knot: len(by_knot[knot]))
        if not any(candidate <= witnessed for witnessed in by_knot[probe]):
            group = tuple(sorted(candidate))
            big.append(group)
            joined_pairs.difference_update(combinations(group, 2))
    return sorted(big) + sorted(joined_pairs)


def grow(receiver, sender, d, law, names, mark=None):
    stars, roles = joined(receiver, sender, d, mark)
    meetings, loose = holdings(stars)
    own = [role == 'A' for role in roles]
    role_count = Counter()
    ancestry = []
    for role in roles:
        key = (role, role_count[role])
        ancestry.append(names.setdefault(key, len(names)))
        role_count[role] += 1
    sig0 = [('start', 0, 0, len(places)) for places in stars]
    records, totals = [], []
    short_counts = []
    stop = None
    for _ in range(ROUNDS):
        groups_now = groups(loose.keys(), meetings)
        owes = Counter(knot for group in groups_now for knot in group)
        shorts = {knot: n for knot, n in loose.items() if owes[knot] > n}
        short_counts.append(len(shorts))
        paid_groups = [group for group in groups_now if all(knot not in shorts for knot in group)]
        paid = Counter(knot for group in paid_groups for knot in group)
        births = paid_groups + [(knot,) for knot in sorted(loose) if knot not in shorts
                               for _ in range(loose[knot] - paid[knot])]
        first = len(meetings)
        for i, parents in enumerate(births, first):
            meetings.append(set(parents))
            for parent in parents:
                meetings[parent].add(i)
        next_knots = shorts.keys() | set(range(first, len(meetings)))
        demand = Counter(knot for group in groups(next_knots, meetings) for knot in group)

        tally = {reading: Counter() for reading in READINGS}
        multiplicity = Counter()
        loose = Counter(shorts)
        for i, parents in enumerate(births, first):
            p = len(parents)
            q = max(demand[i], 3 - p, 1)
            fresh = {'ORD': q, 'CAP-3': min(q, 3), 'REC-ONE-FEWER': max(3 - p, 0, q - 1)}[law]
            if fresh:
                loose[i] = fresh
            kind = 'offshoot' if p == 1 else 'join'
            own.append(all(own[parent] for parent in parents))
            birth_key = kind, tuple(sorted(ancestry[parent] for parent in parents))
            identity = (*birth_key, multiplicity[birth_key])
            multiplicity[birth_key] += 1
            ancestry.append(names.setdefault(identity, len(names)))
            sig0.append((kind, p, fresh, p + fresh))
            if own[i]:
                tally['name'][(ancestry[i], fresh, p + fresh)] += 1
                tally['sig0'][sig0[i]] += 1
                tally['sig1'][(*sig0[i], tuple(sorted(sig0[parent] for parent in parents)))] += 1
        records.append(tally)
        totals.append(len(meetings))
        if len(meetings) > KNOT_LIMIT:
            stop = 'knots'
            break
    return records, totals, stop, short_counts


def comparison(first, second):
    rows = []
    for t, (base, change) in enumerate(zip(first[0], second[0]), 1):
        row = {'round': t, 'n': base['name'].total(), "n'": change['name'].total()}
        for reading in READINGS:
            row[reading] = [(change[reading] - base[reading]).total(),
                            (base[reading] - change[reading]).total()]
        rows.append(row)
    first_change = next((r['round'] for r in rows if any(r['name'])), None)
    return {'rows': rows, 'first': first_change, 'rounds': len(rows), 'stops': [first[2], second[2]]}


def archive_key(record):
    return record['setting'], record['law'], record['d']


def table_recount(records):
    printed = {}
    setting = None
    for line in (RECORD / 'tables.md').read_text().splitlines():
        if line.startswith('## Setting B'):
            setting = line.split()[2].rstrip(':')
        if setting and (line.startswith('| ORD |') or line.startswith('| CAP-3 |')
                        or line.startswith('| REC-ONE-FEWER |')):
            law, d, *values = [cell.strip() for cell in line.strip('|').split('|')]
            key = (setting, law, int(d))
            if setting == 'B2':
                key += (values.pop(0),)
            printed[key] = values

    def decimal(shares):
        return f'{float(sum(shares) / len(shares)):.2f}' if shares else '-'

    rebuilt = {}
    for rec in records:
        key = archive_key(rec)
        if rec['setting'] == 'B1':
            marks = [rec['marks'][str(i)] for i in range(7)]
            heard = [case for case in marks if case['first'] is not None]
            seen, last = [], []
            for case in heard:
                seen.append(share(case['rows'][case['first'] - 1], 'sig1'))
                last.append(share(case['rows'][-1], 'sig1'))
            rebuilt[key] = [f'{len(heard)} of {len(marks)}', str([case['first'] for case in marks]),
                            decimal(seen), decimal(last)]
        else:
            for label, case in rec['pairs'].items():
                first = case['first']
                rebuilt[(*key, label)] = [str(first), decimal([share(case['rows'][first - 1], 'sig1')]) if first else '-',
                                           decimal([share(case['rows'][-1], 'sig1')]), str(case['rounds'])]
    assert rebuilt == printed, (rebuilt.keys() ^ printed.keys(),
                                {key: values for key, values in rebuilt.items() if printed.get(key) != values})
    return len(printed)


def share(row, reading):
    denominator = row['n'] + row["n'"]
    return Fraction(sum(row[reading]), denominator) if denominator else None


def case_recount(case):
    rows = case['rows']
    assert [r['round'] for r in rows] == list(range(1, 1 + case['rounds']))
    support = Counter({'both': 0, 'only first': 0, 'only second': 0, 'neither': 0})
    for row in rows:
        n, m = row['n'], row["n'"]
        support[('both' if m else 'only first') if n else ('only second' if m else 'neither')] += 1
        for p, q in (row[reading] for reading in READINGS):
            assert 0 <= p <= m and 0 <= q <= n and m - p == n - q, row
        assert sum(row['sig0']) <= sum(row['sig1']), row
    firsts = {reading: next((r['round'] for r in rows if any(r[reading])), None) for reading in READINGS}
    assert firsts['name'] == case['first']
    first_row = None if case['first'] is None else rows[case['first'] - 1]
    return {
        'rounds': case['rounds'], 'stops': case['stops'], 'first difference': firsts,
        'first changed row by name': first_row, 'last row': rows[-1], 'birth count support by round': support,
        'first share': {reading: str(share(rows[first - 1], reading)) if first else None
                        for reading, first in firsts.items()},
        'disagreements': {reading: sum(any(row[reading]) for row in rows) for reading in READINGS},
        'rows with disagreement above the count difference': {
            reading: sum(min(row[reading]) > 0 for row in rows) for reading in READINGS},
    }


def prerequisites(records):
    """Compare the focal archives for starts, chronology and previous counts."""
    by_key = {archive_key(rec): rec for rec in records}
    short = RESEARCH / 'SHORT-AGAIN-20261126-001'
    old = json.loads((short / 'referee-R1/far_ring_replay.json').read_text())
    earlier_b1 = old['same_far_starts_with_recorded_one_fewer']
    for old in earlier_b1:
        rec = by_key['B1', 'REC-ONE-FEWER', old['steps']]
        assert rec['base knots'] == old['unchanged_knots']
        assert {i: case['first'] for i, case in rec['marks'].items() if case['first']} == old['heard_additions']
    ordinary_b1 = 0
    for old in lines(short / 'far.jsonl.gz'):
        if old['A'] != SOURCE or old['B'] != SOURCE or old['law'] != ['ORD', 'CANCEL-WAIT']:
            continue
        rec = by_key['B1', 'ORD', old['d']]
        for mark, case in rec['marks'].items():
            assert old['changes']['B' + mark]['own'] == case['first']
            assert old['changes']['B' + mark]['rounds'] == case['rounds']
            assert old['own births'][:case['rounds']] == [r['n'] for r in case['rows']]
        ordinary_b1 += 1
    b2_archive = RESEARCH / 'SWITCH-RECEIVERS-20261126-001/receivers_runs.jsonl.gz'
    switch_earlier = {}
    for old in lines(b2_archive):
        if old.get('A') != 'n3:g7:122@0' or old['law'] not in ('CAP-3', 'ORD'):
            continue
        rec = by_key['B2', old['law'], old['d']]
        assert old['by sender'][THREE]['differs from the stub'] is None
        for label, (a, b) in PAIRS.items():
            data = rec['pairs'][label]['rows']
            left, right = old['by sender'][a], old['by sender'][b]
            assert [r['n'] for r in data] == left['own births'][:len(data)]
            assert [r["n'"] for r in data] == right['own births'][:len(data)]
            assert a == STUB or left['rounds with the stub'] >= len(data)
            assert right['rounds with the stub'] >= len(data)
            assert right['differs from the stub'] == rec['pairs'][label]['first']
        switch_earlier[f"{old['law']} d={old['d']}"] = old['classes']
    assert ordinary_b1 == len(earlier_b1) == len(switch_earlier) == 8
    return {'earlier B1 ordinary count with waiting cells matching counts, firsts and horizons': ordinary_b1,
            'earlier B1 recorded one fewer cells matching baseline totals and first differences': len(earlier_b1),
            'earlier B2 cells matching own counts and first named differences': len(switch_earlier),
            'earlier B2 senders grouped by receiver history': switch_earlier}


def verify_replay(records):
    per_case = {}
    for rec in records:
        key = archive_key(rec)
        setting, law, d = key
        names = {}
        before = perf_counter()
        if setting == 'B1':
            base = grow(SOURCE, SOURCE, d, law, names)
            assert base[1] == rec['base knots'], key
            changed = {i: grow(SOURCE, SOURCE, d, law, names, int(i)) for i in rec['marks']}
            expected = {i: comparison(base, run) for i, run in changed.items()}
            original = rec['marks']
            runs = {'unmarked': base, **changed}
        else:
            grown = {s: grow(RECEIVER, s, d, law, names) for s in (TWO, THREE, STUB)}
            expected = {label: comparison(grown[a], grown[b]) for label, (a, b) in PAIRS.items()}
            original = rec['pairs']
            runs = grown
        for label in expected:
            assert expected[label] == original[label], (key, label, expected[label], original[label])
        short_rounds = {label: [r for r, count in enumerate(run[3], 1) if count]
                        for label, run in runs.items()}
        summary = {
            'trajectories': len(runs), 'comparisons': len(expected),
            'comparison rounds': sum(c['rounds'] for c in expected.values()),
            'trajectory rounds with any short knot': sum(map(len, short_rounds.values())),
            'seconds': round(perf_counter() - before, 3),
        }
        if law == 'ORD':
            summary['rounds with any short knot, by trajectory'] = {i: rounds for i, rounds in short_rounds.items() if rounds}
            if setting == 'B1':
                summary['comparison horizons if stopped on the first short knot'] = {
                    i: min(c['rounds'], min(short_rounds['unmarked'] + short_rounds[i], default=ROUNDS + 1) - 1)
                    for i, c in expected.items()}
        per_case[f'{setting} {law} d={d}'] = summary
    return per_case


def check_placements():
    stars = STARTS[SOURCE]
    meetings, loose = holdings(stars)
    join = nx.Graph()
    for group in holders_of(stars).values():
        join.add_nodes_from(group)
        if len(group) == 2:
            a, b = group
            multiplicity = join[a][b]['shared'] if join.has_edge(a, b) else 0
            join.add_edge(a, b, shared=multiplicity + 1)
    for knot in join:
        join.nodes[knot].update(site=knot == 0, loose=loose[knot])
    symmetries = list(nx.algorithms.isomorphism.GraphMatcher(
        join, join, node_match=lambda a, b: a == b, edge_match=lambda a, b: a == b).isomorphisms_iter())
    orbits = sorted({tuple(sorted({p[knot] for p in symmetries})) for knot in join})
    offsets = [nx.shortest_path_length(join, 0, knot) for knot in range(len(stars))]
    for d in range(1, 9):
        stars_joined, _ = joined(SOURCE, SOURCE, d)
        sharing, _ = holdings(stars_joined)
        graph = nx.Graph((i, j) for i, nearby in enumerate(sharing) for j in nearby)
        actual = [nx.shortest_path_length(graph, 0, 7 + i) for i in range(len(stars))]
        assert actual == [2 * d + h for h in offsets]
    return {'source site': 0, 'source loose counts before joining': [loose[knot] for knot in range(len(meetings))],
            'mark holder steps within sender from its site': offsets, 'source site-preserving mark classes': orbits,
            'holder steps between sites at meeting count d': '2d'}


def compare_shares(records):
    capped = [r['pairs']['two against the stub'] for r in records if archive_key(r)[:2] == ('B2', 'CAP-3')]
    jammed = [r['marks']['5'] for r in records if archive_key(r)[:2] == ('B1', 'REC-ONE-FEWER')]
    assert all(rec['pairs']['two against the stub'] == rec['pairs']['two against three'] for rec in records
               if rec['setting'] == 'B2')
    same_round = max(case['first'] for case in capped)
    offsets = min(case['rounds'] - case['first'] for case in capped)
    return {
        'B1 changed receiver counts in the first changed round, d=1 through 8': [
            case['rows'][case['first'] - 1]["n'"] for case in jammed],
        'B2 reading of the capped receiver, two-knot sender compared with stub, d=2 through 5': {
            'sig1 shares in absolute round ' + str(same_round): [
                str(share(case['rows'][same_round - 1], 'sig1')) for case in capped],
            'sig1 shares in absolute round 16': [str(share(case['rows'][-1], 'sig1')) for case in capped],
            'sig1 shares at equal elapsed rounds since the first difference': [
                [str(share(case['rows'][case['first'] + lag - 1], 'sig1')) for case in capped]
                for lag in range(offsets + 1)],
        },
    }


def main():
    start = perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    records = sorted((r for r in lines(RECORD / 'runs.jsonl.gz') if r.get('setting') in ('B1', 'B2')), key=archive_key)
    expected = {('B1', law, d) for law in ('ORD', 'REC-ONE-FEWER') for d in range(1, 9)}
    expected |= {('B2', law, d) for law in ('ORD', 'CAP-3') for d in range(2, 6)}
    assert len(records) == len(expected) and set(map(archive_key, records)) == expected
    table_rows = table_recount(records)
    source_checks = prerequisites(records)
    placements = check_placements()
    bins, details = defaultdict(Counter), {}
    for rec in records:
        setting, law, d = archive_key(rec)
        cases = rec['marks'] if setting == 'B1' else rec['pairs']
        assert set(cases) == ({str(i) for i in range(7)} if setting == 'B1' else set(PAIRS))
        totals = bins[f'{setting} {law}']
        totals['preparations'] += 1
        details[f'{setting} {law} d={d}'] = {}
        for label, case in cases.items():
            tally = case_recount(case)
            totals['comparisons'] += 1
            totals['rounds'] += case['rounds']
            totals[f"horizon {case['rounds']}"] += 1
            reference = d + 5 if setting == 'B1' else 2 * d + 1
            totals['comparisons reaching the previously reported first difference round'] += case['rounds'] >= reference
            totals['comparisons continuing beyond that round'] += case['rounds'] > reference
            totals.update(tally['birth count support by round'])
            totals['comparisons with both sides active at the previously reported first difference round'] += (
                case['rounds'] >= reference and bool(case['rows'][reference - 1]['n'] and case['rows'][reference - 1]["n'"]))
            for reading in READINGS:
                totals[f'{reading} comparisons with difference'] += tally['first difference'][reading] is not None
                totals[f'{reading} differing rounds'] += tally['disagreements'][reading]
                totals[f'{reading} differing rounds above the count difference'] += tally['rows with disagreement above the count difference'][reading]
            details[f'{setting} {law} d={d}'][label] = tally
    replays = verify_replay(rec for rec in records if not args.pilot or archive_key(rec) in PILOT)
    result = {
        'printed Setting B rows verified': table_rows, 'archive coverage': bins,
        'start and meeting checks': placements, 'earlier records': source_checks,
        'comparison at equal elapsed versus absolute rounds': compare_shares(records),
        'all comparisons': details,
        'independent replay': {'spending and fresh counts': 'RING-IN-BALANCE-20261123-001/definitions.md',
                               'matching': 'Exact ancestry keys and local signature multisets. No study module imported.',
                               'round limit': ROUNDS, 'knot limit': KNOT_LIMIT, 'cases': replays},
        'resource use': {'seconds': round(perf_counter() - start, 3),
                         'peak RSS KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'all comparisons'}, indent=2))


if __name__ == '__main__':
    main()
