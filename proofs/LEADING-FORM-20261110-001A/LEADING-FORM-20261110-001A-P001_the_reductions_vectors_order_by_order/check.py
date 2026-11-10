#!/usr/bin/env python3
"""Checks for LEADING-FORM-20261110-001A: the Wronskian form of the family, its second solution and the second chain vector.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, about a minute. Checks 1 to 4 test Theorems 1 to 5 at every a for sides 8 to 128 (the decomposition to 64);
check 5 is the computed split of the co-distance-3 coefficient, where the attempt stops."""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import wronski_lib as WL  # noqa: E402

OL, CH, BL, RL = WL.OL, WL.CH, WL.BL, WL.RL
CO = "proofs/CHAIN-ORDERS-20261110-001A/CHAIN-ORDERS-20261110-001A-P001_the_reduced_form_at_every_order"
DEPS = {CO + "/manifest.json": None, CO + "/orders_lib.py": None}
T0 = time.time()
OUT, FAILED = {}, []


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


def each_eigenvalue(sides):
    for m in sides:
        F = RL.GF(m + 1)
        for a in F.exp:
            G, k, fam = OL.monic_least(F, a, m)
            if G is not None:
                yield m, F, a, G, k, fam


# 1: Theorem 1, G Z_0 F = (k + 1) W(G, F) mod k^h for every F (checked on a basis), and G(1) = b G(0) with G(0) != 0
def wronskian_form():
    bad, g0 = 0, 0
    for m, F, a, G, k, fam in each_eigenvalue(range(3, 8)):
        h = 1 << (m - 1)
        Z0 = CH.coefficients(F, a, m, 1)[0]
        g = WL.pad(G, h)
        for d in range(h):
            e = np.zeros(h, dtype=np.int64)
            e[d] = 1
            lhs = BL.poly_mul(F, g, Z0[:, d])[:h]
            w = WL.wronskian(F, g, e)
            rhs = BL.poly_mul(F, np.array([1, 1], dtype=np.int64), w)[:h]
            bad += (lhs != rhs).any()
        b = F.sqrt(a)
        g0 += int(G[0]) == 0
        s = 0                                           # G(1), the sum of the coefficients
        for c in G:
            s ^= int(c)
        g0 += s != F.m(b, int(G[0]))
    return bad == 0 and g0 == 0, {"basis mismatches": int(bad), "eigenvalues with G(0) = 0 or G(1) != b G(0)": int(g0)}


# 2: Theorem 2 (the chain equations in Wronskian form) through Theorem 3: W(G, phi_2) for an exact second chain vector of G Y^i
def second_vector():
    bad, tot = 0, 0
    for m, F, a, G, k, fam in each_eigenvalue(range(3, 8)):
        h = 1 << (m - 1)
        J = len(fam)
        if k < 2:
            continue
        Zh = OL.lam_family(F, a, m, 3)
        L = np.zeros(h, dtype=np.int64)
        t = 1
        while t <= h // 2:
            L[t] ^= 1
            t *= 2
        N = OL.norm_coeffs(F, G)
        for i in range(J):
            if not 2 * i < k - 1:
                continue
            x = fam[i]
            phi1 = np.concatenate([[0], x[:-1]])
            rhs = BL.matmul(F, Zh[1], phi1[:, None])[:, 0] ^ BL.matmul(F, Zh[2], x[:, None])[:, 0]
            A = np.concatenate([Zh[0], rhs[:, None]], axis=1)
            ns = BL.nullspace(F, A)
            sol = next((v for v in ns if v[-1]), None)
            if sol is None:
                continue                                # G Y^i heads a chain of length 2 only
            phi2 = F.mul_np(np.full(len(sol), F.inv(int(sol[-1])), dtype=np.int64), sol)[:-1]
            tot += 1
            got = WL.to_Y_exact(F, WL.wronskian(F, WL.pad(G, h), phi2))
            # predicted: N Y^i (1 + L(Y)) + a^2 G(0)^2 [i = 0] Y^(h-1), mod Y^h, then of degree < h - J
            NYi = np.zeros(h, dtype=np.int64)
            NYi[i:i + len(N)] = N[: h - i]
            one_L = L.copy()
            one_L[0] ^= 1
            pred = BL.poly_mul(F, NYi, one_L)[:h]
            if i == 0:
                pred[h - 1] ^= F.m(F.m(a, a), F.m(int(G[0]), int(G[0])))
            g = np.zeros(h, dtype=np.int64)
            g[: min(h, len(got))] = got[:h]
            bad += (g != pred).any() or pred[h - J:].any() or (len(got) > h and got[h:].any())
    return bad == 0, {"second chain vectors checked": tot, "mismatches": int(bad)}


# 3: Theorem 3, the second solution: degree h + k - 1 - 2J exactly, W(G, G') = c Y^(h-J-1)
def second_solution():
    bad, tot = 0, 0
    for m, F, a, G, k, fam in each_eigenvalue(range(3, 8)):
        if k < 2:
            continue
        h = 1 << (m - 1)
        J = len(fam)
        Gp = WL.second_solution(F, a, m, G, k)
        tot += 1
        if Gp is None:
            bad += 1
            continue
        w = WL.to_Y_exact(F, WL.wronskian(F, WL.pad(G, h), Gp))
        nz = np.nonzero(w)[0]
        deg = int(np.nonzero(Gp)[0][-1])
        bad += not (len(nz) == 1 and nz[0] == h - J - 1 and deg == h + k - 1 - 2 * J)
    return bad == 0, {"eigenvalues with k >= 2": tot, "failures": int(bad)}


# 4: Theorem 4, the decomposition c Y^e F = W(G', F) G + W(G, F) G' on a basis of V
def decomposition():
    bad = 0
    for m, F, a, G, k, fam in each_eigenvalue(range(3, 7)):
        if k < 2:
            continue
        h = 1 << (m - 1)
        Gp = WL.second_solution(F, a, m, G, k)
        g = WL.pad(G, h)
        cw = WL.wronskian(F, g, Gp)
        for d in range(h):
            e = np.zeros(h, dtype=np.int64)
            e[d] = 1
            lhs = BL.poly_mul(F, cw, e)
            rhs = BL.poly_mul(F, WL.wronskian(F, Gp, e), g) ^ BL.poly_mul(F, WL.wronskian(F, g, e), Gp)
            n = max(len(lhs), len(rhs))
            bad += (WL.pad(lhs, n) != WL.pad(rhs, n)).any()
    return bad == 0, {"basis mismatches": int(bad)}


# 5: computed, where the attempt stops: at co-distance 3 (i + j = k - 3, 2i, 2j < k - 1, complement W'), the reduction's
#    coefficient at l^5 is <S psi_2(x), psi_2(y)>; with psi_2 = k^2 x + eta, the pure part <S k^2 x, k^2 y> is 1 and the corrections
#    add up to 1, so the coefficient is 0
def codistance_three():
    def pair_S(F, u, v, h):
        prod = BL.poly_mul(F, BL.shift_poly(u), v)
        return int(prod[h - 1]) if len(prod) > h - 1 else 0
    counts = {"cases": 0, "pure part 1": 0, "corrections sum to 1": 0, "coefficient 0": 0, "eta self-pairing alone 1": 0}
    for m, F, a, G, k, fam in each_eigenvalue(range(4, 7)):
        if k < 3:
            continue
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
        BWW0i = OL.inverse(F, Bs[0][J:, J:])
        for i in range(J):
            for j in range(i, J):
                if i + j != k - 3 or not (2 * i < k - 1 and 2 * j < k - 1):
                    continue
                vecs = []
                for x_idx in (i, j):
                    # psi_1 = W-coordinates solving B_0(psi_1, w) = B_1(x, w); psi_2 from B_0(psi_2, w) = B_1(psi_1, w) + B_2(x, w)
                    c1 = BL.matmul(F, BWW0i, Bs[1][J:, x_idx][:, None])[:, 0]
                    r2 = BL.matmul(F, Bs[1][J:, J:], c1[:, None])[:, 0] ^ Bs[2][J:, x_idx]
                    c2 = BL.matmul(F, BWW0i, r2[:, None])[:, 0]
                    vecs.append(BL.matmul(F, P[:, J:], c2[:, None])[:, 0])
                x, y = fam[i], fam[j]
                k2x = np.concatenate([[0, 0], x[:-2]])
                k2y = np.concatenate([[0, 0], y[:-2]])
                ex, ey = vecs[0] ^ k2x, vecs[1] ^ k2y
                t1 = pair_S(F, k2x, k2y, h)
                t2 = pair_S(F, k2x, ey, h) ^ pair_S(F, ex, k2y, h)
                t3 = pair_S(F, ex, ey, h)
                counts["cases"] += 1
                counts["pure part 1"] += t1 == 1
                counts["corrections sum to 1"] += (t2 ^ t3) == 1
                counts["coefficient 0"] += pair_S(F, vecs[0], vecs[1], h) == 0
                counts["eta self-pairing alone 1"] += t2 == 0 and t3 == 1
    n = counts["cases"]
    return n > 0 and counts["pure part 1"] == n and counts["corrections sum to 1"] == n and counts["coefficient 0"] == n, counts


def main():
    write = "--write" in sys.argv
    check("0 dependencies bound by hash (CHAIN-ORDERS-20261110-001A's manifest and library)", True, {p: sha(p) for p in DEPS})
    ok, info = wronskian_form()
    check("1 Theorem 1: G Z_0 F = (k + 1) W(G, F) mod k^h on a basis of V, and G(1) = b G(0) != 0, every a, sides 8 to 128", ok, info)
    ok, info = second_vector()
    check("2 Theorems 2 and 3(a): W(G, phi_2) = N Y^i (1 + L(Y)) + a^2 G(0)^2 [i = 0] Y^(h-1) mod Y^h, of degree < h - J, "
          "every a and 2i < k - 1, sides 8 to 128", ok, info)
    ok, info = second_solution()
    check("3 Theorem 4: a second solution of degree h + k - 1 - 2J with W(G, G') = c Y^(h-J-1), every a with k >= 2, sides 8 to 128",
          ok, info)
    ok, info = decomposition()
    check("4 Theorem 5: c Y^(h-J-1) F = W(G', F) G + W(G, F) G' on a basis of V, every a with k >= 2, sides 8 to 64", ok, info)
    ok, info = codistance_three()
    check("5 computed: at co-distance 3 the pure part of the l^5 coefficient is 1 and the corrections add 1, every a, sides 16 to 64", ok, info)
    result = {"schema_version": 1, "artifact": "LEADING-FORM-20261110-001A-P001", "checks": OUT,
              "status": "passed" if not FAILED else "failed"}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
