"""Referee R1 for RING-PAIR-20261119-001: three of the 17 fresh starts grown by the referee's own lean engine (JOIN-GROWTH-R1's
lean.py), with bare sizes computed by the referee (max(3, shared + round-1 demand) plus listed surplus; in scope every round-1
group is a pair, so the demand is the number of candidates), against the referee's own cover-model count.

  ../../../.venv/bin/python -B regrow_fresh.py > referee_pair_regrow.json      (from this directory)
"""
import json
import os
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "JOIN-GROWTH-20261118-001/referee-R1"))
sys.path.insert(0, str(HERE.parents[2] / "research/TOUCH-CENSUS-20261118-001/referee-R1"))
import referee_pair as RP  # noqa: E402
import lean as L  # noqa: E402
import referee_touch as RT  # noqa: E402

PICK = ["F14-n9-control", "F16-ring8-four-lone", "F01-5-5-P2", "F10-theta-P4"]


def one(name):
    n, edges, surplus = RP.FRESH[name]
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    shared = [len(nb[k]) for k in range(n)]
    demand = [sum(1 for j in range(n) if j != k and nb[k] & nb[j]) for k in range(n)]
    sizes = [max(3, shared[k] + demand[k]) + surplus.get(k, 0) for k in range(n)]
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = L.Lean(RT.stars(sizes, M))
    cap = int(os.environ.get("MAXJ", "150000"))
    for _ in range(80):
        if G.step() != "ok" or len(G.bits) > cap:
            break
    c = G.counts()
    rooted, dissym, tot, nv, B = RP.orbit_counts(n, edges, surplus, len(c) + 1)
    return {"start": name, "sizes": sizes, "rounds": len(c) - 1, "junctions": len(G.bits), "zero demand": G.zero_demand,
            "referee growth equals the referee's model on every round": [int(x) for x in rooted[:len(c)]] == c, "counts": c}


if __name__ == "__main__":
    with Pool(len(PICK)) as pool:
        print(json.dumps(pool.map(one, PICK), indent=1))
