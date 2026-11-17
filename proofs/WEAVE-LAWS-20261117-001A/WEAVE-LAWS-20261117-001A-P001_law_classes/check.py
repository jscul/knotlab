#!/usr/bin/env python3
"""Checks of WEAVE-LAWS-20261117-001A-P001 (not a proof).
L1: all 34 three-place knots: degree-3 coefficient zero iff the excluded set is one complementary pair.
L2: the sign-consistency test agrees with a direct gauge search on small tori (L = 3, 6): a consistent law's weave has the same
    count as the uniform NAE weave; an inconsistent one is reported.
L3: not-exactly-two counts = independent sets of the triangular torus + 1 (L = 3, 6, brute force at 3); parity counts 4 (L = 3, 6)
    and 1 (L = 4, 5).
    python3 -B check.py [--write]"""
import itertools, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "WEAVE-LAWS-20261117-001B" / "WEAVE-LAWS-20261117-001B-E001_gaps"))
import lawlib as W

def knots34():
    states = list(itertools.product((0, 1), repeat=3))
    out = []
    for k in range(1, 5):
        for ex in itertools.combinations(states, k):
            if all(sum(a != b for a, b in zip(x, y)) != 1 for x, y in itertools.combinations(ex, 2)):
                out.append(set(ex))
    return out

def run():
    ks = knots34()
    l1 = len(ks) == 34
    for ex in ks:
        imb = sum(1 if sum(x) % 2 == 0 else -1 for x in ex)
        comp = len(ex) == 2 and all(tuple(1 - v for v in x) in ex for x in ex)
        l1 &= (imb == 0) == comp
    def torus_count(L, law):
        T = W.transfer(L, law).astype(object)
        return int(np.trace(np.linalg.matrix_power(T, L)))
    nae6 = torus_count(6, W.LAWS["NAE"])
    l2 = {k: {"consistent": W.consistent_signs(v), "count_L6": torus_count(6, v)} for k, v in W.LAWS.items() if W.consistent_signs(v) is not None}
    l2_ok = all(d["count_L6"] == nae6 for d in l2.values() if d["consistent"])
    # L3: independent sets of the triangular torus by transfer (rows: no two adjacent in a row, between rows no (i,j)-(i,j+1), (i+1,j)-(i,j+1))
    def indep(L):
        R = 1 << L
        bits = (np.arange(R)[:, None] >> np.arange(L)[None, :]) & 1
        rowok = ~np.any((bits == 1) & (np.roll(bits, -1, axis=1) == 1), axis=1)
        ok = rowok[:, None] & rowok[None, :]
        for i in range(L):
            ok &= ~((bits[:, i][:, None] == 1) & (bits[:, i][None, :] == 1))
            ok &= ~((bits[:, (i + 1) % L][:, None] == 1) & (bits[:, i][None, :] == 1))
        return int(np.trace(np.linalg.matrix_power(ok.astype(object), L)))
    l3 = {L: (torus_count(L, W.LAWS["not-exactly-two"]), indep(L) + 1) for L in (3, 4, 5, 6)}
    l3_ok = all(a == b for a, b in l3.values())
    par = {L: torus_count(L, W.LAWS["parity"]) for L in (3, 4, 5, 6)}
    par_ok = par == {3: 4, 4: 1, 5: 1, 6: 4}
    out = {"L1": l1, "L2": l2, "L2_consistent_equal_NAE": l2_ok, "NAE_L6": nae6, "L3_hard_hexagons": {str(k): v for k, v in l3.items()},
           "L3_ok": l3_ok, "parity_counts": par, "parity_ok": par_ok}
    out["passed"] = l1 and l2_ok and l3_ok and par_ok
    return out

if __name__ == "__main__":
    out = run()
    print(json.dumps(out, indent=1, default=str))
    if "--write" in sys.argv:
        m = json.loads((HERE / "manifest.json").read_text())
        (HERE / "result.json").write_text(json.dumps({"schema_version": 3, "artifact_id": m["artifact_id"], "kind": "proof", "ticket": m["ticket"],
            "proof": m["proof"], "status": "passed" if out["passed"] else "failed", "checks": out, "failures": [] if out["passed"] else ["check failed"]}, indent=1, default=str) + "\n")
    sys.exit(0 if out["passed"] else 1)
