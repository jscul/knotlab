"""SCALE-MEMORY-20261116-001, referee R1, item 2: is the relative-age read scale-free?

In the referee's own Novelty+ runs (referee_sls.c, logging on), every step records, for the three
distinctions of the attended knot, the relative age a_j / max(a_1, a_2, a_3), where a = steps since the
distinction was last flipped and a never-flipped distinction has age t + 1 (t = steps so far). For
contrast, the same runs give the clipped log age min(1, log1p(a) / log1p(1000)) of WHERE-NEXT's L3.

Runs: rand n = 200, 800, 3200, 12800; INST test instances each (seeds 3,000,000 + i), one run each; two
parameter sets: (0.7, 0.01) at every n, and WHERE-NEXT's re-tuned Novelty+ per cell. Pooled over all steps.
Stability across n: the largest difference between the binned cumulative distributions (a KS-type
distance) of each n against n = 3200.
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

NS = [200, 800, 3200, 12800]
INST = 20
CAP = {200: 10**6, 800: 10**7, 3200: 2 * 10**8, 12800: 2 * 10**9}
RETUNED = {200: (0.7, 0.1), 800: (0.6, 0.05), 3200: (0.7, 0.01), 12800: (0.7, 0.05)}  # WHERE-NEXT retuned_all.json
NB_AGE, NB_DEC, NB_REL = C.NB_AGE, C.NB_DEC, 1000
REL0 = 8 + 2 * (NB_AGE + NB_DEC)
AGE_MID = 2.0 ** ((np.arange(NB_AGE) + 0.5) / 64.0)


def job(a):
    n, s, prm, tag = a
    r = C.run("rand", n, s, "novelty_plus", prm, C.seed_of("SM-relage", n, s, tag), CAP[n], hist=True, tlimit=240.0)
    return n, s, tag, r["flips"], r["solved"], r["timed_out"], r["hist"]


def rel_summary(H):
    obs, ones, ties = int(H[REL0]), int(H[REL0 + 1]), int(H[REL0 + 2])
    h = H[REL0 + 3:REL0 + 3 + NB_REL].astype(float)
    cdf = np.concatenate([np.cumsum(h), [h.sum() + ones]]) / obs  # P(rel < (b+1)/1000), last = 1
    mids = (np.arange(NB_REL) + 0.5) / NB_REL

    def q(p):
        i = int(np.searchsorted(cdf, p))
        return 1.0 if i >= NB_REL else float(mids[i])
    steps = obs // 3
    return {"reads": obs, "frac_equal_1": ones / obs, "frac_steps_with_tied_oldest": ties / steps,
            "q10": q(0.10), "q25": q(0.25), "median": q(0.5), "q75": q(0.75),
            "mean": float((h * mids).sum() + ones) / obs,
            "frac_below_0.001": float(cdf[0]), "frac_below_0.01": float(cdf[9]), "frac_below_0.1": float(cdf[99]),
            "cdf": cdf}


def clipped_summary(H):
    obs, never, gt = int(H[0]), int(H[1]), int(H[2])
    age = H[8:8 + NB_AGE].astype(float)
    feat = np.minimum(1.0, np.log1p(AGE_MID) / math.log1p(1000.0))
    c = np.cumsum(age)
    i = int(np.searchsorted(c, 0.5 * obs))
    med_age = float(AGE_MID[i]) if i < NB_AGE else float("inf")
    return {"frac_clipped_age_gt1000_or_never": (gt + never) / obs,
            "median_clipped_log_age": 1.0 if med_age == float("inf") else min(1.0, math.log1p(med_age) / math.log1p(1000.0)),
            "mean_clipped_log_age": float((age * feat).sum() + never) / obs}


def main():
    t0 = time.time()
    jobs = []
    for n in NS:
        for i in range(INST):
            s = 3_000_000 + i
            C.instance("rand", n, s)
            jobs.append((n, s, (0.7, 0.01), "fixed"))
            jobs.append((n, s, RETUNED[n], "retuned"))
    res = C.pool_map(job, jobs)
    out = {"item": "2 relative-age read vs n", "instances_per_n": INST, "cells": {}}
    for tag in ("fixed", "retuned"):
        cdfs = {}
        for n in NS:
            rows = [r for r in res if r[0] == n and r[2] == tag]
            H = np.sum([r[6] for r in rows], axis=0)
            rs = rel_summary(H)
            cdfs[n] = rs.pop("cdf")
            cs = clipped_summary(H)
            out["cells"][f"{tag}|{n}"] = {"n": n, "params": list((0.7, 0.01) if tag == "fixed" else RETUNED[n]),
                                          "runs": len(rows), "solved": int(sum(r[4] for r in rows)),
                                          "timed_out": int(sum(r[5] for r in rows)),
                                          "median_flips": float(np.median([r[3] for r in rows])),
                                          "relative_age": rs, "clipped_log_age": cs}
        for n in NS:
            out["cells"][f"{tag}|{n}"]["relative_age"]["ks_vs_3200"] = float(np.max(np.abs(cdfs[n] - cdfs[3200])))
        for n in NS:
            c = out["cells"][f"{tag}|{n}"]
            r, k = c["relative_age"], c["clipped_log_age"]
            print(f"{tag:7s} n={n:6d} {str(c['params']):12s} flips {c['median_flips']:>9.0f} | rel: median {r['median']:.3f} "
                  f"q25 {r['q25']:.3f} q10 {r['q10']:.3f} mean {r['mean']:.3f} =1 {r['frac_equal_1']:.3f} "
                  f"tied-oldest steps {r['frac_steps_with_tied_oldest']:.3f} KS vs 3200 {r['ks_vs_3200']:.3f} "
                  f"<.001 {r['frac_below_0.001']:.3f} <.01 {r['frac_below_0.01']:.3f} <.1 {r['frac_below_0.1']:.3f} | "
                  f"clipped: >1000|never {k['frac_clipped_age_gt1000_or_never']:.3f} median {k['median_clipped_log_age']:.3f}",
                  flush=True)
    out["wall_s"] = time.time() - t0
    C.jdump(out, C.HERE / "referee_relage.json")
    print("wall", out["wall_s"])


if __name__ == "__main__":
    main()
