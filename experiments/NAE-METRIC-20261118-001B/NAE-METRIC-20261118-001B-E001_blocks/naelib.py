"""Blocks, cuts and bond distance on complement-closed bases (NAE-METRIC-20261118-001B).

Bond distance b(x, y): the size of the least bond holding x and y, minus one, infinite when none (BOND-METRIC's metriclib, reused
unchanged). The incidence graph of a base has its distinctions and knots as vertices, each knot joined to its distinctions; its
blocks (biconnected components) group the knots, a knot on no cycle being a block alone, and its cut distinctions separate them.
"""
import itertools
import math
import sys
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/BOND-METRIC-20261118-001B/BOND-METRIC-20261118-001B-E001_triangles"))
import metriclib as M  # noqa: E402

NAE3 = M.NAE
NAE_CLASS = [M.NAE] + [M.switch(M.NAE, 1 << i) for i in range(3)]   # not-all-equal and its three betweenness forms


def incidence(knots):
    G = nx.Graph()
    for i, t in enumerate(knots):
        for v in t:
            G.add_edge(("k", i), ("v", v))
    return G


def blocks(knots):
    """Lists of knot indices, one per block."""
    G = incidence(knots)
    out = [sorted(i for kind, i in comp if kind == "k") for comp in nx.biconnected_components(G) if len(comp) > 2]
    seen = {i for b in out for i in b}
    return out + [[i] for i in range(len(knots)) if i not in seen]


def separates(G, y, x, z):
    H = G.copy()
    H.remove_node(("v", y))
    return not nx.has_path(H, ("v", x), ("v", z))


def steps(knots, n):
    """Steps apart: knots on a least chain from x to y (incidence distance / 2); inf when unjoined."""
    G = incidence(knots)
    S = [[math.inf] * n for _ in range(n)]
    for x in range(n):
        if ("v", x) not in G:
            continue
        for node, d in nx.single_source_shortest_path_length(G, ("v", x)).items():
            if node[0] == "v" and node[1] != x:
                S[x][node[1]] = d // 2
    return S


def sub_base(laws, knots, idx):
    """The base of the knots in idx alone, renumbered: (n, knots, map from old distinction to new)."""
    vs = sorted({v for i in idx for v in knots[i]})
    m = {v: j for j, v in enumerate(vs)}
    return len(vs), [(laws[i], tuple(m[v] for v in knots[i])) for i in idx], m


def block_formula(laws, knots, n):
    """b from the blocks alone: within a block its own bond distance; across blocks, b - 1 summed over the blocks met along the
    block-cut tree (the distinctions where the route enters and leaves each block). None when some block allows no state."""
    bl = blocks(knots)
    T = nx.Graph()
    vals = []
    for bi, idx in enumerate(bl):
        k, kn, m = sub_base(laws, knots, idx)
        st = M.states(k, kn)
        if len(st) == 0:
            return None
        vals.append((m, M.bond_matrix(k, st)))
        for v in m:
            T.add_edge(("b", bi), ("v", v))
    out = [[math.inf] * n for _ in range(n)]
    for x, z in itertools.combinations(range(n), 2):
        if ("v", x) not in T or ("v", z) not in T or not nx.has_path(T, ("v", x), ("v", z)):
            continue
        path = nx.shortest_path(T, ("v", x), ("v", z))  # v, b, v, b, ..., v  (the block-cut tree is a tree)
        tot = 0
        for a in range(0, len(path) - 2, 2):
            u, blk, w = path[a][1], path[a + 1][1], path[a + 2][1]
            m, Db = vals[blk]
            tot += Db[m[u]][m[w]] - 1
        out[x][z] = out[z][x] = tot + 1
    return out


def is_block(knots):
    """All knots in one block: the primal graph (distinctions adjacent when they share a knot) is biconnected; a distinction in
    one knot only is allowed."""
    G = nx.Graph()
    for t in knots:
        G.add_edges_from(itertools.combinations(t, 2))
    return nx.is_biconnected(G)


def double_meetings(knots):
    return sum(len(set(a) & set(b)) == 2 for a, b in itertools.combinations(knots, 2))


def split_b(S, n):
    """Bond distance on a complement-closed state set holding both constant states, from triples alone, capped at 3:
    1 when no state separates x and y (equal columns), 2 when some z separated from both has one of the three never alone
    against the other two, else 3 (meaning at least 3)."""
    full = (1 << n) - 1
    st = [s for s in S if s not in (0, full)]
    col = [tuple((s >> v) & 1 for s in st) for v in range(n)]

    def alone(a, b, c):
        return any(((s >> a) & 1) != ((s >> b) & 1) and ((s >> b) & 1) == ((s >> c) & 1) for s in st)
    out = {}
    for x, y in itertools.combinations(range(n), 2):
        if col[x] == col[y]:
            out[(x, y)] = 1
            continue
        ok = any(col[z] != col[x] and col[z] != col[y] and not (alone(x, y, z) and alone(y, x, z) and alone(z, x, y))
                 for z in range(n) if z not in (x, y))
        out[(x, y)] = 2 if ok else 3
    return out


NAE4 = frozenset(p for p in range(16) if p not in (0, 15))   # four-place not-all-equal


def states_any(n, knots):
    """Allowed states of knots [(law, places)] of any arity (law: allowed patterns, bit i = place i)."""
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for R, t in knots:
        pat = np.zeros(len(s), dtype=np.int64)
        for i, v in enumerate(t):
            pat |= ((s >> v) & 1) << i
        allowed = np.zeros(1 << len(t), dtype=bool)
        allowed[list(R)] = True
        ok &= allowed[pat]
    return s[ok]


def primal_blocks(knots):
    """Blocks as sets of distinctions: biconnected components of the primal graph (two distinctions adjacent when they share a
    knot), with each knot assigned to the block holding all its distinctions (the advisor's definition; equal to the incidence
    blocks for three-place knots)."""
    G = nx.Graph()
    for t in knots:
        G.add_nodes_from(t)
        G.add_edges_from(itertools.combinations(t, 2))
    comps = [set(c) for c in nx.biconnected_components(G)]
    out = []
    for c in comps:
        idx = [i for i, t in enumerate(knots) if set(t) <= c]
        out.append((sorted(c), idx))
    return out


def bonds_list(n, st):
    return M.bonds(n, M.free_table(n, st))


def knot_graph(knots):
    """For a graph-like base (each distinction in at most two knots): knots as vertices, shared distinctions as edges."""
    G = nx.MultiGraph()
    G.add_nodes_from(range(len(knots)))
    where = {}
    for i, t in enumerate(knots):
        for v in t:
            where.setdefault(v, []).append(i)
    for v, ks in where.items():
        if len(ks) == 2:
            G.add_edge(ks[0], ks[1], v=v)
    return G, where


def series_parallel(G):
    """No K4 minor (treewidth at most 2), by deleting vertices of degree at most 1 and suppressing vertices of degree 2,
    merging parallel edges and dropping loops."""
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from((u, v) for u, v in G.edges() if u != v)
    changed = True
    while changed and H.number_of_nodes() > 0:
        changed = False
        for v in list(H.nodes()):
            d = H.degree(v)
            if d <= 1:
                H.remove_node(v)
                changed = True
            elif d == 2:
                a, b = list(H.neighbors(v))
                H.remove_node(v)
                H.add_edge(a, b)
                changed = True
    return H.number_of_nodes() == 0


def ring(m, twisted):
    """Ring of m knots, knot i = (2i, 2i + 1, 2i + 2 mod 2m): ring distinctions even, private thirds odd; twisted switches knot 0
    at its first ring place."""
    n = 2 * m
    ts = [((2 * i) % n, 2 * i + 1, (2 * i + 2) % n) for i in range(m)]
    laws = [NAE3] * m
    if twisted:
        laws[0] = M.switch(NAE3, 1)
    return n, list(zip(laws, ts))
