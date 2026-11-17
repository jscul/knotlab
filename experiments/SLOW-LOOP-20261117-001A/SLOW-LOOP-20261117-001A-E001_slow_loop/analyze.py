"""Frozen analysis of SLOW-LOOP-20261117-001A's test (S3) and stress (S4) runs.

  python3 analyze.py <test dir> <summary.json> [--stress <stress dir>]

Per instance: the geometric mean of an arm's five runs (charged work W, CPU, flips). Per cell: the median over instances.
R(X) = X's cell figure over F's, F the better of NOV and PS, re-chosen in each of 10,000 paired bootstrap resamples over
instances (99% intervals). Ratios between arms the same way. Verdicts, decision rule and predictions as frozen in
research/SLOW-LOOP-20261117-001/preregistration.md.
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
                row["verdict"] = verdict(row["R_W"], row["R_CPU"])
                if cens > 0.05:
                    row["verdict"] += " (bound: over 5% censored)"
                for key in ("ties", "braids", "n_final", "rebuilds", "targets"):
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
        for num, den in [("G", "ST"), ("G", "RND"), ("G", "Gx"), ("G", "GO"), ("GO", "ST")]:
            if num in fw and den in fw:
                ratios[f"{num}/{den}"] = {"W": boot(fw, num, [den], idx, rng), "CPU": boot(fc, num, [den], idx, rng)}
        if "G" in arms and "RND" in arms:
            fh = {"G": hits(arms["G"]), "RND": hits(arms["RND"])}
            if all(fh["RND"][i] > 0 for i in idx) and all(fh["G"][i] > 0 for i in idx):
                ratios["finds G/RND"] = boot(fh, "G", ["RND"], idx, rng)
            else:
                ratios["finds G/RND"] = None  # some instance with no finds: ratio of medians reported below
            ratios["finds medians"] = {"G": float(np.median([fh["G"][i] for i in idx])),
                                       "RND": float(np.median([fh["RND"][i] for i in idx]))}
        cell["ratios"] = ratios
        if "CDCL" in arms:
            cd = arms["CDCL"]
            solved = [i for i, r in cd.items() if r["cdcl"]["result"] is True]
            cell["CDCL"] = {"instances": len(cd), "solved_60s": len(solved),
                            "median_cpu": float(np.median([r["cdcl"]["cpu"] for r in cd.values()])),
                            "median_propagations": float(np.median([r["cdcl"].get("propagations", -1)
                                                                    for r in cd.values()])),
                            "models_ok": all(r["cdcl"]["model_ok"] for r in cd.values() if r["cdcl"]["result"]),
                            "G_median_cpu_same": float(np.median([fc["G"][i] for i in cd if i in fc["G"]]))
                            if "G" in fc else None}
        out[name] = cell
    return out


def decide(s):
    held = ["local-w10-3200", "local-w40-3200", "embed-3200"]
    tune = ["rand-3200", "block-3200"]
    g = {c: s[c]["arms"]["G"] for c in s if "G" in s[c]["arms"]}
    wins = [c for c in held if c in g and g[c]["verdict"].startswith("charged win")]
    no_loss_tune = all(not g[c]["verdict"].startswith("loss") for c in tune if c in g)
    any_win = [c for c in g if g[c]["verdict"].startswith("charged win")]
    beat_st = [c for c in wins if s[c]["ratios"]["G/ST"]["W"][2] < 1]
    dwell = [c for c in wins if s[c]["ratios"]["G/RND"]["W"][0] <= 0.9 and s[c]["ratios"]["G/RND"]["W"][2] < 1]
    st_as_good = bool(any_win) and all(s[c]["ratios"]["G/ST"]["W"][0] >= 1 for c in any_win)
    if wins and no_loss_tune and set(beat_st) & set(dwell):
        rule = ("1 attention pays: scheduling the moves by the search's attention counts pays, carries over, beats static "
                "probing and beats random targets")
    elif wins and no_loss_tune and beat_st:
        rule = ("2 pays, attention not shown: the slow loop pays, carries over and beats static probing, but the attention "
                "counts are not shown to matter (G/RND not below 0.9 where it wins)")
    elif any_win and st_as_good:
        rule = "3 static is as good: structure change pays where the pattern has local structure; static probing gets it as cheaply"
    elif not any_win:
        rule = "4 no win: no charged win for G anywhere"
    else:
        rule = "5 default: G wins somewhere, but none of readings 1-4 holds as frozen (see cells)"
    return {"rule": rule, "held_out_wins": wins, "all_wins": any_win, "no_loss_on_tuning": no_loss_tune,
            "wins_beating_ST": beat_st, "wins_beating_RND": dwell}


def predictions(s):
    P = {}

    def arm(c, a):
        return s[c]["arms"][a]
    P["P1"] = arm("local-w10-3200", "G")["verdict"].startswith("charged win")
    r = arm("rand-3200", "G")["R_W"]
    P["P2"] = r[0] <= 1.15 and r[2] <= 1.25
    P["P3"] = arm("block-3200", "G")["R_W"][0] > 0.8
    P["P4"] = arm("local-w40-3200", "G")["verdict"].startswith(("charged win", "work win"))
    P["P5"] = s["local-w10-3200"]["ratios"]["G/ST"]["W"][0] >= 0.9
    P["P6"] = any(s[c]["ratios"]["G/RND"]["W"][0] <= 0.9 and s[c]["ratios"]["G/RND"]["W"][2] < 1
                  for c in s if c.endswith("3200"))
    t = s["local-w10-3200"]["ratios"]["G/GO"]["W"][0]
    P["P7"] = 0.8 <= t <= 1.25
    P["P8"] = all(0.9 <= s[c]["ratios"]["G/Gx"]["W"][0] <= 1.11 for c in s)
    cd = s["local-w10-3200"].get("CDCL")
    P["P9"] = bool(cd and cd["solved_60s"] == cd["instances"] and cd["median_cpu"] < cd["G_median_cpu_same"])
    cr = s["rand-3200"].get("CDCL")
    P["P10"] = bool(cr and cr["solved_60s"] < cr["instances"] / 2)
    P["P11"] = all(row["unverified"] == 0 and row["contradictions"] == 0 for c in s for row in s[c]["arms"].values())
    fm = s["embed-3200"]["ratios"].get("finds medians")
    P["P12"] = bool(fm and fm["G"] >= fm["RND"])
    P["P13"] = arm("embed-3200", "G")["verdict"].startswith(("charged win", "work win"))
    return P


def table(s):
    lines = ["| Cell | F | " + " | ".join(f"{a} R_W" for a in ("G", "Gx", "RND", "ST", "GO")) + " | G verdict |",
             "| --- | --- | " + " | ".join("---" for _ in range(5)) + " | --- |"]
    for c, cell in s.items():
        f = cell["arms"][cell["F_point"]]
        row = [c, f"{cell['F_point']} {f['W']:.3g}"]
        for a in ("G", "Gx", "RND", "ST", "GO"):
            if a in cell["arms"]:
                p, lo, hi = cell["arms"][a]["R_W"]
                row.append(f"{p:.2f} [{lo:.2f}, {hi:.2f}]")
            else:
                row.append("")
        row.append(cell["arms"]["G"]["verdict"] if "G" in cell["arms"] else "")
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
