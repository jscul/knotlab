#!/usr/bin/env python3
"""Referee TRAVEL-READ-R1: an independent test of "bounded across" on the 66 rank-1 travelling bases, with the referee's own code
(ref_fold.py of the COMMON-FOLD referee folder for windows and torus certificates; no import of either census).

    python3 -B ref_travel.py --part second [--workers 8]     (result_second.jsonl)
    python3 -B ref_travel.py --part certified                (result_certified.json, from TRAVEL-READ's own cross.jsonl)

second:    for each rank-1 base (only one travelling direction found in the census's family of ten shifts and sets of 2 to 4 cells of
           [0, 1] x [0, 2]), search a second, independent travelling direction in a wider family: every shift (a, b) with
           0 <= a <= 4, |b| <= 4 not parallel to the first, sets A of 2 or 3 cells of [0, 2] x [0, 2] holding (0, 0), in a window
           x in [-9, 13], y in [-11, 13]; certified as in the census (p with sigma(p) carried by a torus state, A free). A second
           certified direction t2 makes bond distance bounded on the cone of t1 and t2 and its mirror (the pre-registration's
           settled cone), which would explain boundedness across by definition.
certified: the frozen T2 classes recomputed from TRAVEL-READ's cross.jsonl using only certified window bonds (uncertified ones
           treated as not found)."""
import itertools
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1] / "COMMON-FOLD-20261112-001" / "referee-R1"))
import ref_fold as F  # noqa: E402

CROSS = ROOT / "artifacts/TRAVEL-READ-20261112-001A/TRAVEL-READ-20261112-001A-E001_law_reading/cross.jsonl"
MAIN = ROOT / "artifacts/COMMON-FOLD-20261112-001A/COMMON-FOLD-20261112-001A-E001_periodic_influence/main.json"
WIDE = (-9, 13, -11, 13)
BOX3 = [(x, y) for x in range(0, 3) for y in range(0, 3)]


def kinds_of(sample, r):
    rows = json.load(open(MAIN))["rows"]
    rb = rows[sample]["by r"][str(r)]
    return [tuple(map(tuple, k)) for k in rb["kinds"]]


def second_job(item):
    sample, r, t1 = item
    t0 = time.time()
    K = kinds_of(sample, r)
    idx, cl = F.window_clauses(K, WIDE)
    shifts = [(a, b) for a in range(0, 5) for b in range(-4, 5) if (a, b) != (0, 0) and (a > 0 or b > 0)
              and a * t1[1] - b * t1[0] != 0]
    found = None
    with Glucose4(bootstrap_with=cl) as so:
        assert so.solve()
        for size in (2, 3):
            for A in itertools.combinations(BOX3, size):
                if (0, 0) not in A:
                    continue
                for tail in itertools.product((0, 1), repeat=size - 1):
                    p = (0,) + tail
                    lits = [idx[c] if v else -idx[c] for c, v in zip(A, p)]
                    if not so.solve(assumptions=lits):
                        continue
                    for t in shifts:
                        for sig in (0, 1):
                            ok = True
                            for c, v in zip(A, p):
                                tc = (c[0] + t[0], c[1] + t[1])
                                if tc not in idx:
                                    ok = False
                                    break
                                want = v ^ sig
                                if so.solve(assumptions=lits + [-idx[tc] if want else idx[tc]]):
                                    ok = False
                                    break
                            if not ok:
                                continue
                            fix = list(zip(A, p)) + [((c[0] + t[0], c[1] + t[1]), v ^ sig) for c, v in zip(A, p)]
                            if F.carried(K, fix) and all(F.carried(K, list(zip(A, (0,) + q)))
                                                         for q in itertools.product((0, 1), repeat=size - 1)):
                                found = {"A": [list(c) for c in A], "p": list(p), "t": list(t), "sigma": sig}
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break
    return {"sample": sample, "r": r, "t1": t1, "second direction": found, "seconds": round(time.time() - t0, 1)}


def classify(row, certified_only):
    """the frozen T2 rule on one cross-section: flat iff b(10, +-6) - b(10, +-2) <= 1 in every direction where both are defined and
    at least one direction is defined to +-6; line iff some difference >= 2; else open"""
    one = row["one cross-section"]

    def b(y):
        e = one.get(f"10,{y}")
        if not e or e.get("b") is None:
            return None
        if certified_only and not e.get("certified"):
            return None
        return e["b"]
    diffs, defined6 = [], False
    for sgn in (1, -1):
        b6, b2 = b(6 * sgn), b(2 * sgn)
        if b6 is not None:
            defined6 = True
        if b6 is not None and b2 is not None:
            diffs.append(b6 - b2)
    if any(d >= 2 for d in diffs):
        return "line"
    if diffs and defined6 and all(d <= 1 for d in diffs):
        return "flat"
    return "open"


def certified_part():
    rows = [json.loads(l) for l in open(CROSS)]
    out = {}
    for co in (False, True):
        c = {"flat": 0, "line": 0, "open": 0}
        for r_ in rows:
            c[classify(r_, co)] += 1
        out["certified bonds only" if co else "window bonds (frozen)"] = c
    # an upper-bound reading: a certified bond of size at most 5 holding the origin and a target at across-count 6 (either side)
    ub = 0
    for r_ in rows:
        one = r_["one cross-section"]
        if any((one.get(f"10,{y}") or {}).get("certified") and (one.get(f"10,{y}") or {}).get("b", 99) <= 5 for y in (6, -6)):
            ub += 1
    out["bases with a certified bond of at most 5 to (10, 6) or (10, -6)"] = ub
    allc = sum(1 for r_ in rows for k, e in r_["one cross-section"].items() if e and e.get("b") is not None)
    cert = sum(1 for r_ in rows for k, e in r_["one cross-section"].items() if e and e.get("b") is not None and e.get("certified"))
    out["one-cross-section bonds: found, certified"] = [allc, cert]
    return out


if __name__ == "__main__":
    part = sys.argv[sys.argv.index("--part") + 1]
    t0 = time.time()
    if part == "certified":
        res = certified_part()
        (HERE / "result_certified.json").write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps(res, indent=1))
    else:
        workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
        rows = [json.loads(l) for l in open(CROSS)]
        items = [(r_["sample"], r_["r"], tuple(r_["t"])) for r_ in rows]
        with Pool(workers) as pool, open(HERE / "result_second.jsonl", "w") as f:
            for k, rec in enumerate(pool.imap_unordered(second_job, items, chunksize=1)):
                f.write(json.dumps(rec) + "\n")
                f.flush()
                print(k + 1, rec["sample"], rec["r"], bool(rec["second direction"]), rec["seconds"], flush=True)
    print("done", part, round(time.time() - t0, 1), "s")
