"""Task 2: is the training-size win robust to a wider tuning of the hand-written rules?

At rand n = 200 and 800 (and, lighter, 3200), the referee's own rules are tuned on separate instances
(the study's re-tuning seeds 4,000,000 + i, i < 64; 32 at n = 3200; TUNE_REPS runs each) over wide
grids, by median flips with the tuning cap (runs at the cap count as the cap; the median is unaffected
while fewer than half are censored):
  Novelty+          p in {0.1, ..., 1.0} x wp in {0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2}
  probSAT (poly)    cb in {1.0, 1.25, ..., 4.0} x eps in {0.25, 0.5, 1}
  Adaptive Novelty+ (Hoos 2002) wp in {0, 0.01, 0.05} x 1/theta in {3, 6, 12} x phi in {0.1, 0.2, 0.4}
                    (the published default is 1/theta = 6, phi = 0.2, wp = 0.01)
  Novelty++         p in {0.3, ..., 0.9} x dp in {0.01, 0.02, 0.05, 0.1, 0.2}
  WalkSAT/SKC       p in {0.1, ..., 0.9}
Then on the study's 100 test instances per cell:
  - every grid setting once per instance with cap TEST_GRID_CAP (an optimistic "best on test" bound for
    the rules, since it selects on the test instances);
  - each family's tuning-selected setting (and its next TOPK - 1) with TEST_REPS runs per instance at the
    study's cap (the honest estimate).
Ratios to the study's L3 runs on the same instances are paired bootstraps over instances.

Usage: referee_task2_wide_tuning.py tune N | test N
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import referee_common as C  # noqa: E402

TUNE_INST = {200: 64, 800: 64, 3200: 32}
TUNE_REPS = {200: 2, 800: 2, 3200: 1}
TUNE_CAP = {200: 10**6, 800: 10**6, 3200: 10**7}
TEST_GRID_CAP = {200: 10**6, 800: 10**6, 3200: 10**7}
TEST_REPS = 5
TOPK = {"novelty_plus": 5, "novelty_pp": 5}  # others: 3


def grid(n):
    g = []
    for p, wp in itertools.product([round(0.1 * i, 2) for i in range(1, 11)],
                                   [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2]):
        g.append(("novelty_plus", (p, wp)))
    for cb, eps in itertools.product([1.0 + 0.25 * i for i in range(13)], [0.25, 0.5, 1.0]):
        g.append(("probsat", (cb, eps)))
    for wp, it, phi in itertools.product([0.0, 0.01, 0.05], [3, 6, 12], [0.1, 0.2, 0.4]):
        g.append(("adapt_novelty_plus", (wp, it, phi)))
    for p, dp in itertools.product([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], [0.01, 0.02, 0.05, 0.1, 0.2]):
        g.append(("novelty_pp", (p, dp)))
    for p in [round(0.1 * i, 2) for i in range(1, 10)]:
        g.append(("walksat", (p,)))
    # fine grids around the optimum (added after the coarse grids showed a sharp optimum near p = 0.7)
    for p, wp in itertools.product([round(0.55 + 0.025 * i, 3) for i in range(11)], [0.0, 0.005, 0.01, 0.02, 0.05]):
        g.append(("novelty_plus", (p, wp)))
    for p, dp in itertools.product([0.55, 0.6, 0.65, 0.7, 0.75, 0.8], [0.005, 0.01, 0.02, 0.05]):
        g.append(("novelty_pp", (p, dp)))
    if n >= 3200:  # lighter (added after n = 200 and 800): only the region that was competitive there
        keep = {"novelty_plus": lambda q: 0.5 <= q[0] <= 0.85, "novelty_pp": lambda q: 0.55 <= q[0] <= 0.8,
                "probsat": lambda q: q[0] <= 2.0,
                "adapt_novelty_plus": lambda q: tuple(q) in {(0.01, 6, 0.2), (0.01, 12, 0.4), (0.0, 12, 0.4)}}
        g = [x for x in g if x[0] in keep and keep[x[0]](x[1])]
    seen, out = set(), []
    for a, prm in g:
        key = (a, tuple(round(float(v), 6) for v in prm))
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def job(a):
    phase, fam, n, algo, prm, iseed, rep, cap = a
    r = C.run(fam, n, iseed, algo, prm, C.seed_of("task2", phase, fam, n, iseed, algo, prm, rep), cap)
    return (algo, prm, iseed, rep, r["flips"], r["solved"], r["cpu"], r["mean_noise"])


def tune(n):
    t0 = time.time()
    fam = "rand"
    seeds = [C.RETUNE_SEED0[fam] + i for i in range(TUNE_INST[n])]
    for s in seeds:
        C.instance(fam, n, s)
    G = grid(n)
    path = C.HERE / f"referee_task2_tune_n{n}.json"
    prev = json.loads(path.read_text()) if path.exists() else None
    have = {(r["algo"], tuple(round(float(v), 6) for v in r["params"])) for r in prev["grid"]} if prev else set()
    G = [x for x in G if x not in have]
    print("settings to run", len(G), "kept", len(have))
    jobs = [("tune", fam, n, a, p, s, r, TUNE_CAP[n]) for a, p in G for s in seeds for r in range(TUNE_REPS[n])]
    res = C.pool_map(job, jobs) if jobs else []
    agg = defaultdict(list)
    cpu = prev["cpu_s"] if prev else 0.0
    noise = defaultdict(list)
    for algo, prm, s, r, fl, ok, c, mn in res:
        agg[(algo, prm)].append((fl, ok))
        cpu += c
        if algo == "adapt_novelty_plus":
            noise[(algo, prm)].append(mn)
    rows = []
    for (algo, prm), v in agg.items():
        f = np.array([x[0] for x in v], dtype=float)
        rows.append({"algo": algo, "params": list(prm), "median": float(np.median(f)),
                     "mean_log": float(np.mean(np.log(np.maximum(f, 1)))),
                     "censored": int(sum(not x[1] for x in v)), "runs": len(v),
                     **({"mean_adapted_noise": float(np.mean(noise[(algo, prm)]))} if (algo, prm) in noise else {})})
    if prev:
        rows += prev["grid"]
    rows.sort(key=lambda r: (r["algo"], r["median"]))
    best = {}
    for r in rows:
        if r["algo"] not in best:
            best[r["algo"]] = r
    for a, r in best.items():
        print(f"tune n={n} {a:20s} best {r['params']} median {r['median']:.1f} meanlog {r['mean_log']:.3f} "
              f"censored {r['censored']}/{r['runs']}")
    out = {"task": "2 wide tuning (tune)", "family": fam, "n": n, "tuning_seeds": [seeds[0], seeds[-1]],
           "reps": TUNE_REPS[n], "cap": TUNE_CAP[n], "objective": "median flips (censored runs = cap)",
           "cpu_s": cpu, "wall_s": time.time() - t0 + (prev["wall_s"] if prev else 0.0), "best": best, "grid": rows}
    C.jdump(out, path)
    print("wall", time.time() - t0)


def test(n):
    t0 = time.time()
    fam = "rand"
    T = json.loads((C.HERE / f"referee_task2_tune_n{n}.json").read_text())
    seeds = [C.TEST_SEED0[fam] + i for i in range(100)]
    for s in seeds:
        C.instance(fam, n, s)
    S = C.study_results()
    L3 = {s: [S[(fam, n, "L3")][s][0]] for s in seeds}
    L3_med = float(np.median([v[0] for v in L3.values()]))
    nov_arm = "novelty_plus@cell" if (fam, n, "novelty_plus@cell") in S else "novelty_plus@train"
    NOV = {s: [S[(fam, n, nov_arm)][s][0]] for s in seeds}
    NOV_med = float(np.median([v[0] for v in NOV.values()]))
    # selected settings: top TOPK per family by tuning median
    by_algo = defaultdict(list)
    for r in T["grid"]:
        by_algo[r["algo"]].append(r)
    sel = []
    for a, rs in by_algo.items():
        rs.sort(key=lambda r: r["median"])
        sel += [(a, tuple(r["params"]), rank) for rank, r in enumerate(rs[:TOPK.get(a, 3)])]
    # the "best on test" grid: every tuned setting except those censored in at least half the tuning runs
    hopeless = {(r["algo"], tuple(round(float(v), 6) for v in r["params"])) for r in T["grid"]
                if r["median"] >= T["cap"]}
    G = [x for x in grid(n) if x not in hopeless]
    if n >= 3200:  # time: the "best on test" grid only near each family's tuning optimum (within 1.3x)
        fbest = {}
        for r in T["grid"]:
            fbest[r["algo"]] = min(fbest.get(r["algo"], float("inf")), r["median"])
        near = {(r["algo"], tuple(round(float(v), 6) for v in r["params"])) for r in T["grid"]
                if r["median"] <= 1.3 * fbest[r["algo"]]}
        G = [x for x in G if x in near]
    jobs = [("testgrid", fam, n, a, p, s, 0, TEST_GRID_CAP[n]) for a, p in G for s in seeds]
    jobs += [("testsel", fam, n, a, p, s, r, C.CAP[(fam, n)]) for a, p, _ in sel for s in seeds
             for r in range(TEST_REPS)]
    # tag jobs so the two phases do not mix
    res = C.pool_map(job2, jobs)
    grid_runs = defaultdict(dict)
    sel_runs = defaultdict(lambda: defaultdict(list))
    cpu = 0.0
    for ph, algo, prm, s, r, fl, ok, c in res:
        cpu += c
        if ph == "testgrid":
            grid_runs[(algo, prm)][s] = (fl, ok)
        else:
            sel_runs[(algo, prm)][s].append((r, fl))
    oracle = []
    for (algo, prm), d in grid_runs.items():
        f = np.array([d[s][0] for s in seeds], dtype=float)
        oracle.append({"algo": algo, "params": list(prm), "median": float(np.median(f)),
                       "censored": int(sum(not d[s][1] for s in seeds))})
    oracle.sort(key=lambda r: r["median"])
    oracle_best = {}
    for r in oracle:
        oracle_best.setdefault(r["algo"], r)
    for a, r in oracle_best.items():
        g = grid_runs[(a, tuple(r["params"]))]
        r["ratio_to_L3"] = C.median_ratio_boot({s: [g[s][0]] for s in seeds}, L3)
        r["ratio_to_study_novelty_plus"] = C.median_ratio_boot({s: [g[s][0]] for s in seeds}, NOV)
    selected = []
    for a, p, rank in sel:
        d = {s: [fl for _, fl in sorted(v)] for s, v in sel_runs[(a, p)].items()}
        allf = np.concatenate([np.asarray(d[s], dtype=float) for s in seeds])
        selected.append({"algo": a, "params": list(p), "tuning_rank": rank, "runs": int(len(allf)),
                         "median": float(np.median(allf)),
                         "censored": int(np.sum(allf >= C.CAP[(fam, n)])),
                         "ratio_to_L3": C.median_ratio_boot(dict(d), L3),
                         "ratio_to_study_novelty_plus": C.median_ratio_boot(dict(d), NOV),
                         "flips_by_instance": {str(s): d[s] for s in seeds}})
    for r in selected:
        q = r["ratio_to_L3"]
        print(f"test n={n} sel{r['tuning_rank']} {r['algo']:20s} {str(r['params']):18s} median {r['median']:>9.1f} "
              f"rule/L3 {q['point']:.3f} [{q['lo']:.3f},{q['hi']:.3f}] "
              f"rule/studyNov+ {r['ratio_to_study_novelty_plus']['point']:.3f}")
    for a, r in oracle_best.items():
        q = r["ratio_to_L3"]
        print(f"oracle n={n} {a:20s} {str(r['params']):18s} median {r['median']:>9.1f} rule/L3 {q['point']:.3f} "
              f"[{q['lo']:.3f},{q['hi']:.3f}]")
    out = {"task": "2 wide tuning (test)", "family": fam, "n": n, "test_seeds": [seeds[0], seeds[-1]],
           "study_L3_median": L3_med, "study_novelty_plus_arm": nov_arm, "study_novelty_plus_median": NOV_med,
           "grid_settings_on_test": len(G), "grid_settings_skipped_hopeless": len(hopeless),
           "selected_reps": TEST_REPS, "selected_cap": C.CAP[(fam, n)], "grid_cap": TEST_GRID_CAP[n],
           "note": "ratio = rule median / study median; rule/L3 below 1.2 would mean the rule is within 1.2x of L3",
           "cpu_s": cpu, "wall_s": time.time() - t0, "selected": selected,
           "oracle_best_per_family": oracle_best, "oracle_grid": oracle}
    C.jdump(out, C.HERE / f"referee_task2_test_n{n}.json")
    print("wall", time.time() - t0)


def job2(a):
    r = job(a)
    return (a[0],) + r[:7]


if __name__ == "__main__":
    {"tune": tune, "test": test}[sys.argv[1]](int(sys.argv[2]))
