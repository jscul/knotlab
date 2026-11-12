#!/usr/bin/env python3
"""Referee MISSING-KNOTS-R1, with the referee's own code (no import of census.py, fates.py or bonddp.py):
  1. M1 to M4 recomputed from bases.jsonl (least squares with an intercept), with a bootstrap over bases (2,000 resamples) for each
     cell's slope and for M2r's ratio; the slope on the gap, and how closely M follows the gap within a cell (R^2 of M on the gap); the
     coefficient of variation across cells for the gap as well as for the five counts;
  2. the bases regenerated with the referee's generators (RANDOM-FATES-R1's gen_newest, the frozen draw order of proc_band; the band
     as the census defines it) from the census's seeds, the pairs from its pair seeds, and every pair's counts M, D, M3, M4, W2
     recomputed and compared with the record;
  3. the least bond L recomputed exactly by the referee's search (RANDOM-FATES-R1's Base.least_bond, sizes 2 to 5) for up to 40 pairs
     per cell whose recorded L is at most 5, and checked to be above 5 where the record says more (up to 40 per cell).

    python3 -B ref_missing.py      (writes result_missing.json)"""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "RANDOM-FATES-20261112-001" / "referee-R1"))
import ref_fates as RF  # noqa: E402

ART = ROOT / "artifacts" / "MISSING-KNOTS-20261112-001A" / "MISSING-KNOTS-20261112-001A-E001_missing_knot_count"
N = 800
GAPS = (16, 32, 64, 128, 256)
NQ = [f"N{q}" for q in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9)]
BP = [f"B{p}" for p in (0.5, 0.6, 0.7, 0.8, 0.9)]
BAND = [t for t in itertools.combinations(range(N), 3) if t[2] - t[0] <= 3]


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0:
        return None
    xm, ym = x.mean(), y.mean()
    return float(((x - xm) * (y - ym)).sum() / ((x - xm) ** 2).sum())


def rsq(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1] ** 2)


def summary(bases):
    rng = np.random.default_rng(7)
    by = {lab: [b for b in bases if b["label"] == lab] for lab in NQ + BP}
    out = {}
    for lab, bs in by.items():
        dfn = lambda bb: [p for b in bb for p in b["between"] if p["status"] == "ok"]
        d = dfn(bs)
        e = {"defined share": len(d) / sum(len(b["between"]) for b in bs)}
        for c in ("M", "D", "M3", "M4", "W2", "gap"):
            e["slope " + c] = ols([p[c] if c != "gap" else p["j"] - p["i"] for p in d], [p["L"] for p in d])
        e["R2 of M on the gap (defined pairs)"] = rsq([p["j"] - p["i"] for p in d], [p["M"] for p in d])
        boots = []
        for _ in range(2000):
            pick = [bs[k] for k in rng.integers(0, len(bs), len(bs))]
            dd = dfn(pick)
            boots.append(ols([p["M"] for p in dd], [p["L"] for p in dd]))
        boots = [b for b in boots if b is not None]
        e["slope M bootstrap 95%"] = [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]
        e["_boots"] = boots
        ws = [ols([p["M"] for p in b["within"] if p["status"] == "ok"], [p["L"] for p in b["within"] if p["status"] == "ok"])
              for b in bs if sum(p["status"] == "ok" for p in b["within"]) >= 6]
        ws = [w for w in ws if w is not None]
        e["within: bases with >= 6 defined stretches"] = len(ws)
        e["within median slope"] = float(np.median(ws)) if len(ws) >= 5 else None
        out[lab] = e
    r = np.array(out["B0.9"]["_boots"][:1990]) / np.array(out["B0.5"]["_boots"][:1990])
    res = {"cells": {k: {kk: vv for kk, vv in v.items() if kk != "_boots"} for k, v in out.items()},
           "M2r ratio": out["B0.9"]["slope M"] / out["B0.5"]["slope M"],
           "M2r ratio bootstrap 95% (independent resamples of the two cells)": [float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))],
           "M2r: share of resamples with ratio <= 0.8": float(np.mean(r <= 0.8))}
    allN = [p for b in bases if b["label"] in NQ for p in b["between"] if p["status"] == "ok"]
    res["M1 pooled R2 on M"] = rsq([p["M"] for p in allN], [p["L"] for p in allN])
    res["M1 pooled R2 on the gap"] = rsq([p["j"] - p["i"] for p in allN], [p["L"] for p in allN])
    cv = {}
    for c in ("M", "D", "M3", "M4", "W2", "gap"):
        sl = [out[l]["slope " + c] for l in NQ + BP if out[l]["slope " + c] is not None and out[l]["defined share"] >= 0.5]
        cv[c] = float(np.std(sl) / np.mean(sl))
    res["M4 coefficient of variation across cells (defined share >= 0.5)"] = cv
    return res


def make_base(label, rng):
    if label.startswith("B"):
        p = float(label[1:])
        return [t for t in BAND if rng.random() < p]
    g = RF.gen_newest(4, float(label[1:]), rng)
    K = []
    while True:
        t = next(g)
        if t is None:
            continue
        if max(t) >= N:
            return K
        K.append(t)


def counts(kset, i, j):
    M = W2 = 0
    for m in range(i + 3, j + 1):
        miss = sum(1 for t in itertools.combinations(range(m - 3, m + 1), 3) if t not in kset)
        M += miss
        W2 += miss >= 2
    D = [t for t in BAND if i <= t[0] and t[2] <= j and t not in kset]
    return {"M": M, "D": len(D), "M3": sum(1 for t in D if t[2] - t[0] == 2), "M4": sum(1 for t in D if t[2] - t[0] == 3), "W2": W2}


def regen(bases):
    out = {"bases": 0, "knot counts match": 0, "pairs": 0, "pair positions match": 0, "counts match": 0}
    lb = {}
    t0 = time.time()
    for rec in bases:
        lab, b = rec["label"], rec["base"]
        K = make_base(lab, random.Random(seed_of("MK", lab, b)))
        out["bases"] += 1
        out["knot counts match"] += len(K) == rec["knots"]
        kset = set(K)
        prng = random.Random(seed_of("MK", lab, b, "pairs"))
        pairs = []
        for g in GAPS:
            for _ in range(8):
                i = prng.randrange(40, 760 - g - 3)
                pairs.append((i, i + g + prng.randrange(4)))
        base = None
        for (i, j), p in zip(pairs, rec["between"]):
            out["pairs"] += 1
            if (i, j) != (p["i"], p["j"]):
                continue
            out["pair positions match"] += 1
            c = counts(kset, i, j)
            out["counts match"] += all(c[k] == p[k] for k in c)
            cell = lb.setdefault(lab, {"checked <= 5": 0, "agree": 0, "checked > 5": 0, "agree > 5": 0, "disagreements": []})
            small = p["status"] == "ok" and p["L"] <= 5 and cell["checked <= 5"] < 40
            big = p["status"] == "ok" and p["L"] > 5 and cell["checked > 5"] < 40 and j - i <= 40
            if small or big:
                if base is None:
                    base = RF.Base(N, K, samples=200, seed=b)
                pool = [w for w in range(max(0, i - 8), min(N, j + 9))]
                mine = base.least_bond(i, j, pool, pool, max_size=5)
                if small:
                    cell["checked <= 5"] += 1
                    cell["agree"] += mine == p["L"]
                    if mine != p["L"] and len(cell["disagreements"]) < 5:
                        cell["disagreements"].append([lab, b, i, j, p["L"], mine])
                else:
                    cell["checked > 5"] += 1
                    cell["agree > 5"] += mine is None
                    if mine is not None and len(cell["disagreements"]) < 5:
                        cell["disagreements"].append([lab, b, i, j, p["L"], mine])
        if base is not None:
            base.close()
        print(lab, b, round(time.time() - t0), "s", flush=True)
    out["least bond spot checks"] = lb
    return out


def main():
    bases = [json.loads(l) for l in (ART / "bases.jsonl").read_text().splitlines()]
    res = {"summary": summary(bases)}
    (HERE / "result_missing.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res["summary"], indent=1)[:4000], flush=True)
    res["regeneration"] = regen(bases)
    (HERE / "result_missing.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res["regeneration"].items() if k != "least bond spot checks"}, indent=1))


if __name__ == "__main__":
    main()
