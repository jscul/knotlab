#!/usr/bin/env python3
"""Stress test for TIE-LAW-20261109-001 (TIE-LAW-S1 in docs/LONG_RUNNING.md): attainment of the tie at tau one size past the covers
read, on types whose balls to tau exceed two million contacts: (8, 12), (6, 10), (5, 7), (4, 9) and (6, 7), one prime each, read to
radius tau with a cap of 30 million contacts. Theorem 2 already proves that no tie comes earlier; this reads whether one comes at tau.
Writes stress_test.json after each type.

    .venv/bin/python3 -B stress_test.py"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/TIE-LAW-20261109-001A/TIE-LAW-20261109-001A-P001_no_tie_comes_before_tau"))
import tie_lib as T  # noqa: E402

OUT = HERE / "stress_test.json"


def main():
    res = {}
    for m, f in ((8, 12), (6, 10), (5, 7), (4, 9), (6, 7)):
        t0 = time.time()
        tau = T.tau_formula(m, f)
        p = T.prime_for(m, f, 10 ** 7)
        ties, reached = T.first_tie(m, f, p, tau, limit=30_000_000)
        first = min(ties) if ties else None
        res[f"{m},{f}"] = {"tau": tau, "p": p, "radius read": reached, "first tie": first, "at first": ties.get(first),
                           "pass": (first == tau) if reached >= tau else None, "seconds": round(time.time() - t0)}
        done = [v["pass"] for v in res.values()]
        OUT.write_text(json.dumps({"types": res, "pass": all(v is True for v in done) if None not in done else "partial"}, indent=1) + "\n")
        print(m, f, res[f"{m},{f}"], flush=True)


if __name__ == "__main__":
    main()
