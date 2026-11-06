"""A plain crossing inside braces (PLAIN-BRACE-20261031-001A).

A *site* replaces a crossing of an edge e (wire A) and an edge f (wire B). Wire A runs from e's point end, wire B from f's line end:
    e's point side - l_s - c0 [junction 0] c2 - lambda_0 - c0 [junction 1] ... c2 [junction k-1] - e's line side
    f's line side  - pi_s - c1 [junction 0] c3 - pi_0     - c1 [junction 1] ... c3 [junction k-1] - f's point side
with the start rung l_s - pi_s and a rung lambda_j - pi_j between consecutive junctions; no caps. Every junction is a square
(c0, c1, c2, c3) glued by trisum to two plain cubes. The P-side ports (l_s for wire A, c3 for wire B) are lines and the L-side ports (c2
for wire A, pi_s for wire B) are points, so sites chain along an edge by direct edges.

As a map from (colour of e's point end, colour of pi_s) to (colour of the last c2, colour of f's point end) the site acts by (N W)^k, with W
the junction and N the rung; the exact crossing (e and f restored) is the identity."""
import itertools
import networkx as nx
import sympy as sp
import cross_lib as X
import twist_lib as TW

CUBE = nx.convert_node_labels_to_integers(nx.hypercube_graph(3), ordering="sorted")
LAB = (2, 6, 4, 0)                       # a square face of the cube, (c0, c1, c2, c3) with c0 a point
ST = [(0, 0), (0, 1), (1, 0), (1, 1)]


def nae(a, b, c):
    return 0 if a == b == c else 1


def page_tensor(g=CUBE, lab=LAB):
    inc, pts, att, sq = TW.page(g, list(lab))
    assert tuple(sq) == tuple(lab)
    return TW.page_tensor(inc, pts, att, set())


def matrices(g=CUBE, lab=LAB):
    """W (junction of two plain copies of the page) and N (rung) as 4 x 4 matrices on the states (wire A colour, wire B colour)"""
    F = page_tensor(g, lab)
    Wt = TW.junction(F, F, (0, 0, 0), (0, 0, 0))
    W = sp.Matrix(4, 4, lambda i, j: Wt[ST[i][0], ST[i][1], ST[j][0], ST[j][1]])
    N = sp.Matrix(4, 4, lambda i, j: nae(ST[i][0], ST[j][0], ST[j][1]) * (ST[i][1] == ST[j][1]))
    return W, N


def add_page(B, tag, g, lab, sq_names):
    colg = nx.bipartite.color(g)
    pc = colg[lab[0]]
    sqe = {frozenset((lab[i], lab[(i + 1) % 4])) for i in range(4)}
    nm = lambda v: sq_names[lab.index(v)] if v in lab else (('pt' if colg[v] == pc else 'ln'), tag, v)  # noqa: E731
    for a, b in g.edges():
        if frozenset((a, b)) in sqe:
            continue
        pa, lb = (a, b) if colg[a] == pc else (b, a)
        B.edge(nm(pa), nm(lb))


def site(B, c, k, g=CUBE, lab=LAB):
    """build the site c with k junctions; returns {'A': (P-side port, L-side port), 'B': (P-side port, L-side port)}"""
    ls, ps = ('ln', 's', c), ('pt', 's', c)
    B.edge(ps, ls)
    prevA, prevB = ls, ps
    for j in range(k):
        sqn = [('pt', 'J', (c, j), 0), ('ln', 'J', (c, j), 1), ('pt', 'J', (c, j), 2), ('ln', 'J', (c, j), 3)]
        add_page(B, ('Q', (c, j)), g, lab, sqn)
        add_page(B, ('R', (c, j)), g, lab, sqn)
        B.edge(sqn[0], prevA)
        B.edge(prevB, sqn[1])
        if j < k - 1:
            lam, pi = ('ln', 'lam', (c, j)), ('pt', 'pi', (c, j))
            B.edge(sqn[2], lam)
            B.edge(pi, sqn[3])
            B.edge(pi, lam)
            prevA, prevB = lam, pi
    last = (('pt', 'J', (c, k - 1), 2), ('ln', 'J', (c, k - 1), 3))
    return {'A': (ls, last[0]), 'B': (last[1], ps)}


def k33_instance(k, unreversed=False):
    """K3,3 with E = (P0, L1) and F = (P2, L0) crossing once; F is wire A, E wire B. unreversed: wire B from E's point end, the site of
    SOFT-CROSS A with its cap replaced by a rung (control)."""
    B = X.Builder()
    for p in X.K33_POINTS:
        for l in X.K33_LINES:
            if (p, l) not in (X.E_EDGE, X.F_EDGE):
                B.edge(p, l)
    if not unreversed:
        ports = site(B, 0, k)
        B.edge(X.F_EDGE[0], ports['A'][0])      # P2 - l_s
        B.edge(ports['A'][1], X.F_EDGE[1])      # c2 - L0
        B.edge(X.E_EDGE[1], ports['B'][1])      # L1 - pi_s
        B.edge(ports['B'][0], X.E_EDGE[0])      # c3 - P0
        return B
    pe, lf = ('pt', 'pi_e'), ('ln', 'l_f')
    B.edge(pe, X.E_EDGE[1])
    B.edge(X.F_EDGE[0], lf)
    prevA, prevB = lf, X.E_EDGE[0]
    for j in range(k):
        sqn = [('pt', 'J', (0, j), 0), ('ln', 'J', (0, j), 1), ('pt', 'J', (0, j), 2), ('ln', 'J', (0, j), 3)]
        add_page(B, ('Q', (0, j)), CUBE, LAB, sqn)
        add_page(B, ('R', (0, j)), CUBE, LAB, sqn)
        B.edge(sqn[0], prevA)
        B.edge(prevB, sqn[1])
        if j < k - 1:
            lam, pi = ('ln', 'lam', (0, j)), ('pt', 'pi', (0, j))
            B.edge(sqn[2], lam)
            B.edge(pi, sqn[3])
            B.edge(pi, lam)
            prevA, prevB = lam, pi
    B.edge(('pt', 'J', (0, k - 1), 2), X.F_EDGE[1])
    B.edge(pe, ('ln', 'J', (0, k - 1), 3))
    B.edge(pe, lf)                              # the rung that replaces SOFT-CROSS A's cap
    return B


def k33_rest():
    """R(x, y, s, t): colourings of K3,3 minus E and F with P2 = x, L1 seeing y on E's former leg, L0 seeing s on F's, P0 = t"""
    Pp, Ll = X.K33_POINTS, X.K33_LINES
    R = {}
    for x, y, s, t in itertools.product((0, 1), repeat=4):
        cnt = 0
        for p1 in (0, 1):
            col = {Pp[0]: t, Pp[1]: p1, Pp[2]: x}
            ok = True
            for l in Ll:
                seen = [col[p] for p in Pp if (p, l) not in (X.E_EDGE, X.F_EDGE)]
                if l == X.E_EDGE[1]:
                    seen.append(y)
                if l == X.F_EDGE[1]:
                    seen.append(s)
                ok &= len(set(seen)) == 2
            cnt += ok
        R[(x, y, s, t)] = cnt
    return R


def faces(g):
    ok, emb = nx.check_planarity(g)
    assert ok
    seen, out = set(), []
    for u, v in emb.edges():
        if (u, v) not in seen:
            out.append(emb.traverse_face(u, v, mark_half_edges=seen))
    return out


def cyclic4(g):
    """a planar cubic graph has no cyclic edge cut of size at most 3: its dual has no loop, no separating 2-cycle, no separating triangle"""
    fs = faces(g)
    where = {}
    for k, f in enumerate(fs):
        for i in range(len(f)):
            where.setdefault(frozenset((f[i], f[(i + 1) % len(f)])), []).append(k)
    D = nx.MultiGraph()
    D.add_nodes_from(range(len(fs)))
    for e, ks in where.items():
        if len(ks) == 1 or ks[0] == ks[1]:
            return False
        D.add_edge(ks[0], ks[1])
    S = nx.Graph(D)
    for a, b in S.edges():
        if D.number_of_edges(a, b) >= 2:
            h = S.copy()
            h.remove_nodes_from([a, b])
            if h.number_of_nodes() and not nx.is_connected(h):
                return False
    for a in S:
        for b, c in itertools.combinations([x for x in S[a] if x > a], 2):
            if S.has_edge(b, c):
                h = S.copy()
                h.remove_nodes_from([a, b, c])
                if h.number_of_nodes() and not nx.is_connected(h):
                    return False
    return True
