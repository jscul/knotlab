#!/usr/bin/env python3
"""Stress test for GROW-CHOOSE-20261109-001, one size past ticket A's tubes (3 x 3, 3 x 4, 4 x 4 at g = 2, 3 x 3 at g = 3): the 3 x 5
and 5 x 3 tubes at g = 2 and the 3 x 4 tube at g = 3, four splits, the two first-cut rules (the order-free rule passes the 120-ring
limit at lag 2), lags 0 to 12, through ticket A's run.one. Checks H2 (from lag 3 on, allowed cuts only across the direction grown) and
H3 (lower, upper, copy: no growth after lag 2), and records where fresh growth stops. Writes stress_test.json beside this file."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth"))
import run as R  # noqa: E402

R.OUT = HERE / "stress_parts" / "x.json"


def main():
    t0 = time.time()
    jobs = [(tb, s, r) for tb in ((3, 5, 2), (5, 3, 2), (3, 4, 3)) for s in R.SPLITS for r in R.RULES[1:]]
    with Pool(8) as pool:
        res = pool.map(R.one, jobs, chunksize=1)
    h2 = [(x["tube"], x["split"], x["rule"], e["lag"]) for x in res for e in x["lags"]
          if "clean cuts" in e and e["lag"] >= 3 and len({k for k, a in e["clean cuts"]}) == 2]
    h3 = [(x["tube"], x["split"], x["rule"], e["lag"]) for x in res for e in x["lags"]
          if x["split"] != "fresh" and e.get("inserted") and e["lag"] > 2]
    fresh = {"%s, %s" % (x["tube"], x["rule"]): {"final": x["final"], "lags with growth": [e["lag"] for e in x["lags"] if e.get("inserted")],
             "unknown": sum(len(e.get("unknown cuts", [])) for e in x["lags"])} for x in res if x["split"] == "fresh"}
    out = {"H2 violations": h2, "H3 violations": h3, "fresh runs": fresh, "pass": not h2 and not h3, "seconds": round(time.time() - t0)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    for p in (HERE / "stress_parts").glob("*.json"):
        p.unlink()
    (HERE / "stress_parts").rmdir()
    print(json.dumps(out)[:1500])
    print("PASS" if out["pass"] else "FAIL")


if __name__ == "__main__":
    main()
