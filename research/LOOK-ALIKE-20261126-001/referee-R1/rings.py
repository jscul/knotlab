"""Match the census to the proved five-knot ring counts and read equal-rate pairs."""
import argparse
from collections import defaultdict
from itertools import combinations
import gzip
import json
from math import comb
from pathlib import Path
from time import monotonic

HERE = Path(__file__).resolve().parent


def ring_order(stars):
    holds = list(map(set, stars))
    neighbours = [[j for j, other in enumerate(holds) if i != j and own & other]
                  for i, own in enumerate(holds)]
    if len(stars) != 5 or any(len(group) != 2 for group in neighbours):
        return None
    order = [0, min(neighbours[0])]
    while len(order) < 5:
        order.append(next(j for j in neighbours[order[-1]] if j != order[-2]))
    return [order[(2 * i) % 5] for i in range(5)]


def round_count(word, t):
    # A round-t member has t+1 distinctions on the count in Theorem 3:
    # a consecutive run in join order and any selection of its leftovers.
    total = 0
    for position in range(5):
        available = 0
        for length in range(1, t + 2):
            available += word[(position + length - 1) % 5]
            remaining = t + 1 - length
            if remaining <= available:
                total += comb(available, remaining)
    return total


def rate(total_leftovers):
    low, high = 1., 2.
    for _ in range(50):
        x = (low + high) / 2
        if x ** (5 + total_leftovers) < (x + 1) ** total_leftovers:
            low = x
        else:
            high = x
    return (low + high) / 2


def pair_read(first, second, reading):
    nested_rounds, equal_rounds = [], []
    for t, (left, right) in enumerate(zip(first['rows'], second['rows']), 1):
        a, b = ({json.dumps(k): v for k, v in r[reading]} for r in (left, right))
        if all(v <= b.get(k, 0) for k, v in a.items()) or all(v <= a.get(k, 0) for k, v in b.items()):
            nested_rounds.append(t)
        if a == b:
            equal_rounds.append(t)
    last = min(len(first['rows']), len(second['rows']))
    return {'common_rounds': last, 'nested_rounds': nested_rounds, 'equal_rounds': equal_rounds,
            'suffix_onset': next((t for t in range(1,last+1) if
                                  all(r in nested_rounds for r in range(t,last+1))), None)}


def main(pilot):
    results, pairs, counts = [], [], defaultdict(list)
    t0 = monotonic()
    candidates = 0
    with gzip.open(HERE.parent / 'phase2_grown.jsonl.gz', 'rt') as data:
        for line in data:
            x = json.loads(line)
            order = ring_order(x['stars'])
            if not order:
                continue
            candidates += 1
            word = [x['loose'][k] - 2 for k in order]
            if min(word) < 0:
                assert x['end'] == 'stalls at round 1'
                continue
            counts[sum(word)].append(x)
            observed = [r['n'] for r in x['rows']]
            expected = [round_count(word,t) for t in range(1,len(observed)+1)]
            results.append({'five_knot_census_index': x['index'], 'leftovers_in_join_order': word,
                            'rate_from_ring_theorem': rate(sum(word)), 'recorded_label': x['kind'],
                            'saved_rounds': len(observed), 'end': x['end'],
                            'formula_disagreements': [t for t,(a,b) in enumerate(zip(observed,expected),1)
                                                      if a != b]})
            if pilot and len(results) == 3:
                break
    for leftovers, group in counts.items():
        for a, b in combinations(group, 2):
            pairs.append({'leftovers': leftovers, 'five_knot_indices': [a['index'],b['index']],
                          **{reading: pair_read(a,b,reading) for reading in ('sig0','sig1')}})
    output = {'ring_starts_examined': candidates, 'funded_rings': results, 'equal_rate_pairs': pairs,
              'seconds': round(monotonic() - t0, 4)}
    name = 'rates_pilot.json' if pilot else 'rates.json'
    (HERE / name).write_text(json.dumps(output, indent=2) + '\n')
    print(name, output['seconds'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    main(parser.parse_args().pilot)
