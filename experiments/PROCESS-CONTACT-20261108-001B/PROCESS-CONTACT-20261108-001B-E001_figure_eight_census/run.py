"""PROCESS-CONTACT-20261108-001B-E001: two rings that share their contact cell (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/PROCESS-CONTACT-20261108-001B/
                                          PROCESS-CONTACT-20261108-001B-E001_figure_eight_census/run/rows.json and result.json
    .venv/bin/python3 -B run.py --pilot   times a few configurations and prints no verdicts (the contract's feasibility check)
Each configuration's verdict at every lag is exact: the joint dynamics is iterated until its T-step map repeats."""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIB = ROOT / "proofs/PROCESS-CONTACT-20261108-001A/PROCESS-CONTACT-20261108-001A-P001_which_contacts_bind_two_processes"
sys.path.insert(0, str(LIB))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
import process_contact_lib as P  # noqa: E402
import time_knots_lib as K  # noqa: E402

OUT = ROOT / "artifacts" / "PROCESS-CONTACT-20261108-001B" / "PROCESS-CONTACT-20261108-001B-E001_figure_eight_census" / "run"
SIZES_ALIKE = ((3, 4), (4, 4), (4, 5), (5, 6))
SIZE_MIXED = (3, 4)
LINEAR_OR_AFFINE = set(P.LINEAR) | set(P.AFFINE)


def classify(verdicts, T1, period):
    cyc = verdicts[T1 - 1:T1 + period - 1]
    pre = verdicts[:T1 - 1]
    if all(verdicts):
        return "binds at every lag"
    if all(cyc):
        return "binds from some lag on"
    if any(cyc):
        return "binds at recurring lags only"
    if any(pre):
        return "binding decays"
    return "never binds"


def shared(rule_a, m, rule_b, n, g2):
    sa, sb, own = P.shared_sides(m, n)
    N = m + n - 1
    nxt = P.shared_state_maps(rule_a, m, rule_b, n, g2)
    verdicts, T1, period = P.lags_exactly(nxt, 0, lambda F: P.binds(F, sa, sb, own, N))
    return verdicts, T1, period


def ring_cell_nonconstant_always(rule, m):
    """a ring closed on itself: is its cell 0 nonconstant at every lag T >= 1 (exact)"""
    s = P.bits_of(m)
    nxt = np.zeros(1 << m, dtype=np.int64)
    ns = P.ring_step(s, rule)
    for j in range(m):
        nxt |= ns[:, j].astype(np.int64) << j
    verdicts, T1, period = P.lags_exactly(nxt, 0, lambda F: bool(F.min() != F.max()))
    return P.at_every_lag(verdicts, T1, period, 1)


def linear_prediction(rule, m, n, g2, lags):
    """for a linear or affine ring rule and a parity combiner the shared system is affine; binding at lag T holds exactly when
    the support of the contact's row of M^T meets both rings"""
    N = m + n - 1
    nxt = P.shared_state_maps(rule, m, rule, n, g2)
    base = int(nxt[0])
    cols = [int(nxt[1 << j]) ^ base for j in range(N)]           # column j: the image of the j-th unit vector
    # check affinity on all states
    for u in range(1 << N):
        v = base
        for j in range(N):
            if u >> j & 1:
                v ^= cols[j]
        if v != int(nxt[u]):
            return None
    rowmask = lambda M, i: sum(((M[j] >> i) & 1) << j for j in range(N))
    sa, sb, _ = P.shared_sides(m, n)
    out = []
    Mt = [1 << j for j in range(N)]                              # M^0 as columns
    for _ in range(lags):
        Mt = [sum_cols(cols, c) for c in Mt]
        row = rowmask(Mt, 0)
        out.append(bool(row & sa) and bool(row & sb))
    return out


def sum_cols(cols, c):
    v = 0
    j = 0
    while c:
        if c & 1:
            v ^= cols[j]
        c >>= 1
        j += 1
    return v


def job(args):
    kind, ra, rb, m, n, g2 = args
    verdicts, T1, period = shared(ra, m, rb, n, g2)
    return {"kind": kind, "rule_a": ra, "rule_b": rb, "m": m, "n": n, "combiner": g2, "name": P.two_input_name(g2),
            "class": classify(verdicts, T1, period), "first binding lag": next((T for T, v in enumerate(verdicts, 1) if v), None),
            "first lag without binding": next((T for T, v in enumerate(verdicts, 1) if not v), None),
            "repeat from": T1, "period": period, "lags computed": len(verdicts),
            "verdicts": "".join("1" if v else "0" for v in verdicts[:64])}


def main():
    t0 = time.time()
    reps = K.classes()
    if "--pilot" in sys.argv:
        for (ra, rb, m, n, g2) in ((30, 30, 5, 6, 6), (110, 110, 5, 6, 8), (184, 184, 5, 6, 6), (90, 90, 5, 6, 14), (54, 30, 3, 4, 6)):
            s = time.time()
            v, T1, period = shared(ra, m, rb, n, g2)
            print("pilot", ra, rb, m, n, g2, "lags computed", len(v), "seconds", round(time.time() - s, 2))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [("alike", r, r, m, n, g2) for (m, n) in SIZES_ALIKE for r in reps for g2 in P.TWO_INPUT]
    jobs += [("mixed", ra, rb, SIZE_MIXED[0], SIZE_MIXED[1], g2) for ra in reps for rb in reps for g2 in P.TWO_INPUT if ra != rb]
    with Pool(16) as pool:
        rows = pool.map(job, jobs, chunksize=64)
    # controls
    ctrl_lin = []
    for row in rows:
        if row["kind"] == "alike" and row["rule_a"] in LINEAR_OR_AFFINE and row["combiner"] in P.PARITIES:
            pred = linear_prediction(row["rule_a"], row["m"], row["n"], row["combiner"], row["lags computed"])
            ctrl_lin.append(pred is not None and "".join("1" if v else "0" for v in pred[:64]) == row["verdicts"])
    ctrl_onesided = all(row["class"] == "never binds" for row in rows if row["combiner"] in (0, 15, 0b1100, 0b0011, 0b1010, 0b0101))
    sample = [row for row in rows if row["kind"] == "alike" and row["m"] == 3][::37]
    ctrl_knots = []
    for row in sample:
        m, n = row["m"], row["n"]
        sa, sb, own = P.shared_sides(m, n)
        F1 = P.shared_maps(row["rule_a"], m, row["rule_b"], n, row["combiner"], 1)[0]
        ctrl_knots.append(P.binds_by_knots(F1, sa, sb, m + n - 1, K.knots_across_time) == (row["verdicts"][0] == "1"))
    controls = {"linear and affine rules with a parity combiner match the linear algebra at every computed lag": bool(ctrl_lin) and all(ctrl_lin),
                "constant and one-input combiners never bind": ctrl_onesided,
                "lag-1 verdicts agree with the minimally decisive sets on a sample": bool(ctrl_knots) and all(ctrl_knots)}
    # primary observable
    by_comb = defaultdict(Counter)
    for row in rows:
        by_comb[(row["kind"], row["name"])][row["class"]] += 1
    always = [row for row in rows if row["class"] == "binds at every lag"]
    nonparity_always = [row for row in always if row["combiner"] not in P.PARITIES]
    eventually = [row for row in rows if row["class"] in ("binds at every lag", "binds from some lag on")]
    nonparity_eventually = [row for row in eventually if row["combiner"] not in P.PARITIES]
    # feedback against the listening counterpart (Theorem 3: c(T) = g(a_0(T), b_0(T)) on rings closed on themselves)
    keep = {}
    for r in reps:
        for m in range(3, 7):
            keep[(r, m)] = ring_cell_nonconstant_always(r, m)
    table = Counter()
    examples = defaultdict(list)
    for row in rows:
        if row["combiner"] not in P.PARITIES:
            continue
        cp = keep[(row["rule_a"], row["m"])] and keep[(row["rule_b"], row["n"])]
        sh = row["class"] == "binds at every lag"
        key = f"listening {'binds' if cp else 'fails'} at every lag, shared {'binds' if sh else 'fails'}"
        table[key] += 1
        if cp != sh and len(examples[key]) < 12:
            examples[key].append([row["rule_a"], row["rule_b"], row["m"], row["n"], row["name"], row["class"]])
    xor_always = {(row["rule_a"], row["m"], row["n"]) for row in rows
                  if row["kind"] == "alike" and row["name"] == "xor" and row["class"] == "binds at every lag"}
    result = {
        "experiment": "PROCESS-CONTACT-20261108-001B-E001", "configurations": len(rows), "controls": controls,
        "controls_ok": all(controls.values()),
        "classes by combiner": {f"{k[0]} | {k[1]}": dict(sorted(v.items())) for k, v in sorted(by_comb.items())},
        "configurations binding at every lag": len(always),
        "non-parity combiners binding at every lag": [[r["rule_a"], r["rule_b"], r["m"], r["n"], r["name"]] for r in nonparity_always],
        "non-parity combiners binding from some lag on (or always)": len(nonparity_eventually),
        "non-parity examples binding from some lag on": [[r["rule_a"], r["rule_b"], r["m"], r["n"], r["name"], r["first binding lag"]]
                                                          for r in nonparity_eventually[:40]],
        "parity combiners: feedback against the listening counterpart": dict(sorted(table.items())),
        "examples where feedback changes the verdict": dict(examples),
        "rules (alike) binding at every lag under XOR at every declared size": sorted(
            r for r in reps if all((r, m, n) in xor_always for (m, n) in SIZES_ALIKE)),
        "longest repeat": max(row["repeat from"] + row["period"] for row in rows),
        "seconds": round(time.time() - t0, 1),
    }
    (OUT / "rows.json").write_text(json.dumps(rows, indent=0) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1)[:6000])


if __name__ == "__main__":
    main()
