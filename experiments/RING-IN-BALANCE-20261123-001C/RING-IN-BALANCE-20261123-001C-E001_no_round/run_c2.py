"""C2: the birth-by-birth law (RATION-3, waiting) under ANY and DEAD on D2(4,3), D2(5,3), DW(5,3),
D2(6,3), Ring(5,3) and Ring(7,3); BY-GENERATION with each of its three tie rules and UNIFORM;
seeds 0-99; each run to 600 moves or 4,000 knots. 4,800 runs.

Usage: python -B run_c2.py [processes] [seeds]   -> c2_runs.jsonl (one line per run), c2_log.txt
"""

import json
import os
import resource
import sys
import time
from multiprocessing import Pool

import birth_by_birth as bb
from selfcheck import ART

STARTS = ["D2(4,3)", "D2(5,3)", "DW(5,3)", "D2(6,3)", "Ring(5,3)", "Ring(7,3)"]
MEM_CAP = 4 * 1024 ** 3


def jobs(nseeds=100):
    return [(st, rule, order, seed) for st in STARTS for rule in ("ANY", "DEAD") for order in bb.ORDERS
            for seed in range(nseeds)]


def one(job):
    st, rule, order, seed = job
    t0 = time.time()
    b = bb.BBB(st, rule, "RATION-3", "WAIT", order, seed=seed, run_id="C2")
    try:
        b.run(max_moves=600, max_knots=4000)
    except Exception as e:          # recorded, not hidden
        b.end = f"error: {type(e).__name__}: {e}"
    s = b.summary()
    s["wall_s"] = round(time.time() - t0, 3)
    s["maxrss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    return s


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP, MEM_CAP))


def main(nproc=8, nseeds=100):
    J = jobs(nseeds)
    t0 = time.time()
    with Pool(nproc, initializer=_limit) as pool:
        res = pool.map(one, J, chunksize=4)
    wall = time.time() - t0
    path = os.path.join(ART, "c2_runs.jsonl")
    with open(path, "w") as f:
        for r in res:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    peak = max(r["maxrss_mb"] for r in res)
    with open(os.path.join(ART, "c2_log.txt"), "w") as f:
        f.write(f"C2: {len(res)} runs, {wall:.1f} s wall on {nproc} processes, peak RSS {peak} MB\n")
    print("written", path, f"{wall:.1f} s, peak RSS {peak} MB")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8, int(sys.argv[2]) if len(sys.argv) > 2 else 100)
