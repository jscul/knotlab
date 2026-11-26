"""Count the longest simple cycle made of shared distinctions in each sampled start.

A pair of knots sharing two distinctions supplies a length-two cycle.
Only the starting holdings are read. No grown classes are inferred.
"""
import argparse
from collections import Counter, defaultdict
import json
from archive import records
from starts import census_start, extension_start


def longest(knots):
    held = defaultdict(list)
    for i, knot in enumerate(knots):
        for d in knot:
            held[d].append(i)
    meetings = Counter(tuple(v) for v in held.values() if len(v) == 2)
    partners = [set() for _ in knots]
    for i, j in meetings:
        partners[i].add(j)
        partners[j].add(i)
    best = 2 if any(m >= 2 for m in meetings.values()) else 0
    for first, peers in enumerate(partners):
        pending = [(p, {first, p}) for p in peers if first < p]
        while pending:
            end, used = pending.pop()
            if len(used) >= 3 and first in partners[end]:
                best = max(best, len(used))
            pending.extend((p, used | {p}) for p in partners[end] if p > first and p not in used)
    return best


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot', action='store_true')
    args = p.parse_args()
    result = {}
    for kind, loader in [('census', census_start), ('extension', extension_start)]:
        ids = sorted({int(r['structure'].split()[-1]) for r in records(kind)})
        # One start in each nonempty source shard exercises the same reads in the pilot.
        if args.pilot:
            ids = [next(v for v in ids if v // 1000 == shard) for shard in sorted({v // 1000 for v in ids})]
        result[kind] = Counter(longest(loader(i)) for i in ids)
    print(json.dumps(result, indent=1, sort_keys=True))
