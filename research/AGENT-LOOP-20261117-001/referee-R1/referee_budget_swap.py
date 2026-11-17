"""Referee R1 for AGENT-LOOP-20261117-001: do M2 and M3 change if each measure is read under the other budget (A95)?

  .venv/bin/python -B referee_budget_swap.py > referee_budget_swap.json

Flips under EARN-BUDGET's rule (DrC/Dr, DrC/GN) and charged work under the per-flip budget (DrCf/Dr, DrCf/GNf), with the
frozen thresholds and seed agreement, from the study's raw results. Reuses referee_R_agent.py's statistic.
"""
from __future__ import annotations

import json

import numpy as np

import referee_R_agent as R

SWAP = {"M2": {"flips": ("DrC{s}", "Dr{s}"), "work": ("DrCf{s}", "Dr{s}")},
        "M3": {"flips": ("DrC{s}", "GN"), "work": ("DrCf{s}", "GNf")}}

if __name__ == "__main__":
    d = R.load()
    out = {}
    for cell, arms in d.items():
        idx = sorted(arms["NOV"])
        fig = {m: {a: {i: R.gmean([x[m] for x in v[i]]) for i in idx} for a, v in arms.items()} for m in ("flips", "work")}
        row = {}
        for t, ms in SWAP.items():
            for m, spec in ms.items():
                seeds = {s: R.ratio(fig[m], [x.format(s=s) for x in spec], idx) for s in "01"}
                k = sum(R.ok(v, t, "helps") for v in seeds.values())
                row[f"{t} {m} (other budget)"] = {"seeds": seeds, "verdict": "holds" if k == 2 else
                                                  "seeds disagree" if k == 1 else "fails"}
        out[cell] = row
    print(json.dumps(out, indent=1))
