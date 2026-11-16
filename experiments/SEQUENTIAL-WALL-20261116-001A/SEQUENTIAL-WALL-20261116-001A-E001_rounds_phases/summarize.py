"""Read-out of SEQUENTIAL-WALL-20261116-001A-E001 against the frozen predictions.

python3 -B summarize.py RUN_DIR   (the shared runner's output directory)
Writes summary.json beside this study's artifacts and prints each verdict.
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from longrun import load_results  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "SEQUENTIAL-WALL-20261116-001A",
                   "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases")


def med(xs):
    return float(np.median(xs)) if len(xs) else float("nan")


def slope(xs, ys):
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    return float(np.polyfit(xs, ys, 1)[0])


def main(run_dir):
    recs = load_results(run_dir)
    res = {k: v["result"] for k, v in recs.items() if v.get("status") == "ok"}
    bad = sorted(k for k, v in recs.items() if v.get("status") != "ok")
    out = {"cases_ok": len(res), "cases_not_ok": bad, "verdicts": {}, "tables": {}}
    V = out["verdicts"]

    rand = [r for k, r in res.items() if k.startswith("rand-")]
    by_e = {}
    for r in rand:
        by_e.setdefault(r["e"], []).append(r)
    es = sorted(by_e)
    tab = {}
    for e in es:
        rs = by_e[e]
        tab[e] = {
            "samples": len(rs),
            "alpha_star_median": med([r["alpha_star"] for r in rs]),
            "R_star": med([r["at_k_star"]["R"] for r in rs]),
            "P_star": med([r["at_k_star"]["P"] for r in rs]),
            "R_minus": med([r["at_k_star_minus_1"]["R"] for r in rs]),
            "P_minus": med([r["at_k_star_minus_1"]["P"] for r in rs]),
            "closure_star": med([r["at_k_star"]["closure"] / r["n"] for r in rs]),
            "closure_minus": med([r["at_k_star_minus_1"]["closure"] / r["n"] for r in rs]),
            "R_alpha_mf": med([r["alpha_mf"]["R"] for r in rs]),
            "P_alpha_mf": med([r["alpha_mf"]["P"] for r in rs]),
            "log2_fringe_star": med([r["at_k_star"]["max_log2_fringe"] for r in rs]),
            "strahler_equals_phase_all": all(r["at_k_star"]["rank_equals_phase"] and
                                             r["at_k_star_minus_1"]["rank_equals_phase"] for r in rs),
            "R_ratio_over_P": med([r["at_k_star"]["R"] / max(1, r["at_k_star"]["P"]) for r in rs]),
            "alphas": {a: {"R": med([r["alphas"][a]["R"] for r in rs]), "P": med([r["alphas"][a]["P"] for r in rs])}
                       for a in rs[0]["alphas"]},
            "offsets": {o: {"R": med([r["offsets"][o]["R"] for r in rs if o in r["offsets"]]),
                            "P": med([r["offsets"][o]["P"] for r in rs if o in r["offsets"]])}
                        for o in rs[0]["offsets"]},
        }
    out["tables"]["random"] = tab

    g_ok = all(tab[e]["strahler_equals_phase_all"] for e in es)
    circ = {k: r for k, r in res.items() if k.startswith(("circ-", "unl-"))}
    g_ok &= all(r["evaluation_matches"] and r["forced_or_unforced_everywhere"] for r in circ.values())
    V["G (in-run part)"] = {"holds": bool(g_ok and not bad)}

    p1 = {}
    for a in ("0.03", "0.06", "0.2", "0.4"):
        p1[a] = [tab[20]["alphas"][a]["R"], tab[12]["alphas"][a]["R"]]
    V["P1"] = {"values": p1, "holds": all(v[0] <= 3 * v[1] for v in p1.values())}

    big = [e for e in es if e >= 14]
    s_star = slope(big, [np.log2(tab[e]["R_star"]) for e in big])
    s_mf = slope(big, [np.log2(tab[e]["R_alpha_mf"]) for e in big])
    V["P2"] = {"slope_k_star": s_star, "slope_alpha_mf": s_mf, "holds": s_star >= 0.15 and s_mf >= 0.15}
    V["P2a"] = {"slope_k_star": s_star, "holds": 0.29 <= s_star <= 0.37}
    V["P2b"] = {"slope_alpha_mf": s_mf, "holds": 0.21 <= s_mf <= 0.29}

    ps = [tab[e]["P_star"] for e in es]
    s_p = slope(es, ps)
    growth = tab[20]["P_star"] - tab[10]["P_star"]
    V["P3"] = {"P_star_by_e": dict(zip(es, ps)), "growth_2^10_to_2^20": growth, "slope": s_p,
               "holds": tab[20]["P_star"] <= 16 and 2 <= growth <= 8 and 0.2 <= s_p <= 0.8,
               "rejected_alternative_loglog_view_right": growth <= 1}
    V["P3b"] = {"R_over_P_2^20": tab[20]["R_ratio_over_P"], "R_over_P_2^12": tab[12]["R_ratio_over_P"],
                "holds": tab[20]["R_ratio_over_P"] >= 3 * tab[12]["R_ratio_over_P"]}

    p4 = {}
    ok4 = True
    for e in (18, 20):
        o = tab[e]["offsets"]
        dP = o["0.001"]["P"] - o["0.03"]["P"]
        rR = o["0.001"]["R"] / o["0.03"]["R"]
        p4[e] = {"P_diff": dP, "R_ratio": rR}
        ok4 &= (1 <= dP <= 5) and (2 <= rR <= 12)
    V["P4"] = {"values": p4, "holds": bool(ok4)}

    cnt = 0
    for r in by_e[20]:
        a = r["at_k_star"]
        new = a["closure"] - a["k"]
        cnt += int(max(a["phase_sizes"]) * 2 >= new) if a["phase_sizes"] else 0
    V["P5"] = {"samples_with_half_in_one_phase": cnt, "of": len(by_e[20]), "holds": cnt >= 7}

    lay = {}
    for k, r in res.items():
        if k.startswith("circ-"):
            lay.setdefault((r["w"], r["d"]), []).append(r)
    ltab = {}
    for (w, d), rs in sorted(lay.items()):
        alive = [r for r in rs if r["out_true"] > 0]
        ltab[f"w{w}-d{d}"] = {"alive": len(alive), "of": len(rs),
                             "out_max_strahler": med([r["out_max_rank"] for r in alive]),
                             "P": med([r["P"] for r in rs]), "P_dual": med([r["P_dual"] for r in rs]),
                             "two_sided": med([r["two_sided"] for r in rs]), "R": med([r["R"] for r in rs])}
    out["tables"]["layered"] = ltab
    a256, a64 = ltab["w1024-d256"], ltab["w1024-d64"]
    ratio6 = a256["out_max_strahler"] / a64["out_max_strahler"]
    V["P6"] = {"d256": a256["out_max_strahler"], "d64": a64["out_max_strahler"], "ratio": ratio6,
               "alive_d256": a256["alive"],
               "holds": ratio6 >= 1.6 and a256["out_max_strahler"] >= 6 and a256["alive"] >= 7}
    V["P6-linear"] = {"ratio": ratio6, "holds": ratio6 >= 3}
    r7 = a256["two_sided"] / max(1e-9, a64["two_sided"])
    V["P7"] = {"d256": a256["two_sided"], "d64": a64["two_sided"], "ratio": r7, "holds": r7 >= 1.6}

    unl = {}
    for k, r in res.items():
        if k.startswith("unl-"):
            unl.setdefault(r["g"], []).append(r)
    utab = {g: {"out_max_strahler": med([r["out_max_rank"] for r in rs]), "P": med([r["P"] for r in rs]),
                "P_dual": med([r["P_dual"] for r in rs]), "R": med([r["R"] for r in rs])}
            for g, rs in sorted(unl.items())}
    out["tables"]["unlayered"] = utab
    vals = [utab[g]["out_max_strahler"] for g in sorted(utab)]
    V["P8"] = {"by_size": {g: utab[g]["out_max_strahler"] for g in sorted(utab)},
               "holds": max(vals) <= 8 and vals[-1] - vals[0] <= 3}

    p9 = {e: [tab[e]["log2_fringe_star"], tab[e]["P_star"]] for e in (16, 18, 20)}
    V["P9"] = {"values": p9, "holds": all(f >= 3 * p for f, p in p9.values())}

    struct = {k: r for k, r in res.items() if k.split("-")[0] in ("chain", "ladder", "pyramid", "tree")}
    out["tables"]["structured"] = struct
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "summary.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    for k, v in V.items():
        print(k, "HOLDS" if v["holds"] else "FAILS", {x: y for x, y in v.items() if x != "holds"})


if __name__ == "__main__":
    main(sys.argv[1])
