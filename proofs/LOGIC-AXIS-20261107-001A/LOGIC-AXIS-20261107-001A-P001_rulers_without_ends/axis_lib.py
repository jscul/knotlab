"""Parity laws on finite sets of distinctions: allowed states, knots and bond distance.

A parity law is a list of parity checks (sets of variables whose sum must be 0 over F2). Its allowed
states form a subspace. Each variable gets a column: its values in a basis of the allowed states.
A finite set S is constrained as a whole exactly when its columns sum to zero after removing a
dependent part, and the K1-K3 test reads:

- S is a knot  <=>  |S| >= 3, the columns of S sum to 0, and rank(S) = |S| - 1
  (the only parity check supported in S is the full one, so every proper part is free).

Bond distance (NATIVE-NETWORK-20261021-001): the least size of a knot through u and v, minus one.
"""

from __future__ import annotations

from itertools import combinations
from typing import Hashable, Iterable, Sequence


def bits(mask: int) -> Iterable[int]:
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def reduce_rows(rows: Iterable[int]) -> list[tuple[int, int]]:
    """Fully reduced echelon basis: (pivot, row) pairs, each row holding exactly one pivot bit."""
    basis: list[tuple[int, int]] = []
    for row in rows:
        for pivot, b in basis:
            if row >> pivot & 1:
                row ^= b
        if row:
            pivot = row.bit_length() - 1
            basis = [(q, b ^ row if b >> pivot & 1 else b) for q, b in basis]
            basis.append((pivot, row))
    return basis


def rank(vectors: Iterable[int]) -> int:
    return len(reduce_rows(vectors))


def nullspace(rows: Sequence[int], n: int) -> list[int]:
    basis = reduce_rows(rows)
    pivots = {p for p, _ in basis}
    solutions = []
    for free in range(n):
        if free in pivots:
            continue
        s = 1 << free
        for p, b in basis:
            if b >> free & 1:
                s |= 1 << p
        solutions.append(s)
    return solutions


class ParityLaw:
    def __init__(self, variables: Sequence[Hashable], checks: Iterable[Iterable[Hashable]]):
        self.vars = list(variables)
        self.index = {v: i for i, v in enumerate(self.vars)}
        if len(self.index) != len(self.vars):
            raise ValueError("variables must be distinct")
        self.checks = []
        for check in checks:
            m = 0
            for v in check:
                m ^= 1 << self.index[v]
            self.checks.append(m)
        self.solutions = nullspace(self.checks, len(self.vars))
        cols = [0] * len(self.vars)
        for j, s in enumerate(self.solutions):
            for i in bits(s):
                cols[i] |= 1 << j
        self.col = {v: cols[self.index[v]] for v in self.vars}

    # --- allowed states -------------------------------------------------------------------------
    def allows(self, assignment: dict) -> bool:
        """Is the 0/1 assignment (missing variables = 0) an allowed state?"""
        m = 0
        for v, value in assignment.items():
            if value:
                m |= 1 << self.index[v]
        return all(bin(m & c).count("1") % 2 == 0 for c in self.checks)

    def rank_of(self, variables: Iterable[Hashable]) -> int:
        return rank(self.col[v] for v in variables)

    def projection_is_product(self, a: Sequence[Hashable], b: Sequence[Hashable]) -> bool:
        """X_{A u B} = X_A x X_B  <=>  dim X_{AuB} = dim X_A + dim X_B (dim X_S = rank of S's columns)."""
        return self.rank_of(list(a) + list(b)) == self.rank_of(a) + self.rank_of(b)

    def is_knot(self, s: Sequence[Hashable]) -> bool:
        s = list(s)
        if len(s) < 3 or len(set(s)) != len(s):
            return False
        total = 0
        for v in s:
            total ^= self.col[v]
        return total == 0 and self.rank_of(s) == len(s) - 1

    # --- bond distance --------------------------------------------------------------------------
    def smallest_knot(self, u, v, max_size: int, candidates: Sequence[Hashable] | None = None):
        """Smallest knot containing u and v with at most max_size variables, or None.

        Exhaustive over the candidate variables (default: all), by increasing size, meeting in the
        middle on subset sums of the columns."""
        if candidates is None:
            candidates = self.vars
        others = [w for w in candidates if w != u and w != v]
        target = self.col[u] ^ self.col[v]
        for extra in range(1, max_size - 1):
            found = self._knots_with_extra(u, v, others, target, extra, first_only=True)
            if found:
                return found[0]
        return None

    def knots_with_extra(self, u, v, extra: int, candidates: Sequence[Hashable] | None = None):
        if candidates is None:
            candidates = self.vars
        others = [w for w in candidates if w != u and w != v]
        return self._knots_with_extra(u, v, others, self.col[u] ^ self.col[v], extra, first_only=False)

    def _knots_with_extra(self, u, v, others, target, extra, first_only):
        out = []
        if extra == 1:
            for w in others:
                if self.col[w] == target and self.is_knot([u, v, w]):
                    out.append((u, v, w))
                    if first_only:
                        return out
            return out
        half = extra // 2
        table: dict[int, list[tuple]] = {}
        for combo in combinations(others, half):
            x = 0
            for w in combo:
                x ^= self.col[w]
            table.setdefault(x, []).append(combo)
        seen = set()
        for combo in combinations(others, extra - half):
            x = target
            for w in combo:
                x ^= self.col[w]
            for partner in table.get(x, ()):
                if set(partner) & set(combo):
                    continue
                members = tuple(sorted(set(partner) | set(combo), key=repr))
                if members in seen:
                    continue
                seen.add(members)
                s = (u, v) + members
                if self.is_knot(s):
                    out.append(s)
                    if first_only:
                        return out
        return out

    def knots_through(self, u, max_size: int, candidates: Sequence[Hashable] | None = None):
        """All knots containing u with at most max_size variables (exhaustive over candidates)."""
        if candidates is None:
            candidates = self.vars
        others = [w for w in candidates if w != u]
        found = set()
        for size in range(3, max_size + 1):
            for combo in combinations(others, size - 1):
                x = self.col[u]
                for w in combo:
                    x ^= self.col[w]
                if x == 0 and self.is_knot((u,) + combo):
                    found.add(frozenset((u,) + combo))
        return found


def chained(sites: Sequence[tuple[int, ...]], reach: int) -> bool:
    """Is the set of sites connected when sites at sup-norm distance <= reach are joined?"""
    sites = list(sites)
    if not sites:
        return True
    seen = {0}
    stack = [0]
    while stack:
        i = stack.pop()
        for j in range(len(sites)):
            if j not in seen and max(abs(a - b) for a, b in zip(sites[i], sites[j])) <= reach:
                seen.add(j)
                stack.append(j)
    return len(seen) == len(sites)


# --- concrete laws ----------------------------------------------------------------------------------

def grid_edges(shape: Sequence[int]):
    """Edges of the box grid {0..L_i-1}^d as variables (direction, site); site = lower endpoint."""
    d = len(shape)
    edges = []
    for site in _points(shape):
        for k in range(d):
            if site[k] + 1 < shape[k]:
                edges.append((k, site))
    return edges


def _points(shape):
    if not shape:
        yield ()
        return
    for rest in _points(shape[1:]):
        for i in range(shape[0]):
            yield (i,) + rest


def _step(site, k, delta=1):
    s = list(site)
    s[k] += delta
    return tuple(s)


def gauge_law(shape: Sequence[int]) -> ParityLaw:
    """Flat Z2 connections on a box: every plaquette's four edges sum to 0."""
    edges = set(grid_edges(shape))
    d = len(shape)
    checks = []
    for site in _points(shape):
        for i in range(d):
            for j in range(i + 1, d):
                plaquette = [(i, site), (j, site), (i, _step(site, j)), (j, _step(site, i))]
                if all(e in edges for e in plaquette):
                    checks.append(plaquette)
    return ParityLaw(sorted(edges), checks)


def tseitin_law(shape: Sequence[int]) -> ParityLaw:
    """Even subgraphs of a box grid: the edges at every vertex sum to 0."""
    edges = set(grid_edges(shape))
    d = len(shape)
    checks = []
    for site in _points(shape):
        star = [(k, site) for k in range(d) if (k, site) in edges]
        star += [(k, _step(site, k, -1)) for k in range(d) if (k, _step(site, k, -1)) in edges]
        checks.append(star)
    return ParityLaw(sorted(edges), checks)


def ledrappier_triangle(n: int) -> ParityLaw:
    """Ledrappier's law x(i,j)+x(i+1,j)+x(i,j+1)=0 on the patch i,j>=0, i+j<=n."""
    points = [(i, j) for i in range(n + 1) for j in range(n + 1 - i)]
    pts = set(points)
    checks = [[(i, j), (i + 1, j), (i, j + 1)] for (i, j) in points if (i + 1, j) in pts and (i, j + 1) in pts]
    return ParityLaw(points, checks)


# --- shortest cycle through two edges (an independent method for the gauge law) ----------------------

def shortest_cycle_through(shape: Sequence[int], e, f) -> int | None:
    """Length of the shortest cycle of the box grid containing edges e and f.

    Two vertex-disjoint paths join the endpoints of e to those of f (either pairing), avoiding e and f;
    computed as a two-unit min-cost flow with unit vertex capacities (successive shortest paths)."""
    def ends(edge):
        k, s = edge
        return s, _step(s, k)
    ea, eb = ends(e)
    fa, fb = ends(f)
    vertices = list(_points(shape))
    idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    # node split: in = 2i, out = 2i+1; source = 2n, sink = 2n+1
    graph: list[list[list[int]]] = [[] for _ in range(2 * n + 2)]

    def add(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    banned = {frozenset((ea, eb)), frozenset((fa, fb))}
    for v in vertices:
        add(2 * idx[v], 2 * idx[v] + 1, 1, 0)
    for edge in grid_edges(shape):
        a, b = ends(edge)
        if frozenset((a, b)) in banned:
            continue
        add(2 * idx[a] + 1, 2 * idx[b], 1, 1)
        add(2 * idx[b] + 1, 2 * idx[a], 1, 1)
    source, sink = 2 * n, 2 * n + 1
    for v in {ea, eb}:
        add(source, 2 * idx[v], 1, 0)
    for v in {fa, fb}:
        add(2 * idx[v] + 1, sink, 1, 0)
    flow = cost = 0
    while flow < 2:
        dist = [None] * len(graph)
        prev = [None] * len(graph)
        dist[source] = 0
        queue = [source]
        in_queue = [False] * len(graph)
        in_queue[source] = True
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False
            for i, (v, cap, c, _) in enumerate(graph[u]):
                if cap > 0 and (dist[v] is None or dist[u] + c < dist[v]):
                    dist[v] = dist[u] + c
                    prev[v] = (u, i)
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)
        if dist[sink] is None:
            return None
        v = sink
        while v != source:
            u, i = prev[v]
            graph[u][i][1] -= 1
            back = graph[u][i][3]
            graph[v][back][1] += 1
            v = u
        flow += 1
        cost += dist[sink]
    return cost + 2


def all_knots_through(law: ParityLaw, u, max_size: int, candidates: Sequence[Hashable] | None = None):
    """Every knot containing u with at most max_size variables (meet in the middle over column sums)."""
    if candidates is None:
        candidates = law.vars
    others = [w for w in candidates if w != u]
    found = set()
    for extra in range(2, max_size):
        half = extra // 2
        table: dict[int, list[tuple]] = {}
        for combo in combinations(others, half):
            x = 0
            for w in combo:
                x ^= law.col[w]
            table.setdefault(x, []).append(combo)
        for combo in combinations(others, extra - half):
            x = law.col[u]
            for w in combo:
                x ^= law.col[w]
            for partner in table.get(x, ()):
                if set(partner) & set(combo):
                    continue
                members = frozenset((u,) + partner + combo)
                if members not in found and law.is_knot(list(members)):
                    found.add(members)
    return found
