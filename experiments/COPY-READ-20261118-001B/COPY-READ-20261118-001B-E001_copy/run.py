"""COPY-READ-20261118-001B-E001: the frozen run.  SEEDK from every bracketing of 5, 6 and 7 and every third of 8 (105 starts), one
seed each, to n = 30; after the switch every fill that makes a new crossing is labelled and given its pictures.
Run: python -B run.py [--procs 8]."""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import copylib as C  # noqa: E402

M = C.M
OUT = os.path.join(C.ROOT, "artifacts", "COPY-READ-20261118-001B", "COPY-READ-20261118-001B-E001_copy")
NMAX = 30


def jobs():
    J = []
    for n0 in (5, 6, 7, 8):
        for i, ks in enumerate(M.bracketings(0, n0 - 1)):
            if n0 == 8 and i % 3:
                continue
            J.append((n0, i, ks, 80_000_000 + len(J)))
    return J


def job(arg):
    n0, i, ks, seed = arg
    t = time.time()
    rows, refused, n_refused, verified = C.run(ks, n0, NMAX, seed)
    return {"n0": n0, "index": i, "knots": ks, "seed": seed, "absorbing": rows, "refused": refused, "n_refused": n_refused,
            "verified": verified, "seconds": round(time.time() - t, 1)}


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
