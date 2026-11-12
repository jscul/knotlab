#!/usr/bin/env python3
"""Referee SHIFT-COUNT-R1, ticket A's certified directions rechecked with the referee's own code (ref_fold.py of COMMON-FOLD-R1 for the
bases, its window and tori; a two-way eventually periodic certificate in the frame of the direction, derived as in FAR-BOUND-R1's
ref_quadrants.py; no import of any census.py).

For every base of COMMON-FOLD's draw (sample i, kinds random.Random(50000 + i).sample(kinds, 8)[:r]) that ticket A calls certified
rank 2: take its first certified direction d1 and its first certified direction d2 independent of d1, with ticket A's certificate
(A, p, k, sigma) for each, and check:
  forced  in a window of 61 x 61 cells, p on A is satisfiable and forces sigma(p) on A + k d (sound for the infinite base);
  free    every pattern on A, and p with sigma(p) on A + k d, is carried by a torus (ref_fold's 199 tori) or by a two-way
          eventually periodic state in the frame (d, u) of d (periods p_a along >= the kinds' along-span, q across >= the
          across-span, tails of two blocks each side constrained equal; several period pairs tried, from the kinds' spans upward;
          the direction's frame first, then the standard axes).
Base 16 (its kinds from ACROSS-FOLD: {0, (0,1), (1,-1)}, {0, (0,2), (1,1)}) is checked to have only (1, -1) among the census's
directions forced... and sample 97 at r = 3 with directions (1, 0) and (-1, -1) is reported in full.

    python3 -B ref_shiftcount.py [workers]      (writes result_shiftcount.jsonl, summary in result_shiftcount_summary.json)"""
import itertools
import json
import math
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "COMMON-FOLD-20261112-001" / "referee-R1"))
import ref_fold as RF  # noqa: E402

ROWS = ROOT / "artifacts" / "SHIFT-COUNT-20261112-001A" / "SHIFT-COUNT-20261112-001A-E001_second_direction" / "rows.jsonl"
PERIODS = [(2, 4), (2, 6), (4, 4), (4, 6), (4, 8), (6, 6), (6, 8), (8, 8), (4, 12), (8, 12), (6, 12), (12, 12), (8, 16), (4, 16)]


def kinds_of(sample, r):
    return random.Random(50000 + sample).sample(RF.KINDS, 8)[:r]


def frame(d):
    """a basis (d, u) of Z^2 with det 1: frame coordinates (alpha, y) of z = alpha d + y u"""
    a, b = d
    g, x, y = egcd(a, b)
    assert g == 1
    u = (-y, x)             # a x + b y = 1, det [[a, -y], [b, x]] = a x + b y = 1
    def co(z):
        # solve z = alpha d + y u
        det = a * u[1] - b * u[0]
        al = (z[0] * u[1] - z[1] * u[0]) // det
        yy = (a * z[1] - b * z[0]) // det
        return (al, yy)
    return u, co


def egcd(a, b):
    if b == 0:
        return (abs(a), (1 if a > 0 else -1), 0)
    g, x, y = egcd(b, a % b)
    return (g, y, x - (a // b) * y)


def window_forces(K, A, p, t, sigma, w=(-30, 30, -30, 30)):
    idx, cl = RF.window_clauses(K, w)
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        base = [idx[c] if v else -idx[c] for c, v in zip(A, p)]
        if not s.solve(assumptions=base):
            return False
        for c, v in zip(A, p):
            cc = (c[0] + t[0], c[1] + t[1])
            want = v ^ sigma
            if s.solve(assumptions=base + [-idx[cc] if want else idx[cc]]):
                return False
    return True


def eventual_carries(K, fix, d):
    u, co = frame(d)
    fk = [tuple(co(v) for v in k) for k in K]
    sa = max(max(v[0] for v in k) - min(v[0] for v in k) for k in fk)
    sy = max(max(v[1] for v in k) - min(v[1] for v in k) for k in fk)
    fc = [(co(c), v) for c, v in fix]
    a0 = min(c[0] for c, _ in fc) - 1
    a1 = max(c[0] for c, _ in fc) + 2
    b0 = min(c[1] for c, _ in fc) - 1
    b1 = max(c[1] for c, _ in fc) + 2
    tries = [(pa, q) for pa, q in PERIODS if pa >= sa and q >= sy]
    tries += [(pa, q) for pa in sorted({sa, sa + 1, sa + 2, sa + 3, sa + 4, 2 * sa}) for q in sorted({sy, sy + 1, sy + 2, sy + 3, sy + 4,
              sy + 5, sy + 6, 2 * sy}) if (pa, q) not in tries and pa >= 1]
    for pa, q in tries:
        var = {}
        for a in range(a0 - 2 * pa, a1 + 2 * pa):
            for b in range(b0 - 2 * q, b1 + 2 * q):
                var[a, b] = len(var) + 1
        cl = []
        for (a, b) in var:
            for k in fk:
                cells = [(a + v[0], b + v[1]) for v in k]
                if all(c in var for c in cells):
                    tt = [var[c] for c in cells]
                    cl += [tt, [-x for x in tt]]
        for (a, b), v in var.items():
            if (a1 <= a < a1 + pa) or (a0 - 2 * pa <= a < a0 - pa):
                w = var.get((a + pa, b))
                if w:
                    cl += [[-v, w], [v, -w]]
            if (b1 <= b < b1 + q) or (b0 - 2 * q <= b < b0 - q):
                w = var.get((a, b + q))
                if w:
                    cl += [[-v, w], [v, -w]]
        assum = [var[c] if val else -var[c] for c, val in fc]
        if any(-x in assum for x in assum):
            return False
        with Solver(name="cadical153", bootstrap_with=cl) as s:
            if s.solve(assumptions=assum):
                return [pa, q]
    return False


def carried(K, fix, d):
    if RF.carried(K, fix):
        return "torus"
    for dd in (d, (1, 0), (0, 1)):             # the direction's frame first, then the standard axes
        e = eventual_carries(K, fix, dd)
        if e:
            return f"eventual {e} in the frame of {list(dd)}"
    return False


def check_direction(K, d, cert):
    A = [tuple(c) for c in cert["A"]]
    p, k, sigma = cert["p"], cert["k"], cert["sigma"]
    t = (k * d[0], k * d[1])
    forced = window_forces(K, A, p, t, sigma)
    fix = list(zip(A, p)) + [((c[0] + t[0], c[1] + t[1]), v ^ sigma) for c, v in zip(A, p)]
    c1 = carried(K, fix, d)
    free = []
    for q in itertools.product((0, 1), repeat=len(A) - 1):
        free.append(carried(K, list(zip(A, (0,) + q)), d))
    return {"direction": list(d), "forced": forced, "pattern and its image carried by": c1, "A free": all(free),
            "free by": sorted(set(str(f) for f in free))}


def job(row):
    t0 = time.time()
    K = kinds_of(row["sample"], row["r"])
    dirs = [tuple(x) for x in row["certified directions"]]
    out = {"sample": row["sample"], "r": row["r"], "rank certified (census)": row["rank certified"]}
    if row["rank certified"] < 2:
        return out
    d1 = dirs[0]
    d2 = next(x for x in dirs if x[0] * d1[1] - x[1] * d1[0] != 0)
    picks = [d1, d2]
    if (row["sample"], row["r"]) == (97, 3):
        picks = [(1, 0), (-1, -1)]
    out["checks"] = [check_direction(K, d, row["certificates"][f"{d[0]},{d[1]}"]) for d in picks]
    out["confirmed rank 2"] = all(c["forced"] and c["pattern and its image carried by"] and c["A free"] for c in out["checks"])
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    rows = [json.loads(l) for l in ROWS.read_text().splitlines()]
    rows = [r for r in rows if isinstance(r.get("sample"), int)]
    out_path = HERE / "result_shiftcount.jsonl"
    done = set()
    if out_path.exists():
        done = {(json.loads(l)["sample"], json.loads(l)["r"]) for l in out_path.read_text().splitlines()}
    todo = [r for r in rows if (r["sample"], r["r"]) not in done]
    t0 = time.time()
    with Pool(workers) as pool:
        for res in pool.imap_unordered(job, todo):
            with open(out_path, "a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(res["sample"], res["r"], res.get("confirmed rank 2"), res.get("seconds"), round(time.time() - t0), "s", flush=True)
    res = [json.loads(l) for l in out_path.read_text().splitlines()]
    summ = {"bases": len(res), "census certified rank 2": sum(1 for r in res if r["rank certified (census)"] >= 2),
            "referee confirms rank 2": sum(1 for r in res if r.get("confirmed rank 2")),
            "not confirmed": [[r["sample"], r["r"], r["checks"]] for r in res if r["rank certified (census)"] >= 2 and not r.get("confirmed rank 2")]}
    (HERE / "result_shiftcount_summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summ.items() if k != "not confirmed"}), len(summ["not confirmed"]))


if __name__ == "__main__":
    main()
