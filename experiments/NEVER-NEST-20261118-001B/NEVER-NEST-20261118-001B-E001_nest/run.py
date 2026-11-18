"""NEVER-NEST-20261118-001B-E001: the frozen runs.  Parts:

E1  exact distributions of NN from every bracketing of 5 to 8 distinctions to n = 12
E2  exact distributions of NN2 from every bracketing of 5 and 6 distinctions to n = 10
R1  labelled runs of NN (with the line tracked), NN2, KF3 and SUB to n = 40 from every bracketing of 5 to 8 (two seeds for
    5 to 7, one for 8)
R2  NNF from the line of 5 to 8 and from the 2 x 2 pattern; CC from the 2 x 2 pattern, from the line of 5 to 8 with one fill
    (a uniform triple, KF3's first step) and from the bare line of 5 (10 runs); 50 runs each to n = 40; the class law of
    LOCAL-ROOM-20261118-001 (its frozen code) from the 2 x 2 pattern, 50 runs to n = 40

Run: python -B run.py --part E1|E2|R1|R2 [--procs 8], then --merge.
"""
import argparse
import json
import multiprocessing as mp
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nnlib as L  # noqa: E402

M = L.M
ROOT = L.ROOT
OUT = os.path.join(ROOT, "artifacts", "NEVER-NEST-20261118-001B", "NEVER-NEST-20261118-001B-E001_nest")
NMAX_EXACT = {"E1": 12, "E2": 10}
NMAX = 40


def starts(n0s):
    return [(n0, i, ks) for n0 in n0s for i, ks in enumerate(M.bracketings(0, n0 - 1))]


def job_exact(arg):
    part, rule, n0, i, ks = arg
    t = time.time()
    lv = L.exact(ks, n0, NMAX_EXACT[part], rule)
    return {"n0": n0, "index": i, "knots": ks, "rule": rule, "levels": L.fr(lv), "seconds": round(time.time() - t, 1)}


def job_run(arg):
    rule, n0, i, ks, seed = arg
    t = time.time()
    tr = L.grow(ks, n0, NMAX, rule, seed, track_line=(rule == "NN"))
    return {"n0": n0, "index": i, "knots": ks, "rule": rule, "seed": seed, "trace": tr, "seconds": round(time.time() - t, 1)}


def job_free(arg):
    rule, start, seed = arg
    t = time.time()
    if start == "2x2":
        S, n = L.square_states(), 4
    elif start.startswith("line"):
        n = int(start[4:])
        S = L.line_states(n)
    else:                                   # "fill<n0>": the line of n0 with one uniformly chosen fill of a triple
        n = int(start[4:])
        S = L.line_states(n)
        z = sorted(L.free_zero(S, n))
        S = M.apply(S, n, *random.Random(seed).choice(z))
        n += 1
    tr = L.free_grow(S, n, NMAX, seed, rule=rule)
    return {"rule": rule, "start": start, "seed": seed, "trace": tr, "seconds": round(time.time() - t, 1)}


def job_class(seed):
    sys.path.append(os.path.join(ROOT, "experiments", "LOCAL-ROOM-20261118-001B", "LOCAL-ROOM-20261118-001B-E001_local"))
    import locallib  # noqa: E402
    t = time.time()
    states, n, tr = locallib.class_grow(NMAX, seed)
    return {"rule": "class", "start": "2x2", "seed": seed, "trace": tr, "seconds": round(time.time() - t, 1)}


def seed_of(rule, n0, i, k):
    return 1_000_000 * ("NN", "NN2", "KF3", "SUB").index(rule) + 10_000 * n0 + 10 * i + k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.merge:
        merged = {}
        for p in ("E1", "E2", "R1", "R2"):
            f = os.path.join(OUT, f"part_{p}.json")
            if os.path.exists(f):
                merged[p] = json.load(open(f))
        json.dump(merged, open(os.path.join(OUT, "results.json"), "w"))
        print("merged", sorted(merged))
        return
    t0 = time.time()
    if a.part == "E1":
        jobs = [("E1", "NN", n0, i, ks) for n0, i, ks in starts((5, 6, 7, 8))]
        fn = job_exact
    elif a.part == "E2":
        jobs = [("E2", "NN2", n0, i, ks) for n0, i, ks in starts((5, 6))]
        fn = job_exact
    elif a.part == "R1":
        jobs = []
        for rule in ("NN", "NN2", "KF3", "SUB"):
            for n0, i, ks in starts((5, 6, 7, 8)):
                for k in range(2 if n0 <= 7 else 1):
                    jobs.append((rule, n0, i, ks, seed_of(rule, n0, i, k)))
        fn = job_run
    elif a.part == "R2":
        jobs = [("NNF", st, 7_000_000 + 1000 * j + s) for j, st in enumerate(("line5", "line6", "line7", "line8", "2x2"))
                for s in range(50)]
        jobs += [("CC", st, 9_000_000 + 1000 * j + s) for j, st in enumerate(("2x2", "fill5", "fill6", "fill7", "fill8"))
                 for s in range(50)]
        jobs += [("CC", "line5", 9_900_000 + s) for s in range(10)]
        fn = job_free
    else:
        raise SystemExit("unknown part")
    with mp.Pool(a.procs) as pool:
        res = []
        for k, r in enumerate(pool.imap(fn, jobs, chunksize=1)):
            res.append(r)
            if (k + 1) % 25 == 0:
                print(a.part, k + 1, "of", len(jobs), round(time.time() - t0), "s", flush=True)
        if a.part == "R2":
            res += list(pool.imap(job_class, [8_000_000 + s for s in range(50)], chunksize=1))
    out = {"part": a.part, "jobs": len(res), "seconds": round(time.time() - t0, 1), "results": res}
    json.dump(out, open(os.path.join(OUT, f"part_{a.part}.json"), "w"))
    print(a.part, "done", len(res), "in", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
