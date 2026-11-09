#!/usr/bin/env python3
"""Stress test for RETURN-DIGITS-20261109-001, one size past each check of ticket A:
Theorem 1 at side 64 (ticket A: 4 to 32); Theorem 2 at h = 128 (to 64); Theorem 3 at h = 64 (to 32); Theorem 4's recursion
32 -> 64 (to 16 -> 32) and its determinant identity at h = 8 and 16 by evaluation at random points of GF(2^16) (exact to h = 4);
Theorem 5 at sides 64 and 128 (to 32), at 128 against the low part of the cone polynomial recorded by CONE-COLLAPSE-S1; the factor
1 + Tr_(GF(2n)) at 64 and 128 (to 32). Writes stress_test.json and stress_test_log.txt beside this file."""
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIB = ROOT / "proofs/RETURN-DIGITS-20261109-001A/RETURN-DIGITS-20261109-001A-P001_a_one_dimensional_return_map"
sys.path.insert(0, str(LIB))
import digits_lib as D  # noqa: E402
CL = D.CL
T0 = time.time()
LOG = HERE / "stress_test_log.txt"
CONE_S1 = ROOT / "research/CONE-COLLAPSE-20261109-001/stress_test.json"
RES = {}


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, "a") as f:
        f.write("[%6.0fs] %s\n" % (time.time() - T0, s))


def save(final=False):
    RES["seconds"] = round(time.time() - T0)
    if final:
        RES["pass"] = all(v.get("pass") for v in RES.values() if isinstance(v, dict))
    (HERE / "stress_test.json").write_text(json.dumps(RES, indent=1, default=str) + "\n")


def model_Cs(n):
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


class GF:
    def __init__(self, K):
        f, mul = CL.field(K)
        self.q = (1 << K) - 1
        self.exp = [1]
        for _ in range(self.q - 1):
            self.exp.append(mul(self.exp[-1], 2))
        self.log = {v: i for i, v in enumerate(self.exp)}

    def m(self, a, b):
        return 0 if a == 0 or b == 0 else self.exp[(self.log[a] + self.log[b]) % self.q]

    def inv(self, a):
        return self.exp[(-self.log[a]) % self.q]

    def pw(self, a, e):
        return 1 if e == 0 else (0 if a == 0 else self.exp[(self.log[a] * e) % self.q])

    def ev(self, poly, x):
        v = 0
        for i in range(poly.bit_length()):
            if (poly >> i) & 1:
                v ^= self.pw(x, i)
        return v

    def det(self, M):
        A = [r[:] for r in M]
        n = len(A)
        d = 1
        for c in range(n):
            p = next((i for i in range(c, n) if A[i][c]), None)
            if p is None:
                return 0
            A[c], A[p] = A[p], A[c]
            d = self.m(d, A[c][c])
            iv = self.inv(A[c][c])
            for i in range(c + 1, n):
                if A[i][c]:
                    f = self.m(A[i][c], iv)
                    A[i] = [x ^ self.m(f, y) for x, y in zip(A[i], A[c])]
        return d


def main():
    open(LOG, "w").close()
    # Theorem 1 at side 64
    ok = CL.return_map(64)["Cs"] == model_Cs(64)
    RES["Theorem 1 at side 64"] = {"pass": ok}
    log("Theorem 1 at 64:", ok)
    # Theorem 2 at h = 128
    h = 128
    m = (2 * h).bit_length() - 1
    e = D.eps_poly(h)
    ok = e == 1 + sum(1 << (h - h // (1 << j)) for j in range(1, m)) and D.mulmod(e, e, h) == 1
    ok &= all(D.mulmod(e, D.W_poly(k), h) == D.W_poly(h - 1 - k) for k in range(h))
    RES["Theorem 2 at h = 128"] = {"pass": ok}
    log("Theorem 2 at 128:", ok)
    save()
    # Theorem 3 at h = 64
    h = 64
    m = (2 * h).bit_length() - 1
    ech = D.charpoly_symbolic(D.S_matrix(h))
    want = [0] * (h + 1)
    want[h] = 1 << h
    for j in range(m):
        want[h - (1 << j)] ^= 1 << (h - (1 << j))
    RES["Theorem 3 at h = 64"] = {"pass": ech == want}
    log("Theorem 3 at 64:", ech == want)
    save()
    # Theorem 4: recursion 32 -> 64
    h = 32
    A, T2 = D.T_matrix(h), D.T_matrix(2 * h)
    R = D.reversal(h)
    I = [[1 if i == j else 0 for j in range(h)] for i in range(h)]
    Z = [[0] * h for _ in range(h)]
    p = 1 << h
    AR = CL.pmat_mul(A, R)

    def add(*Ms):
        out = [r[:] for r in Ms[0]]
        for M in Ms[1:]:
            for i in range(h):
                for j in range(h):
                    out[i][j] ^= M[i][j]
        return out

    def scal(pp, M):
        return [[D.pmul(pp, x) for x in r] for r in M]

    def unit(i, j):
        M = [[0] * h for _ in range(h)]
        M[i][j] = 1
        return M
    TL, TR = CL.pmat_mul(A, add(R, scal(p, I))), scal(p, AR)
    BL = add(A, scal(p, unit(0, 0)), unit(0, h - 1))
    BR = add(AR, scal(p, unit(0, h - 1)))
    Tk = [TL[i] + TR[i] for i in range(h)] + [BL[i] + BR[i] for i in range(h)]
    P = [I[i] + R[i] for i in range(h)] + [Z[i] + I[i] for i in range(h)]
    ok = CL.pmat_mul(CL.pmat_mul(P, Tk), P) == T2
    RES["Theorem 4 recursion 32 -> 64"] = {"pass": ok}
    log("Theorem 4 recursion 32 -> 64:", ok)
    save()
    # Theorem 4's determinant identity at h = 8 and 16, at 24 random points (c, z) of GF(2^16)
    F = GF(16)
    rng = random.Random(1)
    rec = {}
    for h in (8, 16):
        S = D.S_matrix(h)
        Rh = D.reversal(h)
        MS = CL.pmat_mul(Rh, S)
        S2 = CL.pmat_mul(S, S)
        T2 = D.T_matrix(2 * h)
        bad = 0
        for _ in range(24):
            c = F.exp[rng.randrange(F.q)]
            z = F.exp[rng.randrange(F.q)]
            ph = F.pw(c, h)
            lhs = F.det([[F.ev(T2[i][j], c) ^ (z if i == j else 0) for j in range(2 * h)] for i in range(2 * h)])
            Q = [[F.ev(S2[i][j], c) ^ F.m(F.m(ph, z), F.ev(MS[i][j], c) ^ (1 if (i == 0 and j == h - 1) else 0))
                  ^ (F.m(z, z) if i == j else 0) for j in range(h)] for i in range(h)]
            rhs = F.det(Q)
            bad += lhs != rhs
        rec[h] = {"points": 24, "mismatches": bad}
    RES["Theorem 4 determinant identity at h = 8, 16 (random points of GF(2^16))"] = {
        "pass": all(v["mismatches"] == 0 for v in rec.values()), "detail": rec}
    log("Theorem 4 identity at 8, 16:", rec)
    save()
    # Theorem 5 and the trace factor at 64 and 128
    P64 = CL.cone_polynomial(64, CL.cone_spectrum(64))
    log("cone polynomial at 64 assembled")
    for m in (6, 7):
        h, n = 1 << (m - 1), 1 << m
        t = time.time()
        d = CL.bareiss_det(D.linearized_matrix(m))
        v = D.val(d)
        Q = d >> v
        log("det of the linearized matrix at side %d: degree %d, mu^%d factor (%.0fs)" % (n, D.pdeg(d), v, time.time() - t))
        rec = {"mu-valuation": v, "degree of the rest": D.pdeg(Q)}
        if n == 64:
            rec["equals mu^h det(I - mu A_cone)"] = v == h and Q == P64
        else:
            low = json.loads(CONE_S1.read_text())["stages"]["1 collapse, traces, stability, return map"][
                "cone polynomial at 128 below degree 129"]
            lowpoly = sum(1 << i for i in low)
            rec["valuation h, degree n(n-1)/2"] = v == h and D.pdeg(Q) == n * (n - 1) // 2
            rec["agrees with CONE-COLLAPSE-S1's cone polynomial below degree 129"] = (Q & ((1 << 129) - 1)) == lowpoly
        f = D.trace_poly(m + 1) ^ 1
        q1, r1 = D.pdivmod(Q, f)
        q2, r2 = D.pdivmod(q1, f)
        rec["1 + Tr divides exactly once"] = r1 == 0 and r2 != 0
        rec["quotient a square"] = CL.deriv(q1) == 0
        rec["pass"] = all(x for k, x in rec.items() if isinstance(x, bool))
        RES["Theorem 5 and the trace factor at side %d" % n] = rec
        log("side", n, rec)
        save()
    save(final=True)
    log("done, pass", RES["pass"])


if __name__ == "__main__":
    main()
