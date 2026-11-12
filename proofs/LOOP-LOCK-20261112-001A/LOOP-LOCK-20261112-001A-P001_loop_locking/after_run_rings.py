#!/usr/bin/env python3
"""After the run, descriptive (not frozen): for the one-shift ring of n knots (j, j+1, j+2) under one-order stitches, the ring's states
are the closed walks of length n of the transfer on pairs of states, (u, v) -> (v, w) when (u, v, w) is allowed across one knot (the
advisor's). The ring locks every copy into one state exactly when no closed walk of length n visits a pair (u, v) with u != v. This
lists, for each harmony of the overlap arm, the lengths n up to 60 with such a walk, so as to say whether locking on rings is bounded
or holds at every length in some residue class.

    .venv/bin/python3 -B after_run_rings.py"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import loop_lib as L  # noqa: E402

NMAX = 60


def off_diagonal_lengths(h):
    W, R, T = L.relation(h)
    n = len(W)
    pairs = [(u, v) for u in range(n) for v in range(n)]
    idx = {p: i for i, p in enumerate(pairs)}
    M = np.zeros((len(pairs), len(pairs)), dtype=bool)
    for (u, v, w) in R:
        M[idx[(u, v)], idx[(v, w)]] = True
    off = [idx[(u, v)] for (u, v) in pairs if u != v]
    lengths = []
    P = np.eye(len(pairs), dtype=bool)
    for k in range(1, NMAX + 1):
        P = (P.astype(np.uint8) @ M.astype(np.uint8)) > 0
        if any(P[i, i] for i in off):
            lengths.append(k)
    return lengths


if __name__ == "__main__":
    ov = json.loads((HERE / "result_overlap.json").read_text())["checks"]["result"]
    hs = L.E.harmonies()
    rows = []
    for n in ov["harmonies"]:
        h = hs[n]
        if len(L.E.N.states(h)) > 20:
            rows.append({"harmony": h["orbits"], "skipped": "more than 20 states"})
            continue
        ls = off_diagonal_lengths(h)
        locks = [k for k in range(3, NMAX + 1) if k not in ls]
        rows.append({"harmony": h["orbits"], "P": h["P"], "lengths with an unlocking walk": ls, "ring lengths 3..60 that lock": locks})
        print("+".join(h["orbits"])[:40], "P", h["P"], "locks at", locks[:30], "..." if len(locks) > 30 else "")
    (HERE / "result_after_run_rings.json").write_text(json.dumps({"status": "descriptive, after the run", "rows": rows}, indent=1) + "\n")
