"""Count the two structural histories of the recorded three-founder veto control."""
import argparse
from collections import Counter, defaultdict
from itertools import islice, product
import json
from pathlib import Path
import resource
import sys
from time import perf_counter


def run(limit):
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root / 'experiments/STATE-FEEDS-GROWTH-20261119-001'
                           / 'STATE-FEEDS-GROWTH-20261119-001-E001_feedback'))
    import growth

    start = ((0, 2, 3), (0, 1, 6), (1, 4, 5))
    allowed = (s for s in product((0, 1), repeat=7)
               if all(sum(s[d] for d in row) % 2 == 0 for row in start))
    histories = defaultdict(list)
    for word in islice(allowed, limit):
        old = {d for d, v in enumerate(word) if v}
        frame = growth.step(start, old, ('P', 'V'))
        assert frame['status'] == 'extend'
        histories[frame['stars']].append(frozenset(frame['occupied']))
    counts = {len(rows)-len(start): len(words) for rows, words in histories.items()}
    if limit < 16:
        return dict(by_birth_count=counts)
    assert counts == {4: 1, 5: 15}
    rows, words = next((rows, words) for rows, words in histories.items() if len(rows) == 8)
    left = {2, 3, 7, 8, 9, 10}
    right = {4, 5, 13, 14, 15, 16}
    outside = set.union(*map(set, rows)) - left - right
    assert all(set(row).isdisjoint(left) or set(row).isdisjoint(right) for row in rows)
    counts_with_rest_zero = Counter((tuple(sorted(w & left)), tuple(sorted(w & right)))
                                    for w in words if w.isdisjoint(outside))
    left_values = sorted({a for a, _ in counts_with_rest_zero} | {()})
    right_values = sorted({b for _, b in counts_with_rest_zero} | {()})
    table = [[counts_with_rest_zero[a, b] for b in right_values] for a in left_values]
    assert table == [[0, 1], [1, 1]]
    return dict(start=start, by_birth_count=counts, five_birth_scopes=rows, left=sorted(left),
                right=sorted(right), outside=sorted(outside), left_values=left_values,
                right_values=right_values, counts_at_zero_outside=table)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--states', type=int, choices=(2, 16), required=True)
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2**30, 2**30))
    start_time = perf_counter()
    result = run(args.states)
    result.update(seconds=round(perf_counter()-start_time, 4),
                  peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print(json.dumps(result, indent=2))
