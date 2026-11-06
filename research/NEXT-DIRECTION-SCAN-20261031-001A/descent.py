"""Lane A (NEXT-DIRECTION-SCAN-20261031-001A): does a local law favour the knot's sign class?

For each small cubic bipartite graph, enumerate its sign classes (signings modulo cuts, one per element of the cycle space dual), count
the proper colourings of each (every line sees colour xor sign not all equal), and study descent by single sign flips: a step flips
one incidence and lowers the number of colourings. The knot's class is the class with no colouring (it exists iff the graph is
Pfaffian, and is then unique). A trap is a class with colourings and no neighbour with fewer.

Run: .venv/bin/python -B descent.py [--write]"""
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"))
import computation_lib as CL  # noqa: E402

T0 = time.time()


def trisum(pieces):
    """glue planar braces along a common square face (square edges deleted); pieces: list of (graph, square 4-tuple, c0 a point)"""
    G = nx.Graph()
    for i, (g, S) in enumerate(pieces):
        col = nx.bipartite.color(g)
        assert col[S[0]] == col[S[2]] != col[S[1]] == col[S[3]]
        nm = lambda v: ('sq', S.index(v)) if v in S else (i, v)  # noqa: E731
        sqe = {frozenset((S[k], S[(k + 1) % 4])) for k in range(4)}
        G.add_edges_from((nm(a), nm(b)) for a, b in g.edges() if frozenset((a, b)) not in sqe)
    return G


def square_of(g):
    ok, emb = nx.check_planarity(g)
    seen = set()
    col = nx.bipartite.color(g)
    for u, v in emb.edges():
        if (u, v) not in seen:
            f = emb.traverse_face(u, v, mark_half_edges=seen)
            if len(f) == 4:
                i0 = [k for k in range(4) if col[f[k]] == 0][0]
                return tuple(f[i0:] + f[:i0])


def analyse(g, name):
    named = all(isinstance(v, tuple) and v[0] in ('p', 'l') for v in g)
    if named:
        col = {v: (0 if v[0] == 'p' else 1) for v in g}
        g = nx.convert_node_labels_to_integers(g, label_attribute='name')
        col = {v: col[g.nodes[v]['name']] for v in g}
    else:
        g = nx.convert_node_labels_to_integers(g)
        col = nx.bipartite.color(g)
    pts = [v for v in g if col[v] == 0]
    lns = [v for v in g if col[v] == 1]
    E = [tuple(e) for e in g.edges()]
    T = nx.minimum_spanning_tree(g)
    tree = {frozenset(e) for e in T.edges()}
    cotree = [e for e in E if frozenset(e) not in tree]
    beta = len(cotree)
    # fundamental cycle of each co-tree edge, as a set of edges
    fund = []
    for (a, b) in cotree:
        path = nx.shortest_path(T, a, b)
        fund.append({frozenset((path[k], path[k + 1])) for k in range(len(path) - 1)} | {frozenset((a, b))})
    mask = {frozenset(e): sum(1 << j for j, C in enumerate(fund) if frozenset(e) in C) for e in E}
    pidx = {p: k for k, p in enumerate(pts)}
    X = ((np.arange(2 ** len(pts))[:, None] >> np.arange(len(pts))[None, :]) & 1).astype(np.int8)
    cot_index = {frozenset(e): j for j, e in enumerate(cotree)}
    counts = np.zeros(2 ** beta, dtype=np.int64)
    line_inc = [[(pidx[p], cot_index.get(frozenset((l, p)))) for p in g[l]] for l in lns]
    for s in range(2 ** beta):
        good = np.ones(len(X), dtype=bool)
        for inc in line_inc:
            cols = [X[:, pi] ^ (1 if (j is not None and s >> j & 1) else 0) for pi, j in inc]
            good &= ~((cols[0] == cols[1]) & (cols[1] == cols[2]))
        counts[s] = good.sum()
    knots = [s for s in range(2 ** beta) if counts[s] == 0]
    traps = []
    for s in range(2 ** beta):
        if counts[s] == 0:
            continue
        if all(counts[s ^ m] >= counts[s] for m in mask.values()):
            traps.append(s)
    # flip distance from the knot's class (if any) and monotonicity of counts along it
    dist = {}
    if knots:
        H = nx.Graph()
        for s in range(2 ** beta):
            for m in set(mask.values()):
                H.add_edge(s, s ^ m)
        dist = nx.single_source_shortest_path_length(H, knots[0])
    by_dist = {}
    for s, d in dist.items():
        by_dist.setdefault(d, []).append(int(counts[s]))
    plain = int(counts[0])
    rec = {"vertices": g.number_of_nodes(), "planar": nx.check_planarity(g)[0], "sign classes": 2 ** beta,
           "classes with no colouring (knot's class)": len(knots), "traps (classes with colourings and no lower neighbour)": len(traps),
           "smallest count among traps": int(min(counts[t] for t in traps)) if traps else None,
           "plain class count": plain, "largest count": int(counts.max()),
           "counts by flip distance from the knot (min, max)": {d: [min(v), max(v)] for d, v in sorted(by_dist.items())}}
    print(name, json.dumps(rec), round(time.time() - T0, 1), "s", flush=True)
    return rec


CUBE = nx.convert_node_labels_to_integers(nx.hypercube_graph(3))
P6 = nx.circular_ladder_graph(6)
P8 = nx.circular_ladder_graph(8)
TO = nx.convert_node_labels_to_integers(CL.omnitruncation(nx.complete_graph(4)))
FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def point_block(H, p):
    """replace point p by a Fano plane minus the line (0, 1, 2), whose points 0, 1, 2 take p's three places"""
    lines, k = [], 0
    for l in H:
        nl = []
        for q in l:
            if q == p:
                nl.append(('b', p, k))
                k += 1
            else:
                nl.append(q)
        lines.append(tuple(nl))
    return lines + [tuple(('b', p, q) for q in fl) for fl in FANO[1:]]


def line_block(H, i):
    """replace line i by a Fano plane minus the point 0; the three lines through 0 take line i's three points"""
    l = H[i]
    through0 = [fl for fl in FANO if 0 in fl]
    out = [H[j] for j in range(len(H)) if j != i]
    for slot, fl in zip(l, through0):
        out.append(tuple(('d', i, q) for q in fl if q != 0) + (slot,))
    return out + [tuple(('d', i, q) for q in fl) for fl in FANO if 0 not in fl]


def incidence(H):
    g = nx.Graph()
    for i, l in enumerate(H):
        for q in l:
            g.add_edge(('p', q), ('l', i))
    return g


GRAPHS = {
    "cube": CUBE,
    "6-prism": P6,
    "8-prism": P8,
    "Heawood (Fano)": nx.heawood_graph(),
    "trisum of three cubes": trisum([(CUBE, square_of(CUBE))] * 3),
    "trisum of cube, cube, 6-prism": trisum([(CUBE, square_of(CUBE)), (CUBE, square_of(CUBE)), (P6, square_of(P6))]),
    "truncated octahedron": TO,
    "Fano with a point block (13 points)": incidence(point_block(FANO, 0)),
    "Fano with a line block (13 points)": incidence(line_block(FANO, 0)),
    "Pappus (girth 6, control)": nx.pappus_graph(),
    "K3,3 (control, not Pfaffian)": nx.complete_bipartite_graph(3, 3),
    "Moebius-Kantor (control)": nx.LCF_graph(16, [5, -5], 8),
}
OUT = {name: analyse(g, name) for name, g in GRAPHS.items()}
pf = {k: v for k, v in OUT.items() if v["classes with no colouring (knot's class)"] == 1}
OUT["summary"] = {"Pfaffian graphs (one class with no colouring)": sorted(pf),
                  "Pfaffian graphs with traps": sorted(k for k, v in pf.items() if v["traps (classes with colourings and no lower neighbour)"]),
                  "seconds": round(time.time() - T0, 1)}
print(json.dumps(OUT["summary"]))
if "--write" in sys.argv:
    (HERE / "results.json").write_text(json.dumps(OUT, indent=1) + "\n")
