"""Post-hoc readings (not pre-registered) for SEQUENTIAL-WALL-20261116-001.

1. Phase sizes at k* (n = 2^18, 2^20): ratios of successive phases before the
   smallest phase and after it, against the advisor's Newton-at-a-tangency
   rates 1/(1 + rho) = 0.54 and 1/(1 - rho) = 6.9 with rho = 1/sqrt(3) at c = 3.
2. Layered circuits (width 1024): log-log slope of the median largest output
   Strahler number against depth.
python3 -B research/SEQUENTIAL-WALL-20261116-001/posthoc.py
"""
import json, os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from longrun import load_results
RUN = os.path.join(ROOT, "artifacts/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/run")
recs = {k: v["result"] for k, v in load_results(RUN).items() if v.get("status") == "ok"}
out = {}
for e in (18, 20):
    down, up = [], []
    for k, r in recs.items():
        if k.startswith(f"rand-n{e}-"):
            ps = r["at_k_star"]["phase_sizes"]
            j = int(np.argmin(ps[:-2])) if len(ps) > 3 else 0
            down += [ps[i + 1] / ps[i] for i in range(0, max(0, j - 1))]
            up += [ps[i + 1] / ps[i] for i in range(j + 1, min(len(ps) - 1, j + 3))]
    out[f"n2^{e}"] = {"shrink_ratio_median": float(np.median(down)), "grow_ratio_median": float(np.median(up)),
                      "shrink_samples": len(down), "grow_samples": len(up)}
ds, ss = [], []
for d in (8, 16, 32, 64, 128, 256):
    vals = [r["out_max_rank"] for k, r in recs.items() if k.startswith(f"circ-w1024-d{d}-") and r["out_true"] > 0]
    ds.append(d); ss.append(float(np.median(vals)))
out["layered_w1024"] = {"d": ds, "median_out_strahler": ss,
                        "loglog_slope": float(np.polyfit(np.log2(ds), np.log2(ss), 1)[0]),
                        "loglog_slope_d32_to_256": float(np.polyfit(np.log2(ds[2:]), np.log2(ss[2:]), 1)[0])}
path = os.path.join(ROOT, "artifacts/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/posthoc.json")
json.dump(out, open(path, "w"), indent=1)
print(json.dumps(out, indent=1))
