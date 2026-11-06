#!/usr/bin/env python3
"""Independent re-check of NATIVE-APPROX-20261024-001C-E001's result (run after the producer).

- recomputes the table, the summary and the verdict from rows.jsonl and controls.json with the contract's rules;
- recomputes the widths of 3 seeded trees per row from their seeds and compares them with the stored widths;
- for 20 trees of depth 4 (open knots, both pin probabilities), recomputes the width with exact fractions instead of floats.

    python3 -B check_result.py
"""

from __future__ import annotations

import itertools
import json
import random
from fractions import Fraction

import run


def exact_envelope(tree, R):
    if tree[0] == "pin":
        return Fraction(tree[1]), Fraction(tree[1])
    if tree[0] == "leaf":
        return Fraction(0), Fraction(1)
    _, s, c1, c2 = tree
    o = [k for k in range(3) if k != s]
    lo1, hi1 = exact_envelope(c1, R)
    lo2, hi2 = exact_envelope(c2, R)
    vals = []
    for p1 in (lo1, hi1):
        for p2 in (lo2, hi2):
            z = [Fraction(0), Fraction(0)]
            for a, b, v in itertools.product((0, 1), repeat=3):
                t = [0, 0, 0]
                t[s], t[o[0]], t[o[1]] = v, a, b
                if tuple(t) in R:
                    z[v] += (p1 if a else 1 - p1) * (p2 if b else 1 - p2)
            vals.append(z[1] / (z[0] + z[1]))
    return min(vals), max(vals)


def main() -> int:
    rows = [json.loads(line) for line in (run.OUT / "rows.jsonl").read_text().splitlines()]
    result = json.loads((run.OUT / "result.json").read_text())
    controls = json.loads((run.OUT / "controls.json").read_text())
    table, summary = run.summarize(rows)
    ok = table == result["table"] and summary == result["summary"] and run.verdict_of(controls, summary) == result["verdict"]
    ok &= len(rows) == len(run.KNOTS) * len(run.PINS) * len(run.DEPTHS)
    replayed = 0
    for r in rows:
        for i in (0, 37, 99):
            w, _ = run.width(r["knot"], r["q"], r["L"], i)
            ok &= w == r["widths"][i]
            replayed += 1
    exact = 0
    for label in run.OPEN[:5]:
        for q in run.PINS:
            for i in (0, 1):
                tree = run.draw_tree(random.Random(run.seed_of(label, q, 4, i)), 4, q)
                lo, hi = exact_envelope(tree, run.relation(label))
                stored = [r for r in rows if r["knot"] == label and r["q"] == q and r["L"] == 4][0]["widths"][i]
                ok &= abs(float(hi - lo) - stored) < 1e-12
                exact += 1
    print(json.dumps({"table, summary and verdict reproduced; widths replayed and checked exactly": ok, "replayed widths": replayed,
                      "exact widths": exact, "verdict": result["verdict"]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
