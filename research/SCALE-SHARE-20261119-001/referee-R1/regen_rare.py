"""The study's own samples (regenerated as in regen_study.py) that the rule puts in a rare class, dimension 3 or more: each grown
40 rounds by the referee's engine against the rule's counts, and the referee's own dimension read from its counts (the exponent
of the last rounds' growth plus one).

  ../../../.venv/bin/python -B regen_rare.py > referee_scale_regen_rare.json
"""
import json
import math
import sys
from multiprocessing import Pool

import referee_scale as R

sys.path.insert(0, str(R.ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
import referee_cluster as RC  # noqa: E402

S = R.S


def one(args):
    n, seed = args
    out = []
    for sizes, M in S.chain(n, 1000, seed, dense=seed >= 4):
        c = R.base(S.classify(sizes, M))
        if not c.startswith("dimension") or int(c.split()[1]) < 3:
            continue
        sz, e = S.edges_of(sizes, M)
        G, o = RC.my_growth(sz, e, rounds=40, maxj=400000)
        cc = G.counts()
        pred = S.Cl.series(sz, e, len(cc))
        a, b = cc[-11], cc[-1]
        slope = math.log(b / a) / math.log((len(cc) - 1) / (len(cc) - 11)) if a and b else None
        out.append({"n": n, "chain": seed, "class": c, "equal": pred[:len(cc)] == cc, "rounds": len(cc) - 1, "outcome": o,
                    "referee's dimension (local exponent + 1)": round(slope + 1, 2) if slope is not None else None})
    return out


if __name__ == "__main__":
    with Pool(12) as pool:
        res = pool.map(one, [(n, c) for n in (5, 6, 7, 8, 10, 12, 16, 20) for c in range(8)], chunksize=1)
    rows = [x for r in res for x in r]
    print(json.dumps({"rare samples": len(rows), "equal to the referee's growth": sum(r["equal"] for r in rows), "rows": rows}, indent=1))
