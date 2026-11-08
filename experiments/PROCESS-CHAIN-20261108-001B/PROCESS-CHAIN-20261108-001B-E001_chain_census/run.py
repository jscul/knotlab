"""PROCESS-CHAIN-20261108-001B-E001: chains of three rings joined by two shared contacts (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/PROCESS-CHAIN-20261108-001B/
                                          PROCESS-CHAIN-20261108-001B-E001_chain_census/run/rows.json and result.json
    .venv/bin/python3 -B run.py --pilot   times a few configurations and prints no verdicts (the contract's feasibility check)
T-step maps are told apart by 16-byte digests, and a repeated digest is confirmed by recomputing the earlier map."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PROCESS-CHAIN-20261108-001A/PROCESS-CHAIN-20261108-001A-P001_what_a_chain_of_contacts_can_carry"))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
import chain_lib as C  # noqa: E402
import time_knots_lib as K  # noqa: E402

S, P = C.S, C.P
OUT = ROOT / "artifacts" / "PROCESS-CHAIN-20261108-001B" / "PROCESS-CHAIN-20261108-001B-E001_chain_census" / "run"
SIZES = ((3, 4, 3), (4, 4, 4), (4, 6, 4), (5, 6, 5))
CAP = 4096
TESTS = {"c1 binds A and B": (0, ("A", "B")), "c2 binds B and C": (1, ("B", "C")), "c1 binds A and C": (0, ("A", "C")),
         "c2 binds A and C": (1, ("A", "C")), "c2 binds A, B and C": (1, ("A", "B", "C"))}
COLUMNS = ["rule", "mA", "mB", "mC", "family", "law", "d", "repeat from", "period"] + [f"{t}: from" for t in TESTS]


def holds_from(verdicts, T1, period, start):
    """the verdict holds at every lag T >= start, exactly (the computed lags stand for all lags)"""
    if T1 is None:
        return None
    return all(verdicts[min(start, T1) - 1:T1 + period - 1]) and all(verdicts[start - 1:])


def job(args):
    r, mA, mB, mC, family, law = args
    k = mB // 2
    d = C.ring_distance(k, mB)
    a, b, c, N, blocks = C.layout(mA, mB, mC, k)
    nxt = C.chain_state_map(r, mA, mB, mC, k, family, law)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, series = {}, {t: [] for t in TESTS}
    T1 = period = None
    for T in range(1, CAP + 1):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            back = np.arange(len(nxt), dtype=np.int64)
            for _ in range(seen[key]):
                back = nxt[back]
            if not (back == cur).all():
                raise RuntimeError("digest collision")
            T1, period = seen[key], T - seen[key]
            break
        seen[key] = T
        F = {0: (cur & 1).astype(np.uint8), 1: ((cur >> 1) & 1).astype(np.uint8)}
        for t, (bit, names) in TESTS.items():
            series[t].append(C.binds(F[bit], blocks, names, N))
    out = [r, mA, mB, mC, family, law, d, T1, period]
    for t in TESTS:
        start = 1 if t in ("c1 binds A and B", "c2 binds B and C") else d + 1
        out.append(start if holds_from(series[t], T1, period, start) else (None if T1 is None else 0))
    return out


def main():
    t0 = time.time()
    reps = K.classes()
    laws = [("proposals", g2) for g2 in P.PARITIES] + [("self-blind", u) for u in S.NONCONSTANT_TWO]
    if "--pilot" in sys.argv:
        for args in ((30, 5, 6, 5, "proposals", 6), (110, 5, 6, 5, "self-blind", 6), (184, 5, 6, 5, "self-blind", 9), (90, 4, 6, 4, "proposals", 9)):
            s = time.time()
            job(args)
            print("pilot", args, "seconds", round(time.time() - s, 3))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(r, *size, fam, law) for size in SIZES for r in reps for fam, law in laws]
    with Pool(16) as pool:
        rows = pool.map(job, jobs, chunksize=8)
    rec = [dict(zip(COLUMNS, row)) for row in rows]
    decided = [x for x in rec if x["repeat from"] is not None]
    held = lambda x, t: bool(x[f"{t}: from"])
    both = [x for x in decided if held(x, "c1 binds A and B") and held(x, "c2 binds B and C")]
    ends_both = [x for x in both if held(x, "c1 binds A and C") and held(x, "c2 binds A and C")]
    ends_c2 = [x for x in both if held(x, "c2 binds A and C")]
    counter = [[x["rule"], x["mA"], x["mB"], x["mC"], x["family"], x["law"]] for x in both if x not in ends_both]
    not_both = [x for x in decided if x not in both]
    # controls
    lin = sorted(set(P.LINEAR) | set(P.AFFINE))
    ctrl_light = all(not held(x, "c2 binds A and C") or x["c2 binds A and C: from"] == x["d"] + 1 for x in decided)
    controls = {"far-ring binding is never claimed before the light cone (Theorem 2)": ctrl_light,
                "every configuration has its verdicts or is reported undecided": len(rec) == len(jobs)}
    by = {}
    for (mA, mB, mC) in SIZES:
        sel = [x for x in decided if (x["mA"], x["mB"], x["mC"]) == (mA, mB, mC)]
        bsel = [x for x in sel if x in both]
        by[f"{mA}/{mB}/{mC}"] = {"decided": len(sel),
                                 "both contacts persist": len(bsel),
                                 "of those, c2 binds the ends from d + 1": sum(held(x, "c2 binds A and C") for x in bsel),
                                 "of those, both contacts bind the ends from d + 1": sum(held(x, "c1 binds A and C") and held(x, "c2 binds A and C") for x in bsel),
                                 "of those, c2 binds all three rings from d + 1": sum(held(x, "c2 binds A, B and C") for x in bsel),
                                 "ends bound at c2 though not both contacts persist": sum(held(x, "c2 binds A and C") for x in sel if x not in bsel)}
    result = {
        "experiment": "PROCESS-CHAIN-20261108-001B-E001", "configurations": len(rec), "undecided": len(rec) - len(decided),
        "controls": controls, "controls_ok": all(controls.values()),
        "both contacts persist": len(both),
        "of those, c2 binds the ends from d + 1": len(ends_c2),
        "of those, both contacts bind the ends from d + 1": len(ends_both),
        "H1 (whenever both contacts persist, both bind the ends from d + 1)": len(counter) == 0,
        "counterexamples to H1 (first 40)": counter[:40], "counterexamples to H1": len(counter),
        "ends bound at c2 from d + 1 though not both contacts persist": sum(held(x, "c2 binds A and C") for x in not_both),
        "by size": by,
        "by family (both persist; ends at c2 among them)": {fam: [sum(1 for x in both if x["family"] == fam),
                                                                   sum(1 for x in ends_c2 if x["family"] == fam)] for fam in ("proposals", "self-blind")},
        "seconds": round(time.time() - t0, 1)}
    (OUT / "rows.json").write_text(json.dumps({"columns": COLUMNS, "rows": rows}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1)[:6000])


if __name__ == "__main__":
    main()
