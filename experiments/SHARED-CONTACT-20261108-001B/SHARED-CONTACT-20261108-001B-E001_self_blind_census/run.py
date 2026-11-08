"""SHARED-CONTACT-20261108-001B-E001: shared contacts that do not read themselves (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/SHARED-CONTACT-20261108-001B/
                                          SHARED-CONTACT-20261108-001B-E001_self_blind_census/run/rows.json and result.json
    .venv/bin/python3 -B run.py --pilot   times a few configurations and prints no verdicts (the contract's feasibility check)"""
from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SHARED-CONTACT-20261108-001A/SHARED-CONTACT-20261108-001A-P001_when_a_shared_contact_binds_at_the_first_step"))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
import shared_contact_lib as S  # noqa: E402
import time_knots_lib as K  # noqa: E402

P = S.P
OUT = ROOT / "artifacts" / "SHARED-CONTACT-20261108-001B" / "SHARED-CONTACT-20261108-001B-E001_self_blind_census" / "run"
PROPOSALS = ROOT / "artifacts/PROCESS-CONTACT-20261108-001B/PROCESS-CONTACT-20261108-001B-E001_figure_eight_census/run/rows.json"
SIZES = ((3, 4), (4, 4), (4, 5), (5, 6))
CAP = 4096
COLUMNS = ["rule", "m", "n", "u", "v", "class", "first lag without binding", "repeat from", "period", "lags computed"]


def job(args):
    r, m, n, u, v = args
    nxt = S.selfblind_state_map(r, m, r, n, S.parity_table(u, v))
    verdicts, T1, period = S.lags_capped(nxt, lambda F: S.fast_binds(F, m, n), CAP)
    first_fail = next((T for T, ok in enumerate(verdicts, 1) if not ok), None)
    return [r, m, n, u, v, S.classify(verdicts, T1, period), first_fail, T1, period, len(verdicts)]


def main():
    t0 = time.time()
    reps = K.classes()
    if "--pilot" in sys.argv:
        for (r, m, n, u, v) in ((30, 5, 6, 6, 6), (110, 5, 6, 8, 14), (184, 5, 6, 6, 9), (90, 5, 6, 6, 6), (54, 3, 4, 12, 3)):
            s = time.time()
            row = job((r, m, n, u, v))
            print("pilot", r, m, n, u, v, "lags computed", row[-1], "seconds", round(time.time() - s, 3))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(r, m, n, u, v) for (m, n) in SIZES for r in reps for u in S.NONCONSTANT_TWO for v in S.NONCONSTANT_TWO]
    with Pool(16) as pool:
        rows = pool.map(job, jobs, chunksize=64)
    rec = [dict(zip(COLUMNS, row)) for row in rows]
    # controls
    lin = sorted(set(P.LINEAR) | set(P.AFFINE))
    ctrl_lin = []
    for row in rec:
        if row["rule"] in lin and row["u"] in S.AFFINE_TWO and row["v"] in S.AFFINE_TWO and row["repeat from"]:
            m, n = row["m"], row["n"]
            nxt = S.selfblind_state_map(row["rule"], m, row["rule"], n, S.parity_table(row["u"], row["v"]))
            sa, sb, _ = P.shared_sides(m, n)
            rws = S.affine_contact_row(nxt, m + n - 1, row["lags computed"])
            pred = [bool(x & sa) and bool(x & sb) for x in rws]
            first = next((T for T, ok in enumerate(pred, 1) if not ok), None)
            ctrl_lin.append(first == row["first lag without binding"])
    ctrl_lag1 = all(row["first lag without binding"] != 1 for row in rec)      # Theorem 2: every u + v with u, v nonconstant binds at lag 1
    rng = random.Random(20261108)
    ctrl_impl = []
    for row in rng.sample(rec, 300):
        m, n = row["m"], row["n"]
        h = S.parity_table(row["u"], row["v"])
        L = min(8, row["lags computed"])
        maps = S.selfblind_maps(row["rule"], m, row["rule"], n, h, L)
        sa, sb, own = P.shared_sides(m, n)
        direct = next((T for T, F in enumerate(maps, 1) if not P.binds(F, sa, sb, own, m + n - 1)), None)
        recorded = row["first lag without binding"] if (row["first lag without binding"] or 10 ** 9) <= L else None
        ctrl_impl.append(direct == recorded)
    controls = {"linear and affine rules with affine u, v follow the M^T row": bool(ctrl_lin) and all(ctrl_lin),
                "every configuration binds at lag 1 (Theorem 2)": ctrl_lag1,
                "direct simulation and process_contact_lib.binds agree on 300 sampled rows to lag 8": all(ctrl_impl)}
    # primary observable
    classes = Counter(row["class"] for row in rec)
    by_size = {f"{m} + {n}": dict(Counter(row["class"] for row in rec if (row["m"], row["n"]) == (m, n))) for (m, n) in SIZES}
    always = [row for row in rec if row["class"] == "binds at every lag"]
    frac_sb = len(always) / len(rec)
    prop = json.loads(PROPOSALS.read_text())
    prop_par = [r for r in prop if r["kind"] == "alike" and r["combiner"] in P.PARITIES]
    frac_prop = sum(r["class"] == "binds at every lag" for r in prop_par) / len(prop_par)
    pairs_sb = {(row["rule"], row["m"], row["n"]) for row in always}
    pairs_prop = {(r["rule_a"], r["m"], r["n"]) for r in prop_par if r["class"] == "binds at every lag"}
    per_rule = defaultdict(int)
    for row in always:
        per_rule[row["rule"]] += 1
    result = {
        "experiment": "SHARED-CONTACT-20261108-001B-E001", "configurations": len(rec), "controls": controls,
        "controls_ok": all(controls.values()),
        "classes": dict(sorted(classes.items())), "classes by size": by_size,
        "self-blind configurations binding at every lag": len(always),
        "fraction binding at every lag: self-blind parities": round(frac_sb, 5),
        "fraction binding at every lag: proposal parities on the same rings (PROCESS-CONTACT-20261108-001B)": round(frac_prop, 5),
        "H1 (self-blind at least twice the proposal fraction)": frac_sb >= 2 * frac_prop,
        "(rule, size) pairs with some persistent law: self-blind": len(pairs_sb),
        "(rule, size) pairs with some persistent law: proposals": len(pairs_prop),
        "pairs persistent under proposals but under no self-blind law": sorted(pairs_prop - pairs_sb),
        "rules with a persistent self-blind law at every size": sorted(r for r in reps if all((r, m, n) in pairs_sb for (m, n) in SIZES)),
        "persistent self-blind laws per rule (top 20)": dict(sorted(per_rule.items(), key=lambda kv: -kv[1])[:20]),
        "undecided within the cap": classes.get("undecided", 0),
        "seconds": round(time.time() - t0, 1),
    }
    (OUT / "rows.json").write_text(json.dumps({"columns": COLUMNS, "rows": rows}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1)[:5000])


if __name__ == "__main__":
    main()
