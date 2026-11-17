"""Task 3: do the memory features saturate with size?

The learned agent's memory reads, for each distinction of the attended knot, its age (steps since it was
last flipped, read as log1p(age) clipped at 1,000 steps; never = clipped) and its flip count decayed with
tau = 50 steps; and for each candidate knot the same for visits. In the referee's own Novelty+ runs with
the study's re-tuned parameters per cell, every step records these for the three members of the attended
(uniformly drawn violated) knot and for the attended knot itself (referee_sls.c logging).

Per n, pooled over every step of every run (each step weighs once) and as the median of per-run values:
fraction of member ages above 1,000 or never, fraction never, median age (never = infinite), median age
among flipped members, median age / n, median decayed count (never = 0), the agent's age feature
min(1, log1p(age) / log1p(1000)), and the same for the knot's visit memory.

Usage: referee_task3_memory_scale.py
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import referee_common as C  # noqa: E402

NB_AGE, NB_DEC = C.NB_AGE, C.NB_DEC
CELLS = [(200, 100), (800, 100), (3200, 100), (12800, 20)]
CAP = {200: 10**6, 800: 10**7, 3200: 2 * 10**8, 12800: 2 * 10**9}
AGE_LO = 2.0 ** (np.arange(NB_AGE) / 64.0)          # lower edge of age bin b
AGE_MID = 2.0 ** ((np.arange(NB_AGE) + 0.5) / 64.0)
DEC_MID = 10.0 ** ((np.arange(NB_DEC) + 0.5) / 50.0 - 40.0)


def split(H):
    o = 8
    age = H[o:o + NB_AGE]; o += NB_AGE
    dec = H[o:o + NB_DEC]; o += NB_DEC
    kage = H[o:o + NB_AGE]; o += NB_AGE
    kdec = H[o:o + NB_DEC]
    return age, dec, kage, kdec


def hist_quantile(counts, mids, extra_low=0, extra_high=0, q=0.5):
    """Quantile of a binned distribution with extra_low mass below every bin (e.g. decayed 0) and
    extra_high above every bin (e.g. never flipped = infinite age)."""
    tot = counts.sum() + extra_low + extra_high
    if tot == 0:
        return float("nan")
    target = q * tot
    if target <= extra_low:
        return 0.0
    c = extra_low + np.cumsum(counts)
    i = int(np.searchsorted(c, target))
    if i >= len(counts):
        return float("inf")
    return float(mids[i])


def summarize(H, n):
    age, dec, kage, kdec = split(H)
    obs, never, gt, dzero, kobs, knever, kgt, kdzero = (int(x) for x in H[:8])
    # age feature (study's agefeat): min(1, log1p(age) / log1p(1000)), never = 1
    feat_mid = np.minimum(1.0, np.log1p(AGE_MID) / math.log1p(1000.0))
    s = {
        "member_obs": obs,
        "frac_age_gt1000_or_never": (gt + never) / obs,
        "frac_never": never / obs,
        "median_age_never_inf": hist_quantile(age, AGE_MID, 0, never),
        "median_age_flipped": hist_quantile(age, AGE_MID),
        "q25_age_flipped": hist_quantile(age, AGE_MID, q=0.25),
        "q75_age_flipped": hist_quantile(age, AGE_MID, q=0.75),
        "median_age_over_n_never_inf": hist_quantile(age, AGE_MID, 0, never) / n,
        "median_age_over_n_flipped": hist_quantile(age, AGE_MID) / n,
        "median_age_feature": min(1.0, math.log1p(hist_quantile(age, AGE_MID, 0, never)) / math.log1p(1000.0)),
        "mean_age_feature": float((age * feat_mid).sum() + never) / obs,
        "median_decayed_count": hist_quantile(dec, DEC_MID, dzero, 0),
        "frac_decayed_below_0.01": float(dzero + dec[DEC_MID < 0.01].sum()) / obs,
        "frac_decayed_above_0.5": float(dec[DEC_MID > 0.5].sum()) / obs,
        "mean_decayed_count": float((dec * DEC_MID).sum()) / obs,
        "knot_obs": kobs,
        "knot_frac_age_gt1000_or_never": (kgt + knever) / kobs,
        "knot_frac_never": knever / kobs,
        "knot_median_age_never_inf": hist_quantile(kage, AGE_MID, 0, knever),
        "knot_median_age_visited": hist_quantile(kage, AGE_MID),
        "knot_median_decayed_count": hist_quantile(kdec, DEC_MID, kdzero, 0),
        "knot_frac_decayed_below_0.01": float(kdzero + kdec[DEC_MID < 0.01].sum()) / kobs,
    }
    return s


def job(a):
    n, iseed, prm = a
    r = C.run("rand", n, iseed, "novelty_plus", prm, C.seed_of("task3", n, iseed), CAP[n], hist=True)
    H = r.pop("hist")
    return n, iseed, r, H


def main():
    t0 = time.time()
    R = json.loads((C.ART / "retuned_all.json").read_text())["cells"]
    jobs = []
    for n, k in CELLS:
        prm = tuple(R[f"rand|{n}"]["novelty_plus"][1])
        for i in range(k):
            C.instance("rand", n, C.TEST_SEED0["rand"] + i)
            jobs.append((n, C.TEST_SEED0["rand"] + i, prm))
    res = C.pool_map(job, jobs)
    out = {"task": "3 memory features vs n (referee Novelty+, study's re-tuned parameters)", "cells": {}}
    for n, k in CELLS:
        rows = [r for r in res if r[0] == n]
        Hs = np.sum([r[3] for r in rows], axis=0)
        pooled = summarize(Hs, n)
        per_run = [summarize(r[3], n) for r in rows if r[3][0] > 0]
        med_per_run = {key: float(np.median([p[key] for p in per_run])) for key in per_run[0]}
        flips = [r[2]["flips"] for r in rows]
        out["cells"][str(n)] = {"n": n, "instances": len(rows), "params": R[f"rand|{n}"]["novelty_plus"][1], "cap": CAP[n],
                                "median_flips": float(np.median(flips)), "solved": int(sum(r[2]["solved"] for r in rows)),
                                "median_flips_over_n": float(np.median(flips)) / n,
                                "pooled_over_steps": pooled, "median_of_per_run": med_per_run,
                                "cpu_s": float(sum(r[2]["cpu"] for r in rows))}
        p = pooled
        print(f"n={n:6d} runs {len(rows)} med flips {np.median(flips):>10.0f} | members: >1000|never "
              f"{p['frac_age_gt1000_or_never']:.3f} never {p['frac_never']:.3f} med age {p['median_age_never_inf']:.0f} "
              f"(flipped {p['median_age_flipped']:.0f}) age/n {p['median_age_over_n_never_inf']:.3f} "
              f"feat {p['median_age_feature']:.3f} dec {p['median_decayed_count']:.3g} dec<.01 "
              f"{p['frac_decayed_below_0.01']:.3f} | knot >1000|never {p['knot_frac_age_gt1000_or_never']:.3f} "
              f"med age {p['knot_median_age_never_inf']:.0f} dec {p['knot_median_decayed_count']:.3g}", flush=True)
        r2 = med_per_run
        print(f"         per-run medians: >1000|never {r2['frac_age_gt1000_or_never']:.3f} med age "
              f"{r2['median_age_never_inf']:.0f} age/n {r2['median_age_over_n_never_inf']:.3f} dec "
              f"{r2['median_decayed_count']:.3g}", flush=True)
    out["wall_s"] = time.time() - t0
    C.jdump(out, C.HERE / "referee_task3_memory_scale.json")
    print("wall", time.time() - t0)


if __name__ == "__main__":
    main()
