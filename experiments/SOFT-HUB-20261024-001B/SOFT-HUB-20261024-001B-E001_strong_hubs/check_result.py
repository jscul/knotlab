#!/usr/bin/env python3
"""Independent re-check of SOFT-HUB-20261024-001B-E001's result (run after the producer).

- recomputes the table, the summary and the verdict from rows.jsonl and controls.json with the contract's rules;
- re-evaluates every annealed gadget with a separate standard-library evaluator (dictionary-based variable elimination over Python
  integers, not numpy) and compares F;
- re-runs three sampling chunks and two pairs chunks from their seeds and compares them with the stored rows.

    .venv/bin/python -B check_result.py
"""

from __future__ import annotations

import itertools
import json

import run


def exact_F(label, n, a):
    """independent evaluator: factors as dicts {assignment tuple: count}, eliminated in order of edge index"""
    R = run.relation(label)
    factors = []
    for v in range(n):
        kinds = [a[(v, p)] for p in range(3)]
        vars_ = []
        for k in kinds:
            if k[0] == "E":
                vars_.append(("e", k[1]))
            elif k[0] == "T":
                vars_.append(("t", k[1]))
            elif k[0] == "F":
                vars_.append(("f", v, len(vars_)))
            else:
                vars_.append(None)
        tab = {}
        uniq = sorted({x for x in vars_ if x is not None}, key=str)
        for vals in itertools.product((0, 1), repeat=len(uniq)):
            asg = dict(zip(uniq, vals))
            t = tuple(asg[x] if x is not None else kinds[p][1] for p, x in enumerate(vars_))
            if t in R:
                tab[vals] = tab.get(vals, 0) + 1
        factors.append((uniq, tab))
    elim = sorted({x for vs, _ in factors for x in vs if x[0] != "t"}, key=str)
    for x in elim:
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
                if prod == 0:
                    break
            if prod:
                k = tuple(asg[y] for y in outv)
                tab[k] = tab.get(k, 0) + prod
        rest.append((outv, tab))
        factors = rest
    F = {}
    for x in run.CUBE:
        asg = {("t", k): x[k] for k in range(3)}
        prod = 1
        for vs, tb in factors:
            prod *= tb.get(tuple(asg[y] for y in vs), 0)
        F[x] = prod
    return [F[x] for x in run.CUBE]


def main() -> int:
    rows = [json.loads(line) for line in (run.OUT / "rows.jsonl").read_text().splitlines()]
    result = json.loads((run.OUT / "result.json").read_text())
    controls = json.loads((run.OUT / "controls.json").read_text())
    table, summary = run.summarize(rows)
    ok = table == result["table"] and summary == result["summary"] and run.verdict_of(controls, summary) == result["verdict"]
    checked = 0
    for r in rows:
        if r["part"] == "anneal":
            n, a = run.gadget_from_json(r["gadget"])
            ok &= exact_F(r["knot"], n, a) == r["F"]
            checked += 1
    jobs = run.jobs()
    replay = [j for j in jobs if j[0] == "sample"][:3] + [j for j in jobs if j[0] == "pairs"][:2]
    stored = {run.key(r): r for r in rows}
    for kind, args in replay:
        fresh = run.run_job((kind, args))
        ok &= fresh == stored[run.key(fresh)]
    print(json.dumps({"table, summary and verdict reproduced; annealed gadgets re-evaluated; chunks replayed": ok,
                      "annealed gadgets re-evaluated": checked, "chunks replayed": len(replay), "verdict": result["verdict"]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
