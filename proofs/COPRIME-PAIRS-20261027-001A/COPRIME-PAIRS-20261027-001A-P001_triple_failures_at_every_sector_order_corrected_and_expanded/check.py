"""Checks for COPRIME-PAIRS-20261027-001A-P001 (successor of COPRIME-DICHOTOMY-20261027-001C-P001).

  1 Lemma 3.0: the literal Fox closure rows (computed from relator values) equal t^-1 (Bur_t - I) on random braids
  2 Lemma 3.1 and the reversed Artin identity (replay): Squier invariance, J_t^T 1, bundle identity; reversed product = 1
  3 Lemma 4.0: parity and balanced triple shapes on pair quotients; on knot models the odd layer-2 residuals vanish
    identically, the pinned trivial-character cocycles are zero, and the odd layer-4 residuals do not depend on the odd
    layer-3 cocycles (even ones do: control)
  4 Lemma 4.3: Bur_t(delta_k) on F^k/1 has characteristic polynomial sum_(i<k) t^(i-k+1) x^i; Fix Bur_t(C_k) is exactly the
    bundle constants at t^k = -1 and the constants elsewhere; the integer-exponent map exp(c(g)A) theta'^u(g) satisfies the
    T(2,13) relators with theta' of order 6 (d = 12, k = 2) and kills the longitude; every datum lifts on C_k (eight (p, d, k))
  5 Lemma 4.4 inputs (replay): Alexander polynomial and amphichirality of b(4m^2+1, 2m)
  6 Lemma 6.1: two-partition lemma (exhaustive, n <= 6); cables: first and last strands separated at every root character;
    amphichiral braids and random conjugates: the over-strand conjugation separates first and last strands at t0 and 1/t0
  7 Lemma 7.2 with the actual kappa: W_0^(3) = -[X1, [X2, X3]] from the Magnus expansion of P4; exact counts
    0 < f(0, s*) < f(0); one direct exponential sum including kappa_t* equals |U| times the count
  8 Gadget replication: measured form = predicted form on K2 gadgets (6_3 at (7,3), C_2 at (13,4), and a conjugated
    figure-eight representative at (11,5))
Run: python3 -B check.py [--write]"""
import glob
import itertools
import json
import os
import sys
import time
import numpy as np
import sympy as sp

T_START = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, glob.glob(os.path.join(ROOT, "proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*"))[0])
sys.path.insert(1, glob.glob(os.path.join(ROOT, "experiments/COPRIME-DICHOTOMY-20261027-001B/*E002_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
from cd_lib import (BraidAlg, Grp, CyclicBraidModel, braid_meta, free_graded, nullspace, rank, solve_any, root_of_unity,
                    pair_failures, triple_failures)  # noqa: E402
import gd  # noqa: E402  (read-only: Burau, Squier forms, summands, gadgets, predictions)
import mlib  # noqa: E402  (read-only: P4, free-group Artin action, Magnus tensor)

out = {}
ok_all = True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:700], flush=True)


def inv_word(w):
    return [-g for g in reversed(w)]


def is_knot(word, n):
    try:
        braid_meta(word, n)
        return True
    except AssertionError:
        return False


def fixed(word, n, t, p):
    return nullspace((gd.bur_word(word, n, t, p) - np.eye(n, dtype=np.int64)) % p, p)


def class_vector(word, n, t, p):
    """a non-constant fixed colouring when the fixed space is constants plus one class, else None"""
    F = fixed(word, n, t, p)
    if len(F) != 2: return None
    return next(f for f in F if len(set(((f - f[0]) % p).tolist())) > 1)


# ---------------------------------------------------------------- 1 Lemma 3.0 (Fox normalization)
rng = np.random.default_rng(1)
rows, bad, tested = [], 0, 0
for (p, d) in [(7, 3), (13, 4), (11, 5), (7, 6), (13, 12)]:
    zeta = root_of_unity(p, d)
    A = BraidAlg(gd.four_way(p, d, 1), zeta)
    nb = 0
    while nb < 8:
        n = int(rng.integers(2, 6))
        word = [int(rng.integers(1, n)) * int(rng.choice([1, -1])) for _ in range(int(rng.integers(3, 14)))]
        if not is_knot(word, n): continue
        nb += 1
        M = CyclicBraidModel(word, n, A, p)
        for c in range(d):
            t = pow(zeta, c, p)
            lit = M.Lin[c][:n] % p
            pred = pow(t, p - 2, p) * (gd.bur_word(word, n, t, p) - np.eye(n, dtype=np.int64)) % p
            bad += int((lit != pred).any()); tested += 1
    rows.append({"p": p, "d": d, "braids": nb})
report("1 Fox normalization", bad == 0, {"cases": rows, "characters tested": tested, "mismatches": bad})

# ---------------------------------------------------------------- 2 Squier form and the reversed Artin identity (replay)
t = sp.symbols("t")


def bur_sym(n, g, tt):
    M = sp.eye(n)
    i = abs(g) - 1
    if g > 0:
        M[i, i], M[i, i + 1], M[i + 1, i], M[i + 1, i + 1] = 1 - 1 / tt, 1 / tt, 1, 0
    else:
        M[i, i], M[i, i + 1], M[i + 1, i], M[i + 1, i + 1] = 0, 1, tt, 1 - tt
    return M


ok, rows = True, {}
for n in range(2, 8):
    J = sp.Matrix(n, n, lambda a, b: 1 if a == b else ((t - 1) * t ** (a - b - 1) if a > b else 0))
    nbad = 0
    for g in list(range(1, n)) + [-g for g in range(1, n)]:
        E = sp.simplify(bur_sym(n, g, 1 / t).T * J * bur_sym(n, g, t) - J)
        nbad += any(e != 0 for e in E)
    rows[f"symbolic n={n}"] = nbad == 0
    ok &= nbad == 0
modp_bad = 0
for p in (5, 7, 11, 13):
    for tt in range(2, p):
        for n in (5, 8, 12):
            J = gd.squier(n, tt, p)
            for g in list(range(1, n)) + [-g for g in range(1, n)]:
                modp_bad += int(((gd.bur(n, g, pow(tt, p - 2, p), p).T @ J @ gd.bur(n, g, tt, p) - J) % p).any())
            one = np.ones(n, dtype=np.int64)
            modp_bad += int(((J.T @ one - np.array([pow(tt, n - 1 - q, p) for q in range(n)])) % p).any())
        for d in range(2, p):
            if (p - 1) % d: continue
            td = root_of_unity(p, d)
            n = 3 * d + 1
            J = gd.squier(n, td, p)
            s = np.random.default_rng(d * p).integers(0, p, n)
            T = (J.T @ s) % p
            for o in range(n - d + 1):
                modp_bad += int((T[o:o + d].sum() - sum(pow(td, i, p) * s[o + i] for i in range(d))) % p != 0)
rows["mod p failures (invariance, J^T 1, bundle identity)"] = modp_bad
ok &= modp_bad == 0
rng = np.random.default_rng(3)
nrev, nfwd_fail = 0, 0
for trial in range(60):
    n = int(rng.integers(2, 7))
    word = [int(rng.integers(1, n)) * int(rng.choice([1, -1])) for _ in range(int(rng.integers(1, 13)))]
    img = mlib.artin(word, n)
    R = [mlib.red([(j, -1)] + img[j]) for j in range(n)]
    rev, fwd = [], []
    for j in range(n - 1, -1, -1):
        P = [(q, 1) for q in range(n - 1, j - 1, -1)]
        rev += P + R[j] + mlib.inv(P)
    for j in range(n):
        P = [(q, 1) for q in range(0, j + 1)]
        fwd += P + R[j] + mlib.inv(P)
    nrev += int(len(mlib.red(rev)) == 0)
    nfwd_fail += int(len(mlib.red(fwd)) != 0)
rows["reversed Artin identity holds"] = f"{nrev}/60"
rows["forward identity fails"] = f"{nfwd_fail}/60"
ok &= nrev == 60 and nfwd_fail > 0
report("2 Squier form and reversed Artin identity", ok, rows)

# ---------------------------------------------------------------- 3 Lemma 4.0 (canonical pinned coordinates)
rows, ok = [], True
for (p, d, gens, c) in [(7, 6, [1, 5, 3], 3), (7, 6, [1, 5, 3], 4), (13, 12, [1, 11, 4, 8], 3), (13, 4, [1, 3, 2], 4),
                        (11, 10, [2, 8, 5, 3], 3), (13, 6, [1, 5, 2, 4], 4), (7, 3, [0, 1, 2], 4), (11, 5, [1, 4, 0], 4)]:
    Q = gd.p2_quotient(free_graded(p, d, gens, c))
    tf = triple_failures(Q)
    far = [(a, b) for (a, b) in tf if b % d not in (a % d, (-a) % d)]
    odd = [k for k in range(Q.D) if Q.chars[k] % d]
    bad_parity = 0
    for m in (2, 3, 4):
        for tup in itertools.product(odd, repeat=m):
            v = Q.unit(tup[0])
            for k in tup[1:]:
                v = Q.br(v, Q.unit(k))
            nz = np.nonzero(v[0])[0]
            if len(nz):
                chars = {int(Q.chars[k]) % d for k in nz}
                if (m % 2 == 0) != (chars == {0}): bad_parity += 1
    shapes = set()
    for a in range(1, d):
        if (2 * a) % d == 0: continue
        Ua, Um = Q.comp(a), Q.comp(-a)
        for x, y, z in itertools.product(Ua + Um, repeat=3):
            v = Q.br(Q.br(Q.unit(x), Q.unit(y)), Q.unit(z))
            if v.any():
                shapes.add((sum(k in Ua for k in (x, y, z)), sum(k in Um for k in (x, y, z))))
    unbalanced = sorted(s for s in shapes if 0 in s)
    rows.append({"p": p, "d": d, "generator characters": gens, "class": c, "pair failures": pair_failures(Q),
                 "far triple failures": far, "parity violations": bad_parity, "triple shapes (+a, -a)": sorted(shapes),
                 "unbalanced": unbalanced})
    ok &= not far and not bad_parity and not pair_failures(Q) and not unbalanced


def layered_runs(Mo, rng, bs):
    """two layered lifts sharing the layer-1 and layer-2 data and differing in the odd layer-3 cocycles"""
    A, p = Mo.A, Mo.p
    odd = {k for k in range(A.D) if A.chars[k] % A.d}
    rnd = {k: (rng.integers(0, p, (bs, len(Mo.cocycles[int(A.chars[k])]))) @ Mo.cocycles[int(A.chars[k])]) % p
           for k in odd if A.layer[k] <= 2 and len(Mo.cocycles[int(A.chars[k])])}
    res = []
    for run in range(2):
        r3 = {k: (rng.integers(0, p, (bs, len(Mo.cocycles[int(A.chars[k])]))) @ Mo.cocycles[int(A.chars[k])]) % p
              for k in odd if A.layer[k] == 3 and len(Mo.cocycles[int(A.chars[k])])}
        V = np.zeros((bs, Mo.n, A.D), dtype=np.int64)
        okl, R2 = np.ones(bs, dtype=bool), None
        for lay in (1, 2, 3):
            R = Mo.run(V)
            if lay == 2: R2 = R
            for k in [k for k in range(A.D) if A.layer[k] == lay]:
                X, b = solve_any(Mo.Lin[int(A.chars[k])], (-R[:, :, k]).T % p, p)
                okl &= ~b
                V[:, :, k] = (X.T + rnd.get(k, 0) + r3.get(k, 0)) % p
        res.append((R2, Mo.run(V), okl, r3))
    return res, odd


rng = np.random.default_rng(31)
rows_k = []
for (p, d, name, summ, aname) in [(7, 3, "6_1 (chiral)", gd.CHIRAL["6_1"], "layer4"), (7, 3, "6_1 (chiral)", gd.CHIRAL["6_1"], "F4"),
                                  (7, 3, "6_3", gd.AMPH["6_3"], "layer4"), (13, 4, "C_2 of T(2,13)", gd.torus_cable(13, 2), "layer4"),
                                  (11, 5, "4_1", gd.AMPH["4_1"], "F4")]:
    zeta = root_of_unity(p, d)
    e = 1
    if name == "4_1":
        e = next(a for a in range(1, d) if (pow(zeta, a, p) + pow(zeta, -a % d, p)) % p == 3)
    L = gd.layer4_algebra(p, d, e) if aname == "layer4" else gd.p2_quotient(free_graded(p, d, [e, -e % d], 4))
    w, n = summ
    Mo = CyclicBraidModel(w, n, BraidAlg(L, zeta), p)
    (R2a, R4a, oka, r3a), (R2b, R4b, okb, r3b) = layered_runs(Mo, rng, 24)[0]
    odd = [k for k in range(L.D) if L.chars[k] % d]
    odd2 = [k for k in odd if L.layer[k] == 2]
    odd4 = [k for k in odd if L.layer[k] == 4]
    even4 = [k for k in range(L.D) if L.layer[k] == 4 and L.chars[k] % d == 0]
    zero2 = all(not (R2a[:, :, k] % p).any() and not (R2b[:, :, k] % p).any() for k in odd2)
    same4 = all(((R4a[:, :, k] - R4b[:, :, k]) % p == 0).all() for k in odd4)
    varied = any(((r3a[k] - r3b[k]) % p).any() for k in r3a)
    even_moves = any(((R4a[:, :, k] - R4b[:, :, k]) % p).any() for k in even4)
    triv0 = len(Mo.cocycles[0]) == 0
    rows_k.append({"p": p, "d": d, "knot": name, "algebra": aname, "odd layer-2 / layer-4 components": [len(odd2), len(odd4)],
                   "odd layer-2 residuals vanish": zero2,
                   "pinned trivial cocycles": len(Mo.cocycles[0]), "odd layer-3 cocycles varied": varied,
                   "odd layer-4 residuals unchanged": same4, "even layer-4 residuals moved (control)": even_moves,
                   "samples unobstructed through layer 3": int((oka & okb).sum())})
    ok &= zero2 and same4 and varied and even_moves and triv0
ok &= any(r["odd layer-2 / layer-4 components"][0] for r in rows_k) and any(r["odd layer-2 / layer-4 components"][1] for r in rows_k)
report("3 canonical pinned coordinates", ok, {"pair quotients": rows, "knot models": rows_k})

# ---------------------------------------------------------------- 4 Lemma 4.3 (cable summands)
x = sp.symbols("x")
ok, rows = True, []
spec_bad, spec_n = 0, 0
for p in (5, 7, 11, 13, 17):
    for k in range(1, 7):
        delta = list(range(1, k))
        for tt in range(2, p):
            Mk = gd.bur_word(delta, k, tt, p) if k > 1 else np.eye(1, dtype=np.int64)
            cp = sp.Poly(sp.Matrix(Mk.tolist()).charpoly(x).as_expr(), x)
            ti = pow(tt, p - 2, p)
            target = sp.Poly(sp.expand((x - 1) * sum(pow(ti, k - 1 - i, p) * x ** i for i in range(k))), x)
            spec_bad += int(any((a - b) % p for a, b in itertools.zip_longest(cp.all_coeffs()[::-1], target.all_coeffs()[::-1],
                                                                              fillvalue=0)))
            spec_n += 1
rows.append({"delta_k characteristic polynomials (p <= 17, k <= 6, every t != 1)": spec_n, "mismatches": spec_bad})
ok &= spec_bad == 0
fix_bad, fix_rows = 0, []
for (p, k) in [(5, 1), (5, 2), (13, 2), (7, 3), (13, 3), (11, 5), (17, 4), (13, 6)]:
    w, n = gd.torus_cable(p, k)
    roots = []
    for tt in range(2, p):
        F = fixed(w, n, tt, p)
        if pow(tt, k, p) == p - 1:
            roots.append(tt)
            B = np.zeros((2, n), dtype=np.int64); B[0, :k] = 1; B[1, k:] = 1
            fix_bad += int(not (len(F) == 2 and rank(np.vstack([F, B]) % p, p) == 2))
        else:
            fix_bad += int(not (len(F) == 1 and len(set(F[0].tolist())) == 1))
    fix_rows.append({"p": p, "k": k, "strands": n, "crossings": len(w), "roots t^k = -1": roots})
rows.append({"Fix Bur_t(C_k) = bundle constants at t^k = -1, constants elsewhere": fix_rows, "failures": fix_bad})
ok &= fix_bad == 0

# the integer-exponent map on T(2,13) with theta' = tau^2 of order 6 (d = 12)
p, d, k = 13, 12, 2
zeta = root_of_unity(p, d)
Rset = [c for c in range(1, d) if pow(zeta, c * k, p) == p - 1]
order_theta = d // int(np.gcd(k, d))
word_T, nT = [1] * p, 2
Fm = fixed(word_T, nT, p - 1, p)
cvec = np.array([0, 1], dtype=np.int64)
is_cocycle = len(Fm) == 2
hom_rows = []
for aname, L in [("four-way", gd.four_way(p, d, 3)), ("pairfail3", free_graded(p, d, [3, 3], 3)),
                 ("layer4", gd.layer4_algebra(p, d, 3))]:
    Aalg = BraidAlg(L, zeta)
    G = Grp(Aalg)
    bs = 16
    U = [kk for kk in range(L.D) if int(L.chars[kk]) % d in Rset]
    Avec = np.zeros((bs, L.D), dtype=np.int64)
    Avec[:, U] = rng.integers(0, p, (bs, len(U)))
    gens = [((cvec[j] * Avec) % p, k) for j in range(nT)]
    cur, overs = list(gens), {}
    for l, g in enumerate(word_T):
        i = abs(g) - 1
        a, b = cur[i], cur[i + 1]
        if g > 0:
            overs[l] = a
            cur[i], cur[i + 1] = G.mul(G.mul(G.inv(a), b), a), a
        else:
            overs[l] = b
            cur[i], cur[i + 1] = b, G.mul(G.mul(b, a), G.inv(b))
    rel_ok = all(G.mul(G.inv(gens[j]), cur[j])[1] == 0 and not (G.mul(G.inv(gens[j]), cur[j])[0] % p).any()
                 for j in range(nT))
    order, writhe = braid_meta(word_T, nT)
    lam = (np.zeros((bs, L.D), dtype=np.int64), 0)
    for l in order:
        lam = G.mul(lam, overs[l] if word_T[l] > 0 else G.inv(overs[l]))
    for _ in range(abs(writhe)):
        lam = G.mul(lam, G.inv(gens[0]) if writhe > 0 else gens[0])
    lam_ok = lam[1] == 0 and not (lam[0] % p).any()
    hom_rows.append({"algebra": aname, "dim U": len(U), "relators hold": bool(rel_ok), "longitude -> 1": bool(lam_ok)})
    ok &= rel_ok and lam_ok
rows.append({"integer-exponent map": {"p": p, "d": d, "k": k, "root characters": Rset, "order of theta'": order_theta,
                                      "c is a sign-twisted cocycle": is_cocycle, "algebras": hom_rows}})
ok &= order_theta == 6 and is_cocycle

lift_rows = []
for (p, d, k) in [(5, 4, 2), (13, 4, 2), (7, 6, 3), (13, 6, 3), (11, 10, 5), (17, 8, 4), (13, 12, 6), (13, 12, 2)]:
    zeta = root_of_unity(p, d)
    w, n = gd.torus_cable(p, k)
    R = [c for c in range(1, d) if pow(zeta, c * k, p) == p - 1]
    for aname in ("four-way", "F3", "layer4", "pairfail3"):
        e = R[0]
        L = {"four-way": gd.four_way(p, d, e), "F3": gd.p2_quotient(free_graded(p, d, [e, -e % d], 3)),
             "layer4": gd.layer4_algebra(p, d, e), "pairfail3": free_graded(p, d, [e, e], 3)}[aname]
        Mo = CyclicBraidModel(w, n, BraidAlg(L, zeta), p)
        dims = {c: len(Mo.cocycles[c]) for c in range(1, d)}
        roots_ok = all((dims[c] == 2) == (c in R) and dims[c] in (1, 2) for c in range(1, d))   # constants + classes
        oddk = [kk for kk in range(L.D) if L.chars[kk] % d]
        inputs = {kk: (rng.integers(0, p, (12, len(Mo.cocycles[int(L.chars[kk])]))) @ Mo.cocycles[int(L.chars[kk])]) % p
                  for kk in oddk}
        lift, _, _ = Mo.solve(inputs)
        lift_rows.append({"p": p, "d": d, "k": k, "algebra": aname, "cohomology exactly at t^k = -1": roots_ok,
                          "lift fraction": float(lift.mean())})
        ok &= roots_ok and bool(lift.all())
rows.append({"every datum lifts": lift_rows})
report("4 cable summands (Lemma 4.3)", ok, rows)


# ---------------------------------------------------------------- 5 Lemma 4.4 inputs (replay)
def two_bridge(alpha, beta):
    alpha = abs(alpha)
    beta = beta % alpha
    if beta % 2 == 0: beta -= alpha
    eps = [1 - 2 * (((i * beta) // alpha) % 2) for i in range(1, alpha)]
    w = [(2 if i % 2 == 0 else 1) * e for i, e in enumerate(eps)]
    return 2, [[1] + w + [-2] + [-g for g in reversed(w)]]


def fox_alexander(word_rel):
    outp, pref = 0, 0
    for g in word_rel:
        if abs(g) == 1:
            outp += t ** pref if g > 0 else -t ** (pref - 1)
        pref += 1 if g > 0 else -1
    return sp.expand(outp)


ok, rows = True, []
for m in range(1, 7):
    _, rels = two_bridge(4 * m * m + 1, 2 * m)
    dax = fox_alexander(rels[0])
    target = -m * m * (t + 1 / t) + 2 * m * m + 1
    unit_ok = any(sp.simplify(dax - s * t ** kk * target) == 0 for s in (1, -1) for kk in range(-3, 4))
    amph = (4 * m * m) % (4 * m * m + 1) == 4 * m * m
    rows.append({"m": m, "Alexander polynomial matches": unit_ok, "(2m)^2 = -1 mod 4m^2+1": amph})
    ok &= unit_ok and amph
for (p, d) in [(7, 3), (13, 3), (11, 5), (19, 9), (29, 7), (31, 15)]:
    zeta = root_of_unity(p, d)
    for a in range(1, d):
        t0 = pow(zeta, a, p)
        sq = next(xx for xx in range(1, p) if xx * xx % p == t0)
        m = sq * pow(t0 - 1, p - 2, p) % p
        poly = [(-m * m) % p, (2 * m * m + 1) % p, (-m * m) % p]           # t * Delta = -m^2 t^2 + (2m^2+1) t - m^2
        roots = [tt for tt in range(1, p) if (poly[0] * tt * tt + poly[1] * tt + poly[2]) % p == 0]
        good = sorted(roots) == sorted({t0, pow(t0, p - 2, p)}) and len(roots) == 2 and (4 * m * m + 1) % p != 0
        ok &= good
        if not good: rows.append({"p": p, "d": d, "a": a, "roots": roots})
rows.append({"odd-order roots t0 (p, d) checked": [(7, 3), (13, 3), (11, 5), (19, 9), (29, 7), (31, 15)],
             "all roots exactly t0^(+-1), Delta(-1) != 0": ok})
report("5 amphichiral summands (Lemma 4.4)", ok, rows)


# ---------------------------------------------------------------- 6 Lemma 6.1 (reading strands)
def partitions(s):
    if not s:
        yield []
        return
    first, rest = s[0], s[1:]
    for P in partitions(rest):
        for i in range(len(P)):
            yield P[:i] + [[first] + P[i]] + P[i + 1:]
        yield [[first]] + P


def two_partition_pair(lab1, lab2):
    n = len(lab1)
    return next(((a, b) for a in range(n) for b in range(n) if a != b and lab1[a] != lab1[b] and lab2[a] != lab2[b]), None)


ok, rows = True, []
tp_fail, tp_n = 0, 0
for n in range(2, 7):
    parts = [P for P in partitions(list(range(n))) if len(P) >= 2]
    labs = []
    for P in parts:
        lab = [0] * n
        for bi, B in enumerate(P):
            for q in B: lab[q] = bi
        labs.append(lab)
    for l1 in labs:
        for l2 in labs:
            tp_n += 1
            tp_fail += int(two_partition_pair(l1, l2) is None)
rows.append({"two-partition lemma: partition pairs (n <= 6)": tp_n, "failures": tp_fail})
ok &= tp_fail == 0

cab_bad = 0
for (p, k) in [(5, 2), (13, 2), (7, 3), (13, 3), (11, 5), (17, 4), (13, 6)]:
    w, n = gd.torus_cable(p, k)
    for tt in range(2, p):
        if pow(tt, k, p) != p - 1: continue
        v = class_vector(w, n, tt, p)
        cab_bad += int(v is None or (v[-1] - v[0]) % p == 0)
rows.append({"cables: first and last strands separated at every t with t^k = -1": cab_bad == 0})
ok &= cab_bad == 0


def eta_word(qa, qb, n):
    """move strand qa to position 0 and strand qb to position n - 1, each as an over-strand"""
    w = [-j for j in range(qa, 0, -1)]
    qb2 = qb + 1 if qb < qa else qb
    w += list(range(qb2 + 1, n))
    return w


rng = np.random.default_rng(6)
amph_rows, fixed_count, bad_before = [], 0, 0
cases = []
for name in gd.AMPH:
    w0, n = gd.AMPH[name]
    found = 0
    for p in (7, 11, 13, 19, 29, 31, 37, 41, 43, 61, 67, 71, 73, 79):
        for d in range(3, p, 2):
            if (p - 1) % d or found >= 2: continue
            zeta = root_of_unity(p, d)
            for a in range(1, d):
                t0, t1 = pow(zeta, a, p), pow(zeta, (-a) % d, p)
                if class_vector(w0, n, t0, p) is not None and class_vector(w0, n, t1, p) is not None:
                    cases.append((name, p, d, t0, t1)); found += 1
                    break
for (name, p, d, t0, t1) in cases:
    w0, n = gd.AMPH[name]
    for trial in range(12):
        gam = [int(rng.integers(1, n)) * int(rng.choice([1, -1])) for _ in range(int(rng.integers(0, 9)))]
        beta = inv_word(gam) + list(w0) + gam
        v0, v1 = class_vector(beta, n, t0, p), class_vector(beta, n, t1, p)
        sep = lambda va, vb, a, b: (va[a] - va[b]) % p != 0 and (vb[a] - vb[b]) % p != 0
        before = sep(v0, v1, 0, n - 1)
        bad_before += int(not before)
        qa, qb = two_partition_pair([int(z) for z in v0], [int(z) for z in v1])
        eta = eta_word(qa, qb, n)
        beta2 = inv_word(eta) + beta + eta
        assert is_knot(beta2, n)
        u0, u1 = class_vector(beta2, n, t0, p), class_vector(beta2, n, t1, p)
        after = u0 is not None and u1 is not None and sep(u0, u1, 0, n - 1)
        fixed_count += int(after)
        ok &= after
    amph_rows.append({"knot": name, "p": p, "d": d, "t0": t0})
ok &= {c[0] for c in cases} == set(gd.AMPH)
rows.append({"amphichiral representatives (random conjugates)": len(cases) * 12, "first/last not separated before": bad_before,
             "separated after the over-strand conjugation": fixed_count, "cases": amph_rows})
ok &= bad_before > 0
report("6 reading strands (Lemma 6.1)", ok, rows)

# ---------------------------------------------------------------- 7 Lemma 7.2 with the actual kappa
ok, rows = True, []
for pp in (5, 7, 11):
    T3 = mlib.degree3_tensor(mlib.P4, 4, pp)
    target = {}
    for (a, b, c), s in [((1, 2, 3), 1), ((1, 3, 2), -1), ((2, 3, 1), -1), ((3, 2, 1), 1)]:      # [X1, [X2, X3]]
        target[(a, b, c)] = (-s) % pp
    got = {kk: v % pp for kk, v in T3[0].items() if v % pp}
    ok &= got == {kk: v for kk, v in target.items() if v}
rows.append({"W_0^(3) = -[X1, [X2, X3]] (Magnus degree 3, p = 5, 7, 11)": bool(ok)})


def edge_counts(L, R_chars, p, d):
    U = [k for k in range(L.D) if L.layer[k] <= 2 and int(L.chars[k]) % d in R_chars]
    outs = [k for k in range(L.D) if L.layer[k] >= 3 and int(L.chars[k]) % d in R_chars]
    E = np.eye(L.D, dtype=np.int64)
    best = None
    pairs = np.array(list(itertools.product(range(p), repeat=2 * len(U))), dtype=np.int64)
    P2 = np.zeros((len(pairs), L.D), dtype=np.int64); P3 = np.zeros((len(pairs), L.D), dtype=np.int64)
    P2[:, U] = pairs[:, :len(U)]; P3[:, U] = pairs[:, len(U):]
    B = L.br(P2, P3)
    for o in outs:
        zero = np.ones(len(pairs), dtype=bool)
        for i in U:
            zero &= L.br(np.repeat(E[i:i + 1], len(pairs), axis=0), B)[:, o] % p == 0
        cnt = int(zero.sum())
        if cnt < p ** (2 * len(U)) and (best is None or cnt < best[0]):
            best = (cnt, o)
    return best, U, B


for (p, d, aname, kind) in [(7, 3, "four-way", "amphichiral"), (13, 4, "four-way", "cable"), (7, 6, "four-way", "cable"),
                            (11, 5, "four-way", "amphichiral"), (5, 4, "layer4", "cable"), (7, 3, "layer4", "amphichiral")]:
    zeta = root_of_unity(p, d)
    L = gd.four_way(p, d, 1) if aname == "four-way" else gd.layer4_algebra(p, d, 1)
    if kind == "amphichiral":
        R = {1, d - 1}
    else:
        kk = next(kk for kk in range(1, d) if pow(zeta, kk, p) == p - 1)
        R = {c for c in range(1, d) if pow(zeta, c * kk, p) == p - 1}
    best, U, B = edge_counts(L, R, p, d)
    if best is None:
        rows.append({"p": p, "d": d, "algebra": aname, "nonzero trilinear form": False}); ok = False; continue
    cnt, o = best
    f0, fd = p ** (3 * len(U)), p ** len(U) * cnt
    row = {"p": p, "d": d, "algebra": aname, "summand": kind, "dim U": len(U), "s* component": L.names[o],
           "f(0)/|U'|^3": f0, "f(0,s*)/|U'|^3": fd, "0 < f(0,s*) < f(0)": 0 < fd < f0}
    if (p, d, aname) == (7, 3, "four-way"):
        tstar = pow(zeta, int(L.chars[o]), p)
        kap = gd.kappa(tstar, p)
        E = np.eye(L.D, dtype=np.int64)
        Mlin = np.array([L.br(np.repeat(E[i:i + 1], len(B), axis=0), B)[:, o] % p for i in U])     # (dim U, pairs)
        omega = np.exp(2j * np.pi / p)
        total = 0j
        for A1 in itertools.product(range(p), repeat=len(U)):
            val = (-kap * (np.array(A1) @ Mlin)) % p
            total += np.exp(2j * np.pi * val / p).sum()
        row["kappa_t*"] = kap
        row["direct exponential sum"] = round(total.real, 3)
        row["imaginary part"] = round(abs(total.imag), 6)
        good = abs(total.real - fd) < 1e-3 and abs(total.imag) < 1e-3
        row["direct sum = |U| * count"] = bool(good)
        ok &= good
    rows.append(row)
    ok &= 0 < fd < f0
report("7 edge weight with the actual coefficients", ok, rows)

# ---------------------------------------------------------------- 8 gadget replication
ok, rows = True, []
rng = np.random.default_rng(8)
w41, n41 = gd.AMPH["4_1"]
p, d = 11, 5
zeta = root_of_unity(p, d)
a41 = next(a for a in range(1, d) if (pow(zeta, a, p) + pow(zeta, -a % d, p)) % p == 3)
t0, t1 = pow(zeta, a41, p), pow(zeta, -a41 % d, p)
conj41 = None
for trial in range(200):
    gam = [int(rng.integers(1, n41)) * int(rng.choice([1, -1])) for _ in range(int(rng.integers(1, 7)))]
    beta = inv_word(gam) + list(w41) + gam
    v0, v1 = class_vector(beta, n41, t0, p), class_vector(beta, n41, t1, p)
    if (v0[0] - v0[-1]) % p and (v1[0] - v1[-1]) % p: continue
    qa, qb = two_partition_pair([int(z) for z in v0], [int(z) for z in v1])
    eta = eta_word(qa, qb, n41)
    conj41 = (inv_word(eta) + beta + eta, n41)
    u0, u1 = class_vector(conj41[0], n41, t0, p), class_vector(conj41[0], n41, t1, p)
    assert (u0[0] - u0[-1]) % p and (u1[0] - u1[-1]) % p
    break
assert conj41 is not None
for (p, d, summ, name, e) in [(7, 3, gd.AMPH["6_3"], "6_3", 1), (13, 4, gd.torus_cable(13, 2), "(2,1)-cable of T(2,13)", 1),
                              (11, 5, conj41, "figure-eight, conjugated representative", a41)]:
    zeta = root_of_unity(p, d)
    word, n, events, vstr, pb = gd.build_gadget(2, [(0, 1)], d, summ, summ)
    for aname in ("four-way", "layer4"):
        L = gd.four_way(p, d, e) if aname == "four-way" else gd.layer4_algebra(p, d, e)
        A = BraidAlg(L, zeta)
        Mo = CyclicBraidModel(word, n, A, p)
        odd = [k for k in range(L.D) if L.chars[k] % d]
        inputs = {k: (rng.integers(0, p, (8, len(Mo.cocycles[int(L.chars[k])]))) @ Mo.cocycles[int(L.chars[k])]) % p
                  for k in odd if L.layer[k] <= 3}
        data = {k: v for k, v in inputs.items() if L.layer[k] <= 2}
        match, nonzero = True, 0
        for comp in [k for k in odd if L.layer[k] >= 3]:
            cs = Mo.cocycles[(-int(L.chars[comp])) % d]
            s = (rng.integers(0, p, (8, len(cs))) @ cs) % p
            Qm, okm, _, _ = gd.measure_Q(Mo, inputs, int(L.layer[comp]), comp, s)
            Qp = gd.predict_Q(L, A, word, n, events, data, s, comp, p)
            match &= bool((Qm[okm] == Qp[okm]).all()); nonzero += int((Qm != 0).sum())
        rows.append({"p": p, "d": d, "summand": name, "algebra": aname, "strands": n, "crossings": len(word), "match": match,
                     "nonzero samples": nonzero})
        ok &= match and nonzero > 0
report("8 gadget replication", ok, rows)

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "COPRIME-PAIRS-20261027-001A-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out,
                   "seconds": round(time.time() - T_START, 1)}, fh, indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T_START, 1), "s")
