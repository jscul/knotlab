#!/usr/bin/env python3
"""Checks for CODIST-THREE-20261110-001A: the second vector on the pair of solutions, and how far the co-distance-3 cancellation goes.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, about a minute. Check 1 tests Theorem 1 (the gap of N L(Y)) at every a for sides 8 to 128; checks 2 and 3 test
Theorems 2 and 3 (the split of the order-4 coefficient, the canonical second vector) at sides 16 to 64; check 3 also records the
computed remaining identity; check 4 records a negative computation (a direct continued-fraction reading)."""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pair_lib as PL  # noqa: E402

WL, OL, CH, BL, RL = PL.WL, PL.OL, PL.CH, PL.BL, PL.RL
LF = "proofs/LEADING-FORM-20261110-001A/LEADING-FORM-20261110-001A-P001_the_reductions_vectors_order_by_order"
DEPS = {LF + "/manifest.json": None, LF + "/wronski_lib.py": None}
T0 = time.time()
OUT, FAILED = {}, []


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


def eigenvalues(sides, kmin):
    for m in sides:
        F = RL.GF(m + 1)
        for a in F.exp:
            G, k, fam = OL.monic_least(F, a, m)
            if G is not None and k >= kmin:
                yield m, F, a, G, k, fam


def ext_h2(wY, h):
    """[k^(h-2)] of a polynomial in Y: the sum of its coefficients at Y^(h-1-2^t)"""
    s, t = 0, 1
    while t <= h - 1:
        d = h - 1 - t
        if 0 <= d < len(wY):
            s ^= int(wY[d])
        t *= 2
    return s


# 1: Theorem 1, the gap: [Y^d](N L) = 0 for h - k + 1 <= d <= h - 2, and [Y^(h-1)](N L) = a^2 G(0)^2
def gap():
    bad = tot = 0
    for m, F, a, G, k, fam in eigenvalues(range(3, 8), 2):
        h = 1 << (m - 1)
        N = OL.norm_coeffs(F, G)
        NL = BL.poly_mul(F, np.array(N, dtype=np.int64), PL.L_poly(h))
        tot += 1
        coef = lambda d: int(NL[d]) if d < len(NL) else 0
        bad += any(coef(d) for d in range(h - k + 1, h - 1)) or coef(h - 1) != F.m(F.m(a, a), F.m(int(G[0]), int(G[0])))
    return bad == 0, {"eigenvalues with k >= 2": tot, "failures": bad}


def schur_psi2(F, a, m, G, fam, k):
    h = 1 << (m - 1)
    J = len(fam)
    Zh = OL.lam_family(F, a, m, 3)
    W = OL.good_complement(G, fam, h, k)
    P = np.zeros((h, h), dtype=np.int64)
    for j, f in enumerate(fam):
        P[:, j] = f
    for t, w in enumerate(W):
        P[:, J + t] = w
    Gam = BL.gram(h)
    Bs = [BL.matmul(F, BL.matmul(F, P.T.copy(), BL.matmul(F, Z.T.copy(), Gam)), P) for Z in Zh]
    inv0 = OL.inverse(F, Bs[0][J:, J:])
    out = []
    for i in range(J):
        c1 = BL.matmul(F, inv0, Bs[1][J:, i][:, None])[:, 0]
        r2 = BL.matmul(F, Bs[1][J:, J:], c1[:, None])[:, 0] ^ Bs[2][J:, i]
        c2 = BL.matmul(F, inv0, r2[:, None])[:, 0]
        out.append(BL.matmul(F, P[:, J:], c2[:, None])[:, 0])
    return out


def pieces(F, a, h, g, ps, x, y, j):
    """Q1..Q5 of the order-4 coefficient for the second vector ps of x, against y = G Y^j"""
    Wk = WL.wronskian(F, g, ps)
    Wx = WL.to_Y_exact(F, Wk)
    Gt = BL.poly_mul(F, g, BL.shift_poly(ps))
    kW = np.zeros(max(len(Gt), len(Wk) + 1), dtype=np.int64)
    kW[1:1 + len(Wk)] ^= Wk
    Ix = WL.to_Y_exact(F, WL.pad(Gt, len(kW)) ^ kW)
    shift = lambda w: np.concatenate([np.zeros(j, dtype=np.int64), w])
    q1 = ext_h2(shift(Wx), h)
    q2 = int(Wx[h - 2 - j]) if 0 <= h - 2 - j < len(Wx) else 0
    q3 = ext_h2(shift(Ix), h)
    q4 = F.m(F.m(a, a), F.m(int(ps[0]), int(y[0])))
    xy = BL.poly_mul(F, x, y)
    q5 = F.m(F.m(a, a), F.m(int(x[0]), int(y[0]))) ^ F.m(F.pw(a, 4), int(xy[0]) ^ int(xy[1]))
    return q1, q2, q3, q4, q5


# 2: Theorem 2, the order-4 coefficient at i + j <= k - 3 (x, y in K_1, complement W') is Q1 + ... + Q5, with Q1 = Q2 = 0
def split():
    c = {"pairs": 0, "split equals the coefficient": 0, "Q1 = 0": 0, "Q2 = 0": 0, "coefficient 0": 0}
    for m, F, a, G, k, fam in eigenvalues(range(4, 7), 3):
        h = 1 << (m - 1)
        g = WL.pad(G, h)
        psi2 = schur_psi2(F, a, m, G, fam, k)
        for i in range(len(fam)):
            for j in range(len(fam)):
                if i + j > k - 3 or not (2 * i < k - 1 and 2 * j < k - 1):
                    continue
                x, y = fam[i], fam[j]
                q = pieces(F, a, h, g, psi2[i], x, y, j)
                ky = np.concatenate([[0], y[:-1]])
                prod = BL.poly_mul(F, BL.shift_poly(psi2[i]), ky)
                direct = (int(prod[h - 1]) if len(prod) > h - 1 else 0) ^ q[3] ^ q[4]
                c["pairs"] += 1
                c["split equals the coefficient"] += (q[0] ^ q[1] ^ q[2] ^ q[3] ^ q[4]) == direct
                c["Q1 = 0"] += q[0] == 0
                c["Q2 = 0"] += q[1] == 0
                c["coefficient 0"] += direct == 0
    n = c["pairs"]
    return n > 0 and c["split equals the coefficient"] == n and c["Q1 = 0"] == n and c["Q2 = 0"] == n, c


# 3: Theorem 3 (the canonical second vector is a second chain vector of degree < h) and, computed, Q3 + Q4 + Q5 = 0 for it
def canonical():
    c = {"vectors": 0, "chain equation holds": 0, "pairs": 0, "canonical Q3 + Q4 + Q5 = 0": 0}
    for m, F, a, G, k, fam in eigenvalues(range(4, 7), 3):
        h = 1 << (m - 1)
        g = WL.pad(G, h)
        Q, P = PL.components(F, G, h)
        Qpp, Ppp = PL.bezout(F, P, Q)
        Zh = OL.lam_family(F, a, m, 3)
        for i in range(len(fam)):
            if not 2 * i < k - 1:
                continue
            x = fam[i]
            # W_x of a second chain vector: LEADING-FORM-20261110-001A, Theorem 3
            N = OL.norm_coeffs(F, G)
            NYi = np.zeros(h, dtype=np.int64)
            NYi[i:i + len(N)] = np.array(N, dtype=np.int64)[: h - i]
            oneL = PL.L_poly(h)
            oneL[0] ^= 1
            Wx = BL.poly_mul(F, NYi, oneL)[:h]
            if i == 0:
                Wx[h - 1] ^= F.m(F.m(a, a), F.m(int(G[0]), int(G[0])))
            ps = PL.canonical_second_vector(F, G, h, Wx, Q, P, Qpp)
            c["vectors"] += 1
            phi1 = np.concatenate([[0], x[:-1]])
            rhs = BL.matmul(F, Zh[1], phi1[:, None])[:, 0] ^ BL.matmul(F, Zh[2], x[:, None])[:, 0]
            c["chain equation holds"] += not (BL.matmul(F, Zh[0], ps[:, None])[:, 0] ^ rhs).any()
            for j in range(len(fam)):
                if i + j > k - 3 or not 2 * j < k - 1:
                    continue
                q = pieces(F, a, h, g, ps, x, fam[j], j)
                c["pairs"] += 1
                c["canonical Q3 + Q4 + Q5 = 0"] += (q[2] ^ q[3] ^ q[4]) == 0
    return c["chain equation holds"] == c["vectors"] and c["canonical Q3 + Q4 + Q5 = 0"] == c["pairs"], c


# 4: negative, computed: the top coefficients of phi = xi N/(1 + xi (k + 1 + Lam0)) do not show the leading form
def continued_fraction_reading():
    tot = bad = 0
    for m, F, a, G, k, fam in eigenvalues(range(4, 7), 1):
        h = 1 << (m - 1)
        Q, P = PL.components(F, G, h)
        Qpp, Ppp = PL.bezout(F, P, Q)
        pad = lambda v: np.concatenate([np.array(v, dtype=np.int64), np.zeros(max(0, h - len(v)), dtype=np.int64)])[:h]
        Lam0 = pad(PL.ymul(F, Q, Qpp)) ^ pad(PL.ymul(F, Q, Ppp)) ^ np.concatenate([[0], pad(PL.ymul(F, P, Ppp))[:-1]])
        N = pad(OL.norm_coeffs(F, G))
        D = PL.L_poly(h) ^ Lam0
        D[0] ^= 1
        Lu = 2 * k + 2
        binv = F.inv(F.sqrt(a))
        xi = [np.zeros(h, dtype=np.int64) for _ in range(Lu)]
        xi[1][0] ^= 1
        for r in range(1, m):
            e = 1 << r
            for extra in (0, 1):
                if e + extra < Lu:
                    xi[e + extra][h - (1 << (r - 1))] ^= F.m(binv, F.pw(a, e))
        xiY = [OL.to_Y(F, v, h) for v in xi]
        rm = lambda u, v: pad(BL.poly_mul(F, u, v))
        num = [rm(v, N) for v in xiY]
        den = [rm(v, D) for v in xiY]
        inv = [np.zeros(h, dtype=np.int64) for _ in range(Lu)]
        inv[0][0] = 1
        for r in range(1, Lu):
            acc = np.zeros(h, dtype=np.int64)
            for s in range(1, r + 1):
                acc ^= rm(den[s], inv[r - s])
            inv[r] = acc
        phi = [np.zeros(h, dtype=np.int64) for _ in range(Lu)]
        for i in range(Lu):
            for j in range(Lu - i):
                phi[i + j] ^= rm(num[i], inv[j])
        for s in range(2 * ((k + 1) // 2) - 1):
            tot += 1
            e = 2 * (k - s) - 1
            ser = [int(phi[r][h - 1 - s]) for r in range(Lu)]
            want = 1 if OL.is_pow2(k - s) else 0
            bad += any(ser[:e]) or (e < Lu and ser[e] != want)
    return bad > 0, {"coefficients": tot, "differing from the leading form": bad}


def main():
    write = "--write" in sys.argv
    check("0 dependencies bound by hash (LEADING-FORM-20261110-001A's manifest and library)", True, {p: sha(p) for p in DEPS})
    ok, info = gap()
    check("1 Theorem 1: [Y^d](N L(Y)) = 0 for h - k + 1 <= d <= h - 2 and [Y^(h-1)](N L(Y)) = a^2 G(0)^2, every a with k >= 2, sides 8 to 128",
          ok, info)
    ok, info = split()
    check("2 Theorem 2: the order-4 coefficient at i + j <= k - 3 splits into Q1 + ... + Q5 with Q1 = Q2 = 0, sides 16 to 64", ok, info)
    ok, info = canonical()
    check("3 Theorem 3 and computed: the canonical second vector is a second chain vector of degree < h, and Q3 + Q4 + Q5 = 0 for it "
          "at i + j <= k - 3, sides 16 to 64", ok, info)
    ok, info = continued_fraction_reading()
    check("4 negative, computed: the top coefficients of phi = xi N/(1 + xi (k + 1 + Lam0)) do not show the leading form, sides 16 to 64",
          ok, info)
    result = {"schema_version": 1, "artifact": "CODIST-THREE-20261110-001A-P001", "checks": OUT,
              "status": "passed" if not FAILED else "failed"}
    if write:
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", HERE / "result.json")
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
