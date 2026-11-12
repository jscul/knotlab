#!/usr/bin/env python3
"""Referee COMMON-FOLD-R1, ticket A: the periodic-influence census rebuilt with the referee's own code (no import of census.py).

    python3 -B ref_fold.py [--workers 8]      (writes result_fold.jsonl, one line per sample, and prints a summary)

Kinds, samples and the readings follow the pre-registration's text: the 171 kinds of three cells of [0, 2] x [-2, 2] up to
translation; sample i is random.Random(50000 + i).sample(kinds, 8) (the frozen draw, so that the census's own bases are re-read); the
base at r is the first r kinds. Readings, with Glucose 4 (the census used Minisat 2.2):
- contradiction: no state on the window x in [-6, 8], y in [-8, 10];
- base: a state on one of the tori Z^2 / <(P, s), (0, Q)> listed by the pre-registration (P, Q <= 8 with s = 0; 1 <= s < P <= 6,
  Q <= 6); else unsettled;
- tied along t (ten shifts): the window forces x_t given x_0;
- travels along t: a set A of 2 to 4 cells of [0, 1] x [0, 2] holding (0, 0), a pattern p (first value 0), sigma, such that the
  window forces sigma(p) on A + t; certified when p with sigma(p) is carried by a torus state and every pattern on A is.
Beyond the census, for every base not classed tied: ties along the same ten shifts in a window twice as wide (x in [-16, 18],
y in [-18, 20]), so that a tie the small window missed would show (a travelling base misclassified)."""
import itertools
import json
import math
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
SHIFTS = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (1, -2), (2, 1), (2, -1), (0, 2), (2, 0)]
BOX = [(x, y) for x in range(0, 2) for y in range(0, 3)]
WIN = (-6, 8, -8, 10)
BIG = (-16, 18, -18, 20)


def kinds():
    cells = [(x, y) for x in range(0, 3) for y in range(-2, 3)]
    out = set()
    for t in itertools.combinations(cells, 3):
        pts = sorted(t)
        x0, y0 = pts[0]
        out.add(tuple((x - x0, y - y0) for x, y in pts))
    return sorted(out)


KINDS = kinds()


def window_clauses(K, w):
    X0, X1, Y0, Y1 = w
    idx = {}
    for x in range(X0, X1 + 1):
        for y in range(Y0, Y1 + 1):
            idx[(x, y)] = len(idx) + 1
    cl = []
    for (x, y) in idx:
        for k in K:
            pts = [(x + a, y + b) for a, b in k]
            if all(p in idx for p in pts):
                v = [idx[p] for p in pts]
                cl += [v, [-u for u in v]]
    return idx, cl


TORI = [(P, 0, Q) for P in range(1, 9) for Q in range(1, 9)] + \
       [(P, s, Q) for P in range(2, 7) for s in range(1, P) for Q in range(1, 7)]


def torus_ok(K, P, s, Q, fix):
    def red(x, y):
        k, xm = divmod(x, P)
        return (xm, (y - k * s) % Q)
    cells = [(x, y) for x in range(P) for y in range(Q)]
    idx = {c: i + 1 for i, c in enumerate(cells)}
    cl = []
    for (x, y) in cells:
        for k in K:
            v = [idx[red(x + a, y + b)] for a, b in k]
            if len(set(v)) < 3 and len(set(v)) == 1:
                return False                     # a knot folded onto one cell: NAE impossible
            cl += [v, [-u for u in v]]
    for (x, y), val in fix:
        cl.append([idx[red(x, y)] if val else -idx[red(x, y)]])
    with Glucose4(bootstrap_with=cl) as so:
        return so.solve()


def carried(K, fix):
    return any(torus_ok(K, P, s, Q, fix) for P, s, Q in TORI)


def ties(K, w):
    idx, cl = window_clauses(K, w)
    with Glucose4(bootstrap_with=cl) as so:
        if not so.solve():
            return None
        o = idx[(0, 0)]
        out = []
        for t in SHIFTS:
            can_eq = so.solve(assumptions=[-o, -idx[t]])
            can_ne = so.solve(assumptions=[-o, idx[t]])
            if not (can_eq and can_ne):
                out.append([list(t), 0 if can_eq else 1])
        return out


def read(K):
    idx, cl = window_clauses(K, WIN)
    so = Glucose4(bootstrap_with=cl)
    try:
        if not so.solve():
            return {"outcome": "contradiction"}
        res = {"outcome": "base" if carried(K, []) else "unsettled"}
        o = idx[(0, 0)]
        tied = []
        for t in SHIFTS:
            if not so.solve(assumptions=[-o, -idx[t]]) or not so.solve(assumptions=[-o, idx[t]]):
                tied.append(list(t))
        res["tied"] = tied
        found = uncert = None
        for size in range(2, 5):
            for A in itertools.combinations(BOX, size):
                if (0, 0) not in A:
                    continue
                for tail in itertools.product((0, 1), repeat=size - 1):
                    p = (0,) + tail
                    lits = [idx[c] if v else -idx[c] for c, v in zip(A, p)]
                    if not so.solve(assumptions=lits):
                        continue
                    for t in SHIFTS:
                        for sig in (0, 1):
                            forced = True
                            for c, v in zip(A, p):
                                tc = (c[0] + t[0], c[1] + t[1])
                                want = v ^ sig
                                if so.solve(assumptions=lits + [-idx[tc] if want else idx[tc]]):
                                    forced = False
                                    break
                            if not forced:
                                continue
                            fix = list(zip(A, p)) + [((c[0] + t[0], c[1] + t[1]), v ^ sig) for c, v in zip(A, p)]
                            free = all(carried(K, list(zip(A, (0,) + q))) for q in itertools.product((0, 1), repeat=size - 1))
                            rec = {"A": [list(c) for c in A], "p": list(p), "t": list(t), "sigma": sig}
                            if carried(K, fix) and free:
                                found = rec
                                break
                            if uncert is None:
                                uncert = rec
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break
        res["travels"] = found
        res["uncertified"] = None if found else uncert
        if not tied:
            big = ties(K, BIG)
            res["tied in the wide window"] = big
        return res
    finally:
        so.delete()


def classify(r):
    if r["outcome"] == "contradiction":
        return "contradiction"
    if r["tied"]:
        return "tied"
    if r["travels"]:
        return "travels"
    if r["uncertified"]:
        return "travels, uncertified"
    return "none found"


def job(i):
    order = random.Random(50000 + i).sample(KINDS, 8)
    out = {"sample": i, "by r": {}}
    for r in range(1, 9):
        rd = read(order[:r])
        rd["class"] = classify(rd)
        out["by r"][str(r)] = rd
    return out


if __name__ == "__main__":
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    print("kinds", len(KINDS), flush=True)
    t0 = time.time()
    path = HERE / "result_fold.jsonl"
    done = set()
    if path.exists():
        done = {json.loads(l)["sample"] for l in open(path)}
    todo = [i for i in range(200) if i not in done]
    with Pool(workers) as pool, open(path, "a") as f:
        for k, row in enumerate(pool.imap_unordered(job, todo, chunksize=1)):
            f.write(json.dumps(row) + "\n")
            f.flush()
            if (k + 1) % 20 == 0:
                print(k + 1, "samples", round(time.time() - t0, 1), "s", flush=True)
    print("done", round(time.time() - t0, 1), "s")
