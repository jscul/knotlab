"""Exploratory, designed after FAR-BOUND-20261112-001A's recheck (not frozen, not certified): on TRAVEL-READ's 66 rank-1 bases, a
pattern on 2 to 4 cells of [0, 1] x [0, 2] forcing its own translate (window SAT only) along any primitive shift (a, b) with
0 <= a <= 6, |b| <= 6, or a multiple up to 4 of it; the rank of the directions found. Used only to compare with the far-range
outcome; a certified search with a different family is the referee's (TRAVEL-READ-R1).

    .venv/bin/python -B research/FAR-BOUND-20261112-001/second_direction.py
Output: research/FAR-BOUND-20261112-001/second_direction.json
"""
import sys, json, itertools, math, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments/TRAVEL-READ-20261112-001A/TRAVEL-READ-20261112-001A-E001_law_reading"))
import census as T
C = T.C
from pysat.solvers import Minisat22
from multiprocessing import Pool
SH = [(a, b) for a in range(0, 7) for b in range(-6, 7) if (a, b) != (0, 0) and (a > 0 or b > 0) and math.gcd(a, abs(b)) == 1]
def job(key):
    sm = SMS[key]; kinds = sm["kinds"]
    idx, cl = C.window(kinds, (-16, 22, -18, 24)); s = Minisat22(bootstrap_with=cl)
    found = set()
    for size in range(2, 5):
        for A in itertools.combinations(C.BOX, size):
            if (0, 0) not in A: continue
            for tail in itertools.product((0, 1), repeat=size - 1):
                p = (0,) + tail; assum = [idx[c] * (1 if v else -1) for c, v in zip(A, p)]
                if not s.solve(assumptions=assum): continue
                for t in SH:
                    if t in found: continue
                    for k in (1, 2, 3, 4):
                        tt = (t[0] * k, t[1] * k)
                        done = False
                        for fl in (0, 1):
                            if all((c[0] + tt[0], c[1] + tt[1]) in idx and not s.solve(assumptions=assum + [idx[(c[0] + tt[0], c[1] + tt[1])] * (-1 if (v ^ fl) else 1)]) for c, v in zip(A, p)):
                                found.add(t); done = True; break
                        if done: break
    s.delete()
    ds = sorted(found)
    rank = 2 if any(a[0] * b[1] - a[1] * b[0] for a, b in itertools.combinations(ds, 2)) else (1 if ds else 0)
    return key, rank, ds
SMS = {(x["sample"], x["r"]): x for x in T.samples()}
if __name__ == "__main__":
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "artifacts/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/recheck.jsonl"))]
    cls = {(r["sample"], r["r"]): r.get("class") for r in rows}
    from collections import Counter
    tally = Counter()
    RES = {}
    with Pool(4) as p:
        for key, rank, ds in p.imap_unordered(job, list(cls)):
            tally[(cls[key], rank)] += 1
            RES[key] = [rank, ds]
            if cls[key] == "growing across": print(key, rank, ds, flush=True)
    print(dict(tally))
    json.dump({f"{k[0]},{k[1]}": v for k, v in RES.items()}, open(os.path.join(ROOT, "research/FAR-BOUND-20261112-001/second_direction.json"), "w"))
