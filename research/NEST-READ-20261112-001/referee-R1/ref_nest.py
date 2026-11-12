#!/usr/bin/env python3
"""Referee NEST-READ-R1 (lean, records only; the referee's own summary code): P2, P3 and P4 recomputed from runs_*.jsonl; P3's
concentration over families (share of shortcut pairs from the top families, and the difference with them left out); P3 within
untied and tied constraining families; the uniform pairs not found, by steps apart, and how many nested pairs P4 loses to them.

    python3 -B ref_nest.py      (writes result_nest.json; trimmed() adds the symmetric trim, run after main)"""
import glob
import json
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "artifacts" / "NEST-READ-20261112-001A" / "NEST-READ-20261112-001A-E001_levels"


def load():
    fams = []
    for f in sorted(glob.glob(str(ART / "runs_*.jsonl"))):
        variant = Path(f).name.split("_")[1]
        for l in open(f):
            r = json.loads(l)
            if r["kind"] == "family":
                r["variant"] = variant
                fams.append(r)
    return fams


reach = lambda p: p["d"] is not None
short = lambda p: p["L"] is not None and 3 <= p["L"] < p["d"] + 2
bonded_tf = lambda p: p["L"] is not None and p["L"] >= 3


def share(fams, pred, val):
    v = [val(p) for x in fams for p in x["pairs"] if pred(p)]
    return (float(np.mean(v)) if v else None), len(v)


def boot_diff(A, B, pred, val, reps=2000, seed=3):
    rng = np.random.default_rng(seed)
    def s(F):
        v = [val(p) for x in F for p in x["pairs"] if pred(p)]
        return np.mean(v)
    point = s(A) - s(B)
    bs = [s([A[i] for i in rng.integers(0, len(A), len(A))]) - s([B[i] for i in rng.integers(0, len(B), len(B))]) for _ in range(reps)]
    return [round(float(point), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]


def slope_mean(fams, excess, reps=2000, seed=7):
    sl = []
    for x in fams:
        ps = [(p, b) for p, b in zip(x["pairs"], x["base"]) if reach(p) and (b.get("found") or not excess)]
        if len({p["s"] for p, _ in ps}) < 3:
            continue
        s = np.array([p["s"] for p, _ in ps], float)
        y = np.array([bonded_tf(p) - (bonded_tf(b) if excess else 0) for p, b in ps], float)
        sl.append(np.polyfit(s, y, 1)[0])
    sl = np.array(sl)
    rng = np.random.default_rng(seed)
    bs = [sl[rng.integers(0, len(sl), len(sl))].mean() for _ in range(reps)]
    return [round(float(sl.mean()), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4), len(sl)]


def main():
    fams = load()
    out = {"families": len(fams), "by stratum": dict(Counter((x["variant"], x["stratum"], x["tied"]) for x in fams).items().__iter__()) and
           {f"{v} {s} tied={t}": c for (v, s, t), c in Counter((x["variant"], x["stratum"], x["tied"]) for x in fams).items()}}
    acyc = [x for x in fams if x["acyclic"]]
    out["code control: acyclic pairs with L != d + 2 (L <= 5 or both beyond)"] = sum(
        1 for x in acyc for p in x["pairs"] if reach(p) and not ((p["L"] == p["d"] + 2) or (p["L"] is None and p["d"] + 2 > 5)))
    mon_c = [x for x in fams if x["stratum"] == "monotone" and not x["acyclic"]]
    con = [x for x in fams if x["stratum"] == "constraining"]
    out["P2 near (d <= 3) bonded, far (d >= 4) bonded"] = [share(mon_c, lambda p: reach(p) and p["d"] <= 3, lambda p: p["L"] is not None),
                                                           share(mon_c, lambda p: reach(p) and p["d"] >= 4, lambda p: p["L"] is not None)]
    out["P3 shortcut shares (constraining, monotone cyclic)"] = [share(con, reach, short), share(mon_c, reach, short)]
    out["P3 difference [boot]"] = boot_diff(con, mon_c, reach, short)
    out["P3 untied constraining minus monotone cyclic"] = boot_diff([x for x in con if not x["tied"]], mon_c, reach, short)
    out["P3 tied constraining minus monotone cyclic"] = boot_diff([x for x in con if x["tied"]], mon_c, reach, short)
    # concentration: shortcut pairs per family
    per = sorted(((sum(short(p) for p in x["pairs"] if reach(p)), sum(reach(p) for p in x["pairs"]), i) for i, x in enumerate(con)), reverse=True)
    tot = sum(a for a, _, _ in per)
    k10 = max(1, len(per) // 10)
    out["P3: constraining families with any shortcut"] = [sum(1 for a, _, _ in per if a), len(per)]
    out["P3: share of shortcut pairs from the top 10% of constraining families"] = round(sum(a for a, _, _ in per[:k10]) / tot, 3)
    drop = {i for _, _, i in per[:k10]}
    out["P3 difference without the top 10% of constraining families"] = boot_diff([x for i, x in enumerate(con) if i not in drop], mon_c, reach, short)
    for v in ("knot", "direct"):
        out[f"P3 difference, {v} variant"] = boot_diff([x for x in con if x["variant"] == v], [x for x in mon_c if x["variant"] == v], reach, short)
    out["P4 excess slope [mean, ci, families]"] = slope_mean(con, True)
    out["raw slope (constraining)"] = slope_mean(con, False)
    nf = Counter()
    for x in fams:
        for p, b in zip(x["pairs"], x["base"]):
            if reach(p):
                nf[(min(p["d"], 7), b.get("found", False))] += 1
    out["uniform pair found, by steps apart (d capped at 7): [found, not found]"] = {d: [nf[(d, True)], nf[(d, False)]] for d in range(1, 8)}
    out["constraining reachable pairs lost to P4 (no uniform pair)"] = [sum(1 for x in con for p, b in zip(x["pairs"], x["base"]) if reach(p) and not b.get("found")),
                                                                         sum(1 for x in con for p in x["pairs"] if reach(p))]
    (HERE / "result_nest.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()


def trimmed():
    """P3 with the top 10% of families by shortcut share removed from both strata (a symmetric trim), and each stratum's share of
    shortcut pairs from its own top 10%."""
    fams = load()
    mon_c = [x for x in fams if x["stratum"] == "monotone" and not x["acyclic"]]
    con = [x for x in fams if x["stratum"] == "constraining"]

    def trim(F):
        sc = [(np.mean([short(p) for p in x["pairs"] if reach(p)]) if any(reach(p) for p in x["pairs"]) else 0, i) for i, x in enumerate(F)]
        sc.sort(reverse=True)
        drop = {i for _, i in sc[:max(1, len(F) // 10)]}
        return [x for i, x in enumerate(F) if i not in drop]

    def top_share(F):
        per = sorted((sum(short(p) for p in x["pairs"] if reach(p)) for x in F), reverse=True)
        return round(sum(per[:max(1, len(F) // 10)]) / max(1, sum(per)), 3)
    return {"top-10% share of shortcut pairs (constraining, monotone cyclic)": [top_share(con), top_share(mon_c)],
            "P3 difference, both strata trimmed of their top 10% by shortcut share": boot_diff(trim(con), trim(mon_c), reach, short),
            "families with any shortcut (constraining, monotone cyclic)": [[sum(any(short(p) for p in x["pairs"] if reach(p)) for x in F), len(F)] for F in (con, mon_c)]}

