"""Counting on plain Pfaffian braces is #P-hard (PLAIN-BRACE-20261031-001B).

Weaving: a plain cubic source G is drawn with straight edges, its vertices at points of distinct faces of a planar frame F (a prism or
another cyclically 4-edge-connected planar cubic bipartite graph, drawn by Tutte's barycentric method so that its faces are convex). Every
crossing (G with F, or G with G) becomes a ladder site of plain cube junctions (brace_lib.site). Along every edge, oriented from its point
end to its line end, the sites are chained by direct edges: P-side ports are lines, L-side ports are points."""
import itertools
import random
import numpy as np
import networkx as nx
import cross_lib as X
import brace_lib as BL


def tutte(g, outer):
    """barycentric embedding with the outer face on a regular polygon (convex faces for 3-connected planar g)"""
    pos, n = {}, len(outer)
    for i, v in enumerate(outer):
        pos[v] = np.array([np.cos(2 * np.pi * i / n), np.sin(2 * np.pi * i / n)])
    inner = [v for v in g if v not in pos]
    idx = {v: i for i, v in enumerate(inner)}
    A = np.zeros((len(inner), len(inner)))
    b = np.zeros((len(inner), 2))
    for v in inner:
        A[idx[v], idx[v]] = g.degree(v)
        for w in g[v]:
            if w in idx:
                A[idx[v], idx[w]] -= 1
            else:
                b[idx[v]] += pos[w]
    xs = np.linalg.solve(A, b)
    for v in inner:
        pos[v] = xs[idx[v]]
    return pos


def named(g, tag):
    col = nx.bipartite.color(g)
    return nx.relabel_nodes(g, {v: (('pt' if col[v] == 0 else 'ln'), tag, v) for v in g})


def prism(n):
    """the prism C_2n x K2 as a frame (points and lines named)"""
    return named(nx.circular_ladder_graph(2 * n), 'F')


def cross(p1, p2, q1, q2):
    d, e, w = p2 - p1, q2 - q1, q1 - p1
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-12:
        return None
    t = (w[0] * e[1] - w[1] * e[0]) / den
    s = (w[0] * d[1] - w[1] * d[0]) / den
    return (t, s) if 1e-9 < t < 1 - 1e-9 and 1e-9 < s < 1 - 1e-9 else None


def drawing(F, G, seed, faces_only=None):
    """positions: F by Tutte (outer face the largest), G's vertices at centroids of distinct inner faces (perturbed)"""
    rng = random.Random(seed)
    fs = BL.faces(F)
    outer = max(fs, key=len)
    pos = tutte(F, outer)
    inner = [f for f in fs if f is not outer and (faces_only is None or len(f) == faces_only)]
    assert len(inner) >= G.number_of_nodes()
    for v, f in zip(sorted(G, key=str), rng.sample(inner, G.number_of_nodes())):
        pos[v] = np.array([pos[u] for u in f]).mean(axis=0) + np.array([rng.uniform(-1e-3, 1e-3), rng.uniform(-1e-3, 1e-3)])
    return pos


def build(F, G, pos, k=1, kmap=None, restored=()):
    """the woven instance: every crossing a site with k junctions (kmap: crossing -> k overrides), except the crossings in `restored`,
    where the two edges simply pass (no site). Returns (builder, crossings as (edge i, edge j))."""
    edges = [tuple(sorted(e, key=lambda v: 0 if X.is_point(v) else 1)) for e in list(F.edges()) + list(G.edges())]
    cr = []
    for i, j in itertools.combinations(range(len(edges)), 2):
        if set(edges[i]) & set(edges[j]):
            continue
        r = cross(pos[edges[i][0]], pos[edges[i][1]], pos[edges[j][0]], pos[edges[j][1]])
        if r:
            cr.append((i, j, r[0], r[1]))
    along = {i: [] for i in range(len(edges))}
    for c, (i, j, t, s) in enumerate(cr):
        if c in restored:
            continue
        along[i].append((t, c, 'A'))
        along[j].append((s, c, 'B'))
    B = X.Builder()
    ports = {}
    for c in range(len(cr)):
        if c in restored:
            continue
        kc = (kmap or {}).get(c, k)
        pr = BL.site(B, c, kc)
        ports[(c, 'A')], ports[(c, 'B')] = pr['A'], pr['B']
    for i, (p, l) in enumerate(edges):
        seq = [p] + [x for t, c, role in sorted(along[i]) for x in ports[(c, role)]] + [l]
        for a, b in zip(seq[0::2], seq[1::2]):
            B.edge(a, b)
    return B, [(i, j) for i, j, t, s in cr]


def two_halves():
    """a plain cubic source with a 2-edge cut: two copies of K3,3 minus an edge, joined crosswise"""
    G = nx.Graph()
    for cp in (0, 1):
        for i, j in itertools.product(range(3), repeat=2):
            if (i, j) != (0, 0):
                G.add_edge(('pt', 'g', cp, i), ('ln', 'g', cp, j))
    G.add_edge(('pt', 'g', 0, 0), ('ln', 'g', 1, 0))
    G.add_edge(('pt', 'g', 1, 0), ('ln', 'g', 0, 0))
    return G
