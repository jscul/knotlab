#!/usr/bin/env python3
"""Run SPACING-20261109-001A-E001 (frozen contract beside this file): balance and borders at spacings 4 and 5.

    .venv/bin/python3 -B run.py
Balance and hearing through ISOLATION-NEED-20261109-001A-E001's run.one (every born cell a variable, persistence through a full cycle of
the state, to 24 x 24); reach through GROW-HEAR-20261109-001A-E001's growing (horizon_lib, to 96 x 96). 8 worker processes. Writes
artifacts/SPACING-20261109-001A/SPACING-20261109-001A-E001_borders/run/result.json."""
import importlib.util
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ISO = load("isolation_run", "experiments/ISOLATION-NEED-20261109-001A/ISOLATION-NEED-20261109-001A-E001_hearing_and_balance/run.py")
HEAR = load("hear_run", "experiments/GROW-HEAR-20261109-001A/GROW-HEAR-20261109-001A-E001_hearing_reach/run.py")
ISO.MAX_RINGS.update({4: 600, 5: 600})
JOBS = [(g, "open", P) for g in (4, 5) for P in (1, 2, 3, 4)]
OUT = ROOT / "artifacts/SPACING-20261109-001A/SPACING-20261109-001A-E001_borders/run/result.json"


def both(job):
    g, rule, P = job
    bal = ISO.one(job)
    reach = HEAR.growing(g, P)
    reach.pop("reach by lag", None)
    return {"g": g, "P": P, "balance": bal, "reach": reach}


def main():
    t0 = time.time()
    with Pool(8) as pool:
        res = pool.map(both, JOBS, chunksize=1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"experiment_id": "SPACING-20261109-001A-E001", "runs": res, "seconds": round(time.time() - t0)},
                              indent=1, default=str) + "\n")
    for r in res:
        b, h = r["balance"], r["reach"]
        print("g", r["g"], "P", r["P"], [(d["side"], d["balanced"], d["hearing"]) for d in b["doublings"]],
              "max reach", h["largest reach"], "heard by", h["original rings that ever hear it (distance, first lag)"], b["seconds"], "s")


if __name__ == "__main__":
    main()
