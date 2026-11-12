#!/usr/bin/env python3
"""Referee SHIFT-COUNT-R1, ticket C on base 16 with the referee's own code: base 16's kinds {0, (0,1), (1,-1)} and {0, (0,2), (1,1)}
(standard coordinates), in the sheared frame (alpha, y) of standard (alpha, y - alpha): {0, (0,1), (1,0)} and {0, (0,2), (1,2)}. The
part {(0,0), (0,-1), (0,1), (0,5), (8,5)} (frame) with patterns 00001 and 00010. For every lattice <(n, 0), (k, m)> of the frame,
n, m <= 24, 0 <= k < n: is the pattern carried by a state invariant under the lattice? And is it carried by a two-way eventually
periodic state (ref_shiftcount.py's certificate in the frame of (1, -1))? Also, for the base's states on every such lattice, whether
any state exists at all (so that an empty C is not just an empty base).

    python3 -B ref_lattices.py      (writes result_lattices.json)"""
import json
import sys
import time
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_shiftcount as S  # noqa: E402

FK = [((0, 0), (0, 1), (1, 0)), ((0, 0), (0, 2), (1, 2))]
STD = [((0, 0), (0, 1), (1, -1)), ((0, 0), (0, 2), (1, 1))]
PART = [(0, 0), (0, -1), (0, 1), (0, 5), (8, 5)]
PATTERNS = [(0, 0, 0, 0, 1), (0, 0, 0, 1, 0)]
NMAX = 24


def red(a, b, n, k, m):
    j = b // m
    return ((a - j * k) % n, b - j * m)


def lattice_cnf(n, k, m):
    idx = {(a, b): a * m + b + 1 for a in range(n) for b in range(m)}
    cl = []
    for (a, b) in idx:
        for kd in FK:
            v = [idx[red(a + dx, b + dy, n, k, m)] for dx, dy in kd]
            if len(set(v)) == 1:
                return idx, None                         # a knot on one cell: no state
            cl += [v, [-x for x in v]]
    return idx, cl


def main():
    t0 = time.time()
    out = {"lattices": 0, "lattices with a state": 0}
    carry = {str(p): [] for p in PATTERNS}
    for n in range(1, NMAX + 1):
        for m in range(1, NMAX + 1):
            for k in range(n):
                out["lattices"] += 1
                idx, cl = lattice_cnf(n, k, m)
                if cl is None:
                    continue
                with Solver(name="cadical153", bootstrap_with=cl) as s:
                    if not s.solve():
                        continue
                    out["lattices with a state"] += 1
                    imgs = [idx[red(a, b, n, k, m)] for a, b in PART]
                    for p in PATTERNS:
                        lits = [w if v else -w for w, v in zip(imgs, p)]
                        if any(-x in lits for x in lits):
                            continue
                        if s.solve(assumptions=lits):
                            carry[str(p)].append([n, k, m])
        print(n, round(time.time() - t0), "s", flush=True)
    out["C (lattices carrying the pattern)"] = {p: len(v) for p, v in carry.items()}
    out["C sample"] = {p: v[:10] for p, v in carry.items()}
    std = [(a, b - a) for a, b in PART]       # frame (alpha, y) -> standard (alpha, y - alpha)
    out["carried by a two-way eventually periodic state (frame of (1, -1))"] = {
        str(p): S.eventual_carries(STD, list(zip(std, p)), (1, -1)) for p in PATTERNS}
    (HERE / "result_lattices.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "C sample"}, indent=1))


if __name__ == "__main__":
    main()
