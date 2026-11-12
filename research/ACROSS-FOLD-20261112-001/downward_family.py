"""Downward heddle bonds, designed after the referee found bonds reaching rows -3 to -5 through a second along-count (not frozen).

Sheared frame of base 16. The knot {(0, r-2), (0, r), (1, r)} lets two equal values at (0, r) and (1, r) force (0, r - 2) to the
other value, two across-counts back. Chaining it: with (1, 0), (1, -2), ..., (1, -2(j-1)) equal to the origin's value in turn
forcing (0, -2), ..., (0, -2j), and two more distinctions at along-count 0 completing a triple at the bottom, the triple travels and
forces the far distinction. For |y| = 2j + 2 the set is {(0,0), (1,0), (1,-2), ..., (1,-2(j-1)), (0,-2j-2), (0,-2j-1), (k, y)}; for
|y| = 2j + 3 it is {(0,0), (1,0), ..., (1,-2j), (0,-2j-3), (0,-2j-1), (k, y)}; both of size floor((|y|+1)/2) + 3, the heddle's size at
+|y|. Checked here as bonds (refuted in a window; every proper part carried by periodic states of period 3 to 15, the audit's
certificates) for y = -3 to -10 at k = 5, 8, 11 and 20.

    .venv/bin/python -B research/ACROSS-FOLD-20261112-001/downward_family.py
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv.append("--deep")
sys.path.insert(0, HERE)
import soundness_audit as S  # noqa: E402
from pysat.solvers import Minisat22  # noqa: E402


def family(y, k):
    n = -y
    if n % 2 == 0:
        j = (n - 2) // 2
        col1 = [(1, -2 * i) for i in range(j)]
        bottom = [(0, -2 * j - 2), (0, -2 * j - 1)]
    else:
        j = (n - 3) // 2
        col1 = [(1, -2 * i) for i in range(j + 1)]
        bottom = [(0, -2 * j - 3), (0, -2 * j - 1)]
    return sorted([(0, 0)] + col1 + bottom) + [(k, y)]


def main():
    t0 = time.time()
    out = []
    for y in range(-3, -11, -1):
        for k in (5, 8, 11, 20):
            cells = family(y, k)
            idx, cl = S.C.window(-8, k + 6, y - 10, 12)
            s = Minisat22(bootstrap_with=cl)
            v = S.classify(s, idx, cells)
            s.delete()
            out.append({"y": y, "k": k, "size": len(cells), "expected size": (-y + 1) // 2 + 3, "set": cells, "verdict": v})
            print(y, k, len(cells), v, round(time.time() - t0, 1), flush=True)
    res = {"designed": "after the referee's report; not frozen", "results": out,
           "holds": all(r["verdict"] == "bond" and r["size"] == r["expected size"] for r in out), "seconds": round(time.time() - t0, 1)}
    json.dump(res, open(os.path.join(HERE, "downward_family.json"), "w"), indent=1)
    print(res["holds"])


if __name__ == "__main__":
    main()
