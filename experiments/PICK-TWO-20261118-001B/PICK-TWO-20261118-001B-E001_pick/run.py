"""PICK-TWO-20261118-001B-E001: the frozen runs.  Parts:

C1  caps: CAP(3) from lines of 5 to 8 (20 runs each) and Q3 (10); CAP(4) from lines of 5 and 8 (10 each) and Q4 (5); to n = 60
C2  linear prices w = 1.0, 1.9, 2.0, 2.1, 3.0 from lines of 5 and 8, 20 runs each, to n = 40
C3  quadratic prices w = 0.25, 0.35, 0.5, 1.0 from lines of 5 and 8, 20 runs each, to n = 40
C4  rules told no number (KEEP, CC, ODD, FRESH, NEWCROSS, SEED) from lines of 5, 6, 7, 8, 10 and 12 (20 runs each) and from Q3 and
    the 3 x 3 x 3 grid (10 each), to n = 60

Runs stop early at 62 states, the fill enumeration's limit, and say so.  Run: python -B run.py --part C1|C2|C3|C4 [--procs 8],
then --merge.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import picklib as P  # noqa: E402

OUT = os.path.join(P.ROOT, "artifacts", "PICK-TWO-20261118-001B", "PICK-TWO-20261118-001B-E001_pick")
NO_NUMBER = ("KEEP", "CC", "ODD", "FRESH", "NEWCROSS", "SEED")


def grid333():
    """The full 3 x 3 x 3 grid: three chains of two splits each, as states over its 27 cells."""
    cells = [(a, b, c) for a in range(3) for b in range(3) for c in range(3)]
    n = len(cells)
    full = (1 << n) - 1
    S = {0, full}
    for axis in range(3):
        for t in (1, 2):
            s = sum(1 << i for i, x in enumerate(cells) if x[axis] >= t)
            S.add(s)
            S.add(full ^ s)
    return tuple(sorted(S)), n


def begin(name):
    if name == "G333":
        return grid333()
    return P.start(name)


def job(arg):
    part, rule, param, start, nmax, seed = arg
    t = time.time()
    S, n = begin(start)
    tr = P.grow(S, n, nmax, rule, seed, tuple(param) if isinstance(param, list) else param)
    return {"part": part, "rule": rule, "param": param, "start": start, "seed": seed, "trace": tr,
            "seconds": round(time.time() - t, 1)}


def jobs_for(part):
    J = []
    base = {"C1": 1, "C2": 2, "C3": 3, "C4": 4}[part] * 10_000_000

    def add(rule, param, start, nmax, runs, tag):
        for s in range(runs):
            J.append((part, rule, param, start, nmax, base + len(J)))
    if part == "C1":
        for st in ("line5", "line6", "line7", "line8"):
            add("CAP", 3, st, 60, 20, 1)
        add("CAP", 3, "Q3", 60, 10, 2)
        for st in ("line5", "line8"):
            add("CAP", 4, st, 60, 10, 3)
        add("CAP", 4, "Q4", 60, 5, 4)
    elif part == "C2":
        for w in (1.0, 1.9, 2.0, 2.1, 3.0):
            for st in ("line5", "line8"):
                add("PRICE", ["lin", w], st, 40, 20, 5)
    elif part == "C3":
        for w in (0.25, 0.35, 0.5, 1.0):
            for st in ("line5", "line8"):
                add("PRICE", ["quad", w], st, 40, 20, 6)
    elif part == "C4":
        for rule in NO_NUMBER:
            for st in ("line5", "line6", "line7", "line8", "line10", "line12"):
                add(rule, None, st, 60, 20, 7)
            for st in ("Q3", "G333"):
                add(rule, None, st, 60, 10, 8)
    return J


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.merge:
        merged = {}
        for p in ("C1", "C2", "C3", "C4"):
            f = os.path.join(OUT, f"part_{p}.json")
            if os.path.exists(f):
                merged[p] = json.load(open(f))
        json.dump(merged, open(os.path.join(OUT, "results.json"), "w"))
        print("merged", sorted(merged))
        return
    J = jobs_for(a.part)
    assert len({j[-1] for j in J}) == len(J), "seeds must differ"
    t0 = time.time()
    res = []
    with mp.Pool(a.procs) as pool:
        for k, r in enumerate(pool.imap_unordered(job, J, chunksize=1)):
            res.append(r)
            if (k + 1) % 25 == 0:
                print(a.part, k + 1, "of", len(J), round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: (r["rule"], str(r["param"]), r["start"], r["seed"]))
    json.dump({"part": a.part, "jobs": len(res), "seconds": round(time.time() - t0, 1), "results": res},
              open(os.path.join(OUT, f"part_{a.part}.json"), "w"))
    print(a.part, "done", len(res), "in", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
