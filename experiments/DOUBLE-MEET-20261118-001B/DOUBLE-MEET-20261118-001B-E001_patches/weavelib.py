"""Patches of the weave (DOUBLE-MEET-20261118-001B).

The six-regular weave: distinctions (i, j), knots of two classes, u(i, j) = {(i, j), (i+1, j), (i, j+1)} and
d(i, j) = {(i+1, j), (i, j+1), (i+1, j+1)}; two knots meeting twice are of different classes. Every knot is not-all-equal. A patch
is a set of knots; it is a disc when it has no hole and no pinch (Euler characteristic 1, and the knots around each distinction
connected through double meetings). A lone distinction lies in one knot of the patch. Two lone distinctions x (in knot K) and z face
each other when z = x + p (u - x) + q (v - x) for the other two distinctions u, v of K and integers p, q >= 1. Bond distance comes from
BOND-METRIC's metriclib, steps apart from NAE-METRIC's naelib, both unchanged.
"""
import itertools
import math
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/NAE-METRIC-20261118-001B/NAE-METRIC-20261118-001B-E001_blocks"))
import naelib as N  # noqa: E402

M = N.M


def verts(t):
    o, i, j = t
    return [(i, j), (i + 1, j), (i, j + 1)] if o == "u" else [(i + 1, j), (i, j + 1), (i + 1, j + 1)]


def nbrs(t):
    o, i, j = t
    return [("d", i, j), ("d", i - 1, j), ("d", i, j - 1)] if o == "u" else [("u", i, j), ("u", i + 1, j), ("u", i, j + 1)]


def is_disc(T):
    V = {v for t in T for v in verts(t)}
    E = {tuple(sorted(e)) for t in T for e in itertools.combinations(verts(t), 2)}
    if len(V) - len(E) + len(T) != 1:
        return False
    for v in V:
        star = [t for t in T if v in verts(t)]
        G = nx.Graph()
        G.add_nodes_from(range(len(star)))
        for a, b in itertools.combinations(range(len(star)), 2):
            if len(set(verts(star[a])) & set(verts(star[b]))) == 2:
                G.add_edge(a, b)
        if not nx.is_connected(G):
            return False
    return True


def normal(T):
    """Translate so the least distinction is (0, 0) (fixed patches, up to translation only)."""
    V = [v for t in T for v in verts(t)]
    mi, mj = min(i for i, _ in V), min(j for _, j in V)
    return frozenset((o, i - mi, j - mj) for o, i, j in T)


def all_discs(kmax):
    """Every connected set of at most kmax knots (connected through double meetings), up to translation, that is a disc."""
    level = {normal({("u", 0, 0)}), normal({("d", 0, 0)})}
    out = [T for T in level]
    for _ in range(kmax - 1):
        nxt = set()
        for T in level:
            for t in T:
                for nb in nbrs(t):
                    if nb not in T:
                        nxt.add(normal(set(T) | {nb}))
        level = nxt
        out += list(level)
    return [T for T in out if is_disc(T)]


def parallelogram(a, b):
    sites = {(i, j) for i in range(a) for j in range(b)}
    return frozenset(t for i in range(a) for j in range(b) for t in (("u", i, j), ("d", i, j)) if all(v in sites for v in verts(t)))


def read(T):
    """Bond distance, steps apart and lone distinctions of a patch."""
    V = sorted({v for t in T for v in verts(t)})
    ix = {v: k for k, v in enumerate(V)}
    ts = [tuple(sorted(ix[v] for v in verts(t))) for t in sorted(T)]
    n = len(V)
    st = M.states(n, [(N.NAE3, t) for t in ts])
    D = M.bond_matrix(n, st)
    S = N.steps(ts, n)
    deg = {v: sum(v in verts(t) for t in T) for v in V}
    lone = {v: next(t for t in T if v in verts(t)) for v in V if deg[v] == 1}
    return V, ix, D, S, lone, len(st)


def facing(x, kx, z):
    """p, q >= 1 with z = x + p (u - x) + q (v - x), u, v the other distinctions of x's knot kx; else None."""
    u, v = [w for w in verts(kx) if w != x]
    d1, d2 = (u[0] - x[0], u[1] - x[1]), (v[0] - x[0], v[1] - x[1])
    det = d1[0] * d2[1] - d1[1] * d2[0]
    dz = (z[0] - x[0], z[1] - x[1])
    P = (dz[0] * d2[1] - dz[1] * d2[0]) / det
    Q = (d1[0] * dz[1] - d1[1] * dz[0]) / det
    if P != int(P) or Q != int(Q) or P < 1 or Q < 1:
        return None
    return int(P), int(Q)


def height_distances(T):
    """D(s, t): least weight of a route inside the patch, a forward step (e1 = (1, 0), e2 = (-1, 1), e3 = (0, -1)) costing 1 and a
    backward step 2 (the advisor's height-function distance)."""
    G = nx.DiGraph()
    E = {tuple(sorted(e)) for t in T for e in itertools.combinations(verts(t), 2)}
    for a, b in E:
        d = (b[0] - a[0], b[1] - a[1])
        f, g = (a, b) if d in ((1, 0), (-1, 1), (0, -1)) else (b, a)
        G.add_edge(f, g, w=1)
        G.add_edge(g, f, w=2)
    return dict(nx.all_pairs_dijkstra_path_length(G, weight="w"))


def tight_sets(V, DD):
    """For every set R of at least three distinctions (bit masks over V's order), whether some cyclic order has
    sum of D <= 3(|R| - 2) (directed tour, Held-Karp from R's least member)."""
    n = len(V)
    W_ = [[DD[V[a]][V[b]] for b in range(n)] for a in range(n)]
    INF = float("inf")
    tight = set()
    for s in range(n):
        # tours starting and ending at s, visiting only members > s
        dp = {(1 << s, s): 0}
        best = {}
        for mask in range(1 << n):
            if not (mask >> s) & 1 or mask & ((1 << s) - 1):
                continue
            for last in range(n):
                c = dp.get((mask, last))
                if c is None:
                    continue
                if bin(mask).count("1") >= 3:
                    tot = c + W_[last][s]
                    if tot < best.get(mask, INF):
                        best[mask] = tot
                for nx_ in range(s + 1, n):
                    if not (mask >> nx_) & 1:
                        key = (mask | (1 << nx_), nx_)
                        v = c + W_[last][nx_]
                        if v < dp.get(key, INF):
                            dp[key] = v
        for mask, tot in best.items():
            if tot <= 3 * (bin(mask).count("1") - 2):
                tight.add(mask)
    return tight
