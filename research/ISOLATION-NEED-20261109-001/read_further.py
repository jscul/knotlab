#!/usr/bin/env python3
"""Read further, as ISOLATION-NEED-20261109-001A-E001's frozen decision rule asks for a run that hears and stays balanced to its size
limit: the open doubling law every 2 and every 4 lags at g = 3, from 3 x 3, to 48 x 48 (2,400 rings), through ticket A's run.one.
Writes read_further.json beside this file."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "isolation_run", ROOT / "experiments/ISOLATION-NEED-20261109-001A/ISOLATION-NEED-20261109-001A-E001_hearing_and_balance/run.py")
R = importlib.util.module_from_spec(_spec)
sys.modules["isolation_run"] = R
_spec.loader.exec_module(R)   # its own "import run" then finds BIRTH-RULE-20261109-001A-E001's run.py

R.MAX_RINGS[3] = 2400


def main():
    t0 = time.time()
    with Pool(2) as pool:
        res = pool.map(R.one, [(3, "open", 2), (3, "open", 4)], chunksize=1)
    out = {"runs": res, "seconds": round(time.time() - t0)}
    (HERE / "read_further.json").write_text(json.dumps(out, indent=1) + "\n")
    for r in res:
        print(r["P"], [(d["side"], d["balanced"], d["hearing"]) for d in r["doublings"]], r["seconds"], "s", flush=True)


if __name__ == "__main__":
    main()
