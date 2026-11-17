"""Analysis of MEET-TRANSFER-20261117-001A, following its frozen pre-registration.

  analyze_meet.py screen  --runs DIR --out screen.json      stage 1: keep the top three Novelty+, top probSAT, top WalkSAT
  analyze_meet.py confirm --runs DIR --out retuned.json     stage 2: rank them on 20 instances x 5 runs by the test metric
  analyze_meet.py gates   --training DIR --out gates.json   G-learn per arm and training pattern
  analyze_meet.py summary --runs DIR --out summary.json

The per-instance figure is the geometric mean of the five run lengths (a censored run counted at the cap); a seed's figure is
the median over instances; an arm's figure is the geometric mean of its seeds' figures. R divides it by the best rule's, the best
rule re-chosen in each of 10,000 paired resamples (99% intervals).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
from longrun import load_results  # noqa: E402

B = 10_000
LEVEL = 99.0
SEEDS = {"D": 4, "Dl": 4, "Dr": 2, "Dn": 2, "L3sm": 2}
PRIMARY = "local4.0w10|3200"


def family_of(algo):
    return "novelty_plus" if algo == "novelty_plus" else ("probsat" if algo.startswith("probsat") else algo)


def ok(path):
    return [rec["result"] for rec in load_results(str(path)).values() if rec["status"] == "ok"]


def key(cell):
    fam, alpha, w, n = cell
    return f"{fam}{alpha}w{w}|{n}"


def inst_geo(runs, cap):
    return math.exp(np.mean([math.log(r["flips"] if r["solved"] else cap) for r in runs]))


def inst_score(runs, cap):
    return float(np.mean([math.log(r["flips"]) if r["solved"] else math.log(cap) + math.log1p(r["minviol"]) for r in runs]))


def cmd_screen(a):
    by = defaultdict(lambda: defaultdict(list))
    for r in ok(a.runs):
        by[key(r["cell"])][(r["algo"], tuple(r["params"]))].append(inst_score(r["runs"], r["cap"]))
    out = {}
    for cell, d in by.items():
        ranked = sorted(d.items(), key=lambda kv: float(np.median(kv[1])))
        pick = [k for k in ranked if k[0][0] == "novelty_plus"][:3]
        for fam in ("probsat", "walksat"):
            pick += [k for k in ranked if family_of(k[0][0]) == fam][:1]
        out[cell] = [[algo, list(prm)] for (algo, prm), _ in pick]
        print(cell, [(algo, prm, round(float(np.median(v)), 2)) for (algo, prm), v in pick])
    Path(a.out).write_text(json.dumps(out, indent=1))


def cmd_confirm(a):
    by = defaultdict(lambda: defaultdict(list))
    for r in ok(a.runs):
        by[key(r["cell"])][(r["algo"], tuple(r["params"]))].append(inst_geo(r["runs"], r["cap"]))
    out = {}
    detail = {}
    for cell, d in by.items():
        med = {k: float(np.median(v)) for k, v in d.items()}
        nov = sorted([k for k in med if k[0] == "novelty_plus"], key=lambda k: med[k])
        arms = [[f"novelty_plus#{i + 1}", algo, list(prm)] for i, (algo, prm) in enumerate(nov)]
        for fam in ("probsat", "walksat"):
            ks = sorted([k for k in med if family_of(k[0]) == fam], key=lambda k: med[k])
            if ks:
                arms.append([fam, ks[0][0], list(ks[0][1])])
        out[cell] = arms
        detail[cell] = {f"{k[0]}{k[1]}": v for k, v in med.items()}
        print(cell, [(n, al, p, round(med[(al, tuple(p))])) for n, al, p in arms])
    Path(a.out).write_text(json.dumps(out, indent=1))
    Path(a.out).with_name("confirm_detail.json").write_text(json.dumps(detail, indent=1))


def cmd_gates(a):
    import engine as E
    import train_mixed as M
    from multiprocessing import Pool
    refs = {}
    cells = [("rand", 2.1, 10), ("rand", 4.0, 10), ("block", 2.5, 20), ("local", 4.0, 10)]
    tasks = [(c, algo, prm, M.VAL_SEED0 + i) for c in cells for algo, prm in (("novelty_plus", (0.7, 0.01)), ("probsat_poly", (1.8, 1.0)))
             for i in range(M.VAL_PER_CELL)]
    with Pool(8) as p:
        res = p.map(_ref_one, tasks)
    for (c, algo, prm, s), f in zip(tasks, res):
        refs.setdefault(f"{c[0]}{c[1]}", {}).setdefault(algo, []).append(f)
    refm = {c: {al: float(np.median(v)) for al, v in d.items()} for c, d in refs.items()}
    out = {"references": refm}
    for d in sorted((Path(a.training) / "runs").iterdir()):
        s = json.loads((d / "summary.json").read_text())
        rows = [json.loads(l) for l in (d / "log.jsonl").read_text().splitlines() if '"val_medians"' in l]
        sel = min(rows, key=lambda r: r["val_mean_log_flips"])
        arm = d.name.split("_s")[0]
        g = {}
        for c, m in sel["val_medians"].items():
            ref = refm[c]["probsat_poly"] if arm == "Dn" else min(refm[c].values())
            g[c] = {"median": m, "reference": ref, "ratio": m / ref, "pass": m <= 1.15 * ref}
        out[d.name] = {"selected_tag": sel["tag"], "families": g, "G_learn": all(v["pass"] for v in g.values()),
                       "cpu_total": s["cpu_total"]}
        print(d.name, out[d.name]["G_learn"], {c: round(v["ratio"], 2) for c, v in g.items()})
    Path(a.out).write_text(json.dumps(out, indent=1))


def _ref_one(t):
    import engine as E
    import train_mixed as M
    (fam, alpha, w), algo, prm, s = t
    i = E.planted(fam, M.VAL_N, alpha, s, w=w)
    return E.run(i, algo, prm, seed=s, max_flips=M.VAL_CAP)["flips"]


def cmd_summary(a):
    rows = []
    for d in a.runs:
        rows += ok(d)
    cells = defaultdict(lambda: defaultdict(dict))
    caps = {}
    for r in rows:
        k = key(r["cell"])
        cells[k][r["arm"]][r["seed"]] = r
        caps[k] = r["cap"]
    rng = np.random.default_rng(20261117)
    summary = {"cells": {}}
    for k, arms in sorted(cells.items()):
        seeds = sorted(set.intersection(*[set(v) for v in arms.values()]))
        S = len(seeds)
        cap = caps[k]
        G = {arm: np.array([inst_geo(v[s]["runs"], cap) for s in seeds]) for arm, v in arms.items()}
        cens = {arm: float(np.mean([not q["solved"] for s in seeds for q in v[s]["runs"]])) for arm, v in arms.items()}
        cpu = {arm: float(np.median([np.mean([q["cpu"] for q in v[s]["runs"]]) for s in seeds])) for arm, v in arms.items()}
        rules = [arm for arm in arms if not any(arm.startswith(p + "_s") for p in SEEDS)]
        idx = [rng.integers(0, S, S) for _ in range(B)]

        def armfig(name, ix=None):
            ks = [f"{name}_s{j}" for j in range(SEEDS[name]) if f"{name}_s{j}" in G]
            return math.exp(np.mean([math.log(np.median(G[x] if ix is None else G[x][ix])) for x in ks]))

        def best(ix=None):
            return min(np.median(G[r] if ix is None else G[r][ix]) for r in rules)

        def ratio(num, den):
            pt = num(None) / den(None)
            bs = np.array([num(ix) / den(ix) for ix in idx])
            lo, hi = np.percentile(bs, [(100 - LEVEL) / 2, 100 - (100 - LEVEL) / 2])
            return {"point": float(pt), "lo": float(lo), "hi": float(hi)}

        bname = min(rules, key=lambda r: np.median(G[r]))
        cell = {"instances": S, "cap": cap, "best_rule": bname,
                "arms": {arm: {"median": float(np.median(G[arm])), "p95": float(np.percentile(G[arm], 95)),
                               "censored_runs": cens[arm], "median_cpu": cpu[arm]} for arm in arms},
                "R": {}, "R_seed": {}, "ratios": {}, "usable": {}}
        for name in SEEDS:
            ks = [f"{name}_s{j}" for j in range(SEEDS[name])]
            if not all(x in G for x in ks):
                continue
            cell["R"][name] = ratio(lambda ix, n=name: armfig(n, ix), best)
            cell["R_seed"][name] = [float(np.median(G[x]) / best()) for x in ks]
            solved_arm = 1 - np.mean([cens[x] for x in ks])
            p95 = math.exp(np.mean([math.log(np.percentile(G[x], 95)) for x in ks])) / np.percentile(G[bname], 95)
            r = cell["R"][name]
            cell["usable"][name] = {"R_ok": r["point"] <= 2.0 and r["hi"] < 2.5, "solved_ok": solved_arm >= 1 - cens[bname],
                                    "p95_ratio": float(p95), "p95_ok": p95 <= 3.0,
                                    "seeds_ok": all(v <= 2.0 for v in cell["R_seed"][name])}
            cell["usable"][name]["usable"] = all(cell["usable"][name][x] for x in ("R_ok", "solved_ok", "p95_ok", "seeds_ok"))
        for nm, (x, y) in {"X": ("D", "Dr"), "Y": ("D", "L3sm"), "Z": ("Dr", "L3sm"), "K": ("D", "Dn"), "oracle": ("D", "Dl")}.items():
            if x in cell["R"] and y in cell["R"]:
                cell["ratios"][nm] = ratio(lambda ix, x=x: armfig(x, ix), lambda ix, y=y: armfig(y, ix))
        summary["cells"][k] = cell
    # verdict for D on the primary cell
    c = summary["cells"].get(PRIMARY)
    if c and "D" in c["R"]:
        r, sv = c["R"]["D"], c["R_seed"]["D"]
        win = r["point"] <= 0.8 and r["hi"] < 0.9 and all(v <= 0.8 for v in sv)
        cost = c["arms"]["D_s0"]["median_cpu"] < c["arms"][c["best_rule"]]["median_cpu"]
        if win and cost:
            v = "real win"
        elif win:
            v = "mechanism win"
        elif r["lo"] > 0.9 and all(x > 0.9 for x in sv):
            v = "clean loss"
        elif (r["lo"] > 0.9) != all(x > 0.9 for x in sv):
            v = "inconclusive (seed split: learner variance)"
        else:
            v = "inconclusive"
        summary["verdict_D_primary"] = {"verdict": v, "R": r, "R_seeds": sv, "usable": c["usable"]["D"]}
    Path(a.out).write_text(json.dumps(summary, indent=1, default=float))
    for k, c in summary["cells"].items():
        print(f"== {k} ({c['instances']} instances; best rule {c['best_rule']} {c['arms'][c['best_rule']]['median']:.0f})")
        for name, r in c["R"].items():
            u = c["usable"][name]
            print(f"  R {name}: {r['point']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}] seeds {[round(x, 2) for x in c['R_seed'][name]]} "
                  f"usable {u['usable']} (p95 {u['p95_ratio']:.2f})")
        for nm, r in c["ratios"].items():
            print(f"  {nm}: {r['point']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]")
    print("verdict:", summary.get("verdict_D_primary"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nm in ("screen", "confirm", "summary"):
        p = sub.add_parser(nm)
        p.add_argument("--runs", nargs="+" if nm == "summary" else None, required=True)
        p.add_argument("--out", required=True)
    p = sub.add_parser("gates")
    p.add_argument("--training", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd in ("screen", "confirm") and isinstance(a.runs, list):
        a.runs = a.runs[0]
    {"screen": cmd_screen, "confirm": cmd_confirm, "gates": cmd_gates, "summary": cmd_summary}[a.cmd](a)
