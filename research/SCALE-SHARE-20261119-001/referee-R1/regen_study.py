"""Regenerate the study's own samples (scale.chain with the job's seeds and starts, run read-only only to regenerate the study's
data; checked against the classes recorded in runs/scale-share), then find every sample whose map has a cycle of blocks through
a first-round group of three, and every sample the rule calls a ring, and grow each with the referee's own engine (FIRST-KNOT-R1,
25 rounds) against the rule.

  ../../../.venv/bin/python -B regen_study.py > referee_scale_regen.json
"""
import json
import sys
from collections import Counter
from multiprocessing import Pool

import referee_scale as R
import scan_cycles as SC

sys.path.insert(0, str(R.ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
import referee_cluster as RC  # noqa: E402

S = R.S


def recorded():
    rec = {}
    for line in open(R.RUN):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("S-"):
            rec[(int(r["case"][3:5]), int(r["case"][-1]))] = [x["class"] for x in r["result"]["samples"]]
    return rec


def one(args):
    n, seed, rec = args
    samp = S.chain(n, 1000, seed, dense=seed >= 4)
    out = {"n": n, "chain": seed, "classes equal the record": None, "flagged": [], "rings": []}
    cls = []
    for sizes, M in samp:
        c = S.classify(sizes, M)
        cls.append(c)
        sz, e = S.edges_of(sizes, M)
        A = S.Cl.analyse(sz, e)
        flag = bool(A.get("scope")) and not A.get("stall") and SC.hyper_cycle(A)
        ring = R.base(c).startswith("ring")
        if flag or ring:
            G, o = RC.my_growth(sz, e, rounds=25, maxj=60000)
            cc = G.counts()
            pred = S.Cl.series(sz, e, len(cc))
            row = {"class": R.base(c), "equal for 25 rounds": pred[:len(cc)] == cc, "mine": [o, cc[:10]], "rule": pred[:10],
                   "sizes": sz, "touches": e}
            (out["flagged"] if flag else out["rings"]).append(row)
    out["classes equal the record"] = cls == rec
    return out


if __name__ == "__main__":
    rec = recorded()
    jobs = sorted(rec, key=lambda k: -k[0])
    with Pool(12) as pool:
        res = pool.map(one, [(n, c, rec[(n, c)]) for n, c in jobs], chunksize=1)
    out = {"chains regenerated": len(res), "chains whose classes equal the record": sum(r["classes equal the record"] for r in res)}
    for n in sorted({r["n"] for r in res}):
        rs = [r for r in res if r["n"] == n]
        fl = [x for r in rs for x in r["flagged"]]
        rg = [x for r in rs for x in r["rings"]]
        out[n] = {"samples with the cycle-through-hyperedge shape": len(fl),
                  "... their rule classes": dict(Counter(x["class"] for x in fl)),
                  "... equal to the referee's growth": sum(x["equal for 25 rounds"] for x in fl),
                  "samples the rule calls a ring": len(rg), "... equal to the referee's growth": sum(x["equal for 25 rounds"] for x in rg),
                  "details": fl + rg}
    print(json.dumps(out, indent=1, default=str))
