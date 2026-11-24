"""C1: the part-round law with the two and the three added rules on D2(4,3), D2(5,3) and Ring(5,3)
under each of the seven priorities; seeds 0-19 for the priorities with a random choice (every
priority but ALL-IN-TURN, since ties are uniform), one run for ALL-IN-TURN. A run goes on until the
part that returns has returned 12 times, 4,000 moves or 20,000 knots. 726 runs.

Usage: python -B run_c1.py [processes]      -> c1_results.json, c1_log.txt
"""

import json
import os
import resource
import sys
import time
from multiprocessing import Pool

import growth as g
import iso
import part_round as pr
from selfcheck import ART

STARTS = ["D2(4,3)", "D2(5,3)", "Ring(5,3)"]
MEM_CAP = 4 * 1024 ** 3


def jobs():
    out = []
    for start in STARTS:
        for law in ("two", "three"):
            for prio in pr.PRIORITIES:
                seeds = [0] if prio == "ALL-IN-TURN" else list(range(20))
                for seed in seeds:
                    out.append((start, law, prio, seed))
    return out


def one(job):
    start, law, prio, seed = job
    t0 = time.time()
    run = pr.PartRoundRun(start, g.LAWS[law], prio, seed=seed, run_id="C1")
    try:
        run.run()
    except Exception as e:          # e.g. growth.PartInteraction: recorded, not hidden
        run.end = f"error: {type(e).__name__}: {e}"
        run.run_time = time.time() - t0
    a = run.analysis()
    a["p2"] = pr.p2_check(run)
    a.update({"start": start, "law": law, "priority": prio, "seed": seed, "n_start": int(start.split("(")[1].split(",")[0]),
              "wall_s": round(time.time() - t0, 3),
              "maxrss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)})
    return a


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP, MEM_CAP))


def main(nproc=8):
    J = jobs()
    t0 = time.time()
    with Pool(nproc, initializer=_limit) as pool:
        res = pool.map(one, J, chunksize=1)
    wall = time.time() - t0
    out = {"runs": res, "wall_s": round(wall, 1), "processes": nproc,
           "peak_maxrss_mb": max(r["maxrss_mb"] for r in res), "n_runs": len(res)}
    path = os.path.join(ART, "c1_results.json")
    with open(path, "w") as f:
        json.dump(out, f)
    with open(os.path.join(ART, "c1_log.txt"), "w") as f:
        f.write(f"C1: {len(res)} runs, {wall:.1f} s wall on {nproc} processes, peak RSS {out['peak_maxrss_mb']} MB\n")
        for r in res:
            f.write(f"{r['start']} {r['law']} {r['priority']} seed {r['seed']}: end {r['end']}, moves {r['moves']}, "
                    f"knots {r['knots']}, returns {len(r['returns'])}, R {r['p2']['R']}, P2 same {r['p2']['same']}, "
                    f"{r['wall_s']} s\n")
    print("written", path, f"{wall:.1f} s")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
