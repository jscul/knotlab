#!/usr/bin/env python3
"""Checks for RETURN-DIGITS-20261109-001A: the return map of the cut-open torus at n = 2^m as a one-dimensional operator, its
reversal, the spectrum without the reversal, the digit recursion and the linearized form of the cone polynomial.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, about two minutes. Checks 1 to 5 test the theorems on small cases; check 6 is a computation; check 7 reads the stress
run (stress_test.json beside the decision note)."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import digits_lib as D  # noqa: E402

CL = D.CL
T0 = time.time()
OUT = {}
CONE = "proofs/CONE-COLLAPSE-20261109-001A/CONE-COLLAPSE-20261109-001A-P001_the_cone_and_its_return_map"
DEPS = {
    CONE + "/manifest.json": "220ceb6c18c74cf54ff51f53bca81468bd38d0512836a37a34e63d06f621d273",
    CONE + "/collapse_lib.py": "43d32af505197d097bf5de21b03dd30140f75a8e9c12d16f0b9580d11b44fc18",
}
STRESS = ROOT / "research/RETURN-DIGITS-20261109-001/stress_test.json"
FAILED = []


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


def model_Cs(n):
    """w^(n+1) T_h(w^-2) as GF(2)[w] ints"""
    h = n // 2
    T = D.T_matrix(h)
    out = [[0] * h for _ in range(h)]
    for i in range(h):
        for k in range(h):
            x = T[i][k]
            for j in range(x.bit_length()):
                if (x >> j) & 1:
                    out[i][k] ^= 1 << (n + 1 - 2 * j)
    return out


# 1: the one-dimensional model against the torus
def one_dim():
    info = {}
    for n in (4, 8, 16, 32):
        info[n] = CL.return_map(n)["Cs"] == model_Cs(n)
    return all(info.values()), info


# 2: the reversal is multiplication by eps = W_(h-1) = 1 + sum_j K^(h - h/2^j), eps^2 = 1
def reversal_is_eps():
    info = {}
    for h in (1, 2, 4, 8, 16, 32, 64):
        m = (2 * h).bit_length() - 1
        e = D.eps_poly(h)
        form = 1 + sum(1 << (h - h // (1 << j)) for j in range(1, m))
        ok = e == form and D.mulmod(e, e, h) == 1
        ok &= all(D.mulmod(e, D.W_poly(k), h) == D.W_poly(h - 1 - k) for k in range(h))
        info[h] = ok
    return all(info.values()), info


# 3: det(zI + S_h(c)) = c^h (1 + L_m(z/c))
def s_spectrum():
    info = {}
    for h in (1, 2, 4, 8, 16, 32):
        m = (2 * h).bit_length() - 1
        e = D.charpoly_symbolic(D.S_matrix(h))
        want = [0] * (h + 1)     # c^h + sum_(j<m) c^(h - 2^j) z^(2^j); the j = m - 1 term is z^h
        want[h] = 1 << h
        for j in range(m):
            want[h - (1 << j)] ^= 1 << (h - (1 << j))
        info[h] = e == want
    return all(info.values()), info


# 4: the digit recursion, and the quadratic form of its characteristic polynomial
def recursion():
    info = {}

    def add(*Ms):
        out = [r[:] for r in Ms[0]]
        for M in Ms[1:]:
            for i in range(len(out)):
                for j in range(len(out[0])):
                    out[i][j] ^= M[i][j]
        return out

    def scal(p, M):
        return [[D.pmul(p, x) for x in r] for r in M]

    def unit(h, i, j):
        M = [[0] * h for _ in range(h)]
        M[i][j] = 1
        return M

    ok_rec = True
    for h in (1, 2, 4, 8, 16):
        A, T2 = D.T_matrix(h), D.T_matrix(2 * h)
        R = D.reversal(h)
        I = [[1 if i == j else 0 for j in range(h)] for i in range(h)]
        Z = [[0] * h for _ in range(h)]
        p = 1 << h
        AR = CL.pmat_mul(A, R)
        TL, TR = CL.pmat_mul(A, add(R, scal(p, I))), scal(p, AR)
        BL = add(A, scal(p, unit(h, 0, 0)), unit(h, 0, h - 1))
        BR = add(AR, scal(p, unit(h, 0, h - 1)))
        Tk = [TL[i] + TR[i] for i in range(h)] + [BL[i] + BR[i] for i in range(h)]
        P = [I[i] + R[i] for i in range(h)] + [Z[i] + I[i] for i in range(h)]
        info["T_%d from T_%d" % (2 * h, h)] = CL.pmat_mul(CL.pmat_mul(P, Tk), P) == T2
        ok_rec &= info["T_%d from T_%d" % (2 * h, h)]
    # quadratic form, exact for h <= 4 (Laplace expansion of polynomial matrices in z with GF(2)[c] coefficients)

    def bmul(a, b):
        out = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y:
                        out[i + j] ^= D.pmul(x, y)
        return out

    def badd(a, b):
        L = max(len(a), len(b))
        return [(a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0) for i in range(L)]

    def bdet(M):
        if len(M) == 1:
            return M[0][0]
        tot = [0]
        for j in range(len(M)):
            if any(M[0][j]):
                tot = badd(tot, bmul(M[0][j], bdet([r[:j] + r[j + 1:] for r in M[1:]])))
        return tot

    def trim(a):
        while len(a) > 1 and a[-1] == 0:
            a = a[:-1]
        return a
    ok_q = True
    for h in (1, 2, 4):
        S = D.S_matrix(h)
        R = D.reversal(h)
        MS = CL.pmat_mul(R, S)
        S2 = CL.pmat_mul(S, S)
        p = 1 << h
        Q = [[[S2[i][j], D.pmul(p, MS[i][j] ^ (1 if (i == 0 and j == h - 1) else 0)), 1 if i == j else 0]
              for j in range(h)] for i in range(h)]
        e = CL.charpoly_berkowitz(D.T_matrix(2 * h))
        same = trim(bdet(Q)) == trim([e[2 * h - i] for i in range(2 * h + 1)])
        info["det(zI + T_%d) = det(z^2 + S^2 + c^h z (MS + E)), h = %d" % (2 * h, h)] = same
        ok_q &= same
    return ok_rec and ok_q, info


def cone_poly(n):
    """det(I - mu A_cone) as a GF(2)[mu] int"""
    if n <= 16:
        Ac = CL.cone(n)[2]
        cp = CL.charpoly(Ac)
        return CL.prev(cp, CL.pdeg(cp))
    return CL.cone_polynomial(n, CL.cone_spectrum(n))


# 5: the linearized form det(sum_i mu^(2^i) C_i) = mu^h det(I - mu A_cone)
def linearized(polys):
    info = {}
    for m in (2, 3, 4, 5):
        h, n = 1 << (m - 1), 1 << m
        d = CL.bareiss_det(D.linearized_matrix(m))
        info[n] = d == (polys[n] << h)
    return all(info.values()), info


# 6: computed: (1 + Tr_(GF(2n)))(mu) divides det(I - mu A_cone) exactly once, with a square quotient
def trace_factor(polys):
    info = {}
    for m in (2, 3, 4, 5):
        n = 1 << m
        f = D.trace_poly(m + 1) ^ 1
        q, r = D.pdivmod(polys[n], f)
        q2, r2 = D.pdivmod(q, f)
        square = CL.deriv(q) == 0
        info[n] = {"divides": r == 0, "exactly once": r2 != 0, "quotient a square": square}
    ok = all(v["divides"] and v["exactly once"] and v["quotient a square"] for v in info.values())
    return ok, info


def main():
    write = "--write" in sys.argv
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash (CONE-COLLAPSE-20261109-001A's manifest and library)", deps == DEPS, deps)
    ok, info = one_dim()
    check("1 Theorem 1: the return map C_s of the torus equals w^(n+1) T_h(w^-2), sides 4 to 32", ok, info)
    ok, info = reversal_is_eps()
    check("2 Theorem 2: the reversal is multiplication by eps = W_(h-1) = 1 + sum_j K^(h - h/2^j), eps^2 = 1, h = 1 to 64", ok, info)
    ok, info = s_spectrum()
    check("3 Theorem 3: det(zI + S_h(c)) = c^h (1 + L_m(z/c)), h = 1 to 32", ok, info)
    ok, info = recursion()
    check("4 Theorem 4: T_2h from T_h by the digit recursion (h = 1 to 16), and det(zI + T_2h) = det(z^2 + S_h^2 + "
          "c^h z (M S_h + E)) (h = 1 to 4)", ok, info)
    polys = {n: cone_poly(n) for n in (4, 8, 16, 32)}
    ok, info = linearized(polys)
    check("5 Theorem 5: det(mu S^-1 + sum_(i=1..m) mu^(2^i) N^(h - 2^(i-1))) = mu^h det(I - mu A_cone), sides 4 to 32", ok, info)
    ok, info = trace_factor(polys)
    check("6 computed: 1 + Tr_(GF(2n))(mu) divides det(I - mu A_cone) exactly once and the quotient is a square, sides 4 to 32",
          ok, info)
    s = json.loads(STRESS.read_text()) if STRESS.exists() else None
    if s is not None and s.get("pass") is not None:
        check("7 the stress run (stress_test.json)", s["pass"] is True, s)
    else:
        OUT["7 the stress run (stress_test.json)"] = {"pass": None, "info": "pending (RETURN-DIGITS-S1)"}
        print("PENDING 7 the stress run", flush=True)
    res = {"ticket": "RETURN-DIGITS-20261109-001A", "artifact_id": "RETURN-DIGITS-20261109-001A-P001", "checks": OUT,
           "status": "passed" if not FAILED else "failed"}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("result.json matches a fresh run:", same)
        if not same:
            sys.exit(1)
    if FAILED:
        sys.exit(1)


if __name__ == "__main__":
    main()
