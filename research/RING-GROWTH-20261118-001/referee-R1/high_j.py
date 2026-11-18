"""Referee R1 for RING-GROWTH: the general formula checked exactly on the census rings with j = 3, 4, 5 spare distinctions."""
import json
import math
import sys
from multiprocessing import Pool

import referee_ring as R

KEYS = [([4, 4, 5, 5, 5], [0, 0, 1, 1, 1, 0, 1, 1, 0, 0]), ([4, 4, 5, 5, 5], [1, 0, 0, 1, 0, 1, 0, 1, 1, 0]),
        ([4, 5, 5, 5, 5], [0, 0, 1, 1, 1, 0, 1, 1, 0, 0]), ([5, 5, 5, 5, 5], [0, 0, 1, 1, 1, 0, 1, 1, 0, 0]),
        ([5, 5, 5, 5, 5], [0, 0, 1, 1, 1, 0, 1, 2, 0, 0])]


def one(key):
    sizes, flat = key
    s, M = R.RT.key_to(sizes, flat)
    j = R.spare(s, M)
    G = R.grown(s, M, maxj=60000)
    c = G.counts()[1:-1]
    first = None
    for st in range(5 + j, len(c)):
        if all(c[t] == sum(math.comb(j, i) * c[t - 5 - i] for i in range(j + 1)) for t in range(st, len(c))):
            first = st + 1
            break
    return {"key": [sizes, flat], "j": j, "rounds": len(c), "per-round counts": c,
            "formula holds from round (to the last)": first, "terms checked": (len(c) - first + 1) if first else 0}


if __name__ == "__main__":
    with Pool(5) as P:
        print(json.dumps(P.map(one, KEYS), indent=1))
