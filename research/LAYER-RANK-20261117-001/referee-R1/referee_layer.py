"""Referee R1 for LAYER-RANK-20261117-001 (own code; nothing imported from the study).

  .venv/bin/python -B referee_layer.py > referee_layer.json

1. The infinite-width recursion, written from the gate rules: a true gate's rank is the least Strahler number of its
   derivation; an OR of true inputs takes the least of max(rank, 1); an AND of two true inputs of ranks i, j takes max(i, j),
   or i + 1 when i = j. Inputs are independent at infinite width. The identity Q_{L+1}(r) = Q_L(r) - q_L(r)^2 / 2 is checked
   against it at every layer. The frozen M-quantities are recomputed, and the largest rank among w gates (r with
   P(rank > r) < 1 / (w p), the study's rule) and the mean are read at the depths SEQUENTIAL-WALL measured.
2. An exact finite-width simulation, the referee's own: w gates per layer, each reading two distinct uniform gates of the layer
   below, AND or OR with chance 1/2, inputs true with chance 1/2. Compared with the recursion at w = 2^17 (S1), and the
   frozen S2 readings at w = 1,024 to depth 4,096 (50 samples).
"""
from __future__ import annotations

import json
import math

import numpy as np


def step(q):
    """One layer at infinite width; q[r] = P(true with rank r). Returns the next q."""
    R = len(q) + 2
    q = np.concatenate([q, np.zeros(R - len(q))])
    p = q.sum()
    # OR: inputs' ranks lifted to at least 1; result is the least over true inputs
    qo = q.copy()
    qo[1] += qo[0]
    qo[0] = 0.0
    S = np.cumsum(qo[::-1])[::-1]               # P(true, lifted rank >= r)
    surv = S + (1 - p)                          # P(input is false or has lifted rank >= r)
    surv_next = np.concatenate([surv[1:], [1 - p]])
    or_ = surv ** 2 - surv_next ** 2            # P(min over true inputs = r, at least one true)
    # AND: both true; rank max if different, r + 1 if both r
    C = np.cumsum(q)                            # P(true, rank <= r)
    Cprev = np.concatenate([[0.0], C[:-1]])
    and_ = C ** 2 - Cprev ** 2 - q ** 2         # max = r, the two not both r
    and_[1:] += q[:-1] ** 2
    out = 0.5 * or_ + 0.5 * and_
    while len(out) > 2 and out[-1] < 1e-300:
        out = out[:-1]
    return out


def stats(q, L):
    p = q.sum()
    f = q / p
    r = np.arange(len(f))
    mu = float((f * r).sum())
    sd = float(math.sqrt((f * (r - mu) ** 2).sum()))
    F = np.cumsum(f)
    half = int(round(math.sqrt(L) / 2))
    return {"p": float(p), "mean": mu, "sd": sd, "LF1": float(L * F[1]) if len(F) > 1 else None,
            "LF2": float(L * F[2]) if len(F) > 2 else None, "mean_x_tie": float(mu * (f ** 2).sum()),
            "profile_half": float(f[half] * L / (2 * half)) if half < len(f) else None,
            **{f"largest_of_{w}": int(np.searchsorted(F, 1 - 1.0 / (w * p))) for w in (1024,)}}


def recursion(Lmax, cps):
    q = np.array([0.5])
    out, worst = {}, 0.0
    for L in range(1, Lmax + 1):
        new = step(q)
        if L >= 2:  # the identity, from layer L to L + 1 with every true rank >= 1 at layer L
            Q = np.cumsum(np.concatenate([q, np.zeros(len(new) - len(q))]))
            Qn = np.cumsum(new)
            qq = np.concatenate([q, np.zeros(len(new) - len(q))])
            worst = max(worst, float(np.max(np.abs(Qn - (Q - 0.5 * qq ** 2)))))
        q = new
        if L in cps:
            out[L] = stats(q, L)
    return out, worst


def simulate(w, d, rng, cps):
    t = rng.random(w) < 0.5
    rk = np.zeros(w, np.int64)
    out = {}
    BIG = np.int64(1) << 40
    for L in range(1, d + 1):
        a = rng.integers(0, w, w)
        b = (a + rng.integers(1, w, w)) % w            # distinct from a
        g_and = rng.random(w) < 0.5
        ta, tb, ra, rb = t[a], t[b], rk[a], rk[b]
        and_t = ta & tb
        and_r = np.where(ra == rb, ra + 1, np.maximum(ra, rb))
        or_t = ta | tb
        or_r = np.minimum(np.where(ta, np.maximum(ra, 1), BIG), np.where(tb, np.maximum(rb, 1), BIG))
        t = np.where(g_and, and_t, or_t)
        rk = np.where(t, np.where(g_and, and_r, or_r), 0)
        if L in cps:
            out[L] = {"p": float(t.mean()), "largest": int(rk[t].max()) if t.any() else -1,
                      "mean": float(rk[t].mean()) if t.any() else -1.0}
    return out


def main():
    cps = sorted({8, 16, 32, 64, 128, 256, 512, 1024, 4096, 10, 100, 1000, 10000, 100000})
    rec, worst = recursion(100000, set(cps))
    lg = lambda L: math.log(L)
    M = {"identity_max_abs_error": worst,
         "M1_mean_exponent_1e3_1e5": math.log(rec[100000]["mean"] / rec[1000]["mean"]) / math.log(100),
         "M2_mean_over_sqrtL": [rec[1000]["mean"] / math.sqrt(1000), rec[100000]["mean"] / math.sqrt(100000)],
         "M3_sd_exponent": math.log(rec[100000]["sd"] / rec[1000]["sd"]) / math.log(100),
         "M4": [rec[100000]["LF1"], rec[100000]["LF2"]], "M5": rec[100000]["mean_x_tie"], "M6": rec[100000]["profile_half"],
         "M7_slope": ((rec[100000]["mean"] + lg(100000) / 4) - (rec[1000]["mean"] + lg(1000) / 4))
                     / (math.sqrt(100000) - math.sqrt(1000))}
    # what lowers the exponent at the depths SEQUENTIAL-WALL measured
    ds = [8, 16, 32, 64, 128, 256]
    small = {d: {"mean": rec[d]["mean"], "largest_of_1024": rec[d]["largest_of_1024"], "sqrt_d": math.sqrt(d),
                 "two_thirds_sqrt_d_minus_quarter_ln": 2 / 3 * math.sqrt(d) - lg(d) / 4} for d in ds}
    ex = lambda key: math.log(small[256][key] / small[8][key]) / math.log(32)
    local = {"largest_of_1024_exponent_8_256": ex("largest_of_1024"), "mean_exponent_8_256": ex("mean"),
             "mean_local_exponents": {f"{a}-{b}": math.log(small[b]["mean"] / small[a]["mean"]) / math.log(b / a)
                                      for a, b in zip(ds, ds[1:])},
             "largest_minus_sqrt_d": {d: small[d]["largest_of_1024"] - math.sqrt(d) for d in ds}}
    rng = np.random.default_rng(20261117)
    s1 = {}
    for w, d in ((2 ** 17, 1024),):
        runs = [simulate(w, d, rng, {64, 256, 1024}) for _ in range(3)]
        s1[w] = {L: {"sim_mean_median": float(np.median([r[L]["mean"] for r in runs])), "recursion_mean": rec[L]["mean"]
                     if L in rec else None} for L in (64, 256, 1024)}
    runs = [simulate(1024, 4096, rng, {1024, 4096}) for _ in range(50)]
    s2 = {}
    for L in (1024, 4096):
        alive = [r[L]["largest"] for r in runs if r[L]["largest"] >= 0]
        s2[L] = {"median_largest_with_some_true": float(np.median(alive)) if alive else None,
                 "all_false_share": float(np.mean([r[L]["p"] == 0 for r in runs])),
                 "all_true_share": float(np.mean([r[L]["p"] == 1 for r in runs]))}
    print(json.dumps({"recursion": {str(k): v for k, v in rec.items()}, "M": M, "small_depths": small, "local": local,
                      "S1": s1, "S2": s2}, indent=1))


if __name__ == "__main__":
    main()
