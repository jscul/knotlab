#!/usr/bin/env python3
"""Checks for FULL-REACH-PROOF-20261108-001A: the cut-open torus walk, its symmetries, the torus it comes from, and what is special
at powers of two.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. Checks 1 to 8 test proved statements on small sides; checks 9 to 11 are computations (exact), and
check 12 reads the stress run (stress_test.json beside the decision note), sides to 64."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import reach_lib as R  # noqa: E402

T0 = time.time()
OUT = {}
DEPS = {
    "experiments/FULL-REACH-20261108-001A/FULL-REACH-20261108-001A-E001_cut_open_tori/contract.json":
        "00f5970f8969d383af0d457dfe85502bd48194d3ac730727f55212ad42780c10",
}
STRESS = ROOT / "research/FULL-REACH-PROOF-20261108-001/stress_test.json"
FAILED = []


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


def is_pow2(n):
    return n & (n - 1) == 0


# 1-3: the draft's lemmas
def draft_lemmas():
    ok1 = ok2 = ok3 = True
    for n in range(2, 13):
        P, ix, A = R.box(n)
        N = len(P)
        PA = R.perm_matrix(P, ix, lambda p: (p[0], 2 * n - 2 - p[1]))
        At = R.transpose(A, N)
        ok1 &= R.mat_mul(R.mat_mul(PA, A), PA) == At
        ok2 &= all(R.layer(q) == (R.layer(p) + 1) % 4 for p in P for q in R.reads(n, p))
    for n in range(2, 17):
        P, ix, A = R.box(n)
        ok3 &= R.rank(A) == len(P)
    return ok1, ok2, ok3


# 4: A + A^T = T (x) T on the contacts
def sum_is_product():
    bad = []
    for n in range(2, 17):
        P, ix, A = R.box(n)
        N = len(P)
        At = R.transpose(A, N)
        TT = [sum(1 << ix[q] for q in ((p[0] + a, p[1] + b) for a in (-1, 1) for b in (-1, 1)) if q in ix) for p in P]
        if [a ^ b for a, b in zip(A, At)] != TT:
            bad.append(n)
    return bad


# 5: the quarter turn commutes; the mirror P and the diagonal reflection D transpose; so PA and DA are symmetric
def symmetries():
    bad = []
    for n in range(2, 17):
        P, ix, A = R.box(n)
        N, M = len(P), 2 * n - 2
        At = R.transpose(A, N)
        rho = R.perm_matrix(P, ix, lambda p: (p[1], M - p[0]))
        Pm = R.perm_matrix(P, ix, lambda p: (p[0], M - p[1]))
        Dg = R.perm_matrix(P, ix, lambda p: (p[1], p[0]))
        ok = (R.mat_mul(rho, A) == R.mat_mul(A, rho) and R.mat_mul(R.mat_mul(Pm, A), Pm) == At
              and R.mat_mul(R.mat_mul(Dg, A), Dg) == At)
        PA, DA = R.mat_mul(Pm, A), R.mat_mul(Dg, A)
        ok &= R.transpose(PA, N) == PA and R.transpose(DA, N) == DA
        if not ok:
            bad.append(n)
    return bad


# 6: A is the principal submatrix of the side-2n torus walk on all contacts but the two cut lines
def principal():
    bad = []
    for n in range(2, 13):
        T, tix, M = R.torus(n)
        P, ix, A = R.box(n)
        for k, p in enumerate(P):
            r = M[tix[p]]
            sub = sum(1 << kk for kk, q in enumerate(P) if (r >> tix[q]) & 1)
            if sub != A[k]:
                bad.append(n)
                break
    return bad


# 7: at sides 2^m the torus walk dies in n steps; its Green's function on a cut line is the circle's; det(I - wA) = det R_CC(w)
def torus_at_powers_of_two():
    info = {}
    ok = True
    for n in (2, 4, 8, 16):
        T, tix, M = R.torus(n)
        Nt = len(T)
        Mn = R.mat_pow(M, n)
        Mn1 = R.mat_pow(M, n - 1)
        dies = all(r == 0 for r in Mn) and any(Mn1)
        Ch, Cv = R.cut_lines(n)
        C = Ch + Cv
        Rcc = R.resolvent_block(M, tix, C, 2 * n)
        # 1D Green's function on a circle of n points: (1 + w^2 (s + 1/s))^-1 = sum_{k < n/2} w^{2k} (s + 1/s)^k
        circ = [0] * n   # coefficient polys by offset
        powk = [0] * n
        powk[0] = 1
        for k in range(n // 2):
            for o in range(n):
                if powk[o]:
                    circ[o] ^= 1 << (2 * k)
            nxt = [0] * n
            for o in range(n):
                if powk[o]:
                    nxt[(o + 1) % n] ^= 1
                    nxt[(o - 1) % n] ^= 1
            powk = nxt
        line_ok = all(Rcc[a][b] == circ[(b - a) % n] for a in range(n) for b in range(n)) and \
            all(Rcc[n + a][n + b] == circ[(b - a) % n] for a in range(n) for b in range(n))
        rec = {"M^n = 0, M^(n-1) != 0": dies, "cut-line blocks are the circle's Green's function": line_ok}
        if n <= 8:
            P, ix, A = R.box(n)
            N = len(P)
            chi = R.charpoly(A, N)
            d = R.poly_det(Rcc)
            rec["det R_CC(w) = det(I - wA) (reversed characteristic polynomial)"] = d == R.prev(chi, N)
            rec["degree"] = R.pdeg(d)
        ok &= all(v for k, v in rec.items() if k != "degree")
        info[n] = rec
    return ok, info


# 8: det(xI - M_h) = det(u_n(y) + u_{n-1}(y) L + R u_{n-1}(y) + R u_{n-2}(y) L), y = xI + T_{n-1}, for every n
def transfer_identity():
    bad = []
    for n in range(2, 9):
        pts, hix, Mh = R.h_grid_walk(n)
        chi = R.charpoly(Mh, len(pts))
        s = n - 1
        Lm = [[1 if j == i - 1 else 0 for j in range(s)] for i in range(s)]
        Rm = [[1 if j == i + 1 else 0 for j in range(s)] for i in range(s)]
        y = [[(0b10 if i == j else 0) ^ (1 if abs(i - j) == 1 else 0) for j in range(s)] for i in range(s)]
        us = R.chebyshev(n, y, s)   # u_0 .. u_n
        Phi = R.madd(R.madd(us[n], R.mmul(us[n - 1], Lm)), R.madd(R.mmul(Rm, us[n - 1]), R.mmul(R.mmul(Rm, us[n - 2]), Lm)))
        if R.poly_det(Phi) != chi:
            bad.append(n)
    return bad


# 9: at which sides is every eigenvalue a (2n - 1)-th root of unity? (exact at the powers of two; a lower bound elsewhere suffices)
def collapse(sides):
    out = {}
    for n in sides:
        Q = R.layer_Q(n)
        D = len(Q)
        rng = random.Random(n)
        m = 1
        for _ in range(4):
            m = R.plcm(m, R.minpoly_vec(Q, rng.getrandbits(D)))
        M = 2 * n - 1
        kk = next((k for k in range(14) if R.ppowmod(2, M * (1 << k), m) == 1), None)
        rec = {"layer dimension": D, "roots of unity of order dividing 2n - 1 (lower bound)": kk is not None}
        if kk is not None:
            Qn = np.zeros((D, D), dtype=np.float32)
            for i, r in enumerate(Q):
                for j in range(D):
                    if (r >> j) & 1:
                        Qn[i, j] = 1
            e = None
            for k in range(kk, 14):
                Rk, B, t = np.eye(D, dtype=np.float32), Qn.copy(), M * (1 << k)
                while t:
                    if t & 1:
                        Rk = np.mod(Rk @ B, 2)
                    B = np.mod(B @ B, 2)
                    t >>= 1
                if np.array_equal(Rk, np.eye(D, dtype=np.float32)):
                    e = 4 * (1 << k)
                    break
            rec["least power of two e with A^(e(2n - 1)) = I (exact)"] = e
        out[n] = rec
    return out


# 10: Jordan structure of Q = A^4 on a layer at the powers of two: multiplicities k(k + 1)/2 with geometric multiplicity 2k - 1
def jordan(n):
    Q = R.layer_Q(n)
    D = len(Q)
    rng = random.Random(7)
    m = 1
    for _ in range(6):
        m = R.plcm(m, R.minpoly_vec(Q, rng.getrandbits(D)))
    res, total = [], 0
    for p in R.factor(m):
        # p(Q) as rows
        PQ = [0] * D
        Pw = R.identity(D)
        i = 0
        while p >> i:
            if (p >> i) & 1:
                PQ = [a ^ b for a, b in zip(PQ, Pw)]
            Pw = R.mat_mul(Pw, Q)
            i += 1
        dims, Pk = [], R.identity(D)
        while True:
            Pk = R.mat_mul(Pk, PQ)
            d = D - R.rank(Pk)
            if dims and d == dims[-1]:
                break
            dims.append(d)
        dp = R.pdeg(p)
        res.append({"degree": dp, "algebraic": dims[-1] // dp, "geometric": dims[0] // dp,
                    "kernel dimensions": [d // dp for d in dims]})
        total += dims[-1]
    tri = all(any(r["algebraic"] == k * (k + 1) // 2 and r["geometric"] == 2 * k - 1 for k in range(1, 60)) for r in res)
    return {"layer dimension": D, "accounted": total, "triangular with geometric 2k - 1": tri, "classes": res}


# 13: Proposition 6's hypothesis (an irreducible layer polynomial of full degree) holds at sides 3, 5, 7, 11 and no other to 24
def irreducible_layers(sides):
    out = {}
    for n in sides:
        Q = R.layer_Q(n)
        D = len(Q)
        rng = random.Random(n)
        m = 1
        for _ in range(3):
            m = R.plcm(m, R.minpoly_vec(Q, rng.getrandbits(D)))
        fac = R.factor(m)
        # a found divisor of full degree D is the characteristic polynomial; one of lower degree rules out irreducibility,
        # since then every nonzero vector would have minimal polynomial of degree D
        out[n] = {"layer dimension": D, "degree found": R.pdeg(m), "factor degrees": sorted(R.pdeg(p) for p in fac),
                  "irreducible of full degree": R.pdeg(m) == D and len(fac) == 1 and set(fac.values()) == {1}}
    return out


# 11: ring-level reach at 8 and 16 (the failing set) and the contact level
def predicted(n):
    out = set()
    for k in range(1, n // 4):
        for X, Y in ((4 * k, 4 * k - 1), (4 * k - 1, 2 * n - 2 - 4 * k)):
            out |= {(X, Y), (2 * n - 2 - X, 2 * n - 2 - Y)}
    return out


def reach_census(n):
    P, ix, A = R.box(n)
    rings = {(i, j): sum(1 << ix[q] for q in R.ring(n, i, j)) for i in range(n) for j in range(n)}
    full = (1 << len(P)) - 1
    short, fail = 0, {}
    for k, p in enumerate(P):
        row, union, basis = 1 << k, 0, {}
        while True:
            x = row
            while x and (x.bit_length() - 1) in basis:
                x ^= basis[x.bit_length() - 1]
            if not x:
                break
            basis[x.bit_length() - 1] = x
            union |= row
            row = R.vec_mat(row, A)
        short += union != full
        miss = sorted(r for r, msk in rings.items() if not msk & union)
        if miss:
            fail[p] = miss
    return short, fail


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependency bound by hash (FULL-REACH-20261108-001A's frozen contract)", all(DEPS[p] == deps[p] for p in DEPS), deps)
    ok1, ok2, ok3 = draft_lemmas()
    check("1 Lemma 1: A^T = PAP for the mirror P(X, Y) = (X, 2n - 2 - Y), sides 2 to 12", ok1)
    check("2 Lemma 2: every read goes from layer r to layer r + 1, sides 2 to 12", ok2)
    check("3 Lemma 3: A is invertible over GF(2), sides 2 to 16", ok3)
    b = sum_is_product()
    check("4 Theorem 1: A + A^T = T (x) T on the contacts (T the null-boundary path walk on 2n - 1 sites), sides 2 to 16", not b, b)
    b = symmetries()
    check("5 Theorem 2: the quarter turn commutes with A; the mirror and the diagonal reflection carry A to A^T; PA and DA are "
          "symmetric, sides 2 to 16", not b, b)
    b = principal()
    check("6 Theorem 3: A is the principal submatrix of the side-2n torus walk on all contacts but the two cut lines, sides 2 to 12",
          not b, b)
    ok, info = torus_at_powers_of_two()
    check("7 Theorem 4: at sides 2, 4, 8, 16 the torus walk satisfies M^n = 0 (not M^(n-1)); its Green's function on each cut line "
          "is the circle's; det(I - wA) = det R_CC(w) at 2, 4, 8", ok, info)
    b = transfer_identity()
    check("8 Theorem 5: det(xI - A^2 on h) = det(u_n(y) + u_(n-1)(y) L + R u_(n-1)(y) + R u_(n-2)(y) L), y = xI + T_(n-1), sides 2 "
          "to 8", not b, b)
    col = collapse(range(3, 25))
    roots = [n for n, r in col.items() if r["roots of unity of order dividing 2n - 1 (lower bound)"]]
    exact = {n: col[n].get("least power of two e with A^(e(2n - 1)) = I (exact)") for n in roots}
    check("9 Computed: every eigenvalue of A is a (2n - 1)-th root of unity at sides 4, 8, 16 and at no other side from 3 to 24; "
          "A^(e(2n - 1)) = I with e = 4, 8, 16", roots == [4, 8, 16] and exact == {4: 4, 8: 8, 16: 16}, {"sides": roots, "e": exact})
    jd = {n: jordan(n) for n in (4, 8, 16)}
    check("10 Computed: at sides 4, 8, 16 every eigenvalue of A^4 on a layer has algebraic multiplicity k(k + 1)/2 and geometric "
          "multiplicity 2k - 1 for some k", all(j["triangular with geometric 2k - 1"] and j["accounted"] == j["layer dimension"]
                                                for j in jd.values()), jd)
    cen = {}
    for n in (8, 16):
        short, fail = reach_census(n)
        cen[n] = {"contacts missing some contact": short, "failing set = predicted": set(fail) == predicted(n),
                  "each misses three rings": all(len(v) == 3 for v in fail.values())}
    check("11 Computed: at 8 and 16 the contacts missing a ring are exactly the predicted n - 4, each missing three rings; 44 and "
          "68 contacts miss some contact", all(c["failing set = predicted"] and c["each misses three rings"] for c in cen.values())
          and cen[8]["contacts missing some contact"] == 44 and cen[16]["contacts missing some contact"] == 68, cen)
    irr = irreducible_layers(range(3, 25))
    check("13 Proposition 6: the layer polynomial is irreducible of full degree at sides 3, 5, 7, 11 and at no other side from 3 to "
          "24, so there every contact reads every contact", [n for n, r in irr.items() if r["irreducible of full degree"]] == [3, 5, 7, 11],
          irr)
    if STRESS.is_file():
        st = json.loads(STRESS.read_text())
        stages = {k: st[k]["pass"] for k in ("collapse", "jordan", "census") if k in st}
        check("12 Stress run (stress_test.json), the stages completed: sides 3 to 64, every eigenvalue a (2n - 1)-th root of unity "
              "exactly at 4, 8, 16, 32, 64; the k(k + 1)/2 multiplicities at 32 and 64; the ring census at 49, 50 and 64 (a stage not "
              "yet run is listed as pending)", all(v is True for v in stages.values()),
              {"stages": stages, "pending": [k for k in ("collapse", "jordan", "census") if k not in st],
               "collapse": {k: v for k, v in st.get("collapse", {}).items()}})
    result = {"ticket": "FULL-REACH-PROOF-20261108-001A", "artifact_id": "FULL-REACH-PROOF-20261108-001A-P001", "checks": OUT,
              "status": "passed" if not FAILED else "failed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
    elif path.is_file():
        old = json.loads(path.read_text())
        same = json.dumps(old["checks"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True)
        print("result.json matches a fresh run:", same)
    print("failed:", FAILED)
    return 0 if not FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
