"""EARN-BUDGET-R1 task 2b: the referee's tuning picked (0.8, 0), the study's own choice, so the asked test "best vs (0.8, 0)"
compares a setting with itself. Here the next three by the referee's tuning score, (0.75, 0.005), (0.775, 0.005) and
(0.775, 0.0), are run against (0.8, 0) on the same 20 test instances x 3 runs as task 2 (same engine, seeds and cap).
Paired ratio of medians of per-instance geometric-mean work, bootstrap 99%. Output: referee_earn_task2b_runnersup.json.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

import referee_earn_task2_grid_edge as T  # noqa: E402

SETTINGS = [(0.8, 0.0), (0.75, 0.005), (0.775, 0.005), (0.775, 0.0)]


def main():
    from multiprocessing import Pool
    t0 = time.time()
    seeds = [8_100_000 + i for i in range(20)]
    jobs = [(p, wp, s, r, T.TEST_CAP) for (p, wp) in SETTINGS for s in seeds for r in range(3)]
    with Pool(8) as pool:
        te = pool.map(T.one, jobs, chunksize=1)
    G = {st: np.array([T.gm([x["work"] for x in te if (x["p"], x["wp"]) == st and x["seed"] == s]) for s in seeds])
         for st in SETTINGS}
    rng = np.random.default_rng(31)
    idx = rng.integers(0, 20, (10000, 20))
    base = G[(0.8, 0.0)]
    out = {"median_work": {str(list(s)): float(np.median(G[s])) for s in SETTINGS}, "vs_(0.8,0)": {},
           "unsolved": sum(not x["solved"] for x in te), "failed_state_checks": sum(x["ok"] is False for x in te)}
    for s in SETTINGS[1:]:
        rb = np.median(G[s][idx], 1) / np.median(base[idx], 1)
        out["vs_(0.8,0)"][str(list(s))] = {"ratio": float(np.median(G[s]) / np.median(base)),
                                           "ci99": [float(np.quantile(rb, 0.005)), float(np.quantile(rb, 0.995))],
                                           "mean_log_ratio_paired": float(np.mean(np.log(G[s] / base)))}
    out["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "referee_earn_task2b_runnersup.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
