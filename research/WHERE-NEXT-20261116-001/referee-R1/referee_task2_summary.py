"""Task 2 summary: the widely tuned rules against L3, with L3's median taken both from the study's single
run per instance and from the referee's five fresh-seed L3 runs per instance (referee_L3_rerun.json).
Ratios are rule / L3 (above 1: L3 takes fewer flips), paired bootstrap over the 100 test instances, each
resampled instance bringing all of its runs on both sides. Writes referee_task2_summary.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import referee_common as C  # noqa: E402


def main():
    S = C.study_results()
    L3r = json.loads((C.HERE / "referee_L3_rerun.json").read_text())["cells"]
    out = {"cells": {}}
    for n in (200, 800, 3200):
        p = C.HERE / f"referee_task2_test_n{n}.json"
        if not p.exists():
            continue
        T = json.loads(p.read_text())
        seeds = [C.TEST_SEED0["rand"] + i for i in range(100)]
        L3s = {s: [S[("rand", n, "L3")][s][0]] for s in seeds}
        L3f = {int(k): v for k, v in L3r[f"L3|rand|{n}"]["fresh_flips_by_instance"].items()}
        nov = T["study_novelty_plus_arm"]
        NOV = {s: [S[("rand", n, nov)][s][0]] for s in seeds}
        cell = {"study_L3_median": float(np.median([v[0] for v in L3s.values()])),
                "fresh_L3_median_5reps": float(np.median(np.concatenate([L3f[s] for s in seeds]))),
                "study_novelty_plus": {"arm": nov, "median": float(np.median([v[0] for v in NOV.values()]))},
                "study_R_vs_retuned": None, "rules": []}
        cell["study_ratio_novelty_plus_over_L3"] = C.median_ratio_boot(NOV, L3s)
        cell["study_novelty_plus_over_fresh_L3"] = C.median_ratio_boot(NOV, L3f)
        for r in T["selected"]:
            d = {int(k): v for k, v in r["flips_by_instance"].items()}
            row = {"algo": r["algo"], "params": r["params"], "tuning_rank": r["tuning_rank"],
                   "median_5reps": r["median"],
                   "over_study_L3": C.median_ratio_boot(d, L3s),
                   "over_fresh_L3": C.median_ratio_boot(d, L3f),
                   "over_study_novelty_plus": C.median_ratio_boot(d, NOV)}
            cell["rules"].append(row)
        # headline picks
        sel = [x for x in cell["rules"] if x["tuning_rank"] == 0]
        cell["tuning_selected"] = {x["algo"]: {"params": x["params"], "median": x["median_5reps"],
                                               "over_fresh_L3": x["over_fresh_L3"]["point"],
                                               "over_fresh_L3_ci": [x["over_fresh_L3"]["lo"], x["over_fresh_L3"]["hi"]],
                                               "over_study_L3": x["over_study_L3"]["point"]} for x in sel}
        best5 = min((x for x in cell["rules"] if x["algo"] in ("novelty_plus", "novelty_pp")),
                    key=lambda x: x["median_5reps"])
        cell["best_of_top5_on_test"] = {"algo": best5["algo"], "params": best5["params"],
                                        "median": best5["median_5reps"], "over_fresh_L3": best5["over_fresh_L3"],
                                        "over_study_L3": best5["over_study_L3"]}
        cell["oracle_single_run_best"] = {a: {"params": v["params"], "median": v["median"],
                                              "over_study_L3": v["ratio_to_L3"]["point"]}
                                          for a, v in T["oracle_best_per_family"].items()}
        out["cells"][str(n)] = cell
        print(f"n={n}: study L3 {cell['study_L3_median']:.1f}, fresh L3 {cell['fresh_L3_median_5reps']:.1f}; "
              f"study Nov+ {cell['study_novelty_plus']['median']:.1f} (/study L3 "
              f"{cell['study_ratio_novelty_plus_over_L3']['point']:.2f}, /fresh L3 "
              f"{cell['study_novelty_plus_over_fresh_L3']['point']:.2f})")
        for a, v in cell["tuning_selected"].items():
            print(f"   tuning-selected {a:20s} {str(v['params']):18s} median {v['median']:>9.1f} /fresh L3 "
                  f"{v['over_fresh_L3']:.3f} [{v['over_fresh_L3_ci'][0]:.3f}, {v['over_fresh_L3_ci'][1]:.3f}] "
                  f"/study L3 {v['over_study_L3']:.3f}")
        b = cell["best_of_top5_on_test"]
        print(f"   best of top-5 on test {b['algo']} {b['params']} median {b['median']:.1f} /fresh L3 "
              f"{b['over_fresh_L3']['point']:.3f} [{b['over_fresh_L3']['lo']:.3f}, {b['over_fresh_L3']['hi']:.3f}] "
              f"/study L3 {b['over_study_L3']['point']:.3f}")
    C.jdump(out, C.HERE / "referee_task2_summary.json")


if __name__ == "__main__":
    main()
