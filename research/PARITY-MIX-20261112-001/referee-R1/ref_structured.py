#!/usr/bin/env python3
"""Referee PARITY-MIX-R1, structured placements beyond 4 x 4: does a state survive on n x n (n = 3 to 8) for each harmony with a
flip-blind triple, when the parity knots are (a) one knot, (b) the star of one copy (the three knots that hold it: cells (0, 0),
(0, n - 1), (n - 1, 0)), (c) the stars of two copies at every offset, (d) the stars of every copy in one count (a ring of stars along
the second copy shift)? Tests whether "no survivor in the 8 x 8 samples" means rare or absent. Uses ref_parity_fast.py's lighter check.

    python3 -B ref_structured.py      (writes result_structured.json)"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_parity as RP  # noqa: E402
import ref_parity_fast as F  # noqa: E402
from pysat.solvers import Glucose4  # noqa: E402


def alive(st, n, K):
    with Glucose4(bootstrap_with=F.light_cnf(st, n, frozenset(K))) as s:
        return s.solve()


def star(n, r, c):
    cell = lambda a, b: (a % n) * n + (b % n)
    return {cell(r, c), cell(r, c - 1), cell(r - 1, c)}


def main():
    t0 = time.time()
    census = json.loads((HERE / "result_census.json").read_text())["rows"]
    pick = [i for i, r in enumerate(census) if r["flip-blind triples"]]
    out = []
    for i in pick:
        st = RP.setup(RP.hs()[i])
        for n in range(3, 9):
            row = {"harmony": st["name"], "n": n}
            row["one knot"] = alive(st, n, [0])
            K1 = star(n, 0, 0)
            row["one star"] = alive(st, n, K1)
            two = {}
            for dr in range(n):
                for dc in range(n):
                    if (dr, dc) == (0, 0):
                        continue
                    K = frozenset(K1 | star(n, dr, dc))
                    two[f"{dr},{dc}"] = [len(K), alive(st, n, K)]
            row["two stars (offset: k, state)"] = two
            ring = frozenset(set().union(*(star(n, 0, c) for c in range(n))))
            row["stars of one count (k, state)"] = [len(ring), alive(st, n, ring)]
            out.append(row)
            print(st["name"][:40], n, row["one knot"], row["one star"], sum(v[1] for v in two.values()), "of", len(two),
                  row["stars of one count (k, state)"], round(time.time() - t0), "s", flush=True)
            (HERE / "result_structured.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
