"""FULL-REACH-20261108-001A-E001: full reach on the cut-open torus (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/FULL-REACH-20261108-001A/FULL-REACH-20261108-001A-E001_cut_open_tori/
                                          run/result.json
    .venv/bin/python3 -B run.py --pilot   times sides 3 to 12 and prints no verdicts
The n x n torus of rule-60 rings with equally spaced law-(12, 12) contacts (LATTICE-NET-20261108-001A's lattice_lib), cut by the contacts
h(n - 1, j) and v(i, n - 1), a ring of cuts round it in each direction (GENUS-CUT-20261108-001A). For every uncut contact c, the rings it
needs: the contacts reached by an odd number of walks of some length avoiding the cuts, read exactly by following row c of A^k until the
next row lies in the span of the earlier ones, stopping early once every ring is covered."""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LATTICE-NET-20261108-001A/LATTICE-NET-20261108-001A-P001_odd_tori_compose_rings_of_cuts_separate"))
import lattice_lib as T  # noqa: E402

OUT = ROOT / "artifacts" / "FULL-REACH-20261108-001A" / "FULL-REACH-20261108-001A-E001_cut_open_tori" / "run"
SIDES = range(3, 49)
STATE = {}


def setup(n):
    sizes, contacts, rot, edges, ring, hidx, vidx = T.torus(n, 2)
    cut = [hidx[(n - 1, j)] for j in range(n)] + [vidx[(i, n - 1)] for i in range(n)]
    ins = T.in_sets(sizes, contacts, cut)
    rc = T.ring_contacts(rot, edges, ring)
    cutmask = sum(1 << c for c in cut)
    names = {e: ("h", p) for p, e in hidx.items()}
    names.update({e: ("v", p) for p, e in vidx.items()})
    rnames = {i: v for v, i in ring.items()}
    return ins, {r: sum(1 << d for d in cs) & ~cutmask for r, cs in rc.items()}, cut, len(contacts), names, rnames


def init(n):
    STATE["data"] = setup(n)


def missing(c):
    ins, ringmask, cut, m, names, rnames = STATE["data"]
    remaining = dict(ringmask)
    row, union, basis = 1 << c, 0, {}
    while True:
        union |= row
        for r in [r for r, msk in remaining.items() if msk & union]:
            del remaining[r]
        if not remaining:
            return c, []
        x = row
        while x:
            top = x.bit_length() - 1
            if top not in basis:
                break
            x ^= basis[top]
        if not x:
            return c, sorted(remaining)
        basis[x.bit_length() - 1] = x
        nxt, y = 0, row
        while y:
            low = y & -y
            nxt ^= ins[low.bit_length() - 1]
            y ^= low
        row = nxt


def side(n):
    ins, ringmask, cut, m, names, rnames = setup(n)
    uncut = [c for c in range(m) if c not in set(cut)]
    with Pool(16, initializer=init, initargs=(n,)) as pool:
        res = pool.map(missing, uncut, chunksize=8)
    bad = [(c, mis) for c, mis in res if mis]
    return {"uncut contacts": len(uncut), "contacts missing a ring": len(bad),
            "examples": [{"contact": "%s(%d, %d)" % (names[c][0], *names[c][1]), "rings never needed": [list(rnames[r]) for r in mis]} for c, mis in bad[:4]]}


def main():
    t0 = time.time()
    if "--pilot" in sys.argv:
        for n in range(3, 13):
            side(n)
        print("pilot: sides 3 to 12 in", round(time.time() - t0, 1), "s")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    by = {}
    for n in SIDES:
        by[str(n)] = side(n)
        print(n, by[str(n)]["contacts missing a ring"], round(time.time() - t0, 1), "s", flush=True)
    fails = [int(n) for n, v in by.items() if v["contacts missing a ring"]]
    result = {"experiment": "FULL-REACH-20261108-001A-E001", "sides": [min(SIDES), max(SIDES)], "sides where some uncut contact misses a ring": fails,
              "H1 (the failing sides are exactly the powers of two from 8: 8, 16, 32)": fails == [8, 16, 32],
              "by side": by, "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "by side"}, indent=1))


if __name__ == "__main__":
    main()
