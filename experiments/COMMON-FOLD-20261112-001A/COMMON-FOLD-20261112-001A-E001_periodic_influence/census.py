"""The frozen census of COMMON-FOLD-20261112-001A-E001 (contract.json beside this file): global influence among random periodic bases.

A knot kind is a set of three offsets in Z^2 up to translation, from the box [0, 2] x [-2, 2] (171 kinds, normalized so the least
offset in lexicographic order is (0, 0)). A periodic base with kinds K has the distinction set Z^2 and a not-all-equal knot on
z + k for every z and every kind k in K.

Weighting W(r): sample i (i = 0 .. 199) draws one uniform random order of the 171 kinds (random.Random(50000 + i)); its base at r is
the first r kinds, r = 1 .. 8 (nested prefixes: each r has the uniform weighting over r-sets of kinds).

For each base (all certificates sound):
  - outcome: "contradiction" when no state exists on the window of columns -6 .. 8 and rows -8 .. 10 (SAT); "base" when a doubly
    periodic state exists for periods (P, 0) and (s, Q), 1 <= P, Q <= 8 with s = 0, or 1 <= s < P <= 6 and Q <= 6; else "unsettled".
  - lattice: rank and index of the lattice spanned by the kinds' offsets (rank 1 or index > 1: the base splits into copies).
  - tied along t: for a shift t of SHIFTS, the value at 0 forces the value at t (window SAT): a tie at every multiple of t.
  - travels along t: a set A of 2 to 4 cells of the box [0, 1] x [0, 2] containing (0, 0), a pattern p on A (first value 0), t in
    SHIFTS and sigma (identity or complement) such that p on A forces sigma(p) on A + t (window SAT, each value); certified when p
    with sigma(p) on A + t is carried by a doubly periodic state and every pattern on A is (A free). Lemma (pre-registration): a
    certified travelling pattern gives, for every k, a bond of at most |A| + 1 distinctions holding a + k t and a member of A.
Rates with Wilson 95% intervals. Controls: base 16 (kinds {(0,0),(0,1),(1,-1)}, {(0,0),(0,2),(1,1)}) must travel and be tied along no listed shift.
A sensitivity part reruns samples 0 .. 49 at r = 2, 3, 4 with A of 2 to 4 cells in [0, 2] x [0, 2], all shifts (a, b) with
0 <= a <= 2, |b| <= 2, and the window -9 .. 11 by -11 .. 13.

    .venv/bin/python -B experiments/COMMON-FOLD-20261112-001A/COMMON-FOLD-20261112-001A-E001_periodic_influence/census.py [--part main | sens | control] [--workers 8]
Output: artifacts/COMMON-FOLD-20261112-001A/COMMON-FOLD-20261112-001A-E001_periodic_influence/{main,sens,control}.json and log.txt.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import random
import sys
import time
from multiprocessing import Pool

from pysat.solvers import Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "COMMON-FOLD-20261112-001A", "COMMON-FOLD-20261112-001A-E001_periodic_influence")
N_SAMPLES, RMAX, SEED0 = 200, 8, 50000
SHIFTS = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (1, -2), (2, 1), (2, -1), (0, 2), (2, 0)]
BOX = [(x, y) for x in range(0, 2) for y in range(0, 3)]
WIN = (-6, 8, -8, 10)
SENS_SHIFTS = [(a, b) for a in range(0, 3) for b in range(-2, 3) if (a, b) != (0, 0) and (a > 0 or b > 0)]
SENS_BOX = [(x, y) for x in range(0, 3) for y in range(0, 3)]
SENS_WIN = (-9, 11, -11, 13)
BASE16 = [((0, 0), (0, 1), (1, -1)), ((0, 0), (0, 2), (1, 1))]


def norm(kind):
    pts = sorted(kind)
    x0, y0 = pts[0]
    return tuple((x - x0, y - y0) for x, y in pts)


def all_kinds():
    cells = [(x, y) for x in range(0, 3) for y in range(-2, 3)]
    return sorted({norm(t) for t in itertools.combinations(cells, 3)})


KINDS = all_kinds()


def lattice(kinds):
    vecs = [v for k in kinds for v in k if v != (0, 0)]
    dets = [abs(a[0] * b[1] - a[1] * b[0]) for a, b in itertools.combinations(vecs, 2)]
    g = 0
    for d in dets:
        g = math.gcd(g, d)
    return {"rank": 2 if g else 1, "index": g if g else None}


def window(kinds, w):
    X0, X1, Y0, Y1 = w
    cells = [(x, y) for x in range(X0, X1 + 1) for y in range(Y0, Y1 + 1)]
    idx = {c: i + 1 for i, c in enumerate(cells)}
    cl = []
    for (x, y) in cells:
        for k in kinds:
            pts = [(x + a, y + b) for a, b in k]
            if all(p in idx for p in pts):
                v = [idx[p] for p in pts]
                cl += [v, [-u for u in v]]
    return idx, cl


def tori():
    out = [(P, 0, Q) for P in range(1, 9) for Q in range(1, 9)]
    out += [(P, s, Q) for P in range(2, 7) for s in range(1, P) for Q in range(1, 7)]
    return out


TORI = tori()


def torus_carries(kinds, P, s, Q, fix):
    def rep(x, y):
        xm = x % P
        kk = (x - xm) // P
        return (xm, (y - kk * s) % Q)
    cells = [(x, y) for x in range(P) for y in range(Q)]
    idx = {c: i + 1 for i, c in enumerate(cells)}
    cl = []
    for (x, y) in cells:
        for k in kinds:
            v = [idx[rep(x + a, y + b)] for a, b in k]
            cl += [v, [-u for u in v]]
    for (x, y), val in fix:
        cl.append([idx[rep(x, y)] * (1 if val else -1)])
    with Minisat22(bootstrap_with=cl) as s_:
        return s_.solve()


def carried(kinds, fix):
    return any(torus_carries(kinds, P, s, Q, fix) for P, s, Q in TORI)


def read_base(kinds, box=BOX, shifts=SHIFTS, w=WIN):
    res = {"kinds": [list(map(list, k)) for k in kinds], "lattice": lattice(kinds)}
    idx, cl = window(kinds, w)
    s = Minisat22(bootstrap_with=cl)
    try:
        if not s.solve():
            res["outcome"] = "contradiction"
            return res
        res["outcome"] = "base" if carried(kinds, []) else "unsettled"
        o = idx[(0, 0)]
        tied = []
        for t in shifts:
            for sig in (0, 1):
                # value 0 at the origin; is the value at t forced to sig?
                if not s.solve(assumptions=[-o, idx[t] * (-1 if sig else 1)]):
                    tied.append({"t": list(t), "sigma": 1 - sig})
        res["tied along"] = tied
        found, uncert = None, None
        for size in range(2, 5):
            for A in itertools.combinations(box, size):
                if (0, 0) not in A:
                    continue
                for tail in itertools.product((0, 1), repeat=size - 1):
                    p = (0,) + tail
                    assum = [idx[c] * (1 if v else -1) for c, v in zip(A, p)]
                    if not s.solve(assumptions=assum):
                        continue
                    for t in shifts:
                        for flip in (0, 1):
                            if all(not s.solve(assumptions=assum + [idx[(c[0] + t[0], c[1] + t[1])] * (-1 if (v ^ flip) else 1)])
                                   for c, v in zip(A, p)):
                                fix = list(zip(A, p)) + [((c[0] + t[0], c[1] + t[1]), v ^ flip) for c, v in zip(A, p)]
                                cert = carried(kinds, fix) and all(
                                    carried(kinds, list(zip(A, (0,) + q))) for q in itertools.product((0, 1), repeat=size - 1))
                                rec = {"A": [list(c) for c in A], "p": list(p), "t": list(t), "sigma": flip, "size": size}
                                if cert:
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
        res["travels, uncertified only"] = None if found else uncert
        return res
    finally:
        s.delete()


def sample_order(i):
    return random.Random(SEED0 + i).sample(KINDS, RMAX)


def job_main(i):
    order = sample_order(i)
    return {"sample": i, "by r": {r: read_base(order[:r]) for r in range(1, RMAX + 1)}}


def job_sens(i):
    order = sample_order(i)
    return {"sample": i, "by r": {r: read_base(order[:r], box=SENS_BOX, shifts=SENS_SHIFTS, w=SENS_WIN) for r in (2, 3, 4)}}


def wilson(k, n):
    if n == 0:
        return [None, None]
    z = 1.96
    c = (k + z * z / 2) / (n + z * z)
    h = z * math.sqrt(k * (n - k) / n + z * z / 4) / (n + z * z)
    return [round(c - h, 4), round(c + h, 4)]


def classify(rb):
    if rb["outcome"] == "contradiction":
        return "contradiction"
    if rb.get("tied along"):
        return "tied"
    if rb.get("travels"):
        return "travels"
    if rb.get("travels, uncertified only"):
        return "travels, uncertified"
    return "none found"


def refl(kinds, fx, fy):
    return tuple(sorted(norm(tuple((x * fx, y * fy) for x, y in k)) for k in kinds))


def summarize(rows, rs):
    out = {}
    for r in rs:
        recs = [row["by r"][r] if r in row["by r"] else row["by r"][str(r)] for row in rows]
        cls = [classify(x) for x in recs]
        n = len(recs)
        nb = sum(x["outcome"] == "base" for x in recs)
        nu = sum(x["outcome"] == "unsettled" for x in recs)
        base_cls = [c for x, c in zip(recs, cls) if x["outcome"] == "base"]
        nonc_cls = [c for c in cls if c != "contradiction"]
        tr_b = sum(c == "travels" for c in base_cls)
        tg_b = sum(c == "tied" for c in base_cls)
        full = [c for x, c in zip(recs, cls) if x["outcome"] == "base" and x["lattice"]["index"] == 1]
        sizes = {}
        for x, c in zip(recs, cls):
            if c == "travels":
                sizes[x["travels"]["size"]] = sizes.get(x["travels"]["size"], 0) + 1
        classes = {min(refl([tuple(map(tuple, k)) for k in x["kinds"]], fx, fy) for fx in (1, -1) for fy in (1, -1)) for x in recs}
        out[r] = {"samples": n, "contradiction": sum(c == "contradiction" for c in cls), "base": nb, "unsettled": nu,
                  "classes under the box's reflections": len(classes),
                  "among bases": {k: sum(c == k for c in base_cls) for k in ("travels", "tied", "travels, uncertified", "none found")},
                  "travels / bases": [tr_b, nb, wilson(tr_b, nb)],
                  "travels / (bases + unsettled)": [sum(c == "travels" for c in nonc_cls), nb + nu, wilson(sum(c == "travels" for c in nonc_cls), nb + nu)],
                  "tied / bases": [tg_b, nb, wilson(tg_b, nb)],
                  "tied or travels / bases": [tg_b + tr_b, nb, wilson(tg_b + tr_b, nb)],
                  "travels / bases of lattice index 1": [sum(c == "travels" for c in full), len(full), wilson(sum(c == "travels" for c in full), len(full))],
                  "contradiction / samples": [sum(c == "contradiction" for c in cls), n, wilson(sum(c == "contradiction" for c in cls), n)],
                  "travelling set sizes": sizes}
    return out


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(msg + "\n")


def main():
    part = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "main"
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    if part == "control":
        res = {"base 16": read_base(BASE16), "r = 1 kinds checked": len(KINDS)}
        res["base 16 class"] = classify(res["base 16"])
        res["holds"] = res["base 16 class"] == "travels"
        json.dump(res, open(os.path.join(OUT, "control.json"), "w"), indent=1)
        log("control", res["base 16 class"], round(time.time() - t0, 1), "s")
        return
    job, rng_, rs = (job_main, range(N_SAMPLES), range(1, RMAX + 1)) if part == "main" else (job_sens, range(50), (2, 3, 4))
    with Pool(workers) as pool:
        rows = []
        for k, row in enumerate(pool.imap(job, rng_, chunksize=1)):
            rows.append(row)
            if (k + 1) % 20 == 0:
                log(part, k + 1, "samples", round(time.time() - t0, 1), "s")
    summ = summarize(rows, rs)
    if part == "main":
        # nested prefixes: a contradiction at r stays one at every larger r (a check)
        bad = [row["sample"] for row in rows
               if any(row["by r"][r]["outcome"] == "contradiction" and row["by r"][r + 1]["outcome"] != "contradiction" for r in range(1, RMAX))]
        lost = sum(1 for row in rows for r in range(1, RMAX)
                   if classify(row["by r"][r]) == "travels" and row["by r"][r + 1]["outcome"] == "base" and classify(row["by r"][r + 1]) != "travels")
        summ["checks"] = {"contradiction monotone along prefixes": not bad, "violations": bad,
                          "certified travelling lost on adding a kind (base kept)": lost}
    json.dump({"rows": rows, "summary": summ}, open(os.path.join(OUT, f"{part}.json"), "w"), indent=1)
    log(part, "summary", json.dumps(summ)[:4000])
    log(part, "done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
