"""Referee recomputation for SPEC-MERGE-20261117-001 (own code; reads the study's raw results only).

  python3 referee_R_spec.py > referee_R_spec.json

Test: per instance the geometric mean of five runs (work, CPU, flips), per cell the median, R against the better of NOV and
NOVt re-chosen in each of 10,000 paired resamples, 99% intervals. Also R against NOV alone, the evidence ratios, censoring,
verification, merges, precision, the undo table (split by check in referee_undo.py), and whether the arms that
never merged ran Novelty+'s own trajectory. Gate D: per checkpoint the mean over instances of (co-flip - random), 99%
bootstrap over instances. Policy: the frozen tuning score recomputed from policy/.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "artifacts/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge"
B = 10_000
RNG = np.random.default_rng(424242)
SPEC = ("A0", "AE", "A")                 # the frozen "speculative arms"
CONTROL = {"A": "Arand", "A0": "Arand0", "AE": "AErand", "Aloc": "Arandloc"}


def rows(path):
    out = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            if r["status"] != "ok":
                raise SystemExit(f"not ok: {r['case']}")
            out.append(r)
    return out


def gm(vals):
    return float(math.exp(sum(math.log(max(v, 1e-9)) for v in vals) / len(vals)))


def boot(num, dens):
    """median(num) / min over dens of median(den), paired over instances, den re-chosen per resample."""
    num = np.asarray(num)
    dens = [np.asarray(d) for d in dens]
    pt = np.median(num) / min(np.median(d) for d in dens)
    sel = RNG.integers(0, len(num), (B, len(num)))
    r = np.median(num[sel], axis=1) / np.min(np.stack([np.median(d[sel], axis=1) for d in dens]), axis=0)
    lo, hi = np.quantile(r, [0.005, 0.995])
    return [round(float(pt), 4), round(float(lo), 4), round(float(hi), 4)]


def verdict(rw, rc):
    if rw[0] <= 0.8 and rw[2] < 0.9:
        return "charged win" if rc[2] < 1 else "work win"
    if rw[1] > 1.1:
        return "loss"
    return "parity or inconclusive"


def test():
    data = defaultdict(lambda: defaultdict(dict))
    for part in ("test_fixed", "test_tuned"):
        for r in rows(ART / part / "results.jsonl"):
            res = r["result"]
            i = int(r["case"].split("|")[-1])
            assert res["seed"] == 8_900_000 + i
            data[res["cell"]][res["arm"]][i] = res["runs"]
    out = {"runs_total": 0, "solved_total": 0, "solved_not_verified_true": 0, "cells": {}}
    for cell, arms in data.items():
        idx = sorted(set.intersection(*[set(v) for v in arms.values()]))
        assert all(len(arms[a][i]) == 5 for a in arms for i in idx)
        fig = {k: {a: [gm([x[k] for x in arms[a][i]]) for i in idx] for a in arms} for k in ("work", "cpu", "flips")}
        c = {"instances": len(idx), "arms": {}, "ratios": {}}
        for a, v in arms.items():
            runs = [x for i in idx for x in v[i]]
            out["runs_total"] += len(runs)
            out["solved_total"] += sum(x["solved"] for x in runs)
            bad = sum(1 for x in runs if x["solved"] and x.get("verified") is not True)
            out["solved_not_verified_true"] += bad
            row = {"W_median": round(float(np.median(fig["work"][a])), 1),
                   "censored": round(sum(not x["solved"] for x in runs) / len(runs), 4), "solved_unverified": bad}
            if a not in ("NOV", "NOVt"):
                row["R_W"] = boot(fig["work"][a], [fig["work"]["NOV"], fig["work"]["NOVt"]])
                row["R_CPU"] = boot(fig["cpu"][a], [fig["cpu"]["NOV"], fig["cpu"]["NOVt"]])
                row["R_flips"] = boot(fig["flips"][a], [fig["flips"]["NOV"], fig["flips"]["NOVt"]])
                row["R_W_vs_NOV"] = boot(fig["work"][a], [fig["work"]["NOV"]])
                row["verdict"] = verdict(row["R_W"], row["R_CPU"])
            if "merges" in runs[0]:
                m = np.array([x["merges"] for x in runs])
                row["merges_median"] = float(np.median(m))
                row["runs_with_merges"] = round(float(np.mean(m > 0)), 4)
                pr = [x["precision_all"] for x in runs if "precision_all" in x]
                row["precision_median"] = round(float(np.median(pr)), 4) if pr else None
                # undo table: round consistent with the planted state (1/0) x kept (1/0)
                tab = defaultdict(int)
                for x in runs:
                    for cons, kept in x.get("round_log", []):
                        tab[f"{cons}{kept}"] += 1
                row["rounds_consistent_kept"] = dict(sorted(tab.items()))
                cu = sum(x["contra_undos"] for x in runs)
                su = sum(x["stall_undos"] for x in runs)
                row["contra_undos"], row["stall_undos"] = cu, su
                row["undos_equal_undone_rounds"] = cu + su == tab["00"] + tab["10"]
                # which check undid which round is not in the stored runs (a right round can contradict once a wrong
                # round has been kept): referee_undo.py reruns the arms to split it
                if a in ("A", "A0", "Aloc", "Arand", "Arand0", "Arandloc"):
                    # runs that never merged: is the trajectory Novelty+'s own (same flips as NOV from that state)?
                    same = tot = 0
                    for i in idx:
                        for r_, x in enumerate(v[i]):
                            if x["merges"] == 0 and x["solved"]:
                                tot += 1
                                same += x["flips"] == arms["NOV"][i][r_]["flips"]
                    row["no_merge_runs_same_flips_as_NOV"] = [same, tot]
            c["arms"][a] = row
        for num, den in list(CONTROL.items()) + [(s, "Gpr") for s in ("A", "A0", "AE", "Aloc")]:
            c["ratios"][f"{num}/{den}"] = {"W": boot(fig["work"][num], [fig["work"][den]]),
                                           "CPU": boot(fig["cpu"][num], [fig["cpu"][den]])}
        c["ratios"]["NOV/NOVt"] = {"W": boot(fig["work"]["NOV"], [fig["work"]["NOVt"]]),
                                   "flips": boot(fig["flips"]["NOV"], [fig["flips"]["NOVt"]])}
        n = {"rand-3200": 3200, "rand3-3200": 3200, "rand-12800": 12800, "local-w10-3200": 3200}[cell]
        c["NOV_median_flips_per_distinction"] = round(float(np.median(fig["flips"]["NOV"])) / n, 2)
        c["NOVt_median_flips_per_distinction"] = round(float(np.median(fig["flips"]["NOVt"])) / n, 2)
        out["cells"][cell] = c
    # frozen reading
    pr = out["cells"]["rand-3200"]["arms"]
    wins = {cell: [a for a in SPEC + ("Aloc",) if out["cells"][cell]["arms"][a]["verdict"] == "charged win"]
            for cell in out["cells"]}
    out["reading0_untested"] = all(pr[a]["merges_median"] == 0 for a in SPEC)
    out["speculative_charged_wins"] = wins
    out["reading"] = 5 if not any(wins.values()) else "see wins"
    return out


def gate():
    rs = [r["result"] for r in rows(ART / "gate" / "results.jsonl")]
    out = {}
    for cell in ("rand-3200", "local-w10-3200"):
        g = [r["gate"] for r in rs if r["cell"] == cell]
        cs = {"instances": len(g), "solved_before_16": sum("solved_at_epoch" in x for x in g)}
        for cp in ("4", "8", "16"):
            pts = [x["checkpoints"][cp] for x in g if cp in x["checkpoints"]
                   and x["checkpoints"][cp].get("coflip") and x["checkpoints"][cp].get("random")]
            d = np.array([p["coflip"]["agree_planted"] - p["random"]["agree_planted"] for p in pts])
            sel = RNG.integers(0, len(d), (B, len(d)))
            lo, hi = np.quantile(d[sel].mean(axis=1), [0.005, 0.995])
            row = {"n": len(pts), "coflip": round(float(np.mean([p["coflip"]["agree_planted"] for p in pts])), 4),
                   "random": round(float(np.mean([p["random"]["agree_planted"] for p in pts])), 4),
                   "diff": [round(float(d.mean()), 4), round(float(lo), 4), round(float(hi), 4)],
                   "state_agree_planted": round(float(np.mean([p["state_agree_planted"] for p in pts])), 4),
                   "candidates_median": float(np.median([p["candidates"] for p in pts]))}
            fd = [p for p in pts if "agree_found" in p["coflip"]]
            row["found"] = [round(float(np.mean([p["coflip"]["agree_found"] for p in fd])), 4),
                            round(float(np.mean([p["random"]["agree_found"] for p in fd])), 4), len(fd)]
            if "tied_share" in pts[0]["coflip"]:
                t = np.array([[p["coflip"]["tied_share"], p["random"]["tied_share"]] for p in pts])
                dt = t[:, 0] - t[:, 1]
                lo, hi = np.quantile(dt[sel].mean(axis=1), [0.005, 0.995])
                row["tied"] = [round(float(t[:, 0].mean()), 4), round(float(t[:, 1].mean()), 4)]
                row["tied_diff"] = [round(float(dt.mean()), 4), round(float(lo), 4), round(float(hi), 4)]
                row["tied_ratio"] = round(float(t[:, 0].mean() / t[:, 1].mean()), 3)
            cs[cp] = row
        out[cell] = cs
    r, l = out["rand-3200"], out["local-w10-3200"]
    out["D_rand"] = any(r[cp]["diff"][0] >= 0.10 and r[cp]["diff"][1] > 0 for cp in ("4", "8", "16"))
    out["D_local"] = any(l[cp]["tied"][0] >= 1.5 * l[cp]["tied"][1] and l[cp]["tied_diff"][1] > 0
                         for cp in ("4", "8", "16"))
    return out


def policy():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sm_job", ROOT / "experiments/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge/job.py")
    job = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(job)
    rs = [r["result"] for r in rows(ART / "policy" / "results.jsonl")]

    def sc(x):
        return math.log(x["work"]) + (0 if x["solved"] else math.log1p(max(0, x["minviol"])))
    base = {(r["cell"], r["seed"], j): sc(x) for r in rs if r["k"] < 0 for j, x in enumerate(r["runs"])}
    seeds = sorted({r["seed"] for r in rs})
    acc = defaultdict(list)
    merged = defaultdict(list)
    for r in rs:
        if r["k"] >= 0:
            for j, x in enumerate(r["runs"]):
                acc[(r["cell"], r["k"])].append(sc(x) - base[(r["cell"], r["seed"], j)])
                merged[(r["cell"], r["k"])].append(x["merges"] > 0)
    out = {"tuning_seeds": [seeds[0], seeds[-1], len(seeds)]}
    chosen = json.loads((ART / "policies.json").read_text())
    for arm, cell in (("A", "rand-3200"), ("Aloc", "local-w10-3200")):
        s = {k: sum(v) / len(v) for (c, k), v in acc.items() if c == cell}
        best = min(s.values())
        k = min(kk for kk, v in s.items() if v == best)
        out[arm] = {"k": k, "setting": job.GRID[k], "score": round(best, 4), "matches_policies_json": job.GRID[k] == chosen[arm],
                    "share_runs_merging": round(float(np.mean(merged[(cell, k)])), 3),
                    "settings_never_merging": [kk for kk in s if not any(merged[(cell, kk)])]}
    return out


if __name__ == "__main__":
    print(json.dumps({"gate": gate(), "policy": policy(), "test": test()}, indent=1))
