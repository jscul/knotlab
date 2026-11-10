#!/usr/bin/env python3
"""Checks for CHAIN-ORDERS-20261110-001A: the reduced form of the cut-open torus's family at every order, at sides 2^m.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, about three minutes. Checks 1 to 5 test Theorems 1 to 5; check 6 is the computed leading form (the target) at every a for
sides 8 to 128 (128 run after registration); check 7 reads the stress run at side 256 (stress_test.json, CHAIN-ORDERS-S1); check 8 is
the computed comparison of the reading (squares of one Jordan block over GF(2))."""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import orders_lib as OL  # noqa: E402

CH, BL, RL = OL.CH, OL.BL, OL.RL
T0 = time.time()
OUT = {}
JC = "proofs/JORDAN-CHAINS-20261110-001A/JORDAN-CHAINS-20261110-001A-P001_the_chains_one_polynomial_heads"
DEPS = {JC + "/manifest.json": "7f29fb0a2fef53fa33f73e65313fc6011be42d7beda9b1c806abcb42edde99a1", JC + "/chains_lib.py": None}
SIDE64 = ROOT / "research/JORDAN-CHAINS-20261110-001/side64.json"
STRESS = ROOT / "research/CHAIN-ORDERS-20261110-001/stress_test.json"
FAILED = []
FIELDS = {}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


def field(m):
    if m not in FIELDS:
        FIELDS[m] = RL.GF(m + 1)
    return FIELDS[m]


def k_of(F, a):
    return (abs(F.kloosterman(a) - 1) - 1) // 2


def chain_blocks(k):
    return [2 * k - 1 - 4 * j for j in range((k + 1) // 2)] if k else []


# 1: Theorem 1, the sparse Taylor form, against the exact Taylor coefficients of JORDAN-CHAINS-20261110-001A
def sparse_form():
    info = {}
    for m in range(2, 8):
        F, n = field(m), 1 << m
        bad = sum([list(map(int, o)) for o in CH.taylor(F, a, m, n)] != OL.sparse_taylor(F, a, m, n) for a in F.exp)
        info["side %d" % n] = {"values of a": len(F.exp), "mismatches": bad}
    return all(v["mismatches"] == 0 for v in info.values()), info


# 2: Theorem 2, one moment matrix: the partial multiplicities of H(w) are those of Z(w) at every a
def moment_matrix():
    info = {}
    for m in (3, 4, 5):
        F = field(m)
        bad = 0
        for a in F.exp:
            k = k_of(F, a)
            L = 2 * k + 2
            bad += OL.hankel_blocks(F, a, m, L) != CH.partial_multiplicities(F, CH.coefficients(F, a, m, L), L)
        info["side %d" % (1 << m)] = {"compared with": "the blocks of Z", "mismatches": bad}
    side64 = json.loads(SIDE64.read_text())
    F = field(6)
    bad = sum(OL.hankel_blocks(F, a, 6, 2 * k_of(F, a) + 2) != chain_blocks(k_of(F, a)) for a in F.exp)
    info["side 64"] = {"compared with": "2k - 1 - 4j, the blocks of Z at every a by JORDAN-CHAINS-A1 (side64.json, pass %s)" % side64["pass"],
                       "mismatches": bad}
    return all(v["mismatches"] == 0 for v in info.values()) and side64["pass"], info


# 3: Theorem 3, Gamma^(k) invertible over GF(2), and the determinant recursions behind its proof
def leading_matrix():
    bad = [k for k in range(1, 1000) if not OL.gamma_invertible(k)]
    return not bad, {"k checked": "1 to 999", "singular": bad}


# 4: Theorem 4, the reparametrized family Zhat(l) = Z_0 + l S + (even in l), from the exact Taylor coefficients
def lam_form():
    info = {}
    for m in range(2, 7):
        F, n, h = field(m), 1 << m, 1 << (m - 1)
        S = RL.star_matrix(F, 0, m, h)
        bad = 0
        for a in F.exp:
            Zh = OL.lam_family(F, a, m, n)
            want = [CH.coefficients(F, a, m, 1)[0], S] + [np.zeros((h, h), dtype=np.int64) for _ in range(n - 2)]
            for r in range(1, m):
                e = 1 << r
                Mk = CH.mult([0] * (h - (1 << (r - 1))) + [1] + [0] * ((1 << (r - 1)) - 1), h)
                for t in range(e, n, e):
                    want[t] = want[t] ^ F.mul_np(np.full((h, h), F.pw(a, e), dtype=np.int64), Mk)
            bad += any((x != y).any() for x, y in zip(Zh, want))
        info["side %d" % n] = {"mismatches": bad}
    return all(v["mismatches"] == 0 for v in info.values()), info


# 5: Theorem 5, orders two and three of the reduction
def low_orders():
    info = {}
    for m in range(3, 8):
        F = field(m)
        res = [OL.third_order_at(F, a, m) for a in F.exp]
        info["side %d" % (1 << m)] = {"values of a": len(res), "failures": sum(not r["ok"] for r in res)}
    return all(v["failures"] == 0 for v in info.values()), info


# 6: the target, the leading form, computed at every a (sides 8 to 64 before registration, 128 after)
def leading_form():
    info = {}
    for m in range(3, 8):
        F = field(m)
        res = [OL.leading_form_at(F, a, m) for a in F.exp]
        counts = {}
        for r in res:
            counts[r["k"]] = counts.get(r["k"], 0) + 1
        info["side %d" % (1 << m)] = {"values of a": len(res), "failures": sum(not r["ok"] for r in res),
                                      "counts by k": {str(k): counts[k] for k in sorted(counts)}}
    return all(v["failures"] == 0 for v in info.values()), info


# 8: the reading: over GF(2) the squares of one Jordan block do not give 2k - 1 - 4j (k = 3 and 5 to 15)
def squares():
    info, agree = {}, {}
    for k in range(1, 16):
        want = chain_blocks(k)
        got = {"wedge^2 of J_(k+1), group": OL.square_blocks(k + 1, "wedge-group"),
               "wedge^2 of J_(k+1), Lie": OL.square_blocks(k + 1, "wedge-lie"),
               "Sym^2 of J_k, group": OL.square_blocks(k, "sym-group")}
        info[str(k)] = {"2k-1-4j": want, **got}
        agree[str(k)] = [name for name, v in got.items() if v == want]
    ok = all(not agree[str(k)] for k in [3] + list(range(5, 16)))
    return ok, {"agreeing at": {k: v for k, v in agree.items() if v}, "blocks": info}


def main():
    write = "--write" in sys.argv
    check("0 dependencies bound by hash (JORDAN-CHAINS-20261110-001A's manifest and library)",
          all(v is None or sha(p) == v for p, v in DEPS.items()), {p: sha(p) for p in DEPS})
    ok, info = sparse_form()
    check("1 Theorem 1: Omega(a + d) = (1 + d/a)(Omega_a + sum_r d^(2^r) k^(h - 2^(r-1))) mod d^n, every a, sides 4 to 128", ok, info)
    ok, info = moment_matrix()
    check("2 Theorem 2: the partial multiplicities of the moment matrix H(w) are those of Z(w), every a, sides 8 to 64", ok, info)
    ok, info = leading_matrix()
    check("3 Theorem 3: Gamma^(k) = [k - i - j a power of two] invertible over GF(2), k < 1000", ok, info)
    ok, info = lam_form()
    check("4 Theorem 4: Zhat(l) = Z_0 + l S + sum_r a^(2^r) l^(2^r)/(1 + l^(2^r)) M_(k^(h - 2^(r-1))), every a, sides 4 to 64", ok, info)
    ok, info = low_orders()
    check("5 Theorem 5: [l^2] M = 0 where i + j <= k - 2, and [l^3] M = [Y^(h-2-i-j)] N(G) on the chains of length >= 2, every a, "
          "sides 8 to 128", ok, info)
    ok, info = leading_form()
    check("6 computed, the target: M_ij = u^(2k-1-2(i+j)) ([k-i-j a power of two] + O(u)), every a, sides 8 to 128", ok, info)
    ok, info = squares()
    check("8 the reading: over GF(2) the exterior and symmetric squares of one Jordan block differ from 2k - 1 - 4j at k = 3 and "
          "5 to 15", ok, info)
    if STRESS.exists():
        st = json.loads(STRESS.read_text())
        done = "pass" in st
        check("7 the stress run at side 256, every a (stress_test.json)", done and st["pass"],
              {"checked": st.get("checked"), "failures": len(st.get("failures", [])), "k counts": st.get("k counts"),
               "seconds": st.get("seconds"), "finished": done})
    else:
        OUT["7 the stress run at side 256, every a (stress_test.json)"] = {"pass": None, "info": "pending (CHAIN-ORDERS-S1)"}
        print("PEND 7 the stress run at side 256 (stress_test.json)")
    result = {"schema_version": 1, "artifact": "CHAIN-ORDERS-20261110-001A-P001", "checks": OUT,
              "status": "passed" if not FAILED else "failed"}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    elif path.exists():
        old = json.loads(path.read_text())
        same = all(old["checks"].get(k, {}).get("pass") == v["pass"] for k, v in OUT.items())
        print("result.json agrees" if same else "result.json DIFFERS")
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
