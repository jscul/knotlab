"""Frozen analysis of EARN-BUDGET-20261117-001A's test (T1) and stress (T2) runs (SLOW-LOOP-20261117-001A's analysis,
copied; arms, ratios, decision rule and predictions changed).

  python3 analyze.py <test dir> <summary.json> [--stress <stress dir>]

Per instance: the geometric mean of an arm's five runs (charged work W, CPU, flips). Per cell: the median over instances.
R(X) = X's cell figure over F's, F the better of NOV and PS, re-chosen in each of 10,000 paired bootstrap resamples over
instances (99% intervals). Ratios between arms the same way. Verdicts, decision rule and predictions as frozen in
research/EARN-BUDGET-20261117-001/preregistration.md.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from longrun import load_results  # noqa: E402

import job  # noqa: E402

B = 10_000
ALPHA = 0.01


def load(d):
    recs = load_results(d)
    bad = {k: r.get("status") for k, r in recs.items() if r.get("status") != "ok"}
    data = defaultdict(dict)  # cell -> arm -> {i: result}
    for k, r in recs.items():
        if r.get("status") != "ok":
            continue
        res = r["result"]
        i = int(k.split("|")[-1])
        data[res["cell"]].setdefault(res["arm"], {})[i] = res
    return data, bad


def figures(arm_res, key):
    """instance index -> geometric mean over runs of key"""
    out = {}
    for i, res in arm_res.items():
        v = [max(run[key], 1e-9) for run in res["runs"]]
        out[i] = math.exp(sum(math.log(x) for x in v) / len(v))
    return out


def boot(fig, num, den_choices, idx, rng):
    """ratio of medians num / min over den_choices, point and 99% interval, paired over instances idx"""
    a = np.array([fig[num][i] for i in idx])
    ds = [np.array([fig[d][i] for i in idx]) for d in den_choices]
    point = np.median(a) / min(np.median(d) for d in ds)
    n = len(idx)
    sel = rng.integers(0, n, (B, n))
    ma = np.median(a[sel], axis=1)
    md = np.min(np.stack([np.median(d[sel], axis=1) for d in ds]), axis=0)
    r = ma / md
    lo, hi = np.quantile(r, [ALPHA / 2, 1 - ALPHA / 2])
    return float(point), float(lo), float(hi)


def verdict(rw, rc):
    p, lo, hi = rw
    if p <= 0.8 and hi < 0.9:
        return "charged win" if rc[2] < 1 else "work win"
    if lo > 1.1:
        return "loss"
    return "parity or inconclusive"


def bound(num_cens, den_cens):
    """Over 5% censored in the numerator makes R a lower bound; in the denominator, an upper bound; in both, neither."""
    if num_cens > 0.05 and den_cens > 0.05:
        return "undetermined (both censored)"
    if num_cens > 0.05:
        return "at least"
    if den_cens > 0.05:
        return "at most"
    return ""


def hits(arm_res):
    """instance index -> moves found per 10^6 incidences of probe work, over its five runs"""
    out = {}
    for i, res in arm_res.items():
        f = sum(r.get("ties", 0) + r.get("shadows", 0) for r in res["runs"])
        w = sum(r.get("work_slow", 0) for r in res["runs"])
        out[i] = 1e6 * f / w if w > 0 else 0.0
    return out


def analyze(data, cells):
    rng = np.random.default_rng(20261117)
    out = {}
    for name in cells:
        arms = data.get(name, {})
        loc = [a for a in arms if a != "CDCL"]
        if not {"NOV", "PS"} <= set(loc):
            continue
        idx = sorted(set.intersection(*[set(arms[a]) for a in loc]))
        if not idx:
            continue
        cell = {"instances": len(idx), "arms": {}}
        fw = {a: figures(arms[a], "work") for a in loc}
        fc = {a: figures(arms[a], "cpu") for a in loc}
        ff = {a: figures(arms[a], "flips") for a in loc}
        cens_of = {}
        for a in loc:
            runs = [run for i in idx for run in arms[a][i]["runs"]]
            cens_of[a] = sum(not r["solved"] for r in runs) / len(runs)
        for a in loc:
            runs = [run for i in idx for run in arms[a][i]["runs"]]
            cens = cens_of[a]
            row = {"W": float(np.median([fw[a][i] for i in idx])), "CPU": float(np.median([fc[a][i] for i in idx])),
                   "flips": float(np.median([ff[a][i] for i in idx])), "censored": cens,
                   "unverified": sum(r["solved"] and not r["verified"] for r in runs),
                   "contradictions": sum(bool(r.get("contradiction")) for r in runs)}
            if a not in ("NOV", "PS"):
                row["R_W"] = boot(fw, a, ["NOV", "PS"], idx, rng)
                row["R_CPU"] = boot(fc, a, ["NOV", "PS"], idx, rng)
                row["R_flips"] = boot(ff, a, ["NOV", "PS"], idx, rng)
                row["R_W_vs_NOV"] = boot(fw, a, ["NOV"], idx, rng)
                row["verdict"] = verdict(row["R_W"], row["R_CPU"])
                b = bound(cens, max(cens_of["NOV"], cens_of["PS"]))
                if b:
                    row["verdict"] += f" (R is {b})"
                    row["bound"] = b
                for key in ("ties", "shadows", "n_final", "rebuilds", "targets", "cpu_fast", "cpu_slow", "cpu_rebuild",
                            "rho_top", "doublings"):
                    row[key] = float(np.median([np.median([r.get(key, 0) for r in arms[a][i]["runs"]]) for i in idx]))
                row["slow_share"] = float(np.median([np.median([(r["work_slow"] + r["work_rebuild"]) / r["work"]
                                                                for r in arms[a][i]["runs"]]) for i in idx]))
                row["slow_work"] = float(np.median([np.median([r["work_slow"] for r in arms[a][i]["runs"]])
                                                    for i in idx]))
                row["finds_per_1e6"] = float(np.median([hits(arms[a])[i] for i in idx]))
            cell["arms"][a] = row
        f_nov, f_ps = cell["arms"]["NOV"]["W"], cell["arms"]["PS"]["W"]
        cell["F_point"] = "NOV" if f_nov <= f_ps else "PS"
        ratios = {}
        for num, den in [("E", "Gb"), ("E", "GbO"), ("E", "Gm"), ("E", "ST"), ("E", "GO"), ("E", "G"), ("Erb", "E"),
                         ("Erb", "ErbL"), ("Gb", "Gm")]:
            if num in fw and den in fw:
                ratios[f"{num}/{den}"] = {"W": boot(fw, num, [den], idx, rng), "CPU": boot(fc, num, [den], idx, rng)}
        cell["ratios"] = ratios
        if "CDCL" in arms:
            cd = arms["CDCL"]
            # the 60 s interrupt did not stop CaDiCaL (pysat), so every run went to its answer; "within 60 s" is read from
            # the wall time
            solved = [i for i, r in cd.items() if r["cdcl"]["result"] is True and r["cdcl"]["wall"] <= 60.0]
            cell["CDCL"] = {"instances": len(cd), "solved_60s": len(solved),
                            "solved_any_time": sum(r["cdcl"]["result"] is True for r in cd.values()),
                            "max_wall": float(max(r["cdcl"]["wall"] for r in cd.values())),
                            "median_cpu": float(np.median([r["cdcl"]["cpu"] for r in cd.values()])),
                            "median_propagations": float(np.median([r["cdcl"].get("propagations", -1)
                                                                    for r in cd.values()])),
                            "models_ok": all(r["cdcl"]["model_ok"] for r in cd.values() if r["cdcl"]["result"]),
                            "G_median_cpu_same": float(np.median([fc["G"][i] for i in cd if i in fc["G"]]))
                            if "G" in fc else None}
        out[name] = cell
    return out


PRIMARY = "local35-w15-3200"
STRUCTURED_HELD = ["local35-w15-3200", "local-w40-3200", "local-w20-3200", "local3-w10-3200"]
POOR = ["rand-3200", "rand3-3200", "heavy-3200"]


def decide(s):
    """The frozen rule, applied in order; the first reading that holds is the verdict. A win is a charged win."""
    def v(c, a):
        return s[c]["arms"][a]["verdict"]

    def r(c, key):
        return s[c]["ratios"][key]["W"]
    wins = [c for c in STRUCTURED_HELD if v(c, "E").startswith("charged win")]
    poor_loss = [c for c in POOR if s[c]["arms"]["E"]["R_W"][1] > 1.1]
    beats_gb = [c for c in s if r(c, "E/Gb")[0] <= 0.9 and r(c, "E/Gb")[2] < 1]
    not_worse_gb = all(r(c, "E/Gb")[2] < 1.1 for c in s)
    beats_st = [c for c in wins if r(c, "E/ST")[2] < 1]
    near_go = r("local-w10-3200", "E/GO")[0] <= 1.5
    primary_win = PRIMARY in wins
    if primary_win and len(wins) >= 2 and not poor_loss and beats_gb and not_worse_gb and beats_st and near_go:
        rule = ("1 the earned budget works: charged wins on the unseen primary and one more structured held-out pattern, no "
                "loss on a structure-poor one, better than the best fixed batched budget somewhere and not worse anywhere, "
                "better than static probing where it wins, and within 1.5 times the eager oracle on local w10")
    elif primary_win and len(wins) >= 2 and not poor_loss:
        rule = ("2 it works, but earning is not shown to matter: as 1 without the comparisons with the fixed batched budget, "
                "static probing or the eager oracle (see which failed)")
    elif wins:
        rule = "3 partial: a charged win on some structured held-out pattern, but not as 1 or 2 require"
    else:
        rule = "4 no charged win on any structured held-out pattern"
    return {"rule": rule, "E_wins_held_out": wins, "primary_win": primary_win, "E_losses_poor": poor_loss,
            "E_beats_Gb": beats_gb, "E_not_worse_than_Gb_anywhere": not_worse_gb, "E_beats_ST_where_it_wins": beats_st,
            "E_within_1.5_of_GO_on_w10": near_go,
            "Erb_removes_SLOW_LOOP_obstruction": v("local-w10-3200", "Erb").startswith("charged win"),
            "ErbL_removes_it": v("local-w10-3200", "ErbL").startswith("charged win")}


def predictions(s):
    def arm(c, a):
        return s[c]["arms"][a]
    P = {}
    P["P1"] = arm("local35-w15-3200", "E")["verdict"].startswith("charged win")
    P["P2"] = arm("local-w20-3200", "E")["verdict"].startswith("charged win")
    P["P3"] = arm("local-w40-3200", "E")["verdict"].startswith("charged win")
    P["P4"] = arm("local3-w10-3200", "E")["verdict"].startswith("charged win")
    P["P5"] = all(arm(c, "E")["R_W"][0] <= 1.1 for c in POOR)
    P["P6"] = any(s[c]["ratios"]["E/Gb"]["W"][0] <= 0.9 and s[c]["ratios"]["E/Gb"]["W"][2] < 1 for c in s) and \
        all(s[c]["ratios"]["E/Gb"]["W"][2] < 1.1 for c in s)
    P["P7"] = arm("local-w10-3200", "Erb")["verdict"].startswith("charged win")
    P["P8"] = s["local-w10-3200"]["ratios"]["E/GO"]["W"][0] <= 1.5
    P["P9"] = all(s[c]["ratios"]["E/GbO"]["W"][0] <= 1.25 for c in STRUCTURED_HELD)
    P["P10"] = all(s[c].get("CDCL", {}).get("max_wall", 99) < 1.0 for c in ("local35-w15-3200", "local-w20-3200",
                                                                             "local3-w10-3200"))
    P["P11"] = all(row["unverified"] == 0 and row["contradictions"] == 0 for c in s for row in s[c]["arms"].values())
    P["P12"] = arm("block-3200", "E")["verdict"].startswith("charged win")
    return P


def table(s):
    arms = ("E", "Erb", "ErbL", "Gb", "GbO", "Gm", "ST", "G", "GO")
    lines = ["| Cell | F | " + " | ".join(f"{a} R_W" for a in arms) + " | E verdict |",
             "| --- | --- | " + " | ".join("---" for _ in arms) + " | --- |"]
    for c, cell in s.items():
        f = cell["arms"][cell["F_point"]]
        row = [c, f"{cell['F_point']} {f['W']:.3g}"]
        for a in arms:
            if a in cell["arms"]:
                p, lo, hi = cell["arms"][a]["R_W"]
                row.append(f"{p:.2f} [{lo:.2f}, {hi:.2f}]")
            else:
                row.append("")
        row.append(cell["arms"]["E"]["verdict"] if "E" in cell["arms"] else "")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main():
    test_dir, out = sys.argv[1], sys.argv[2]
    data, bad = load(test_dir)
    s = analyze(data, [c[0] for c in job.CELLS])
    summ = {"cells": s, "not_ok": bad}
    if len(s) == len(job.CELLS):
        summ["decision"] = decide(s)
        summ["predictions"] = predictions(s)
    if "--stress" in sys.argv:
        sd, sbad = load(sys.argv[sys.argv.index("--stress") + 1])
        summ["stress"] = analyze(sd, [c[0] for c in job.STRESS_CELLS])
        summ["stress_not_ok"] = sbad
    Path(out).write_text(json.dumps(summ, indent=1))
    print(table(s))
    if "decision" in summ:
        print(json.dumps(summ["decision"], indent=1))
        print(json.dumps(summ["predictions"]))


if __name__ == "__main__":
    main()
