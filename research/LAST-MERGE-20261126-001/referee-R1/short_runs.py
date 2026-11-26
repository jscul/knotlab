"""Score shortened runs before and after removing the knot cap, including a separate wider degree screen."""
import argparse
from collections import Counter
import gzip
from itertools import combinations, islice, permutations
import json
from math import comb
from pathlib import Path
from time import perf_counter

OUT = Path(__file__).resolve().parent


def normalized(row, key):
    return {json.dumps(k, separators=(',', ':')): n for k, n in row[key]}


def first_births_up_to_renaming(stars):
    """Enumerate eligible subsets directly and retain each maximal join and single-parent birth."""
    knots = list(map(set, stars))
    frequency = Counter(x for knot in knots for x in knot)
    loose = [sum(frequency[x] == 1 for x in knot) for knot in knots]
    live = [i for i, n in enumerate(loose) if n]
    neighbours = [set(j for j, knot in enumerate(knots) if i != j and knot & here)
                  for i, here in enumerate(knots)]
    blocks = [set(live).intersection(block) for block in neighbours]
    pairs = [set(pair) for pair in combinations(live, 2) if any(set(pair) <= block for block in blocks)]
    groups = [set(group) for size in range(3, len(live) + 1) for group in combinations(live, size)
              if all(set(pair) in pairs for pair in combinations(group, 2))
              and not any(set(group) <= block for block in blocks)]
    joins = [g for g in groups if not any(g < h for h in groups)]
    joins += [p for p in pairs if not any(p <= g for g in groups)]
    children = joins.copy()
    for i in live:
        remainder = loose[i] - sum(i in j for j in joins)
        assert remainder >= 0
        children.extend([{i}] * remainder)
    ordered_loose = sorted(loose)
    return min(tuple(sorted(tuple(sorted(names[i] for i in group)) for group in children))
               for names in permutations(range(len(loose)))
               if all(loose[i] == ordered_loose[j] for i, j in enumerate(names)))


def dimension(counts, maximum):
    tail = counts[-8:]
    if len(counts) >= 10:
        for d in range(1, maximum + 1):
            if tail[0] > 0 and min(tail) == max(tail):
                return d
            tail = [b - a for a, b in zip(tail, tail[1:])]
    return None


def cut(rows, reading, d):
    by_round = [normalized(r, reading) for r in rows]
    kinds = set().union(*by_round)
    for k in range(max(3, d), len(rows) - 1):
        for kind in kinds:
            sample = [r.get(kind, 0) for r in by_round[k-d:k]]
            coefficients = []
            while sample:
                coefficients.append(sample[0])
                sample = [b - a for a, b in zip(sample, sample[1:])]
            if any(sum(c * comb(t, j) for j, c in enumerate(coefficients)) != r.get(kind, 0)
                   for t, r in enumerate(by_round[k:], d)):
                break
        else:
            return k
    return None


def observations(rows, m):
    counts = [r['n'] for r in rows]
    t = max((j for j in range(2, len(counts) + 1) if counts[j-1] < counts[j-2]), default=1)
    frozen_d = dimension(counts, 4)
    wider_d = dimension(counts, 6)
    readings = {}
    if wider_d is not None:
        for reading, offset in [('sig0', 3), ('sig1', 5)]:
            k = cut(rows, reading, wider_d)
            bound = max(m + offset + 2, t + offset)
            readings[reading] = {'K': k, 'meets horizon-specific D rule': k is not None and k <= len(rows) - wider_d,
                                 'combined bound': bound, 'late': None if k is None else k > m + offset + 2,
                                 'within bound': None if k is None else k <= bound,
                                 'K minus T': None if k is None else k-t}
    return {'last round': len(rows), 'T': t, 'D in 1 to 4': frozen_d, 'D in 1 to 6': wider_d, 'readings': readings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extension', type=Path, help='independent growth with the knot cap removed')
    parser.add_argument('--pilot', action='store_true', help='first two shortened records per law')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = perf_counter()
    extended = {}
    if args.extension:
        obj = json.loads(args.extension.read_text())
        assert not obj['differences']
        extended = {(x['knot law'], x['index']): x for x in obj['records checked'] if 'rows' in x}
    records = []
    tally = Counter()
    used = set()
    grouped = {}
    for law in ['nae', 'parity']:
        with gzip.open(OUT.parent / f'grown_fresh_{law}.jsonl.gz', 'rt') as f:
            originals = (x for x in map(json.loads, f) if x['end'] == 'bound' and len(x['rows']) < 24)
            if args.extension:
                originals = (x for x in originals if (law, x['index']) in extended)
            for x in islice(originals, 2 if args.pilot else None):
                key = (law, x['index'])
                old = x['rows']
                rec = {'census index': x['index'], 'law': law, 'M': x['M'], 'before': observations(old, x['M'])}
                plan = first_births_up_to_renaming(x['stars'])
                assert len(plan) == old[0]['n']
                group = grouped.setdefault(plan, {'indices': set(), 'laws': set(), 'suffix': None})
                group['indices'].add(x['index'])
                group['laws'].add(law)
                label = rec['before']['D in 1 to 4']
                assert x['kind'] == ('unread' if label is None else f'dim {label}')
                if args.extension:
                    new = extended[key]
                    used.add(key)
                    assert x['M'] == new['M'] and x['stars'] == new['stars']
                    assert len(new['rows']) == 24
                    for r0, r1 in zip(old, new['rows']):
                        assert r0['n'] == r1['n']
                        for reading in ('sig0', 'sig1'):
                            assert normalized(r0, reading) == normalized(r1, reading)
                    rec['after'] = observations(new['rows'], x['M'])
                    # Only a sole birth can take every loose distinction and distinguish the laws.
                    assert min(r['n'] for r in new['rows']) > 1
                    suffix = [(r['n'], normalized(r, 'sig0'), normalized(r, 'sig1')) for r in new['rows'][1:]]
                    if group['suffix'] is not None:
                        assert group['suffix'] == suffix
                    group['suffix'] = suffix
                    amt = rec['after']
                    for reading, score in amt['readings'].items():
                        tally[f'{law} / D {amt["D in 1 to 6"]} / {reading} / late {score["late"]} / within {score["within bound"]}'] += 1
                records.append(rec)
    if args.extension and not args.pilot:
        assert used == set(extended)
    classes = [{'first-round parent sets, with repeated offshoots': plan, 'census indices': sorted(g['indices']),
                'laws': sorted(g['laws'])} for plan, g in grouped.items()]
    output = {'seconds': round(perf_counter() - start, 3), 'records': records, 'counts': dict(sorted(tally.items())),
              'first-round classes': classes,
              'degree screen': 'The frozen screen allows D in 1 through 4. Values 5 and 6 are descriptive checks outside the freeze.'}
    args.output.write_text(json.dumps(output, indent=2) + '\n')
    print(len(records), output['seconds'], output['counts'])


if __name__ == '__main__':
    main()
