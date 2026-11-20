"""Recompute the frozen filled reading and class from the retained raw draws."""

from collections import Counter
from fractions import Fraction
from itertools import combinations

from sources_span import labels


def binary_rank(words):
    basis = {}
    for word in words:
        while word:
            pivot = word.bit_length()
            if pivot not in basis:
                basis[pivot] = word
                break
            word ^= basis[pivot]
    return len(basis)


def group_demand(live, blocks, candidates):
    coverage = [0] * len(candidates)
    demand = [0] * len(candidates)
    clique = {0: True}
    for subset in range(1, live + 1):
        if subset & ~live:
            continue
        bit = subset & -subset
        u = bit.bit_length() - 1
        rest = subset ^ bit
        clique[subset] = clique[rest] and (rest & ~candidates[u] == 0)
        if not clique[subset] or subset.bit_count() < 3 or any(subset & ~b == 0 for b in blocks):
            continue
        members = labels(subset)
        common = live
        for v in members:
            common &= candidates[v]
        if common:
            continue
        for v in members:
            demand[v] += 1
            coverage[v] |= subset
    return [d + (adj & ~covered).bit_count() for d, adj, covered in zip(demand, candidates, coverage, strict=True)]


def filled_features(sizes, meetings):
    n = len(sizes)
    neighbors = [set() for _ in sizes]
    shared = Counter()
    for a, b in meetings:
        shared.update((a, b))
        neighbors[a].add(b)
        neighbors[b].add(a)
    supply = [size - shared[u] for u, size in enumerate(sizes)]
    points = [u for u in range(n) if supply[u] > 0]
    live = sum(1 << u for u in points)
    families = {w: neighbors[w] & set(points) for w in range(n) if len(neighbors[w] & set(points)) >= 2}
    block_masks = [sum(1 << u for u in members) for members in families.values()]
    of = [set() for _ in sizes]
    incidence = [set() for _ in range(2 * n)]
    numbering = {}
    for w, members in families.items():
        for u in sorted(members):
            of[u].add(w)
            incidence[u].add(n + w)
            incidence[n + w].add(u)
            numbering[u, w] = len(numbering)
    candidates = [sum(1 << v for v in points if v != u and of[u] & of[v]) if u in points else 0
                  for u in range(n)]
    demand = group_demand(live, block_masks, candidates)

    cells = []
    for u, v, w in combinations(points, 3):
        a, b, c = of[u] & of[v], of[v] & of[w], of[w] & of[u]
        if a and b and c and not (a & b & c):
            x, y, z = min(a), min(b), min(c)
            cuts = ((u, x), (v, x), (v, y), (w, y), (w, z), (u, z))
            word = sum(1 << numbering[e] for e in cuts)
            assert word.bit_count() == 6
            cells.append(((u, v, w), (x, y, z), word))

    unseen = set(points)
    b1, b2, rays = [], [], []
    while unseen:
        root = min(unseen)
        seen, pending = {root}, [root]
        while pending:
            found = incidence[pending.pop()] - seen
            seen.update(found)
            pending.extend(found)
        unseen -= seen
        part_cells = [word for holders, _, word in cells if holders[0] in seen]
        rank = binary_rank(part_cells)
        rank_graph = sum(len(incidence[v]) for v in seen) // 2 - len(seen) + 1
        b1.append(rank_graph - rank)
        b2.append(len(part_cells) - rank)
        rays.append(sum((supply[v] - demand[v]) * (2 if supply[v] == 1 else int(supply[v] == 2))
                        for v in seen if v < n))
    if any(b1):
        reading = "cycle left"
    else:
        dimension = max((r if r else (2 if len(rays) >= 2 else 0) for r in rays), default=0)
        reading = f"dimension {dimension}" if dimension else "closes"
    overlap_points = Counter(v for group, _, _ in cells for v in group)
    overlap_blocks = Counter(v for _, family, _ in cells for v in family)
    return {"filled_b1": b1, "filled_b2": b2, "reading": reading, "tri": len(cells),
            "overlap_point": any(n > 1 for n in overlap_points.values()),
            "overlap_block": any(n > 1 for n in overlap_blocks.values()),
            "first_round_funded": all(demand[u] <= supply[u] for u in points),
            "at_most_one_common_holder": all(len(of[u] & of[v]) <= 1 for u, v in combinations(points, 2))}


def measured(outcome, counts):
    dying = {"closed": "closes", "stall": "stall"}
    if outcome in dying:
        return dying[outcome]
    by_lag = {lag: counts[1:] for lag in (1, 2, 3)}
    for degree in range(1, 9):
        need = max(4, degree + 3)
        for lag, current in by_lag.items():
            diff = [b - a for a, b in zip(current, current[lag:])]
            by_lag[lag] = diff
            if len(diff) >= need and not any(diff[-need:]):
                return f"dimension {degree}" + (f" (period {lag})" if lag != 1 else "")
    ratios = [Fraction(b, a) for a, b in zip(counts, counts[1:]) if a]
    if any(r >= 3 for r in ratios[3:]):
        return "explosive"
    last = ratios[-5:]
    if len(last) == 5:
        mean = sum(last) / 5
        if mean > Fraction(21, 20) and all(abs(r - mean) <= Fraction(3, 20) * mean for r in last):
            return "exponential-like"
    return "undecided"


def simple_class(label):
    return label.split(" (")[0]
