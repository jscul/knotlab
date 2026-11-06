#!/usr/bin/env python3
"""Controls (i) to (iii) of LOOP-HUB-20261025-001A-E001, run before the producer; control (iv) is computed by the pairs part.

(i)   annealing restricted to tree gadgets at sizes 8 and 16 (24 seeds) never exceeds lhs/rhs = 1;
(ii)  the annealer reaches lhs/rhs = 1 exactly at sizes 4, 8 and 12 (8 seeds each);
(iii) the planted function [10, 1, 1, 1, 1, 1, 1, 10] is flagged as a violation.

    .venv/bin/python -B controls.py
"""

from __future__ import annotations

import json
from multiprocessing import Pool

import run


def main() -> int:
    run.OUT.mkdir(parents=True, exist_ok=True)
    tree_jobs = [(n, 800000 + 1000 * n + s, run.STEPS, 0.5, True) for n in (8, 16) for s in range(24)]
    eq_jobs = [(n, 900000 + 1000 * n + s, run.STEPS, 0.3 if s % 2 == 0 else 0.75, False) for n in (4, 8, 12) for s in range(8)]
    with Pool(24) as pool:
        trees = pool.map(run.anneal, tree_jobs)
        eqs = pool.map(run.anneal, eq_jobs)
    planted = dict(zip(run.CUBE, [10, 1, 1, 1, 1, 1, 1, 10]))
    reached = {n: any(r["max_lhs_over_rhs"] == 1.0 for r in eqs if r["n"] == n) for n in (4, 8, 12)}
    controls = {
        "(i) tree gadgets never exceed lhs/rhs = 1": all(r["max_lhs_over_rhs"] <= 1.0 for r in trees),
        "(ii) the annealer reaches equality at sizes 4, 8 and 12": all(reached.values()),
        "(iii) the planted function is flagged": run.max_ratio(planted)[0] > 1,
    }
    (run.OUT / "controls.json").write_text(json.dumps(controls, indent=2) + "\n")
    print(json.dumps({"controls": controls, "tree best": max(r["max_lhs_over_rhs"] for r in trees), "reached": reached}, indent=1))
    return 0 if all(controls.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
