"""What networks of permutation contact remember (epic HOLES-COHOMOLOGY-20261019-001).

A network carries a witness at every vertex and, on every edge u -> v, a
permutation p of the witness values: the copy allows (w_u, w_v) exactly when
w_v = p(w_u). Forgetting the witnesses, the permutations are allowed together
exactly when some witness assignment satisfies every copy. That happens exactly
when the holonomy group, the composed permutations around closed walks, has a
common fixed point: the label-extended graph then has a sheet that closes up
(HOLES-COHOMOLOGY-20261019-001B-P001).

- Free contact, where a holonomy that fixes one value fixes all, keeps one
  class per independent loop and never binds two loops.
- With one selector per loop, the shape of the loop constraints is the nerve
  of the holonomies' fixed-point sets; every tie or knot among loops is an
  atom, and every simplicial complex occurs.
- A knot among k loops needs k + 1 witness values; star transpositions reach it.
- The basic two-witness linear relaxation over a ring R misses an impossible
  network exactly when R can write 1 from the holonomy-orbit sizes; pinning one
  witness or holding three at once never misses (HOLES-COHOMOLOGY-20261019-001C-P001).
"""

from __future__ import annotations

import math
from fractions import Fraction
from itertools import combinations, product
from typing import Iterable, Sequence

from .relations import Relation

Perm = tuple[int, ...]


def sheets(vertices: int, edges: Sequence[tuple[int, int]], perms: Sequence[Perm]) -> list[list[tuple[int, int]]]:
    """Components of the label-extended graph, whose nodes are (vertex, witness value)."""
    n = len(perms[0])
    parent = {(v, x): (v, x) for v in range(vertices) for x in range(n)}

    def find(node: tuple[int, int]) -> tuple[int, int]:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for (a, b), p in zip(edges, perms):
        for x in range(n):
            parent[find((a, x))] = find((b, p[x]))
    groups: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for node in parent:
        groups.setdefault(find(node), []).append(node)
    return list(groups.values())


def allowed(vertices: int, edges: Sequence[tuple[int, int]], perms: Sequence[Perm]) -> bool:
    """Whether some witness assignment satisfies every copy: a sheet meets every vertex once."""
    return any(len(sheet) == vertices and len({v for v, _ in sheet}) == vertices
               for sheet in sheets(vertices, edges, perms))


def orbit_sizes(vertices: int, edges: Sequence[tuple[int, int]], perms: Sequence[Perm]) -> list[int]:
    """Sizes of the holonomy group's orbits on the witness values at vertex 0."""
    sizes = [sum(1 for v, _ in sheet if v == 0) for sheet in sheets(vertices, edges, perms)]
    return sorted(size for size in sizes if size)


def fixed_points(p: Perm) -> frozenset[int]:
    return frozenset(x for x in range(len(p)) if p[x] == x)


def selector_relation(holonomies: Sequence[Perm]) -> Relation:
    """The relation on loop selectors s0..s(k-1) of a bouquet of triangles, witnesses forgotten.

    Loop i passes the witness through the identity when s_i is false and
    through holonomies[i] when s_i is true.
    """
    k, n = len(holonomies), len(holonomies[0])
    identity = tuple(range(n))
    edges = [edge for i in range(k) for edge in ((0, 1 + 2 * i), (1 + 2 * i, 2 + 2 * i), (2 + 2 * i, 0))]
    rows = set()
    for s in product((False, True), repeat=k):
        perms = [p for i in range(k) for p in (identity, identity, holonomies[i] if s[i] else identity)]
        if allowed(2 * k + 1, edges, perms):
            rows.add(s)
    return Relation(tuple(f"s{i}" for i in range(k)), frozenset(rows))


def nerve(holonomies: Sequence[Perm]) -> set[frozenset[str]]:
    """Sets of selectors whose holonomies share a fixed point, named like selector_relation's variables."""
    k, n = len(holonomies), len(holonomies[0])
    fixes = [fixed_points(h) for h in holonomies]
    return {frozenset(f"s{i}" for i in chosen) for size in range(k + 1) for chosen in combinations(range(k), size)
            if frozenset(range(n)).intersection(*[fixes[i] for i in chosen])}


def star(k: int) -> list[Perm]:
    """The transpositions (j k), j < k, on k + 1 values: a knot among k loops on the fewest values."""
    out = []
    for j in range(k):
        p = list(range(k + 1))
        p[j], p[k] = k, j
        out.append(tuple(p))
    return out


def knot_among_loops(holonomies: Sequence[Perm]) -> bool:
    """Every k - 1 of the holonomies share a fixed point and all k do not (a tie when k = 2)."""
    k, n = len(holonomies), len(holonomies[0])
    fixes = [fixed_points(h) for h in holonomies]
    every = frozenset(range(n))
    return (not every.intersection(*fixes)
            and all(every.intersection(*[fixes[i] for i in range(k) if i != j]) for j in range(k)))


def basic_relaxation_accepts(sizes: Iterable[int], ring: str) -> bool:
    """Whether the two-witness affine relaxation over ring Q, Z or Fp accepts, given the orbit sizes."""
    sizes = list(sizes)
    if ring == "Q":
        return True
    if ring == "Z":
        return math.gcd(*sizes) == 1
    if ring.startswith("F"):
        return any(size % int(ring[1:]) for size in sizes)
    raise ValueError("ring must be Q, Z or Fp")


def allowed_fraction(group: Sequence[Perm], loops: int) -> Fraction:
    """Share of patterns allowed with every edge uniform on a permutation group, for b1 = loops."""
    n = len(group[0])
    total = Fraction(0)
    for size in range(1, n + 1):
        for points in combinations(range(n), size):
            fixers = sum(1 for g in group if all(g[x] == x for x in points))
            total += (-1) ** (size + 1) * Fraction(fixers, len(group)) ** loops
    return total
