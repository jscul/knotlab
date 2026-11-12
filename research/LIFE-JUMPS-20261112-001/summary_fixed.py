# A copy of the frozen census.py with two changes so its summary runs: HERE points at the experiment folder (the copy lives in research/),
# and json.dump / json.dumps get default=lambda o: o.item(), since the frozen code put numpy booleans in its verdicts and json cannot
# write them (TypeError at the first summary). Nothing that computes a verdict differs; diff against census.py shows exactly these lines.
"""The frozen census of LIFE-JUMPS-20261112-001A-E001 (contract.json beside this file): tie classes over the whole life of
growing knot patterns under not-all-equal.

Processes and readers are RANDOM-FATES-20261112-001A-E001's frozen fates.py (sha256 pinned in the contract), imported by path.
Settings: U(n) on n = 100 (100 runs), 200 (60) and 300 (30), grown until the end; X(0.2) and X(0.3) to 6,000 moves; X(0.35),
O global (0.3) and O local (0.3) to 2,000 moves; 100 runs each. Seeds: sha256 of "LJ:label:run" (fresh; RANDOM-FATES used other
strings). Time is counted in knots. Readings (exact tie classes, fates.Reader with 60 sampled states) at every 2% of the life
(the knots before the ending knot, or all knots when it does not end), at 1 to 20, 30, 40 and 50 knots before an end, and, for
growths that pass them, after 300, 500, 1,000, 2,000, 3,000 and 6,000 knots. Each reading records the distinctions in knots, the
largest class, its two sides (members equal to its first member, and unequal), the tied distinctions, the number of classes, the
closing hazard h (the share of all triples of distinctions lying on one side of one class: a closing knot there would end the
growth, ignoring triples already present), and the median arrival index of the largest class's members.

Run from the repository root:
    .venv/bin/python -B experiments/LIFE-JUMPS-20261112-001A/LIFE-JUMPS-20261112-001A-E001_whole_lives/census.py [--workers 10]
    .venv/bin/python -B experiments/LIFE-JUMPS-20261112-001A/LIFE-JUMPS-20261112-001A-E001_whole_lives/census.py --summary
Output: artifacts/LIFE-JUMPS-20261112-001A/LIFE-JUMPS-20261112-001A-E001_whole_lives/{runs.jsonl, summary.json, log.txt}.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import time
from math import comb
from multiprocessing import Pool

import numpy as np

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "experiments", "LIFE-JUMPS-20261112-001A", "LIFE-JUMPS-20261112-001A-E001_whole_lives")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census"))
import fates as F  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "LIFE-JUMPS-20261112-001A", "LIFE-JUMPS-20261112-001A-E001_whole_lives")
SETTINGS = [("U100", 100), ("U200", 60), ("U300", 30), ("X0.2", 100), ("X0.3", 100), ("X0.35", 100), ("Og0.3", 100), ("Ol0.3", 100)]
HORIZON = {"X0.2": 6000, "X0.3": 6000, "X0.35": 2000, "Og0.3": 2000, "Ol0.3": 2000}
LAGS = list(range(1, 21)) + [30, 40, 50]
FIXED = [300, 500, 1000, 2000, 3000, 6000]


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def make_gen(label, rng):
    if label.startswith("U"):
        return F.proc_uniform(int(label[1:]), rng)
    q = float(label[2:]) if label[:2] in ("Og", "Ol") else float(label[1:])
    if label.startswith("X"):
        return F.proc_expand(q, rng)
    return F.proc_overlap(q, rng, local=label.startswith("Ol"))


def read(K, seed):
    N = max(v for t in K for v in t) + 1
    rd = F.Reader(N, K, samples=60, seed=seed)
    cl = rd.tie_classes()
    rd.close()
    used = len({v for t in K for v in t})
    out = {"m": len(K), "n": used, "classes": len(cl), "tied": sum(len(c) for c in cl)}
    if cl:
        big = max(cl, key=len)
        a = sum(1 for _, e in big if e == 0)
        out.update({"largest": len(big), "sides": [a, len(big) - a],
                    "members_median_index": float(np.median([v for v, _ in big]))})
        h = sum(comb(sum(1 for _, e in c if e == 0), 3) + comb(sum(1 for _, e in c if e == 1), 3) for c in cl)
        out["hazard"] = h / comb(used, 3) if used >= 3 else 0.0
    else:
        out.update({"largest": 1, "sides": [1, 0], "hazard": 0.0})
    out["share"] = out["largest"] / used
    return out


def task(spec):
    label, run = spec
    t0 = time.time()
    rng = random.Random(seed_of("LJ", label, run))
    if label.startswith("U"):
        n = int(label[1:])
        knots, dead = F.grow(make_gen(label, rng), 50 * n)
    else:
        knots, dead = F.grow(make_gen(label, rng), HORIZON[label])
    M = len(knots) - 1 if dead else len(knots)
    pts = set(max(1, int(round(M * k / 50))) for k in range(1, 51))
    if dead:
        pts |= {len(knots) - k for k in LAGS if len(knots) - k >= 1}
    pts |= {m for m in FIXED if m <= M}
    reads = {}
    for m in sorted(pts):
        reads[str(m)] = read(knots[:m], seed=run)
    rec = {"label": label, "run": run, "dead": dead, "knots": len(knots), "M": M,
           "n_end": len({v for t in knots[:M] for v in t}), "reads": reads, "seconds": round(time.time() - t0, 1)}
    if dead:
        rec["killer"] = list(knots[-1])
    return rec


def log(msg):
    print(msg, flush=True)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(msg + "\n")


def run(workers):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "runs.jsonl")
    done = set()
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            done.add((r["label"], r["run"]))
    specs = [(lab, r) for lab, runs in SETTINGS for r in range(runs) if (lab, r) not in done]
    specs.sort(key=lambda s: (not s[0].startswith("U3"), not s[0].startswith("U2"), s[0]))
    log(f"start {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC: {len(specs)} growths")
    t0 = time.time()
    with Pool(workers) as pool, open(path, "a") as f:
        for i, rec in enumerate(pool.imap_unordered(task, specs, chunksize=1)):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if (i + 1) % 50 == 0:
                log(f"{i + 1}/{len(specs)} growths, {time.time() - t0:.0f} s")
    log(f"done {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC, {time.time() - t0:.0f} s")


def at_frac(r, f):
    m = max(1, int(round(r["M"] * f)))
    keys = sorted(int(k) for k in r["reads"])
    k = min(keys, key=lambda x: abs(x - m))
    return r["reads"][str(k)]


def at_lag(r, k):
    return r["reads"].get(str(r["knots"] - k))


def auc(pos, neg):
    if not pos or not neg:
        return None
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def summarize():
    recs = [json.loads(l) for l in open(os.path.join(OUT, "runs.jsonl"))]
    by = {}
    for r in recs:
        by.setdefault(r["label"], []).append(r)
    S = {"settings": {}}
    for lab, rs in by.items():
        e = {"runs": len(rs), "ended": sum(r["dead"] for r in rs)}
        prof = {}
        for f in (0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0):
            xs = [at_frac(r, f)["share"] for r in rs]
            prof[str(f)] = float(np.median(xs))
        e["share_by_life_fraction_median"] = prof
        ends = [r for r in rs if r["dead"]]
        if ends:
            e["share_by_lag_median"] = {str(k): float(np.median([at_lag(r, k)["share"] for r in ends if at_lag(r, k)]))
                                        for k in (50, 40, 30, 20, 10, 5, 2, 1)}
        S["settings"][lab] = e
    P = {}
    # J1
    j1 = {}
    for lab in ("U100", "U200", "U300"):
        rs = by[lab]
        a = np.mean([at_lag(r, 40)["share"] <= 0.05 for r in rs if at_lag(r, 40)])
        b = np.mean([at_lag(r, 1)["share"] >= 0.5 for r in rs])
        j1[lab] = {"share_le_0.05_at_k40": float(a), "share_ge_0.5_at_k1": float(b)}
    P["J1"] = {"detail": j1, "holds": all(v["share_le_0.05_at_k40"] >= 0.9 and v["share_ge_0.5_at_k1"] >= 0.8 for v in j1.values())}
    # J1b: fixed length in knots, not in share of life: median share at k = 10 within a factor two between n = 100 and 300
    s100 = S["settings"]["U100"]["share_by_lag_median"]["10"]
    s300 = S["settings"]["U300"]["share_by_lag_median"]["10"]
    P["J1b"] = {"k10_U100": s100, "k10_U300": s300, "holds": s100 > 0 and 0.5 <= s300 / s100 <= 2}
    # J2: a class of at least 10 with share >= 0.05 at half the life, per process, among growths that end after >= 200 knots
    j2 = {}
    for lab in ("X0.3", "X0.35", "Og0.3", "Ol0.3"):
        rs = [r for r in by[lab] if r["dead"] and r["knots"] >= 200]
        hit = [at_frac(r, 0.5)["largest"] >= 10 and at_frac(r, 0.5)["share"] >= 0.05 for r in rs]
        surv = [r for r in by[lab] if not r["dead"]]
        j2[lab] = {"ended_ge200": len(rs), "share_with_class_at_half_life": float(np.mean(hit)) if hit else None,
                   "survivors": len(surv),
                   "survivors_with_class_at_half": float(np.mean([at_frac(r, 0.5)["largest"] >= 10 and at_frac(r, 0.5)["share"] >= 0.05 for r in surv])) if surv else None}
    P["J2"] = {"detail": j2, "holds": all(v["share_with_class_at_half_life"] is not None and v["share_with_class_at_half_life"] >= 0.6 for v in j2.values())}
    # J3: contrast of r = s(k=20)/s(k=1)
    j3 = {}
    for lab in ("U100", "U200", "U300", "X0.3", "X0.35", "Og0.3", "Ol0.3"):
        rr = [at_lag(r, 20)["share"] / at_lag(r, 1)["share"] for r in by[lab] if r["dead"] and at_lag(r, 20)]
        j3[lab] = float(np.median(rr)) if rr else None
    P["J3"] = {"median_ratio_k20_over_k1": j3,
               "holds": all(j3[l] is not None and j3[l] >= 0.7 for l in ("X0.3", "X0.35", "Og0.3", "Ol0.3"))
               and all(j3[l] is not None and j3[l] <= 0.2 for l in ("U100", "U200", "U300"))}
    # J4: early signal at X(0.3)
    j4 = {}
    for m in (300, 1000):
        alive = [r for r in by["X0.3"] if str(m) in r["reads"] and r["knots"] > m]
        pos = [r["reads"][str(m)]["share"] for r in alive if r["dead"]]
        neg = [r["reads"][str(m)]["share"] for r in alive if not r["dead"]]
        posh = [r["reads"][str(m)]["hazard"] for r in alive if r["dead"]]
        negh = [r["reads"][str(m)]["hazard"] for r in alive if not r["dead"]]
        j4[str(m)] = {"later_end": len(pos), "survive": len(neg), "auc_share": auc(pos, neg), "auc_hazard": auc(posh, negh)}
    P["J4"] = {"detail": j4, "holds": all(v["auc_share"] is not None and v["auc_share"] >= 0.75 for v in j4.values())}
    # J5: X(0.2) at 6,000 knots
    xs = [r["reads"]["6000"]["largest"] for r in by["X0.2"] if "6000" in r["reads"]]
    P["J5"] = {"runs_reaching_6000": len(xs), "share_le15": float(np.mean([x <= 15 for x in xs])) if xs else None,
               "holds": bool(xs) and np.mean([x <= 15 for x in xs]) >= 0.9}
    # J6: the largest class is old
    j6 = {}
    for lab in ("X0.3", "X0.35", "Og0.3", "Ol0.3"):
        rs = [r for r in by[lab] if r["dead"] and at_lag(r, 1).get("members_median_index") is not None]
        old = [at_lag(r, 1)["members_median_index"] < (r["n_end"] - 1) / 2 for r in rs]
        j6[lab] = float(np.mean(old)) if old else None
    P["J6"] = {"share_older_than_median": j6, "holds": all(v is not None and v >= 0.8 for v in j6.values())}
    S["predictions"] = P
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(S, f, indent=1, sort_keys=True, default=lambda o: o.item())
    print(json.dumps(P, indent=1, sort_keys=True, default=lambda o: o.item()))


if __name__ == "__main__":
    if "--summary" in sys.argv:
        summarize()
    else:
        run(int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 10)
