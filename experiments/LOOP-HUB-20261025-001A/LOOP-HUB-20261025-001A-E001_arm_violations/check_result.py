#!/usr/bin/env python3
"""Independent re-check of LOOP-HUB-20261025-001A-E001's result (run after the producer).

- recomputes the table, summary and verdict from rows.jsonl and controls.json;
- re-evaluates every annealed gadget's F with an independent dictionary-based evaluator and recomputes its largest lhs/rhs with exact
  fractions;
- replays one chains row, one cores row and two pairs chunks from their seeds.

    .venv/bin/python -B check_result.py
"""

from __future__ import annotations

import json
from fractions import Fraction

import run

def independent_F(n, a):
    """dictionary-based variable elimination over Python integers (independent of the numpy evaluator)"""
    import itertools
    R = run.R
    factors = []
    for v in range(n):
        kinds = [a[(v, p)] for p in range(3)]
        vars_ = [("e", k[1]) if k[0] == "E" else ("t", k[1]) if k[0] == "T" else ("f", v, p) if k[0] == "F" else None
                 for p, k in enumerate(kinds)]
        uniq = sorted({x for x in vars_ if x is not None}, key=str)
        tab = {}
        for vals in itertools.product((0, 1), repeat=len(uniq)):
            asg = dict(zip(uniq, vals))
            if tuple(asg[x] if x is not None else kinds[p][1] for p, x in enumerate(vars_)) in R:
                tab[vals] = tab.get(vals, 0) + 1
        factors.append((uniq, tab))
    for x in sorted({x for vs, _ in factors for x in vs if x[0] != "t"}, key=str):
        inv = [f for f in factors if x in f[0]]
        rest = [f for f in factors if x not in f[0]]
        allv = sorted({y for vs, _ in inv for y in vs}, key=str)
        outv = [y for y in allv if y != x]
        tab = {}
        for vals in itertools.product((0, 1), repeat=len(allv)):
            asg = dict(zip(allv, vals))
            prod = 1
            for vs, tb in inv:
                prod *= tb.get(tuple(asg[y] for y in vs), 0)
                if not prod:
                    break
            if prod:
                key_ = tuple(asg[y] for y in outv)
                tab[key_] = tab.get(key_, 0) + prod
        rest.append((outv, tab))
        factors = rest
    out = []
    for xx in run.CUBE:
        asg = {("t", k): xx[k] for k in range(3)}
        prod = 1
        for vs, tb in factors:
            prod *= tb.get(tuple(asg[y] for y in vs), 0)
        out.append(prod)
    return out


def main() -> int:
    rows = [json.loads(line) for line in (run.OUT / "rows.jsonl").read_text().splitlines()]
    result = json.loads((run.OUT / "result.json").read_text())
    controls = json.loads((run.OUT / "controls.json").read_text())
    table, summary = run.summarize(rows)
    ok = table == result["table"] and summary == result["summary"] and run.verdict_of(controls, summary) == result["verdict"]
    checked = 0
    for r in rows:
        if r["part"] != "anneal":
            continue
        n, a = run.H.gadget_from_json(r["gadget"])
        F = independent_F(n, a)
        ok &= F == r["F"]
        Fd = dict(zip(run.CUBE, F))
        best = Fraction(0)
        for u in run.AXES:
            for i in range(3):
                lhs, rhs = run.arm_sides(Fd, u, i)
                if lhs and rhs:
                    best = max(best, Fraction(lhs, rhs))
        ok &= float(best) == r["max_lhs_over_rhs"] or (best == 0 and r["max_lhs_over_rhs"] == 0.0)
        checked += 1
    jobs = run.jobs()
    replay = [j for j in jobs if j[0] == "chains"][:1] + [j for j in jobs if j[0] == "cores"][:1] + [j for j in jobs if j[0] == "pairs"][:2]
    stored = {run.key(r): r for r in rows}
    for job in replay:
        fresh = run.run_job(job)
        ok &= fresh == stored[run.key(fresh)]
    print(json.dumps({"table, summary and verdict reproduced; annealed gadgets re-evaluated; rows replayed": ok,
                      "annealed gadgets re-evaluated": checked, "rows replayed": len(replay), "verdict": result["verdict"]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
