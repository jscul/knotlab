"""Task 1: reference behaviour of the hand-written baselines.

The referee's own WalkSAT, probSAT (poly) and Novelty+ (referee_sls.c), with the study's re-tuned
parameters per cell (retuned_all.json) and, where they differ, the training-tuned ones (tuning.json),
on the study's 100 test instances per cell, with the referee's own run seeds and the study's flip caps.
REPS runs per instance. Compared with the study's same-arm runs (test/results.jsonl):
  - run 0 alone (100 runs, the study's design) against the study's 100: median ratio with a paired
    bootstrap over instances, and a two-sided Mann-Whitney U;
  - all REPS runs pooled: median ratio with the instance bootstrap (each resampled instance brings all
    its runs).
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import referee_common as C  # noqa: E402

CELLS = [("rand", 200), ("rand", 800), ("rand", 3200), ("local", 200), ("local", 800)]
RULES = {"novelty_plus": "novelty_plus", "probsat": "probsat", "walksat": "walksat"}
REPS = 5


def configs(cells=None):
    cells = cells or CELLS
    R = json.loads((C.ART / "retuned_all.json").read_text())["cells"]
    T = json.loads((C.ART / "tuning/tuning.json").read_text())
    out = []
    for fam, n in cells:
        for rule in RULES:
            ra, rp = R[f"{fam}|{n}"][rule]
            ta, tp = T[rule]["best"]["algo"], T[rule]["best"]["params"]
            same = (ra, list(rp)) == (ta, list(tp))
            out.append((fam, n, rule, "cell" if not same else "train", tuple(rp)))
            if not same:
                out.append((fam, n, rule, "train", tuple(tp)))
    return out


def job(a):
    fam, n, rule, tag, prm, iseed, rep = a  # noqa
    r = C.run(fam, n, iseed, RULES[rule], prm, C.seed_of("task1", fam, n, iseed, rule, tag, rep), C.CAP[(fam, n)])
    return (fam, n, rule, tag, prm, iseed, rep, r["flips"], r["solved"], r["cpu"])


def main(cells=None, reps=None, out_name="referee_task1_reference.json", task="1 reference behaviour"):
    global REPS
    REPS = reps or REPS
    cells = cells or CELLS
    t0 = time.time()
    cfgs = configs(cells)
    jobs = [(fam, n, rule, tag, prm, C.TEST_SEED0[fam] + i, rep)
            for fam, n, rule, tag, prm in cfgs for i in range(100) for rep in range(REPS)]
    # check every test instance once, in this process
    for fam, n in cells:
        for i in range(100):
            C.instance(fam, n, C.TEST_SEED0[fam] + i)
    res = C.pool_map(job, jobs)
    S = C.study_results()
    by = defaultdict(lambda: defaultdict(dict))
    cpu = defaultdict(float)
    for fam, n, rule, tag, prm, iseed, rep, fl, ok, c in res:
        by[(fam, n, rule, tag, prm)][iseed][rep] = (fl, ok)
        cpu[(fam, n, rule, tag)] += c
    rows = []
    for (fam, n, rule, tag, prm), d in sorted(by.items()):
        arm = f"{rule}@{tag}"
        if (fam, n, arm) not in S:  # re-tuned equal to training-tuned: the study ran only @train
            arm = f"{rule}@train"
        st = S[(fam, n, arm)]
        assert all(tuple(v[2]) == tuple(prm) for v in st.values()), (fam, n, arm, prm)
        mine0 = {k: [d[k][0][0]] for k in d}
        mineall = {k: [d[k][r][0] for r in range(REPS)] for k in d}
        theirs = {k: [st[k][0]] for k in st}
        a0 = [v[0] for v in mine0.values()]
        b = [v[0] for v in theirs.values()]
        allf = np.concatenate([np.asarray(v) for v in mineall.values()])
        row = {"family": fam, "n": n, "rule": rule, "params": list(prm), "study_arm": arm,
               "cap": C.CAP[(fam, n)],
               "study_median": float(np.median(b)), "study_unsolved": int(sum(not v[1] for v in st.values())),
               "referee_median_run0": float(np.median(a0)),
               "referee_median_all": float(np.median(allf)), "referee_runs": int(len(allf)),
               "referee_unsolved": int(sum(not d[k][r][1] for k in d for r in range(REPS))),
               "ratio_run0": C.median_ratio_boot(mine0, theirs),
               "ratio_all": C.median_ratio_boot(mineall, theirs),
               "mwu_run0": C.mwu(a0, b),
               "referee_cpu_s": cpu[(fam, n, rule, tag)]}
        rows.append(row)
        print(f"{fam:5s} {n:5d} {rule:13s} {str(list(prm)):14s} {arm:20s} study {row['study_median']:>10.1f} "
              f"ref0 {row['referee_median_run0']:>10.1f} refall {row['referee_median_all']:>10.1f} "
              f"r0 {row['ratio_run0']['point']:.3f} [{row['ratio_run0']['lo']:.3f},{row['ratio_run0']['hi']:.3f}] "
              f"rall {row['ratio_all']['point']:.3f} [{row['ratio_all']['lo']:.3f},{row['ratio_all']['hi']:.3f}] "
              f"MWU p {row['mwu_run0']['p']:.3f}", flush=True)
    out = {"task": task, "reps_per_instance": REPS, "instances_per_cell": 100,
           "instance_check": "every test instance: m = round(alpha n), three distinct in-range distinctions per knot, "
                             "hidden state non-constant and satisfying every knot; local knots within window 10",
           "solution_check": "every solved run's final state satisfies every knot",
           "wall_s": time.time() - t0, "rows": rows,
           "raw": [list(r[:7]) + [r[7], r[8]] for r in res]}
    C.jdump(out, C.HERE / out_name)
    print("wall", time.time() - t0)


if __name__ == "__main__":
    main()
