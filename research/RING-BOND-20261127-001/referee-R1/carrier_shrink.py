"""Retest the twelve-knot witness after one-place deletions in any of its six carriers."""
import argparse
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent


def recount(limit):
    source = json.loads((HERE / 'layer_witness.json').read_text())
    knots = source['source_knots_not_all_equal']
    carriers = source['lower_carriers_in_A0_A1_B0_B1_C0_C1_order']
    law_masks = [sum(1 << x for x in law) for law in knots]
    states = [s for s in range(1 << 18) if all(0 < (s & m) < m for m in law_masks)]
    all_rows = (1 << len(states)) - 1
    readings = []
    for c in carriers:
        masks = []
        for choice in [tuple(c), *combinations(c, 2)]:
            name = sum(1 << x for x in choice)
            data = bytes((s & name) in (0, name) for s in states)
            # Compress the Boolean column to a bitset over the 7,570 actual states.
            masks.append(sum(1 << i for i, v in enumerate(data) if v))
        readings.append(masks)
    cross = tuple(product((0, 1), (2, 3), (4, 5)))
    tallies = Counter()
    rows = {}
    for choices in product(range(4), repeat=6):
        val = [bits[j] for bits, j in zip(readings, choices)]
        exclusions = sum(not (val[i] & val[j] & val[k]) for i, j, k in cross)
        upper = [all_rows ^ (val[i] ^ val[i + 1]) for i in (0, 2, 4)]
        absent = [w for w in range(8) if not ((upper[0] if w & 4 else all_rows ^ upper[0])
                                               & (upper[1] if w & 2 else all_rows ^ upper[1])
                                               & (upper[2] if w & 1 else all_rows ^ upper[2]))]
        shrunk = sum(bool(j) for j in choices)
        counts = rows.setdefault(shrunk, Counter())
        counts['carrier choices'] += 1
        counts['all eight lower exclusions persist'] += exclusions == 8
        counts['upper image still excludes only 000'] += absent == [0]
        tallies[f'{exclusions} of the eight lower exclusions retained'] += 1
        if sum(r['carrier choices'] for r in rows.values()) == limit:
            break
    return {'source assignments': len(states), 'lower agreements before shrinking': carriers,
            'by number of carriers shrunk': dict(sorted(rows.items())), 'lower exclusions': tallies}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('limit', type=int)
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    t = perf_counter()
    result = recount(a.limit)
    result['seconds'] = round(perf_counter() - t, 3)
    if a.out:
        a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
