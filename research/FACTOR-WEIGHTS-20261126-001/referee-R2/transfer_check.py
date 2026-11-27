"""Check the weighting of reached states for one founder under the recorded transfer law."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import resource
import sys
from time import perf_counter


def run(limit):
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root / 'experiments/RING-TO-END-20261119-001'
                           / 'RING-TO-END-20261119-001-E001_transfer'))
    import transfer

    founders = (frozenset({0, 1}), frozenset(), frozenset({0, 2}), frozenset({1, 2}))
    cube = [frozenset(i for i, bit in enumerate(bits) if bit)
            for bits in product((0, 1), repeat=9)]
    results = {}
    for mode in ('exact_two', 'minimum'):
        weights, histories = Counter(), set()
        for old in founders[:limit]:
            plan = transfer.round_plan(((0, 1, 2),), old)
            first = transfer.realize(plan, mode)
            options = [transfer.lift_options(b, old, mode) for b in first['births']]
            choices = list(product(*options))
            for choice in choices:
                selector = iter(choice)
                step = transfer.realize(plan, mode, pick=lambda birth, opts: next(selector))
                weights[frozenset(step['occupied'])] += Fraction(1, limit*len(choices))
                histories.add(step['stars'])
        assert sum(weights.values()) == 1
        scopes, = histories
        local = [{w.intersection(row) for w in weights} for row in scopes]
        admitted_by_product = [w for w in cube if all(w.intersection(row) in part
                                                      for row, part in zip(scopes, local))]
        target = frozenset({0, 1, 3, 5})
        # Reader A has the first two old distinctions and both of their fresh pairs.
        # Reader B has the third fresh pair. Distinction 2 is the whole complement.
        left, right = {0, 1, 3, 4, 5, 6}, {7, 8}
        assert all(left.isdisjoint(row) or right.isdisjoint(row) for row in scopes)
        event_table = [[0, 0], [0, 0]]
        for w, mass in weights.items():
            if 2 not in w:
                event_table[int(0 in w)][int(7 in w)] += mass
        results[mode] = dict(listed_scopes=scopes, reached=len(weights), states_from_local_supports=len(admitted_by_product),
                             counts_by_weight={str(w): n for w, n in Counter(weights.values()).items()},
                             local_pattern_counts=[len(part) for part in local],
                             target_reached=target in weights, target_locally_admitted=target in admitted_by_product,
                             reader_events_at_zero=event_table)
    return results


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--old', type=int, choices=(1, 4), required=True)
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2**30, 2**30))
    t = perf_counter()
    result = run(args.old)
    result.update(seconds=round(perf_counter()-t, 4), peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print(json.dumps(result, default=str, indent=2))
