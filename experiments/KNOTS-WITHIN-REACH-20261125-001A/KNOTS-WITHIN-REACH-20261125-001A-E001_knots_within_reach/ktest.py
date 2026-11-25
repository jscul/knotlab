"""The knot test on large structures with at most two holders per distinction (runs 3 and checks), R 23.

Parity, ranks (SD line 133): rank(H) - rank(H without the columns of S_u) = 1.  With at most two holders, H's transpose
is the incidence matrix of the graph G on the knots and one outside vertex o (a shared distinction joins its two holders,
a loose one joins its holder to o); over the field of two elements the rows of the knots have rank (number of knots) -
(number of components of G without o), so the difference is 1 + (components of G - u without o) - (components of G
without o).  Computed by connected components of G - u, for each knot tested.
Parity, kernel (FD 7): the allowed states are the cycle space of G; its projection onto the edges at u has rank
deg(u) - (number of components of G - u that u reaches); rank |S_u| - 1 exactly when u is no cut vertex of G.  Computed
by one articulation-point search (a different algorithm for the same quantity).
Both are checked against the fold engine's parity_test (Gaussian elimination) on small structures before use.
Not-all-equal: the fold engine's birth method (knots.jointly_free) on the structure before the knot's round, and its
direct test (knots.nae_direct) where the knot has at most 12 places."""
from __future__ import annotations

import numpy as np
import networkx as nx
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

import kwr


def graph_with_outside(S, N, nd, drop_fresh_of=None):
    """Edges of G for the knots < N and distinctions < nd; o = N.  drop_fresh_of: a knot whose own fresh
    distinctions (held by it alone, made in its round) are left out (the parity closing birth)."""
    rows, cols = [], []
    o = N
    for d in range(nd):
        hh = [w for w in S.holders[d] if w < N]
        if not hh:
            continue
        if len(hh) == 2:
            rows.append(hh[0])
            cols.append(hh[1])
        elif len(hh) == 1:
            if drop_fresh_of is not None and hh[0] == drop_fresh_of:
                continue
            rows.append(hh[0])
            cols.append(o)
        else:
            raise ValueError('more than two holders')
    return np.array(rows), np.array(cols)


def parity_ranks_graph(S, N, nd, knots_, drop_fresh_of=None):
    r, c = graph_with_outside(S, N, nd, drop_fresh_of)
    n = N + 1
    A = csr_matrix((np.ones(len(r)), (r, c)), shape=(n, n))
    A = A + A.T
    ncomp, lab = connected_components(A, directed=False)
    o = N
    base = len(set(lab[:N]) - {lab[o]})
    out = {}
    for u in knots_:
        keep = np.ones(n, dtype=bool)
        keep[u] = False
        idx = np.nonzero(keep)[0]
        B = A[idx][:, idx]
        k, lb = connected_components(B, directed=False)
        o_new = int(np.searchsorted(idx, o))
        comps_without_o = len(set(lb.tolist()) - {lb[o_new]})
        out[u] = (1 + comps_without_o - base) == 1
    return out


def parity_kernel_graph(S, N, nd, knots_, drop_fresh_of=None):
    r, c = graph_with_outside(S, N, nd, drop_fresh_of)
    G = nx.MultiGraph()
    G.add_nodes_from(range(N + 1))
    G.add_edges_from(zip(r.tolist(), c.tolist()))
    simple = nx.Graph(G)
    cut = set(nx.articulation_points(simple))
    return {u: (u not in cut) for u in knots_}
