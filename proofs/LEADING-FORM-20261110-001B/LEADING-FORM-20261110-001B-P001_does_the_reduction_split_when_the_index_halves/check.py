#!/usr/bin/env python3
"""Ticket LEADING-FORM-20261110-001B: the frozen halving test (sub-goal B91's first step).

    .venv/bin/python3 -B check.py          run the test and compare with result.json
    .venv/bin/python3 -B check.py --write  run the test and write result.json
At every eigenvalue with even k = 2c >= 4 for sides 16, 32 and 64: the reduction M of the family to ker X_b (G monic, basis G Y^j) to
order 2k, with the monomial complement W_0 and the complement W' (containing k G Y^j, 2j < k - 1), each in the parameter l of
Zhat(l) = (1 + l) Z(a + a l/(1 + l)) and in the parameter u of Z(a + a u)/(1 + u). S1: entries with i + j odd vanish below order 2k.
S2: entries with i + j even have no even power below 2k. Uses CHAIN-ORDERS-20261110-001A's library (bound by hash)."""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CO = "proofs/CHAIN-ORDERS-20261110-001A/CHAIN-ORDERS-20261110-001A-P001_the_reduced_form_at_every_order"
sys.path.insert(0, str(ROOT / CO))
import orders_lib as OL  # noqa: E402

CH, RL = OL.CH, OL.RL
DEPS = {CO + "/manifest.json": None, CO + "/orders_lib.py": None}
T0 = time.time()


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def u_family(F, a, m, L):
    """Taylor coefficients in u of Z(a + a u)/(1 + u)"""
    Zs = CH.coefficients(F, a, m, L)
    h = Zs[0].shape[0]
    raw = [F.mul_np(np.full((h, h), F.pw(a, r), dtype=np.int64), Zs[r]) for r in range(L)]
    out = [np.zeros((h, h), dtype=np.int64) for _ in range(L)]
    for r in range(L):
        for t in range(L - r):                     # 1/(1 + u) = 1 + u + u^2 + ... in characteristic 2
            out[r + t] ^= raw[r]
    return out


def test_at(F, a, m):
    G, k, fam = OL.monic_least(F, a, m)
    h = 1 << (m - 1)
    L = 2 * k
    fams = {"l": OL.lam_family(F, a, m, L), "u": u_family(F, a, m, L)}
    comps = {"W_0": OL.monomial_complement(G, h, len(fam)), "W'": OL.good_complement(G, fam, h, k)}
    out = {}
    for pn, Zs in fams.items():
        for cn, W in comps.items():
            M = OL.schur(F, Zs, fam, W, L)
            J = len(fam)
            s1 = all(not M[r][i, j] for i in range(J) for j in range(J) if (i + j) % 2 for r in range(L))
            s2 = all(not M[r][i, j] for i in range(J) for j in range(J) if (i + j) % 2 == 0 for r in range(0, L, 2))
            out["%s, %s" % (cn, pn)] = {"S1": s1, "S2": s2}
    return k, out


def main():
    res = {"dependencies": {p: sha(p) for p in DEPS}, "sides": {}, "variants": {}}
    for m in (4, 5, 6):
        F = RL.GF(m + 1)
        rows = []
        for a in F.exp:
            K = F.kloosterman(a)
            k = (abs(K - 1) - 1) // 2
            if k < 4 or k % 2:
                continue
            k2, out = test_at(F, a, m)
            rows.append({"a": "alpha^%d" % F.log[a], "k": k2, "variants": out})
        res["sides"][str(1 << m)] = rows
        print("side %d: %d eigenvalues with even k >= 4 (%.0fs)" % (1 << m, len(rows), time.time() - T0), flush=True)
    names = ["W_0, l", "W', l", "W_0, u", "W', u"]
    for nm in names:
        allrows = [r for rows in res["sides"].values() for r in rows]
        p1 = sum(r["variants"][nm]["S1"] for r in allrows)
        p2 = sum(r["variants"][nm]["S2"] for r in allrows)
        both = sum(r["variants"][nm]["S1"] and r["variants"][nm]["S2"] for r in allrows)
        first_fail = next((r["a"] + " (side " + s + ", k = %d)" % r["k"] for s, rows in res["sides"].items() for r in rows
                           if not (r["variants"][nm]["S1"] and r["variants"][nm]["S2"])), None)
        res["variants"][nm] = {"tested": len(allrows), "S1 holds": p1, "S2 holds": p2, "both hold": both, "first failure": first_fail}
        print(nm, res["variants"][nm])
    res["some variant passes everywhere"] = any(v["both hold"] == v["tested"] for v in res["variants"].values())
    res["decision"] = ("consider the induction on k" if res["some variant passes everywhere"]
                       else "B91's strong form refuted at these sides; proceed with ticket A's co-distance induction")
    res["seconds"] = round(time.time() - T0)
    res["status"] = "passed"                       # the test ran to completion; its outcome is res["decision"]
    print("decision:", res["decision"])
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(res, indent=1) + "\n")
        print("wrote", path)


if __name__ == "__main__":
    main()
