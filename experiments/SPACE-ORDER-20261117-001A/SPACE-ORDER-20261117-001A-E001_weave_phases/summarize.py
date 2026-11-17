"""Read-out of SPACE-ORDER-20261117-001A-E001 against the frozen predictions.
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

OUT = os.path.join(ROOT, "artifacts", "SPACE-ORDER-20261117-001A", "SPACE-ORDER-20261117-001A-E001_weave_phases")


def med(xs):
    return float(np.median(xs)) if len(xs) else float("nan")


def slope(a, b, ya, yb):
    return math.log(yb / ya) / math.log(b / a)


def main(run_dir):
    recs = load_results(run_dir)
    res = {k: v["result"] for k, v in recs.items() if v.get("status") == "ok"}
    bad = sorted(k for k, v in recs.items() if v.get("status") != "ok")
    T = {}
    for k, r in res.items():
        if k.startswith("sweepcheck"):
            continue
        T.setdefault((r["law"], r["pat"], r["L"]), []).append(r)
    tab = {}
    for (law, pat, L), rs in sorted(T.items()):
        a = [r["at_k_star"] for r in rs]
        tab[f"{law}-{pat}-L{L}"] = {
            "samples": len(rs), "k_star_frac": med([r["k_star"] / r["n"] for r in rs]),
            "R": med([x["R"] for x in a]), "P": med([x["P"] for x in a]), "D": med([x["D"] for x in a]),
            "P_over_R": med([x["P"] / max(1, x["R"]) for x in a]), "P_over_D": med([x["P"] / max(1, x["D"]) for x in a]),
            "avalanche": med([r["avalanche"] for r in rs]),
            "R_minus": med([r["at_k_star_minus_1"]["R"] for r in rs]), "P_minus": med([r["at_k_star_minus_1"]["P"] for r in rs]),
            "free_fraction": med([r["free_fraction"] for r in rs]) if law == "nae" else None,
            "fracs": {f: {"R": med([r["fracs"][f]["R"] for r in rs]), "P": med([r["fracs"][f]["P"] for r in rs]),
                          "set": med([r["fracs"][f]["set"] / r["n"] for r in rs])} for f in rs[0]["fracs"]}}
    g = lambda law, pat, L, key: tab[f"{law}-{pat}-L{L}"][key]
    V = {}
    allm = [r[x] for r in res.values() if "at_k_star" in r for x in ("at_k_star", "at_k_star_minus_1")] + \
           [m for r in res.values() if "fracs" in r for m in r["fracs"].values()]
    V["G"] = {"not_ok": bad, "P_ge_D_all": all(m["P_ge_D"] for m in allm),
              "strahler_checked": sum("strahler_equals_phase" in m for m in allm),
              "strahler_all": all(m.get("strahler_equals_phase", True) for m in allm)}
    V["G"]["holds"] = not bad and V["G"]["P_ge_D_all"] and V["G"]["strahler_all"]
    sP = [slope(96, 192, g("two", "W", 96, "P"), g("two", "W", 192, "P")), slope(192, 384, g("two", "W", 192, "P"), g("two", "W", 384, "P"))]
    sR = [slope(96, 192, g("two", "W", 96, "R"), g("two", "W", 192, "R")), slope(192, 384, g("two", "W", 192, "R"), g("two", "W", 384, "R"))]
    V["T1"] = {"P_slopes": sP, "R_slopes": sR, "P_over_R_384": g("two", "W", 384, "P_over_R"),
               "kfrac_48": g("two", "W", 48, "k_star_frac"), "kfrac_384": g("two", "W", 384, "k_star_frac")}
    V["T1"]["holds"] = (min(sP) >= 0.7 and min(sR) >= 0.7 and 0.3 <= V["T1"]["P_over_R_384"] <= 1
                        and V["T1"]["kfrac_384"] <= 0.5 * V["T1"]["kfrac_48"])
    kf = [g("two", "R6", L, "k_star_frac") for L in (24, 48, 96, 192, 384)]
    V["T2"] = {"kfrac": kf, "R_ratio_384_96": g("two", "R6", 384, "R") / g("two", "R6", 96, "R"),
               "P_growth": g("two", "R6", 384, "P") - g("two", "R6", 24, "P"), "P_384": g("two", "R6", 384, "P")}
    V["T2"]["holds"] = (all(0.06 <= x <= 0.11 for x in kf) and V["T2"]["R_ratio_384_96"] >= 2
                        and 1 <= V["T2"]["P_growth"] <= 8 and V["T2"]["P_384"] <= 20)
    V["T3"] = {"ratio": g("two", "W", 384, "P") / g("two", "R6", 384, "P")}
    V["T3"]["holds"] = V["T3"]["ratio"] >= 5
    pd = [g("two", "W", L, "P_over_D") for L in (96, 192, 384)]
    V["T4"] = {"P_over_D": pd, "holds": all(1 <= x <= 1.5 for x in pd)}
    V["O1"] = {"aval_W": g("one", "W", 384, "avalanche"), "aval_R6": g("one", "R6", 384, "avalanche")}
    V["O1"]["holds"] = V["O1"]["aval_W"] <= 0.05 and V["O1"]["aval_R6"] <= 0.05
    V["O2"] = {"R6_growth": g("one", "R6", 384, "P") - g("one", "R6", 24, "P"),
               "W_slope": slope(192, 384, g("one", "W", 192, "P"), g("one", "W", 384, "P"))}
    V["O2"]["holds"] = V["O2"]["R6_growth"] <= 4 and V["O2"]["W_slope"] < 0.2
    ko = [g("one", "R6", L, "k_star_frac") for L in (96, 192, 384)]
    V["O3"] = {"kfrac": ko, "holds": all(0.20 <= x <= 0.245 for x in ko)}
    V["N1"] = {"aval_W": g("nae", "W", 384, "avalanche"), "aval_R6": g("nae", "R6", 384, "avalanche")}
    V["N1"]["holds"] = V["N1"]["aval_W"] <= 0.05 and V["N1"]["aval_R6"] <= 0.05
    nP = {f"{pat}-{L}": g("nae", pat, L, "P") for pat in ("W", "R6") for L in (24, 48, 96, 192, 384)}
    V["N2"] = {"P": nP, "holds": all(x <= 8 for x in nP.values())}
    ff = [g("nae", "W", L, "free_fraction") for L in (48, 96, 192, 384)]
    sc = [r for k, r in res.items() if k.startswith("sweepcheck")]
    dsw = med([abs(r["free300"] - r["free30"]) for r in sc])
    V["N3"] = {"free_W": ff, "sweep_diff": dsw, "holds": all(0.27 <= x <= 0.31 for x in ff) and dsw <= 0.01}
    out = {"cases_ok": len(res), "not_ok": bad, "verdicts": V, "table": tab}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "summary.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    for k, v in V.items():
        print(k, "HOLDS" if v["holds"] else "FAILS", {x: y for x, y in v.items() if x != "holds"})


if __name__ == "__main__":
    main(sys.argv[1])
