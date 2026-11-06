#!/usr/bin/env python3
"""Independent re-check of READING-COST-20261024-001B-E001's result (run after the producer).

- recomputes the table and the verdict from rows.jsonl and controls.json with the contract's rules;
- for every misjudged (configuration, class, sheets) entry: the frozen engine walls.c reports the class as contradicting, the cover
  with that many sheets has an assignment (PySAT, checked clause by clause), and every cover with fewer sheets has none.

    .venv/bin/python -B check_result.py
"""

from __future__ import annotations

import json
import subprocess
import sys

import run
import controls


def main() -> int:
    if not controls.WALLS.exists():   # the compiled engines are build products, not kept with the artifacts
        subprocess.run(["gcc", "-O2", "-std=c99", "-o", str(controls.WALLS), str(controls.FROZEN)], check=True)
    rows = [json.loads(line) for line in (run.OUT / "rows.jsonl").read_text().splitlines()]
    result = json.loads((run.OUT / "result.json").read_text())
    table, verdicts = run.summarize(rows)
    ok = table == result["table"] and verdicts == result["summary"]
    from pysat.solvers import Cadical153
    checked = 0
    for r in rows:
        R, L, M, q = r["R"], r["L"], r["M"], tuple(r["q"])
        for x, c, m in r["misjudged"]:
            c = tuple(c)
            k = run.CLASSES.index(c)
            ok &= bool(controls.frozen_pattern(R, L, M, q, x) >> k & 1)
            n, cl, _ = run.DR.clauses(R, L, M, q, x, c, m, True)
            with Cadical153(bootstrap_with=cl) as s:
                sat = s.solve()
                model = set(v for v in (s.get_model() or []) if v > 0)
            ok &= sat and all(any((lit > 0) == (abs(lit) in model) for lit in clause) for clause in cl)
            for mm in range(1, m):
                ok &= not run.solve(run.DR.clauses(R, L, M, q, x, c, mm, True)[1])
            checked += 1
    print(json.dumps({"table and summary reproduced, misjudged entries verified": ok, "misjudged entries": checked,
                      "verdict": result["verdict"]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
