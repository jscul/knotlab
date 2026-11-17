"""Analysis of WHERE-NEXT-20261116-001A.

  analyze.py retune   --runs DIR --out retuned.json [--stress-from summary.json]
  analyze.py policies --training DIR --out policies.json
  analyze.py test     --runs DIR [--runs DIR ...] --policies policies.json --out summary.json [--cadical DIR]

The test summary follows the frozen pre-registration: medians (only where at most half the runs are censored), solved
fractions, R = L3 / best hand-written rule with a paired bootstrap that re-chooses the best rule in every resample (both
comparators), M = L3 / L2, W = L2w / L2 and L2 / L1, where-diagnostics, cost per instance and break-even N*.
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
LEARNED = ["L1", "L2w", "L2", "L3"]
B = 10_000


def ok_results(path):
    out = []
    for rec in load_results(str(path)).values():
        if rec["status"] == "ok":
            out.append(rec["result"])
    return out


def cmd_retune(a):
    by = defaultdict(list)
    for r in ok_results(a.runs):
        by[(r["fam"], r["n"], r["arm"], r["algo"], tuple(r["params"]))].append(r["score"])
    cells = defaultdict(dict)
    detail = defaultdict(dict)
    for (fam, n, rule, algo, prm), sc in by.items():
        key = f"{fam}|{n}"
        m = float(np.mean(sc))
        detail[key].setdefault(rule, []).append({"algo": algo, "params": list(prm), "mean_score": m, "runs": len(sc)})
        if rule not in cells[key] or m < cells[key][rule][2]:
            cells[key][rule] = [algo, list(prm), m]
    out = {"cells": {k: {r: v[:2] for r, v in d.items()} for k, d in cells.items()},
           "scores": {k: {r: v[2] for r, v in d.items()} for k, d in cells.items()}, "detail": detail}
    if a.previous:
        prev = json.loads(Path(a.previous).read_text())
        prev["cells"].update(out["cells"])
        prev["scores"].update(out["scores"])
        prev["detail"].update(out["detail"])
        out = prev
    if a.stress_rules:
        out["stress_rules"] = a.stress_rules.split(",")
    Path(a.out).write_text(json.dumps(out, indent=1))
    for k in sorted(out["cells"]):
        print(k, out["cells"][k])


def cmd_policies(a):
    root = Path(a.training) / "runs"
    best = {}
    for d in sorted(root.iterdir()):
        s = json.loads((d / "summary.json").read_text())
        arm = s["arm"]
        best.setdefault(arm, []).append((s["best_val_mean_log_flips"], d, s))
    out = {}
    for arm, rows in best.items():
        rows.sort(key=lambda r: r[0])
        v, d, s = rows[0]
        out[arm] = {"theta": str(d / "theta_best.npy"), "flags": s["flags"], "what_params": s["what_params"],
                    "seed": s["seed"], "val_mean_log_flips": v,
                    "seeds": {str(r[2]["seed"]): {"val_mean_log_flips": r[0], "best_tag": r[2]["best_tag"],
                                                  "cpu_total": r[2]["cpu_total"], "flips": r[2]["flips"],
                                                  "work": r[2]["work"]} for r in rows},
                    "training_cpu_total": sum(r[2]["cpu_total"] for r in rows),
                    "training_flips_total": sum(r[2]["flips"] for r in rows),
                    "training_work_total": sum(r[2]["work"] for r in rows)}
        print(arm, "seed", s["seed"], "val", round(v, 3), "both seeds", [round(r[0], 3) for r in rows],
              "training cpu", round(out[arm]["training_cpu_total"]), "s")
    Path(a.out).write_text(json.dumps(out, indent=1))


def med(x):
    return float(np.median(x)) if len(x) else float("nan")


def boot_ratio(num, dens, rng, idx_draws):
    """num: array per instance (inf = censored); dens: dict of arrays; returns ratios per resample."""
    out = np.empty(len(idx_draws))
    for b, idx in enumerate(idx_draws):
        mn = np.median(num[idx])
        md = min(np.median(d[idx]) for d in dens.values())
        out[b] = mn / md if md > 0 else float("nan")
    return out


def cmd_test(a):
    rows = []
    for d in a.runs:
        rows += ok_results(d)
    pol = json.loads(Path(a.policies).read_text())
    cells = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        cells[(r["fam"], r["n"])][r["arm"]][r["seed"]] = r
    rng = np.random.default_rng(20261116)
    summary = {"cells": {}}
    for (fam, n), arms in sorted(cells.items()):
        seeds = sorted(set.intersection(*[set(v) for v in arms.values()]))
        S = len(seeds)
        flips = {arm: np.array([v[s]["flips"] if v[s]["solved"] else math.inf for s in seeds], dtype=float)
                 for arm, v in arms.items()}
        cell = {"instances": S, "arms": {}}
        for arm, v in sorted(arms.items()):
            f = flips[arm]
            cpu = np.array([v[s]["cpu"] for s in seeds])
            work = np.array([v[s]["work"] for s in seeds], dtype=float)
            st = np.array([v[s]["flips"] for s in seeds], dtype=float)
            solved = float(np.isfinite(f).mean())
            row = {"solved": solved, "median_flips": med(f) if solved >= 0.5 else None,
                   "median_cpu": med(cpu), "median_work": med(work), "cpu_per_flip_ns": 1e9 * cpu.sum() / st.sum(),
                   "work_per_flip": work.sum() / st.sum(), "params": v[seeds[0]].get("params")}
            ws = sum(v[s]["where_steps"] for s in seeds)
            if ws:
                row["distinct_candidates_mean"] = sum(v[s]["distinct_sum"] for s in seeds) / ws
            na = sum(v[s]["new_avail"] for s in seeds)
            if na:
                row["took_just_violated_when_available"] = sum(v[s]["new_chosen"] for s in seeds) / na
            cell["arms"][arm] = row
        # comparators
        train_c = {r: flips[f"{r}@train"] for r in RULES if f"{r}@train" in flips}
        cell_c = {r: flips[f"{r}@cell"] if f"{r}@cell" in flips else flips[f"{r}@train"]
                  for r in RULES if f"{r}@train" in flips}
        idx = [rng.integers(0, S, S) for _ in range(B)]

        def ratio(num, dens, level):
            point = np.median(num) / min(np.median(d) for d in dens.values())
            bs = boot_ratio(num, dens, rng, idx)
            lo, hi = np.nanpercentile(bs, [(100 - level) / 2, 100 - (100 - level) / 2])
            best = min(dens, key=lambda r: np.median(dens[r]))
            return {"point": float(point), "lo": float(lo), "hi": float(hi), "level": level, "best_rule": best}

        level = 95.0 if (fam, n) == ("rand", 3200) else 98.3
        for arm in LEARNED:
            if arm in flips and train_c:
                cell.setdefault("R", {})[arm] = {"vs_retuned": ratio(flips[arm], cell_c, level),
                                                 "vs_training_tuned": ratio(flips[arm], train_c, level)}
        if "L3" in flips and "L2" in flips:
            cell["M"] = ratio(flips["L3"], {"L2": flips["L2"]}, level)
        if "L2w" in flips and "L2" in flips:
            cell["W_L2w_over_L2"] = ratio(flips["L2w"], {"L2": flips["L2"]}, level)
        if "L2" in flips and "L1" in flips:
            cell["W_L2_over_L1"] = ratio(flips["L2"], {"L1": flips["L1"]}, level)
        # marginal cost and break-even against the re-tuned best rule (by median CPU)
        if "L3" in arms and cell_c:
            best = cell["R"]["L3"]["vs_retuned"]["best_rule"]
            bname = f"{best}@cell" if f"{best}@cell" in arms else f"{best}@train"
            c_best, c_l3 = cell["arms"][bname]["median_cpu"], cell["arms"]["L3"]["median_cpu"]
            w_best, w_l3 = cell["arms"][bname]["median_work"], cell["arms"]["L3"]["median_work"]
            train_cpu = pol["L3"]["training_cpu_total"]
            cell["cost"] = {"best_rule_arm": bname, "median_cpu_best": c_best, "median_cpu_L3": c_l3,
                            "median_work_best": w_best, "median_work_L3": w_l3,
                            "training_cpu_L3": train_cpu,
                            "N_star": (train_cpu / (c_best - c_l3)) if c_l3 < c_best else math.inf}
        summary["cells"][f"{fam}|{n}"] = cell
    # scaling slopes on rand
    sl = {}
    for arm in sorted({a for (f, n), arms in cells.items() if f == "rand" for a in arms}):
        pts = [(n, summary["cells"][f"rand|{n}"]["arms"].get(arm, {}).get("median_flips"))
               for n in (800, 3200, 12800) if f"rand|{n}" in summary["cells"]]
        pts = [(n, m) for n, m in pts if m]
        if len(pts) >= 2:
            x, y = np.log([p[0] for p in pts]), np.log([p[1] for p in pts])
            sl[arm] = {"slope": float(np.polyfit(x, y, 1)[0]), "points": pts}
    summary["slopes_rand"] = sl
    if a.cadical:
        cad = defaultdict(list)
        for r in ok_results(a.cadical):
            cad[r["n"]].append(r)
        summary["cadical"] = {str(n): {"runs": len(v), "solved": sum(1 for r in v if r["result"] is True),
                                       "median_cpu": med([r["cpu"] if r["result"] is True else math.inf for r in v]),
                                       "median_conflicts": med([r["conflicts"] for r in v])}
                              for n, v in sorted(cad.items())}
    Path(a.out).write_text(json.dumps(summary, indent=1, default=float))
    for k, c in summary["cells"].items():
        print(f"== {k} ({c['instances']} instances)")
        for arm, r in sorted(c["arms"].items(), key=lambda kv: (kv[1]["median_flips"] is None, kv[1]["median_flips"] or 0)):
            extra = ""
            if "distinct_candidates_mean" in r:
                extra = f" distinct {r['distinct_candidates_mean']:.2f}"
            if "took_just_violated_when_available" in r:
                extra += f" took-new {r['took_just_violated_when_available']:.2f}"
            mf = r["median_flips"]
            print(f"  {arm:20s} solved {r['solved']:.2f} median {'censored' if mf is None else round(mf):>12} "
                  f"cpu {r['median_cpu']:.4f}s {r['cpu_per_flip_ns']:.0f} ns/flip work/flip {r['work_per_flip']:.0f}{extra}")
        for arm, rr in c.get("R", {}).items():
            q = rr["vs_retuned"]
            t = rr["vs_training_tuned"]
            print(f"  R {arm}: vs re-tuned {q['point']:.3f} [{q['lo']:.3f}, {q['hi']:.3f}] ({q['best_rule']}); "
                  f"vs training-tuned {t['point']:.3f} [{t['lo']:.3f}, {t['hi']:.3f}] ({t['best_rule']})")
        for key in ("M", "W_L2w_over_L2", "W_L2_over_L1"):
            if key in c:
                print(f"  {key}: {c[key]['point']:.3f} [{c[key]['lo']:.3f}, {c[key]['hi']:.3f}]")
        if "cost" in c:
            print("  cost:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c["cost"].items()})
    if sl:
        print("slopes:", {k: round(v["slope"], 3) for k, v in sl.items()})
    if "cadical" in summary:
        print("cadical:", summary["cadical"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("retune")
    p.add_argument("--runs", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--previous")
    p.add_argument("--stress-rules")
    p = sub.add_parser("policies")
    p.add_argument("--training", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("test")
    p.add_argument("--runs", nargs="+", required=True)
    p.add_argument("--policies", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--cadical")
    a = ap.parse_args()
    {"retune": cmd_retune, "policies": cmd_policies, "test": cmd_test}[a.cmd](a)
