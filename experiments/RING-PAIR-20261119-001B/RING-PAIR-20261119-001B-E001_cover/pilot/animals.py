"""Hypothesis H: junctions of round t of a bare start = deck orbits of connected vertex sets of size t + 1 in the universal cover of
its candidate complex (Gamma edges = round-1 groups; filled triangles = sunflower triples)."""
import sys
from collections import defaultdict
from fractions import Fraction
from gamma import complex_of
import joinlib_path  # noqa
def make(n, E, tri):
    adj = defaultdict(set)
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    T = set()
    for (a, b, c), _ in tri:
        for p in [(a, b, c), (a, c, b), (b, a, c), (b, c, a), (c, a, b), (c, b, a)]:
            T.add(p)
    def push(w, u):
        if len(w) >= 2 and w[-2] == u:
            return w[:-1]
        if len(w) >= 2 and (w[-2], w[-1], u) in T:
            return push(w[:-1], u)
        return w + (u,)
    def nbrs(w):
        return [push(w, u) for u in adj[w[-1]]]
    return nbrs
def rooted_counts(nbrs, root, N):
    cnt = [0] * (N + 1)
    def rec(cur, untried, seen, size):
        cnt[size] += 1
        if size == N: return
        untried = list(untried)
        while untried:
            v = untried.pop()
            new = [u for u in nbrs(v) if u not in seen]
            seen2 = seen | set(new)
            rec(cur | {v}, untried + new, seen2, size + 1)
    rec(frozenset([root]), [u for u in nbrs(root)], {root} | set(nbrs(root)), 1)
    return cnt
def orbit_counts(n, E, tri, N):
    nbrs = make(n, E, tri)
    tot = [Fraction(0)] * (N + 1)
    for x in range(n):
        c = rooted_counts(nbrs, (x,), N)
        for k in range(1, N + 1): tot[k] += Fraction(c[k], k)
    return [tot[k] for k in range(1, N + 1)]   # index t = size - 1
