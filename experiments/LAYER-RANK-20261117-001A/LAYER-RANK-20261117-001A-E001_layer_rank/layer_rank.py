"""Strahler numbers (untangling phases) of layered random monotone circuits.

Layer 0: w inputs, each true with chance 1/2 (rank 0).  Every gate of layer
L reads two distinct uniformly random gates of layer L - 1 and is AND or OR
with chance 1/2.  The rank of a true gate is the least Strahler number of its
derivation, as in SEQUENTIAL-WALL-20261116-001 (atoms with one held helper for
OR): OR takes the least of max(rank, 1) over its true inputs; AND of true
inputs of ranks i, j takes max(i, j) if i != j and i + 1 if i == j.

meanfield(): the exact infinite-width recursion for q_L(r) = P(true, rank r).
simulate(): exact finite-width circuits, layer by layer.
"""

import numpy as np


def meanfield(L_max, checkpoints, ws=(1024, 4096, 16384)):
    a = np.zeros(4)
    a[0] = 0.5
    out = {}
    cps = set(checkpoints)
    for L in range(1, L_max + 1):
        R = len(a)
        if a[-1] > 1e-300 or a[-2] > 1e-300:
            a = np.concatenate([a, np.zeros(R)])
            R = len(a)
        p = a.sum()
        A = np.concatenate([[0.0], np.cumsum(a)[:-1]])  # sum_{s<r} a(s)
        AND = 2 * a * A
        AND[1:] += a[:-1] ** 2
        b = a.copy()
        b[1] += b[0]
        b[0] = 0.0
        tail = b.sum() - np.cumsum(b)  # sum_{s>r} b(s)
        OR = b ** 2 + 2 * b * tail + 2 * b * (1 - p)
        a = 0.5 * AND + 0.5 * OR
        if L in cps:
            pt = a.sum()
            f = a / pt
            r = np.arange(len(f))
            mu = float((f * r).sum())
            sd = float(np.sqrt((f * (r - mu) ** 2).sum()))
            cdf = np.cumsum(f)
            rec = {"p": float(pt), "mean": mu, "sd": sd, "tie": float((f ** 2).sum()),
                   "mode": int(np.argmax(f))}
            for w in ws:
                # rank r with P(rank > r) < 1 / (w p): the largest of about w p true gates
                rec[f"q_w{w}"] = int(np.searchsorted(cdf, 1 - 1.0 / (w * pt)))
            out[L] = rec
    return out


def simulate(w, d, rng, checkpoints):
    true = rng.random(w) < 0.5
    rank = np.where(true, 0, -1).astype(np.int64)
    out = {}
    cps = set(checkpoints)
    BIG = 1 << 40
    for L in range(1, d + 1):
        x = rng.integers(0, w, w)
        y = rng.integers(0, w - 1, w)
        y += y >= x
        is_and = rng.random(w) < 0.5
        tx, ty = true[x], true[y]
        rx, ry = rank[x], rank[y]
        t_and = tx & ty
        hi = np.maximum(rx, ry)
        r_and = np.where(rx == ry, rx + 1, hi)
        t_or = tx | ty
        ox = np.where(tx, np.maximum(rx, 1), BIG)
        oy = np.where(ty, np.maximum(ry, 1), BIG)
        r_or = np.minimum(ox, oy)
        true = np.where(is_and, t_and, t_or)
        rank = np.where(true, np.where(is_and, r_and, r_or), -1)
        if L in cps:
            rt = rank[true]
            out[L] = {"p": float(true.mean()), "alive": bool(true.any() and not true.all()),
                      "max": int(rt.max()) if len(rt) else -1,
                      "mean": float(rt.mean()) if len(rt) else -1.0,
                      "sd": float(rt.std()) if len(rt) else -1.0}
    return out
