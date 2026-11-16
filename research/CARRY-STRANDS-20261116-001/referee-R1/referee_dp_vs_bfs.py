"""Referee R1: the spend-only BFS distance equals the tree DP, per
distinction and per phase (fresh code only).

For every pattern and w = 1, 2, 3, and every spend-only phase, the BFS's
first distance to each unforced distinction equals the least number of
internal nodes of a derivation tree over the phase's forced set with
Strahler number <= w (INF on both sides when not reached).
"""

import itertools
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_carry as R  # noqa: E402
import referee_task1_theorems as T1  # noqa: E402
import referee_task1b_larger as B  # noqa: E402


def main():
    t0 = time.time()
    cnt = bad = per_dist = 0
    wit = []
    src = itertools.chain(T1.random_small(seed=3, per_n=300, jump_per_n=200),
                          itertools.islice(B.gen(seed=8), 0, 900), T1.structured_small())
    for (n, at, H) in src:
        for w in (1, 2, 3):
            F = set(H)
            ok = True
            while True:
                first, _ = R.bfs_phase(at, F, w, "spend")
                s = R.spend_min_steps(n, at, F, w)
                for v in range(n):
                    if v in F:
                        continue
                    per_dist += 1
                    if first.get(v, R.INF) != s[v]:
                        ok = False
                new = set(first) - F
                if not new:
                    break
                F |= new
            cnt += 1
            if not ok:
                bad += 1
                if len(wit) < 3:
                    wit.append({"n": n, "atoms": at, "held": sorted(H), "w": w})
    out = {"pattern_w_cases": cnt, "distinction_phase_comparisons": per_dist, "disagreements": bad,
           "witnesses": wit, "seconds": round(time.time() - t0, 1)}
    print(out)
    with open(os.path.join(HERE, "referee_dp_vs_bfs.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
