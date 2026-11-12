"""The frozen census of MISSING-KNOTS-20261112-001A-E001 (contract.json beside this file): is the law's count along patterns of
knots within four consecutive distinctions a count of missing knots, with a unit that does not depend on the process?

Libraries, imported by path with pinned hashes: RANDOM-FATES-20261112-001A-E001's fates.py (proc_band) and
RANDOM-FATES-20261112-001C-E001's bonddp.py (least_bond, exact; margin 8).
Bases (800 distinctions, 10 each; seeds sha256 "MK:label:base"): newest-four growth at q in {0, 0.1, 0.3, 0.5, 0.7, 0.9}
(grown until the move that would bring distinction 800), and the "Bernoulli band" at p in {0.5, 0.6, 0.7, 0.8, 0.9}: each of the
knots within four consecutive distinctions of 0..799 present independently with probability p.
Pairs: (between) per base, for each gap g in {16, 32, 64, 128, 256}, 8 pairs with i uniform in [40, 760 - g - 3], j = i + g + r,
r uniform in {0..3}; (within) per base, the non-overlapping intervals [40 + 64k, 40 + 64(k+1)] that fit below 760 (11 of them).
Counts per pair: M = knots missing from the windows {m-3..m}, m in [i+3, j], summed over windows (4 minus those present);
D = distinct missing knots with all three distinctions in [i, j]; M3 and M4 = missing knots of span 2 and span 3 (max - min)
among D; W2 = windows with at least two missing knots; gap = j - i.

Run from the repository root:
    .venv/bin/python -B experiments/MISSING-KNOTS-20261112-001A/MISSING-KNOTS-20261112-001A-E001_missing_knot_count/census.py [--workers 6]
    .venv/bin/python -B experiments/MISSING-KNOTS-20261112-001A/MISSING-KNOTS-20261112-001A-E001_missing_knot_count/census.py --summary
Output: artifacts/MISSING-KNOTS-20261112-001A/MISSING-KNOTS-20261112-001A-E001_missing_knot_count/{bases.jsonl, summary.json}.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001C", "RANDOM-FATES-20261112-001C-E001_newest_four_count"))
import bonddp as B  # noqa: E402
import fates as F  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "MISSING-KNOTS-20261112-001A", "MISSING-KNOTS-20261112-001A-E001_missing_knot_count")
N = 800
SETTINGS = [f"N{q}" for q in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9)] + [f"B{p}" for p in (0.5, 0.6, 0.7, 0.8, 0.9)]
BASES = 10
GAPS = (16, 32, 64, 128, 256)
PAIRS = 8


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


ALL = [t for t in itertools.combinations(range(N), 3) if t[2] - t[0] <= 3]


def make_base(label, rng):
    if label.startswith("B"):
        p = float(label[1:])
        return [t for t in ALL if rng.random() < p]
    gen = F.proc_band(4, float(label[1:]), rng)
    K = []
    while True:
        t = next(gen)
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
    D = [t for t in ALL if i <= t[0] and t[2] <= j and t not in kset]
    return {"M": M, "D": len(D), "M3": sum(1 for t in D if t[2] - t[0] == 2), "M4": sum(1 for t in D if t[2] - t[0] == 3), "W2": W2}


def base_task(spec):
    label, b = spec
    t0 = time.time()
    rng = random.Random(seed_of("MK", label, b))
    K = make_base(label, rng)
    kset = set(K)
    step = B.make_step(N, K)
    prng = random.Random(seed_of("MK", label, b, "pairs"))
    between, within = [], []
    for g in GAPS:
        for _ in range(PAIRS):
            i = prng.randrange(40, 760 - g - 3)
            j = i + g + prng.randrange(4)
            L, S, st = B.least_bond(N, K, i, j, step=step)
            between.append({"i": i, "j": j, "g": g, "L": L, "status": st, **counts(kset, i, j)})
    k = 0
    while 40 + 64 * (k + 1) <= 760:
        i, j = 40 + 64 * k, 40 + 64 * (k + 1)
        L, S, st = B.least_bond(N, K, i, j, step=step)
        within.append({"i": i, "j": j, "L": L, "status": st, **counts(kset, i, j)})
        k += 1
    return {"label": label, "base": b, "knots": len(K), "between": between, "within": within, "seconds": round(time.time() - t0, 1)}


def run(workers):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "bases.jsonl")
    done = set()
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            done.add((r["label"], r["base"]))
    specs = [(lab, b) for lab in SETTINGS for b in range(BASES) if (lab, b) not in done]
    with Pool(workers) as pool, open(path, "a") as f:
        for rec in pool.imap_unordered(base_task, specs):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(rec["label"], rec["base"], rec["seconds"], flush=True)


def slope(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0:
        return None
    return float(np.polyfit(x, y, 1)[0])


def r2(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1] ** 2)


def summarize():
    bases = [json.loads(l) for l in open(os.path.join(OUT, "bases.jsonl"))]
    S = {"cells": {}}
    for lab in SETTINGS:
        bs = [b for b in bases if b["label"] == lab]
        pairs = [p for b in bs for p in b["between"]]
        dfn = [p for p in pairs if p["status"] == "ok"]
        cell = {"pairs": len(pairs), "defined_share": len(dfn) / len(pairs),
                "defined_by_gap": {str(g): sum(1 for p in pairs if p["g"] == g and p["status"] == "ok") / sum(1 for p in pairs if p["g"] == g) for g in GAPS},
                "blowups": sum(p["status"] == "blowup" for p in pairs)}
        for c in ("M", "D", "M3", "M4", "W2", "gap"):
            xs = [p[c] if c != "gap" else p["j"] - p["i"] for p in dfn]
            cell[f"slope_{c}"] = slope(xs, [p["L"] for p in dfn])
            cell[f"r2_{c}"] = r2(xs, [p["L"] for p in dfn])
        ws = []
        for b in bs:
            w = [p for p in b["within"] if p["status"] == "ok"]
            if len(w) >= 6:
                s = slope([p["M"] for p in w], [p["L"] for p in w])
                if s is not None:
                    ws.append(s)
        cell["within_slopes"] = ws
        cell["within_slope_median"] = float(np.median(ws)) if len(ws) >= 5 else None
        S["cells"][lab] = cell
    C = S["cells"]
    N_ = [f"N{q}" for q in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9)]
    B_ = [f"B{p}" for p in (0.5, 0.6, 0.7, 0.8, 0.9)]
    P = {}
    P["M1"] = {"slopes": {l: C[l]["slope_M"] for l in N_},
               "pooled_r2": r2([p["M"] for b in bases if b["label"] in N_ for p in b["between"] if p["status"] == "ok"],
                               [p["L"] for b in bases if b["label"] in N_ for p in b["between"] if p["status"] == "ok"])}
    P["M1"]["holds"] = all(s is not None and 0.09 <= s <= 0.13 for s in P["M1"]["slopes"].values()) and (P["M1"]["pooled_r2"] or 0) >= 0.95
    P["M2"] = {"slopes": {l: C[l]["slope_M"] for l in B_}}
    P["M2"]["holds"] = all(s is not None and 0.09 <= s <= 0.13 for s in P["M2"]["slopes"].values())
    s5, s9 = C["B0.5"]["slope_M"], C["B0.9"]["slope_M"]
    P["M2_rival"] = {"B0.9_over_B0.5": (s9 / s5) if s5 and s9 is not None else None,
                     "holds": s5 is not None and s9 is not None and s9 <= 0.8 * s5}
    P["M3"] = {"within_slope_median": {l: C[l]["within_slope_median"] for l in N_ + B_}}
    elig = [v for v in P["M3"]["within_slope_median"].values() if v is not None]
    P["M3"]["holds"] = len(elig) >= 5 and all(0.09 <= v <= 0.13 for v in elig)
    cv = {}
    for c in ("M", "D", "M3", "M4", "W2"):
        sl = [C[l][f"slope_{c}"] for l in N_ + B_ if C[l][f"slope_{c}"] is not None and C[l]["defined_share"] >= 0.5]
        cv[c] = float(np.std(sl) / np.mean(sl)) if len(sl) >= 3 and np.mean(sl) > 0 else None
    P["M4_steadiest_count"] = {"coefficient_of_variation": cv, "steadiest": min((k for k in cv if cv[k] is not None), key=lambda k: cv[k], default=None)}
    S["predictions"] = P
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(S, f, indent=1, sort_keys=True)
    print(json.dumps(P, indent=1, sort_keys=True))


if __name__ == "__main__":
    if "--summary" in sys.argv:
        summarize()
    else:
        run(int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6)
