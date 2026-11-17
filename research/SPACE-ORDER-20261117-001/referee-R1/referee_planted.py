"""Referee R1 for SPACE-ORDER-20261117-001: the planted not-all-equal process, checked.

  .venv/bin/python -B referee_planted.py > referee_planted.json

The study plants by 30 zero-energy sweeps (random single flips that keep every knot not-all-equal) from the three-class state.
Zero-energy flips keep the large-scale shape of the state's height function, which relaxes only slowly, so 30 sweeps may leave
the three-class order of the start in place at large L. This measures, with the referee's own dynamics:
- the three-class order parameter |sum_v s_v w^c(v)| / n (s = 2x - 1, w = exp(2 pi i / 3), c = (i + 2j) mod 3) of the study's
  own 30-sweep states, against states after many more sweeps;
- the free share (a distinction that can flip without making a knot all-equal);
- whether the study's not-all-equal readings (k*/n, R*, P*, avalanche) change when the planted state is mixed longer.

The referee's dynamics: the three classes are never co-knotted, so one sweep updates each class at once, flipping each allowed
distinction with probability 1/2 (the uniform measure on the reachable not-all-equal states is stationary for it).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

import referee_core as C

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = ROOT / "experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases"


def classes(L):
    i = np.arange(L * L) % L
    j = np.arange(L * L) // L
    return (i + 2 * j) % 3


def order_param(state, L):
    s = 2.0 * state - 1.0
    w = np.exp(2j * np.pi * classes(L) / 3)
    return float(abs((s * w).sum()) / len(s))


def blocked(K, x):
    """b[v] = True when flipping v would make some knot all-equal."""
    b = np.zeros(len(x), bool)
    for p in range(3):
        v, u, w = K[:, p], K[:, (p + 1) % 3], K[:, (p + 2) % 3]
        hit = (x[u] == x[w]) & (x[u] == 1 - x[v])
        b[v[hit]] = True
    return b


def sweeps(K, x, L, t, rng):
    x = x.copy()
    cl = classes(L)
    for _ in range(t):
        for c in range(3):
            b = blocked(K, x)
            flip = (cl == c) & ~b & (rng.random(len(x)) < 0.5)
            x[flip] ^= 1
    return x


def nae_reading(K, state, order, L):
    n = L * L
    at = C.Atoms(n, C.nae_atoms(K, state))
    nb = C.neighbours(K, n)
    k, _ = at.k_star(order)
    r1 = C.reading(at, nb, order[:k])
    r0 = C.reading(at, nb, order[:max(1, k - 1)])
    return {"k_star_frac": k / n, "R": r1["R"], "P": r1["P"], "avalanche": (r1["set"] - r0["set"]) / n}


def main():
    spec = importlib.util.spec_from_file_location("so_job", E / "job.py")
    job = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(job)
    W = job.W
    out = {}
    for L, cnt, long_t in ((48, 4, 3000), (96, 4, 3000), (192, 3, 3000)):
        rows = []
        for s in range(cnt):
            rng = np.random.default_rng(job.seed_of(f"nae:W:{L}:{s}"))
            K = W.weave(L)
            st30 = W.zero_energy_sweeps(K, W.three_class_state(L), job.SWEEPS, rng)  # the study's planted state
            order = rng.permutation(L * L)
            myrng = np.random.default_rng(1000 + 17 * s + L)
            three = W.three_class_state(L).astype(np.int8)
            mine = {t: sweeps(K, three, L, t, myrng) for t in (30, 300)}
            mine[long_t] = sweeps(K, mine[300], L, long_t - 300, myrng)
            for x in [st30] + list(mine.values()):
                assert C.nae_atoms(K, x) is not None
            rows.append({
                "order_param": {"three_class_start": order_param(three, L), "study_30": order_param(st30, L),
                                **{f"referee_{t}": order_param(x, L) for t, x in mine.items()}},
                "free_share": {"study_30": float(1 - blocked(K, st30).mean()),
                               **{f"referee_{t}": float(1 - blocked(K, x).mean()) for t, x in mine.items()}},
                "reading": {"study_30": nae_reading(K, st30, order, L),
                            f"referee_{long_t}": nae_reading(K, mine[long_t], order, L)}})
        out[L] = rows
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
