#!/usr/bin/env python3
"""One size past for TIME-KNOTS-20261107-001's computed claims (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B research/TIME-KNOTS-20261107-001/stress_test.py quick   the quick checks (stress_test_quick.json)
    .venv/bin/python3 -B research/TIME-KNOTS-20261107-001/stress_test.py census  the census at T = 7 (stress_test_census7.json)
Reuses ticket A's library and GROWTH-LAW-20261107-001A's generic K1-K3 enumerator."""
import collections
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
sys.path.insert(0, str(ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"))
import time_knots_lib as K  # noqa: E402
import growth_law_lib as G  # noqa: E402

T0 = time.time()


def generic_knots(F, n):
    R = G.Rel([f"x{j}" for j in range(n)] + ["y"], K.relation_of_map(F, n))
    return set(G.knots(R))


def quick():
    out = {}
    # Theorem 1 at T = 3 (one lag past the check's T = 2) on all 88 rules
    mism = 0
    for r in K.classes():
        F = K.t_step_map(r, 3)
        kn, _, _ = K.knots_across_time(F, 7)
        mism += generic_knots(F, 7) != {S | (1 << 7) for S in kn}
    out["Theorem 1 at T = 3, all 88 rules: mismatches"] = mism
    # Theorem 2 one size past: random 6-input functions, and all terms and clauses of 6 inputs
    rng = np.random.default_rng(7)
    n = 6
    u = np.arange(1 << n)
    bad = 0
    for k in range(1, 7):
        for vs in itertools.combinations(range(n), k):
            for signs in itertools.product((0, 1), repeat=k):
                lits = [((u >> j) & 1) == s for j, s in zip(vs, signs)]
                for F in (np.logical_and.reduce(lits).astype(np.uint8), np.logical_or.reduce(lits).astype(np.uint8)):
                    bad += bool(K.knots_across_time(F, n)[0])
    knotted = 0
    for _ in range(300):
        F = rng.integers(0, 2, size=1 << n).astype(np.uint8)
        knotted += bool(K.knots_across_time(F, n)[0])
    out["Theorem 2 one size past: 6-input terms and clauses with a knot"] = bad
    out["Theorem 2 one size past: random 6-input functions with a knot (of 300)"] = knotted
    # rule 102 one size past: T = 7, 8, in the past light cone of (T, 0) and in the wider window of (T + 1, 0)
    rows = []
    for T, W in ((7, 7), (8, 8), (7, 8), (8, 9)):
        cone = [(t, i) for t in range(W + 1) for i in range(W - t + 1)]
        idx = {c: k for k, c in enumerate(cone)}
        rs = []
        for v in range(1 << (W + 1)):
            vals = {(0, i): (v >> i) & 1 for i in range(W + 1)}
            for t in range(1, W + 1):
                for i in range(W - t + 1):
                    vals[(t, i)] = vals[(t - 1, i)] ^ vals[(t - 1, i + 1)]
            rs.append(sum(vals[c] << idx[c] for c in cone))
        R = G.Rel([f"c{t}_{i}" for (t, i) in cone], rs)
        a, b = "c0_0", f"c{T}_0"
        others = [x for x in R.names if x not in (a, b)]
        least = None
        for k in range(1, 4):
            for S in itertools.combinations(others, k):
                if G.is_knot_set(R, [a, b] + list(S)):
                    least = k + 2
                    break
            if least:
                break
        rows.append([T, W, least])
    out["rule 102, least knot through (0,0) and (T,0) [T, window: the past cone of (W, 0), size] (2 + w(T): T=7 -> 4, T=8 -> 3)"] = rows
    out["light cone of (T, 0) matches 2 + w(T)"] = {7: rows[0][2] == 4, 8: rows[1][2] == 3}
    out["wider window matches 2 + w(T)"] = {7: rows[2][2] == 4, 8: rows[3][2] == 3}
    out["pass"] = mism == 0 and bad == 0 and rows[2][2] == 4 and rows[3][2] == 3
    out["seconds"] = round(time.time() - T0, 1)
    (HERE / "stress_test_quick.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def census7():
    T = 7
    n = 2 * T + 1
    rows = {}
    for r in K.classes():
        F = K.t_step_map(r, T)
        kn, ties, const = K.knots_across_time(F, n)
        rows[r] = {"knots": len(kn), "ties": len(ties), "constant": const,
                   "least knot": min((bin(S).count("1") + 1 for S in kn), default=None)}
        print(r, rows[r], round(time.time() - T0, 1), flush=True)
    prev = json.loads((ROOT / "artifacts/TIME-KNOTS-20261107-001B/TIME-KNOTS-20261107-001B-E001_elementary_census/run/result.json").read_text())
    cls = prev["classes of behaviour"]
    kf_ok = all(rows[r]["knots"] == 0 for r in cls["knot-free at every lag"])
    one_ok = all(rows[r]["knots"] == 1 for r in cls["one knot at every lag"])
    prev_rows = json.loads((ROOT / "artifacts/TIME-KNOTS-20261107-001B/TIME-KNOTS-20261107-001B-E001_elementary_census/run/rows.json").read_text())
    grow_ok = [r for r in cls["knots at every lag, growing"] if rows[r]["knots"] <= prev_rows[str(r)][-1]["knots"]]
    F = K.t_step_map(184, T)
    kn184 = set(K.knots_across_time(F, n)[0])
    all8 = {sum(1 << j for j in S) for S in itertools.combinations(range(n), T + 1)}
    out = {"T": T, "knot-free class still knot-free": kf_ok, "one-knot class still one knot": one_ok,
           "growing rules that did not grow at T = 7": grow_ok, "rule 184 knots are all sets of T + 1 cells": kn184 == all8,
           "rule 184 knots": len(kn184), "rows": rows, "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test_census7.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    {"quick": quick, "census": census7}[sys.argv[1]]()
