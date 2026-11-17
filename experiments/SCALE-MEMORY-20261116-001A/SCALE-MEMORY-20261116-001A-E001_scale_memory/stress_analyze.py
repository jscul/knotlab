"""The n = 51200 stress cell of SCALE-MEMORY-20261116-001A, read after the disclosed stop of 2026-11-17 (see stress_sf_job.py).

Arms with all 100 instances finished (the scale-free L3s and L3sm, both seeds, and the comparators) are read as the frozen protocol
reads a cell: an arm's figure is the geometric mean of its two seeds' median flips, R is that over the best re-tuned rule's
median, with a 99% paired bootstrap re-choosing the best rule in each resample. Every other arm is reported only as the number of
instances it finished; its unfinished runs are not finished within the flips reached and enter no figure.

  stress_analyze.py ARTIFACT_DIR
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
recs = []
for sub in ("test", "stress_sf"):
    for v in load_results(str(A / sub)).values():
        if v["status"] == "ok" and v["result"]["n"] == 51200:
            recs.append(v["result"])
by = defaultdict(dict)
for r in recs:
    by[r["arm"]][r["seed"]] = r
full = {a: d for a, d in by.items() if len(d) == 100}
partial = {a: len(d) for a, d in by.items() if len(d) < 100}
seeds = sorted(set.intersection(*[set(d) for d in full.values()]))
S = len(seeds)
F = {a: np.array([d[s]["flips"] if d[s]["solved"] else math.inf for s in seeds], dtype=float) for a, d in full.items()}
rules = [a for a in F if "@" in a]
cell_rules = {r.split("@")[0]: (F[f"{r.split('@')[0]}@cell"] if f"{r.split('@')[0]}@cell" in F else F[r]) for r in rules}
rng = np.random.default_rng(20261117)
idx = [rng.integers(0, S, S) for _ in range(10_000)]


def armfig(name, ix=None):
    return math.exp(np.mean([math.log(np.median(F[f"{name}_s{k}"] if ix is None else F[f"{name}_s{k}"][ix])) for k in (0, 1)]))


def best(ix=None):
    return min(np.median(v if ix is None else v[ix]) for v in cell_rules.values())


out = {"instances": S, "medians": {a: float(np.median(v)) for a, v in F.items()},
       "solved": {a: float(np.isfinite(v).mean()) for a, v in F.items()}, "not_finished_arms": partial, "R": {}}
for name in ("L3s", "L3sm"):
    pt = armfig(name) / best()
    bs = np.array([armfig(name, ix) / best(ix) for ix in idx])
    lo, hi = np.percentile(bs, [0.5, 99.5])
    out["R"][name] = {"point": float(pt), "lo": float(lo), "hi": float(hi),
                      "seeds": [float(np.median(F[f"{name}_s{k}"]) / best()) for k in (0, 1)]}
pt = armfig("L3sm") / armfig("L3s")
bs = np.array([armfig("L3sm", ix) / armfig("L3s", ix) for ix in idx])
out["L3sm_over_L3s"] = {"point": float(pt), "lo": float(np.percentile(bs, 0.5)), "hi": float(np.percentile(bs, 99.5))}
(A / "stress_51200.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
