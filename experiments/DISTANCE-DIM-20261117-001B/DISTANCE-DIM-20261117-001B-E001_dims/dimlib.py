"""Library for DISTANCE-DIM-20261117-001B-E001.

Implication bases: the allowed states are the up-sets of a finite poset (the base of its two-place
implications).  Disagreement counts, strict betweenness, comparability read from pair patterns and from
betweenness, order dimension (the Dushnik-Miller two-test via Golumbic's implication classes), and the
order rebuilt up to reversal.  Not-all-equal chain grids (square grid on a torus, every edge one knot with a
private distinction), by row transfer matrices.  The order-only reading: gap neighbours (strict lune: v is a
gap of o when no w has T(o,w) < T(o,v) and T(w,v) < T(o,v); the literature's relative neighbourhood graph)
and level sizes by breadth-first search."""
import itertools
from collections import deque

import numpy as np


# ---------- implication bases ----------

def grid_poset(*sides):
    """Product of chains: elements are coordinate tuples; u <= v iff every coordinate <=."""
    elems = list(itertools.product(*[range(s) for s in sides]))
    leq = lambda u, v: all(a <= b for a, b in zip(u, v))
    return elems, leq


def crown(k):
    """Standard example S_k: a_i < b_j iff i != j (dimension k)."""
    elems = [("a", i) for i in range(k)] + [("b", i) for i in range(k)]
    def leq(u, v):
        return u == v or (u[0] == "a" and v[0] == "b" and u[1] != v[1])
    return elems, leq


def upsets(elems, leq):
    """All up-sets, as bitmasks over elems, by recursion on a linear extension (largest first)."""
    n = len(elems)
    order = sorted(range(n), key=lambda i: -sum(leq(elems[j], elems[i]) for j in range(n)))  # many below = high
    above = [sum(1 << j for j in range(n) if j != i and leq(elems[i], elems[j])) for i in range(n)]
    out = []
    def rec(k, mask):
        if k == n:
            out.append(mask)
            return
        i = order[k]
        rec(k + 1, mask)                                  # i not in the up-set
        if above[i] & ~mask == 0:                         # everything above i already in
            rec(k + 1, mask | (1 << i))
    # process from the top so "above" elements are decided first
    order.sort(key=lambda i: sum(leq(elems[i], elems[j]) for j in range(n)))
    rec(0, 0)
    return out


def table_from_states(n, states):
    """Disagreement counts d[u][v] for states given as bitmasks over n distinctions."""
    S = np.array([[(s >> i) & 1 for i in range(n)] for s in states], dtype=np.int64)
    ones = S.sum(axis=0)
    both = S.T @ S
    return ones[:, None] + ones[None, :] - 2 * both


def strict_between(D):
    """All (u, w, v), u < v, with w strictly between u and v."""
    n = len(D)
    out = []
    for u in range(n):
        for v in range(u + 1, n):
            for w in range(n):
                if w not in (u, v) and D[u][w] > 0 and D[w][v] > 0 and D[u][v] == D[u][w] + D[w][v]:
                    out.append((u, w, v))
    return out


def comparability_from_between(n, triples):
    comp = set()
    for u, w, v in triples:
        comp |= {frozenset((u, w)), frozenset((w, v)), frozenset((u, v))}
    return comp


def is_comparability_graph(n, edges):
    """Golumbic: transitively orientable iff no implication class contains an arc and its reverse."""
    E = {frozenset(e) for e in edges}
    adj = [set() for _ in range(n)]
    for e in E:
        a, b = tuple(e)
        adj[a].add(b)
        adj[b].add(a)
    arcs = [(a, b) for a in range(n) for b in adj[a]]
    idx = {a: k for k, a in enumerate(arcs)}
    parent = list(range(len(arcs)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        parent[find(x)] = find(y)
    for a in range(n):
        for b in adj[a]:
            for c in adj[a]:          # (a,b) Gamma (a,c) when b, c not adjacent
                if c != b and c not in adj[b]:
                    union(idx[(a, b)], idx[(a, c)])
            for c in adj[b]:          # (a,b) Gamma (c,b) when a, c not adjacent
                if c != a and c not in adj[a]:
                    union(idx[(a, b)], idx[(c, b)])
    return all(find(idx[(a, b)]) != find(idx[(b, a)]) for (a, b) in arcs)


def dimension_at_most_two(n, comp):
    """A poset has dimension <= 2 iff its incomparability graph is a comparability graph (Dushnik-Miller)."""
    incomp = [(u, v) for u in range(n) for v in range(u + 1, n) if frozenset((u, v)) not in comp]
    return is_comparability_graph(n, incomp)


# ---------- order-only levels ----------

def rng_gaps(T, nodes, start):
    """Gap neighbours of start under the order-only reading: v with no w nearer to each (T(start,w) < T(start,v)
    and T(w,v) < T(start,v))."""
    out = []
    for v in nodes:
        if v == start:
            continue
        t = T[start][v]
        if not any(w not in (start, v) and T[start][w] < t and T[w][v] < t for w in nodes):
            out.append(v)
    return out


def bfs_levels(n, nbrs, start):
    dist = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for w in nbrs(u):
            if w not in dist:
                dist[w] = dist[u] + 1
                q.append(w)
    sizes = {}
    for v, k in dist.items():
        sizes[k] = sizes.get(k, 0) + 1
    return [sizes[k] for k in sorted(sizes)]


# ---------- not-all-equal chain grid ----------

def chain_grid_rates(L, exact=False):
    """Square grid on an L x L torus, every edge one NAE knot (u, p, v) with a private p.  Summing out p
    gives weight 1 when u = v and 2 when u != v.  Returns N (states of the whole base) and the disagreement
    rate from grid distinction (0, 0) to grid distinction (c, r), by row transfer matrices."""
    R = 1 << L
    bits = (np.arange(R)[:, None] >> np.arange(L)[None, :]) & 1
    horiz = np.prod(np.where(bits != np.roll(bits, -1, axis=1), 2, 1), axis=1)       # within a row
    vert = np.prod(np.where(bits[:, None, :] != bits[None, :, :], 2, 1), axis=2)      # row to row
    dt = object if exact else np.float64
    T = (horiz[:, None] * vert).astype(dt)
    if not exact:
        T = T / T.sum(axis=1).max()
    P = [np.eye(R, dtype=np.int64).astype(dt)]
    for _ in range(L):
        P.append(P[-1].dot(T))
    N = np.trace(P[L])
    one = bits.astype(dt)
    rates = {}
    for r in range(L):
        left1 = one[:, 0][:, None] * P[r]
        left0 = (1 - one[:, 0])[:, None] * P[r]
        col1 = (left1 * P[L - r].T).sum(axis=0)
        col0 = (left0 * P[L - r].T).sum(axis=0)
        for c in range(L):
            rates[(c, r)] = ((col1 * (1 - one[:, c])).sum() + (col0 * one[:, c]).sum()) / N
    return N, rates


def with_bottom_top(elems, leq):
    """Add a least and a greatest element."""
    bot, top = ("bot",), ("top",)
    def leq2(u, v):
        if u == bot or v == top:
            return True
        if u == top or v == bot:
            return u == v
        return leq(u, v)
    return [bot] + list(elems) + [top], leq2


def young(a, b, ca, cb):
    """The a x b grid with the ca x cb corner at the top removed."""
    elems = [(i, j) for i in range(a) for j in range(b) if not (i >= a - ca and j >= b - cb)]
    return elems, lambda u, v: u[0] <= v[0] and u[1] <= v[1]


def comparable_from_patterns(n, states):
    """Pairs for which some joint pattern of values never occurs."""
    seen = {}
    for s in states:
        for u in range(n):
            for v in range(u + 1, n):
                seen.setdefault((u, v), set()).add(((s >> u) & 1, (s >> v) & 1))
    return {frozenset(p) for p, pats in seen.items() if len(pats) < 4}


def orient_from_between(n, comp, triples):
    """Rebuild a transitive orientation from betweenness: two comparable pairs sharing w are oriented
    alike (a chain, w in the middle) or both toward w (u, v incomparable).  Returns the set of arcs (u, v)
    meaning u < v, or None if propagation meets a contradiction."""
    between = {(u, w, v) for u, w, v in triples} | {(v, w, u) for u, w, v in triples}
    nbr = {}
    for e in comp:
        a, b = tuple(e)
        nbr.setdefault(a, set()).add(b)
        nbr.setdefault(b, set()).add(a)
    arcs = {}
    for e in comp:
        if e in arcs:
            continue
        a, b = sorted(e)
        arcs[e] = (a, b)
        stack = [e]
        while stack:
            f = stack.pop()
            lo, hi = arcs[f]
            for w in (lo, hi):
                x = hi if w == lo else lo           # f = {x, w}
                for y in nbr[w]:
                    if y == x:
                        continue
                    g = frozenset((w, y))
                    if (x, w, y) in between:          # chain x - w - y: same direction through w
                        want = (w, y) if (x, w) == (lo, hi) else (y, w)
                    elif frozenset((x, y)) not in comp:  # incomparable: both toward w, or both away
                        want = (y, w) if hi == w else (w, y)
                    else:
                        continue                      # x, y comparable but w not between: decided elsewhere
                    if g in arcs:
                        if arcs[g] != want:
                            return None
                    else:
                        arcs[g] = want
                        stack.append(g)
    return set(arcs.values())


def realizer_ok(n, leq_idx, exts):
    """Do the linear extensions intersect to the order exactly?"""
    pos = [{x: k for k, x in enumerate(L)} for L in exts]
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            all_before = all(p[u] < p[v] for p in pos)
            if all_before != leq_idx(u, v):
                return False
    return True


def linear_extensions(n, less):
    """All linear extensions (small posets only)."""
    out = []
    def rec(seq, left):
        if not left:
            out.append(list(seq))
            return
        for x in sorted(left):
            if not any(less(y, x) for y in left if y != x):
                seq.append(x)
                rec(seq, left - {x})
                seq.pop()
    rec([], set(range(n)))
    return out
