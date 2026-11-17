"""Read-out of LAYER-RANK-20261117-001A-E001 against the frozen predictions.
python3 -B summarize.py RUN_DIR
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from longrun import load_results  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "LAYER-RANK-20261117-001A", "LAYER-RANK-20261117-001A-E001_layer_rank")


def main(run_dir):
    recs = load_results(run_dir)
    res = {k: v["result"] for k, v in recs.items() if v.get("status") == "ok"}
    bad = sorted(k for k, v in recs.items() if v.get("status") != "ok")
    V = {"G": {"not_ok": bad, "holds": not bad}}
    mf = {int(k): v for k, v in res["mf"]["rows"].items()}
    m3, m5 = mf[1000], mf[100000]
    ex = math.log(m5["mean"] / m3["mean"]) / math.log(100)
    V["M1"] = {"exponent": ex, "holds": 0.505 <= ex <= 0.53}
    a, b = m3["mean"] / math.sqrt(1000), m5["mean"] / math.sqrt(100000)
    V["M2"] = {"mu_over_sqrtL_1e3": a, "mu_over_sqrtL_1e5": b, "holds": 0.60 <= a <= 0.63 and 0.65 <= b <= 0.662}
    es = math.log(m5["sd"] / m3["sd"]) / math.log(100)
    V["M3"] = {"sd_exponent": es, "holds": 0.49 <= es <= 0.52}
    V["M4"] = {"L_F1": m5["L_F1"], "L_F2": m5["L_F2"], "holds": 3.95 <= m5["L_F1"] <= 4.05 and 10.3 <= m5["L_F2"] <= 10.6}
    V["M5"] = {"mean_times_tie": m5["mean_times_tie"], "holds": 0.85 <= m5["mean_times_tie"] <= 0.93}
    V["M6"] = {"profile": m5["profile_at_half_front"], "holds": 0.9 <= m5["profile_at_half_front"] <= 1.1}
    y3, y5 = m3["mean"] + 0.25 * math.log(1000), m5["mean"] + 0.25 * math.log(100000)
    sl = (y5 - y3) / (math.sqrt(100000) - math.sqrt(1000))
    V["M7"] = {"slope": sl, "holds": 0.64 <= sl <= 0.69}
    devs = []
    for k, r in res.items():
        if k.startswith("val-"):
            w = r["w"]
            for L, s in r["sim"].items():
                if int(L) <= w / 128:
                    m = r["mf"][str(L)] if str(L) in r["mf"] else r["mf"][L]
                    devs.append((k, int(L), abs(s["mean"] - m["mean"]) / m["mean"]))
    by = {}
    for k, L, d in devs:
        by.setdefault((k.split("-s")[0], L), []).append(d)
    meds = {f"{a}-L{L}": float(np.median(v)) for (a, L), v in sorted(by.items())}
    V["S1"] = {"median_rel_dev": meds, "holds": all(v <= 0.05 for v in meds.values())}
    w1 = [r["sim"] for k, r in res.items() if k.startswith("w1024-")]
    s2 = {}
    for L in ("1024", "4096"):
        rows = [s[L] if L in s else s[int(L)] for s in w1]
        alive = [x for x in rows if x["p"] > 0]
        s2[L] = {"median_max": float(np.median([x["max"] for x in alive])) if alive else None,
                 "all_false_share": float(np.mean([x["p"] == 0 for x in rows])),
                 "all_true_share": float(np.mean([x["p"] == 1 for x in rows]))}
    V["S2"] = {"values": s2, "holds": (s2["1024"]["median_max"] is not None and 31 <= s2["1024"]["median_max"] <= 44
                                     and s2["4096"]["median_max"] is not None and 75 <= s2["4096"]["median_max"] <= 130
                                     and 0.10 <= s2["1024"]["all_false_share"] <= 0.35
                                     and 0.35 <= s2["4096"]["all_false_share"] <= 0.65)}
    cw = {}
    for w in (64, 128, 256, 512, 1024):
        slopes = []
        for k, r in res.items():
            if k.startswith(f"collapse-w{w}-"):
                sim = {int(L): v for L, v in r["sim"].items()}
                L1, L2 = 40 * w, 100 * w
                if sim[L1]["p"] == 1 and sim[L2]["p"] == 1:
                    slopes.append((sim[L2]["mean"] - sim[L1]["mean"]) / (L2 - L1) * math.sqrt(w))
        cw[w] = {"c": float(np.median(slopes)) if slopes else None, "fixed_true_samples": len(slopes)}
    cs = [v["c"] for v in cw.values() if v["c"] is not None]
    V["S3"] = {"c_by_w": cw, "holds": len(cs) == 5 and all(0.3 <= c <= 1.5 for c in cs) and max(cs) / min(cs) <= 1.5}
    out = {"verdicts": V, "mf": mf}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "summary.json"), "w"), indent=1, sort_keys=True, default=str)
    for k, v in V.items():
        print(k, "HOLDS" if v["holds"] else "FAILS", {x: y for x, y in v.items() if x != "holds"})


if __name__ == "__main__":
    main(sys.argv[1])
