"""Referee R1 for WEAVE-LAWS-20261117-001: NAE with a density eps of the three other not-all-equal-class knots (own code).

  .venv/bin/python -B referee_mix.py > referee_mix.json 2> referee_mix_runs.jsonl
  .venv/bin/python -B referee_mix.py --long > referee_mix_long.jsonl

A probe one size past the study, not a study: each knot of the weave is NAE, or with probability eps one of the three signed
not-all-equal knots (uniformly); every knot of such a base is in the pairwise class, so its pair counts and N carry the base
(each signed NAE knot holds iff N minus half the pair counts' mismatches with its pattern is zero).  On the cylinder of width w
and many rows the base is read through the product of row transfers, one distinction at a time (front of w + 1 bits):
- whether any state survives;
- states per distinction, exp(top Lyapunov exponent / w);
- the gap, (first minus second Lyapunov exponent) per row in log base 3, and gap x width;
exponents averaged over rows after a burn-in of 100.  Widths are multiples of 3, where NAE's finite-width readings are cleanest.
Critical: gap x width stays level as w grows (NAE: about 1.2).  Disordered: the gap levels off at a positive value, so gap x width
grows in proportion to w.
Checks: eps = 0 reproduces NAE's dense transfer spectrum; at w = 6 the distinction-at-a-time product equals the strip product
of referee_scope.strip on the same draws.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

from referee_laws import live, top_eigs, transfer
from referee_scope import PAIRS, strip

KEYS = list(PAIRS)


def draws(w, rows, eps, seed):
    rng = np.random.default_rng(seed)
    U = np.where(rng.random((rows, w)) < eps, rng.integers(1, 4, (rows, w)), 0)
    D = np.where(rng.random((rows, w)) < eps, rng.integers(1, 4, (rows, w)), 0)
    return U, D


def excluded_mask(code, a, b, c):
    m = np.zeros(a.shape, bool)
    for p in PAIRS[KEYS[code]]:
        m |= (a == p[0]) & (b == p[1]) & (c == p[2])
    return m


def run(w, U, D, k=3, seed=0, burn=0):
    N = 1 << (w + 1)
    s = np.arange(N)
    bit = [(s >> t) & 1 for t in range(w + 1)]
    rng = np.random.default_rng(seed)
    V = np.zeros((N, k))
    V[: 1 << w] = rng.random((1 << w, k))
    V[: 1 << w, 0] = 1.0
    logs = np.zeros(k)
    rows = len(U)
    for j in range(rows):
        for i in range(w):
            old_i = bit[i]
            old_next = bit[i + 1] if i + 1 < w else bit[w]
            new = np.zeros_like(V)
            for x in (0, 1):
                xs = np.full(N, x)
                bad = excluded_mask(U[j, i], old_i, old_next, xs)
                if i >= 1:
                    bad |= excluded_mask(D[j, i - 1], old_i, bit[i - 1], xs)
                if i == w - 1:
                    bad |= excluded_mask(D[j, w - 1], bit[w], xs, bit[0])
                idx = (s & ~(1 << i)) | (x << i)
                if i == 0:
                    idx = (idx & ~(1 << w)) | (bit[0] << w)
                ok = ~bad
                for c in range(k):
                    new[:, c] += np.bincount(idx[ok], weights=V[ok, c], minlength=N)
            V = new
        V[: 1 << w] += V[1 << w:]
        V[1 << w:] = 0
        if not V[:, 0].any():
            return {"dead_at_row": j + 1}
        Q, R = np.linalg.qr(V[: 1 << w])
        d = np.abs(np.diag(R))
        if j >= burn:
            logs += np.log(np.where(d > 0, d, 1e-300))
        V[: 1 << w] = Q * np.sign(np.diag(R))
    g = logs / (rows - burn)
    out = {"per_site": math.exp(g[0] / w), "lyapunov_per_row": g.tolist()}
    if burn == 0:
        out["log_count"] = float(logs[0] + math.log(V[:, 0].sum()))
    if k > 1:
        out.update(gap_log3=float((g[0] - g[1]) / math.log(3)), gap_x_width=float((g[0] - g[1]) / math.log(3) * w))
    return out


def strip_log_count(w, U, D):
    v, lc = np.ones(1 << w), 0.0
    for j in range(len(U)):
        T = strip(w, [PAIRS[KEYS[c]] for c in U[j]], [PAIRS[KEYS[c]] for c in D[j]]).astype(float)
        v = T.T @ v
        t = v.sum()
        if t == 0:
            return None
        lc += math.log(t)
        v /= t
    return lc


def checks():
    out = {}
    for w in (6, 9):
        m = top_eigs(live(transfer(w, (PAIRS["NAE"], PAIRS["NAE"]))))
        lam1 = next(x for x in m if x < m[0] * (1 - 1e-9))
        U = np.zeros((300, w), int)
        r = run(w, U, U, burn=100)
        out[f"NAE w={w}"] = {"dense_per_site": float(m[0] ** (1 / w)), "dense_gap": float(math.log(m[0] / lam1, 3)),
                             "product_per_site": r["per_site"], "product_gap": r["gap_log3"]}
    U, D = draws(6, 60, 0.1, 5)
    r = run(6, U, D, k=1)
    out["w=6 eps=0.1, 60 rows: strip log count vs distinction-at-a-time"] = [strip_log_count(6, U, D),
                                                                              r["log_count"]]
    return out


def main(widths=(6, 9, 12, 15), eps_list=(0.0, 0.01, 0.03, 0.1, 0.3), rows=600, burn=100, seeds=(1, 2)):
    out = {"checks": checks(), "runs": []}
    for eps in eps_list:
        for w in widths:
            for seed in (seeds if eps > 0 else seeds[:1]):
                U, D = draws(w, rows, eps, 1000 * seed + w)
                r = run(w, U, D, burn=burn)
                r.update(eps=eps, width=w, seed=seed, rows=rows, burn=burn)
                out["runs"].append(r)
                print(json.dumps(r), file=sys.stderr, flush=True)
    print(json.dumps(out, indent=1))


def long_runs():
    """Survival over 5,000 rows (eps 0.1 and 0.03, widths 6 and 9, three fresh seeds); writes JSON lines."""
    for eps in (0.1, 0.03):
        for w in (6, 9):
            for seed in (11, 12, 13):
                U, D = draws(w, 5000, eps, seed * 100 + w)
                r = run(w, U, D, burn=100)
                r.pop("lyapunov_per_row", None)
                print(json.dumps({"eps": eps, "width": w, "seed": seed, "rows": 5000, **r}), flush=True)


if __name__ == "__main__":
    long_runs() if "--long" in sys.argv else main()
