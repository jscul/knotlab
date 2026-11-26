"""Check the engine's census logs and replay readings from saved growth rows."""

import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random
import resource
import subprocess
from time import perf_counter

import networkx as nx


STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
LOOK = STUDY.parent / 'LOOK-ALIKE-20261126-001'
BOUND = STUDY.parent / 'SETTLE-BOUND-20261126-001'
RESULT_COMMIT = '815b1964d7'
LAWS = ('nae', 'parity')
SEED = 20261204


def census_ids(size):
    ids = []
    for entry, meeting in enumerate(nx.graph_atlas_g()):
        if len(meeting) != size or not nx.is_connected(meeting):
            continue
        members = tuple(range(size))
        pairs = {frozenset(pair) for pair in meeting.edges()}
        symmetries = [p for p in permutations(members)
                      if {frozenset(p[k] for k in pair) for pair in pairs} == pairs]
        minimum = [max(0, 3 - meeting.degree(k)) for k in members]
        for loose in product(*(range(m, 4) for m in minimum)):
            if any(loose) and all(loose <= tuple(loose[p[k]] for k in members)
                                  for p in symmetries):
                ids.append((entry, loose, pairs))
    return ids


def file_sha(path):
    with path.open('rb') as stream:
        return sha256(stream.read()).hexdigest()


def raw_archive(path, ids, horizon):
    records = []
    with gzip.open(path, 'rt') as stream:
        for line in stream:
            record = json.loads(line)
            if len(record['stars']) != len(ids[0][1]):
                continue
            assert record['index'] == len(records)
            entry, loose, pairs = ids[len(records)]
            assert (record['graph'], tuple(record['loose'])) == (entry, loose)
            holders = defaultdict(set)
            for knot, stars in enumerate(record['stars']):
                assert len(set(stars)) == len(stars)
                for d in stars:
                    holders[d].add(knot)
            assert all(len(h) in (1, 2) for h in holders.values())
            shared = [frozenset(h) for h in holders.values() if len(h) == 2]
            assert set(shared) == pairs and len(shared) == len(pairs)
            open_counts = Counter(next(iter(h)) for h in holders.values() if len(h) == 1)
            assert tuple(open_counts[k] for k in range(len(loose))) == loose
            assert record['knots'] == len(record['stars']) + sum(row['n'] for row in record['rows'])
            for row in record['rows']:
                first, second = readings(row)
                assert sum(first.values()) == sum(second.values()) == row['n'] > 0
                marginal = Counter()
                for (kind, parents), count in second.items():
                    assert len(parents) == kind[1] and tuple(sorted(parents)) == parents
                    marginal[kind] += count
                assert marginal == first
            end, rows = record['end'], record['rows']
            if end == 'bound':
                assert record['knots'] > 30000 >= record['knots'] - rows[-1]['n']
                assert len(rows) <= horizon
            elif end.startswith('closes at round '):
                assert 1 + len(rows) == int(end.split()[-1]) <= horizon
                assert rows[-1]['n'] == 1 and rows[-1]['sig0'][0][0][2] == 0
            elif end == 'stalls at round 1':
                assert not rows
            else:
                assert end == 'rounds' and len(rows) == horizon
            records.append(record)
    assert len(records) == len(ids)
    return records


def readings(row):
    first = Counter({tuple(kind): n for kind, n in row['sig0']})
    second = Counter({(tuple(kind), tuple(map(tuple, parents))): n
                      for (kind, parents), n in row['sig1']})
    assert len(first) == len(row['sig0']) and len(second) == len(row['sig1'])
    assert all(n > 0 for n in first.values()) and all(n > 0 for n in second.values())
    return first, second


def table_histogram(keys):
    counts = Counter(keys)
    return [{'rounds': rounds, 'growth end': growth, 'engine end': engine, 'starts': count}
            for (rounds, growth, engine), count in sorted(counts.items())]


def archive_inventory(path, records):
    return {
        'path': str(path.relative_to(ROOT)),
        'serialized SHA-256': file_sha(path),
        'starts': len(records),
        'birth rounds': sum(len(r['rows']) for r in records),
        'births': sum(r['knots'] - len(r['stars']) for r in records),
        'end and round counts': table_histogram((len(r['rows']), r['end'], None) for r in records),
    }


def verify_snapshot(content, law, raw):
    end_of_line = content.rfind(b'\n') + 1
    complete, tail = content[:end_of_line], content[end_of_line:]
    compared = Counter()
    hints = []
    records = list(map(json.loads, complete.splitlines()))
    assert records == sorted(records, key=lambda row: row['index'])
    for index, row in enumerate(records):
        assert set(row) == {'law', 'index', 'agree', 'rounds compared', 'growth end', 'engine end'}
        assert row['index'] == index and row['law'] == law and type(row['agree']) is bool
        witness = raw[index]
        tested = row['rounds compared']
        expected = len(witness['rows'])
        assert 0 <= tested <= expected and row['growth end'] == witness['end']
        if row['engine end'] != 'cap':
            assert tested == expected
        compared['comparisons'] += 1
        compared['agreements'] += row['agree']
        compared['zero-round agreements'] += row['agree'] and tested == 0
        compared['agreements with at least one compared round'] += row['agree'] and tested > 0
        compared['compared birth rounds'] += tested
        compared['compared births'] += sum(r['n'] for r in witness['rows'][:tested])
        compared['starts compared through round 24'] += tested == 24
        compared['shared growth stopped at the cumulative knot bound'] += witness['end'] == 'bound'
        compared['shared growth stopped at that bound before round 24'] += witness['end'] == 'bound' and tested < 24
        compared['engine stopped at its per-round cap'] += row['engine end'] == 'cap'
        expected_engine_end = ('stall' if witness['end'].startswith('stalls') else
                               'closed' if witness['end'].startswith('closes') else 'rounds')
        if row['engine end'] != expected_engine_end:
            hints.append(index)
    return {
        'snapshot SHA-256': sha256(complete).hexdigest(),
        'partial line bytes omitted': len(tail),
        'first missing index': len(records) if len(records) < len(raw) else None,
        'missing starts': len(raw) - len(records),
        'census coverage is a contiguous prefix': True,
        'counts': dict(compared),
        'end and round counts': table_histogram((r['rounds compared'], r['growth end'], r['engine end'])
                                               for r in records),
        'nonagreements': [r for r in records if not r['agree']],
        'unexpected engine end indices': hints,
    }


def verification_logs(law, raw):
    file = STUDY / f'verify_5_{law}.jsonl'
    committed = subprocess.check_output(['git', 'show', f'{RESULT_COMMIT}:{file.relative_to(ROOT)}'], cwd=ROOT)
    working = file.read_bytes()
    assert working.startswith(committed)
    return {'committed': verify_snapshot(committed, law, raw),
            'working copy': verify_snapshot(working, law, raw)}


def bitrow(distinctions):
    return sum(1 << distinction for distinction in distinctions)


def remainder(row, equations):
    while row and row.bit_length() in equations:
        row ^= equations[row.bit_length()]
    return row


def join_groups(places, holders, active):
    """Read common holders directly from the distinctions held by live knots."""
    through = defaultdict(set)
    for knot in active:
        for d in places[knot]:
            for other in holders[d]:
                if other != knot:
                    through[other].add(knot)
    by_knot = defaultdict(list)
    for group in through.values():
        if len(group) >= 2:
            for member in group:
                by_knot[member].append(group)
    pairs = {pair for group in through.values() for pair in combinations(sorted(group), 2)}
    candidate = nx.Graph()
    candidate.add_edges_from(pairs)
    groups = []
    covered = set()
    for clique in nx.find_cliques(candidate):
        if len(clique) >= 3 and not any(group.issuperset(clique) for group in by_knot[clique[0]]):
            join = tuple(sorted(clique))
            groups.append(join)
            covered.update(combinations(join, 2))
    return sorted(groups) + sorted(pairs - covered)


def holdings_growth(stars, law, horizon, bound=30000, reader=None):
    """Carry the actual holdings and decide parity by reduction of binary rows."""
    places = [list(knots) for knots in stars]
    holders = defaultdict(list)
    for knot, distinctions in enumerate(places):
        for d in distinctions:
            holders[d].append(knot)
    assert all(len(roster) in (1, 2) for roster in holders.values())
    fresh_distinction = max(holders, default=-1) + 1
    active = {k: [d for d in distinctions if len(holders[d]) == 1]
              for k, distinctions in enumerate(places)}
    active = {k: opened for k, opened in active.items() if opened}
    descriptions = [('start', 0, 0, len(distinctions)) for distinctions in stars]
    follows_reader = [k == reader for k in range(len(stars))] if reader is not None else None
    equations = {}
    if law == 'parity':
        for distinctions in places:
            signed = remainder(bitrow(distinctions), equations)
            if signed:
                equations[signed.bit_length()] = signed

    rounds = []
    groups = join_groups(places, holders, active)
    for rnd in range(1, horizon + 1):
        if not active:
            return rounds, f'closes at round {rnd}', len(places)
        use = Counter(k for parents in groups for k in parents)
        if any(use[k] > len(opened) for k, opened in active.items()):
            return rounds, f'stalls at round {rnd}', len(places)
        births = groups + [(k,) for k, opened in active.items() for _ in range(len(opened) - use[k])]
        supply = {k: iter(opened) for k, opened in active.items()}
        new_ids = list(range(len(places), len(places) + len(births)))
        implied = []
        for knot, parents in zip(new_ids, births):
            given = [next(supply[k]) for k in parents]
            places.append(given)
            for d in given:
                holders[d].append(knot)
            implied.append(law == 'parity' and remainder(bitrow(given), equations) == 0)
        following_groups = join_groups(places, holders, new_ids)
        demand = Counter(knot for parents in following_groups for knot in parents)
        active = {}
        first, second = Counter(), Counter()
        for knot, parents, redundant in zip(new_ids, births, implied):
            if redundant:
                assert demand[knot] == 0
                fresh = 0
            else:
                fresh = max(demand[knot], 3 - len(parents), 1)
                opened = list(range(fresh_distinction, fresh_distinction + fresh))
                for d in opened:
                    holders[d].append(knot)
                places[knot].extend(opened)
                active[knot] = opened
                fresh_distinction += fresh
                if law == 'parity':
                    row = bitrow(places[knot])
                    equations[row.bit_length()] = row
            kind = 'offshoot' if len(parents) == 1 else 'join'
            desc = (kind, len(parents), fresh, len(places[knot]))
            descriptions.append(desc)
            if follows_reader is not None:
                follows_reader.append(any(follows_reader[parent] for parent in parents))
                if not follows_reader[-1]:
                    continue
            first[desc] += 1
            second[desc, tuple(sorted(descriptions[parent] for parent in parents))] += 1
        rounds.append((first, second))
        if bound is not None and len(places) > bound:
            return rounds, 'bound', len(places)
        groups = following_groups
    return rounds, 'rounds', len(places)


def compare_views(expected, actual):
    return [(r, field) for r, (left, right) in enumerate(zip(expected, actual), 1)
            for i, field in enumerate(('sig0', 'sig1')) if left[i] != right[i]]


def replay_record(rec, law, horizon):
    expected = [readings(row) for row in rec['rows'][:horizon]]
    actual, end, knots = holdings_growth(rec['stars'], law, horizon)
    if horizon == 1 and expected:
        expected_end = 'rounds'
        expected_knots = len(rec['stars']) + rec['rows'][0]['n']
    else:
        expected_end, expected_knots = rec['end'], rec['knots']
    diffs = compare_views(expected, actual)
    assert len(expected) == len(actual) and end == expected_end and knots == expected_knots and not diffs, (
        law, rec['index'], horizon, len(expected), len(actual), diffs[:2], end, expected_end, knots, expected_knots)
    return len(expected), knots - len(rec['stars'])


def replay_selection(records):
    eligible = [rec for rec in records if rec['rows']]
    groups = defaultdict(list)
    for rec in eligible:
        groups[rec['end'], len(rec['rows'])].append(rec)
    selected = {records[0]['index']}
    selected.update(r['index'] for r in Random(SEED).sample(eligible, 80))
    for group in groups.values():
        selected.add(group[0]['index'])
        selected.add(max(group, key=lambda r: max(row['n'] for row in r['rows']))['index'])
    return selected


def replay_five(records, law, pilot):
    selected = replay_selection(records)
    if pilot:
        largest = max((r for r in records if r['rows']), key=lambda r: max(row['n'] for row in r['rows']))
        first = [r for r in records[:8] if r['index'] != largest['index']]
        replay = first + [largest]
        selected &= {r['index'] for r in first}
        selected.add(largest['index'])
    else:
        replay = records
    counts = Counter()
    started = perf_counter()
    for rec in replay:
        index = rec['index']
        horizon = 24 if index in selected else 1
        case_start = perf_counter()
        rounds, births = replay_record(rec, law, horizon)
        if pilot and horizon == 24:
            print(f'{law} index {index} {rounds} rounds {births} births {perf_counter() - case_start:.3f}s', flush=True)
        counts['starts checked through round one or its stall'] += 1
        counts['starts checked through their last saved round'] += horizon == 24
        counts['compared birth rounds'] += rounds
        counts['compared births'] += births
    return {'counts': counts, 'last-saved-round replay indices': sorted(selected),
            'seconds': round(perf_counter() - started, 4)}


def roster_readings(rollout, horizon):
    return [r for r in rollout.views(None, horizon) if any(r)]


def replay_four(records, pilot):
    from growth import Roster, grow

    counters = {}
    for law in LAWS:
        started = perf_counter()
        counts = Counter()
        end_counts = Counter()
        if pilot:
            largest = max(records, key=lambda r: max((row['n'] for row in r['rows']), default=0))
            replay = records[:3] + [largest]
        else:
            replay = records
        for rec in replay:
            stars = rec['stars']
            places = list(map(len, stars))
            pairs = [(a, b) for a, b in combinations(range(4), 2) if set(stars[a]).intersection(stars[b])]
            holdings, end, _ = holdings_growth(stars, law, 24)
            assert end != 'bound'
            model = grow(Roster.from_graph(places, pairs), 24, law, cap=30000)
            roster = roster_readings(model, 24)
            assert len(holdings) == len(roster) and not compare_views(holdings, roster), (law, rec['index'])
            status = 'stall' if end.startswith('stalls') else 'closed' if end.startswith('closes') else end
            assert status == model.end, (law, rec['index'], status, model.end)
            if law == 'nae':
                old = [readings(row) for row in rec['rows']]
                assert not compare_views(old, holdings[:20]) and len(old) == min(20, len(holdings))
                assert rec['end'] == end
                counts['birth rounds compared to the predecessor archive'] += len(old)
            counts['starts'] += 1
            counts['birth rounds compared between both replays'] += len(holdings)
            counts['births compared between both replays'] += sum(sum(first.values()) for first, _ in holdings)
            end_counts[len(holdings), end, model.end] += 1
        counters[law] = {'counts': counts, 'end and round counts': table_histogram(end_counts.elements()),
                         'seconds': round(perf_counter() - started, 4)}
    return counters


def comparison_controls(records):
    first_round = readings(next(r for r in records if r['rows'])['rows'][0])
    first, second = first_round
    reading = next(iter(first))
    altered_offspring = first.copy()
    altered_offspring[reading[:2] + (reading[2] + 1, reading[3] + 1)] += altered_offspring.pop(reading)
    pair = next(iter(second))
    parents = pair[1]
    changed_parent = parents[-1][:3] + (parents[-1][3] + 1,)
    altered_parents = second.copy()
    altered_parents[pair[0], parents[:-1] + (changed_parent,)] += altered_parents.pop(pair)
    assert sum(altered_offspring.values()) == sum(first.values())
    assert sum(altered_parents.values()) == sum(second.values())
    tally = {
        'changed first reading while preserving the birth total is detected':
            compare_views([first_round], [(altered_offspring, second)]) == [(1, 'sig0')],
        'changed parent reading while preserving the first reading and birth total is detected':
            compare_views([first_round], [(first, altered_parents)]) == [(1, 'sig1')],
        'changed stopping behavior on a zero-round reference escapes a prefix comparison':
            not compare_views([], [first_round]) and len([first_round]) != len([]),
    }
    assert all(tally.values())
    return tally


def disconnected_control():
    from growth import Roster, grow

    # Three pairwise-touching three-place knots and an isolated three-place knot.
    stars = [[0, 1, 3], [0, 2, 4], [1, 2, 5], [6, 7, 8]]
    roster = Roster.from_holdings(stars)
    differences = {}
    for law in LAWS:
        holdings, _, _ = holdings_growth(stars, law, 1)
        reads = roster_readings(grow(roster, 1, law), 1)
        difference = compare_views(holdings, reads)
        if law == 'nae':
            assert not difference
        else:
            assert difference == [(1, 'sig0'), (1, 'sig1')]
        differences[law] = {'mismatches [round, reading]': difference,
                            'explicit holdings first reading': sorted(holdings[0][0].items()),
                            'roster first reading': sorted(reads[0][0].items())}
    return {'starting holdings': stars, 'readings': differences}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--logs-only', action='store_true')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    limit = 2 << 30
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    started = perf_counter()
    small = LOOK / 'phase1_grown.jsonl.gz'
    four = raw_archive(small, census_ids(4), 20)
    ids = census_ids(5)
    result = {'pilot': args.pilot, 'pinned comparison logs': RESULT_COMMIT, 'sample seed': SEED,
              'four-knot not-all-equal archive': archive_inventory(small, four),
              'comparator controls': comparison_controls(four), 'five knots': {}}
    tree = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', RESULT_COMMIT, str(STUDY.relative_to(ROOT))],
                                   cwd=ROOT, text=True)
    result['four-knot comparison logs present in the result commit'] = any('verify_4' in p for p in tree.splitlines())
    if not args.logs_only:
        result['four-knot replay'] = replay_four(four, args.pilot)
        result['disconnected-presentation control'] = disconnected_control()
        print('Four-knot replay and disconnected control complete.', flush=True)
    for law, file in zip(LAWS, ('grown_g5_nae.jsonl.gz', 'grown_g5_par.jsonl.gz')):
        path = BOUND / file
        five = raw_archive(path, ids, 24)
        result['five knots'][law] = {'matching growth archive': archive_inventory(path, five),
                                    'comparison logs': verification_logs(law, five)}
        if not args.logs_only:
            result['five knots'][law]['replay'] = replay_five(five, law, args.pilot)
            print(f'Five-knot {law} replay complete.', flush=True)
    result['total seconds'] = round(perf_counter() - started, 4)
    args.output.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
