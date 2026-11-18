"""Decode permitted complete-round allocations from an anonymous scalar table."""

from collections import Counter, defaultdict
from itertools import combinations, product


def twin_classes(neighbors):
    """Classify rows equal away from their two own positions (including the far color)."""
    by_row = defaultdict(list)
    for i, row in enumerate(neighbors):
        for color in {None, *row.values()}:
            filled = row if color is None else {**row, i: color}
            by_row[(color, tuple(sorted(filled.items())))].append(i)
    return sorted(tuple(group) for group in by_row.values() if len(group) > 1)


def read_frontier(neighbors):
    """Input rows give only distances at most five. More distant entries are omitted."""
    twins = twin_classes(neighbors)
    terminal = [group for group in twins if len(group) == 3]
    incoming = {}
    for group in terminal:
        row = neighbors[group[0]]
        shortest = min(row.values())
        star = {group[0], *(j for j, value in row.items() if value == shortest)}
        if not set(group) <= star:
            raise ValueError("Nearest neighborhood misses a loose sibling")
        incoming[group] = star - set(group)

    adjacent = {group: set() for group in terminal}
    for g, h in combinations(terminal, 2):
        if any(j in neighbors[i] for i in incoming[g] for j in incoming[h]):
            adjacent[g].add(h)
            adjacent[h].add(g)

    # A qualifying triple has pairwise predecessor witnesses, but no single
    # predecessor supports one entering distinction at each of all three.
    pairs = {tuple(sorted((g, h))) for g in terminal for h in adjacent[g]}
    triples = set()
    for g, h in pairs:
        for k in adjacent[g] & adjacent[h]:
            if h >= k:
                continue
            one_predecessor = any(
                j in neighbors[i] and w in neighbors[i] and w in neighbors[j]
                for i, j, w in product(incoming[g], incoming[h], incoming[k])
            )
            if not one_predecessor:
                triples.add((g, h, k))
    covered = {pair for triple in triples for pair in combinations(triple, 2)}
    groups = list(triples | (pairs - covered))
    uses = Counter(g for group in groups for g in group)
    for g in terminal:
        if uses[g] > len(g):
            raise ValueError("Too few loose distinctions for the recovered groups")
        groups.extend([(g,)] * (len(g) - uses[g]))
    return {"triplets": tuple(terminal), "incoming": incoming, "adjacent": adjacent,
            "groups": tuple(sorted(groups))}


def sparse_rows(width, supports):
    """Coordinate-free conversion of a bond list to its scalar table for test inputs."""
    rows = [{} for _ in range(width)]
    for support in supports:
        ids = []
        word = support
        while word:
            bit = word & -word
            ids.append(bit.bit_length() - 1)
            word ^= bit
        distance = len(ids) - 1
        for i, j in combinations(ids, 2):
            if distance < rows[i].get(j, 6):
                rows[i][j] = rows[j][i] = distance
    return rows
