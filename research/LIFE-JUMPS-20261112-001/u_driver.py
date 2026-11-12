"""Run the frozen census.task of LIFE-JUMPS-20261112-001A-E001 for the uniform settings on 100 and 200 distinctions in a third unit, so they
do not wait behind the uniform growths on 300 distinctions (22 to 67 minutes each). Same code, same seeds; written to
runs_u.jsonl and merged into runs.jsonl, keeping one record per (label, run), before the summary. Run from the repository root
with the workspace's .venv python: research/LIFE-JUMPS-20261112-001/u_driver.py --workers 6
"""

import json
import os
import sys
import time
from multiprocessing import Pool

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "LIFE-JUMPS-20261112-001A", "LIFE-JUMPS-20261112-001A-E001_whole_lives"))
workers = int(sys.argv[sys.argv.index("--workers") + 1])
sys.argv = [sys.argv[0]]
import census as C  # noqa: E402


def main():
    done = set()
    for name in ("runs.jsonl", "runs_xo.jsonl", "runs_u.jsonl"):
        p = os.path.join(C.OUT, name)
        if os.path.exists(p):
            for line in open(p):
                r = json.loads(line)
                done.add((r["label"], r["run"]))
    specs = [(lab, r) for lab, runs in C.SETTINGS if lab in ("U100", "U200") for r in range(runs) if (lab, r) not in done]
    C.log(f"u driver start {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC: {len(specs)} growths")
    t0 = time.time()
    with Pool(workers) as pool, open(os.path.join(C.OUT, "runs_u.jsonl"), "a") as f:
        for i, rec in enumerate(pool.imap_unordered(C.task, specs, chunksize=1)):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if (i + 1) % 50 == 0:
                C.log(f"u driver: {i + 1}/{len(specs)} growths, {time.time() - t0:.0f} s")
    C.log(f"u driver done {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC, {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
