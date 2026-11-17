"""Referee R1 for LAYER-RANK-20261117-001: the spread of S1 (simulation against the recursion at w = 2^17, d <= 1,024).

  .venv/bin/python -B referee_s1_spread.py > referee_s1_spread.json

Twelve of the referee's own simulations (referee_layer.simulate) against the referee's recursion: the relative deviation of the
mean rank at d = 256, 512 and 1,024, with each run's true fraction (which drifts at finite width).
"""
import json

import numpy as np

import referee_layer as R

rec, _ = R.recursion(1024, {256, 512, 1024})
rng = np.random.default_rng(77)
rows = []
for k in range(12):
    s = R.simulate(2 ** 17, 1024, rng, {256, 512, 1024})
    rows.append({L: {"rel_dev": s[L]["mean"] / rec[L]["mean"] - 1, "p": s[L]["p"]} for L in (256, 512, 1024)})
out = {L: {"median_rel_dev": float(np.median([r[L]["rel_dev"] for r in rows])),
           "range": [float(min(r[L]["rel_dev"] for r in rows)), float(max(r[L]["rel_dev"] for r in rows))],
           "corr_with_p": float(np.corrcoef([r[L]["rel_dev"] for r in rows], [r[L]["p"] for r in rows])[0, 1]),
           "share_of_medians_of_3_above_5pct": float(np.mean([np.median([rows[i + j][L]["rel_dev"] for j in range(3)]) > 0.05
                                                              for i in range(0, 12, 3)]))} for L in (256, 512, 1024)}
print(json.dumps({"runs": rows, "summary": out}, indent=1, default=str))
