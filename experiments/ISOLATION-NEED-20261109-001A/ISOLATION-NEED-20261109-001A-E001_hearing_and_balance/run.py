#!/usr/bin/env python3
"""Run ISOLATION-NEED-20261109-001A-E001 (frozen contract beside this file): hearing and balance under the doubling law.

    .venv/bin/python3 -B run.py
On BIRTH-RULE-20261109-001A-E001's run.py (its double(), readings() and hearing(), every born cell a variable, persistence through a
full cycle of the state). 8 worker processes, one per (g, rule, P). Writes
artifacts/ISOLATION-NEED-20261109-001A/ISOLATION-NEED-20261109-001A-E001_hearing_and_balance/run/result.json."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules"))
import run as B  # noqa: E402

C = B.C
OUT = ROOT / "artifacts/ISOLATION-NEED-20261109-001A/ISOLATION-NEED-20261109-001A-E001_hearing_and_balance/run/result.json"
JOBS = [(2, rule, P) for rule in ("open", "open plus copy") for P in range(1, 9)] + \
       [(3, rule, P) for rule in ("open", "open plus copy") for P in range(1, 5)]
MAX_RINGS = {2: 2400, 3: 600}


def one(job):
    g, rule, P = job
    t0 = time.time()
    run = C.Run2(C.Tube2([0, 1, 2], [0, 1, 2], g))
    t, rows = 0, []
    while len(run.tube.rings) * 4 <= MAX_RINGS[g] or t % P:
        if t % P == 0:
            old = B.double(run, t, rule)
            bal, oldb = B.readings(run, old)
            rows.append({"lag": t, "side": len(run.tube.cols), "balanced": bal, "hearing": B.hearing(run)})
            if bal is False:
                break
        run.step()
        t += 1
    first_hear = next((k for k, r in enumerate(rows) if r["hearing"] > 0), None)
    first_unbal = next((k for k, r in enumerate(rows) if r["balanced"] is False), None)
    delay = None if first_hear is None or first_unbal is None else first_unbal - first_hear
    return {"g": g, "rule": rule, "P": P, "doublings": rows, "first doubling with hearing": first_hear,
            "first unbalanced doubling": first_unbal, "delay": delay, "seconds": round(time.time() - t0, 1)}


def main():
    with Pool(8) as pool:
        res = pool.map(one, JOBS, chunksize=1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"experiment_id": "ISOLATION-NEED-20261109-001A-E001", "runs": res}, indent=1) + "\n")
    for r in res:
        print("g", r["g"], r["rule"], "P", r["P"], "hear", r["first doubling with hearing"], "unbalanced", r["first unbalanced doubling"],
              "delay", r["delay"], [(d["side"], d["balanced"], d["hearing"]) for d in r["doublings"]], r["seconds"], "s")


if __name__ == "__main__":
    main()
