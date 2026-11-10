#!/usr/bin/env python3
"""Run CROSS-BORDER-20261110-001A-E001 (frozen contract beside this file): slower doubling at odd spacings, borders and balance.

    .venv/bin/python3 -B run.py
Through SPACING-20261109-001A-E001's run.py (balance and hearing by ISOLATION-NEED-20261109-001A-E001's run.one to 24 x 24; reach and the
original rings hearing ring (0, 0) by GROW-HEAR-20261109-001A-E001's growing to 96 x 96). 8 worker processes. Writes
artifacts/CROSS-BORDER-20261110-001A/CROSS-BORDER-20261110-001A-E001_slow_doubling/run/result.json."""
import importlib.util
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("spacing_run", ROOT / "experiments/SPACING-20261109-001A/SPACING-20261109-001A-E001_borders/run.py")
S = importlib.util.module_from_spec(spec)
sys.modules["spacing_run"] = S
spec.loader.exec_module(S)
S.ISO.MAX_RINGS.update({3: 600, 5: 600})
JOBS = [(g, "open", P) for g in (3, 5) for P in (6, 8, 12, 16)]
OUT = ROOT / "artifacts/CROSS-BORDER-20261110-001A/CROSS-BORDER-20261110-001A-E001_slow_doubling/run/result.json"


def main():
    t0 = time.time()
    with Pool(8) as pool:
        res = pool.map(S.both, JOBS, chunksize=1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"experiment_id": "CROSS-BORDER-20261110-001A-E001", "runs": res, "seconds": round(time.time() - t0)},
                              indent=1, default=str) + "\n")
    for r in res:
        b, h = r["balance"], r["reach"]
        print("g", r["g"], "P", r["P"], [(d["side"], d["balanced"], d["hearing"]) for d in b["doublings"]],
              "max reach", h["largest reach"], "heard by", h["original rings that ever hear it (distance, first lag)"], b["seconds"], "s", flush=True)


if __name__ == "__main__":
    main()
