"""Referee R1 for WEAVE-LAWS-20261117-001: how far "the pairwise laws are critical or frozen" reaches (own code).

  .venv/bin/python -B referee_scope.py > referee_scope.json

1. Every law that puts one not-all-equal-class knot on all up knots and one on all down knots: 4 x 4 = 16 pairs (the study tested
   6). For each: the bond-sign consistency test (own derivation), the exact frozen test on the live part of the row transfer
   (referee_laws.frozen_exact), states per distinction and the gap, widths 3..12.
2. Arrangements where each knot of the weave picks one of the four not-all-equal-class knots at random (a base, not a law), on
   the cylinder of width w and 400 rows: whether any state survives, states per distinction (top Lyapunov exponent of the row
   transfer product), and the rate at which the second exponent falls behind (the random analogue of the gap).
   Control: a random gauge of NAE (every knot NAE with the literals of one random flip of the distinctions), whose counts must
   equal NAE's.
"""
from __future__ import annotations

import itertools
import json
import math

import numpy as np

from referee_laws import frozen_exact, live, top_eigs, transfer

PAIRS = {"NAE": {(0, 0, 0), (1, 1, 1)}, "p1": {(1, 0, 0), (0, 1, 1)}, "p2": {(0, 1, 0), (1, 0, 1)}, "p3": {(0, 0, 1), (1, 1, 0)}}
UP = {(0, 1): "e1", (0, 2): "e2", (1, 2): "e3"}      # up knot (v(i,j), v(i+1,j), v(i,j+1))
DOWN = {(0, 1): "e3", (0, 2): "e2", (1, 2): "e1"}    # down knot (v(i+1,j), v(i,j+1), v(i+1,j+1))


def ferro(excl, bonds):
    p = min(excl)
    return frozenset(bonds[k] for k in bonds if p[k[0]] != p[k[1]])


def type_pairs():
    out = {}
    for a, b in itertools.product(PAIRS, repeat=2):
        law = (PAIRS[a], PAIRS[b])
        rows = []
        for w in range(3, 13):
            S = live(transfer(w, law))
            fz, _ = frozen_exact(S)
            r = {"width": w, "live_rows": int(len(S)), "spectral_radius_exactly_1": fz}
            if fz is False:
                m = top_eigs(S)
                lam1 = next((x for x in m if x < m[0] * (1 - 1e-9)), None)
                r.update(per_site=float(m[0] ** (1 / w)), gap=None if not lam1 else float(math.log(m[0] / lam1, 3)))
            rows.append(r)
        out[f"{a} up, {b} down"] = {"consistent": ferro(PAIRS[a], UP) == ferro(PAIRS[b], DOWN), "rows": rows}
    return out


def strip(w, up_knots, down_knots):
    """Row transfer for one strip; up_knots[i], down_knots[i] are excluded sets at column i."""
    R = 1 << w
    b = (np.arange(R)[:, None] >> np.arange(w)[None, :]) & 1
    T = np.ones((R, R), dtype=bool)
    for i in range(w):
        x0, x1 = b[:, i][:, None], b[:, (i + 1) % w][:, None]
        y0, y1 = b[:, i][None, :], b[:, (i + 1) % w][None, :]
        for p in up_knots[i]:
            T &= ~((x0 == p[0]) & (x1 == p[1]) & (y0 == p[2]))
        for p in down_knots[i]:
            T &= ~((x1 == p[0]) & (y0 == p[1]) & (y1 == p[2]))
    return T


def flip(excl, f):
    return {tuple(s ^ g for s, g in zip(p, f)) for p in excl}


def random_run(w, rows, seed, gauge, eps=None):
    """eps None: each knot one of the four uniformly; eps a number: NAE, or with probability eps one of the three others."""
    rng = np.random.default_rng(seed)
    keys = list(PAIRS)
    g = rng.integers(0, 2, size=(w, rows + 1))
    Q = np.linalg.qr(rng.random((1 << w, 3)))[0]
    logs = np.zeros(3)
    log_count = 0.0
    v = np.ones(1 << w)
    for j in range(rows):
        if gauge:
            ups = [flip(PAIRS["NAE"], (g[i, j], g[(i + 1) % w, j], g[i, j + 1])) for i in range(w)]
            downs = [flip(PAIRS["NAE"], (g[(i + 1) % w, j], g[i, j + 1], g[(i + 1) % w, j + 1])) for i in range(w)]
        elif eps is None:
            ups = [PAIRS[keys[k]] for k in rng.integers(0, 4, size=w)]
            downs = [PAIRS[keys[k]] for k in rng.integers(0, 4, size=w)]
        else:
            pick = lambda: PAIRS[keys[rng.integers(1, 4)]] if rng.random() < eps else PAIRS["NAE"]
            ups = [pick() for _ in range(w)]
            downs = [pick() for _ in range(w)]
        T = strip(w, ups, downs).astype(float)
        v = T.T @ v
        s = v.sum()
        if s == 0:
            return {"width": w, "seed": seed, "eps": eps, "dead_at_row": j + 1}
        log_count += math.log(s)
        v /= s
        Q, Rm = np.linalg.qr(T.T @ Q)
        d = np.abs(np.diag(Rm))
        logs += np.log(np.where(d > 0, d, 1e-300))
    return {"width": w, "seed": seed, "eps": eps, "per_site": math.exp(log_count / (w * rows)), "exact_log_count": log_count,
            "lyapunov_per_row": (logs / rows).tolist(), "gap_log3": float((logs[0] - logs[1]) / rows / math.log(3))}


def nae_cylinder_log_count(w, rows):
    T = transfer(w, (PAIRS["NAE"], PAIRS["NAE"])).astype(float)
    v, lc = np.ones(1 << w), 0.0
    for _ in range(rows):
        v = T.T @ v
        s = v.sum()
        lc += math.log(s)
        v /= s
    return lc


def main():
    out = {"type_pairs": type_pairs(), "random": [], "gauge_control": []}
    for w in (4, 5, 6, 7, 8, 9):
        for seed in (1, 2, 3):
            out["random"].append(random_run(w, 400, seed, gauge=False))
        c = random_run(w, 400, 7, gauge=True)
        c["NAE_log_count"] = nae_cylinder_log_count(w, 400)
        c["equal_to_NAE"] = abs(c["exact_log_count"] - c["NAE_log_count"]) < 1e-6 * c["NAE_log_count"]
        out["gauge_control"].append(c)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
