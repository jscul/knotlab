"""Referee R1 for DISTANCE-ORDER-20261117-001: the weave under the weakest ordinal reading of "between".

  .venv/bin/python -B referee_ordinal.py > referee_ordinal.json

Read tau = -log_3 |corr| (corr from referee_order.weave's float transfer matrix) as a closeness, and call w ordinally between u
and v when tau(u, w) < tau(u, v) and tau(w, v) < tau(u, v). The ordinal gaps of the start v(0,0) are the v with nothing
ordinally between them and the start. Reported with their steps apart and whether they share the start's class
((i + 2j) mod 3), against the six knot-neighbours (one step apart).
"""
import json
import math

import numpy as np

import referee_order as O


def corr_table(L):
    R = 1 << L
    a = np.arange(R)
    bit = lambda x, i: (x >> (i % L)) & 1
    T = np.ones((R, R), dtype=bool)
    for i in range(L):
        ai, ai1 = bit(a, i)[:, None], bit(a, i + 1)[:, None]
        bi, bi1 = bit(a, i)[None, :], bit(a, i + 1)[None, :]
        T &= ~((ai == ai1) & (ai1 == bi))
        T &= ~((ai1 == bi) & (bi == bi1))
    T = T.astype(np.float64)
    P = [np.eye(R)]
    for _ in range(L):
        P.append(P[-1] @ T)
    N = np.trace(P[L])
    spin = 1.0 - 2.0 * ((a[:, None] >> np.arange(L)[None, :]) & 1)
    tau = {}
    for r in range(L):
        col = ((spin[:, 0][:, None] * P[r]) * P[L - r].T).sum(axis=0)
        for c in range(L):
            v = float((col * spin[:, c]).sum() / N)
            tau[(c, r)] = 0.0 if (c, r) == (0, 0) else -math.log(abs(v), 3)
    return tau


def steps(L, c, r):
    best = None
    for x in (c - L, c, c + L):
        for y in (r - L, r, r + L):
            s = abs(x) + abs(y) if x * y >= 0 else max(abs(x), abs(y))
            best = s if best is None else min(best, s)
    return best


out = {}
for L in (6, 9, 12):
    tau = corr_table(L)
    keys = [k for k in tau if k != (0, 0)]
    gaps = []
    for k in keys:
        if not any(w != k and tau[w] < tau[k] - 1e-9 and tau[((k[0] - w[0]) % L, (k[1] - w[1]) % L)] < tau[k] - 1e-9
                   for w in keys):
            gaps.append(k)
    out[L] = {"ordinal_gaps": len(gaps),
              "by_steps_and_class": sorted({(steps(L, *k), (k[0] + 2 * k[1]) % 3 == 0, round(tau[k], 3)) for k in gaps}),
              "knot_neighbours_all_gaps": all(((dx % L, dy % L) in gaps) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)])}
    print(L, out[L], flush=True)
print(json.dumps(out, indent=1, default=str))
