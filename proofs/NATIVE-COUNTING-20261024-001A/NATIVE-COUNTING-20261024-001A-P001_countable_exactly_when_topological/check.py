#!/usr/bin/env python3
"""Check of NATIVE-COUNTING-20261024-001A-P001 (standard library only, seed 20261024).

Checks:
- Theorem 1: for every symmetric signature [f0, f1, f2, f3] with entries in {-2, ..., 2}, two copies glued along one edge give a
  four-leg function symmetric in its legs exactly when f0 f2 + f1 f3 = f1^2 + f2^2, exactly when it is a generalized Fibonacci gate
  (f2 = m f1 + f0 and f3 = m f2 + f1 for some m) or of the form [a, 0, 0, b]; among the 34 knots this holds for exactly the four
  topological knots;
- Theorem 2: each topological knot is lambda_0 v_0^3 + lambda_1 v_1^3 with v_0, v_1 orthonormal, and on random connected native networks
  with pinned and unpinned legs the brute-force count equals sum_j lambda_j^n prod_legs <v_j, leg> (unpinned leg: (1, 1)); with every
  leg pinned this is 2^g times a parity test for the parity knots, and D^(2g-2) (phi^t + (-1)^t phi^(2-2g-t)) for the Fibonacci knot,
  evaluated exactly in Q(sqrt 5);
- Theorem 3: membership of every knot in the tractable families of Backens's Holant^c dichotomy (products of unary and binary
  functions; generalized equalities after an orthogonal or the K transformation; weight-at-most-one functions after K or KX; affine
  functions after a matrix S taking the equality and the pins to affine functions; local affine functions). Exactly the four
  topological knots belong to some family.
Controls: each family test accepts a constructed member (a product, a rotated generalized equality, K applied to a generalized equality,
K applied to a weight-at-most-one function, a transformed affine function, a point mass) and rejects a random complex tensor; a wrong
count formula (lambda_j^(n+1)) disagrees with the brute-force counts.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import cmath
import itertools
import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- membership in the tractable families

CUBE = list(itertools.product((0, 1), repeat=3))
TOL = 1e-9

def knots():
    out = []
    for m in range(256):
        R = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out

def vec(R):
    return {x: (1.0 if x in R else 0.0) for x in CUBE}

def transform(f, A):
    """(A^{tensor 3}) f for a 2x2 matrix A (list of rows), f dict over CUBE"""
    g = {}
    for y in CUBE:
        s = 0
        for x in CUBE:
            if f[x] != 0:
                s += A[y[0]][x[0]] * A[y[1]][x[1]] * A[y[2]][x[2]] * f[x]
        g[y] = s
    return g

def inv2(A):
    a, b = A[0]; c, d = A[1]
    det = a * d - b * c
    return [[d / det, -b / det], [-c / det, a / det]]

def factorizable(f):
    """f is a tensor product across some bipartition {i} | {j, k}"""
    for i in range(3):
        # matrix M[v][(others)] = f with variable i = v
        M = [[0j] * 4 for _ in range(2)]
        for x in CUBE:
            others = tuple(x[p] for p in range(3) if p != i)
            M[x[i]][others[0] * 2 + others[1]] = f[x]
        r = all(abs(M[0][a] * M[1][b] - M[0][b] * M[1][a]) < TOL for a in range(4) for b in range(4))
        if r:
            return True
    return False

def mode_directions(f, mode):
    """factor directions in `mode` of a GHZ-type tensor: perps of the roots of det(f contracted with phi) = 0. Returns list of 2 vectors or None"""
    # f(phi) = phi0 * F0 + phi1 * F1, Fv = slice with x[mode] = v (2x2 over the other two modes)
    F = []
    for v in (0, 1):
        M = [[0j, 0j], [0j, 0j]]
        for x in CUBE:
            if x[mode] == v:
                o = [x[p] for p in range(3) if p != mode]
                M[o[0]][o[1]] = f[x]
        F.append(M)
    def det(M): return M[0][0] * M[1][1] - M[0][1] * M[1][0]
    # det(p F0 + q F1) = a p^2 + b p q + c q^2
    a = det(F[0]); c = det(F[1])
    b = det([[F[0][i][j] + F[1][i][j] for j in range(2)] for i in range(2)]) - a - c
    if abs(a) < TOL and abs(b) < TOL and abs(c) < TOL:
        return None
    disc = b * b - 4 * a * c
    if abs(disc) < TOL:
        return None                     # repeated root: not GHZ type
    roots = []                          # roots as (p, q)
    if abs(a) > TOL:
        s = cmath.sqrt(disc)
        roots = [((-b + s) / (2 * a), 1), ((-b - s) / (2 * a), 1)]
    else:
        # a = 0: q (b p + c q) = 0 -> q = 0 (p = 1) or p = -c/b
        roots = [(1, 0), (-c / b, 1)]
    # direction a with phi . a = 0 for phi = (p, q): a = (q, -p)
    return [(q, -p) for p, q in roots]

def same_line(u, w):
    return abs(u[0] * w[1] - u[1] * w[0]) < 1e-7 * max(1, abs(u[0]) + abs(u[1])) * max(1, abs(w[0]) + abs(w[1]))

def ghz_pair(f):
    """common unordered pair of factor directions across the three modes, or None"""
    dirs = [mode_directions(f, m) for m in range(3)]
    if any(d is None for d in dirs):
        return None
    u, w = dirs[0]
    for d in dirs[1:]:
        if not ((same_line(d[0], u) and same_line(d[1], w)) or (same_line(d[0], w) and same_line(d[1], u))):
            return None
    return u, w

def bil(u, w): return u[0] * w[0] + u[1] * w[1]

def in_OE(f):
    p = ghz_pair(f)
    if p is None: return False
    u, w = p
    return abs(bil(u, w)) < 1e-7 and abs(bil(u, u)) > 1e-7 and abs(bil(w, w)) > 1e-7

def in_KE(f):
    p = ghz_pair(f)
    if p is None: return False
    u, w = p
    iso = [(1, 1j), (1, -1j)]
    return ((same_line(u, iso[0]) and same_line(w, iso[1])) or (same_line(u, iso[1]) and same_line(w, iso[0])))

K = [[1, 1], [1j, -1j]]
X = [[0, 1], [1, 0]]
def matmul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]

def in_KM(f):
    for A in (K, matmul(K, X)):
        g = transform(f, inv2(A))
        if all(abs(g[x]) < TOL for x in CUBE if sum(x) >= 2):
            return True
    return False

# affine test
def affine_subspaces():
    subs = set()
    for k in range(4):
        for basis in itertools.combinations([x for x in CUBE if any(x)], k):
            span = {(0, 0, 0)}
            for b in basis:
                span |= {tuple((a + c) % 2 for a, c in zip(s, b)) for s in span}
            if len(span) != 2 ** k: continue
            for off in CUBE:
                subs.add(frozenset(tuple((a + c) % 2 for a, c in zip(s, off)) for s in span))
    return subs
AFF = affine_subspaces()
QUAD = []
for coef in itertools.product((0, 1), repeat=6):
    QUAD.append(coef)
def qval(coef, x):
    a1, a2, a3, b12, b13, b23 = coef
    return (a1 * x[0] + a2 * x[1] + a3 * x[2] + b12 * x[0] * x[1] + b13 * x[0] * x[2] + b23 * x[1] * x[2]) % 2
LIN = list(itertools.product((0, 1), repeat=4))   # l(x) = c0 + c.x mod 2
def is_affine(g):
    supp = frozenset(x for x in CUBE if abs(g[x]) > 1e-7)
    if not supp: return True
    if supp not in AFF: return False
    x0 = min(supp)
    c = g[x0]
    for lc in LIN:
        for qc in QUAD:
            ok = True
            base = (1j ** ((lc[0] + sum(a * b for a, b in zip(lc[1:], x0))) % 2)) * ((-1) ** qval(qc, x0))
            for x in supp:
                val = (1j ** ((lc[0] + sum(a * b for a, b in zip(lc[1:], x))) % 2)) * ((-1) ** qval(qc, x))
                if abs(g[x] * base - c * val) > 1e-7:
                    ok = False; break
            if ok: return True
    return False

UNARY_AFF = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 1j), (1, -1j)]
AFF_BIN = []
for y in itertools.product([0, 1, -1, 1j, -1j], repeat=3):
    if any(v != 0 for v in y):
        AFF_BIN.append(y)
def binary_affine(y00, y01, y11):
    g = {}
    # embed as ternary-free check: build a 2-variable affine test by brute force
    vals = {(0, 0): y00, (0, 1): y01, (1, 0): y01, (1, 1): y11}
    supp = [k for k, v in vals.items() if abs(v) > 1e-7]
    if not supp: return True
    ref = vals[supp[0]]
    ratios = [vals[k] / ref for k in supp]
    if any(min(abs(r - t) for t in (1, -1, 1j, -1j)) > 1e-7 for r in ratios): return False
    # support affine in F2^2: sizes 1, 2 (any pair is affine), 4
    if len(supp) == 3: return False
    # full support: values c * i^{l} (-1)^{q}: always representable for symmetric 2x2 with ratios in {+-1, +-i}? check quadratic consistency
    if len(supp) == 4:
        for lc in itertools.product((0, 1), repeat=3):
            for qc in itertools.product((0, 1), repeat=3):
                ok = True
                for k in vals:
                    l = (lc[0] + lc[1] * k[0] + lc[2] * k[1]) % 2
                    q = (qc[0] * k[0] + qc[1] * k[1] + qc[2] * k[0] * k[1]) % 2
                    l0 = lc[0] % 2
                    if abs(vals[k] / ref - (1j ** l) * ((-1) ** q) / (1j ** l0)) > 1e-7:
                        ok = False; break
                if ok: return True
        return False
    return True

def S_candidates():
    out = []
    for r1 in UNARY_AFF:
        for r2 in UNARY_AFF:
            if abs(r1[0] * r2[1] - r1[1] * r2[0]) < 1e-9: continue
            # S^T S = r1^T r1 + beta2 * r2^T r2 must be affine: solve for beta2 against each affine binary pattern
            A0 = [r1[0] * r1[0], r1[0] * r1[1], r1[1] * r1[1]]
            B0 = [r2[0] * r2[0], r2[0] * r2[1], r2[1] * r2[1]]
            for y in AFF_BIN:
                # find beta2, c with A0 + beta2 B0 = c y
                sols = set()
                for (i, j) in ((0, 1), (0, 2), (1, 2)):
                    # 2x2 system in (beta2, c): B0[i] beta2 - y[i] c = -A0[i]; same for j
                    det = B0[i] * (-y[j]) - B0[j] * (-y[i])
                    if abs(det) < 1e-12: continue
                    beta2 = ((-A0[i]) * (-y[j]) - (-A0[j]) * (-y[i])) / det
                    c = (B0[i] * (-A0[j]) - B0[j] * (-A0[i])) / det
                    if abs(c) < 1e-12 or abs(beta2) < 1e-12: continue
                    if all(abs(A0[k] + beta2 * B0[k] - c * y[k]) < 1e-9 for k in range(3)):
                        sols.add((round(beta2.real, 9) if isinstance(beta2, complex) else round(beta2, 9),
                                  round(beta2.imag, 9) if isinstance(beta2, complex) else 0.0))
                for br, bi in sols:
                    beta = cmath.sqrt(complex(br, bi))
                    for b in (beta, -beta):
                        S = [[r1[0], r1[1]], [b * r2[0], b * r2[1]]]
                        out.append(S)
    return out
SC = S_candidates()

def in_SA(f):
    for S in SC:
        g = transform(f, inv2(S))
        if is_affine(g):
            return True
    return False

def in_L(f):
    supp = frozenset(x for x in CUBE if abs(f[x]) > 1e-9)
    if supp not in AFF: return False
    T = cmath.exp(1j * cmath.pi / 4)
    for x in supp:
        g = {y: f[y] * (T ** sum(a * b for a, b in zip(x, y))) for y in CUBE}
        if not is_affine(g): return False
    return True


# ---------------------------------------------------------------- Theorem 1: the gluing criterion
def glued_symmetric(f):
    """g(a,b,c,d) = sum_e f(a,b,e) f(e,c,d) for symmetric f given by weights f[k]; symmetric under all leg permutations?"""
    def F(x): return f[sum(x)]
    g = {x: sum(F((x[0], x[1], e)) * F((e, x[2], x[3])) for e in (0, 1)) for x in itertools.product((0, 1), repeat=4)}
    return all(g[x] == g[tuple(x[p] for p in perm)] for x in g for perm in itertools.permutations(range(4)))


def fibonacci_gate(f):
    f0, f1, f2, f3 = f
    if f1 != 0:
        m = Fraction(f2 - f0, f1)
        return f3 == m * f2 + f1
    # f1 = 0: f2 = f0 required, then f3 = m f2 for some m (any m if f2 = 0 and f3 = 0)
    if f2 != f0:
        return False
    return f2 != 0 or f3 == 0


def criterion_checks():
    grid = list(itertools.product(range(-2, 3), repeat=4))
    agree_eq = agree_fib = 0
    for f in grid:
        sym = glued_symmetric(f)
        eq = f[0] * f[2] + f[1] * f[3] == f[1] ** 2 + f[2] ** 2
        fib_or_eq = fibonacci_gate(f) or (f[1] == 0 and f[2] == 0)
        agree_eq += sym == eq
        agree_fib += sym == fib_or_eq
    topo = []
    for R in knots():
        sym = all(tuple(t[p] for p in perm) in R for t in R for perm in itertools.permutations(range(3)))
        if not sym:
            continue
        f = [int(any(sum(t) == k for t in R)) for k in range(4)]
        if glued_symmetric(f):
            topo.append(f)
    return {"symmetric signatures tested": len(grid), "four-leg symmetry agrees with the equation": agree_eq,
            "agrees with Fibonacci gate or [a, 0, 0, b]": agree_fib,
            "knots satisfying it (allowed numbers of ones)": sorted([k for k in range(4) if f[k]] for f in topo)}


# ---------------------------------------------------------------- Theorem 2: decompositions and count formulas
PHI = (1 + 5 ** 0.5) / 2
DD = math.sqrt(2 + PHI)          # D, with D^2 = 1 + phi^2 = 2 + phi
SMAT = [[1 / DD, PHI / DD], [PHI / DD, -1 / DD]]


def decomposition(weights):
    """(lambdas, vectors) with f = sum_j lambda_j v_j^3 for the four topological knots, keyed by allowed numbers of ones"""
    s = 1 / math.sqrt(2)
    if weights == [0, 2]:
        return [math.sqrt(2), math.sqrt(2)], [(s, s), (s, -s)]
    if weights == [1, 3]:
        return [math.sqrt(2), -math.sqrt(2)], [(s, s), (s, -s)]
    if weights == [0, 2, 3]:
        return [1 / SMAT[0][j] for j in range(2)], [(SMAT[0][j], SMAT[1][j]) for j in range(2)]
    if weights == [0, 1, 3]:
        return [1 / SMAT[0][j] for j in range(2)], [(SMAT[1][j], SMAT[0][j]) for j in range(2)]
    raise ValueError(weights)


def decomposition_ok(weights):
    lam, vs = decomposition(weights)
    R = {x for x in CUBE if sum(x) in weights}
    ortho = all(abs(sum(a * b for a, b in zip(vs[i], vs[j])) - (i == j)) < 1e-12 for i in range(2) for j in range(2))
    exact = all(abs(sum(l * v[x[0]] * v[x[1]] * v[x[2]] for l, v in zip(lam, vs)) - (x in R)) < 1e-12 for x in CUBE)
    return ortho and exact


def random_network(rng, n, L, free_prob):
    while True:
        slots = [(v, p) for v in range(n) for p in range(3)]
        rng.shuffle(slots)
        legs, rest = slots[:L], slots[L:]
        pairs = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for a, b in pairs:
            parent[find(a[0])] = find(b[0])
        if len({find(v) for v in range(n)}) != 1:
            continue
        var, nv = {}, 0
        for a, b in pairs:
            var[a] = var[b] = nv
            nv += 1
        leg_vals = []
        for s in legs:
            var[s] = ("leg", len(leg_vals))
            leg_vals.append(None if rng.random() < free_prob else rng.randint(0, 1))
        return [tuple(var[(v, p)] for p in range(3)) for v in range(n)], nv, leg_vals


def brute_count(R, scopes, nv, leg_vals):
    free = [i for i, x in enumerate(leg_vals) if x is None]
    total = 0
    for fb in itertools.product((0, 1), repeat=len(free)):
        lv = list(leg_vals)
        for i, b in zip(free, fb):
            lv[i] = b
        for bits in range(1 << nv):
            ok = True
            for sc in scopes:
                t = tuple(lv[v[1]] if isinstance(v, tuple) else (bits >> v & 1) for v in sc)
                if t not in R:
                    ok = False
                    break
            total += ok
    return total


def formula_count(weights, n, leg_vals, power_shift=0):
    lam, vs = decomposition(weights)
    tot = 0.0
    for l, v in zip(lam, vs):
        term = l ** (n + power_shift)
        for x in leg_vals:
            term *= (v[0] + v[1]) if x is None else v[x]
        tot += term
    return tot


class Q5:
    def __init__(self, a, b=0):
        self.a, self.b = Fraction(a), Fraction(b)

    def __add__(self, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(self.a + o.a, self.b + o.b)

    def __mul__(self, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(self.a * o.a + 5 * self.b * o.b, self.a * o.b + self.b * o.a)

    def inv(self):
        nrm = self.a * self.a - 5 * self.b * self.b
        return Q5(self.a / nrm, -self.b / nrm)

    def __pow__(self, k):
        base, out = (self if k >= 0 else self.inv()), Q5(1)
        for _ in range(abs(k)):
            out = out * base
        return out


def fibonacci_exact(g, t):
    """D^(2g-2) (phi^t + (-1)^t phi^(2-2g-t)) in Q(sqrt 5); returns an integer if the value is one"""
    phi = Q5(Fraction(1, 2), Fraction(1, 2))
    d2 = Q5(Fraction(5, 2), Fraction(1, 2))
    val = (d2 ** (g - 1)) * ((phi ** t) + (phi ** (2 - 2 * g - t)) * Q5((-1) ** t))
    assert val.b == 0 and val.a.denominator == 1, (g, t, val.a, val.b)
    return int(val.a)


def counting_checks(rng):
    out = {"decompositions with orthonormal vectors": {}, "networks": 0, "formula agrees": 0, "closed-form agrees": 0,
           "wrong power disagrees somewhere": False}
    for w in ([0, 2], [1, 3], [0, 2, 3], [0, 1, 3]):
        out["decompositions with orthonormal vectors"][str(w)] = decomposition_ok(w)
    for _ in range(400):
        w = rng.choice([[0, 2], [1, 3], [0, 2, 3], [0, 1, 3]])
        R = {x for x in CUBE if sum(x) in w}
        n = rng.randint(1, 7)
        L = rng.randint(0, n + 2)
        if (3 * n - L) % 2:
            L += 1
        if L > 3 * n or (n == 1 and L == 1):
            continue
        scopes, nv, leg_vals = random_network(rng, n, L, free_prob=rng.choice([0.0, 0.3]))
        if nv > 13:
            continue
        c = brute_count(R, scopes, nv, leg_vals)
        out["networks"] += 1
        out["formula agrees"] += abs(formula_count(w, n, leg_vals) - c) < 1e-6 * max(1, c)
        out["wrong power disagrees somewhere"] |= abs(formula_count(w, n, leg_vals, power_shift=1) - c) > 1e-6 * max(1, c)
        if all(x is not None for x in leg_vals):
            g = (n - L) // 2 + 1
            if w == [0, 2]:
                cf = 2 ** g * (sum(leg_vals) % 2 == 0)
            elif w == [1, 3]:
                cf = 2 ** g * (sum(leg_vals) % 2 == n % 2)
            elif w == [0, 2, 3]:
                cf = fibonacci_exact(g, sum(leg_vals))
            else:
                cf = fibonacci_exact(g, L - sum(leg_vals))
            out["closed-form agrees"] += cf == c
        else:
            out["closed-form agrees"] += 1
    return out


# ---------------------------------------------------------------- Theorem 3: the families
def family_row(f):
    return {"product of unary and binary": factorizable(f), "orthogonal generalized equality": in_OE(f),
            "K generalized equality": in_KE(f), "K weight at most one": in_KM(f), "S affine": in_SA(f), "local affine": in_L(f)}


def family_checks():
    rows = []
    for R in knots():
        fam = family_row(vec(R))
        rows.append((sorted("".join(map(str, t)) for t in CUBE if t not in R), fam))
    tract = [(z, [k for k, v in fam.items() if v]) for z, fam in rows if any(fam.values())]
    return {"knots": len(rows), "knots in some family": len(tract), "those knots (excluded tuples, families)": tract,
            "knots in no family": len(rows) - len(tract)}


def family_controls(rng):
    th = 0.7
    O = [[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]
    ghz = {x: (1.0 if x in ((0, 0, 0), (1, 1, 1)) else 0.0) for x in CUBE}
    ghz2 = {x: (1.0 if x == (0, 0, 0) else (2.0 if x == (1, 1, 1) else 0.0)) for x in CUBE}
    wmass = {x: ({(0, 0, 0): 1.0, (1, 0, 0): 2.0, (0, 1, 0): 1.0, (0, 0, 1): 3.0}.get(x, 0.0)) for x in CUBE}
    prod = {x: (1.0 if x[1] == x[2] else 0.0) * (2.0 if x[0] else 1.0) for x in CUBE}
    parity = {x: float(sum(x) % 2 == 0) for x in CUBE}
    S = SC[len(SC) // 2]
    point = {x: float(x == (0, 1, 1)) for x in CUBE}
    rand = {x: complex(rng.gauss(0, 1), rng.gauss(0, 1)) for x in CUBE}
    return {
        "a product is accepted": factorizable(prod),
        "a rotated generalized equality is accepted": in_OE(transform(ghz2, O)),
        "K applied to a generalized equality is accepted": in_KE(transform(ghz, K)),
        "K applied to a weight-at-most-one function is accepted": in_KM(transform(wmass, K)),
        "a transformed affine function is accepted": in_SA(transform(parity, S)),
        "a point mass is local affine": in_L(point),
        "a random complex tensor is rejected by every test": not any(family_row(rand).values()),
    }


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    crit = criterion_checks()
    count = counting_checks(rng)
    fams = family_checks()
    ctl = family_controls(rng)
    ctl["a wrong count formula disagrees with brute force"] = count.pop("wrong power disagrees somewhere")
    topo = [[0, 2], [0, 1, 3], [0, 2, 3], [1, 3]]
    ok = (crit["four-leg symmetry agrees with the equation"] == crit["symmetric signatures tested"]
          and crit["agrees with Fibonacci gate or [a, 0, 0, b]"] == crit["symmetric signatures tested"]
          and crit["knots satisfying it (allowed numbers of ones)"] == sorted(topo)
          and all(count["decompositions with orthonormal vectors"].values())
          and count["formula agrees"] == count["closed-form agrees"] == count["networks"] > 0
          and fams["knots in some family"] == 4 and fams["knots in no family"] == 30
          and sorted(sorted(z) for z, _ in fams["those knots (excluded tuples, families)"]) == sorted(
              [sorted("".join(map(str, t)) for t in CUBE if sum(t) not in w) for w in topo])
          and all(ctl.values()))
    result["checks"] = {"gluing criterion": crit, "count formulas": count, "tractable families": fams}
    result["controls"] = ctl
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": ctl}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
