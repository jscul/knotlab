#!/usr/bin/env python3
"""Referee PREFIX-END-R1, part 1 (from the census's records, the referee's own code; no import of census.py):
  - every matched concordance recomputed (positive above its matched negative, ties half), all runs and odd runs;
  - the risk set: negatives that end at the very next knot (they would be positives at the same age), and how often one growth serves
    as a negative;
  - the conditional logit: (a) the census's pairwise fit (logistic on paired differences, no intercept, standardized) reimplemented
    by Newton's method to the exact optimum; (b) the proper conditional likelihood for 1:3 matched sets (softmax over each set),
    fitted by Newton's method; (c) statsmodels' ConditionalLogit (a standard implementation, from a scratch install, if importable);
    each fit on even runs and scored by matched concordance on odd runs;
  - bootstraps: over positives only (the census's), and over growths (each growth resampled once, in either role, so negatives
    shared between matched sets are resampled together), for the paired differences;
  - partial readings: Pnest against kappa within terciles of m/n, and correlations.

    python3 -B ref_prefix.py      (writes result_prefix.json)"""
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "artifacts" / "PREFIX-END-20261112-001A" / "PREFIX-END-20261112-001A-E001_prefix_end"
SM = os.environ.get("REF_STATSMODELS")
FEATS = ["mn", "kappa", "maxD", "Uprefix", "Pnest", "hazard"]


def load():
    G = {json.loads(l)["run"]: json.loads(l) for l in (ART / "growths.jsonl").read_text().splitlines()}
    B = [json.loads(l) for l in (ART / "bases.jsonl").read_text().splitlines()]
    pos = {b["pos_run"]: b for b in B if b["role"] == "pos"}
    neg = {}
    for b in B:
        if b["role"] == "neg":
            neg.setdefault(b["pos_run"], []).append(b)
    neg2 = {}
    for b in B:
        if b["role"] == "neg2":
            neg2.setdefault(b["pos_run"], []).append(b)
    return G, pos, neg, neg2


def conc(pairs):
    a = np.array(pairs, float)
    return float(np.mean(np.where(a[:, 0] > a[:, 1], 1.0, np.where(a[:, 0] == a[:, 1], 0.5, 0.0)))) if len(a) else None


def vec(b):
    return np.array([b["mn"], b["kappa"], b["maxD"]] + b["deciles"], float)


def fit_pairwise(X, lam):
    """logistic on paired differences, no intercept: minimize mean softplus(-X w) + lam/2 |w|^2 (the census's objective), Newton"""
    w = np.zeros(X.shape[1])
    for _ in range(50):
        z = X @ w
        p = 1 / (1 + np.exp(-z))
        g = X.T @ (p - 1) / len(X) + lam * w
        Hm = (X * (p * (1 - p))[:, None]).T @ X / len(X) + lam * np.eye(len(w))
        w -= np.linalg.solve(Hm, g)
    return w


def fit_conditional(sets, lam=0.0):
    """1:k conditional logit: maximize sum log softmax(x_pos . w) over each matched set, Newton (sets: list of (x_pos, [x_neg]))"""
    d = len(sets[0][0])
    w = np.zeros(d)
    for _ in range(60):
        g = -lam * w
        Hm = -lam * np.eye(d)
        for xp, xn in sets:
            Xs = np.vstack([xp] + list(xn))
            s = Xs @ w
            s -= s.max()
            p = np.exp(s) / np.exp(s).sum()
            mean = p @ Xs
            g += xp - mean
            Hm -= (Xs * p[:, None]).T @ Xs - np.outer(mean, mean)
        w -= np.linalg.solve(Hm, g)
    return w


def main():
    G, pos, neg, neg2 = load()
    out = {"positives": len(pos), "negatives": sum(len(v) for v in neg.values())}
    nn = [b for v in neg.values() for b in v]
    out["negatives ending at the very next knot"] = sum(1 for b in nn if G[b["run"]]["dead"] and G[b["run"]]["knots"] == b["M"] + 1)
    out["negatives that end later / never"] = [sum(1 for b in nn if G[b["run"]]["dead"]), sum(1 for b in nn if not G[b["run"]]["dead"])]
    from collections import Counter
    use = Counter(b["run"] for b in nn)
    out["distinct negative growths; most uses of one"] = [len(use), max(use.values())]
    runs_all = sorted(pos)
    runs_odd = [r for r in runs_all if r % 2 == 1]
    pairs = lambda f, rs, N=neg: [(pos[r][f], n[f]) for r in rs for n in N.get(r, []) if f in n and f in pos[r]]
    out["concordance (all runs)"] = {f: conc(pairs(f, runs_all)) for f in FEATS}
    out["concordance (odd runs)"] = {f: conc(pairs(f, runs_odd)) for f in FEATS}
    # conditional logit, three ways
    train = [(vec(pos[r]), [vec(n) for n in neg[r]]) for r in runs_all if r % 2 == 0]
    X = np.array([xp - xn for xp, xns in train for xn in xns])
    sd = X.std(0) + 1e-9
    w_pair = fit_pairwise(X / sd, 1e-3)
    w_cond = fit_conditional([(xp / sd, [xn / sd for xn in xns]) for xp, xns in train])
    sc = lambda w, b: float((vec(b) / sd) @ w)
    out["conditional logit, odd runs"] = {
        "pairwise objective (the census's), exact optimum": conc([(sc(w_pair, pos[r]), sc(w_pair, n)) for r in runs_odd for n in neg[r]]),
        "1:3 conditional likelihood (Newton)": conc([(sc(w_cond, pos[r]), sc(w_cond, n)) for r in runs_odd for n in neg[r]])}
    if SM:
        sys.path.insert(0, SM)
        try:
            from statsmodels.discrete.conditional_models import ConditionalLogit
            rows, ys, gs = [], [], []
            for r in runs_all:
                if r % 2:
                    continue
                for b, y in [(pos[r], 1)] + [(n, 0) for n in neg[r]]:
                    rows.append(vec(b) / sd)
                    ys.append(y)
                    gs.append(r)
            res = ConditionalLogit(np.array(ys), np.array(rows), groups=np.array(gs)).fit(disp=0)
            w_sm = np.asarray(res.params)
            out["conditional logit, odd runs"]["statsmodels ConditionalLogit"] = conc([(sc(w_sm, pos[r]), sc(w_sm, n)) for r in runs_odd for n in neg[r]])
            out["statsmodels and Newton conditional weights agree (max abs difference)"] = float(np.max(np.abs(w_sm - w_cond)))
        except Exception as e:                       # noqa: BLE001
            out["statsmodels"] = f"not used: {e}"
    best_cheap = max(("mn", "kappa", "maxD"), key=lambda f: conc(pairs(f, runs_odd)))
    out["best cheap feature on odd runs"] = [best_cheap, conc(pairs(best_cheap, runs_odd))]
    # bootstraps of paired differences
    rng = np.random.default_rng(11)

    def diff(fa, fb, rs, wts=None, score=None):
        pa = [((score(pos[r]), score(n)) if fa == "logit" else (pos[r][fa], n[fa])) for r in rs for n in neg[r]]
        pb = [(pos[r][fb], n[fb]) for r in rs for n in neg[r]]
        if wts is None:
            return conc(pa) - conc(pb)
        ww = np.array([wts[(r, n["run"])] for r in rs for n in neg[r]], float)
        f = lambda P: float(np.sum(ww * np.array([1.0 if a > b else 0.5 if a == b else 0.0 for a, b in P])) / ww.sum())
        return f(pa) - f(pb)
    growths = sorted(G)
    boots = {}
    tests = [("Pnest", "mn", runs_all), ("Pnest", "kappa", runs_all), ("maxD", "mn", runs_all), ("logit", best_cheap, runs_odd)]
    score = lambda b: sc(w_pair, b)
    for fa, fb, rs in tests:
        key = f"{fa} minus {fb}" + (" (odd runs)" if rs is runs_odd else "")
        base = diff(fa, fb, rs, score=score)
        bp, bg = [], []
        for _ in range(1000):
            pick = list(rng.choice(rs, len(rs)))
            bp.append(diff(fa, fb, pick, score=score))
            cnt = Counter(rng.choice(growths, len(growths)))
            wts = {(r, n["run"]): cnt[r] * cnt[n["run"]] for r in rs for n in neg[r]}
            if sum(wts.values()) == 0:
                continue
            bg.append(diff(fa, fb, rs, wts, score=score))
        boots[key] = {"difference": base, "bootstrap over positives 95%": [float(np.quantile(bp, 0.025)), float(np.quantile(bp, 0.975))],
                      "bootstrap over growths 95%": [float(np.quantile(bg, 0.025)), float(np.quantile(bg, 0.975))]}
    out["paired differences"] = boots
    # Pnest against kappa within terciles of m/n, and correlations over all bases read
    allb = [pos[r] for r in runs_all] + nn
    mn = np.array([b["mn"] for b in allb])
    cuts = np.quantile([pos[r]["mn"] for r in runs_all], [1 / 3, 2 / 3])
    terc = {}
    for t, (lo, hi) in enumerate(((-1, cuts[0]), (cuts[0], cuts[1]), (cuts[1], 99))):
        rs = [r for r in runs_all if lo < pos[r]["mn"] <= hi]
        terc[str(t)] = {f: conc(pairs(f, rs)) for f in ("mn", "kappa", "Pnest", "maxD")}
    out["within terciles of the positive's m/n"] = terc
    M = np.array([[b[f] for f in ("mn", "kappa", "maxD", "Pnest", "hazard")] for b in allb])
    out["rank correlations (mn, kappa, maxD, Pnest, hazard)"] = np.corrcoef(np.argsort(np.argsort(M, axis=0), axis=0).T).round(3).tolist()
    (HERE / "result_prefix.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
