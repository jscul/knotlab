#!/usr/bin/env python3
"""Checks for LINEAR-ROOTS-20261109-001A: Kloosterman multiplicities of the cut-open torus at sides n = 2^m.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. Checks 1 to 3 test Theorems 1 to 3 on finite cases; checks 4 to 8 are computations; check 9 reads the
stress run (stress_test.json beside the decision note)."""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import roots_lib as RL  # noqa: E402

D, CL = RL.D, RL.CL
T0 = time.time()
OUT = {}
RD = "proofs/RETURN-DIGITS-20261109-001A/RETURN-DIGITS-20261109-001A-P001_a_one_dimensional_return_map"
CC = "proofs/CONE-COLLAPSE-20261109-001A/CONE-COLLAPSE-20261109-001A-P001_the_cone_and_its_return_map"
FR = "proofs/FULL-REACH-PROOF-20261108-001A/FULL-REACH-PROOF-20261108-001A-P001_symmetries_the_torus_and_powers_of_two"
DEPS = {
    RD + "/manifest.json": "0604ca4e92ae7d1d958ad8e993b0bcc5f7850a9927efb73891df1d10dfa4e8bd",
    RD + "/digits_lib.py": None,
    CC + "/collapse_lib.py": "43d32af505197d097bf5de21b03dd30140f75a8e9c12d16f0b9580d11b44fc18",
    CC + "/result.json": None,
    "research/CONE-COLLAPSE-20261109-001/stress_test.json": None,
}
STRESS = ROOT / "research/LINEAR-ROOTS-20261109-001/stress_test.json"
FAILED = []


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


FIELDS = {}


def field(K):
    if K not in FIELDS:
        FIELDS[K] = RL.GF(K)
    return FIELDS[K]


def kl_table(F):
    return {a: F.kloosterman(a) for a in F.exp}


# 1: Theorem 1, the count: sum over a in GF(q)* of K(a)(K(a) - 2)/8 = q(q - 2)/8 = n(n - 1)/2, with K(a) = 0 mod 4
def count():
    info = {}
    for K in range(2, 10):
        F = field(K)
        q = 1 << K
        ks = kl_table(F)
        mod4 = all(v % 4 == 0 for v in ks.values())
        tot = sum(v * (v - 2) for v in ks.values())
        info[q] = {"K(a) = 0 mod 4": mod4, "sum K(K - 2)/8": tot // 8 if tot % 8 == 0 else tot / 8, "q(q - 2)/8": q * (q - 2) // 8}
        info[q]["pass"] = mod4 and tot == q * (q - 2)
    return all(v["pass"] for v in info.values()), info


# 2: Theorem 2: dim ker(I + C_s(a)) = dim of the solutions of (k + 1) F(k + 1) = Omega_b(k) F(k) mod k^h, b = sqrt(a)
def normalized_kernel():
    info = {}
    for m in (2, 3, 4, 5):
        n, h = 1 << m, 1 << (m - 1)
        F = field(m + 1)
        T = D.T_matrix(h)
        bad = 0
        for a in F.exp:
            d1 = RL.return_map_kernel_dim(F, a, n, T)
            d2 = h - F.rank(RL.star_matrix(F, F.sqrt(a), m, h))
            bad += d1 != d2
        info[n] = {"values of a": F.q1, "mismatches": bad}
    return all(v["mismatches"] == 0 for v in info.values()), info


# 3: Theorem 3: k^h Omega_b(k) = b^2 + sum_(i=0..m) b^(2^(i+2)) k^(2h - 2^i) (b in GF(q)), so Omega_b(y) = y^h Tr(b^4/y) + b^2/y^h on GF(q)*
def trace_form():
    info = {}
    for m in range(2, 9):
        n, h = 1 << m, 1 << (m - 1)
        F = field(m + 1)
        bad_poly = 0
        for b in F.exp:
            lhs = [0] * (3 * h)
            for d, c in enumerate(RL.omega(F, b, m, h)):
                lhs[d + h] ^= c
            rhs = [0] * (3 * h)
            rhs[0] ^= F.m(b, b)
            for i in range(m + 1):
                rhs[2 * h - (1 << i)] ^= F.pw(b, 1 << (i + 2))
            bad_poly += lhs != rhs
        bad_eval = 0
        if m <= 6:
            for b in F.exp:
                om = RL.omega(F, b, m, h)
                b4, b2 = F.pw(b, 4), F.m(b, b)
                for y in F.exp:
                    yh = F.pw(y, h)
                    bad_eval += F.ev(om, y) != ((yh if F.tr(F.m(b4, F.inv(y))) else 0) ^ F.m(b2, F.inv(yh)))
        info[n] = {"polynomial identity mismatches": bad_poly, "evaluation mismatches (sides to 64)": bad_eval}
    return all(v["polynomial identity mismatches"] == 0 and v["evaluation mismatches (sides to 64)"] == 0 for v in info.values()), info


# 4: computed: the geometric law, dim ker(I + C_s(a)) = |K(a)|/4 for every a in GF(2n)*, sides 4 to 128
def geometric_law():
    info = {}
    for m in range(2, 8):
        n, h = 1 << m, 1 << (m - 1)
        F = field(m + 1)
        ks = kl_table(F)
        bad = 0
        for a in F.exp:
            d = h - F.rank(RL.star_matrix(F, F.sqrt(a), m, h))
            bad += d != abs(ks[a]) // 4
        info[n] = {"values of a": F.q1, "mismatches": bad}
    return all(v["mismatches"] == 0 for v in info.values()), info


# 5: computed: the algebraic law and the Jordan blocks against CONE-COLLAPSE-20261109-001's class data, sides 4 to 128
def algebraic_law():
    info = {}
    res = json.loads((ROOT / CC / "result.json").read_text())
    c5 = next(v for k, v in res["checks"].items() if k.startswith("5"))["info"]
    for ns in ("4", "8", "16", "32", "64"):
        n = int(ns)
        F = field(n.bit_length())
        bad = 0
        for s, k in c5[ns]["classes (coset: k)"].items():
            Kmu = F.kloosterman(F.exp[(-int(s)) % F.q1])
            bad += RL.k_index(Kmu) != k
        info[n] = {"classes": len(c5[ns]["classes (coset: k)"]), "k mismatches": bad,
                   "Jordan blocks 2k - 1, 2k - 5, ... (CONE-COLLAPSE)": c5[ns]["Jordan blocks 2k - 1, 2k - 5, ..."]}
    st = json.loads((ROOT / "research/CONE-COLLAPSE-20261109-001/stress_test.json").read_text())
    F = field(8)
    classes = st["stages"]["2 multiplicities, parity and Jordan blocks"]["classes"]
    bad = 0
    for c in classes:
        Kmu = F.kloosterman(F.exp[(-c["coset"]) % F.q1])
        alg, geo, blocks = RL.law(Kmu)
        dims = [sum(min(j, b) for b in blocks) for j in range(1, (max(blocks) if blocks else 0) + 1)] or [0]
        bad += not (c["alg"] == alg and c["k"] == RL.k_index(Kmu) and c["kernel dims"] == dims)
    info[128] = {"classes": len(classes), "mismatches (multiplicity, k, kernel dims of m_s(A)^j)": bad}
    ok = all(v.get("k mismatches", v.get("mismatches (multiplicity, k, kernel dims of m_s(A)^j)")) == 0 for v in info.values())
    ok &= all(v.get("Jordan blocks 2k - 1, 2k - 5, ... (CONE-COLLAPSE)", True) for v in info.values())
    return ok, info


# 6: computed: the law's period, the least power of two e at least the largest Jordan block, against the computed periods
def period():
    computed = {4: 4, 8: 8, 16: 16, 32: 16, 64: 32, 128: 32}   # FULL-REACH-PROOF-20261108-001 (4 to 64), CONE-COLLAPSE-S1 (128)
    st = json.loads((ROOT / "research/CONE-COLLAPSE-20261109-001/stress_test.json").read_text())
    computed[128] = st["stages"]["1 collapse, traces, stability, return map"]["least e (power of two) with A_cone^(255 e) = I"]
    info = {}
    for n, e in computed.items():
        F = field(n.bit_length())
        top = max(max(RL.law(F.kloosterman(a))[2] or [0]) for a in F.exp)
        pred = 1
        while pred < top:
            pred *= 2
        info[n] = {"largest Jordan block": top, "predicted e": pred, "computed e": e}
    return all(v["predicted e"] == v["computed e"] for v in info.values()), info


# 7: computed: the eigenvalue 1 has multiplicity (t^2 - 1)/8, t = 1 - K(1) the trace of y^2 + xy = x^3 + 1 over GF(2^(m+1)),
#    t_1 = -1, t_2 = -3, t_(r+1) = -t_r - 2 t_(r-1); against the classes of coset 0 (checks 5)
def eigenvalue_one():
    t = {1: -1, 2: -3}
    for r in range(3, 10):
        t[r] = -t[r - 1] - 2 * t[r - 2]
    info = {}
    for m in range(2, 8):
        F = field(m + 1)
        K1 = F.kloosterman(1)
        info[1 << m] = {"K(1)": K1, "1 - t_(m+1)": 1 - t[m + 1], "multiplicity (t^2 - 1)/8": (t[m + 1] ** 2 - 1) // 8}
    return all(v["K(1)"] == v["1 - t_(m+1)"] for v in info.values()), info


# 8: computed: at the sides 3 to 20 that are not powers of two the cone's characteristic polynomial has an irreducible factor whose
#    degree does not divide the order of 2 mod 2n - 1
def not_powers_of_two():
    info = {}
    for n in range(3, 21):
        if n & (n - 1) == 0:
            continue
        q = 2 * n - 1
        d, x = 1, 2 % q
        while x != 1:
            x, d = (2 * x) % q, d + 1
        fac = CL.factor(CL.charpoly(CL.cone(n)[2]))
        degs = sorted({CL.pdeg(f) for f in fac})
        info[n] = {"order of 2 mod 2n - 1": d, "factor degrees": degs, "some degree not dividing it": any(d % g for g in degs)}
    return all(v["some degree not dividing it"] for v in info.values()), info


def main():
    write = "--write" in sys.argv
    deps = {p: sha(p) for p in DEPS}
    ok = all(v is None or deps[p] == v for p, v in DEPS.items())
    check("0 dependencies bound by hash (RETURN-DIGITS-20261109-001A, CONE-COLLAPSE-20261109-001A's library, result and stress data)", ok, deps)
    for name, fn in (("1 Theorem 1: sum over a in GF(q)* of K(a)(K(a) - 2)/8 = q(q - 2)/8 and K(a) = 0 mod 4, q = 4 to 512", count),
                     ("2 Theorem 2: dim ker(I + C_s(a)) = dim of the solutions of (k + 1) F(k + 1) = Omega_b(k) F(k) mod k^h, b^2 = a, "
                      "every a, sides 4 to 32", normalized_kernel),
                     ("3 Theorem 3: k^h Omega_b(k) = b^2 + sum_(i=0..m) b^(2^(i+2)) k^(2h - 2^i) for b in GF(2n) (sides 4 to 256), and "
                      "Omega_b(y) = y^h Tr(b^4/y) + b^2/y^h on GF(2n)* (sides 4 to 64)", trace_form),
                     ("4 computed: dim ker(I + C_s(a)) = |K(a)|/4 for every a in GF(2n)*, sides 4 to 128", geometric_law),
                     ("5 computed: algebraic multiplicity K(K - 2)/8 and Jordan blocks of the law, every class, sides 4 to 128 "
                      "(CONE-COLLAPSE-20261109-001's data)", algebraic_law),
                     ("6 computed: the law's period exponent (least power of two at least the largest block) equals the computed one, "
                      "sides 4 to 128", period),
                     ("7 computed: K(1) = 1 - t_(m+1) for the curve y^2 + xy = x^3 + 1, so the eigenvalue 1 has multiplicity "
                      "(t_(m+1)^2 - 1)/8, sides 4 to 128", eigenvalue_one),
                     ("8 computed: at sides 3 to 20 other than powers of two the cone has an irreducible factor of degree not dividing "
                      "ord_(2n - 1)(2)", not_powers_of_two)):
        ok, info = fn()
        check(name, ok, info)
    s = json.loads(STRESS.read_text()) if STRESS.exists() else None
    if s is not None and s.get("pass") is not None:
        check("9 the stress run (stress_test.json)", s["pass"] is True, s)
    else:
        OUT["9 the stress run (stress_test.json)"] = {"pass": None, "info": "pending (LINEAR-ROOTS-S1)"}
        print("PENDING 9 the stress run", flush=True)
    res = {"ticket": "LINEAR-ROOTS-20261109-001A", "artifact_id": "LINEAR-ROOTS-20261109-001A-P001", "checks": OUT,
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
