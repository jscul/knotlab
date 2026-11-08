#!/usr/bin/env python3
"""One size past for PROCESS-CHAIN-20261108-001's census (research-next-steps, "Stress-Test Published Claims"), with the contacts
placed off the opposite point of the middle ring, so that the two ways round it have different lengths.

    .venv/bin/python3 -B research/PROCESS-CHAIN-20261108-001/stress_test.py   writes stress_test.json and stress_test_rows.json
Chains (4, 5, 4) and (5, 7, 5) have their contacts 2 and 3 cells apart one way and 3 and 4 the other; (5, 8, 5) has them opposite.
Reuses ticket B's run.py (job, holds_from) with 16 worker processes."""
import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/PROCESS-CHAIN-20261108-001B/PROCESS-CHAIN-20261108-001B-E001_chain_census"))
import run as B  # noqa: E402

T0 = time.time()
SIZES = ((4, 5, 4), (5, 7, 5), (5, 8, 5))


def main():
    reps = B.K.classes()
    laws = [("proposals", g2) for g2 in B.P.PARITIES] + [("self-blind", u) for u in B.S.NONCONSTANT_TWO]
    jobs = [(r, *size, fam, law) for size in SIZES for r in reps for fam, law in laws]
    jobs.sort(key=lambda j: -(j[1] + j[2] + j[3]))
    with Pool(16) as pool:
        rows = pool.map(B.job, jobs, chunksize=1)
    rec = [dict(zip(B.COLUMNS, row)) for row in rows]
    held = lambda x, t: bool(x[f"{t}: from"])
    out = {"sizes": [list(s) for s in SIZES], "configurations": len(rec)}
    for size in SIZES:
        sel = [x for x in rec if (x["mA"], x["mB"], x["mC"]) == size and x["repeat from"] is not None]
        both = [x for x in sel if held(x, "c1 binds A and B") and held(x, "c2 binds B and C")]
        out["/".join(map(str, size))] = {
            "decided": len(sel), "undecided": sum(1 for x in rec if (x["mA"], x["mB"], x["mC"]) == size and x["repeat from"] is None),
            "both contacts persist": len(both),
            "of those, c2 binds the ends from d + 1": sum(held(x, "c2 binds A and C") for x in both),
            "of those, both contacts bind the ends from d + 1": sum(held(x, "c1 binds A and C") and held(x, "c2 binds A and C") for x in both),
            "ends bound at c2 from d + 1, any": sum(held(x, "c2 binds A and C") for x in sel),
            "ends bound at c2 from d + 1, examples": [[x["rule"], x["family"], x["law"]] for x in sel if held(x, "c2 binds A and C")][:12],
            "rules with both contacts persistent": dict(Counter(x["rule"] for x in both).most_common(12))}
    out["seconds"] = round(time.time() - T0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    (HERE / "stress_test_rows.json").write_text(json.dumps({"columns": B.COLUMNS, "rows": rows}) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
