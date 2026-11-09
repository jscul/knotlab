#!/usr/bin/env python3
"""Checks for CONE-COLLAPSE-20261109-001A: the cut-open torus walk as two particles, its quarter-turn cone, and the return map of
the cut line at powers of two.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. Checks 1 to 4 test proved statements (and the Smith form) on small sides; checks 5 to 8 are exact
computations at sides 4 to 64; check 9 reads the stress run at side 128 (stress_test.json beside the decision note)."""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import collapse_lib as L  # noqa: E402

T0 = time.time()
OUT = {}
DEPS = {
    "proofs/FULL-REACH-PROOF-20261108-001A/FULL-REACH-PROOF-20261108-001A-P001_symmetries_the_torus_and_powers_of_two/manifest.json":
        "affc32533a4d960bd72b879ef5870513fe8ffaad5614bf296900aa27d5d618d0",
}
STRESS = ROOT / "research/CONE-COLLAPSE-20261109-001/stress_test.json"
FAILED = []
POWERS = (4, 8, 16, 32, 64)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


# 1: the two-particle form
def two_particle():
    bad = []
    for n in range(2, 17):
        S = 2 * n - 1
        Te, To, R, Lm = L.two_particle(n)
        A = np.zeros((S * S, S * S))
        for (X, Y) in L.points(n):
            for (X2, Y2) in L.reads(n, (X, Y)):
                A[Y * S + X, Y2 * S + X2] = 1
        odd = np.array([(Y + X) % 2 == 1 for Y in range(S) for X in range(S)])
        sub = np.ix_(odd, odd)
        f1 = np.mod(np.kron(Te, R) + np.kron(To, Lm), 2)[sub]
        f2 = np.mod(np.kron(Lm, Te) + np.kron(R, To), 2)[sub]
        if not ((f1 == A[sub]).all() and (f2 == A[sub]).all()):
            bad.append(n)
    return bad


# 2: the quarter turn is free and commutes with A; the cone filtration; the characteristic polynomial is the cone's to the fourth
def quarter_turn():
    bad, info = [], {}
    for n in range(2, 13):
        P, ix, A = L.box(n)
        rho = L.quarter_turn(n)
        Rm = np.zeros_like(A)
        for k, p in enumerate(P):
            Rm[k, ix[rho(p)]] = 1
        free = all(rho(p) != p and rho(rho(p)) != p for p in P)
        commutes = (L.mm2(Rm, A) == L.mm2(A, Rm)).all()
        reps, orb, Ac = L.cone(n)
        Tn = len(reps)
        E = np.mod(Rm + np.eye(len(P)), 2)
        Ej, ranks = np.eye(len(P)), []
        for j in range(1, 5):
            Ej = L.mm2(Ej, E)
            ranks.append(L.rank2(Ej))
        filt = ranks == [3 * Tn, 2 * Tn, Tn, 0]
        rec = {"free": free, "commutes": commutes, "ranks of (rho + 1)^j": ranks}
        if n <= 8:
            cpA, cpC = L.charpoly(A), L.charpoly(Ac)
            c4 = L.pmul(L.pmul(cpC, cpC), L.pmul(cpC, cpC))
            rec["charpoly(A) = charpoly(A_cone)^4"] = cpA == c4
            filt &= cpA == c4
        info[n] = rec
        if not (free and commutes and filt):
            bad.append(n)
    return bad, info


# 3: the cut-line reduction at powers of two
def cut_line():
    info, ok = {}, True
    for n in (2, 4, 8, 16):
        rm = L.return_map(n)
        I = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        rec = {
            "G = G' (the two cut lines' blocks)": rm["G"] == rm["Gv"],
            "R_C2C1 = H J": rm["H2"] == L.pmat_mul(rm["H"], rm["J"]),
            "H = J H J": rm["H"] == L.pmat_mul(L.pmat_mul(rm["J"], rm["H"]), rm["J"]),
            "G (I + w^2 K) = I": L.pmat_mul(rm["G"], rm["Ginv"]) == I,
            "C J = J C": L.pmat_mul(rm["C"], rm["J"]) == L.pmat_mul(rm["J"], rm["C"]),
            "C = w C'(w^2) (odd entries)": all(x & 0x5555555555555555555555555555555555555555555555555555555555555555 == 0
                                              for r in rm["C"] for x in r),
        }
        if n >= 4:
            reps, orb, Ac = L.cone(n)
            cp = L.charpoly(Ac)
            Pc = L.prev(cp, L.pdeg(cp))
            dCs = L.bareiss_det(L.pmat_plus_identity(rm["Cs"]))
            rec["det(I + C_s) = det(I - w A_cone)"] = dCs == Pc
            if n <= 8:
                P, ix, A = L.box(n)
                cpA = L.charpoly(A)
                dC = L.bareiss_det(L.pmat_plus_identity(rm["C"]))
                rec["det(I - wA) = det(I + C)^2"] = L.prev(cpA, L.pdeg(cpA)) == L.pmul(dC, dC)
                rec["det(I + C) = det(I + C_s)^2"] = dC == L.pmul(dCs, dCs)
        ok &= all(rec.values())
        info[n] = rec
    return ok, info


# 4: the Smith form of I + C_s(w) is the cone's Jordan data
def smith(spec):
    info, ok = {}, True
    for n in (4, 8, 16):
        rm = L.return_map(n)
        inv = [d for d in L.smith_form(L.pmat_plus_identity(rm["Cs"])) if d != 1]
        # predicted: the i-th largest invariant factor holds rev(m_s)^(i-th largest Jordan block of class s)
        blocks = {}
        for r in spec[n]["classes"]:
            dims = r["kernel dims"]
            if not dims or dims[-1] == 0:
                continue
            cnt = [dims[0]] + [dims[j] - dims[j - 1] for j in range(1, len(dims))]   # blocks of size >= j
            sizes = sorted((j + 1 for j in range(len(cnt)) for _ in range(cnt[j] - (cnt[j + 1] if j + 1 < len(cnt) else 0))),
                           reverse=True)
            blocks[r["coset"]] = (L.prev(r["minpoly"], r["size"]), sizes)
        depth = max(len(s) for _, s in blocks.values())
        pred = []
        for i in range(depth):
            d = 1
            for rv, sizes in blocks.values():
                if i < len(sizes):
                    for _ in range(sizes[i]):
                        d = L.pmul(d, rv)
            pred.append(d)
        match = sorted(inv) == sorted(pred)
        info[n] = {"nontrivial invariant factors": len(inv), "match the Jordan blocks": match,
                   "degrees": sorted(L.pdeg(d) for d in inv)}
        ok &= match
    return ok, info


# 5: the spectrum of the cone at 4 to 64: every eigenvalue a (2n - 1)-th root of unity, multiplicity k(k + 1)/2 with Jordan
#    blocks 2k - 1, 2k - 5, ..., and the parity of k(k + 1)/2 equal to Tr(1/lambda)
def spectrum(spec):
    info, ok = {}, True
    for n in POWERS:
        cl = spec[n]["classes"]
        T = n * (n - 1) // 2
        accounted = sum(r["alg"] * r["size"] for r in cl)
        tri = all(L.triangular_index(r["alg"]) is not None for r in cl)
        cg = all(r["kernel dims"] == (L.clebsch_gordan_dims(L.triangular_index(r["alg"])) or [0]) for r in cl) if tri else False
        par = all((r["alg"] % 2) == r["Tr(1/lambda)"] for r in cl)
        info[n] = {"cone dimension": T, "accounted by (2n - 1)-th roots of unity": accounted,
                   "classes (coset: k)": {r["coset"]: L.triangular_index(r["alg"]) for r in cl},
                   "triangular": tri, "Jordan blocks 2k - 1, 2k - 5, ...": cg, "parity = Tr(1/lambda)": par}
        ok &= accounted == T and tri and cg and par
    return ok, info


# 6: traces of the cone walk: tr(A_cone^j) = 1 exactly when j = 2^i mod (2n - 1)
def traces():
    info, ok = {}, True
    for n in POWERS:
        Ac = L.cone(n)[2]
        q = 2 * n - 1
        pw2 = {pow(2, i, q) for i in range(q)}
        Pw, bad = np.eye(Ac.shape[0]), []
        for j in range(1, q + 1):
            Pw = L.mm2(Pw, Ac)
            t = int(np.trace(Pw)) % 2
            if t != (1 if j % q in pw2 else 0):
                bad.append(j)
        info[n] = {"j checked": q, "mismatches": bad}
        ok &= not bad
    return ok, info


# 7: the cone polynomials of n and 2n agree below degree 2n and differ at degree 2n
def stability(spec):
    info, ok = {}, True
    polys = {n: L.cone_polynomial(n, spec[n]) for n in POWERS}
    for n in POWERS[:-1]:
        x = polys[n] ^ polys[2 * n]
        first = L.val(x)
        info[n] = {"first differing degree of P_n and P_2n": first}
        ok &= first == 2 * n
    low = [i for i in range(64) if (polys[64] >> i) & 1]
    info["P_64 below degree 64"] = low
    return ok, info


# 8: the return map's characteristic polynomial det(z + C_s) = sum e_j z^(h - j)
def return_char(n_list=(4, 8, 16, 32)):
    info, ok = {}, True
    for n in n_list:
        rm = L.return_map(n)
        e = L.charpoly_berkowitz(rm["Cs"])
        h, m = n // 2, n.bit_length() - 1
        rec = {
            "e_1 = w + w^3": e[1] == 0b1010,
            "e_j has valuation j(2j - 1)": all(L.val(e[j]) == j * (2 * j - 1) for j in range(1, h + 1)),
            "e_j / w^j is a square": all(L.deriv(e[j] >> j) == 0 for j in range(1, h + 1)),
            "e_h = w^(n(n - 1)/2)": e[h] == 1 << (n * (n - 1) // 2),
            "e_(h-1) = w^((h-1)(2h-3)) (sum_(i<m) w^(2^i - 1))^2":
                e[h - 1] == L.pmul(1 << ((h - 1) * (2 * h - 3)), L.psquare(sum(1 << ((1 << i) - 1) for i in range(m)))),
        }
        ok &= all(rec.values())
        info[n] = rec
    return ok, info


def main():
    write = "--write" in sys.argv
    deps = {p: sha(p) for p in DEPS}
    check("0 dependency bound by hash (FULL-REACH-PROOF-20261108-001A's manifest)", deps == DEPS, deps)
    check("1 Theorem 1: A = T_e (x) R + T_o (x) L = L (x) T_e + R (x) T_o on the contacts, sides 2 to 16", not two_particle(),
          two_particle())
    bad, info = quarter_turn()
    check("2 Theorem 2: the quarter turn is free and commutes with A, (rho + 1)^j has rank (4 - j) T, and charpoly(A) = "
          "charpoly(A_cone)^4, sides 2 to 12 (the last at 2 to 8)", not bad, info)
    ok, info = cut_line()
    check("3 Theorem 3: at sides 2, 4, 8, 16 the cut-line blocks satisfy G = G', R_C2C1 = HJ, H = JHJ, G^-1 = I + w^2 K, CJ = JC; "
          "det(I - w A_cone) = det(I + C_s) (4, 8, 16) and det(I - wA) = det(I + C)^2 = det(I + C_s)^4 (4, 8)", ok, info)
    spec = {n: L.cone_spectrum(n) for n in POWERS}
    ok, info = smith(spec)
    check("4 the Smith form of I + C_s(w) at sides 4, 8, 16 is the cone's Jordan data", ok, info)
    ok, info = spectrum(spec)
    check("5 computed: at sides 4 to 64 every eigenvalue of the cone is a (2n - 1)-th root of unity, each with multiplicity "
          "k(k + 1)/2 and Jordan blocks 2k - 1, 2k - 5, ..., the multiplicity odd exactly when Tr(1/lambda) = 1", ok, info)
    ok, info = traces()
    check("6 computed: tr(A_cone^j) = 1 exactly when j is a power of two mod 2n - 1, for j = 1 to 2n - 1, sides 4 to 64", ok, info)
    ok, info = stability(spec)
    check("7 computed: det(I - w A_cone) at sides n and 2n agree below degree 2n and differ at degree 2n, n = 4 to 32", ok, info)
    ok, info = return_char()
    check("8 computed: det(z + C_s) = sum e_j z^(h - j) with e_1 = w + w^3, val e_j = j(2j - 1), e_h = w^(n(n-1)/2) and "
          "e_(h-1) = w^((h-1)(2h-3)) (sum_(i<m) w^(2^i - 1))^2, sides 4 to 32", ok, info)
    s = json.loads(STRESS.read_text()) if STRESS.exists() else None
    if s is not None and s.get("pass") is not None:
        check("9 the stress run at side 128 (stress_test.json)", s["pass"] is True, s)
    else:
        done = {k: v.get("pass") for k, v in (s or {}).get("stages", {}).items()}
        OUT["9 the stress run at side 128 (stress_test.json)"] = {"pass": None,
                                                                 "info": {"pending (CONE-COLLAPSE-S1)": True, "stages done": done}}
        print("PENDING 9 the stress run at side 128", done, flush=True)
    res = {"ticket": "CONE-COLLAPSE-20261109-001A", "artifact_id": "CONE-COLLAPSE-20261109-001A-P001", "checks": OUT,
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
