"""The frozen census of ACROSS-FOLD-20261112-001B-E001 (contract.json beside this file): lower bounds across the fold.

Sheared frame of base 16 (FOLD-20261112-001A-P001): knot kinds {0, (0,1), (1,0)} and {0, (0,2), (1,2)}. A bond is a constrained set
whose every proper part is free. Constrained: some value pattern fails in a window (SAT; sound). Free: every pattern is carried by a
state periodic in the row coordinate with period m (exact transfer walks, m from the set's row span + 3 to 12; sound).

  M. Column-0 family: for targets (k, y), k in {5, 8, 11}, y in 0 .. 10, the least bond A u {(k, y)} with A in column 0, containing row
     0, rows within [min(0, y) - 3, max(0, y) + 3]; predicted floor((y + 1)/2) + 3 (y >= 2) or 4 where k >= floor((y + 1)/2) + 1.
  D. Downward: the same for y in {-3, -4, -5}, up to size 7.
  N. General: for targets (5, 3) and (5, 4), any bond of size at most 4 containing the origin and the target, the other two anywhere in
     columns -1 .. 6 and rows -3 .. 7.

Run from the repository root:
    .venv/bin/python -B experiments/ACROSS-FOLD-20261112-001B/ACROSS-FOLD-20261112-001B-E001_lower_bounds/census.py
Output: artifacts/ACROSS-FOLD-20261112-001B/ACROSS-FOLD-20261112-001B-E001_lower_bounds/census.json and census_log.txt.
"""

from __future__ import annotations

import itertools
import json
import os
import sys
import time
from multiprocessing import Pool

from pysat.solvers import Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "ACROSS-FOLD-20261112-001B", "ACROSS-FOLD-20261112-001B-E001_lower_bounds")
KINDS = [((0, 0), (0, 1), (1, 0)), ((0, 0), (0, 2), (1, 2))]
KS, YS, YDOWN, MAXSIZE = (5, 8, 11), range(0, 11), (-3, -4, -5), 7
NTARGETS, NBOX = ((5, 3), (5, 4)), ((-1, 6), (-3, 7))
WORKERS = 8


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "census_log.txt"), "a") as f:
        f.write(msg + "\n")


def window(X0, X1, Y0, Y1):
    cells = [(x, r) for x in range(X0, X1 + 1) for r in range(Y0, Y1 + 1)]
    idx = {c: i + 1 for i, c in enumerate(cells)}
    cl = []
    for (x, r) in cells:
        for kind in KINDS:
            pts = [(x + a, r + b) for a, b in kind]
            if all(p in idx for p in pts):
                cl += [[idx[p] for p in pts], [-idx[p] for p in pts]]
    return idx, cl


class Strip:
    def __init__(self, m):
        self.m = m
        n = 1 << m
        b = self.bit
        self.succ = [[d for d in range(n)
                      if all(not (b(c, r) == b(c, r + 1) and b(d, r) == b(c, r)) and not (b(c, r) == b(c, r + 2) and b(d, r + 2) == b(c, r))
                             for r in range(m))] for c in range(n)]
        pred = [[] for _ in range(n)]
        for c in range(n):
            for d in self.succ[c]:
                pred[d].append(c)
        fut = set(range(n))
        while True:
            new = {c for c in fut if any(d in fut for d in self.succ[c])}
            if new == fut:
                break
            fut = new
        past = set(range(n))
        while True:
            new = {d for d in past if any(c in past for c in pred[d])}
            if new == past:
                break
            past = new
        self.fut, self.past = fut, past

    def bit(self, c, r):
        return (c >> (r % self.m)) & 1

    def carries(self, cells, p):
        """cells (x, r) with x >= 0 relative to the least column; exact for states of period m."""
        x0 = min(x for x, _ in cells)
        by = {}
        for (x, r), v in zip(cells, p):
            by.setdefault(x - x0, []).append((r, v))
        span = max(by)
        cur = {c for c in self.past if all(self.bit(c, r) == v for r, v in by.get(0, []))}
        for step in range(1, span + 1):
            nxt = set()
            for c in cur:
                nxt.update(self.succ[c])
            cur = {d for d in nxt if all(self.bit(d, r) == v for r, v in by.get(step, []))}
            if not cur:
                return False
        return bool(cur & self.fut)


STRIPS = {}


def free(cells):
    rows = [r for _, r in cells]
    ms = range(max(3, max(rows) - min(rows) + 3), 13)
    for p in itertools.product((0, 1), repeat=len(cells)):
        ok = False
        for m in ms:
            if m not in STRIPS:
                STRIPS[m] = Strip(m)
            if STRIPS[m].carries(cells, p):
                ok = True
                break
        if not ok:
            return False
    return True


def constrained(s, idx, cells):
    return any(not s.solve(assumptions=[idx[c] * (1 if b else -1) for c, b in zip(cells, p)])
               for p in itertools.product((0, 1), repeat=len(cells)))


def is_bond(s, idx, cells):
    return constrained(s, idx, cells) and all(free([c for c in cells if c != u]) for u in cells)


def column0(job):
    k, y = job
    idx, cl = window(-8, k + 6, -14, 18)
    s = Minisat22(bootstrap_with=cl)
    t = (k, y)
    rows = [r for r in range(min(0, y) - 3, max(0, y) + 4) if r != 0]
    best = None
    for size in range(2, MAXSIZE + 1):
        for A in itertools.combinations(rows, size - 2):
            cells = [(0, r) for r in sorted((0,) + A)] + [t]
            if is_bond(s, idx, cells):
                best = {"size": size, "A": sorted((0,) + A)}
                break
        if best:
            break
    s.delete()
    return {"k": k, "y": y, "least": best}


def general(t):
    (x0, x1), (y0, y1) = NBOX
    idx, cl = window(-8, 12, -12, 14)
    s = Minisat22(bootstrap_with=cl)
    box = [(x, r) for x in range(x0, x1 + 1) for r in range(y0, y1 + 1) if (x, r) not in ((0, 0), t)]
    found = None
    for size in (3, 4):
        for extra in itertools.combinations(box, size - 2):
            cells = sorted([(0, 0), t] + list(extra))
            if is_bond(s, idx, cells):
                found = {"size": size, "set": cells}
                break
        if found:
            break
    s.delete()
    return {"target": list(t), "bond of size <= 4": found}


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "census_log.txt"), "w").close()
    t0 = time.time()
    jobs = [(k, y) for k in KS for y in list(YS) + list(YDOWN)]
    with Pool(WORKERS) as pool:
        col = pool.map(column0, jobs, chunksize=1)
        log("column-0 family done", round(time.time() - t0, 1), "s")
        gen = pool.map(general, list(NTARGETS), chunksize=1)
    log("general search done", round(time.time() - t0, 1), "s")
    prof = {}
    for r in col:
        prof.setdefault(r["y"], {})[r["k"]] = r["least"]["size"] if r["least"] else None
    expected = {y: (y + 1) // 2 + 3 if y >= 2 else 4 for y in YS}
    # M is registered where the ladder is a bond (k >= floor((y + 1) / 2) + 1, Theorem L); nearer columns are measured only
    m_cells = [(y, k) for y in YS for k in KS if y <= 1 or k >= (y + 1) // 2 + 1]
    m_bad = [(y, k, prof[y][k]) for y, k in m_cells if prof[y][k] != expected[y]]
    d_bad = [(y, k, prof[y][k]) for y in YDOWN for k in KS if prof[y][k] is not None]
    n_bad = [g for g in gen if g["bond of size <= 4"]]
    summary = {"profile (least column-0 bond size by row, at k = 5, 8, 11)": prof,
               "M": {"expected": expected, "cells": len(m_cells), "mismatches": m_bad, "holds": not m_bad},
               "D": {"found": d_bad, "holds": not d_bad},
               "N": {"found": n_bad, "holds": not n_bad}}
    summary["failures"] = [x for x in ("M", "D", "N") if not summary[x]["holds"]]
    log("summary:", json.dumps(summary, default=str)[:3000])
    json.dump({"column 0": col, "general": gen, "summary": summary}, open(os.path.join(OUT, "census.json"), "w"), indent=1, default=str)
    log("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
