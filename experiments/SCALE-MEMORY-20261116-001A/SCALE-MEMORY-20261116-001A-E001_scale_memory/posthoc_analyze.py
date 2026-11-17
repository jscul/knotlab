"""The analysis that wrote posthoc_summary.json for SCALE-MEMORY-20261116-001A's post hoc five-run check (not frozen).

Statistic: for each test instance, the geometric mean of an arm's five run lengths (flips); the arm's figure is the median of
that over the instances, and for L3s and L3sm the geometric mean of their two seeds' figures. Ratios are taken against each
Novelty+ setting and against the best of the three, re-chosen in each of 10,000 paired resamples of the instances (99%
percentile intervals, generator seed 1). Committed 2026-11-17 after the referee (SCALE-MEMORY-R1) noted it was missing; it is
the code that was run, unchanged.

  posthoc_analyze.py ARTIFACT_DIR
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from longrun import load_results  # noqa: E402

A = Path(sys.argv[1])
r = load_results(str(A / "posthoc"))
d = defaultdict(dict)
for v in r.values():
    if v["status"] != "ok":
        continue
    x = v["result"]
    fl = [q["flips"] if q["solved"] else math.inf for q in x["runs"]]
    d[(x["n"], x["arm"])][x["seed"]] = (np.exp(np.mean(np.log(fl))) if all(np.isfinite(fl)) else math.inf, np.median(fl),
                                        sum(q["solved"] for q in x["runs"]))
rng = np.random.default_rng(1)
out = {}
for n in (3200, 12800):
    arms = sorted({a for (m, a) in d if m == n})
    seeds = sorted(set.intersection(*[set(d[(n, a)]) for a in arms]))
    S = len(seeds)
    V = {a: np.array([d[(n, a)][s][0] for s in seeds]) for a in arms}
    solved = {a: sum(d[(n, a)][s][2] for s in seeds) for a in arms}
    med = {a: float(np.median(V[a])) for a in arms}
    print(f"== n={n} instances {S}")
    for a in sorted(arms, key=lambda a: med[a]):
        print(f"  {a:24s} median of per-instance geomean {med[a]:>12.0f}  solved {solved[a]}/{5 * S}")
    nov = [a for a in arms if a.startswith("novelty")]
    idx = [rng.integers(0, S, S) for _ in range(10000)]

    def arm_stat(name, ix):
        if name in ("L3s", "L3sm"):
            return math.exp(np.mean([np.log(np.median(V[f"{name}_s{k}"][ix])) for k in (0, 1)]))
        return float(np.median(V[name][ix]))
    res = {}
    for name in ("L3s", "L3sm", "L3_s1"):
        for comp in ["best"] + nov:
            def den(ix):
                return min(np.median(V[c][ix]) for c in nov) if comp == "best" else np.median(V[comp][ix])
            pt = arm_stat(name, np.arange(S)) / den(np.arange(S))
            bs = np.array([arm_stat(name, ix) / den(ix) for ix in idx])
            lo, hi = np.percentile(bs, [0.5, 99.5])
            res[f"{name} / {comp}"] = [round(pt, 3), round(float(lo), 3), round(float(hi), 3)]
            print(f"  {name} / {comp}: {pt:.3f} [{lo:.3f}, {hi:.3f}] (99%)")
    out[str(n)] = {"instances": S, "medians": med, "solved": solved, "ratios_99": res}
json.dump(out, open(A / "posthoc_summary.json", "w"), indent=1)
