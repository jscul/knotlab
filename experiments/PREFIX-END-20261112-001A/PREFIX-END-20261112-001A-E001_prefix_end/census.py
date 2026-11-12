"""The frozen census of PREFIX-END-20261112-001A-E001 (contract.json beside this file): can the end of growth with closings
anywhere be read from its prefix counts?

Growths: 800 of X(0.3) to 6,000 moves (RANDOM-FATES-20261112-001A-E001's fates.py, hash pinned), seeds sha256 "PE:X0.3:run".
Positives: each ending's last base, at age M (its knots before the killing knot). Negatives (primary, risk set): for each positive,
3 growths of the same run parity drawn uniformly (seeded) among those with more than M knots, read at age M. Secondary negatives:
3 drawn among those with at least M + 500 knots (cheap features only). Even runs train, odd runs test.
Features of a base (n distinctions in knots, m knots, e(j) = knots among the oldest j):
  mn       m/n
  kappa    sum d(d - 1) / sum d over distinctions' knot counts d
  maxD     max over j >= 20 of e(j)/j
  Uprefix  max over j in {20, 40, 80, 160, 320} and the deciles of n of the share of 20 uniform patterns (j distinctions, e(j)
           distinct knots) allowing no state
  Pnest    share of 100 resamples keeping each knot's youngest distinction (the others redrawn uniformly among older ones, in age
           order, simple) allowing no state: the prefix counts' own end share
  hazard   the share of all triples lying on one side of one tie class (exact tie classes, fates.Reader): the base's chance of
           ending at a uniform closing (a ceiling)
  logit    conditional logistic regression on paired differences (positive minus each matched negative) of mn, kappa, maxD and
           e(j)/j at j/n = 0.1 .. 0.9, fit on even runs, its score on odd runs
Metric: matched concordance, P(feature of positive > feature of its matched negative), ties counted half, on odd runs (test) and on
all runs for unfitted features; 95% intervals by 1,000 bootstraps over positive growths.

Run from the repository root:
    .venv/bin/python -B experiments/PREFIX-END-20261112-001A/PREFIX-END-20261112-001A-E001_prefix_end/census.py --grow [--workers 8]
    .venv/bin/python -B experiments/PREFIX-END-20261112-001A/PREFIX-END-20261112-001A-E001_prefix_end/census.py --features [--workers 8]
    .venv/bin/python -B experiments/PREFIX-END-20261112-001A/PREFIX-END-20261112-001A-E001_prefix_end/census.py --summary
Output: artifacts/PREFIX-END-20261112-001A/PREFIX-END-20261112-001A-E001_prefix_end/{growths.jsonl, bases.jsonl, summary.json}.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from math import comb
from multiprocessing import Pool

import numpy as np
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census"))
import fates as F  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "PREFIX-END-20261112-001A", "PREFIX-END-20261112-001A-E001_prefix_end")
RUNS, H, Q = 800, 6000, 0.3
NEG, NEG2, GAP = 3, 3, 500
R_NEST, R_UNI = 100, 20


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def growth(run):
    knots, dead = F.grow(F.proc_expand(Q, random.Random(seed_of("PE", "X0.3", run))), H)
    return [tuple(sorted(t)) for t in knots], dead


def sat(K):
    if not K:
        return True
    with Solver(name=F.SOLVER, bootstrap_with=[c for t in K for c in F.cls(t)]) as s:
        return s.solve()


def nested(K, rng):
    out = set()
    for t in sorted(K, key=lambda t: t[2]):
        y = t[2]
        for _ in range(1000):
            a, b = rng.sample(range(y), 2)
            nt = tuple(sorted((a, b, y)))
            if nt not in out:
                break
        out.add(nt)
    return list(out)


def uniform(n, m, rng):
    seen = set()
    m = min(m, comb(n, 3))
    while len(seen) < m:
        seen.add(tuple(sorted(rng.sample(range(n), 3))))
    return list(seen)


def features(K, rng, full=True):
    n = max(v for t in K for v in t) + 1
    mx = np.bincount([t[2] for t in K], minlength=n)
    e = np.cumsum(mx)
    D = np.array([e[j - 1] / j for j in range(1, n + 1)])
    deg = np.bincount([v for t in K for v in t], minlength=n)
    f = {"n": int(n), "m": len(K), "mn": len(K) / n, "kappa": float((deg * (deg - 1)).sum() / deg.sum()),
         "maxD": float(D[19:].max()) if n > 20 else float(D.max()),
         "argmaxD": int(np.argmax(D[19:]) + 20) if n > 20 else int(np.argmax(D) + 1),
         "deciles": [float(D[max(1, int(round(n * x))) - 1]) for x in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)]}
    if full:
        js = sorted({j for j in (20, 40, 80, 160, 320) if j <= n} | {max(3, int(round(n * x))) for x in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)})
        f["Uprefix"] = max(sum(not sat(uniform(j, int(e[j - 1]), rng)) for _ in range(R_UNI)) / R_UNI for j in js)
        f["Pnest"] = sum(not sat(nested(K, rng)) for _ in range(R_NEST)) / R_NEST
        rd = F.Reader(n, K, samples=60, seed=1)
        cl = rd.tie_classes()
        rd.close()
        h = sum(comb(sum(1 for _, x in c if x == 0), 3) + comb(sum(1 for _, x in c if x == 1), 3) for c in cl)
        f["hazard"] = h / comb(n, 3)
    return f


def grow_task(run):
    K, dead = growth(run)
    return {"run": run, "dead": dead, "knots": len(K)}


def base_task(spec):
    run, M, role, pos_run = spec
    K, dead = growth(run)
    rng = random.Random(seed_of("PE", "feat", run, M, role, pos_run))
    f = features(K[:M], rng, full=(role != "neg2"))
    return {"run": run, "M": M, "role": role, "pos_run": pos_run, **f}


def plan():
    G = {json.loads(l)["run"]: json.loads(l) for l in open(os.path.join(OUT, "growths.jsonl"))}
    rng = random.Random(seed_of("PE", "plan"))
    specs = []
    for r, g in sorted(G.items()):
        if not g["dead"]:
            continue
        M = g["knots"] - 1
        specs.append((r, M, "pos", r))
        risk = [s for s, h in G.items() if s % 2 == r % 2 and s != r and h["knots"] > M]
        safe = [s for s, h in G.items() if s % 2 == r % 2 and s != r and h["knots"] >= M + GAP]
        for s in rng.sample(risk, min(NEG, len(risk))):
            specs.append((s, M, "neg", r))
        for s in rng.sample(safe, min(NEG2, len(safe))):
            specs.append((s, M, "neg2", r))
    return specs


def run_grow(workers):
    os.makedirs(OUT, exist_ok=True)
    with Pool(workers) as pool, open(os.path.join(OUT, "growths.jsonl"), "w") as f:
        for rec in pool.imap(grow_task, range(RUNS), chunksize=4):
            f.write(json.dumps(rec) + "\n")


def run_features(workers):
    path = os.path.join(OUT, "bases.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(b["run"], b["M"], b["role"], b["pos_run"]) for b in map(json.loads, open(path))}
    specs = [s for s in plan() if s not in done]
    specs.sort(key=lambda s: -s[1])
    with Pool(workers) as pool, open(path, "a") as f:
        for rec in pool.imap_unordered(base_task, specs, chunksize=1):
            f.write(json.dumps(rec) + "\n")
            f.flush()


def concord(pairs):
    if not pairs:
        return None
    return float(np.mean([1.0 if a > b else 0.5 if a == b else 0.0 for a, b in pairs]))


def summarize():
    B = [json.loads(l) for l in open(os.path.join(OUT, "bases.jsonl"))]
    pos = {b["pos_run"]: b for b in B if b["role"] == "pos"}
    neg = {}
    for b in B:
        if b["role"] in ("neg", "neg2"):
            neg.setdefault((b["pos_run"], b["role"]), []).append(b)
    feats = ["mn", "kappa", "maxD", "Uprefix", "Pnest", "hazard"]

    def vec(b):
        return np.array([b["mn"], b["kappa"], b["maxD"]] + b["deciles"])

    train = [(pos[r], n) for r in pos if r % 2 == 0 for n in neg.get((r, "neg"), [])]
    X = np.array([vec(p) - vec(n) for p, n in train])
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xs = X / sd
    w = np.zeros(X.shape[1])
    for _ in range(3000):                        # logistic regression on differences, no intercept (conditional, 1:1)
        z = Xs @ w
        g = Xs.T @ (1 / (1 + np.exp(-z)) - 1) / len(Xs) + 1e-3 * w
        w -= 0.5 * g
    score = lambda b: float((vec(b) / sd) @ w)
    S = {"positives": len(pos), "logit_weights": w.tolist()}
    rng = np.random.default_rng(seed_of("PE", "boot") % (2 ** 32))
    for split in ("all", "test"):
        runs = [r for r in pos if split == "all" or r % 2 == 1]
        out = {}
        for fe in feats + ["logit"]:
            if fe == "logit" and split == "all":
                continue
            def pairs_for(rs, role="neg"):
                pr = []
                for r in rs:
                    for n in neg.get((r, role), []):
                        if fe == "logit":
                            pr.append((score(pos[r]), score(n)))
                        elif fe in pos[r] and fe in n:
                            pr.append((pos[r][fe], n[fe]))
                return pr
            c = concord(pairs_for(runs))
            boots = []
            for _ in range(1000):
                rs = list(rng.choice(runs, len(runs)))
                boots.append(concord(pairs_for(rs)))
            out[fe] = {"concordance": c, "ci95": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]}
            if fe in ("mn", "kappa", "maxD", "logit"):
                out[fe]["concordance_vs_safe"] = concord(pairs_for(runs, "neg2"))
        # paired differences against m/n
        def diff_ci(fa, fb):
            def val(rs):
                pa, pb = [], []
                for r in rs:
                    for n in neg.get((r, "neg"), []):
                        av = (score(pos[r]), score(n)) if fa == "logit" else (pos[r].get(fa), n.get(fa))
                        bv = (pos[r][fb], n[fb])
                        if None not in av:
                            pa.append(av)
                            pb.append(bv)
                return concord(pa) - concord(pb)
            v = val(runs)
            bs = [val(list(rng.choice(runs, len(runs)))) for _ in range(1000)]
            return {"diff": v, "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]}
        out["Pnest_minus_mn"] = diff_ci("Pnest", "mn")
        out["Pnest_minus_kappa"] = diff_ci("Pnest", "kappa")
        out["maxD_minus_mn"] = diff_ci("maxD", "mn")
        if split == "test":
            best = max(("mn", "kappa", "maxD"), key=lambda f: out[f]["concordance"])
            out["logit_minus_best_cheap"] = {"best": best, **diff_ci("logit", best)}
        S[split] = out
    E1 = {"positives_share_Uprefix_gt_half": float(np.mean([p["Uprefix"] > 0.5 for p in pos.values()])),
          "negatives_share_Uprefix_gt_half": float(np.mean([n["Uprefix"] > 0.5 for (r, role), ns in neg.items() if role == "neg" for n in ns]))}
    S["E1"] = E1
    a = S["all"]
    t = S["test"]
    P = {"E0_mn_above_0.55": a["mn"]["concordance"] >= 0.55,
         "E1_uniform_prefix_fails": E1["positives_share_Uprefix_gt_half"] < 0.10,
         "E2_counts_read_the_end": a["Pnest"]["concordance"] >= 0.65 and a["Pnest_minus_mn"]["diff"] >= 0.05 and a["Pnest_minus_mn"]["ci95"][0] > 0,
         "E2_kill_within_0.05_of_mn": abs(a["Pnest_minus_mn"]["diff"]) < 0.05,
         "E3_maxD_no_better_than_mn": a["maxD_minus_mn"]["diff"] <= 0.03,
         "E4_fit_beats_cheap": t["logit_minus_best_cheap"]["ci95"][0] > 0}
    S["predictions"] = P
    # tertiles by age
    ages = sorted(p["M"] for p in pos.values())
    cuts = [ages[len(ages) // 3], ages[2 * len(ages) // 3]]
    S["tertiles"] = {}
    for name, lo, hi in (("young", -1, cuts[0]), ("middle", cuts[0], cuts[1]), ("old", cuts[1], 10 ** 9)):
        rs = [r for r, p in pos.items() if lo < p["M"] <= hi]
        S["tertiles"][name] = {fe: concord([(pos[r][fe], n[fe]) for r in rs for n in neg.get((r, "neg"), []) if fe in n]) for fe in feats}
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(S, f, indent=1, sort_keys=True, default=lambda o: o.item() if hasattr(o, "item") else o)
    print(json.dumps(S, indent=1, sort_keys=True, default=lambda o: o.item() if hasattr(o, "item") else o))


if __name__ == "__main__":
    w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    if "--grow" in sys.argv:
        run_grow(w)
    elif "--features" in sys.argv:
        run_features(w)
    else:
        summarize()
