"""Soundness audit of ACROSS-FOLD-20261112-001B-E001, designed after its census ran (not frozen).

The census finds a bond when the set is refuted in a window (sound) and every proper part is carried by states periodic in the row
coordinate (sound). Its negatives are not certificates: a candidate it rejects may be a bond whose constraint lies outside the window,
or whose parts it failed to certify, and its periods started at the set's row span + 3, so parts of row span 10 or more were never
certified at all. This audit certifies every rejection below the predicted size:

  - "free": the candidate itself is carried by periodic states in every pattern, so it is not constrained;
  - "part constrained": some proper part is refuted in a window, so the candidate is not minimal;
  - "bond": refuted, every part certified free: a bond smaller than predicted (a failure of M, D or N);
  - "uncertified, refuted": refuted in the window, no part refuted, some part not certified free (a possible bond);
  - "uncertified, not refuted": not refuted in the window and not certified free (a bond only if its constraint lies outside the
    window).

Periods: every m from 3 to 12. A state periodic in rows with period m carrying the pattern is a state of the base whatever the set's
row span, since two cells of one column whose rows agree mod m are checked to agree, so every m is sound.

With --deep, periods 13 to 15 are added for the patterns the shorter ones do not carry (packed bit matrices), the output goes to
soundness_audit_deep.json, and the ladders of rows 9 and 10 (one size past Theorem L) are classified at k = 8 and 11.

Families: M at k = 5, 8, 11 and y = 0 .. 10 (candidates below the predicted size, at most 7, where k >= floor((y+1)/2) + 1), D at
y = -3, -4, -5 (sizes to 7), N for (5, 3) and (5, 4) (sizes 3 and 4 in the box), exactly the census's candidate sets.

    .venv/bin/python -B research/ACROSS-FOLD-20261112-001/soundness_audit.py [--workers 8] [--deep] [--only k,y]
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
spec = importlib.util.spec_from_file_location("census", os.path.join(
    ROOT, "experiments/ACROSS-FOLD-20261112-001B/ACROSS-FOLD-20261112-001B-E001_lower_bounds/census.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
from pysat.solvers import Minisat22  # noqa: E402

MS = range(3, 13)
DEEP = (13, 14, 15)      # with --deep: periods the pure-Python strips cannot reach, as packed bit matrices (numpy)
STRIPS = {}
USE_DEEP = "--deep" in sys.argv


class BigStrip:
    """The strip of period m as a packed bit matrix; the same transfer rule and the same exact carrying test as census.Strip."""

    def __init__(self, m, chunk=1024):
        import numpy as np
        self.np, self.m, N = np, m, 1 << m
        self.N = N
        bits = self.bits = ((np.arange(N)[:, None] >> np.arange(m)[None, :]) & 1).astype(np.uint8)
        rows = []
        for c0 in range(0, N, chunk):
            Cb = bits[c0:c0 + chunk]
            ok = np.ones((len(Cb), N), dtype=bool)
            for r in range(m):
                r1, r2 = (r + 1) % m, (r + 2) % m
                ok &= ~((Cb[:, r] == Cb[:, r1])[:, None] & (bits[None, :, r] == Cb[:, r][:, None]))
                ok &= ~((Cb[:, r] == Cb[:, r2])[:, None] & (bits[None, :, r2] == Cb[:, r][:, None]))
            rows.append(np.packbits(ok, axis=1, bitorder="little").view(np.uint64))
        self.A = np.concatenate(rows)
        fut = np.ones(N, bool)
        while True:
            fp = np.packbits(fut, bitorder="little").view(np.uint64)
            new = fut & (self.A & fp[None, :]).any(axis=1)
            if (new == fut).all():
                break
            fut = new
        past = np.ones(N, bool)
        while True:
            new = past & self.step(past)
            if (new == past).all():
                break
            past = new
        self.fut, self.past = fut, past

    def step(self, cur):
        np = self.np
        idx = np.nonzero(cur)[0]
        if len(idx) == 0:
            return np.zeros(self.N, bool)
        red = np.bitwise_or.reduce(self.A[idx], axis=0)
        return np.unpackbits(red.view(np.uint8), bitorder="little")[: self.N].astype(bool)

    def match(self, rv):
        mk = self.np.ones(self.N, bool)
        for r, v in rv:
            mk &= self.bits[:, r % self.m] == v
        return mk

    def carries(self, cells, p):
        x0 = min(x for x, _ in cells)
        by = {}
        for (x, r), v in zip(cells, p):
            by.setdefault(x - x0, []).append((r, v))
        cur = self.past & self.match(by.get(0, []))
        for s in range(1, max(by) + 1):
            if not cur.any():
                return False
            cur = self.step(cur) & self.match(by.get(s, []))
        return bool((cur & self.fut).any())


def strip(m):
    if m not in STRIPS:
        STRIPS[m] = C.Strip(m) if m <= 12 else BigStrip(m)
    return STRIPS[m]


def free_any(cells):
    ms = list(MS) + (list(DEEP) if USE_DEEP else [])
    for p in itertools.product((0, 1), repeat=len(cells)):
        if not any(strip(m).carries(cells, p) for m in ms):
            return False
    return True


def ladder(y):
    return [0, 1, 2] + list(range(4, y + 1, 2)) if y % 2 == 0 else [-1, 0, 1] + list(range(3, y + 1, 2))


def classify(s, idx, cells):
    if C.constrained(s, idx, cells):
        parts = [[c for c in cells if c != u] for u in cells]
        if any(C.constrained(s, idx, T) for T in parts):
            return "part constrained"
        return "bond" if all(free_any(T) for T in parts) else "uncertified, refuted"
    return "free" if free_any(cells) else "uncertified, not refuted"


def expected(y):
    return (y + 1) // 2 + 3 if y >= 2 else 4


def column0(job):
    k, y = job
    idx, cl = C.window(-8, k + 6, -14, 18)
    s = Minisat22(bootstrap_with=cl)
    t = (k, y)
    rows = [r for r in range(min(0, y) - 3, max(0, y) + 4) if r != 0]
    top = min(expected(y) - 1, 7) if y >= 0 else 7
    tally, odd = {}, []
    for size in range(2, top + 1):
        for A in itertools.combinations(rows, size - 2):
            cells = [(0, r) for r in sorted((0,) + A)] + [t]
            v = classify(s, idx, cells)
            tally[v] = tally.get(v, 0) + 1
            if v != "free" and v != "part constrained":
                odd.append({"verdict": v, "rows": sorted((0,) + A)})
    lad = None
    if y >= 9 and USE_DEEP:      # one size past Theorem L: is the ladder a bond at rows 9 and 10?
        lad = classify(s, idx, [(0, r) for r in ladder(y)] + [t])
    s.delete()
    return {"k": k, "y": y, "sizes": [2, top], "ladder (rows 9, 10, --deep)": lad, "tally": tally, "bonds or uncertified": odd[:20], "n odd": len(odd)}


def general(t):
    (x0, x1), (y0, y1) = C.NBOX
    idx, cl = C.window(-8, 12, -12, 14)
    s = Minisat22(bootstrap_with=cl)
    box = [(x, r) for x in range(x0, x1 + 1) for r in range(y0, y1 + 1) if (x, r) not in ((0, 0), t)]
    tally, odd = {}, []
    for size in (3, 4):
        for extra in itertools.combinations(box, size - 2):
            cells = sorted([(0, 0), t] + list(extra))
            v = classify(s, idx, cells)
            tally[v] = tally.get(v, 0) + 1
            if v != "free" and v != "part constrained":
                odd.append({"verdict": v, "set": cells})
    s.delete()
    return {"target": list(t), "tally": tally, "bonds or uncertified": odd[:20], "n odd": len(odd)}


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    t0 = time.time()
    if "--only" in sys.argv:
        k, y = map(int, sys.argv[sys.argv.index("--only") + 1].split(","))
        print(json.dumps(column0((k, y))), round(time.time() - t0, 1), "s")
        return
    jobs = [(k, y) for k in C.KS for y in C.YS if y <= 1 or k >= (y + 1) // 2 + 1] + [(k, y) for k in C.KS for y in C.YDOWN]
    with Pool(workers) as pool:
        col = pool.map(column0, jobs, chunksize=1)
        gen = pool.map(general, list(C.NTARGETS), chunksize=1)
    total = {}
    for r in col + gen:
        for v, n in r["tally"].items():
            total[v] = total.get(v, 0) + n
    out = {"designed": "after the census ran; not frozen", "periods": [3, max(DEEP) if USE_DEEP else 12], "column 0": col, "general": gen, "total": total,
           "bonds": [r for r in col + gen if r["tally"].get("bond")], "seconds": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "soundness_audit_deep.json" if USE_DEEP else "soundness_audit.json"), "w"), indent=1)
    print(json.dumps(total), out["seconds"], "s")


if __name__ == "__main__":
    main()
