"""Independent recomputation of the note's headline numbers, in code written separately from the repository's libraries.

It imports no repository module. It uses the standard library, numpy, sympy and networkx only. Each part recomputes one claim from
scratch and records whether it agrees with the number the note quotes.

    .venv/bin/python -B independent.py [--write]"""
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
OUT = {}


def part(name, ok, **detail):
    OUT[name] = {"ok": bool(ok), **detail}
    print(("ok  " if ok else "BAD ") + name, json.dumps(detail, default=str)[:300], flush=True)


def orbit_classes(k, rels):
    """classes of relations (frozensets of k-tuples) under flips and permutations of the k places"""
    cube = list(itertools.product((0, 1), repeat=k))
    def image(R, perm, f):
        return frozenset(tuple(s[perm[i]] ^ f[i] for i in range(k)) for s in R)
    seen, classes = set(), []
    for R in rels:
        if R in seen:
            continue
        orb = {image(R, perm, f) for perm in itertools.permutations(range(k)) for f in cube}
        seen |= orb
        classes.append(orb)
    return classes


def knots(k):
    cube = list(itertools.product((0, 1), repeat=k))
    out = []
    for m in range(1, (1 << len(cube)) - 1):
        R = frozenset(s for i, s in enumerate(cube) if m >> i & 1)
        if all(len({tuple(s[j] for j in range(k) if j != d) for s in R}) == 2 ** (k - 1) for d in range(k)):
            out.append(R)
    return out


# I1 three-place knots
k3 = knots(3)
c3 = orbit_classes(3, k3)
part("I1 three-place knots: 34 in 5 classes of sizes 2, 4, 8, 8, 12", len(k3) == 34 and sorted(len(c) for c in c3) == [2, 4, 8, 8, 12],
     knots=len(k3), class_sizes=sorted(len(c) for c in c3))

# I2 four-place knots
k4 = knots(4)
c4 = orbit_classes(4, k4)
vf = [c for c in c4 if all(frozenset(tuple(1 - x for x in s) for s in R) == R for R in c)]
part("I2 four-place knots: 742 in 20 classes; 30 value-free in 4 classes", len(k4) == 742 and len(c4) == 20 and len(vf) == 4
     and sum(len(c) for c in vf) == 30, knots=len(k4), classes=len(c4), value_free=sum(len(c) for c in vf))

FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def colourings(n):
    return ((np.arange(1 << n)[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)


# I3 the knot's coupling on Fano at the dimer point
C = colourings(7)
mono = sum(((C[:, list(L)].sum(1) % 3) == 0).astype(np.int64) for L in FANO)
M3 = int(sum(int(v) for v in ((-3) ** mono)))
M0 = int((mono == 0).sum())
pm = sum(1 for perm in itertools.permutations(range(7)) if all(perm[i] in FANO[i] for i in range(7)))
part("I3 knot's coupling on Fano: M(0) = 0 and M(-3) = (-2)^7 * #PM = -3072, #PM = 24", M0 == 0 and pm == 24 and M3 == (-2) ** 7 * 24 == -3072,
     M_minus3=M3, perfect_matchings=pm)

# I4 the theta identity on Fano at lam = 2
TH = []
for i, L in enumerate(FANO):
    u, v = 7 + 2 * i, 7 + 2 * i + 1
    TH += [(p, u, v) for p in L]
C21 = colourings(21)
odd = sum((C21[:, list(L)].sum(1) % 2).astype(np.int64) for L in TH)
left = sum(int(c) * 2 ** int(k) for k, c in zip(*np.unique(odd, return_counts=True)))
lp = Fraction(2) + Fraction(1, 2) - 1
nae_right = sum(lp ** int(m) for m in mono)
right = (2 * 2 * 3) ** 7 * nae_right
part("I4 theta identity: M_par(theta Fano; 2) = 10912465152 = (2*2*3)^7 * M_nae(Fano; 3/2)", left == right == 10912465152,
     left=left, right=str(right))

# I5 parity's count on Fano as a code weight enumerator
oddF = sum((C[:, list(L)].sum(1) % 2).astype(np.int64) for L in FANO)
ok5 = True
for lam in (Fraction(2), Fraction(3), Fraction(-2), Fraction(1, 3)):
    direct = sum(lam ** int(k) for k in oddF)
    formula = (1 + lam) ** 7 + 7 * (1 + lam) ** 3 * (1 - lam) ** 4
    ok5 &= direct == formula
part("I5 parity's count on Fano is (1+lam)^7 + 7 (1+lam)^3 (1-lam)^4, not proportional to (1+lam)^7 + (1-lam)^7", ok5)

# I6 signed not-all-equal never fails on the 5-point 4-regular system
L5 = [tuple(p for p in range(5) if p != j) for j in range(5)]
C5 = colourings(5)
fails = 0
for v in itertools.product(itertools.product((0, 1), repeat=4), repeat=5):
    ok = np.ones(len(C5), dtype=bool)
    for L, s in zip(L5, v):
        seen = C5[:, list(L)] ^ np.array(s)
        ok &= ~((seen.sum(1) == 0) | (seen.sum(1) == 4))
    fails += not ok.any()
part("I6 every signing of signed not-all-equal on the 5-point 4-regular system is solvable", fails == 0, signings=16 ** 5, failing=fails)

# I7 complementarity
ok7 = True
for k in (2, 3, 4):
    cube = list(itertools.product((0, 1), repeat=k))
    small = [R for R in knots(k) if len(R) == 2 ** (k - 1)]
    parity = {frozenset(s for s in cube if sum(s) % 2 == b) for b in (0, 1)}
    ok7 &= set(small) == parity
part("I7 complementarity: for k = 2, 3, 4 the knots with 2^(k-1) states are exactly the parity cosets", ok7)


# I8 the 13-point splice: its nontrivial 3-edge cut is knot against hub
def splice(H1, t, H2, m):
    M, out, j = H2[m], [], 0
    for l in H1:
        if t in l:
            out.append(tuple(("b", M[j]) if q == t else ("a", q) for q in l))
            j += 1
        else:
            out.append(tuple(("a", q) for q in l))
    out += [tuple(("b", q) for q in l) for i, l in enumerate(H2) if i != m]
    lab = {p: i for i, p in enumerate(sorted({p for l in out for p in l}))}
    return [tuple(lab[p] for p in l) for l in out]


S13 = splice(FANO, 0, FANO, 0)
g = nx.Graph()
g.add_edges_from((("l", i), ("p", p)) for i, L in enumerate(S13) for p in L)
cuts = []
for cut in itertools.combinations(list(g.edges()), 3):
    h = g.copy()
    h.remove_edges_from(cut)
    comps = list(nx.connected_components(h))
    if len(comps) == 2 and min(map(len, comps)) > 1:
        cuts.append((cut, comps))
ok8 = len(cuts) == 1
for cut, comps in cuts:
    X = next(c for c in comps if sum(1 if v[0] == "p" else -1 for v in c) == 1)
    Y = next(c for c in comps if c is not X)
    ports = [(u if u in X else w)[1] for u, w in cut]
    xp = sorted(v[1] for v in X if v[0] == "p")
    xl = [S13[v[1]] for v in X if v[0] == "l"]
    point_side = set()
    for c in itertools.product((0, 1), repeat=len(xp)):
        col = dict(zip(xp, c))
        if all(len({col[p] for p in L}) == 2 for L in xl):
            point_side.add(tuple(col[p] for p in ports))
    yp = sorted(v[1] for v in Y if v[0] == "p")
    slots = {}
    for j, (u, w) in enumerate(cut):
        s, p = (u, w) if u in Y else (w, u)
        slots[(s[1], p[1])] = j
    line_side = set()
    for c in itertools.product((0, 1), repeat=len(yp)):
        col = dict(zip(yp, c))
        for y in itertools.product((0, 1), repeat=3):
            good = True
            for v in Y:
                if v[0] != "l":
                    continue
                L = S13[v[1]]
                seen = [y[slots[(v[1], p)]] if (v[1], p) in slots else col[p] for p in L]
                if len(set(seen)) == 1:
                    good = False
                    break
            if good:
                line_side.add(y)
    ok8 &= point_side == {(0, 0, 0), (1, 1, 1)} and line_side == {y for y in itertools.product((0, 1), repeat=3) if len(set(y)) == 2}
part("I8 the 13-point splice has one nontrivial 3-edge cut; its point side accepts exactly equality and its line side exactly not-all-equal",
     ok8, cuts=len(cuts))

# I9 the eight-line parity piece's transfer matrix
PIECE = [(4, 2, 5), (4, 6, 2), (3, 2, 0), (7, 6, 1), (1, 7, 5), (3, 0, 5), (3, 0, 6), (4, 1, 7)]
SIGNS = [0, 0, 0, 1, 0, 0, 0, 0]
lam = sp.Symbol("lam")
G = sp.zeros(2, 2)
for c in itertools.product((0, 1), repeat=8):
    for x in (0, 1):
        k = 0
        for i, L in enumerate(PIECE):
            s = SIGNS[i] + sum(x if (i == 0 and p == 4) else c[p] for p in L)
            k += s % 2
        G[x, c[4]] += lam ** k
det = sp.factor(G.det())
part("I9 the eight-line parity piece has det G = -16 lam^2 (lam-1)^6 (lam+1)^6",
     sp.expand(G.det() + 16 * lam ** 2 * (lam - 1) ** 6 * (lam + 1) ** 6) == 0, det=str(det))

ok = all(v["ok"] for v in OUT.values())
OUT["ok"] = ok
if "--write" in sys.argv:
    (HERE / "independent_result.json").write_text(json.dumps(OUT, indent=1, default=str) + "\n")
print("ALL OK" if ok else "FAILURES")
sys.exit(0 if ok else 1)
