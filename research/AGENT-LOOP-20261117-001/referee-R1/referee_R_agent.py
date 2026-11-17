"""Referee recomputation for AGENT-LOOP-20261117-001 (own code; reads the study's raw results only).

  .venv/bin/python -B referee_R_agent.py > referee_R_agent.json

Statistic as frozen: per instance the geometric mean of five runs (flips, charged work, CPU); per cell and arm the median over
instances; a ratio of cell medians with a 99% paired bootstrap over instances (10,000 resamples). R against the better of NOV and
NOV8, re-chosen per resample. Capped rule: a ratio is a bound when either arm (for R: the arm, or both NOV and NOV8) has more
than 10% capped runs. Tests per Dr seed; a cell holds a test when both seeds pass; a family when the first cell holds and at
least one second cell holds. Room: the median over the restarted arm's runs of the share of flips after the first rebuild.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "artifacts/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop"
B = 10_000
RNG = np.random.default_rng(777)
FAM = {"local": ("local-w30-3200", ("local-w10-3200", "local-w20-3200")), "block": ("block-w40-3200", ("block-w20-3200",))}
SPEC = {"M1": {"flips": ("DrCf{s}", "DrRf{s}"), "work": ("DrC{s}", "DrR{s}")},
        "M2": {"flips": ("DrCf{s}", "Dr{s}"), "work": ("DrC{s}", "Dr{s}")},
        "M3": {"flips": ("DrCf{s}", "GNf"), "work": ("DrC{s}", "GN")},
        "M4": {"flips": ("DrCf{s}", "Dr{s}", "GNf", "NOV"), "work": ("DrC{s}", "Dr{s}", "GN", "NOV")}}


def gmean(v):
    return float(np.exp(np.mean(np.log(np.maximum(np.asarray(v, float), 1e-9)))))


def load():
    d = defaultdict(lambda: defaultdict(dict))
    for line in open(ART / "test" / "results.jsonl"):
        r = json.loads(line)
        assert r["status"] == "ok"
        res = r["result"]
        i = int(r["case"].split("|")[-1])
        assert res["seed"] == 9_100_000 + i and len(res["runs"]) == 5
        d[res["cell"]][res["arm"]][i] = res["runs"]
    return d


def ratio(fig, names, idx, mins=None):
    v = [np.array([fig[a][i] for i in idx]) for a in names]
    sel = RNG.integers(0, len(idx), (B, len(idx)))
    if mins:  # R: names[0] over the smaller of the medians of mins
        dens = [np.array([fig[a][i] for i in idx]) for a in mins]
        pt = np.median(v[0]) / min(np.median(x) for x in dens)
        bs = np.median(v[0][sel], axis=1) / np.min(np.stack([np.median(x[sel], axis=1) for x in dens]), axis=0)
    else:
        pt = np.median(v[0]) / np.median(v[1])
        bs = np.median(v[0][sel], axis=1) / np.median(v[1][sel], axis=1)
        if len(v) == 4:
            pt /= np.median(v[2]) / np.median(v[3])
            bs = bs / (np.median(v[2][sel], axis=1) / np.median(v[3][sel], axis=1))
    lo, hi = np.quantile(bs, [0.005, 0.995])
    return [round(float(pt), 4), round(float(lo), 4), round(float(hi), 4)]


def ok(t, test, kind):
    if kind == "hurts":
        return t[0] >= 1.11 and t[1] > 1
    thr = 0.8 if test == "M2" else 0.9
    return t[0] <= thr and t[2] < thr + 0.1


def main():
    d = load()
    out = {"cells": {}, "checks": {}}
    total = solved = good = 0
    for cell, arms in d.items():
        idx = sorted(set.intersection(*[set(v) for v in arms.values()]))
        assert len(idx) == 50
        fig = {m: {a: {i: gmean([x[m] for x in v[i]]) for i in idx} for a, v in arms.items()} for m in ("flips", "work", "cpu")}
        capped = {a: float(np.mean([not x["solved"] for i in idx for x in v[i]])) for a, v in arms.items()}
        for a, v in arms.items():
            for i in idx:
                for x in v[i]:
                    total += 1
                    if x["solved"]:
                        solved += 1
                        good += x.get("verified") is True
        c = {"capped": {a: round(p, 4) for a, p in capped.items() if p > 0}, "room": {}, "R": {}, "tests": {},
             "per_rebuild": {}}
        for a, v in arms.items():
            runs = [x for i in idx for x in v[i]]
            if a.startswith(("DrC", "DrR")):
                c["room"][a] = round(float(np.median([(x["flips"] - x["flips_first"]) / x["flips"]
                                                      if x.get("flips_first") is not None and x["flips"] else 0.0
                                                      for x in runs])), 3)
                c["per_rebuild"][a] = {"rebuilds_median": float(np.median([x["rebuilds"] for x in runs])),
                                       "flips_after_first_per_rebuild": round(float(np.median(
                                           [(x["flips"] - x["flips_first"]) / max(1, x["rebuilds"]) for x in runs
                                            if x.get("flips_first") is not None] or [0])), 1),
                                       "flips_after_first_median": round(float(np.median(
                                           [x["flips"] - x["flips_first"] if x.get("flips_first") is not None else 0
                                            for x in runs])), 1)}
            if a not in ("NOV", "NOV8", "SL"):
                bound = capped[a] > 0.1 or min(capped["NOV"], capped["NOV8"]) > 0.1
                c["R"][a] = {m: ratio(fig[m], [a], idx, mins=["NOV", "NOV8"]) + (["bound"] if bound else [])
                             for m in ("flips", "work", "cpu")}
        for test, ms in SPEC.items():
            for m, spec in ms.items():
                seeds = {}
                for s in "01":
                    names = [x.format(s=s) for x in spec]
                    seeds[s] = {"ratio": ratio(fig[m], names, idx), "bound": any(capped[x] > 0.1 for x in names)}
                e = {"seeds": seeds}
                kinds = ("helps", "hurts") if test == "M1" else ("helps",)
                if test == "M1":
                    rr = "DrRf" if m == "flips" else "DrR"
                    e["room"] = all(c["room"][f"{rr}{s}"] >= 0.5 for s in "01")
                for k in kinds:
                    if any(p["bound"] for p in seeds.values()):
                        e[k] = "bound"
                    elif test == "M1" and not e["room"]:
                        e[k] = "no room"
                    else:
                        n_ok = sum(ok(p["ratio"], test, k) for p in seeds.values())
                        e[k] = "holds" if n_ok == 2 else "seeds disagree" if n_ok == 1 else "fails"
                c["tests"][f"{test} {m}"] = e
        # context: the other budget for M1, M3; co-flip targets
        c["context"] = {f"M1 {m} other budget s{s}": ratio(fig[m], [f"DrC{s}" if m == "flips" else f"DrCf{s}",
                                                                   f"DrR{s}" if m == "flips" else f"DrRf{s}"], idx)
                        for m in ("flips", "work") for s in "01"}
        c["context"]["GNco/GN"] = {m: ratio(fig[m], ["GNco", "GN"], idx) for m in ("flips", "work")}
        c["context"]["GNf/GN"] = {m: ratio(fig[m], ["GNf", "GN"], idx) for m in ("flips", "work")}
        c["context"]["Dr/F flips"] = {s: ratio(fig["flips"], [f"Dr{s}"], idx, mins=["NOV", "NOV8"]) for s in "01"}
        c["context"]["GN slow work median"] = float(np.median([x["work_slow"] for i in idx for x in arms["GN"][i]]))
        c["context"]["DrC0 slow work median"] = float(np.median([x["work_slow"] for i in idx for x in arms["DrC0"][i]]))
        c["context"]["probes GN median"] = float(np.median([x["probes"] for i in idx for x in arms["GN"][i]]))
        sl = [x for i in idx for x in arms["SL"][i]]
        c["SL"] = {"solved": sum(x["solved"] for x in sl), "runs": len(sl),
                   "n_final_range": [int(min(x["n_final"] for x in sl)), int(max(x["n_final"] for x in sl))],
                   "n_final_median": float(np.median([x["n_final"] for x in sl])),
                   "work_median": float(np.median([x["work"] for x in sl]))}
        if cell == "rand-3200":
            same = sum(1 for s in "01" for b in ("", "f") for i in idx for x, y in
                       zip(arms[f"DrC{b}{s}"][i], arms[f"DrR{b}{s}"][i]) if x["flips"] == y["flips"] and x["work"] == y["work"])
            reb = sum(x["rebuilds"] for s in "01" for b in ("", "f") for i in idx for x in arms[f"DrC{b}{s}"][i])
            c["rand_identity"] = {"identical_runs": same, "of": 4 * 250, "rebuilds_total": reb}
        out["cells"][cell] = c
    out["checks"] = {"runs": total, "solved": solved, "solved_verified_true": good}

    def fam(f, key, k):
        first, rest = FAM[f]
        v1 = out["cells"][first]["tests"][key][k]
        reps = {r: out["cells"][r]["tests"][key][k] for r in rest}
        return {"first": v1, "rest": reps, "family": v1 if v1 != "holds" else
                ("holds" if "holds" in reps.values() else "not replicated")}
    out["family"] = {f: {f"{t} {m}" + (f" {k}" if t == "M1" else ""): fam(f, f"{t} {m}", k)
                         for t in SPEC for m in ("flips", "work") for k in (("helps", "hurts") if t == "M1" else ("helps",))}
                     for f in FAM}
    mem, loop = {}, {}
    for f in FAM:
        for m in ("flips", "work"):
            h = out["family"][f][f"M1 {m} helps"]["family"]
            u = out["family"][f][f"M1 {m} hurts"]["family"]
            mem[f"{f} {m}"] = h if h in ("no room", "bound") else ("carry helps" if h == "holds" else
                                                                   "carry hurts" if u == "holds" else "no difference shown")
        p2 = {m for m in ("flips", "work") if out["family"][f][f"M2 {m}"]["family"] == "holds"}
        p3 = {m for m in ("flips", "work") if out["family"][f][f"M3 {m}"]["family"] == "holds"}
        loop[f] = (1 if "work" in p2 & p3 else 2 if "flips" in p2 & p3 else 3 if p2 and p3 else 4 if p2 else 5 if p3 else 6,
                   sorted(p2), sorted(p3))
    out["memory"], out["loop"] = mem, loop
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
