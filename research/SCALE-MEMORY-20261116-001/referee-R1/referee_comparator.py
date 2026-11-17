"""SCALE-MEMORY-20261116-001, referee R1, item 1: cross-check of the post hoc Novelty+ comparator.

The referee's own Novelty+ (referee_sls.c) at (p, wp) = (0.7, 0), (0.7, 0.01), (0.7, 0.05) on the 100 test
instances rand n = 12800 and 3200 (seeds 3,000,000 .. 3,000,099; instances from the study's `planted`, each
checked independently), 3 runs per instance at 12800 and 5 at 3200, caps 2e9 and 2e8, referee run seeds.
A CPU-time guard (TLIM s per run) stops a stuck run; any such run is reported (none is expected).

Statistics per setting: the median over instances of each instance's geometric mean over its runs (the
study's post hoc statistic) and the pooled median over all runs. Ratios of (0.7, 0.05) to the other two,
with a paired bootstrap over instances (each instance carries all its runs), 10,000 resamples, 95%.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import referee_common as C  # noqa: E402

SETTINGS = [(0.7, 0.0), (0.7, 0.01), (0.7, 0.05)]
REPS = {12800: 3, 3200: 5}
CAP = {12800: 2 * 10**9, 3200: 2 * 10**8}
TLIM = 240.0
STUDY_POSTHOC = {3200: {(0.7, 0.0): 71960, (0.7, 0.01): 74046, (0.7, 0.05): 87876},
                 12800: {(0.7, 0.0): 363539, (0.7, 0.01): 367547, (0.7, 0.05): 416884}}
FROZEN_12800 = 416258


def job(a):
    n, s, prm, rep = a
    r = C.run("rand", n, s, "novelty_plus", prm, C.seed_of("SM-comparator", n, s, prm, rep), CAP[n], tlimit=TLIM)
    return n, s, prm, rep, r["flips"], r["solved"], r["timed_out"], r["cpu"]


def stat_geo(X):  # X: instances x reps
    return float(np.median(np.exp(np.mean(np.log(X), axis=1))))


def main():
    t0 = time.time()
    seeds = [3_000_000 + i for i in range(100)]
    for n in (12800, 3200):
        for s in seeds:
            C.instance("rand", n, s)
    jobs = [(n, s, prm, r) for n in (12800, 3200) for s in seeds for prm in SETTINGS for r in range(REPS[n])]
    res = C.pool_map(job, jobs)
    out = {"item": "1 post hoc comparator cross-check", "tlimit_s": TLIM, "cells": {}}
    rng = np.random.default_rng(11)
    for n in (3200, 12800):
        X, unsolved, timed, cpu = {}, 0, 0, 0.0
        for prm in SETTINGS:
            rows = sorted((r for r in res if r[0] == n and r[2] == prm), key=lambda r: (r[1], r[3]))
            X[prm] = np.array([[r[4] for r in rows if r[1] == s] for s in seeds], dtype=float)
            unsolved += sum(not r[5] for r in rows)
            timed += sum(r[6] for r in rows)
            cpu += sum(r[7] for r in rows)
        B = 10000
        idx = rng.integers(0, len(seeds), (B, len(seeds)))

        def boot_geo(prm):
            G = np.exp(np.mean(np.log(X[prm]), axis=1))
            return np.median(G[idx], axis=1)

        def boot_pool(prm):
            return np.median(X[prm][idx].reshape(B, -1), axis=1)

        cell = {"n": n, "instances": len(seeds), "reps": REPS[n], "cap": CAP[n], "unsolved": unsolved,
                "timed_out": timed, "cpu_s": cpu, "settings": {}}
        bg = {prm: boot_geo(prm) for prm in SETTINGS}
        bp = {prm: boot_pool(prm) for prm in SETTINGS}
        for prm in SETTINGS:
            cell["settings"][str(prm)] = {
                "median_of_instance_geomeans": stat_geo(X[prm]),
                "pooled_median": float(np.median(X[prm])),
                "median_of_first_runs": float(np.median(X[prm][:, 0])),
                "study_posthoc_geomean_stat": STUDY_POSTHOC[n][prm],
                "referee_over_study": stat_geo(X[prm]) / STUDY_POSTHOC[n][prm],
                "geo_ci95": [float(np.quantile(bg[prm], 0.025)), float(np.quantile(bg[prm], 0.975))]}
        best_geo = min(SETTINGS[:2], key=lambda p: stat_geo(X[p]))
        ratios = {}
        for other in SETTINGS[:2]:
            rg, rp = bg[(0.7, 0.05)] / bg[other], bp[(0.7, 0.05)] / bp[other]
            ratios[f"(0.7, 0.05) / {other}"] = {
                "geo_point": stat_geo(X[(0.7, 0.05)]) / stat_geo(X[other]),
                "geo_ci95": [float(np.quantile(rg, 0.025)), float(np.quantile(rg, 0.975))],
                "pooled_point": float(np.median(X[(0.7, 0.05)]) / np.median(X[other])),
                "pooled_ci95": [float(np.quantile(rp, 0.025)), float(np.quantile(rp, 0.975))]}
        # against the better of the two low-walk settings, re-chosen in every resample
        bmin = np.minimum(bg[(0.7, 0.0)], bg[(0.7, 0.01)])
        r = bg[(0.7, 0.05)] / bmin
        ratios["(0.7, 0.05) / best of the other two (re-chosen per resample)"] = {
            "geo_point": stat_geo(X[(0.7, 0.05)]) / min(stat_geo(X[p]) for p in SETTINGS[:2]),
            "geo_ci95": [float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))]}
        if n == 12800:
            b = min(stat_geo(X[p]) for p in SETTINGS[:2])
            ratios["study frozen single-run (0.7, 0.05) 416,258 / referee best geo stat"] = {"point": FROZEN_12800 / b}
        cell["ratios"] = ratios
        cell["best_low_walk_setting_geo"] = str(best_geo)
        out["cells"][str(n)] = cell
        print(f"n={n}: unsolved {unsolved}, timed out {timed}, cpu {cpu:.0f} s")
        for prm in SETTINGS:
            v = cell["settings"][str(prm)]
            print(f"   {prm}: geo-stat {v['median_of_instance_geomeans']:>10.0f} "
                  f"[{v['geo_ci95'][0]:.0f}, {v['geo_ci95'][1]:.0f}]  pooled {v['pooled_median']:>10.0f}  "
                  f"study {v['study_posthoc_geomean_stat']:>8d}  referee/study {v['referee_over_study']:.3f}")
        for k, v in ratios.items():
            print(f"   {k}: {json.dumps(v)}")
    out["wall_s"] = time.time() - t0
    out["raw"] = [[r[0], r[1], list(r[2]), r[3], r[4], r[5], r[6]] for r in res]
    C.jdump(out, C.HERE / "referee_comparator.json")
    print("wall", out["wall_s"])


if __name__ == "__main__":
    main()
