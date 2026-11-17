"""Task 1 extension: the stress cell rand n = 12800 (cap 2e9), the referee's Novelty+ at the study's
re-tuned parameters (0.7, 0.05) on the study's 50 stress instances (seeds 3,000,000 + i), two runs each,
compared with the study's novelty_plus@cell runs (stress/results.jsonl)."""
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import referee_common as C  # noqa: E402


def job(a):
    s, rep = a
    r = C.run("rand", 12800, s, "novelty_plus", (0.7, 0.05), C.seed_of("task1x", 12800, s, rep), 2 * 10**9)
    return s, rep, r["flips"], r["solved"], r["cpu"]


if __name__ == "__main__":
    t0 = time.time()
    S = C.study_results(C.ART / "stress/results.jsonl")[("rand", 12800, "novelty_plus@cell")]
    assert all(tuple(v[2]) == (0.7, 0.05) for v in S.values())
    seeds = sorted(S)
    for s in seeds:
        C.instance("rand", 12800, s)
    res = C.pool_map(job, [(s, r) for s in seeds for r in range(2)])
    mine = {}
    for s, r, fl, ok, c in sorted(res):
        mine.setdefault(s, []).append(fl)
    theirs = {s: [S[s][0]] for s in seeds}
    out = {"task": "1 extension: rand n = 12800 Novelty+ (0.7, 0.05)", "instances": len(seeds),
           "study_median": float(np.median([S[s][0] for s in seeds])),
           "referee_median_run0": float(np.median([mine[s][0] for s in seeds])),
           "referee_median_all": float(np.median(np.concatenate([mine[s] for s in seeds]))),
           "referee_unsolved": int(sum(not r[3] for r in res)),
           "ratio_run0": C.median_ratio_boot({s: [mine[s][0]] for s in seeds}, theirs),
           "ratio_all": C.median_ratio_boot(mine, theirs),
           "mwu_run0": C.mwu([mine[s][0] for s in seeds], [S[s][0] for s in seeds]),
           "cpu_s": float(sum(r[4] for r in res)), "wall_s": time.time() - t0,
           "flips_by_instance": {str(s): mine[s] for s in seeds}}
    C.jdump(out, C.HERE / "referee_task1_rand12800.json")
    print({k: v for k, v in out.items() if k != "flips_by_instance"})
