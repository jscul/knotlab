"""Planar knot spaces beyond the census, for HANDLE-EMERGENCE-20261102-001A.

A knot space's incidence graph (points on one side, lines on the other) is cubic and bipartite. When it is plane, Kasteleyn signs make
the signed knot fail: on every face of length 2k the number of negative incidences is congruent to k + 1 mod 2 (all faces but one; the
last follows). Failure is checked directly, never assumed.

Families:
- grow(): from the cube (the incidence graph of K4^(3)) by ladder moves. A move picks a face and two of its edges at even distance
  along it, subdivides each twice and joins the four new vertices by a square inside the face; the graph stays plane, cubic and
  bipartite.
- prism(k): the prism over a 2k-cycle.
- permutohedron(): the truncated octahedron, as permutations of four symbols joined by adjacent transpositions."""
import itertools
import random
import sys
from pathlib import Path

import networkx as nx
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "proofs/HUB-GLUE-20261102-001A/HUB-GLUE-20261102-001A-P001_selection_leaves_a_hub_and_pieces_glue"))
import glue_lib as G  # noqa: E402


def faces(emb):
    seen, out = set(), []
    for v, w in emb.edges():
        if (v, w) not in seen:
            out.append(emb.traverse_face(v, w, mark_half_edges=seen))
    return out


def ladder(g, rng):
    ok, emb = nx.check_planarity(g)
    assert ok
    f = rng.choice([f for f in faces(emb) if len(f) >= 4])
    k = len(f)
    i, j = rng.choice([(i, j) for i in range(k) for j in range(i + 2, k, 2)])
    vi, vi1, vj, vj1 = f[i], f[(i + 1) % k], f[j], f[(j + 1) % k]
    a1, a2, b1, b2 = (max(g.nodes) + t for t in range(1, 5))
    h = g.copy()
    h.remove_edge(vi, vi1)
    h.remove_edge(vj, vj1)
    h.add_edges_from([(vi, a1), (a1, a2), (a2, vi1), (vj, b1), (b1, b2), (b2, vj1), (a1, b2), (a2, b1)])
    return h


def grow(n_points, seed):
    rng = random.Random(seed)
    g = nx.convert_node_labels_to_integers(nx.hypercube_graph(3))
    while g.number_of_nodes() < 2 * n_points:
        g = ladder(g, rng)
    return g


def prism(k):
    g = nx.Graph()
    m = 2 * k
    g.add_edges_from([(i, (i + 1) % m) for i in range(m)] + [(m + i, m + (i + 1) % m) for i in range(m)] + [(i, m + i) for i in range(m)])
    return g


def permutohedron():
    perms = list(itertools.permutations(range(4)))
    idx = {p: i for i, p in enumerate(perms)}
    g = nx.Graph()
    for p in perms:
        for i in range(3):
            q = list(p)
            q[i], q[i + 1] = q[i + 1], q[i]
            g.add_edge(idx[p], idx[tuple(q)])
    return g


def kasteleyn(g):
    """incidence signs (1 = negative) satisfying the face condition on all faces but one, by elimination over F2"""
    ok, emb = nx.check_planarity(g)
    assert ok
    edges = sorted({tuple(sorted(e)) for e in g.edges()})
    idx = {e: i for i, e in enumerate(edges)}
    rows, rhs = [], []
    for f in faces(emb)[1:]:
        r = np.zeros(len(edges), dtype=np.uint8)
        for a, b in zip(f, f[1:] + f[:1]):
            r[idx[tuple(sorted((a, b)))]] ^= 1
        rows.append(r)
        rhs.append((len(f) // 2 + 1) % 2)
    A, y = np.array(rows, dtype=np.uint8), np.array(rhs, dtype=np.uint8)
    piv, r = [], 0
    for c in range(A.shape[1]):
        p = next((i for i in range(r, A.shape[0]) if A[i, c]), None)
        if p is None:
            continue
        A[[r, p]], y[[r, p]] = A[[p, r]], y[[p, r]]
        for i in range(A.shape[0]):
            if i != r and A[i, c]:
                A[i] ^= A[r]
                y[i] ^= y[r]
        piv.append(c)
        r += 1
    assert not y[r:].any()
    x = np.zeros(A.shape[1], dtype=np.uint8)
    for i, c in enumerate(piv):
        x[c] = y[i]
    return {e: int(x[idx[e]]) for e in edges}


def to_space(g, swap=False):
    """(lines, signs, n): points are one colour class of the incidence graph, lines the other; None if two lines coincide"""
    col = nx.bipartite.color(g)
    pts = sorted(v for v in g if col[v] == (1 if swap else 0))
    lns = sorted(v for v in g if col[v] == (0 if swap else 1))
    pi = {v: i for i, v in enumerate(pts)}
    sg = kasteleyn(g)
    lines = [tuple(pi[p] for p in sorted(g[L])) for L in lns]
    signs = [[sg[tuple(sorted((L, p)))] for p in sorted(g[L])] for L in lns]
    if len({frozenset(L) for L in lines}) < len(lines):
        return None
    return lines, signs, len(pts)


def incidence_planar(lines):
    g = nx.Graph()
    g.add_edges_from((("p", p), ("l", k)) for k, L in enumerate(lines) for p in L)
    return nx.check_planarity(g)[0]
