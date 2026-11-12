#!/usr/bin/env python3
"""Referee OLD-CORE-R1, the "critical closing rate between 0.25 and 0.3" against the horizon: X(0.2), X(0.25) and X(0.3) grown to
20,000 moves (fresh seeds, sha256 of "OC-R1:label:run"), 40 growths each, with RANDOM-FATES-R1's generator; the share that has ended
by 2,000, 4,000, 6,000, 10,000, 15,000 and 20,000 moves. A rate below the critical one should show no growing share of endings with
the horizon.

    python3 -B ref_horizon.py [workers]      (writes result_horizon.json)"""
import json
import random
import sys
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "RANDOM-FATES-20261112-001" / "referee-R1"))
import ref_fates as RF  # noqa: E402

MARKS = (2000, 4000, 6000, 10000, 15000, 20000)


def job(arg):
    label, run = arg
    rng = random.Random(RF.seed_of("OC-R1", label, run))
    g = RF.make(label, rng)
    with Glucose4() as s:
        for move in range(1, MARKS[-1] + 1):
            t = next(g)
            if t is None:
                continue
            for c in RF.nae_clauses(t):
                s.add_clause(c)
            if not s.solve():
                return label, run, move
    return label, run, None


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    args = [(lab, r) for lab in ("X0.2", "X0.25", "X0.3") for r in range(40)]
    with Pool(workers) as pool:
        res = pool.map(job, args, chunksize=1)
    out = {}
    for lab in ("X0.2", "X0.25", "X0.3"):
        ends = [m for l, r, m in res if l == lab]
        out[lab] = {str(h): sum(1 for m in ends if m is not None and m <= h) for h in MARKS}
        out[lab]["growths"] = len(ends)
    (HERE / "result_horizon.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
