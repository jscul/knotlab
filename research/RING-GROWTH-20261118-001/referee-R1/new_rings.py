"""Referee R1 for RING-FORMULA-20261118-001: odd rings the study did not grow, grown by the referee's engine, against
c(t) = sum_i C(j, i) c(t - n - i); and the ring of five five-place knots against 5 F(t + 2) in every round."""
import json
import math
from multiprocessing import Pool

import referee_ring as R

NEW = {"n = 11, j = 1": [5] + [4] * 10, "n = 9, j = 3": [5, 4, 4, 5, 4, 4, 5, 4, 4], "n = 7, j = 4 (a six-place knot)": [6, 4, 5, 4, 4, 5, 4],
       "n = 5, j = 4 (two six-place knots)": [6, 4, 6, 4, 4], "n = 9, j = 9 (a spare at every knot)": [5] * 9}


def one(item):
    name, sizes = item
    s, M = R.ring(sizes)
    n, j = len(sizes), R.spare(s, M)
    G = R.grown(s, M, maxj=40000, rounds=300)
    c = G.counts()[1:-1]
    first = None
    for st in range(n + j, len(c)):
        if all(c[t] == sum(math.comb(j, i) * c[t - n - i] for i in range(j + 1)) for t in range(st, len(c))):
            first = st + 1
            break
    fib = None
    if j == n:
        F = [0, 1]
        while len(F) < len(c) + 5:
            F.append(F[-1] + F[-2])
        fib = all(G.counts()[t] == n * F[t + 2] for t in range(len(c) + 1))
    return {"ring": name, "sizes": sizes, "n": n, "j": j, "rounds": len(c), "junctions": len(G.bits),
            "predicted rate": R.predicted_rate(n, j), "last ratio": round(c[-1] / c[-2], 4),
            "formula holds from round (to the last)": first, "terms checked": (len(c) - first + 1) if first else 0,
            "n F(t + 2) in every round": fib, "per-round counts (first 12)": c[:12]}


if __name__ == "__main__":
    with Pool(5) as P:
        res = P.map(one, list(NEW.items()))
    print(json.dumps(res, indent=1))
