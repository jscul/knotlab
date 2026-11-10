#!/usr/bin/env python3
"""Checks for JORDAN-CHAINS-20261110-001A: the Jordan chains that one polynomial heads, on the cut-open torus at sides 2^m.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, about a minute. Checks 1 to 4 test Theorems 1 to 3 and the lemma; check 5 is the computed chain lemma at sides 8 to 32;
check 6 reads the registered side-64 run (side64.json, JORDAN-CHAINS-A1) and check 7 the stress run (stress_test.json, JORDAN-CHAINS-S1),
both beside the decision note."""
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
import chains_lib as CH  # noqa: E402

BL, RL = CH.BL, CH.RL
D = RL.D
T0 = time.time()
OUT = {}
KB = "proofs/KLOOSTERMAN-BOUNDS-20261110-001A/KLOOSTERMAN-BOUNDS-20261110-001A-P001_one_polynomial_per_eigenvalue"
DEPS = {KB + "/manifest.json": "93183701f227f000d1efc31c867ad6bff717369712ed2594a635c6727b6f430a", KB + "/bounds_lib.py": None}
STRESS = ROOT / "research/JORDAN-CHAINS-20261110-001/stress_test.json"
SIDE64 = ROOT / "research/JORDAN-CHAINS-20261110-001/side64.json"
FAILED = []
FIELDS = {}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


def field(K):
    if K not in FIELDS:
        FIELDS[K] = RL.GF(K)
    return FIELDS[K]


# 1: Theorem 1: det Z(w) = w^(h(1-n)) det(I + C_s(w)) (at random points of GF(2^16)), Z(a) = X_b, and the Taylor coefficients
def family():
    info = {}
    E = field(16)
    rng = random.Random(1)
    for m in (2, 3, 4):
        n, h = 1 << m, 1 << (m - 1)
        T = D.T_matrix(h)
        S = RL.star_matrix(E, 0, m, h)
        bad = 0
        for _ in range(6):
            w = E.exp[rng.randrange(E.q1)]
            c = E.inv(E.m(w, w))
            wn1 = E.pw(w, n + 1)
            lhs_m = np.array([[E.m(wn1, E.ev([(x >> i) & 1 for i in range(x.bit_length())], c)) ^ (1 if i == j else 0)
                               for j, x in enumerate(row)] for i, row in enumerate(T)], dtype=np.int64)
            om = [0] * h
            for e, d in CH.exponents(m):
                om[e] ^= E.pw(w, d % E.q1)
            Z = S ^ CH.mult(om, h)
            dz, dc = det(E, Z), det(E, lhs_m)
            bad += dz != E.m(E.pw(w, (h * (1 - n)) % E.q1), dc)
        info["det identity, side %d" % n] = {"points": 6, "mismatches": bad}
    for m in range(2, 7):
        n, h = 1 << m, 1 << (m - 1)
        F = field(m + 1)
        bad0, badT = 0, 0
        for a in F.exp:
            Zs = CH.coefficients(F, a, m, 6)
            bad0 += not np.array_equal(Zs[0], RL.star_matrix(F, F.sqrt(a), m, h))
            oms = CH.taylor(F, a, m, 6)
            # Omega(a + delta) = (a + delta) Phi(a^2 + delta^2): odd coefficients are a^-1 times the even ones
            badT += any(oms[2 * i + 1] != [F.m(F.inv(a), x) for x in oms[2 * i]] for i in range(3))
            badT += not taylor_direct(F, a, m, 6, oms)
        info["side %d" % n] = {"Z(a) != X_b": bad0, "Taylor mismatches": badT}
    ok = all(v.get("mismatches", 0) == 0 and v.get("Z(a) != X_b", 0) == 0 and v.get("Taylor mismatches", 0) == 0 for v in info.values())
    return ok, info


def det(F, M):
    A = np.array(M, dtype=np.int64)
    n = A.shape[0]
    d = 1
    for c in range(n):
        nz = np.nonzero(A[c:, c])[0]
        if len(nz) == 0:
            return 0
        p = c + nz[0]
        if p != c:
            A[[c, p]] = A[[p, c]]
        d = F.m(d, int(A[c, c]))
        iv = F.inv(int(A[c, c]))
        rows = np.nonzero(A[c + 1:, c])[0] + c + 1
        if len(rows):
            f = F.mul_np(A[rows, c], np.full(len(rows), iv, dtype=np.int64))
            A[rows] ^= F.mul_np(f[:, None], A[c][None, :])
    return d


def taylor_direct(F, a, m, L, oms):
    """the Taylor coefficients of w^d at a from the series (1 + x)^d, x = delta/a, against the closed form"""
    for e, d in CH.exponents(m):
        r = -d
        base = [1 if D.binom_odd(r, i) else 0 for i in range(L)]
        inv = [0] * L
        inv[0] = 1
        for i in range(1, L):
            s = 0
            for j in range(1, i + 1):
                if base[j]:
                    s ^= inv[i - j]
            inv[i] = s
        for i in range(L):
            coef = F.pw(a, (d - i) % F.q1) if inv[i] else 0   # a^d (x)^i with x = delta/a
            if oms[i][e] != coef:
                return False
    return True


# 2: Theorem 2: every Taylor coefficient is self-adjoint for <F, G>
def self_adjoint():
    info = {}
    for m in range(2, 6):
        n, h = 1 << m, 1 << (m - 1)
        F = field(m + 1)
        Gam = BL.gram(h)
        bad = 0
        for a in F.exp:
            for Zi in CH.coefficients(F, a, m, 6):
                bad += not np.array_equal(BL.matmul(F, Gam, Zi), BL.matmul(F, Zi.T, Gam))
        info[n] = {"non-self-adjoint coefficients": bad}
    return all(v["non-self-adjoint coefficients"] == 0 for v in info.values()), info


# 3: Theorem 3: <Z_1 G Y^i, G Y^j> = a^-1 [Y^(h-1-i-j)] N(G), N(G) = G(k) G(k + 1), and exactly k mod 2 blocks of size 1
def size_one_blocks():
    info = {}
    for m in range(3, 7):
        n, h = 1 << m, 1 << (m - 1)
        F = field(m + 1)
        bad_h, bad_b = 0, 0
        for a in F.exp:
            ker, G = CH.least_polynomial(F, RL.star_matrix(F, F.sqrt(a), m, h))
            if G is None:
                continue
            k = h - (len(G) - 1)
            NG = BL.poly_mul(F, G, BL.shift_poly(G))
            NY = in_Y(F, NG)
            Zs = CH.coefficients(F, a, m, 2)
            fam = CH.cyclic_basis(G, h)
            Gam = BL.gram(h)
            for i, u in enumerate(fam):
                Zu = BL.matmul(F, Zs[1], u[:, None])[:, 0]
                for j, v in enumerate(fam):
                    val = pair(F, Gam, Zu, v)
                    idx = h - 1 - i - j
                    want = F.m(F.inv(a), int(NY[idx])) if 0 <= idx < len(NY) else 0
                    bad_h += val != want
            blocks = CH.partial_multiplicities(F, CH.coefficients(F, a, m, 3), 2)
            bad_b += blocks.count(1) != k % 2
        info[n] = {"first-order form mismatches": bad_h, "size-1 block count != k mod 2": bad_b}
    return all(v["first-order form mismatches"] == 0 and v["size-1 block count != k mod 2"] == 0 for v in info.values()), info


def pair(F, Gam, u, v):
    """<u, v> = u^T Gamma v over GF(2^K)"""
    s = 0
    Gv = BL.matmul(F, Gam, v[:, None])[:, 0]
    for x, y in zip(u, Gv):
        if x and y:
            s ^= F.m(int(x), int(y))
    return s


def in_Y(F, p):
    """a tau-invariant polynomial p(k) as a list of coefficients in Y = k^2 + k"""
    p = [int(x) for x in p]
    deg = max((i for i, x in enumerate(p) if x), default=-1)
    out = [0] * (deg // 2 + 1)
    Ypow = [[1]]
    for _ in range(deg // 2 + 1):
        Ypow.append([int(x) for x in BL.times_Y(np.array(Ypow[-1], dtype=np.int64))])
    while deg >= 0:
        assert deg % 2 == 0
        j, c = deg // 2, p[deg]
        out[j] = c
        for i, x in enumerate(Ypow[j]):
            if x:
                p[i] ^= F.m(c, x)
        deg = max((i for i, x in enumerate(p) if x), default=-1)
    return out


# 4: the lemma: phi_1 = a^-1 k G Y^i solves Z_0 phi_1 = Z_1 G Y^i when 2i < k - 1
def first_step():
    info = {}
    for m in range(3, 7):
        n, h = 1 << m, 1 << (m - 1)
        F = field(m + 1)
        bad, tried = 0, 0
        for a in F.exp:
            ker, G = CH.least_polynomial(F, RL.star_matrix(F, F.sqrt(a), m, h))
            if G is None:
                continue
            k = h - (len(G) - 1)
            Zs = CH.coefficients(F, a, m, 2)
            for i, u in enumerate(CH.cyclic_basis(G, h)):
                if 2 * i >= k - 1:
                    continue
                ku = np.concatenate([[0], u[:-1]])
                phi = F.mul_np(np.full(h, F.inv(a), dtype=np.int64), ku)
                bad += not np.array_equal(BL.matmul(F, Zs[0], phi[:, None])[:, 0], BL.matmul(F, Zs[1], u[:, None])[:, 0])
                tried += 1
        info[n] = {"cases": tried, "mismatches": bad}
    return all(v["mismatches"] == 0 for v in info.values()), info


# 5: computed: the chain lemma, every a, sides 8 to 32 (side 64: the registered run, check 6)
def chain_lemma():
    info = {}
    for m in range(3, 6):
        F = field(m + 1)
        bad, by_k = 0, {}
        for a in F.exp:
            r = CH.chain_lemma_at(F, a, m)
            bad += not r["ok"]
            by_k[r["k"]] = by_k.get(r["k"], 0) + 1
        info[1 << m] = {"values of a": F.q1, "failures": bad, "counts by k": by_k}
    return all(v["failures"] == 0 for v in info.values()), info


def main():
    write = "--write" in sys.argv
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash (KLOOSTERMAN-BOUNDS-20261110-001A's manifest and library)",
          all(v is None or deps[p] == v for p, v in DEPS.items()), deps)
    for name, fn in (("1 Theorem 1: det Z(w) = w^(h(1-n)) det(I + C_s(w)) (sides 4 to 16, random points of GF(2^16)), Z(a) = X_b and the Taylor "
                      "coefficients (sides 4 to 64)", family),
                     ("2 Theorem 2: every Taylor coefficient of Z at a is self-adjoint for <F, G>, sides 4 to 32", self_adjoint),
                     ("3 Theorem 3: <Z_1 G Y^i, G Y^j> = a^-1 [Y^(h-1-i-j)] N(G), and k mod 2 blocks of size 1, every a, sides 8 to 64", size_one_blocks),
                     ("4 Lemma: phi_1 = a^-1 k G Y^i solves Z_0 phi_1 = Z_1 G Y^i when 2i < k - 1, every a, sides 8 to 64", first_step),
                     ("5 computed: G Y^j heads a chain of exactly 2k - 1 - 4j and these are the Jordan blocks, every a, sides 8 to 32", chain_lemma)):
        ok, info = fn()
        check(name, ok, info)
    for name, path, run in (("6 the chain lemma at every a, side 64 (side64.json)", SIDE64, "JORDAN-CHAINS-A1"),
                            ("7 the stress run at side 128 (stress_test.json)", STRESS, "JORDAN-CHAINS-S1")):
        s = json.loads(path.read_text()) if path.exists() else None
        if s is not None and s.get("pass") is not None:
            check(name, s["pass"] is True, s)
        else:
            OUT[name] = {"pass": None, "info": "pending (%s)" % run}
            print("PENDING " + name, flush=True)
    res = {"ticket": "JORDAN-CHAINS-20261110-001A", "artifact_id": "JORDAN-CHAINS-20261110-001A-P001", "checks": OUT,
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
