"""Task 2/3 read-out: referee medians vs the study's per-sample records.

Reads referee_task2_n<e>.json (ours) and the study's registered run
artifacts/SEQUENTIAL-WALL-20261116-001A/.../run/results.jsonl (data only; none
of the study's code is imported).  Writes referee_task2_summary.json.
"""

import json
import os
import sys

import numpy as np
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUN = os.path.join(ROOT, "artifacts", "SEQUENTIAL-WALL-20261116-001A",
                   "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases", "run", "results.jsonl")
ES = [10, 12, 14, 16, 18]  # 18 is an extra size beyond the brief
MAIN = [10, 12, 14, 16]


def load_study():
    by_e = {}
    with open(RUN) as fh:
        for line in fh:
            r = json.loads(line)
            if r["status"] == "ok" and r["case"].startswith("rand-"):
                by_e.setdefault(r["result"]["e"], []).append(r["result"])
    return by_e


def load_ours():
    by_e = {}
    for e in ES:
        p = os.path.join(HERE, f"referee_task2_n{e}.json")
        if os.path.exists(p):
            by_e[e] = json.load(open(p))["records"]
    return by_e


QUANT = {
    "alpha_star": lambda r: r["alpha_star"],
    "R_star": lambda r: r["at_k_star"]["R"],
    "P_star": lambda r: r["at_k_star"]["P"],
    "R_minus": lambda r: r["at_k_star_minus_1"]["R"],
    "P_minus": lambda r: r["at_k_star_minus_1"]["P"],
    "closure_star_frac": lambda r: r["at_k_star"]["closure"] / r["n"],
    "closure_minus_frac": lambda r: r["at_k_star_minus_1"]["closure"] / r["n"],
    "log2_fringe_star": lambda r: r["at_k_star"]["max_log2_fringe"],
    "R_a0.03": lambda r: r["alphas"]["0.03"]["R"],
    "P_a0.03": lambda r: r["alphas"]["0.03"]["P"],
    "R_a0.06": lambda r: r["alphas"]["0.06"]["R"],
    "P_a0.06": lambda r: r["alphas"]["0.06"]["P"],
    "R_a0.2": lambda r: r["alphas"]["0.2"]["R"],
    "P_a0.2": lambda r: r["alphas"]["0.2"]["P"],
    "R_a0.4": lambda r: r["alphas"]["0.4"]["R"],
    "P_a0.4": lambda r: r["alphas"]["0.4"]["P"],
}


def boot_median_ci(x, rng, B=4000):
    x = np.asarray(x, float)
    meds = np.median(rng.choice(x, size=(B, len(x)), replace=True), axis=1)
    return [float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))]


def slope(xs, ys):
    return float(np.polyfit(np.asarray(xs, float), np.asarray(ys, float), 1)[0])


def boot_slope(by_e, es, f, transform, rng, B=4000):
    vals = {e: np.array([f(r) for r in by_e[e]], float) for e in es}
    sl = []
    for _ in range(B):
        ys = [transform(np.median(rng.choice(vals[e], size=len(vals[e]), replace=True))) for e in es]
        sl.append(slope(es, ys))
    return [float(np.percentile(sl, 2.5)), float(np.percentile(sl, 97.5))]


def main():
    rng = np.random.default_rng(1)
    st, ours = load_study(), load_ours()
    es = [e for e in ES if e in ours]
    table = {}
    for e in es:
        row = {"samples_ours": len(ours[e]), "samples_study": len(st[e])}
        for q, f in QUANT.items():
            xo = [f(r) for r in ours[e]]
            xs = [f(r) for r in st[e]]
            mw = mannwhitneyu(xo, xs, alternative="two-sided")
            row[q] = {"ours_median": float(np.median(xo)), "ours_ci95": boot_median_ci(xo, rng),
                      "study_median": float(np.median(xs)), "study_ci95": boot_median_ci(xs, rng),
                      "mannwhitney_p": float(mw.pvalue)}
        # internal checks
        row["checks"] = {
            "sigma_equals_phase_all": all(r[w]["sigma_equals_phase"] for r in ours[e]
                                          for w in ("at_k_star", "at_k_star_minus_1")),
            "worklist_closure_agrees_all": all(r[w]["worklist_closure_agrees"] for r in ours[e]
                                               for w in ("at_k_star", "at_k_star_minus_1")),
            "phase_law_same_forced_set_all": all(r[w]["phase_law_same_forced_set"] for r in ours[e]
                                                 for w in ("at_k_star", "at_k_star_minus_1")),
            "k_star_is_least_all": all(r["k_star_is_least"] for r in ours[e]),
            "sigma_le_log2_fringe_all": all(r["at_k_star"].get("sigma_le_log2_fringe_all", True) and
                                            r["at_k_star_minus_1"].get("sigma_le_log2_fringe_all", True)
                                            for r in ours[e]),
            "max_sigma_equals_P_star_all": all(r["at_k_star"]["max_sigma"] == r["at_k_star"]["P"] for r in ours[e]),
        }
        table[e] = row
    sl = {}
    es_all = es
    es = [e for e in es_all if e in MAIN]
    fR = QUANT["R_star"]
    fP = QUANT["P_star"]
    for who, data in (("ours", ours), ("study_same_range", st)):
        sl[who] = {
            "R_star_log2_slope": slope(es, [np.log2(np.median([fR(r) for r in data[e]])) for e in es]),
            "R_star_log2_slope_ci95": boot_slope(data, es, fR, np.log2, rng),
            "P_star_slope": slope(es, [np.median([fP(r) for r in data[e]]) for e in es]),
            "P_star_slope_ci95": boot_slope(data, es, fP, lambda x: x, rng),
        }
    big = [e for e in es if e >= 14]
    if len(big) >= 2:
        sl["ours"]["R_star_log2_slope_14_16"] = slope(big, [np.log2(np.median([fR(r) for r in ours[e]])) for e in big])
        sl["study_same_range"]["R_star_log2_slope_14_16"] = slope(
            big, [np.log2(np.median([fR(r) for r in st[e]])) for e in big])
    if 18 in ours:
        for lo in (14, 10):
            rng_e = [e for e in es_all if e >= lo]
            for who, data in (("ours", ours), ("study_same_range", st)):
                sl[who][f"R_star_log2_slope_{lo}_18"] = slope(rng_e, [np.log2(np.median([fR(r) for r in data[e]])) for e in rng_e])
                sl[who][f"R_star_log2_slope_{lo}_18_ci95"] = boot_slope(data, rng_e, fR, np.log2, rng)
                sl[who][f"P_star_slope_{lo}_18"] = slope(rng_e, [np.median([fP(r) for r in data[e]]) for e in rng_e])
    e_all = sorted(st)
    sl["study_reported"] = {
        "R_star_log2_slope_14_20": slope([e for e in e_all if e >= 14],
                                         [np.log2(np.median([fR(r) for r in st[e]])) for e in e_all if e >= 14]),
        "P_star_slope_10_20": slope(e_all, [np.median([fP(r) for r in st[e]]) for e in e_all]),
    }
    out = {"table": table, "slopes": sl}
    with open(os.path.join(HERE, "referee_task2_summary.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    # compact print
    for e in es_all:
        print(f"log2 n = {e}  (ours {table[e]['samples_ours']}, study {table[e]['samples_study']})")
        for q in QUANT:
            d = table[e][q]
            print(f"  {q:20s} ours {d['ours_median']:8.4g} {np.round(d['ours_ci95'], 4)}  study {d['study_median']:8.4g}"
                  f" {np.round(d['study_ci95'], 4)}  MW p={d['mannwhitney_p']:.3f}")
        print("  checks", table[e]["checks"])
    print(json.dumps(sl, indent=1))


if __name__ == "__main__":
    main()
