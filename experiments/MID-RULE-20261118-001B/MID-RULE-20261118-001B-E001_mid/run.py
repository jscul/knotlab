"""MID-RULE-20261118-001B-E001: the frozen runs.
K: MID2 and ONE knot-local from every bracketing of 5, 6 and 7 and every third of 8 (105 starts), one seed each, to n = 60.
F: MID2 and ONE free from the lines of 5, 8 and 12 and the 2 x 2 pattern (10 runs each), and ANY free from the lines of 5 and 8
   (5 each), to n = 60 (free runs stop at 60 states).
Run: python -B run.py --part K|F [--procs 12], then --merge."""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import midlib as ML  # noqa: E402

M, P = ML.M, ML.P
OUT = os.path.join(ML.ROOT, "artifacts", "MID-RULE-20261118-001B", "MID-RULE-20261118-001B-E001_mid")


def jobs(part):
    J = []
    if part == "K":
        for rule in ("MID2", "ONE"):
            for n0 in (5, 6, 7, 8):
                for i, ks in enumerate(M.bracketings(0, n0 - 1)):
                    if n0 == 8 and i % 3:
                        continue
                    J.append(("K", rule, f"b{n0}", i, ks, 70_000_000 + len(J)))
    else:
        for rule in ("MID2", "ONE"):
            for st in ("line5", "line8", "line12", "2x2"):
                for s in range(10):
                    J.append(("F", rule, st, s, None, 71_000_000 + len(J)))
        for st in ("line5", "line8"):
            for s in range(5):
                J.append(("F", "ANY", st, s, None, 71_000_000 + len(J)))
    return J


def job(arg):
    part, rule, start, i, ks, seed = arg
    t = time.time()
    if part == "K":
        tr = ML.grow_k(ks, int(start[1:]), 60, seed, rule)
    else:
        S, n = P.start(start)
        tr = ML.grow_f(S, n, 60, seed, rule)
    return {"part": part, "rule": rule, "start": start, "index": i, "knots": ks, "seed": seed, "trace": tr,
            "seconds": round(time.time() - t, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part")
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.merge:
        merged = {p: json.load(open(os.path.join(OUT, f"part_{p}.json"))) for p in ("K", "F")}
        json.dump(merged, open(os.path.join(OUT, "results.json"), "w"))
        print("merged")
        return
    J = jobs(a.part)
    t0 = time.time()
    res = []
    with mp.Pool(a.procs) as pool:
        for k, r in enumerate(pool.imap_unordered(job, J, chunksize=1)):
            res.append(r)
            if (k + 1) % 20 == 0:
                print(a.part, k + 1, "of", len(J), round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: (r["rule"], r["start"], r["index"]))
    json.dump({"part": a.part, "jobs": len(res), "seconds": round(time.time() - t0, 1), "results": res},
              open(os.path.join(OUT, f"part_{a.part}.json"), "w"))
    print(a.part, "done", len(res), "in", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
