"""Referee R1 for RING-FORMULA-20261118-001 section 4: one size past the ring of eight (rings of ten and twelve with one five-place
knot, where the proof predicts two interleaved cylinders of circumference n/2, one inert), and the ring of three.

  ../../../.venv/bin/python -B even_rings.py > referee_ring_even.json      (from this directory)

Prediction for n = 10, read off section 4 before running: the inert cylinder adds 5 junctions a round, and g = c - 5 follows the
formula with n/2 = 5 and j = 1, g(t) = g(t - 5) + g(t - 6).  For n = 12 the cylinders have circumference 6, the length section 4
calls degenerate for a ring; no prediction.
"""
import json
from multiprocessing import Pool

import referee_ring as R

RINGS = {"n = 10, one five-place knot": [5] + [4] * 9, "n = 12, one five-place knot": [5] + [4] * 11,
         "n = 3, four-place knots": [4, 4, 4], "n = 3, one five-place knot": [5, 4, 4]}


def one(item):
    name, sizes = item
    s, M = R.ring(sizes)
    G = R.grown(s, M, maxj=30000, rounds=80)
    c = G.counts()
    out = {"ring": name, "sizes": sizes, "rounds": len(c) - 1, "junctions": len(G.bits), "per-round counts (round 0 first)": c}
    if sizes[:2] == [5, 4] and len(sizes) == 10:
        g = [x - 5 for x in c[1:-1]]
        out["g = c - 5 follows g(t) = g(t - 5) + g(t - 6) from round"] = next(
            (st + 1 for st in range(6, len(g)) if all(g[t] == g[t - 5] + g[t - 6] for t in range(st, len(g)))), None)
    d = c[1:-1]
    for k in (1, 2, 3):
        d = [d[i + 1] - d[i] for i in range(len(d) - 1)]
        out[f"difference {k} (last 6)"] = d[-6:]
    return out


if __name__ == "__main__":
    with Pool(len(RINGS)) as P:
        print(json.dumps(P.map(one, list(RINGS.items())), indent=1))
