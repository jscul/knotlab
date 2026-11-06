"""Independent replay for the note 'Counting 2-colourings of 3-regular hypergraphs with Pfaffian incidence graphs'.

Written separately from the repository's libraries (none is imported): numpy, sympy and networkx only, with its own counter.

  I1 the soft crossing: two signed truncated-octahedron pages at a square; in the Hadamard basis the junction has straight entries
     (40000, -1112, 3336, -192) and zero turning entries; the snake multipliers (9/4) mu mu sigma_1 are (810000, 7506, -22518, -432)
  I2 the cube junction: N W = [[2,3,2,5],[8,4,8,9],[9,8,4,8],[5,2,3,2]], characteristic polynomial (x^2 - 19x - 1)(x^2 + 7x + 13)
  I3 K3,3 through plain braces: counts with 1..7 junctions, and #col(K3,3) = 6 from k = 1, 3, 5, 7 by the note's coefficients f
  I4 signs are path lengths: K3,3 with 2 and 5 negated incidences; capped paths; q(-1) = signed count, q(1) = 6
  I5 Theorem A on Fano compositions: #col(H - L)/2 = 5^(number of Fano blocks) by brute force; H itself not 2-colourable
  I6 the similitude, symbolically: MGI(W^) / MGI(F_R^) = c (a^2 + ab + b^2) for all 8 odd patterns and 4 internal leg signs of the split
     form, with one constant c; flipping a host leg sign flips the sign

Run: .venv/bin/python -B independent.py [--write]   (writes independent_result.json next to this file)"""
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
T0 = time.time()
OUT = {}


def nae(*v):
    return 0 if len(set(v)) == 1 else 1


# ------------------------------------------------------------------ a counter: lines as triples of (point, negated?) incidences
def count(lines):
    """number of colourings of the points making every line see its values (colour xor sign) not all equal; bucket elimination"""
    factors = []
    for inc in lines:
        vs = sorted({p for p, s in inc}, key=str)
        tab = {}
        for bits in itertools.product((0, 1), repeat=len(vs)):
            x = dict(zip(vs, bits))
            if nae(*[x[p] ^ s for p, s in inc]):
                tab[bits] = 1
        factors.append((vs, tab))
    points = {p for inc in lines for p, s in inc}
    while points:
        def width(p):
            return len({v for vs, t in factors if p in vs for v in vs})
        p = min(points, key=lambda q: (width(q), str(q)))
        inv = [f for f in factors if p in f[0]]
        rest = [f for f in factors if p not in f[0]]
        nv = sorted({v for vs, t in inv for v in vs} - {p}, key=str)
        tab = {}
        for bits in itertools.product((0, 1), repeat=len(nv)):
            x = dict(zip(nv, bits))
            tot = 0
            for b in (0, 1):
                x[p] = b
                pr = 1
                for vs, t in inv:
                    pr *= t.get(tuple(x[v] for v in vs), 0)
                    if not pr:
                        break
                tot += pr
            if tot:
                tab[bits] = tot
        factors = rest + [(nv, tab)]
        points.discard(p)
    out = 1
    for vs, t in factors:
        out *= t.get((), 0)
    return out


def from_graph(g, neg=frozenset()):
    """lines as incidence triples from a bipartite graph with nodes ('pt', ...) and ('ln', ...)"""
    return [[(p, 1 if frozenset((l, p)) in neg else 0) for p in sorted(g[l], key=str)] for l in g if l[0] == 'ln']


H2 = np.array([[1, 1], [1, -1]], dtype=object)


def hada(F):
    G = np.array(F, dtype=object)
    for ax in range(4):
        G = np.moveaxis(np.tensordot(H2, G, axes=([1], [ax])), 0, ax)
    return G


def mgi(f):
    return f[0, 0, 0, 0] * f[1, 1, 1, 1] - f[1, 1, 0, 0] * f[0, 0, 1, 1] + f[1, 0, 1, 0] * f[0, 1, 0, 1] - f[1, 0, 0, 1] * f[0, 1, 1, 0]


def junction(FQ, FR, s1=(0, 0, 0), s3=(0, 0, 0)):
    W = np.zeros((2, 2, 2, 2), dtype=object)
    for x0, z1, x2, z3, q1, q3, r1, r3 in itertools.product((0, 1), repeat=8):
        W[x0, z1, x2, z3] += FQ[x0, q1, x2, q3] * FR[x0, r1, x2, r3] * nae(z1 ^ s1[0], q1 ^ s1[1], r1 ^ s1[2]) * \
            nae(z3 ^ s3[0], q3 ^ s3[1], r3 ^ s3[2])
    return W


STRAIGHT = [(0, 0, 0, 0), (0, 1, 0, 1), (1, 0, 1, 0), (1, 1, 1, 1)]
TURNING = [(1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 1), (1, 0, 0, 1)]

# ------------------------------------------------------------------ I1 the soft crossing
K4 = nx.complete_graph(4)
ok_, emb = nx.check_planarity(K4)
TO = nx.Graph()
for u, v in emb.edges():                       # flags (vertex, edge, side) joined along the three reflections
    for s in (0, 1):
        w = emb[u][v]['cw'] if s == 0 else emb[u][v]['ccw']
        TO.add_edge((u, v, s), (u, w, 1 - s))
        TO.add_edge((u, v, s), (u, v, 1 - s))
        TO.add_edge((u, v, s), (v, u, 1 - s))
SQUARE = [(2, 0, 1), (2, 0, 0), (0, 2, 1), (0, 2, 0)]
SIGN_Q = {((1, 0, 0), (1, 0, 1)), ((1, 3, 0), (1, 3, 1)), ((1, 3, 0), (3, 1, 1)), ((2, 3, 0), (3, 2, 1))}
SIGN_R = {((1, 3, 0), (3, 1, 1)), ((2, 1, 0), (2, 1, 1)), ((3, 0, 0), (3, 0, 1)), ((3, 1, 0), (1, 3, 1)), ((3, 2, 0), (2, 3, 1)),
          ((3, 2, 0), (3, 2, 1))}


def page_tensor(g, sq, sign):
    """F(z0, z1, z2, z3): colourings of the page's own points making its own lines proper; z0, z2 the square points, z1, z3 the
    colours of the page neighbours of c1, c3; sign: (line, point) incidences negated"""
    col = nx.bipartite.color(g)
    pc = col[sq[0]]
    own_pts = [v for v in g if col[v] == pc and v not in sq]
    own_lns = [v for v in g if col[v] != pc and v not in sq]
    a1 = [w for w in g[sq[1]] if w not in sq][0]
    a3 = [w for w in g[sq[3]] if w not in sq][0]
    F = np.zeros((2, 2, 2, 2), dtype=object)
    for z0, z2 in itertools.product((0, 1), repeat=2):
        for bits in itertools.product((0, 1), repeat=len(own_pts)):
            x = dict(zip(own_pts, bits))
            x[sq[0]], x[sq[2]] = z0, z2
            if all(nae(*[x[p] ^ (1 if (l, p) in sign else 0) for p in g[l]]) for l in own_lns):
                F[z0, x[a1], z2, x[a3]] += 1
    return F


FQ = page_tensor(TO, SQUARE, SIGN_Q)
FR = page_tensor(TO, SQUARE, SIGN_R)
Wh = hada(junction(FQ, FR, (0, 0, 0), (0, 0, 1)))
sigma1 = [int(Wh[s]) for s in STRAIGHT]
mu = (3, -1)
lam = [Fraction(9, 4) * mu[a] * mu[b] * sigma1[i] for i, (a, b) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)])]
OUT["I1 soft crossing"] = {"straight entries": sigma1, "turning entries": [int(Wh[s]) for s in TURNING],
                           "snake multipliers": [int(v) for v in lam], "MGI": int(mgi(Wh)),
                           "ok": sigma1 == [40000, -1112, 3336, -192] and all(Wh[s] == 0 for s in TURNING) and
                           [int(v) for v in lam] == [810000, 7506, -22518, -432]}

# ------------------------------------------------------------------ I2 the cube junction
# cube vertices 0..7 as bit vectors; the square face with bit 2 = 0: c0 = 000 (a point), c1 = 001, c2 = 011, c3 = 010
F_cube = np.zeros((2, 2, 2, 2), dtype=object)
for z0, z1, z2, z3 in itertools.product((0, 1), repeat=4):
    F_cube[z0, z1, z2, z3] = nae(z0, z1, z3) * nae(z2, z1, z3)    # page points 101 (sees c1) and 110 (sees c3); lines 100, 111
Wc = junction(F_cube, F_cube)
ST = [(0, 0), (0, 1), (1, 0), (1, 1)]
Wm = sp.Matrix(4, 4, lambda i, j: Wc[ST[i][0], ST[i][1], ST[j][0], ST[j][1]])
Nm = sp.Matrix(4, 4, lambda i, j: nae(ST[i][0], ST[j][0], ST[j][1]) * (ST[i][1] == ST[j][1]))
S = Nm * Wm
x = sp.Symbol('x')
cp = sp.expand(S.charpoly(x).as_expr())
OUT["I2 cube junction"] = {"NW": S.tolist(), "characteristic polynomial": str(sp.factor(cp)),
                           "ok": S.tolist() == [[2, 3, 2, 5], [8, 4, 8, 9], [9, 8, 4, 8], [5, 2, 3, 2]] and
                           sp.expand(cp - (x ** 2 - 19 * x - 1) * (x ** 2 + 7 * x + 13)) == 0}

# ------------------------------------------------------------------ I3 K3,3 through plain braces


def k33_ladder(k):
    g = nx.Graph()
    P = [('pt', 'P', i) for i in range(3)]
    L = [('ln', 'L', j) for j in range(3)]
    for i in range(3):
        for j in range(3):
            if (i, j) not in ((0, 1), (2, 0)):              # E = (P0, L1) and F = (P2, L0) cross
                g.add_edge(P[i], L[j])
    ls, ps = ('ln', 's'), ('pt', 's')
    g.add_edge(P[2], ls)                                   # wire A from F's point end
    g.add_edge(L[1], ps)                                   # wire B from E's line end
    g.add_edge(ls, ps)
    prevA, prevB = ls, ps
    for j in range(k):
        c0, c1, c2, c3 = ('pt', 'c0', j), ('ln', 'c1', j), ('pt', 'c2', j), ('ln', 'c3', j)
        for side in ('Q', 'R'):                            # a plain cube on the square: lines 100, 111; points 101, 110
            l100, l111, p101, p110 = ('ln', side, j, 100), ('ln', side, j, 111), ('pt', side, j, 101), ('pt', side, j, 110)
            g.add_edges_from([(c0, l100), (c2, l111), (c1, p101), (c3, p110), (l100, p101), (l100, p110), (l111, p101), (l111, p110)])
        g.add_edge(c0, prevA)
        g.add_edge(prevB, c1)
        if j < k - 1:
            lam_, pi_ = ('ln', 'lam', j), ('pt', 'pi', j)
            g.add_edges_from([(c2, lam_), (pi_, c3), (pi_, lam_)])
            prevA, prevB = lam_, pi_
        else:
            g.add_edge(c2, L[0])
            g.add_edge(P[0], c3)
    assert all(d == 3 for _, d in g.degree())
    return g


Z = {k: count(from_graph(k33_ladder(k))) for k in range(1, 8)}
f = [Fraction(-53451621, 2804438), Fraction(521319, 200317), Fraction(-23524, 200317), Fraction(853, 2804438)]
rec = sum(f[j] * Z[2 * j + 1] for j in range(4))
k33 = nx.complete_bipartite_graph(3, 3)
k33 = nx.relabel_nodes(k33, {v: ('pt', v) if v < 3 else ('ln', v) for v in k33})
OUT["I3 K3,3 through plain braces"] = {"counts": Z, "recovered": str(rec), "#col(K3,3)": count(from_graph(k33)),
                                      "vertices": {k: k33_ladder(k).number_of_nodes() for k in (1, 3, 5, 7)},
                                      "ok": [Z[k] for k in (1, 3, 5, 7)] == [80, 31500, 11459396, 4159886188] and rec == 6}

# ------------------------------------------------------------------ I4 signs are path lengths


def capped_path(g, p, l, k, tag):
    """p - l1 - p1 - ... - lk - pk - l, each pair (li, pi) closed by a cube minus the edge 000-100"""
    prev = p
    for t in range(k):
        li, pi = ('ln', 'E', tag, t), ('pt', 'E', tag, t)
        g.add_edge(prev, li)
        g.add_edge(li, pi)
        cube = {v: (('pt' if bin(v).count('1') % 2 == 0 else 'ln'), 'cap', tag, t, v) for v in range(8)}
        for a in range(8):
            for bit in (1, 2, 4):
                b = a ^ bit
                if a < b and {a, b} != {0, 4}:
                    g.add_edge(cube[a], cube[b])
        g.add_edge(cube[0], li)            # the cap's point 000 on the line
        g.add_edge(cube[4], pi)            # the cap's line 100 on the point
        prev = pi
    g.add_edge(prev, l)


def signed_k33(mask):
    neg = {(i, j) for i in range(3) for j in range(3) if mask >> (3 * i + j) & 1}
    return neg


I4 = {}
ok4 = True
for name, mask in (("two negations", 0b000010001), ("five negations", 0b101100110)):
    neg = signed_k33(mask)
    g0 = nx.Graph()
    negset = set()
    for i in range(3):
        for j in range(3):
            g0.add_edge(('pt', i), ('ln', j))
            if (i, j) in neg:
                negset.add(frozenset((('pt', i), ('ln', j))))
    signed = count(from_graph(g0, frozenset(negset)))
    Lneg = len(neg)
    counts = {}
    for k in range(1, Lneg + 2):
        g = nx.Graph()
        for i in range(3):
            for j in range(3):
                if (i, j) in neg:
                    capped_path(g, ('pt', i), ('ln', j), k, (i, j))
                else:
                    g.add_edge(('pt', i), ('ln', j))
        counts[k] = count(from_graph(g))
    tvals = [sp.Rational(-1, 3) ** k for k in range(1, Lneg + 2)]
    A = sp.Matrix([[tv ** j for j in range(Lneg + 1)] for tv in tvals])
    b = sp.Matrix([sp.Rational(counts[k], 9 ** (k * Lneg)) for k in range(1, Lneg + 2)])
    q = A.LUsolve(b)
    qm1 = sum(q[j] * (-1) ** j for j in range(Lneg + 1))
    qp1 = sum(q)
    I4[name] = {"negated incidences": Lneg, "signed count": signed, "q(-1)": str(qm1), "q(1)": str(qp1)}
    ok4 &= qm1 == signed and qp1 == 6
I4["ok"] = ok4
OUT["I4 signs are path lengths"] = I4

# ------------------------------------------------------------------ I5 Theorem A on Fano compositions
FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def point_block(H, p):
    """replace point p by a Fano plane minus the line (0, 1, 2), its points 0, 1, 2 taking p's three places"""
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
    """replace line i by a Fano plane minus the point 0: the three lines through 0 take line i's three points, one each"""
    l = H[i]
    through0 = [fl for fl in FANO if 0 in fl]
    out = [H[j] for j in range(len(H)) if j != i]
    for slot, fl in zip(l, through0):
        out.append(tuple(('d', i, q) for q in fl if q != 0) + (slot,))
    out += [tuple(('d', i, q) for q in fl) for fl in FANO if 0 not in fl]
    return out


def brute(H, drop=None):
    pts = sorted({q for l in H for q in l}, key=str)
    idx = {q: i for i, q in enumerate(pts)}
    X = ((np.arange(2 ** len(pts))[:, None] >> np.arange(len(pts))[None, :]) & 1).astype(np.int8)
    good = np.ones(len(X), dtype=bool)
    for j, l in enumerate(H):
        if j == drop:
            continue
        c = X[:, [idx[q] for q in l]]
        good &= ~((c == 0).all(axis=1) | (c == 1).all(axis=1))
    return int(good.sum()), len(pts)


CASES = {"Fano": (FANO, 1), "a point block": (point_block(FANO, 0), 2), "a line block": (line_block(FANO, 0), 2),
         "two point blocks": (point_block(point_block(FANO, 0), 1), 3), "a point and a line block": (line_block(point_block(FANO, 0), 3), 3)}
I5, ok5 = {}, True
for name, (H, blocks) in CASES.items():
    full, n = brute(H)
    minus, _ = brute(H, drop=0)
    I5[name] = {"points": n, "colourings": full, "colourings minus a line, halved": minus // 2, "5^blocks": 5 ** blocks}
    ok5 &= full == 0 and minus == 2 * 5 ** blocks
I5["ok"] = ok5
OUT["I5 Theorem A on Fano compositions"] = I5

# ------------------------------------------------------------------ I6 the similitude, symbolically
a, b = sp.symbols('alpha beta')
r = {y: sp.Symbol('r' + ''.join(map(str, y))) for y in itertools.product((0, 1), repeat=4) if sum(y) % 2 == 0}
Rhat = np.zeros((2, 2, 2, 2), dtype=object)
for y, s_ in r.items():
    Rhat[y] = s_
FRs = hada(Rhat) / 16                                       # H^-1 = H / 2 on each leg


def split_form(t10, t12, t30, t32, s1, s3):
    F = np.zeros((2, 2, 2, 2), dtype=object)
    for x0, z1, x2, z3 in itertools.product((0, 1), repeat=4):
        v1, v3 = z1 ^ s1, z3 ^ s3
        if x0 ^ t10 == x2 ^ t12:
            F[x0, z1, x2, z3] = int(v1 == x0 ^ t10) * (a * int(v3 == x0 ^ t30) + b * int(v3 == x2 ^ t32))
        else:
            F[x0, z1, x2, z3] = int(v3 == x0 ^ t30) * (b * int(v1 == x0 ^ t10) + a * int(v1 == x2 ^ t12))
    return F


base = sp.expand(mgi(Rhat))
consts, ok6 = set(), True
for tau in itertools.product((0, 1), repeat=4):
    if sum(tau) % 2 == 0:
        continue
    for s1, s3 in itertools.product((0, 1), repeat=2):
        Wsym = junction(split_form(*tau, s1, s3), FRs)
        ratio = sp.factor(sp.expand(mgi(hada(Wsym))) / base)
        c = sp.simplify(ratio / (a ** 2 + a * b + b ** 2))
        ok6 &= c.free_symbols == set()
        consts.add(c)
flip = sp.factor(sp.expand(mgi(hada(junction(split_form(0, 0, 0, 1, 0, 0), FRs, (1, 0, 0), (0, 0, 0))))) / base) / (a ** 2 + a * b + b ** 2)
OUT["I6 similitude"] = {"constants over 32 cases": sorted(map(str, consts)), "host leg sign flipped": str(sp.simplify(flip)),
                        "ok": ok6 and len(consts) == 1 and sp.simplify(flip + next(iter(consts))) == 0}

OUT["ok"] = all(v["ok"] for k, v in OUT.items() if isinstance(v, dict))
OUT["seconds"] = round(time.time() - T0, 1)
for k, v in OUT.items():
    print(k, json.dumps(v, default=str)[:600])
print("ALL OK" if OUT["ok"] else "FAILURES", OUT["seconds"], "s")
if "--write" in sys.argv:
    (HERE / "independent_result.json").write_text(json.dumps(OUT, indent=1, default=str) + "\n")
sys.exit(0 if OUT["ok"] else 1)
