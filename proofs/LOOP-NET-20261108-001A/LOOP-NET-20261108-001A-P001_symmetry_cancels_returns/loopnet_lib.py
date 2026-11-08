"""Networks of loops (LOOP-NET-20261108-001A): rule-60 rings joined by contacts with law (12, 12), read through their contact graph.

A network is (sizes, contacts) in SEPARATE-20261108-001A's net_lib format: contact (ring a, position on a, ring b, position on b, law).
Every contact here has law (12, 12): on each of its rings it reads its left neighbour. On a ring the contacts in increasing position
cut it into corners; the corner from contact d to the next contact e holds the l >= 1 own cells between them. The contact graph has an
arc d -> e for every corner, of weight z a^l with a = z/(1 + z) over GF(2); K[e][d] sums the weights of the corners from d to e, and
D = (I + K)^-1. Positions give each ring a cyclic order of its contacts: a rotation system on the ring graph (rings as vertices, contacts
as edges), so an embedding in an oriented surface. Rational functions over GF(2) are pairs of polynomials stored as Python ints
(bit i = coefficient of z^i)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import net_lib as N  # noqa: E402

LAW = (12, 12)


# ---------- rational functions over GF(2)
def pmul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        b >>= 1
    return out


def pdivmod(a, b):
    q, db = 0, b.bit_length()
    while a and a.bit_length() >= db:
        sh = a.bit_length() - db
        q ^= 1 << sh
        a ^= b << sh
    return q, a


def pgcd(a, b):
    while b:
        a, b = b, pdivmod(a, b)[1]
    return a


def rnorm(n, d):
    if n == 0:
        return (0, 1)
    g = pgcd(n, d)
    return (pdivmod(n, g)[0], pdivmod(d, g)[0])


def radd(x, y):
    return rnorm(pmul(x[0], y[1]) ^ pmul(y[0], x[1]), pmul(x[1], y[1]))


def rmul(x, y):
    return rnorm(pmul(x[0], y[0]), pmul(x[1], y[1]))


def rinv(x):
    return rnorm(x[1], x[0])


def ppow(p, e):
    out = 1
    for _ in range(e):
        out = pmul(out, p)
    return out


ZERO, ONE = (0, 1), (1, 1)
Z, ONE_Z = 0b10, 0b11


def corner_weight(l):
    """z a^l = z^(l + 1) / (1 + z)^l"""
    return rnorm(ppow(Z, l + 1), ppow(ONE_Z, l))


def valuation(x):
    """order of vanishing at z = 0 of a nonzero rational function"""
    n, d = x
    return ((n & -n).bit_length() - 1) - ((d & -d).bit_length() - 1)


# ---------- the contact graph
def corners(sizes, contacts):
    """arcs (d, e, ring, l): e follows d on the ring, with l own cells between them"""
    on = {}
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        on.setdefault(ra, []).append((pa, c))
        on.setdefault(rb, []).append((pb, c))
    out = []
    for ring in sorted(on):
        lst = sorted(on[ring])
        s, m = sizes[ring], len(lst)
        for i in range(m):
            p, d = lst[i]
            q, e = lst[(i + 1) % m]
            out.append((d, e, ring, (q - p - 1) % s if m > 1 else s - 1))
    return out


def dmatrix(sizes, contacts):
    """D = (I + K)^-1 exactly, by Gauss-Jordan over GF(2)(z)"""
    n = len(contacts)
    K = [[ZERO] * n for _ in range(n)]
    for d, e, ring, l in corners(sizes, contacts):
        K[e][d] = radd(K[e][d], corner_weight(l))
    M = [[radd(ONE if i == j else ZERO, K[i][j]) for j in range(n)] + [ONE if i == j else ZERO for j in range(n)] for i in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col][0])
        M[col], M[piv] = M[piv], M[col]
        iv = rinv(M[col][col])
        M[col] = [rmul(x, iv) for x in M[col]]
        for r in range(n):
            if r != col and M[r][col][0]:
                f = M[r][col]
                M[r] = [radd(x, rmul(f, y)) for x, y in zip(M[r], M[col])]
    return [row[n:] for row in M]


def arc_matrix(sizes, contacts):
    """A[e][d] = number of corners from d to e, mod 2"""
    n = len(contacts)
    A = np.zeros((n, n), dtype=np.uint8)
    for d, e, ring, l in corners(sizes, contacts):
        A[e, d] ^= 1
    return A


def odd_returns(A):
    """{c: the lengths k with an odd number of closed walks c -> c}, exact: powers of A over GF(2) until they repeat"""
    n = A.shape[0]
    P, seen, k, out = A.copy(), {}, 1, {}
    A64 = A.astype(np.int64)
    while True:
        key = P.tobytes()
        if key in seen:
            return out, (seen[key], k - seen[key])
        seen[key] = k
        for c in np.nonzero(P.diagonal())[0]:
            out.setdefault(int(c), []).append(k)
        P = (A64 @ P.astype(np.int64) % 2).astype(np.uint8)
        k += 1


def faces(sizes, contacts):
    """the closed routes that change ring at every contact, as lists of corners, and the genus of the embedding"""
    arcs = corners(sizes, contacts)
    nxt = {(ring, d): (e, l) for d, e, ring, l in arcs}
    rings_of = {c: (ra, rb) for c, (ra, pa, rb, pb, law) in enumerate(contacts)}
    seen, out = set(), []
    for d, e, ring, l in arcs:
        if (ring, d) in seen:
            continue
        f, cur = [], (ring, d)
        while cur not in seen:
            seen.add(cur)
            R, x = cur
            y, ll = nxt[cur]
            f.append((R, x, y, ll))
            ra, rb = rings_of[y]
            cur = (rb if R == ra else ra, y)
        out.append(f)
    chi = len(sizes) - len(contacts) + len(out)
    return out, (2 - chi) // 2


# ---------- networks from rotation systems
def network(rot, edges, g):
    """rot: {vertex: [edge ids in cyclic order]}, edges: [(u, v)]; rings of m contacts get size m g, contacts equally spaced"""
    verts = sorted(rot, key=repr)
    idx = {v: i for i, v in enumerate(verts)}
    sizes = tuple(len(rot[v]) * g for v in verts)
    pos = {(v, e): j * g for v in verts for j, e in enumerate(rot[v])}
    return sizes, [(idx[u], pos[(u, e)], idx[v], pos[(v, e)], LAW) for e, (u, v) in enumerate(edges)]


def rotation_of(sizes, contacts):
    rot = {}
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        rot.setdefault(ra, []).append((pa, c))
        rot.setdefault(rb, []).append((pb, c))
    return {v: [c for p, c in sorted(l)] for v, l in rot.items()}, [(ra, rb) for (ra, pa, rb, pb, law) in contacts]


def flip(rot, edges, e):
    """an orientation-preserving automorphism of the map taking dart (e, u) to (e, v), or None. Darts (edge, tail); sigma turns a dart
    to the next edge of its tail's rotation, theta reverses it; a map automorphism commutes with both and is fixed by one dart's image."""
    succ = {}
    for v, lst in rot.items():
        for i, x in enumerate(lst):
            succ[(x, v)] = (lst[(i + 1) % len(lst)], v)

    def theta(d):
        x, t = d
        a, b = edges[x]
        return (x, b if t == a else a)
    u, v = edges[e]
    phi, stack = {(e, u): (e, v)}, [(e, u)]
    while stack:
        d = stack.pop()
        for op in (lambda y: succ[y], theta):
            d2, img = op(d), op(phi[d])
            if d2 in phi:
                if phi[d2] != img:
                    return None
            else:
                phi[d2] = img
                stack.append(d2)
    return phi if len(set(phi.values())) == len(phi) == len(succ) else None


def plane_rotation(Gr):
    import networkx as nx
    ok, emb = nx.check_planarity(Gr)
    assert ok
    eid = {frozenset(e): i for i, e in enumerate(Gr.edges())}
    return {v: [eid[frozenset((v, w))] for w in emb.neighbors_cw_order(v)] for v in emb.nodes()}, list(Gr.edges())


def dihedron(r):
    """a loop of r rings"""
    edges = [(i, (i + 1) % r) for i in range(r)]
    return {i: [(i - 1) % r, i] for i in range(r)}, edges


def hosohedron(m):
    """two rings sharing m contacts, in opposite orders"""
    return {0: list(range(m)), 1: list(range(m - 1, -1, -1))}, [(0, 1)] * m


def platonic(name):
    import networkx as nx
    G = {"tetrahedron": nx.complete_graph(4), "cube": nx.hypercube_graph(3), "octahedron": nx.octahedral_graph(),
         "dodecahedron": nx.dodecahedral_graph(), "icosahedron": nx.icosahedral_graph()}[name]
    return plane_rotation(nx.convert_node_labels_to_integers(G))


def square_torus(n):
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    return _torus(n, dirs, [(i, j) for i in range(n) for j in range(n)], lambda v, d: ((v[0] + d[0]) % n, (v[1] + d[1]) % n))


def triangular_torus(n):
    dirs = ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))
    return _torus(n, dirs, [(i, j) for i in range(n) for j in range(n)], lambda v, d: ((v[0] + d[0]) % n, (v[1] + d[1]) % n))


def _torus(n, dirs, verts, step):
    edges, eid = [], {}
    for v in verts:
        for d in dirs[:len(dirs) // 2]:
            w = step(v, d)
            eid[(v, d)] = eid[(w, (-d[0], -d[1]))] = len(edges)
            edges.append((v, w))
    return {v: [eid[(v, d)] for d in dirs] for v in verts}, edges


def honeycomb_torus(n):
    """A(i, j) = (i, j, 0) joined to B(i, j), B(i - 1, j), B(i, j - 1); both kinds list their edges in the same cyclic (ccw) order"""
    verts = [(i, j, s) for i in range(n) for j in range(n) for s in (0, 1)]
    edges, rot = [], {v: [None] * 3 for v in verts}
    for i in range(n):
        for j in range(n):
            a = (i, j, 0)
            for k, b in enumerate(((i, j, 1), ((i - 1) % n, j, 1), (i, (j - 1) % n, 1))):
                rot[a][k] = rot[b][k] = len(edges)
                edges.append((a, b))
    return rot, edges


def theta(p, q, r, planar=True):
    """two hub rings joined by three paths of p, q, r contacts (a path of k contacts passes through k - 1 rings of two contacts)"""
    edges, nxt, ends = [], 2, []
    for L in (p, q, r):
        prev, first = 0, len(edges)
        for _ in range(L - 1):
            edges.append((prev, nxt))
            prev, nxt = nxt, nxt + 1
        edges.append((prev, 1))
        ends.append((first, len(edges) - 1))
    rot = {}
    for e, (u, v) in enumerate(edges):
        for w in (u, v):
            rot.setdefault(w, []).append(e)
    (a1, b1), (a2, b2), (a3, b3) = ends
    rot[0] = [a1, a2, a3]
    rot[1] = [b1, b3, b2] if planar else [b1, b2, b3]
    return rot, edges


def figure_eight(r1, r2, order="separate"):
    """one hub ring shared by two loops of r1 and r2 rings (the hub counted in each)"""
    edges, nxt, ends = [], 1, []
    for L in (r1, r2):
        prev, first = 0, len(edges)
        for _ in range(L - 1):
            edges.append((prev, nxt))
            prev, nxt = nxt, nxt + 1
        edges.append((prev, 0))
        ends.append((first, len(edges) - 1))
    rot = {}
    for e, (u, v) in enumerate(edges):
        for w in (u, v):
            rot.setdefault(w, []).append(e)
    (x1, y1), (x2, y2) = ends
    rot[0] = {"separate": [x1, y1, x2, y2], "interleaved": [x1, x2, y1, y2]}[order]
    return rot, edges


# ---------- cell-level reading (rows of M^T, net_lib)
def step(rows, r):
    v = 0
    while r:
        low = r & -r
        v ^= rows[low.bit_length() - 1]
        r ^= low
    return v


def read_cells(sizes, contacts, H):
    """per contact: (first lag <= H at which a chain-end witness has coefficient 0, first lag <= H at which it misses a ring), None if never"""
    rings, Nb, blocks = N.layout(sizes, contacts)
    rows, _, _ = N.matrix(sizes, (60,) * len(sizes), contacts)
    out = []
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        wa, wb = rings[ra][pa - 1], rings[rb][pb - 1]
        ma, mb = N.mask(blocks, ra), N.mask(blocks, rb)
        row, lapse, miss = 1 << c, None, None
        for T in range(1, H + 1):
            row = step(rows, row)
            if lapse is None and not (row >> wa & 1 and row >> wb & 1):
                lapse = T
            if miss is None and not (row & ma and row & mb):
                miss = T
            if lapse is not None and miss is not None:
                break
        out.append((lapse, miss))
    return out
