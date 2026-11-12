#!/usr/bin/env python3
"""Referee RANDOM-FATES-R1: the census's numbers recomputed from runs.jsonl with the referee's own aggregation (no import of
census.py or fates.py), with spreads beside the medians.

    python3 -B ref_summary.py      (writes result_summary.json)"""
import collections
import itertools
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A = ROOT / "artifacts/RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census"


def q(xs, p):
    return float(np.quantile(xs, p)) if len(xs) else None


def spread(xs):
    xs = list(xs)
    if not xs:
        return None
    return {"n": len(xs), "median": q(xs, 0.5), "q25": q(xs, 0.25), "q75": q(xs, 0.75), "min": min(xs), "max": max(xs)}


def share(xs):
    xs = list(xs)
    return sum(1 for x in xs if x) / len(xs) if xs else None


def rank(x):
    """average ranks (ties share their mean rank)"""
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=float)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return r


def spearman(x, y):
    rx, ry = rank(x), rank(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def main():
    recs = [json.loads(l) for l in open(A / "runs.jsonl")]
    by = collections.defaultdict(list)
    for r in recs:
        by[r["label"]].append(r)
    out = {"records": len(recs)}

    # expected specs (the pre-registration's roster)
    exp = [(f"U{n}", r) for n, k in ((50, 200), (100, 200), (200, 200), (300, 60)) for r in range(k)]
    labs = [f"X{q}" for q in (0.1, 0.2, 0.3, 0.35, 0.5)] + [f"Og{q}" for q in (0.0, 0.05, 0.1, 0.2, 0.3)] + \
           [f"Ol{q}" for q in (0.05, 0.1, 0.2, 0.3)] + [f"L{w}_{q}" for w in (4, 5, 6) for q in (0.3, 0.5, 0.7)]
    exp += [(l, r) for l in labs for r in range(100)] + [("T", r) for r in range(30)]
    have = collections.Counter((r["label"], r["run"]) for r in recs)
    out["roster"] = {"expected": len(exp), "missing": sorted(set(exp) - set(have)), "extra": sorted(set(have) - set(exp)),
                     "duplicated": sorted(k for k, c in have.items() if c > 1)}

    # (1) outcomes
    o = {}
    for l in labs:
        rs = by[l]
        alive = [not r["dead"] for r in rs]
        o[l] = {"runs": len(rs), "alive share": share(alive)}
    for n in (50, 100, 200, 300):
        o[f"U{n}"] = {"runs": len(by[f"U{n}"]), "all dead": all(r["dead"] for r in by[f"U{n}"]),
                      "density": spread(r["density"] for r in by[f"U{n}"])}
    out["outcomes"] = o

    def lf(x):
        return x["largest_class"] / max(1, x["n_used"])

    def reads(lab, key):
        return [r["reads"][key] for r in sorted(by[lab], key=lambda r: r["run"]) if "reads" in r and key in r["reads"]
                and r["reads"][key].get("state")]

    def prof(rr, d):
        sizes = [s for x in rr for (_, _, s, _) in x.get("bond_profile", {}).get(str(d), [])]
        kinds = collections.Counter(k for x in rr for (_, _, _, k) in x.get("bond_profile", {}).get(str(d), []))
        if not sizes:
            return None
        return {"pairs": len(sizes), "d+2": share(s == d + 2 for s in sizes), "below d+2": share(s is not None and s < d + 2 for s in sizes),
                "none found": share(s is None for s in sizes), "sizes": dict(collections.Counter(str(s) for s in sizes)),
                "kinds": dict(kinds)}

    # (2) P1
    p1 = {}
    for n in (100, 200, 300):
        for f in ("f0.5", "f0.75"):
            rr = reads(f"U{n}", f)
            p1[f"U{n} {f}"] = {"bases": len(rr), "tie-free share": share(x["tied_pairs"] == 0 for x in rr),
                               "distinctions used": spread(x["n_used"] for x in rr),
                               **{f"d={d}": prof(rr, d) for d in (1, 2, 3)}}
    for f in ("f0.5", "f0.75", "f0.9"):
        rr = reads("U50", f)
        p1[f"U50 {f}"] = {"bases": len(rr), "tie-free share": share(x["tied_pairs"] == 0 for x in rr),
                          **{f"d={d}": prof(rr, d) for d in (1, 2, 3)}}
    out["P1"] = p1

    # (3) P2, P3
    p2 = {}
    for n in (50, 100, 200, 300):
        row = {}
        for k in (50, 20, 10, 5, 3, 2, 1):
            rr = reads(f"U{n}", f"k{k}")
            row[f"k{k}"] = {"largest class share": spread(lf(x) for x in rr), "tie reach": spread(x["tie_reach"] for x in rr)}
            if k in (1, 10, 50):
                row[f"k{k}"]["d=3"] = prof(rr, 3)
        row["k50 share <= 0.05"] = share(lf(x) <= 0.05 for x in reads(f"U{n}", "k50"))
        cores = [r for r in by[f"U{n}"] if "core_knots" in r]
        row["core over death knot"] = spread(r["core_knots"] / r["death_knot"] for r in cores)
        p2[f"U{n}"] = row
    # trend of the share at fixed k against n, run by run (Spearman over all runs of the four sizes)
    trend = {}
    for k in (20, 10, 5, 3, 2, 1):
        xs, ys = [], []
        for n in (50, 100, 200, 300):
            for x in reads(f"U{n}", f"k{k}"):
                xs.append(n)
                ys.append(lf(x))
        trend[f"k{k}"] = {"spearman(n, share)": spearman(xs, ys)}
    p2["trend"] = trend
    # bootstrap ratio of medians n = 300 against n = 100 at k = 1, 5, 10, 20
    rng = np.random.default_rng(1)
    boot = {}
    for k in (1, 5, 10, 20):
        a = np.array([lf(x) for x in reads("U100", f"k{k}")])
        b = np.array([lf(x) for x in reads("U300", f"k{k}")])
        rat = []
        for _ in range(4000):
            ma = np.median(rng.choice(a, len(a)))
            mb = np.median(rng.choice(b, len(b)))
            if ma > 0:
                rat.append(mb / ma)
        boot[f"k{k}"] = {"median ratio": float(np.median(b) / np.median(a)), "95% interval": [q(rat, 0.025), q(rat, 0.975)]}
    p2["ratio U300 / U100 (bootstrap)"] = boot
    # knots before the end at which the largest class first passes a share (run by run, from the read points)
    out["P2 P3"] = p2

    # (4) P5c and the X / O last stretch
    xo = {}
    for l in labs:
        if not l.startswith(("X", "Og", "Ol")):
            continue
        row = {}
        for k in (50, 20, 10, 5, 1):
            rr = reads(l, f"k{k}")
            if rr:
                row[f"k{k}"] = spread(lf(x) for x in rr)
        dead = [r for r in by[l] if r["dead"] and "core_knots" in r]
        if dead:
            row["cores"] = {"knots": spread(r["core_knots"] for r in dead), "distinctions": spread(r["core_distinctions"] for r in dead)}
        if row:
            xo[l] = row
    last = [r["reads"]["k1"] for l in labs if l.startswith(("X", "Og", "Ol")) for r in by[l]
            if r["dead"] and "reads" in r and "k1" in r["reads"] and r["reads"]["k1"].get("state")]
    xo["last bases"] = len(last)
    xo["share with largest class >= 0.1"] = share(lf(x) >= 0.1 for x in last)
    out["P5c"] = xo

    # (5) P5a, P5b
    Ld = [r for l in labs if l.startswith(("L5", "L6")) for r in by[l] if r["dead"]]
    p5 = {"endings": len(Ld), "core knots": spread(r["core_knots"] for r in Ld),
          "core index span": spread(r["core_index_span"] for r in Ld),
          "core distinctions": spread(r["core_distinctions"] for r in Ld),
          "share <= 20 knots within span 20": share(r["core_knots"] <= 20 and r["core_index_span"] <= 20 for r in Ld),
          "core knots range": [min(r["core_knots"] for r in Ld), max(r["core_knots"] for r in Ld)],
          "core span+1 range": [min(r["core_index_span"] + 1 for r in Ld), max(r["core_index_span"] + 1 for r in Ld)]}
    Lr = [r for r in Ld if "reads" in r and "k1" in r["reads"] and r["reads"]["k1"].get("state")]
    big = [r["reads"]["k1"]["largest_class"] for r in Lr]
    age = [r["n_at_death"] for r in Lr]
    p5["last bases"] = len(Lr)
    p5["largest class <= 40"] = share(b <= 40 for b in big)
    p5["largest class max"] = max(big)
    p5["spearman (tie-averaged)"] = spearman(age, big)
    old = [(a, b) for a, b in zip(age, big) if a > 20]
    p5["spearman without endings on <= 20 distinctions"] = spearman([a for a, _ in old], [b for _, b in old]) if len(old) > 2 else None
    p5["endings on <= 20 distinctions"] = len(Lr) - len(old)
    p5["largest class share, endings on <= 20"] = spread(b / a for a, b in zip(age, big) if a <= 20)
    out["P5ab"] = p5

    # (6) P6
    p6 = {}
    for l in ("X0.1", "X0.2", "Og0.0", "Og0.05", "Og0.1"):
        rr = reads(l, "end")
        balls = [bb for x in rr for bb in x["step_balls"]]
        p6[l] = {"bases": len(rr), "distinctions used": spread(x["n_used"] for x in rr),
                 **{f"d={d}": prof(rr, d) for d in (1, 2, 3)},
                 "B3/B1 median": q([bb[2] / bb[0] for bb in balls if bb[0]], 0.5),
                 "tie-free share": share(x["tied_pairs"] == 0 for x in rr),
                 "pairs in two or more knots / co-knotted pairs": spread(x["pairs_in_two_or_more"] / x["co_knotted_pairs"] for x in rr),
                 "most knots on a pair": spread(x["max_knots_on_pair"] for x in rr)}
    out["P6"] = p6

    # (7) P7
    p7 = {}
    for l in ("L4_0.5", "L4_0.7"):
        rr = reads(l, "end")
        sizes = [(d, s) for x in rr for d in (2, 3) for (_, _, s, _) in x["bond_profile"][str(d)]]
        p7[l] = {"bases": len(rr), "distinctions used": spread(x["n_used"] for x in rr),
                 "shortcut share d=2,3": share(s is not None and s < d + 2 for d, s in sizes),
                 "d=2": prof(rr, 2), "d=3": prof(rr, 3),
                 "tie reach <= 8": share(x["tie_reach"] <= 8 for x in rr), "tie reach": spread(x["tie_reach"] for x in rr),
                 "B6 median": q([bb[5] for x in rr for bb in x["step_balls"]], 0.5),
                 "B1..B6 medians": [q([bb[i] for x in rr for bb in x["step_balls"]], 0.5) for i in range(6)]}
    out["P7"] = p7

    # controls
    t = reads("T", "end")
    out["C2"] = {"bases": len(t), "tie-free": share(x["tied_pairs"] == 0 for x in t), **{f"d={d}": prof(t, d) for d in (1, 2, 3)}}
    kt = [r["killer_tied_equal"] for r in recs if "killer_tied_equal" in r]
    out["C1"] = {"checked": len(kt), "all": all(kt)}
    (HERE / "result_summary.json").write_text(json.dumps(out, indent=1) + "\n")
    print("wrote result_summary.json")


if __name__ == "__main__":
    main()
