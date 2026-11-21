"""Independent paid-join replay from name-by-name meetings and the ordinary parent rule."""
from collections import Counter
from itertools import combinations, pairwise
from pathlib import Path
import json
import sys

from check_bounded_read import distances

BASE = Path(__file__).resolve().parents[2]
ORDINARY = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(BASE / "experiments" / ORDINARY / (ORDINARY + "-E001_ordinary")))
from end_operator import End, proposals


def paid_groups(n, names, live, radius, suppress=None):
    active = sorted(live)
    live_neighbors = [set() for _ in range(n)]
    for a, b in names:
        if a in live:
            live_neighbors[b].add(a)
        if b in live:
            live_neighbors[a].add(b)
    end = End(dict.fromkeys(active, 1), tuple(tuple(sorted(group)) for group in live_neighbors if group))
    groups = set(proposals(end))
    if radius == "ordinary":
        return groups
    for i, (a, b) in enumerate(names):
        if i == suppress or a in live or b in live:
            continue
        left, right = live_neighbors[a], live_neighbors[b]
        if not left or not right or left & right:
            continue
        remainder = names[:i] + names[i + 1:]
        detour = distances(range(n), remainder, (a,)).get(b)
        if detour is None or radius != "whole" and detour > 2 * radius + 1:
            groups.add(tuple(sorted(left | right)))
    return groups


def remote(length, changed):
    n = 4 + 2 * length
    names = [(0, 1), (0, 2), (1, 3)]
    for end in (0, 1):
        start = 4 + end * length
        names.extend(pairwise([end, *range(start, start + length)]))
    if changed:
        names.append((3 + length, 3 + 2 * length))
    return n, names, dict.fromkeys(range(2, n), 6)


def replay(length, changed, rule, suppress=None):
    n, names, supply = remote(length, changed)
    marked = (2, 3)
    central = tuple(sorted((2, 3, 4, 4 + length)))
    groups = paid_groups(n, names, supply, rule, suppress)
    demand = Counter(h for group in groups for h in group)
    assert all(supply[h] >= demand[h] for h in supply)
    parents = sorted(groups)
    for h, available in supply.items():
        parents.extend([(h,)] * (available - demand[h]))
    assert len(parents) > 1
    children = set(range(n, n + len(parents)))
    next_names = list(names)
    for child, group in zip(sorted(children), parents, strict=True):
        next_names.extend((h, child) for h in group)
    next_groups = paid_groups(n + len(parents), next_names, children, rule)
    next_demand = Counter(h for group in next_groups for h in group)
    fresh = [max(1, 3 - len(group), next_demand[child])
             for child, group in zip(sorted(children), parents, strict=True)]
    left, right = ({n + i for i, g in enumerate(parents) if h in g} for h in marked)
    coinputs = [pair for row in next_groups for pair in combinations(row, 2)]
    separation = distances(children, coinputs, left)
    delay = min((separation[c] for c in right if c in separation), default=None)
    return dict(funded=True, births=len(parents), fresh_names=sum(fresh),
                central_parents=list(central) if central in parents else [],
                central_fresh=fresh[parents.index(central)] if central in parents else None,
                first_common_descendant=None if delay is None else 1 + delay)


def study():
    rows = []
    for length in (3, 5, 8):
        for changed in (False, True):
            cases = {str(k): replay(length, changed, k) for k in ("ordinary", "whole", 2)}
            cases["suppress_central"] = replay(length, changed, 2, 0)
            assert cases["2"]["first_common_descendant"] == 1
            assert cases["whole"]["first_common_descendant"] == (None if changed else 1)
            assert cases["2"]["central_fresh"] > 0
            rows.append(dict(branch_length=length, distal_name=changed, comparative=cases))
    return dict(laws=["parity", "not-all-equal"], reason="Every tested cut has multiple births and is funded.",
                cases=rows)


if __name__ == "__main__":
    print(json.dumps(study(), indent=2))
