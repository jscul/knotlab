"""KNOT-SWITCH-20261118-001B-E001: the frozen runs.  Part S1: KF3, NN, NN2 and SEEDK from every bracketing of 5, 6 and 7
distinctions and 44 of the 132 of 8 (every third, in enumeration order), one seed each; SEEDK to n = 40, the others to n = 30.
Run: python -B run.py --part S1 [--procs 12], then --merge."""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import knotlib as K  # noqa: E402

M = K.M
OUT = os.path.join(K.ROOT, "artifacts", "KNOT-SWITCH-20261118-001B", "KNOT-SWITCH-20261118-001B-E001_switch")
NMAX = {"SEEDK": 40, "KF3": 30, "NN": 30, "NN2": 30}


def jobs():
    J = []
    for rule in ("SEEDK", "KF3", "NN", "NN2"):
        for n0 in (5, 6, 7, 8):
            for i, ks in enumerate(M.bracketings(0, n0 - 1)):
                if n0 == 8 and i % 3:
                    continue
                J.append((rule, n0, i, ks, 50_000_000 + len(J)))
    return J


def job(arg):
    rule, n0, i, ks, seed = arg
    t = time.time()
    tr = K.grow(ks, n0, NMAX[rule], rule, seed)
    return {"rule": rule, "n0": n0, "index": i, "knots": ks, "seed": seed, "trace": tr, "seconds": round(time.time() - t, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="S1")
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.merge:
        r = json.load(open(os.path.join(OUT, "part_S1.json")))
        json.dump({"S1": r}, open(os.path.join(OUT, "results.json"), "w"))
        print("merged")
        return
    J = jobs()
    t0 = time.time()
    res = []
    with mp.Pool(a.procs) as pool:
        for k, r in enumerate(pool.imap_unordered(job, J, chunksize=1)):
            res.append(r)
            if (k + 1) % 25 == 0:
                print("S1", k + 1, "of", len(J), round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: (r["rule"], r["n0"], r["index"]))
    json.dump({"part": "S1", "jobs": len(res), "seconds": round(time.time() - t0, 1), "results": res},
              open(os.path.join(OUT, "part_S1.json"), "w"))
    print("S1 done", len(res), "in", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
