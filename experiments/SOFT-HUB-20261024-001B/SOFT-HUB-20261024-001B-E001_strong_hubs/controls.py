#!/usr/bin/env python3
"""Controls (i) to (iii) of SOFT-HUB-20261024-001B-E001, run before the producer; writes controls.json next to the rows.
Control (iv), Lemma 2 on the enumerated pairs, is computed by the producer's pairs part and required by its verdict.

(i)   no-lone-1 knot: annealing at sizes 8 and 16 (24 seeds) and 20,000 random gadgets never exceed hub ratio 1 on any axis;
(ii)  not-all-equal: annealing at sizes 3, 8 and 16 (24 seeds) reaches hub ratio >= 4/3, and neither its annealed nor 20,000 random
      gadgets violate F(u)F(u-bar) <= s_u on any axis;
(iii) the dichotomy test flags the planted function F = [2, 1, 0, 0, 0, 0, 1, 2] on the axis 000.

    .venv/bin/python -B controls.py
"""

from __future__ import annotations

import json
import random
from multiprocessing import Pool

import run


def sample(label, count, seed):
    rng = random.Random(seed)
    R = run.relation(label)
    T = run.tensor(R, exact=True)
    worst, viol = 0.0, 0
    for _ in range(count):
        n = rng.randint(1, 16)
        a = run.random_gadget(rng, n)
        if a is None:
            continue
        F = run.as_dict(run.evaluate(T, n, a))
        worst = max(worst, max(run.ratios(F).values()))
        viol += len(run.violations(F))
    return worst, viol


def main() -> int:
    run.OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(run.NOLONE1, n, 500000 + 1000 * n + s, run.STEPS) for n in (8, 16) for s in range(24)]
    jobs += [(run.NAE, n, 500000 + 1000 * n + s, run.STEPS) for n in (3, 8, 16) for s in range(24)]
    with Pool(24) as pool:
        rows = pool.map(run.anneal, jobs)
        samp = pool.starmap(sample, [(run.NOLONE1, 1000, 600000 + c) for c in range(20)] + [(run.NAE, 1000, 700000 + c) for c in range(20)])
    fib = [r for r in rows if r["knot"] == run.NOLONE1]
    nae = [r for r in rows if r["knot"] == run.NAE]
    fib_samp, nae_samp = samp[:20], samp[20:]
    planted = {x: v for x, v in zip(run.CUBE, [2, 1, 0, 0, 0, 0, 1, 2])}
    controls = {
        "(i) no-lone-1 gadgets never exceed hub ratio 1": all(r["max_ratio"] <= 1 + 1e-12 for r in fib)
        and all(w <= 1 + 1e-12 for w, _ in fib_samp),
        "(ii) not-all-equal annealing reaches 4/3": max(r["max_ratio"] for r in nae) >= 4 / 3 - 1e-12,
        "(ii) not-all-equal gadgets never violate the split inequality": all(not r["violations"] for r in nae)
        and all(v == 0 for _, v in nae_samp),
        "(iii) the planted function is flagged": (0, 0, 0) in run.violations(planted) and run.ratios(planted)[(0, 0, 0)] > 1,
    }
    details = {"no-lone-1 best": max(max(r["max_ratio"] for r in fib), max(w for w, _ in fib_samp)),
               "not-all-equal best": max(r["max_ratio"] for r in nae)}
    (run.OUT / "controls.json").write_text(json.dumps(controls, indent=2) + "\n")
    print(json.dumps({"controls": controls, "details": details}, indent=1))
    return 0 if all(controls.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
