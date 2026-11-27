"""Read the archived census and compute families from the shared distinctions."""
from collections import deque
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "FORBID-EDITS-20261126-001" / "starts.json"


def roster():
    starts = []
    for count, meetings, loose in json.loads(SOURCE.read_text()):
        rows = [0] * count
        bit = 1
        for left, right, copies in meetings:
            for _ in range(copies):
                rows[left] |= bit
                rows[right] |= bit
                bit <<= 1
        for holder, amount in enumerate(loose):
            rows[holder] |= ((1 << amount) - 1) * bit
            bit <<= amount
        starts.append(tuple(rows))
    return starts


def neighbors(rows):
    return [{j for j, other in enumerate(rows) if i != j and r & other}
            for i, r in enumerate(rows)]


def distances(links, seeds):
    found = dict.fromkeys(seeds, 0)
    todo = deque(found)
    while todo:
        i = todo.popleft()
        for j in links[i]:
            if j not in found:
                found[j] = found[i] + 1
                todo.append(j)
    return found


def connected(rows):
    return bool(rows) and len(distances(neighbors(rows), [0])) == len(rows)


def components(links, indices):
    todo = set(indices)
    groups = []
    while todo:
        group = distances(links, [min(todo)]).keys()
        groups.append(tuple(sorted(group)))
        todo.difference_update(group)
    return groups


def tree(rows):
    """Return named family groups and threshold partitions as sorted masks.

    Across disconnected pieces no finite meeting route exists. The last
    threshold 10**9 matches the archive's convention for that case.
    """
    links = neighbors(rows)
    once = shared = 0
    for r in rows:
        shared |= once & r
        once |= r
    loose = [r & ~shared for r in rows]
    live = [i for i, mask in enumerate(loose) if mask]
    candidates = {i: {j for j in live if i != j and links[i] & links[j]} for i in live}
    families = components(candidates, live)
    masks = [sum(loose[i] for i in group) for group in families]
    costs = {}
    for a, g in enumerate(families):
        walk = distances(links, g)
        for b in range(a):
            costs[a, b] = min(walk.get(i, 10**9) for i in families[b])
    thresholds = []
    for t in sorted(set(costs.values())):
        same = [set() for _ in families]
        for (a, b), d in costs.items():
            if d <= t:
                same[a].add(b)
                same[b].add(a)
        groups = components(same, range(len(families)))
        thresholds.append((t, tuple(sorted(sum(masks[i] for i in g) for g in groups))))
    return tuple(sorted(masks)), tuple(thresholds)
