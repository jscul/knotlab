"""Recount the archived sample coverage and verify the identical-state control."""

import argparse
from collections import Counter, deque
from itertools import combinations, islice
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[1] / 'SELECTED-KNOTS-20261127-001'
SETS = ('census', 'heldout', 'sampled', 'built')


def steps(start, neighbours):
    distance = {start: 0}
    pending = deque([start])
    while pending:
        current = pending.popleft()
        for other in sorted(neighbours[current]):
            if other not in distance:
                distance[other] = distance[current] + 1
                pending.append(other)
    return distance


def merge_levels(leaves, pair_steps):
    """Collect the thresholds at which the family components change."""
    clusters = {frozenset([leaf]) for leaf in leaves}
    merging_levels = []
    for threshold in sorted(set(pair_steps.values())):
        neighbours = {leaf: set() for leaf in leaves}
        for (a, b), cost in pair_steps.items():
            if cost <= threshold:
                neighbours[a].add(b)
                neighbours[b].add(a)
        stage = {frozenset(steps(leaf, neighbours)) for leaf in leaves}
        if not stage <= clusters:
            merging_levels.append(threshold)
            clusters.update(stage)
    return merging_levels


def linear_span(vectors):
    span = {0}
    for vector in vectors:
        span |= {old ^ vector for old in span}
    return span


def recount(label, limit):
    counts = Counter()
    failures = []
    shortest_reading = Counter()
    with (ARCHIVE / f'frozen_{label}.jsonl').open() as records:
        for line in islice(records, limit):
            start = json.loads(line)
            size = start['families']
            counts['start records'] += 1
            counts[f'starts with {size} families'] += 1
            if size < 2:
                continue
            counts['starts with pairs'] += 1
            pair_steps = {tuple(map(int, key.split('-'))): value
                          for key, value in start['distances'].items()}
            assert set(pair_steps) == set(combinations(range(size), 2))
            if 'SK4' in start:
                counts['hierarchies read'] += 1
                counts['hierarchies with nonconstant class facts'] += bool(start['SK4']['layer-three dimension'])
            for row in start['rounds']:
                if 'end' in row:
                    counts['first omitted round: ' + row['end']] += 1
                    continue
                counts['round records'] += 1
                counts['pair records'] += len(pair_steps)
                counts['direct cost failures'] += len(row['SK1 failures'])
                for a, b, d, measured in row['SK1 failures']:
                    t = row['round']
                    two_step_costs = {c: pair_steps[tuple(sorted((a, c)))] +
                                      pair_steps[tuple(sorted((b, c)))] + 2 * (2 + 2 * t)
                                      for c in range(size) if c not in (a, b)}
                    failures.append({'start': start['start'], 'round': t, 'pair': [a, b],
                                     'direct step count': d, 'direct cost': d + 2 + 2 * t,
                                     'recorded cost': measured, 'two steps by intermediate': two_step_costs})
                for scale in (8, 12):
                    criterion = row.get(f'SK3 k={scale}')
                    if criterion is None:
                        continue
                    counts[f'scale {scale} records'] += 1
                    value = criterion['dimension']
                    if value == 0:
                        counts[f'scale {scale} zero dimension'] += 1
                    elif value == size - 1:
                        counts[f'scale {scale} full dimension'] += 1
                    else:
                        counts[f'scale {scale} intermediate dimension'] += 1
                if 'shortest reading: kept sums' in row:
                    kept = row['shortest reading: kept sums']
                    key = f"round {row['round']}: "
                    shortest_reading[key + 'records'] += 1
                    shortest_reading[key + 'any fact'] += bool(kept)
                    shortest_reading[key + 'all facts'] += kept == (1 << (size - 1)) - 1
    return {'counts': counts, 'shortest reading': shortest_reading,
            'direct cost failure witnesses': failures}


def identical_state_control():
    """Omitting any one holder law gives the same allowed states in this control."""
    links = [(i, (i + 1) % 10) for i in range(10)] + [(0, 4), (1, 6)]
    distinctions = [link for link in links for _ in range(2)]
    rows = {node: sum(1 << i for i, link in enumerate(distinctions) if node in link)
            for node in range(10)}
    control = {}
    row_spans = []
    for omitted in (0, 1):
        knots = set(rows) - {omitted}
        row_spans.append(linear_span(rows[node] for node in knots))
        neighbours = {node: set() for node in knots}
        live = set()
        for a, b in links:
            if omitted in (a, b):
                live.add(b if a == omitted else a)
            else:
                neighbours[a].add(b)
                neighbours[b].add(a)
        assert len(steps(min(knots), neighbours)) == len(knots)
        assert all(not (neighbours[a] & neighbours[b]) for a, b in combinations(sorted(live), 2))
        pair_steps = {(a, b): steps(a, neighbours)[b] for a, b in combinations(sorted(live), 2)}
        control[str(omitted)] = {
            'connected': True,
            'singleton families': sorted(live),
            'pair steps': {f'{a}-{b}': d for (a, b), d in pair_steps.items()},
            'distinct merge levels': merge_levels(live, pair_steps),
            'knot arities': [rows[n].bit_count() for n in sorted(knots)],
        }
    assert row_spans[0] == row_spans[1]
    assert control['0']['distinct merge levels'] != control['1']['distinct merge levels']
    rank = len(row_spans[0]).bit_length() - 1
    return {'distinctions by their two bookkeeping holders': distinctions,
            'allowed-state counts in each': 1 << (len(distinctions) - rank),
            'constraint rank in each': rank,
            'identical constraint spans on the same distinctions': True,
            'starts by omitted holder': control}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, help='maximum start records to read per set')
    args = parser.parse_args()
    print(json.dumps({'start limit per set': args.limit,
                      'sets': {label: recount(label, args.limit) for label in SETS},
                      'identical allowed states control': identical_state_control()}, indent=2))


if __name__ == '__main__':
    main()
