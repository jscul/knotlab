"""How deep a network's hole is (epic DEEP-HOLES-20261020-001).

A charge network puts a knot at every vertex of a graph, with the graph's
edges as its distinctions: each vertex asks its edges' flow to equal its
charge mod p. It is impossible when the total charge is nonzero. The depth is
the least number of distinctions linear local reasoning (the affine
relaxation) must hold at once to refute it (DEEP-HOLES-20261020-001B-P001):

- over a ring that computes in the charge group (characteristic p, or Z) the
  depth is the size of one knot, 3 on cubic graphs;
- over every other field it is the toggle width of the graph, whatever the
  charges: the least k such that some sequence of vertex sets from the empty
  set to all vertices, toggling one vertex at a time, keeps every step's
  current cut together with the toggled vertex's edges within k edges;
- the toggle width is at least cutwidth + 1 and at most cutwidth +
  floor(maxdegree / 2); on graphs of maximum degree at most 3 it is exactly
  cutwidth + 1 (CUTWIDTH-DEPTH-20261020-001B-P001).

The program's plain hole criterion cannot see depth: in the complex of partial
solutions, every knot that excludes two or more states is a hole at its own
scope (`scope_hole_rank`).
"""

from __future__ import annotations

import heapq
from fractions import Fraction
from itertools import combinations
from typing import Sequence

from .relations import Relation


def _cut_mask(edges: Sequence[tuple[int, int]], members: int) -> int:
    return sum(1 << i for i, (a, b) in enumerate(edges) if ((members >> a) & 1) != ((members >> b) & 1))


def toggle_width(n: int, edges: Sequence[tuple[int, int]], monotone: bool = False) -> int:
    """Least k with a toggle path from the empty set to all n vertices whose steps cost at most k edges."""
    full = (1 << n) - 1
    stars = [sum(1 << i for i, edge in enumerate(edges) if v in edge) for v in range(n)]
    best = {0: 0}
    heap = [(0, 0)]
    while heap:
        cost, members = heapq.heappop(heap)
        if members == full:
            return cost
        if cost > best[members]:
            continue
        cut = _cut_mask(edges, members)
        for v in range(n):
            if monotone and (members >> v) & 1:
                continue
            step = max(cost, bin(cut | stars[v]).count("1"))
            nxt = members ^ (1 << v)
            if step < best.get(nxt, len(edges) + 1):
                best[nxt] = step
                heapq.heappush(heap, (step, nxt))
    raise ValueError("the graph must be connected")


def cutwidth(n: int, edges: Sequence[tuple[int, int]]) -> int:
    """Least over vertex orderings of the largest number of edges leaving a prefix."""
    width = {0: 0}
    for members in range(1, 1 << n):
        size = bin(_cut_mask(edges, members)).count("1")
        width[members] = max(size, min(width[members ^ (1 << v)] for v in range(n) if (members >> v) & 1))
    return width[(1 << n) - 1]


def charge_depth(n: int, edges: Sequence[tuple[int, int]], group_order: int, characteristic: int) -> int:
    """The least refuting level of an impossible Z_p charge network over a field (characteristic 0 for Q)."""
    if characteristic == group_order:
        return max(sum(1 for edge in edges if v in edge) for v in range(n))
    return toggle_width(n, edges)


def scope_hole_rank(relation: Relation) -> int:
    """Rank over Q of H~_1 of the complex of partial assignments allowed by a three-variable Boolean relation.

    Only the full three-variable relation constrains, so every pair is free;
    the rank is |excluded| - 1 when something is excluded, and 0 otherwise.
    """
    if len(relation.variables) != 3:
        raise ValueError("a scope of three variables")
    pairs = [((i, a), (j, b)) for i, j in ((0, 1), (0, 2), (1, 2)) for a in (False, True) for b in (False, True)]
    index = {pair: k for k, pair in enumerate(pairs)}
    rows = []
    for t in sorted(relation.rows):
        row = [Fraction(0)] * len(pairs)
        row[index[((1, t[1]), (2, t[2]))]] += 1
        row[index[((0, t[0]), (2, t[2]))]] -= 1
        row[index[((0, t[0]), (1, t[1]))]] += 1
        rows.append(row)
    rank, column = 0, 0
    while rank < len(rows) and column < len(pairs):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            column += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i][column]:
                factor = rows[i][column] / rows[rank][column]
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
        column += 1
    return len(pairs) - 5 - rank


def cubic(name: str) -> tuple[int, list[tuple[int, int]]]:
    """A few small cubic graphs by name: K4, K33, prism, cube, wagner, petersen."""
    if name == "K4":
        return 4, list(combinations(range(4), 2))
    if name == "K33":
        return 6, [(i, j) for i in range(3) for j in range(3, 6)]
    if name == "prism":
        return 6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]
    if name == "cube":
        return 8, [(a, b) for a in range(8) for b in range(a + 1, 8) if bin(a ^ b).count("1") == 1]
    if name == "wagner":
        return 8, [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)]
    if name == "petersen":
        outer = [(i, (i + 1) % 5) for i in range(5)]
        spokes = [(i, i + 5) for i in range(5)]
        inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
        return 10, outer + spokes + inner
    raise ValueError(f"unknown graph {name}")
