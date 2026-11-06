"""Checks for COPRIME-DICHOTOMY-20261027-001C-P001.

  1 Lemma 1 and parity: on pair quotients of free graded algebras every triple failure is near; nonzero left-normed monomials of
    degree <= 4 in odd basis elements have character 0 exactly when the degree is even
  2 Lemma 3.1: Bur_(1/t)(g)^T J_t Bur_t(g) = J_t over Z[t, 1/t] (n <= 7) and mod p (n <= 12); bundle identity; J_t^T 1
  3 Lemma 3.2: the reversed Artin identity prod_(j = n-1 .. 0) P_j R_j P_j^-1 = 1 in the free group; the forward one fails
  4 Lemma 4.1 inputs: b(4m^2+1, 2m) has Alexander polynomial -m^2 (t + 1/t) + 2m^2 + 1 and (2m)^2 = -1 mod 4m^2 + 1; the knot built
    from the formula at odd-order t0 has cohomology exactly at t0^(+-1) and every datum lifts (four-way, F3, layer4)
  5 Lemma 4.2: (k,1)-cables of T(2,p) have cohomology exactly at t^k = -1 and every datum lifts (also for a pair-failing algebra)
  6 Lemma 5.1: cable_d(P4) conjugates each bundle strand by W_j on reverse-order bundle products (free group, d = 2..6)
  7 Lemma 7.2: exact edge-weight counts 0 < f(0, s*) < f(0) for the four-way and class-4 algebras on both summand types
  8 Proposition 5.5 on gadgets (replication of COPRIME-DICHOTOMY-20261027-001B-E002 on one gadget per construction)
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
from cd_lib import (GLie, BraidAlg, Grp, CyclicBraidModel, free_graded, nullspace, solve_any, root_of_unity, pair_failures,
                    triple_failures)  # noqa: E402
import gd  # noqa: E402  (read-only: Squier forms, summands, gadgets, predictions)
import mlib  # noqa: E402  (read-only: P4, free-group Artin action, Magnus tensor)
import cp_lib as C  # noqa: E402  (read-only: cables, connected sums)

out = {}
ok_all = True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:600], flush=True)


# ---------------------------------------------------------------- 1 Lemma 1 and parity
rows, ok = [], True
for (p, d, gens, c) in [(7, 6, [1, 5, 3], 3), (7, 6, [1, 5, 3], 4), (13, 12, [1, 11, 4, 8], 3), (13, 4, [1, 3, 2], 4),
                        (11, 10, [2, 8, 5, 3], 3), (13, 6, [1, 5, 2, 4], 4), (7, 3, [0, 1, 2], 4)]:
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
    rows.append({"p": p, "d": d, "generator characters": gens, "class": c, "pair failures": pair_failures(Q), "triple failures": tf,
                 "far": far, "parity violations": bad_parity})
    ok &= not far and not bad_parity and not pair_failures(Q)
report("1 near triples and parity", ok, rows)

# ---------------------------------------------------------------- 2 Squier form
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
    bad = 0
    for g in list(range(1, n)) + [-g for g in range(1, n)]:
        E = sp.simplify(bur_sym(n, g, 1 / t).T * J * bur_sym(n, g, t) - J)
        bad += any(e != 0 for e in E)
    rows[f"symbolic n={n}"] = bad == 0
    ok &= bad == 0
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
report("2 Squier form", ok, rows)

# ---------------------------------------------------------------- 3 reversed Artin identity
rng = np.random.default_rng(3)
ok, nrev, nfwd_fail = True, 0, 0
for trial in range(60):
    n = int(rng.integers(2, 7))
    word = [int(rng.integers(1, n)) * int(rng.choice([1, -1])) for _ in range(int(rng.integers(1, 13)))]
    img = mlib.artin(word, n)
    R = [mlib.red([(j, -1)] + img[j]) for j in range(n)]
    rev = []
    for j in range(n - 1, -1, -1):
        P = [(q, 1) for q in range(n - 1, j - 1, -1)]
        rev += P + R[j] + mlib.inv(P)
    nrev += int(len(mlib.red(rev)) == 0)
    fwd = []
    for j in range(n):
        P = [(q, 1) for q in range(0, j + 1)]
        fwd += P + R[j] + mlib.inv(P)
    nfwd_fail += int(len(mlib.red(fwd)) != 0)
ok = nrev == 60 and nfwd_fail > 0
report("3 reversed Artin identity", ok, {"braids": 60, "reversed identity holds": nrev, "forward identity fails": nfwd_fail})


# ---------------------------------------------------------------- 4 and 5 summands (knot group with mu^d at slope d/p)
def two_bridge(alpha, beta):
    alpha = abs(alpha)
    beta = beta % alpha
    if beta % 2 == 0: beta -= alpha
    eps = [1 - 2 * (((i * beta) // alpha) % 2) for i in range(1, alpha)]
    w = [(2 if i % 2 == 0 else 1) * e for i, e in enumerate(eps)]
    return 2, [[1] + w + [-2] + [-g for g in reversed(w)]]


class PresModel:
    """generators labelled in the coset N sigma, the knot relators and mu^d (lambda^p acts trivially at slope d/p)"""

    def __init__(self, ngen, rels, A):
        self.n, self.rels, self.A, self.p = ngen, rels + [[1] * A.d], A, A.p
        self.Lin = {}
        for c in range(A.d):
            L1 = GLie(self.p, A.d, ["e"], [1], [c], np.zeros((1, 1, 1), dtype=np.int64), check=False)
            V = np.zeros((self.n, self.n, 1), dtype=np.int64)
            for q in range(self.n): V[q, q, 0] = 1
            self.Lin[c] = self.run(V, BraidAlg(L1, A.zeta))[:, :, 0].T % self.p
        self.cocycles = {c: nullspace(self.Lin[c], self.p) for c in range(A.d)}

    def run(self, V, A=None):
        A = A or self.A
        G = Grp(A)
        gens = [(V[:, q].copy(), 1) for q in range(self.n)]
        R = np.zeros((V.shape[0], len(self.rels), A.D), dtype=np.int64)
        for r, rel in enumerate(self.rels):
            acc = (np.zeros_like(V[:, 0]), 0)
            for g in rel:
                acc = G.mul(acc, gens[abs(g) - 1] if g > 0 else G.inv(gens[abs(g) - 1]))
            R[:, r] = acc[0]
        return R

    def lift_fraction(self, bs, rng):
        A, p = self.A, self.p
        odd = [k for k in range(A.D) if A.chars[k] % A.d]
        V = np.zeros((bs, self.n, A.D), dtype=np.int64)
        ok = np.ones(bs, dtype=bool)
        for lay in range(1, int(A.layer.max()) + 1):
            R = self.run(V)
            for k in [k for k in range(A.D) if A.layer[k] == lay]:
                X, bad = solve_any(self.Lin[int(A.chars[k])], (-R[:, :, k]).T % p, p)
                ok &= ~bad
                inp = 0
                if k in odd:
                    B = self.cocycles[int(A.chars[k])]
                    inp = (rng.integers(0, p, (bs, len(B))) @ B) % p
                V[:, :, k] = (X.T + inp) % p
        return float(ok.mean())


def fox_alexander(word_rel):
    """Fox derivative of a two-generator one-relator presentation with respect to the first generator, both generators -> t"""
    outp, pref = 0, 0
    for g in word_rel:
        if abs(g) == 1:
            outp += t ** pref if g > 0 else -t ** (pref - 1)
        pref += 1 if g > 0 else -1
    return sp.expand(outp)


ok, rows4 = True, []
for m in range(1, 6):
    n_, rels = two_bridge(4 * m * m + 1, 2 * m)
    dax = fox_alexander(rels[0])
    target = -m * m * (t + 1 / t) + 2 * m * m + 1
    unit_ok = any(sp.simplify(dax - s * t ** k * target) == 0 for s in (1, -1) for k in range(-3, 4))
    amph = (4 * m * m) % (4 * m * m + 1) == 4 * m * m + 1 - 1
    rows4.append({"m": m, "Alexander polynomial matches": unit_ok, "(2m)^2 = -1 mod 4m^2+1": amph})
    ok &= unit_ok and amph
rng = np.random.default_rng(4)
for (p, d) in [(7, 3), (13, 3), (11, 5), (19, 9), (29, 7)]:
    zeta = root_of_unity(p, d)
    t0 = zeta
    sq = next(x for x in range(1, p) if x * x % p == t0)
    m = sq * pow(t0 - 1, p - 2, p) % p
    n_, rels = two_bridge(4 * m * m + 1, 2 * m)
    for aname in ("four-way", "F3", "layer4"):
        L = {"four-way": gd.four_way(p, d, 1), "F3": gd.p2_quotient(free_graded(p, d, [1, -1], 3)),
             "layer4": gd.layer4_algebra(p, d, 1)}[aname]
        Mo = PresModel(n_, rels, BraidAlg(L, zeta))
        dims = {c: len(Mo.cocycles[c]) for c in range(1, d)}
        roots_ok = all((dims[c] == 2) == (c in (1, d - 1)) and dims[c] in (1, 2) for c in range(1, d))
        fr = Mo.lift_fraction(16, rng)
        rows4.append({"p": p, "d": d, "t0": t0, "m": m, "knot": f"b({4 * m * m + 1}, {2 * m})", "algebra": aname,
                      "roots exactly t0^(+-1)": roots_ok, "lift fraction": fr})
        ok &= roots_ok and fr == 1.0
report("4 amphichiral summands (odd orders)", ok, rows4)

ok, rows5 = True, []
for (p, d, k) in [(5, 4, 2), (13, 4, 2), (7, 6, 3), (13, 6, 3), (11, 10, 5), (17, 8, 4), (13, 12, 6)]:
    zeta = root_of_unity(p, d)
    w, n = gd.torus_cable(p, k)
    R = [c for c in range(1, d) if pow(zeta, c * k, p) == p - 1]
    for aname in ("four-way", "F3", "layer4", "pairfail3"):
        e = R[0]
        L = {"four-way": gd.four_way(p, d, e), "F3": gd.p2_quotient(free_graded(p, d, [e, -e], 3)),
             "layer4": gd.layer4_algebra(p, d, e), "pairfail3": free_graded(p, d, [e, e], 3)}[aname]
        Mo = CyclicBraidModel(w, n, BraidAlg(L, zeta), p)
        dims = {c: len(Mo.cocycles[c]) for c in range(1, d)}
        roots_ok = all((dims[c] == 2) == (c in R) and dims[c] in (1, 2) for c in range(1, d))
        odd = [kk for kk in range(L.D) if L.chars[kk] % d]
        inputs = {kk: (rng.integers(0, p, (12, len(Mo.cocycles[int(L.chars[kk])]))) @ Mo.cocycles[int(L.chars[kk])]) % p
                  for kk in odd}
        lift, _, _ = Mo.solve(inputs)
        rows5.append({"p": p, "d": d, "k": k, "algebra": aname, "roots at t^k = -1 exactly": roots_ok,
                      "lift fraction": float(lift.mean())})
        ok &= roots_ok and bool(lift.all())
report("5 cable summands (even orders)", ok, rows5)

# ---------------------------------------------------------------- 6 the cable lemma in the free group
ok, rows6 = True, []
conj = mlib.artin_conj(mlib.P4, 4)
for d in range(2, 7):
    cw = C.cable(mlib.P4, d)
    img = mlib.artin(cw, 4 * d)

    def Y(k, d=d):
        return [(d * k + d - 1 - i, 1) for i in range(d)]           # reverse-order product x_(dk+d-1) ... x_(dk)
    good = 0
    for j in range(4):
        W, g = conj[j]
        assert g == j
        Wy = mlib.subst(W, lambda kk: Y(kk))
        for i in range(d):
            q = d * j + i
            expect = mlib.red(Wy + [(q, 1)] + mlib.inv(Wy))
            good += int(mlib.red(img[q]) == expect)
    rows6.append({"d": d, "bundle strands conjugated correctly": f"{good}/{4 * d}"})
    ok &= good == 4 * d
report("6 cable lemma", ok, rows6)


# ---------------------------------------------------------------- 7 edge weight counts
def edge_counts(L, R_chars, p, d):
    """U = odd components of layers 1-2 at characters R; s* runs over duals of odd layer-3/4 components at R; returns
    (best count, |U|) where count = #{(pi2, pi3) : <[., [pi2, pi3]], s*> == 0}"""
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
            v = L.br(np.repeat(E[i:i + 1], len(pairs), axis=0), B)[:, o] % p
            zero &= v == 0
        cnt = int(zero.sum())
        if cnt < p ** (2 * len(U)) and (best is None or cnt < best[0]):
            best = (cnt, o)
    return best, len(U)


ok, rows7 = True, []
for (p, d, aname, kind) in [(7, 3, "four-way", "amphichiral"), (13, 4, "four-way", "cable"), (7, 6, "four-way", "cable"),
                            (11, 5, "four-way", "amphichiral"), (5, 4, "layer4", "cable"), (7, 3, "layer4", "amphichiral")]:
    zeta = root_of_unity(p, d)
    L = gd.four_way(p, d, 1) if aname == "four-way" else gd.layer4_algebra(p, d, 1)
    if kind == "amphichiral":
        R = {1, d - 1}
    else:
        k = next(k for k in range(1, d) if pow(zeta, k, p) == p - 1)
        R = {c for c in range(1, d) if pow(zeta, c * k, p) == p - 1}
    best, dimU = edge_counts(L, R, p, d)
    if best is None:
        rows7.append({"p": p, "d": d, "algebra": aname, "summand": kind, "nonzero trilinear form": False}); ok = False; continue
    cnt, o = best
    f0 = p ** (3 * dimU)                                       # per unit of |U'|^3
    fd = p ** dimU * cnt
    rows7.append({"p": p, "d": d, "algebra": aname, "summand": kind, "dim U": dimU, "s* component": L.names[o],
                  "f(0)/|U'|^3": f0, "f(0,s*)/|U'|^3": fd, "0 < f(0,s*) < f(0)": 0 < fd < f0})
    ok &= 0 < fd < f0
report("7 edge weight", ok, rows7)

# ---------------------------------------------------------------- 8 gadget replication
ok, rows8 = True, []
rng = np.random.default_rng(8)
for (p, d, summ, name) in [(7, 3, gd.AMPH["6_3"], "6_3"), (13, 4, gd.torus_cable(13, 2), "(2,1)-cable of T(2,13)")]:
    zeta = root_of_unity(p, d)
    word, n, events, vstr, pb = gd.build_gadget(2, [(0, 1)], d, summ, summ)
    for aname in ("four-way", "layer4"):
        L = gd.four_way(p, d, 1) if aname == "four-way" else gd.layer4_algebra(p, d, 1)
        A = BraidAlg(L, zeta)
        Mo = CyclicBraidModel(word, n, A, p)
        odd = [k for k in range(L.D) if L.chars[k] % d]
        inputs = {k: (rng.integers(0, p, (8, len(Mo.cocycles[int(L.chars[k])]))) @ Mo.cocycles[int(L.chars[k])]) % p
                  for k in odd if L.layer[k] <= 3}
        data = {k: v for k, v in inputs.items() if L.layer[k] <= 2}
        match, nonzero = True, 0
        for comp in [k for k in odd if L.layer[k] >= 3]:
            s = (rng.integers(0, p, (8, len(Mo.cocycles[(-int(L.chars[comp])) % d]))) @ Mo.cocycles[(-int(L.chars[comp])) % d]) % p
            Qm, okm, _, _ = gd.measure_Q(Mo, inputs, int(L.layer[comp]), comp, s)
            Qp = gd.predict_Q(L, A, word, n, events, data, s, comp, p)
            match &= bool((Qm[okm] == Qp[okm]).all()); nonzero += int((Qm != 0).sum())
        rows8.append({"p": p, "d": d, "summand": name, "algebra": aname, "gadget K2 crossings": len(word), "match": match,
                      "nonzero samples": nonzero})
        ok &= match and nonzero > 0
report("8 gadget replication", ok, rows8)

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "COPRIME-DICHOTOMY-20261027-001C-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out,
                   "seconds": round(time.time() - T_START, 1)}, fh, indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T_START, 1), "s")
