"""Referee R1 for WEAVE-LAWS-20261117-001: periodic mixes, a law on a larger cell (own code; a probe, not a study).

  .venv/bin/python -B referee_periodic.py > referee_periodic.json

The up knot at every (i, j) with i and j both divisible by p is one signed not-all-equal knot (p1, p2 or p3); every other knot is
NAE (one knot in 2p^2 is signed).  This is one knot pattern repeated on a p x p cell, so it is a law with a larger cell.  The
p-row transfer T_0 T_1 ... T_{p-1} on the cylinder of width w (a multiple of p) gives states per distinction and the gap per
row, log_3(lambda_0 / |lambda_1|) / p, from the dense spectrum of its live part.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

from referee_scope import PAIRS, strip


def cell_transfer(w, p, defect):
    M = None
    for j in range(p):
        ups = [PAIRS[defect] if (i % p == 0 and j == 0) else PAIRS["NAE"] for i in range(w)]
        T = strip(w, ups, [PAIRS["NAE"]] * w).astype(np.float64)   # counts stay far below 2^53: float BLAS is exact here
        M = T if M is None else M @ T
    return M


def read(w, p, defect):
    M = cell_transfer(w, p, defect)
    supp = M > 0
    k = np.ones(len(M), bool)
    while k.any():
        sub = supp[np.ix_(k, k)]
        good = sub.any(axis=1) & sub.any(axis=0)
        if good.all():
            break
        k[np.flatnonzero(k)[~good]] = False
    if not k.any():
        return {"width": w, "dead": True}
    m = np.sort(np.abs(np.linalg.eigvals(M[np.ix_(k, k)])))[::-1]
    lam1 = next((x for x in m if x < m[0] * (1 - 1e-9)), None)
    g = None if not lam1 else math.log(m[0] / lam1, 3) / p
    return {"width": w, "live_rows": int(k.sum()), "per_site": float(m[0] ** (1 / (w * p))), "gap_per_row": g,
            "gap_x_width": None if g is None else g * w}


def main():
    out = {}
    plan = {(2, "p1"): (4, 6, 8, 10), (2, "p2"): (4, 6, 8, 10), (2, "p3"): (4, 6, 8, 10, 12),
            (3, "p1"): (6, 9), (3, "p2"): (6, 9), (3, "p3"): (6, 9)}     # width 12 (dense 4,096) only where it decides
    for (p, d), widths in plan.items():
        out[f"period {p}, {d} up at one corner"] = rows = []
        for w in widths:
            rows.append(read(w, p, d))
            print(p, d, json.dumps(rows[-1]), file=sys.stderr, flush=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
