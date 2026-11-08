#!/usr/bin/env python3
"""One size past for PROCESS-CONTACT-20261108-001's computed claims (research-next-steps, "Stress-Test Published Claims"), and an
independent recheck of the census at later lags.

    .venv/bin/python3 -B research/PROCESS-CONTACT-20261108-001/stress_test.py recheck   census rows against direct simulation
                                                                                     and minimally decisive sets (recheck.json)
    .venv/bin/python3 -B research/PROCESS-CONTACT-20261108-001/stress_test.py larger    the census one size past (larger.json)
Reuses ticket A's library and ticket B's run.py (job, classify), with 16 worker processes."""
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/PROCESS-CONTACT-20261108-001A/PROCESS-CONTACT-20261108-001A-P001_which_contacts_bind_two_processes"))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
sys.path.insert(0, str(ROOT / "experiments/PROCESS-CONTACT-20261108-001B/PROCESS-CONTACT-20261108-001B-E001_figure_eight_census"))
import process_contact_lib as P  # noqa: E402
import time_knots_lib as K  # noqa: E402
import run as B  # noqa: E402

ROWS = ROOT / "artifacts/PROCESS-CONTACT-20261108-001B/PROCESS-CONTACT-20261108-001B-E001_figure_eight_census/run/rows.json"
T0 = time.time()


def centre_canalizing(r):
    f = lambda l, s, c: (r >> (4 * l + 2 * s + c)) & 1
    return any(len({f(l, s, c) for l in (0, 1) for c in (0, 1)}) == 1 for s in (0, 1))


def recheck_row(row):
    m, n = row["m"], row["n"]
    sa, sb, own = P.shared_sides(m, n)
    N = m + n - 1
    lags = min(6, row["lags computed"])
    maps = P.shared_maps(row["rule_a"], m, row["rule_b"], n, row["combiner"], lags)
    side = "".join("1" if P.binds(F, sa, sb, own, N) else "0" for F in maps)
    knots = "".join("1" if P.binds_by_knots(F, sa, sb, N, K.knots_across_time) else "0" for F in maps) if N <= 8 else side
    return side == row["verdicts"][:lags] and knots == side


def recheck():
    rows = json.loads(ROWS.read_text())
    rng = random.Random(20261108)
    small = [r for r in rows if r["m"] + r["n"] - 1 <= 8]
    pick = rng.sample(small, 400) + rng.sample([r for r in rows if r["m"] == 5], 100)
    with Pool(16) as pool:
        ok = pool.map(recheck_row, pick, chunksize=8)
    out = {"rows rechecked": len(pick), "agree": sum(ok), "lags": "1 to 6 (or to the repeat)",
           "how": "direct simulation (shared_maps) against the census's state-map iteration; minimally decisive sets when the first "
                  "row has at most 8 cells", "seconds": round(time.time() - T0, 1)}
    (HERE / "recheck.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


CAP = 4096


def capped_job(args):
    """ticket B's job, but a configuration whose T-step map has not repeated within CAP lags is reported as undecided, with its
    verdicts over the lags computed (ticket B's sizes never needed more than 3,865)"""
    kind, ra, rb, m, n, g2 = args
    sa, sb, own = P.shared_sides(m, n)
    N = m + n - 1
    nxt = P.shared_state_maps(ra, m, rb, n, g2)
    cur = list(range(len(nxt)))
    import numpy as np
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, verdicts = {}, []
    for T in range(1, CAP + 1):
        cur = nxt[cur]
        key = cur.tobytes()
        if key in seen:
            T1 = seen[key]
            return {"kind": kind, "rule_a": ra, "rule_b": rb, "m": m, "n": n, "combiner": g2, "name": P.two_input_name(g2),
                    "class": B.classify(verdicts, T1, T - T1), "repeat from": T1, "period": T - T1,
                    "first binding lag": next((t for t, v in enumerate(verdicts, 1) if v), None),
                    "verdicts": "".join("1" if v else "0" for v in verdicts[:64])}
        seen[key] = T
        verdicts.append(P.binds(((cur >> 0) & 1).astype(np.uint8), sa, sb, own, N))
    return {"kind": kind, "rule_a": ra, "rule_b": rb, "m": m, "n": n, "combiner": g2, "name": P.two_input_name(g2),
            "class": "undecided: no repeat within %d lags" % CAP, "repeat from": None, "period": None,
            "bound at every computed lag": all(verdicts), "bound at some computed lag": any(verdicts),
            "bound at the last 100 computed lags": all(verdicts[-100:]),
            "first binding lag": next((t for t, v in enumerate(verdicts, 1) if v), None),
            "verdicts": "".join("1" if v else "0" for v in verdicts[:64])}


def larger():
    reps = K.classes()
    jobs = [("alike", r, r, 6, 7, g2) for r in reps for g2 in P.TWO_INPUT]
    jobs += [("mixed", ra, rb, 4, 5, g2) for ra in reps for rb in reps for g2 in (0b0110, 0b1001, 0b1110, 0b1000, 0b0111, 0b0001, 0b1101, 0b1011)
             if ra != rb]
    with Pool(16) as pool:
        rows = pool.map(capped_job, jobs, chunksize=8)
    par = [r for r in rows if r["combiner"] in P.PARITIES]
    lag1 = all((r["verdicts"][0] == "1") == (r["combiner"] in P.PARITIES and not centre_canalizing(r["rule_a"])
                                              and not centre_canalizing(r["rule_b"])) for r in rows)
    keep = {(r, m): B.ring_cell_nonconstant_always(r, m) for r in reps for m in (4, 5, 6, 7)}
    table = Counter()
    for r in par:
        cp = keep[(r["rule_a"], r["m"])] and keep[(r["rule_b"], r["n"])]
        sh = r["class"] == "binds at every lag"
        table[f"listening {'binds' if cp else 'fails'} at every lag, shared {'binds' if sh else 'fails'}"] += 1
    out = {
        "configurations": len(rows),
        "lag 1: binds exactly for a parity combiner with neither rule canalizing at its centre": lag1,
        "classes (alike, 6 + 7 cells), parity combiners": dict(Counter(r["class"] for r in par if r["kind"] == "alike")),
        "classes (mixed, 4 + 5 cells), parity combiners": dict(Counter(r["class"] for r in par if r["kind"] == "mixed")),
        "binding at every lag": [[r["rule_a"], r["rule_b"], r["m"], r["n"], r["name"]] for r in rows if r["class"] == "binds at every lag"],
        "non-parity combiners binding from some lag on": [[r["rule_a"], r["rule_b"], r["m"], r["n"], r["name"], r["first binding lag"]]
                                                          for r in rows if r["combiner"] not in P.PARITIES
                                                          and r["class"] == "binds from some lag on"],
        "parity combiners: feedback against the listening counterpart": dict(sorted(table.items())),
        "longest repeat": max(r["repeat from"] + r["period"] for r in rows if r["repeat from"]),
        "undecided (no repeat within the cap)": [[r["rule_a"], r["rule_b"], r["m"], r["n"], r["name"], r["bound at every computed lag"],
                                                 r["bound at the last 100 computed lags"]] for r in rows if r["repeat from"] is None],
        "seconds": round(time.time() - T0, 1),
    }
    (HERE / "larger.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: (v if not isinstance(v, list) else f"{len(v)} items") for k, v in out.items()}, indent=1))


def theorem3_job(r):
    import numpy as np
    m, n = 6, 6
    sa, sb, own = P.listening_sides(m, n)
    HA, HB = P.ring_contact_history(r, m, 10), P.ring_contact_history(r, n, 10)
    bad = tested = 0
    for g2 in range(16):
        for T, F in enumerate(P.listening_maps(r, m, r, n, P.memoryless(g2), 10), start=1):
            nonconst = bool(HA[:, T - 1].min() != HA[:, T - 1].max() and HB[:, T - 1].min() != HB[:, T - 1].max())
            tested += 1
            bad += P.binds(F, sa, sb, own, m + n + 1) != ((g2 in P.PARITIES) and nonconst)
    return tested, bad


def memory_job(args):
    g, r = args
    import numpy as np
    m, n = 4, 5
    sa, sb, own = P.listening_sides(m, n)
    nxt = P.listening_state_map(r, m, r, n, g)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, verdicts = {}, []
    for T in range(1, CAP + 1):
        cur = nxt[cur]
        key = cur.tobytes()
        if key in seen:
            T1 = seen[key]
            return g, r, (not verdicts[0]) and P.at_every_lag(verdicts, T1, T - T1, 2), verdicts[0], True
        seen[key] = T
        verdicts.append(P.binds(((cur >> (m + n)) & 1).astype(np.uint8), sa, sb, own, m + n + 1))
    return g, r, False, verdicts[0], False


def ticket_a():
    reps = K.classes()
    with Pool(16) as pool:
        t3 = pool.map(theorem3_job, reps)
        mem = pool.map(memory_job, [(g, r) for g in range(256) for r in reps], chunksize=16)
    later = sorted({g for g, r, ok, _, _ in mem if ok})
    lag1 = sorted({g for g, r, _, v1, _ in mem if v1})
    out = {"Theorem 3 at 6 + 6 cells, T = 1..10, all 88 classes alike, all 16 laws": {"maps": sum(t for t, _ in t3),
                                                                                     "mismatches": sum(b for _, b in t3)},
           "lag-1 binding laws at 4 + 5 cells": lag1,
           "laws binding at every lag from 2 on but not at 1, at 4 + 5 cells (some rule)": len(later),
           "undecided within the cap": sum(1 for *_, done in mem if not done),
           "seconds": round(time.time() - T0, 1)}
    (HERE / "ticket_a.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"recheck": recheck, "larger": larger, "ticket_a": ticket_a}[sys.argv[1]]()
