"""Find a pair of choices of outside giving different trees after one paid round."""

import argparse
import json
import resource
import time
from collections import deque
from itertools import combinations, islice


def perfect_matchings(remaining, forbidden):
    if not remaining:
        yield ()
        return
    first, *others = remaining
    for second in others:
        if (first, second) not in forbidden:
            rest = [item for item in others if item != second]
            for later in perfect_matchings(rest, forbidden):
                yield ((first, second), *later)


def adjacency(edges):
    neighbors = {}
    for first, second in edges:
        neighbors.setdefault(first, set()).add(second)
        neighbors.setdefault(second, set()).add(first)
    return neighbors


def distances(start, neighbors, excluded):
    found = {start: 0}
    pending = deque([start])
    while pending:
        current = pending.popleft()
        for other in neighbors[current] - excluded - found.keys():
            found[other] = found[current] + 1
            pending.append(other)
    return found


def three_families(neighbors, root, expanded):
    """Keep the three families separate. Traverse the other center's spent births."""
    live = sorted(neighbors[root])
    if any((neighbors[i] & neighbors[j]) - {root} for i, j in combinations(live, 2)):
        return None
    changed = {v: set(adjacent) for v, adjacent in neighbors.items()}
    for child, parent in enumerate(sorted(neighbors[expanded]), start=len(neighbors)):
        changed[expanded].remove(parent)
        changed[parent].remove(expanded)
        changed[expanded].add(child)
        changed[parent].add(child)
        changed[child] = {expanded, parent}
    counts = []
    for index, i in enumerate(live[:-1]):
        found = distances(i, changed, {root})
        counts.extend(found[j] for j in live[index + 1:])
    counts.sort()
    return counts, 'three together' if counts[0] == counts[1] else 'one pair first'


def search(size, limit):
    cycle = {tuple(sorted((i, (i + 1) % size))) for i in range(size)}
    examined = 0
    for extra in islice(perfect_matchings(list(range(size)), cycle), limit):
        examined += 1
        neighbors = adjacency(cycle.union(extra))
        for a, b in combinations(range(size), 2):
            if b in neighbors[a]:
                continue
            one = three_families(neighbors, a, b)
            if not one:
                continue
            other = three_families(neighbors, b, a)
            if other and one[1] != other[1]:
                return examined, dict(cycle_size=size, chords=extra, centers=(a, b),
                                      step_counts=(one, other))
    return examined, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', type=int, required=True)
    parser.add_argument('--limit', type=int, required=True)
    args = parser.parse_args()
    cap = 1536 * 1024**2
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    before = time.perf_counter()
    examined, witness = search(args.size, args.limit)
    print(json.dumps({'examined_matchings': examined, 'witness': witness,
                      'wall_seconds': round(time.perf_counter() - before, 6)}, indent=2))


if __name__ == '__main__':
    main()
