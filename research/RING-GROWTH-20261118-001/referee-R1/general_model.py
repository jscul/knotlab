"""Referee R1 for RING-FORMULA-20261118-001: the outline step (the grown pattern is the (v, S) model with j spares), checked
round by round on the joint histogram of (parents, fresh), not only on counts, for rings with several spares, six-place knots,
and one size past the study: a seven-place knot and a ring of six-place knots. Also the formula on the two rings past the study.

  ../../../.venv/bin/python -B general_model.py > referee_ring_general.json      (from this directory)

Model, written from RING-FORMULA's section 1: positions v = (a, b), h = a + b >= 0, modulo (n, -n), a in 0..n-1; ring knot R_i at
a = i (n + 1)/2 mod n with sizes[i] - 4 spares; spare x of R_i has lifts (a_x + n k, -a_x - n k), k in Z; junctions (v, S), S a set
of lifts below v, round h + |S|; parents |S| plus one for each of (a - 1, b), (a, b - 1) that S is still below (h >= 1); demand
2 + m(v) - |S|.
"""
import itertools
import json
import math
from collections import Counter
from multiprocessing import Pool

import referee_ring as R

RINGS = {"n = 5, two adjacent spares": [5, 5, 4, 4, 4],
         "n = 5, a six-place knot": [6, 4, 4, 4, 4],
         "n = 5, two six-place knots": [6, 4, 6, 4, 4],
         "n = 5, five five-place knots": [5, 5, 5, 5, 5],
         "n = 7, j = 4 (a six-place knot)": [6, 4, 5, 4, 4, 5, 4],
         "n = 9, j = 3": [5, 4, 4, 5, 4, 4, 5, 4, 4],
         "n = 11, j = 1": [5] + [4] * 10,
         "past the study: a seven-place knot (n = 5, j = 3)": [7, 4, 4, 4, 4],
         "past the study: five six-place knots (n = 5, j = 10)": [6, 6, 6, 6, 6]}


def model_histograms(sizes, T):
    n = len(sizes)
    spares = [(i * (n + 1) // 2) % n for i in range(n) for _ in range(sizes[i] - 4)]
    K = T // n + 3

    def lifts(a, b):
        return frozenset((x, k) for x, a0 in enumerate(spares) for k in range(-K, K + 1) if a0 + n * k <= a and -a0 - n * k <= b)
    out = {}
    for h in range(0, T + 1):
        for a in range(n):
            b = h - a
            L = sorted(lifts(a, b))
            down = (lifts(a - 1, b), lifts(a, b - 1)) if h >= 1 else (frozenset(), frozenset())
            for s in range(0, min(len(L), T - h) + 1):
                t = h + s
                if t == 0:
                    continue
                for S in itertools.combinations(L, s):
                    Sset = set(S)
                    par = s + (h >= 1 and Sset <= down[0]) + (h >= 1 and Sset <= down[1])
                    out.setdefault(t, Counter())[(par, 2 + len(L) - s)] += 1
    return out


def one(item):
    name, sizes = item
    s, M = R.ring(sizes)
    n, j = len(sizes), R.spare(s, M)
    G = R.grown(s, M, maxj=40000, rounds=300)
    T = max(G.round) - 1
    gh = R.growth_histograms(G)
    mh = model_histograms(sizes, T)
    bad = [t for t in range(1, T + 1) if gh.get(t, Counter()) != mh.get(t, Counter())]
    c = [sum(gh[t].values()) for t in range(1, T + 1)]
    first = None
    for st in range(n + j, len(c)):
        if all(c[t] == sum(math.comb(j, i) * c[t - n - i] for i in range(j + 1)) for t in range(st, len(c))):
            first = st + 1
            break
    shapes = sorted(set(k for t in gh for k in gh[t]))
    return {"ring": name, "sizes": sizes, "n": n, "j": j, "rounds compared": T, "junctions": len(G.bits),
            "(parents, fresh) histograms equal every round": not bad, "rounds that differ": bad,
            "(parents, fresh) shapes seen": [list(x) for x in shapes],
            "predicted rate": R.predicted_rate(n, j), "last ratio": round(c[-1] / c[-2], 4),
            "formula holds from round (to the last)": first, "terms checked": (len(c) - first + 1) if first else 0,
            "per-round counts": c}


if __name__ == "__main__":
    with Pool(len(RINGS)) as P:
        res = P.map(one, list(RINGS.items()))
    print(json.dumps(res, indent=1))
