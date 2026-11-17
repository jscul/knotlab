"""Analysis of SCALE-MEMORY-20261116-001A, following its frozen pre-registration.

  analyze_scale.py gates   --training DIR --novelty-val JSON
  analyze_scale.py summary --where DIR --runs DIR [DIR ...] --out summary.json

Per arm the flips figure is the geometric mean of its two seeds' median flips (WHERE-NEXT's L3 counts as an arm with seeds
L3_s0 and L3_s1, its seed-1 runs reused from WHERE-NEXT). R divides it by the best re-tuned hand-written rule's median, with a
paired bootstrap that resamples instances, recomputes every median and re-chooses the best rule. Intervals are 99%.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from longrun import load_results  # noqa: E402

RULES = ["walksat", "probsat", "novelty_plus", "greedy_where", "sticky", "fms"]
ARMS = ["L3", "L3s", "L3m", "L3sm", "L2m", "L3c"]
PRIMARY = {"L3": 3200, "L3s": 3200, "L3m": 12800, "L3sm": 12800, "L2m": 12800, "L3c": 12800}
TRANSFER = {"L3": 12800, "L3s": 12800, "L3m": 51200, "L3sm": 51200, "L2m": 51200, "L3c": 51200}
RATIOS = {"S": ("L3s", "L3"), "T": ("L3m", "L3"), "C": ("L3m", "L3c"), "I_m": ("L3sm", "L3m"), "I_s": ("L3sm", "L3s"),
          "K": ("L3m", "L2m"), "seed_floor": ("L3_s0", "L3_s1")}
LEVEL = 99.0
B = 10_000


def ok_results(path):
    return [rec["result"] for rec in load_results(str(path)).values() if rec["status"] == "ok"]


def cmd_gates(a):
    nov = json.loads(Path(a.novelty_val).read_text())
    out = {}
    for d in sorted((Path(a.training) / "runs").iterdir()):
        s = json.loads((d / "summary.json").read_text())
        rows = [json.loads(l) for l in (d / "log.jsonl").read_text().splitlines() if '"val_median_flips"' in l]
        start = rows[0]["val_median_flips"]
        best = min(r["val_median_flips"] for r in rows)
        sel = min(rows, key=lambda r: r["val_mean_log_flips"])
        vn = str(s["val"][0])
        ref = nov[vn]["median_flips"]
        out[d.name] = {"val_n": int(vn), "selected_median": sel["val_median_flips"], "selected_tag": sel["tag"],
                       "novelty_median": ref, "G_learn_ratio": sel["val_median_flips"] / ref,
                       "G_learn": sel["val_median_flips"] <= 1.15 * ref,
                       "last_stage_start_median": start, "last_stage_best_median": best,
                       "G_train": best <= 0.95 * start, "cpu_total": s["cpu_total"]}
        print(d.name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[d.name].items()})
    Path(a.out).write_text(json.dumps(out, indent=1))


def cmd_summary(a):
    rows = []
    w = Path(a.where)
    for sub in ("test", "stress"):
        for r in ok_results(w / sub):
            if r["arm"] == "L3":
                r = {**r, "arm": "L3_s1"}
            if r["arm"] in ("L1", "L2", "L2w", "A0"):
                continue
            rows.append(r)
    for d in a.runs:
        rows += ok_results(d)
    cells = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        cells[(r["fam"], r["n"])][r["arm"]][r["seed"]] = r
    rng = np.random.default_rng(20261117)
    summary = {"cells": {}}
    for (fam, n), arms in sorted(cells.items()):
        seeds = sorted(set.intersection(*[set(v) for v in arms.values()]))
        S = len(seeds)
        fl = {arm: np.array([v[s]["flips"] if v[s]["solved"] else math.inf for s in seeds], dtype=float)
              for arm, v in arms.items()}
        rules = {r: fl.get(f"{r}@cell", fl.get(f"{r}@train")) for r in RULES if f"{r}@train" in fl}
        idx = [rng.integers(0, S, S) for _ in range(B)]

        def armstat(arm, ix=None):
            vals = []
            for k in (0, 1):
                f = fl[f"{arm}_s{k}"]
                vals.append(np.median(f if ix is None else f[ix]))
            return math.exp(np.mean(np.log(vals))) if all(np.isfinite(vals)) else math.inf

        def ratio(num, den):
            def one(ix=None):
                x = num(ix)
                y = den(ix)
                return x / y if np.isfinite(x) and np.isfinite(y) and y > 0 else (math.inf if not np.isfinite(x) else float("nan"))
            bs = np.array([one(ix) for ix in idx])
            lo, hi = np.nanpercentile(bs, [(100 - LEVEL) / 2, 100 - (100 - LEVEL) / 2])
            return {"point": one(), "lo": float(lo), "hi": float(hi), "level": LEVEL}

        best = lambda ix=None: min(np.median(v if ix is None else v[ix]) for v in rules.values())
        cell = {"instances": S, "arms": {}, "R": {}, "R_seed": {}, "ratios": {}}
        for arm, v in sorted(arms.items()):
            f = fl[arm]
            st = np.array([v[s]["flips"] for s in seeds], dtype=float)
            cpu = np.array([v[s]["cpu"] for s in seeds])
            work = np.array([v[s]["work"] for s in seeds], dtype=float)
            cell["arms"][arm] = {"solved": float(np.isfinite(f).mean()),
                                 "median_flips": float(np.median(f)) if np.isfinite(np.median(f)) else None,
                                 "median_cpu": float(np.median(cpu)), "median_work": float(np.median(work)),
                                 "cpu_per_flip_ns": 1e9 * cpu.sum() / st.sum()}
        if rules:
            bname = min(rules, key=lambda r: np.median(rules[r]))
            cell["best_rule"] = bname
            for arm in ARMS:
                if f"{arm}_s0" in fl and f"{arm}_s1" in fl:
                    cell["R"][arm] = ratio(lambda ix, arm=arm: armstat(arm, ix), best)
                    for k in (0, 1):
                        cell["R_seed"][f"{arm}_s{k}"] = float(np.median(fl[f"{arm}_s{k}"]) / best())
        for name, (x, y) in RATIOS.items():
            if name == "seed_floor":
                if "L3_s0" in fl and "L3_s1" in fl:
                    cell["ratios"][name] = ratio(lambda ix: np.median(fl["L3_s0"] if ix is None else fl["L3_s0"][ix]),
                                                 lambda ix: np.median(fl["L3_s1"] if ix is None else fl["L3_s1"][ix]))
            elif all(f"{z}_s{k}" in fl for z in (x, y) for k in (0, 1)):
                cell["ratios"][name] = ratio(lambda ix, x=x: armstat(x, ix), lambda ix, y=y: armstat(y, ix))
        summary["cells"][f"{fam}|{n}"] = cell
    # verdicts per arm
    verdict = {}
    for arm in ARMS:
        c = summary["cells"].get(f"rand|{PRIMARY[arm]}")
        if not c or arm not in c["R"]:
            continue
        r = c["R"][arm]
        seeds_ok = all(c["R_seed"][f"{arm}_s{k}"] <= 0.8 for k in (0, 1))
        flips_win = r["point"] <= 0.8 and r["hi"] < 0.9 and seeds_ok
        bname = c["best_rule"]
        barm = f"{bname}@cell" if f"{bname}@cell" in c["arms"] else f"{bname}@train"
        cpu_arm = math.exp(np.mean([math.log(c["arms"][f"{arm}_s{k}"]["median_cpu"]) for k in (0, 1)]))
        work_arm = math.exp(np.mean([math.log(c["arms"][f"{arm}_s{k}"]["median_work"]) for k in (0, 1)]))
        cost_win = cpu_arm < c["arms"][barm]["median_cpu"] and work_arm < c["arms"][barm]["median_work"]
        if flips_win and cost_win:
            v = "real win"
        elif flips_win:
            v = "mechanism win"
        elif r["lo"] > 0.9:
            v = "clean loss"
        else:
            v = "inconclusive"
        t = summary["cells"].get(f"rand|{TRANSFER[arm]}", {}).get("R", {}).get(arm)
        verdict[arm] = {"primary": PRIMARY[arm], "R": r, "R_seeds": [c["R_seed"][f"{arm}_s{k}"] for k in (0, 1)],
                        "verdict": v, "median_cpu_arm": cpu_arm, "median_cpu_best": c["arms"][barm]["median_cpu"],
                        "transfer": TRANSFER[arm], "R_transfer": t}
    summary["verdicts"] = verdict
    # slopes of log median flips over rand 800..51200
    sl = {}
    names = sorted({a for (f, n), arms in cells.items() if f == "rand" for a in arms})
    for arm in names:
        pts = [(n, summary["cells"][f"rand|{n}"]["arms"].get(arm, {}).get("median_flips"))
               for n in (800, 3200, 12800, 51200) if f"rand|{n}" in summary["cells"]]
        pts = [(n, m) for n, m in pts if m]
        if len(pts) >= 3:
            sl[arm] = {"slope": float(np.polyfit(np.log([p[0] for p in pts]), np.log([p[1] for p in pts]), 1)[0]),
                       "points": pts}
    summary["slopes_rand"] = sl
    Path(a.out).write_text(json.dumps(summary, indent=1, default=float))
    for k, c in summary["cells"].items():
        print(f"== {k} ({c['instances']} instances; best rule {c.get('best_rule')})")
        for arm, r in sorted(c["arms"].items(), key=lambda kv: (kv[1]["median_flips"] is None, kv[1]["median_flips"] or 0)):
            mf = r["median_flips"]
            print(f"  {arm:20s} solved {r['solved']:.2f} median {'censored' if mf is None else round(mf):>11} "
                  f"cpu {r['median_cpu']:.4f}s {r['cpu_per_flip_ns']:.0f} ns/flip")
        for arm, q in c["R"].items():
            print(f"  R {arm}: {q['point']:.3f} [{q['lo']:.3f}, {q['hi']:.3f}] seeds "
                  f"{c['R_seed'][arm + '_s0']:.3f} {c['R_seed'][arm + '_s1']:.3f}")
        for name, q in c["ratios"].items():
            print(f"  {name}: {q['point']:.3f} [{q['lo']:.3f}, {q['hi']:.3f}]")
    print("verdicts:", json.dumps({k: (v["verdict"], round(v["R"]["point"], 3)) for k, v in verdict.items()}))
    print("slopes:", {k: round(v["slope"], 3) for k, v in sl.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("gates")
    p.add_argument("--training", required=True)
    p.add_argument("--novelty-val", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("summary")
    p.add_argument("--where", required=True)
    p.add_argument("--runs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args()
    {"gates": cmd_gates, "summary": cmd_summary}[a.cmd](a)
