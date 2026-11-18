"""FAR-SIGN-20261118-001B-E001: the frozen run.

Part S: SEEDK from every bracketing of 5, 6 and 7 and the bracketings of 8 at indices 2, 5, 8, ... (105 starts; COPY-CLASS took 0, 3,
6, ... and its referee 1, 4, 7, ...), fresh seeds, to n = 32; and from random bracketings (recursive random split points) of lines of
18 (30 starts) to n = 40, 22 (20) to n = 44 and 26 (10) to n = 48.  Every crossing-making knot-local
extension after the switch is kept with SEED's verdict and the readings of each knot set (signlib.analyse).
Part A (the ablation, no prediction): the bracketings of 5 and 6, at the first three bases after the switch with n <= 14, every fill
with knots on any pairs.
Run: python -B run.py [--procs 8]; writes artifacts/.../part_S.json.gz and part_A.json.gz.
"""
import argparse
import gzip
import json
import multiprocessing as mp
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import signlib as SL  # noqa: E402

M = SL.M
OUT = os.path.join(SL.ROOT, "artifacts", "FAR-SIGN-20261118-001B", "FAR-SIGN-20261118-001B-E001_sign")


def jobs():
    J = []
    for n0 in (5, 6, 7, 8):
        for i, ks in enumerate(M.bracketings(0, n0 - 1)):
            if n0 == 8 and i % 3 != 2:
                continue
            J.append(("S", n0, i, ks, 32, 70_000_000 + len(J)))
    rng = random.Random(20261118)
    for m, cnt, nmax in ((18, 30, 40), (22, 20, 44), (26, 10, 48)):
        for i in range(cnt):
            J.append(("S", m, i, SL.random_bracketing(m - 1, rng), nmax, 70_000_000 + len(J)))
    for n0 in (5, 6):
        for i, ks in enumerate(M.bracketings(0, n0 - 1)):
            J.append(("A", n0, i, ks, 16, 71_000_000 + len(J)))
    return J


def clean(x):
    if isinstance(x, (set, frozenset)):
        return sorted(clean(v) for v in x)
    if isinstance(x, tuple):
        return [clean(v) for v in x]
    if isinstance(x, list):
        return [clean(v) for v in x]
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    return x


def job(arg):
    part, n0, i, ks, nmax, seed = arg
    t = time.time()
    if part == "S":
        rows, _ = SL.run(ks, n0, nmax, seed, closure=True)
        return {"part": "S", "n0": n0, "index": i, "knots": ks, "seed": seed, "nmax": nmax, "rows": clean(rows),
                "seconds": round(time.time() - t, 1)}
    _, abl = SL.run(ks, n0, nmax, seed, ablate_steps=3, ablate_nmax=14, closure=False)
    return {"part": "A", "n0": n0, "index": i, "knots": ks, "seed": seed, "rows": clean(abl), "seconds": round(time.time() - t, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    J = jobs()
    J.sort(key=lambda j: -j[1])                     # longest lines first
    t0 = time.time()
    res = {"S": [], "A": []}
    with mp.Pool(a.procs) as pool:
        for k, r in enumerate(pool.imap_unordered(job, J, chunksize=1)):
            res[r["part"]].append(r)
            if (k + 1) % 25 == 0:
                print(f"{k + 1} of {len(J)} {round(time.time() - t0)} s", flush=True)
    for part in ("S", "A"):
        res[part].sort(key=lambda r: (r["n0"], r["index"]))
        with gzip.open(os.path.join(OUT, f"part_{part}.json.gz"), "wt") as f:
            json.dump(res[part], f)
    print("done", round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
