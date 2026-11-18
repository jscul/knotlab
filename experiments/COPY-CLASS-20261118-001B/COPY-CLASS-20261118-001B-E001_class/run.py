"""COPY-CLASS-20261118-001B-E001: the frozen run.  SEEDK from every bracketing of 5, 6 and 7 and every third of 8 (105 starts) and
from 30 random bracketings of the line of 12 (recursive random split points), one seed each, to n = 30.  Every crossing-making knot
set after the switch is scored; the output keeps tallies and every disagreement in full.  Run: python -B run.py [--procs 8]."""
import argparse
import json
import multiprocessing as mp
import os
import random
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import classlib as C  # noqa: E402

M = C.M
OUT = os.path.join(C.ROOT, "artifacts", "COPY-CLASS-20261118-001B", "COPY-CLASS-20261118-001B-E001_class")
NMAX = 30


def jobs():
    J = []
    for n0 in (5, 6, 7, 8):
        for i, ks in enumerate(M.bracketings(0, n0 - 1)):
            if n0 == 8 and i % 3:
                continue
            J.append((n0, i, ks, 90_000_000 + len(J)))
    rng = random.Random(2026)
    for i in range(30):
        J.append((12, i, C.random_bracketing(11, rng), 90_000_000 + len(J)))
    return J


def job(arg):
    n0, i, ks, seed = arg
    t = time.time()
    rows = C.run(ks, n0, NMAX, seed)
    # extension level: SEED accepts an extension; a rule accepts it if it accepts some knot set of it
    ext = {}
    for r in rows:
        key = (r["n"], r["ext"][0], r["ext"][1])
        e = ext.setdefault(key, {"seed": r["seed"], "cr": False, "crany": False, "copy_class": False, "reasons": Counter(),
                                 "local_equals_all": True, "model_crossers": 0, "splits": r.get("splits", 0)})
        e["cr"] |= r["cr"]
        e["crany"] |= r["crany"]
        e["copy_class"] |= r["copy_class"]
        e["local_equals_all"] &= bool(r["local_equals_all"]) if r["local_equals_all"] is not None else True
        if r.get("reason"):
            e["reasons"][r["reason"]] += 1
        e["model_crossers"] = max(e["model_crossers"], r.get("model_crossers", 0))
    tally = Counter()
    disagreements = []
    for key, e in ext.items():
        tally[f"seed={int(e['seed'])} cr={int(e['cr'])} crany={int(e['crany'])} class={int(e['copy_class'])}"] += 1
        if not e["local_equals_all"]:
            tally["local_not_all"] += 1
        if e["seed"] != e["cr"] or e["seed"] != e["crany"]:
            disagreements.append({"n": key[0], "ext": [key[1], key[2]], **{k: (dict(v) if isinstance(v, Counter) else v)
                                                                            for k, v in e.items()}})
        if not e["seed"]:
            top = e["reasons"].most_common(1)
            tally["refusal: " + (top[0][0] if top else "none")] += 1
    absorbing = [{"n": k[0], "model_crossers": e["model_crossers"], "splits": e["splits"]} for k, e in ext.items() if e["seed"]]
    return {"n0": n0, "index": i, "knots": ks, "seed": seed, "knot_sets": len(rows), "extensions": len(ext), "tally": dict(tally),
            "disagreements": disagreements, "absorbing": absorbing, "seconds": round(time.time() - t, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    J = jobs()
    t0 = time.time()
    res = []
    with mp.Pool(a.procs) as pool:
        for k, r in enumerate(pool.imap_unordered(job, J, chunksize=1)):
            res.append(r)
            if (k + 1) % 15 == 0:
                print(k + 1, "of", len(J), round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: (r["n0"], r["index"]))
    json.dump({"jobs": len(res), "seconds": round(time.time() - t0, 1), "results": res}, open(os.path.join(OUT, "results.json"), "w"))
    print("done", len(res), "in", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
