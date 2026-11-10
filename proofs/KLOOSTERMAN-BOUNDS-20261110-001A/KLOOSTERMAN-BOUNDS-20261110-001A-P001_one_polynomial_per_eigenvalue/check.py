#!/usr/bin/env python3
"""Checks for KLOOSTERMAN-BOUNDS-20261110-001A: the kernels of the cut-open torus at sides 2^m, one polynomial per eigenvalue.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, under a minute. Checks 1 to 4 test Theorems 1 to 4 on finite cases; checks 5 and 6 are computations; check 7 reads the
stress run (stress_test.json beside the decision note)."""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import bounds_lib as BL  # noqa: E402

RL = BL.RL
T0 = time.time()
OUT = {}
LR = "proofs/LINEAR-ROOTS-20261109-001A/LINEAR-ROOTS-20261109-001A-P001_kloosterman_multiplicities"
DEPS = {
    LR + "/manifest.json": "32e65c9216407b424f49f2bd4bde5452c7df0711be93df8afc34073002253a74",
    LR + "/roots_lib.py": None,
}
STRESS = ROOT / "research/KLOOSTERMAN-BOUNDS-20261110-001/stress_test.json"
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


def side(m):
    return 1 << m, 1 << (m - 1), field(m + 1)


def in_kernel(F, X, v):
    return not BL.matmul(F, X, np.asarray(v, dtype=np.int64)[:, None]).any()


# 1: Theorem 1: the shift and the multiplications are self-adjoint for <F, G>: Gamma M = M^T Gamma
def self_adjoint():
    info = {}
    for m in range(2, 7):
        n, h, F = side(m)
        Gam = BL.gram(h)
        bad = 0
        for b in F.exp:
            X = RL.star_matrix(F, b, m, h)
            bad += not np.array_equal(BL.matmul(F, Gam, X), BL.matmul(F, X.T, Gam))
        S = RL.star_matrix(F, 0, m, h)            # Omega_0 = 0: the shift alone
        info[n] = {"values of b": F.q1, "X_b not self-adjoint": bad,
                   "shift self-adjoint": bool(np.array_equal(BL.matmul(F, Gam, S), BL.matmul(F, S.T, Gam)))}
    return all(v["X_b not self-adjoint"] == 0 and v["shift self-adjoint"] for v in info.values()), info


# 2: Theorem 2: any two solutions satisfy F_1(k) F_2(k + 1) = F_1(k + 1) F_2(k)
def wronskian():
    info = {}
    for m in range(3, 7):
        n, h, F = side(m)
        bad, pairs = 0, 0
        for b in F.exp:
            ker = BL.nullspace(F, RL.star_matrix(F, b, m, h))
            for i in range(len(ker)):
                for j in range(i + 1, len(ker)):
                    w = BL.poly_mul(F, ker[i], BL.shift_poly(ker[j])) ^ BL.poly_mul(F, ker[j], BL.shift_poly(ker[i]))
                    bad += bool(w.any())
                    pairs += 1
        info[n] = {"pairs": pairs, "nonzero Wronskians": bad}
    return all(v["nonzero Wronskians"] == 0 for v in info.values()), info


def structure(m):
    """for every b: kernel dim, deg G_b (least top degree), whether the top degrees are deg G + 2j and G Y^j are in the kernel,
    the valuations, and K(b)"""
    n, h, F = side(m)
    rows = []
    for b in F.exp:
        X = RL.star_matrix(F, b, m, h)
        ker = BL.nullspace(F, X)
        K = F.kloosterman(b)
        if not ker:
            rows.append({"dim": 0, "degG": None, "K": K, "cyclic": True, "vals": []})
            continue
        degs, ech = BL.top_degrees(F, ker)
        G = ech[-1][:degs[0] + 1]
        fam, v = [], G.copy()
        while len(v) - 1 < h:
            fam.append(np.concatenate([v, np.zeros(h - len(v), dtype=np.int64)]))
            v = BL.times_Y(v)
        cyclic = degs == [degs[0] + 2 * j for j in range(len(degs))] and len(fam) == len(ker) and all(in_kernel(F, X, f) for f in fam)
        rows.append({"dim": len(ker), "degG": degs[0], "K": K, "cyclic": cyclic, "vals": BL.low_degrees(F, ker)})
    return n, h, rows


STRUCT = {}


def struct(m):
    if m not in STRUCT:
        STRUCT[m] = structure(m)
    return STRUCT[m]


# 3: Theorem 3: the solutions are G_b r(Y) of degree below h, dim = ceil((h - deg G_b)/2)
def cyclic():
    info = {}
    for m in range(3, 8):
        n, h, rows = struct(m)
        bad = sum(1 for r in rows if r["dim"] and not (r["cyclic"] and r["dim"] == (h - r["degG"] + 1) // 2))
        info[n] = {"values of b": len(rows), "kernels not of the form G r(Y)": bad}
    return all(v["kernels not of the form G r(Y)"] == 0 for v in info.values()), info


# 4: Theorem 4: dim ker X_b = h/2 - rank T_b, T_b the Toeplitz matrix of the Pade series psi_b
def pade():
    info = {}
    for m in range(3, 7):
        n, h, F = side(m)
        bad = 0
        for b in F.exp:
            dim = h - F.rank(RL.star_matrix(F, b, m, h))
            T = BL.pade_toeplitz(BL.pade_series(F, b, m, h), h)
            bad += dim != h // 2 - F.rank(T)
        info[n] = {"values of b": F.q1, "mismatches": bad}
    return all(v["mismatches"] == 0 for v in info.values()), info


# 5: computed: deg G_b = h - k_b with k_b = (|K(b) - 1| - 1)/2, and the valuations are 0, ..., dim - 1, every b, sides 8 to 128
def degree_law():
    info = {}
    for m in range(3, 8):
        n, h, rows = struct(m)
        bad = sum(1 for r in rows if (r["dim"] and r["degG"] != h - BL.k_index(r["K"])) or (not r["dim"] and BL.k_index(r["K"]) != 0))
        badv = sum(1 for r in rows if r["vals"] != list(range(r["dim"])))
        info[n] = {"values of b": len(rows), "deg G_b != h - k_b": bad, "valuations not 0..dim-1": badv}
    return all(v["deg G_b != h - k_b"] == 0 and v["valuations not 0..dim-1"] == 0 for v in info.values()), info


# 6: computed: rank T_b equals the linear complexity of psi_1, ..., psi_(h-1), and both are h/2 - |K(b)|/4, sides 8 to 64
def complexity():
    info = {}
    for m in range(3, 7):
        n, h, F = side(m)
        bad = 0
        for b in F.exp:
            psi = BL.pade_series(F, b, m, h)
            T = BL.pade_toeplitz(psi, h)
            L = berlekamp_massey(F, psi[1:h])
            bad += not (F.rank(T) == L == h // 2 - abs(F.kloosterman(b)) // 4)
        info[n] = {"values of b": F.q1, "mismatches": bad}
    return all(v["mismatches"] == 0 for v in info.values()), info


def berlekamp_massey(F, s):
    C, B = [1], [1]
    L, mm, bb = 0, 1, 1
    for N in range(len(s)):
        d = s[N]
        for i in range(1, L + 1):
            if i < len(C):
                d ^= F.m(C[i], s[N - i])
        if d == 0:
            mm += 1
            continue
        coef = F.m(d, F.inv(bb))
        T = C[:]
        need = len(B) + mm
        if len(C) < need:
            C += [0] * (need - len(C))
        for i, x in enumerate(B):
            C[i + mm] ^= F.m(coef, x)
        if 2 * L <= N:
            L, B, bb, mm = N + 1 - L, T, d, 1
        else:
            mm += 1
    return L


def main():
    write = "--write" in sys.argv
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash (LINEAR-ROOTS-20261109-001A's manifest and library)",
          all(v is None or deps[p] == v for p, v in DEPS.items()), deps)
    for name, fn in (("1 Theorem 1: X_b and the shift are self-adjoint for <F, G> = sum_(j<h) [k^j](F G), every b, sides 4 to 64", self_adjoint),
                     ("2 Theorem 2: F_1(k) F_2(k + 1) = F_1(k + 1) F_2(k) for every pair of solutions, sides 8 to 64", wronskian),
                     ("3 Theorem 3: the solutions are G_b r(Y) of degree below h, dim = ceil((h - deg G_b)/2), every b, sides 8 to 128", cyclic),
                     ("4 Theorem 4: dim ker X_b = h/2 - rank T_b (the Pade form), every b, sides 8 to 64", pade),
                     ("5 computed: deg G_b = h - k_b and valuations 0, ..., dim - 1, every b, sides 8 to 128", degree_law),
                     ("6 computed: rank T_b = linear complexity of psi_b = h/2 - |K(b)|/4, every b, sides 8 to 64", complexity)):
        ok, info = fn()
        check(name, ok, info)
    s = json.loads(STRESS.read_text()) if STRESS.exists() else None
    if s is not None and s.get("pass") is not None:
        check("7 the stress run (stress_test.json)", s["pass"] is True, s)
    else:
        OUT["7 the stress run (stress_test.json)"] = {"pass": None, "info": "pending (KLOOSTERMAN-BOUNDS-S1)"}
        print("PENDING 7 the stress run", flush=True)
    res = {"ticket": "KLOOSTERMAN-BOUNDS-20261110-001A", "artifact_id": "KLOOSTERMAN-BOUNDS-20261110-001A-P001", "checks": OUT,
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
