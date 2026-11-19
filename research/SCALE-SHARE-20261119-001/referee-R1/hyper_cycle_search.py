"""Smallest knot count at which the rule fails on a cycle of blocks through a first-round group of three: random arrangements
(the referee's CLUSTER-ALL-R1 sampler, generalized to n knots: sizes 3 to 5, n - 1 to 2n random touches within the sizes,
connected; seeds fixed), those whose map has such a cycle grown 20 rounds by the referee's engine against the rule.

  NS=6,7,8,9,10 TRIES=40000 ../../../.venv/bin/python -B hyper_cycle_search.py > referee_scale_hyper_cycle_search.json
"""
import json
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

import referee_scale as R
import scan_cycles as SC

sys.path.insert(0, str(R.ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
import referee_cluster as RC  # noqa: E402

S = R.S


def sample(n, seed):
    rng = random.Random(seed)
    while True:
        sizes = [rng.randint(3, 5) for _ in range(n)]
        deg = [0] * n
        M = [[0] * n for _ in range(n)]
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for _ in range(rng.randint(n - 1, 2 * n)):
            i, j = rng.choice(pairs)
            if deg[i] < sizes[i] and deg[j] < sizes[j]:
                M[i][j] += 1
                M[j][i] += 1
                deg[i] += 1
                deg[j] += 1
        if RC.RT.connected(n, M):
            return sizes, [(i, j) for i in range(n) for j in range(i + 1, n) for _ in range(M[i][j])]


def job(args):
    n, lo, hi = args
    flagged = []
    for seed in range(lo, hi):
        sz, e = sample(n, 1000000 * n + seed)
        A = S.Cl.analyse(sz, e)
        if not A.get("scope") or A.get("stall") or not SC.hyper_cycle(A):
            continue
        r = RC.compare(("x", sz, e))
        flagged.append({"seed": 1000000 * n + seed, "verdict": r["verdict"], "first difference": r.get("first difference")})
    return n, flagged


if __name__ == "__main__":
    ns = [int(x) for x in os.environ.get("NS", "6,7,8,9,10").split(",")]
    T = int(os.environ.get("TRIES", "40000"))
    W = int(os.environ.get("WORKERS", "12"))
    step = T // W
    with Pool(W) as pool:
        res = pool.map(job, [(n, a, a + step) for n in ns for a in range(0, T, step)], chunksize=1)
    out = {}
    for n in ns:
        f = [x for nn, fl in res if nn == n for x in fl]
        out[n] = {"arrangements tried": T, "in scope with a cycle of blocks through a hyperedge": len(f),
                  "verdicts": dict(Counter(x["verdict"] for x in f)), "misses": [x for x in f if x["verdict"] == "miss"][:5]}
    print(json.dumps(out, indent=1))
