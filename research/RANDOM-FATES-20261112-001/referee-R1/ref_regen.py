#!/usr/bin/env python3
"""Referee RANDOM-FATES-R1: regenerate every growth of the census from its seed with the referee's own code, and compare with
runs.jsonl (death knot for U; dead, knots and size for the others). Also the five U300 runs still pending.

    python3 -B ref_regen.py    (writes result_regen.json)"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import ref_fates as F

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A = ROOT / "artifacts/RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census"
LABS = [f"X{q}" for q in (0.1, 0.2, 0.3, 0.35, 0.5)] + [f"Og{q}" for q in (0.0, 0.05, 0.1, 0.2, 0.3)] + \
       [f"Ol{q}" for q in (0.05, 0.1, 0.2, 0.3)] + [f"L{w}_{q}" for w in (4, 5, 6) for q in (0.3, 0.5, 0.7)]


def roster():
    out = [(f"U{n}", r) for n, k in ((50, 200), (100, 200), (200, 200), (300, 60)) for r in range(k)]
    out += [(l, r) for l in LABS for r in range(100)] + [("T", r) for r in range(30)]
    return out


def job(spec):
    lab, run = spec
    knots, dead = F.grow(lab, run)
    rec = {"label": lab, "run": run, "dead": dead, "knots": len(knots)}
    if lab.startswith("U"):
        rec["density"] = len(knots) / int(lab[1:])
    else:
        rec["n"] = max(v for t in knots for v in t) + 1
        if dead:
            rec["n_at_death"] = len({v for t in knots[:-1] for v in t})
    return rec


if __name__ == "__main__":
    t0 = time.time()
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 6) as pool:
        mine = pool.map(job, roster(), chunksize=4)
    theirs = {(r["label"], r["run"]): r for r in map(json.loads, open(A / "runs.jsonl"))}
    diffs, compared = [], 0
    for m in mine:
        t = theirs.get((m["label"], m["run"]))
        if t is None:
            continue
        compared += 1
        if m["label"].startswith("U"):
            same = t["dead"] and t["death_knot"] == m["knots"]
        else:
            same = t["dead"] == m["dead"] and t["knots"] == m["knots"] and t["n"] == m["n"] and \
                   (not m["dead"] or t["n_at_death"] == m["n_at_death"])
        if not same:
            diffs.append([m, {k: t.get(k) for k in ("dead", "death_knot", "knots", "n", "n_at_death")}])
    pending = [m for m in mine if (m["label"], m["run"]) not in theirs]
    res = {"regenerated": len(mine), "compared": compared, "differences": diffs, "pending runs, regenerated": pending,
           "seconds": round(time.time() - t0, 1)}
    (HERE / "result_regen.json").write_text(json.dumps(res, indent=1) + "\n")
    print("compared", compared, "differences", len(diffs), "seconds", res["seconds"])
