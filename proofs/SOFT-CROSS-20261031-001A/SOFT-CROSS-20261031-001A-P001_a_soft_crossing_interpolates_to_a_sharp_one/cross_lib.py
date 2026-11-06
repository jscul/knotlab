"""A soft crossing interpolates to a sharp one (SOFT-CROSS-20261031-001A).

Instances are signed cubic bipartite graphs: networkx graphs whose vertices are ('pt', ...) points or ('ln', ...) lines, with a set of
negated edges (frozensets). #col counts point colourings in which every line sees (colour xor sign) not all equal.

The soft crossing (TWIST-COUNT-20261030-001B): a junction square (c0, c1, c2, c3) glued by trisum to two twisted copies of the truncated
octahedron page, with the incidence of c3 into the second page negated. Its Hadamard signature on the host's legs is crossover-type with
straight entries (40000, -1112, 3336, -192).

A *k-snake* is k junctions in series: wire A (legs at the points c0, c2) passes one host line between consecutive junctions, wire B (legs at
the lines c1, c3) passes a host point, a host line and a host point. Every spare leg of this plumbing is closed by a *dead cap*, the cube
minus an edge, whose count does not depend on what its two attachments see."""
import itertools
import numpy as np
import networkx as nx
import computation_lib as CL

PAGE = CL.omnitruncation(nx.complete_graph(4))                     # the truncated octahedron (flags of K4)
SQUARE = [(2, 0, 1), (2, 0, 0), (0, 2, 1), (0, 2, 0)]             # c0, c1, c2, c3 on a 4-face; c0, c2 are points
SIGN_Q = [((1, 0, 0), (1, 0, 1)), ((1, 3, 0), (1, 3, 1)), ((1, 3, 0), (3, 1, 1)), ((2, 3, 0), (3, 2, 1))]
SIGN_R = [((1, 3, 0), (3, 1, 1)), ((2, 1, 0), (2, 1, 1)), ((3, 0, 0), (3, 0, 1)), ((3, 1, 0), (1, 3, 1)), ((3, 2, 0), (2, 3, 1)),
          ((3, 2, 0), (3, 2, 1))]                                  # (line, point) incidences negated in the two pages
C3_INTO_R_NEGATED = True                                           # the junction's incidence signs: (0,0,0) at c1, (0,0,1) at c3


def is_point(v):
    return v[0] == 'pt'


class Builder:
    """accumulates a signed cubic bipartite graph"""

    def __init__(self):
        self.g = nx.Graph()
        self.neg = set()

    def edge(self, a, b, negated=False):
        assert is_point(a) != is_point(b), (a, b)
        self.g.add_edge(a, b)
        if negated:
            self.neg.add(frozenset((a, b)))

    def page(self, tag, square, signs):
        """a copy of the truncated octahedron page with its square edges deleted and its square identified with `square`"""
        pc = nx.bipartite.color(PAGE)[SQUARE[0]]
        sqe = {frozenset((SQUARE[i], SQUARE[(i + 1) % 4])) for i in range(4)}

        def name(v):
            if v in SQUARE:
                return square[SQUARE.index(v)]
            return ('pt' if nx.bipartite.color(PAGE)[v] == pc else 'ln', tag, v)
        col = nx.bipartite.color(PAGE)
        for a, b in PAGE.edges():
            if frozenset((a, b)) in sqe:
                continue
            line, point = (a, b) if col[a] != pc else (b, a)
            self.edge(name(point), name(line), (line, point) in signs)
        return name

    def junction(self, j):
        """the soft crossing at square ('J', j): returns its four square vertices (points c0, c2; lines c1, c3)"""
        sq = [('pt', 'J', j, 0), ('ln', 'J', j, 1), ('pt', 'J', j, 2), ('ln', 'J', j, 3)]
        self.page(('Q', j), sq, set(SIGN_Q))
        nameR = self.page(('R', j), sq, set(SIGN_R))
        if C3_INTO_R_NEGATED:
            att3 = [w for w in PAGE[SQUARE[3]] if w not in SQUARE][0]
            self.neg.add(frozenset((sq[3], nameR(att3))))
        return sq

    def cap(self, tag, line_out, point_out):
        """the cube minus an edge: its point u attaches to the outside line, its line v to the outside point"""
        cube = nx.hypercube_graph(3)
        col = nx.bipartite.color(cube)
        u = (0, 0, 0)
        v = (1, 0, 0)
        assert col[u] != col[v]
        nm = lambda w: ('pt' if col[w] == col[u] else 'ln', 'cap', tag, w)  # noqa: E731
        for a, b in cube.edges():
            if {a, b} != {u, v}:
                self.edge(nm(a), nm(b))
        self.edge(nm(u), line_out)
        self.edge(nm(v), point_out)

    def snake(self, k, a_in, b_in, a_out, b_out, tag='S'):
        """k junctions in series between the outside lines a_in, a_out (wire A) and the outside points b_in, b_out (wire B)"""
        prev = None
        for j in range(k):
            c0, c1, c2, c3 = self.junction((tag, j))
            if prev is None:
                self.edge(c0, a_in)
                self.edge(c1, b_in)
            else:
                pc2, pc3 = prev
                lam = ('ln', tag, j, 'lam')
                pi, mu, pi2 = ('pt', tag, j, 'pi'), ('ln', tag, j, 'mu'), ('pt', tag, j, 'pi2')
                self.edge(pc2, lam)
                self.edge(lam, c0)
                self.edge(pc3, pi)
                self.edge(pi, mu)
                self.edge(mu, pi2)
                self.edge(pi2, c1)
                self.cap((tag, j, 'a'), lam, pi)
                self.cap((tag, j, 'b'), mu, pi2)
            prev = (c2, c3)
        self.edge(prev[0], a_out)
        self.edge(prev[1], b_out)

    def system(self):
        """(lines as tuples of point indices, negated (line index, point index)) for amplitude_lib.count"""
        pts = sorted((v for v in self.g if is_point(v)), key=str)
        lns = sorted((v for v in self.g if not is_point(v)), key=str)
        pid = {v: i for i, v in enumerate(pts)}
        H = [tuple(sorted(pid[w] for w in self.g[l])) for l in lns]
        neg = [(i, pid[p]) for i, l in enumerate(lns) for p in self.g[l] if frozenset((l, p)) in self.neg]
        assert all(d == 3 for _, d in self.g.degree())
        return H, neg


# ------------------------------------------------------------------------------------------------ K3,3 with its crossing replaced
K33_POINTS = [('pt', 'K', i) for i in range(3)]
K33_LINES = [('ln', 'K', i) for i in range(3)]
E_EDGE = (K33_POINTS[0], K33_LINES[1])      # crosses F_EDGE in the drawing (hexagon P0 L0 P1 L1 P2 L2, chords P0L1, P1L2, P2L0)
F_EDGE = (K33_POINTS[2], K33_LINES[0])


def k33_signs(mask):
    """a signing of K3,3 from a 9-bit mask (edges in order P_i L_j)"""
    return {(K33_POINTS[i], K33_LINES[j]) for i in range(3) for j in range(3) if mask >> (3 * i + j) & 1}


def k33_instance(k, signs):
    """K3,3 drawn with one crossing (E_EDGE x F_EDGE); E passes the k-snake as wire B (P0 - snake - pi_e - L1), F as wire A
    (P2 - l_f - snake - L0); pi_e and l_f are closed by a cap"""
    B = Builder()
    for p in K33_POINTS:
        for l in K33_LINES:
            if (p, l) not in (E_EDGE, F_EDGE):
                B.edge(p, l, (p, l) in signs)
    pe, lf = ('pt', 'pi_e'), ('ln', 'l_f')
    B.edge(pe, E_EDGE[1], E_EDGE in signs)
    B.edge(F_EDGE[0], lf)
    B.snake(k, lf, E_EDGE[0], F_EDGE[1], pe)
    B.neg |= {frozenset((F_EDGE[1], ('pt', 'J', ('S', k - 1), 2)))} if F_EDGE in signs else set()
    B.cap('c', lf, pe)
    return B


def k33_system(signs):
    H, neg = [], []
    for j, l in enumerate(K33_LINES):
        H.append((0, 1, 2))
        for i, p in enumerate(K33_POINTS):
            if (p, l) in signs:
                neg.append((j, i))
    return H, neg


# ------------------------------------------------------------------------------------------------ tensors
def nae(a, b, c):
    return 0 if a == b == c else 1


H2 = np.array([[1, 1], [1, -1]], dtype=object)


def hada(F):
    G = np.array(F, dtype=object)
    for ax in range(4):
        G = np.moveaxis(np.tensordot(H2, G, axes=([1], [ax])), 0, ax)
    return G


STRAIGHT = [(0, 0, 0, 0), (0, 1, 0, 1), (1, 0, 1, 0), (1, 1, 1, 1)]          # states (yA, yB) = 00, 01, 10, 11
TURNING = [(1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 1), (1, 0, 0, 1)]


def snake_tensor(W, k, wire_b_line=True):
    """colour-basis tensor of the k-snake on its legs (A_in, B_in, A_out, B_out), from the junction tensor W(x0, z1, x2, z3) and the
    plumbing (a host line on wire A and a host point, line and point on wire B, each spare leg free), without the caps' factor 3 each;
    wire_b_line=False passes wire B through a single host point (a control)"""
    T = np.array(W, dtype=object)
    for j in range(1, k):
        T2 = np.zeros((2, 2, 2, 2), dtype=object)
        for ai, bi, a, b in itertools.product((0, 1), repeat=4):
            t = T[ai, bi, a, b]
            if t == 0:
                continue
            for x0, b2 in itertools.product((0, 1), repeat=2):
                w = t * sum(nae(a, x0, f) for f in (0, 1)) * (sum(nae(b, b2, f) for f in (0, 1)) if wire_b_line else int(b == b2))
                for z1n, x2n, z3n in itertools.product((0, 1), repeat=3):
                    if z1n == b2:
                        T2[ai, bi, x2n, z3n] += w * W[x0, z1n, x2n, z3n]
        T = T2
    return T


# ------------------------------------------------------------------------------------------------ Pfaffian certificates
def leaves_of(B):
    """the planar pieces of an instance: the host (everything outside the pages, with every junction's square edges) and every page copy
    (with its square edges), each with its squares"""
    tags = sorted({v[2] for v in B.g if v[1] == 'J'}, key=str)
    sqs = [(('pt', 'J', j, 0), ('ln', 'J', j, 1), ('pt', 'J', j, 2), ('ln', 'J', j, 3)) for j in tags]
    in_page = lambda v: len(v) == 3 and isinstance(v[1], tuple) and v[1][0] in ('Q', 'R')  # noqa: E731
    host = nx.Graph()
    host.add_edges_from((a, b) for a, b in B.g.edges() if not in_page(a) and not in_page(b))
    for S in sqs:
        host.add_edges_from((S[i], S[(i + 1) % 4]) for i in range(4))
    pages = {}
    for v in B.g:
        if in_page(v):
            pages.setdefault(v[1], set()).add(v)
    out = [(host, sqs)]
    for tag, vs in sorted(pages.items(), key=str):
        S = [s for s in sqs if s[0][2] == tag[1]][0]
        g = B.g.subgraph(set(vs) | set(S)).copy()
        g.add_edges_from((S[i], S[(i + 1) % 4]) for i in range(4))
        out.append((g, [S]))
    return out


def certify_pfaffian(B, TW, AM):
    """a Pfaffian certificate: every piece planar, and the Kasteleyn signings of the pieces, switched to one pattern on every square and
    glued, leave the instance non-colourable (THREEFOLD-AMPLITUDE C, Lemma 4)"""
    lv = leaves_of(B)
    planar = all(nx.check_planarity(g)[0] for g, s in lv)
    kap = TW.kasteleyn_tree_signing(lv)
    C = Builder()
    C.g, C.neg = B.g, set(kap)
    H, neg = C.system()
    return planar and not AM.colourable(H, neg), len(lv)


# ------------------------------------------------------------------------------------------------ long edges
def long_edge(B, p, l, k, tag, negated=False):
    """the edge (point p, line l) drawn as a path p - l1 - p1 - ... - lk - pk - l: k interior lines and k interior points, each pair
    (li, pi) closed by a cap; the sign of the original incidence sits on (l, pk)"""
    prev = p
    for i in range(k):
        li, pi = ('ln', 'E', tag, i), ('pt', 'E', tag, i)
        B.edge(prev, li)
        B.edge(li, pi)
        B.cap(('E', tag, i), li, pi)
        prev = pi
    B.edge(prev, l, negated)
