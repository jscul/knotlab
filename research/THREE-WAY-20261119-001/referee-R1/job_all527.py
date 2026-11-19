"""Shared-runner job: the referee's forcing (referee_three.forcing) on every one of UNIQUE-TABLE's 527 population stages (start
and round read from its run records as data, the stage regrown by the referee's engine), with pairs only and with pairs and
three-way readings.  Where the forced words span the stage's equations, every code with the same readings contains them; with
UNIQUE-TABLE's bound (at most as many junctions, so no larger rank) the equations are then fixed.

  .venv/bin/python -B scripts/longrun.py launch research/THREE-WAY-20261119-001/referee-R1/job_all527.py \\
      --out runs/referee-three-way-527 --unit referee-three-way-527 --workers 6 --case-timeout 1800 --case-mem 2G --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
CASES = {}


def setup(params):
    for run in ("unique-table", "unique-table-amend2"):
        for line in open(ROOT / "runs" / run / "results.jsonl"):
            r = json.loads(line)
            if r["case"].startswith("pop") and r["status"] == "ok":
                CASES[r["case"]] = {"key": r["result"]["key"], "round": r["result"]["round"]}


def cases():
    yield from sorted(CASES.items())


def run(case_id, p):
    import referee_three as R3
    S, nb = R3.relabel(R3.stage(p["key"], p["round"]))
    bonds, K, T = R3.readings(S, nb)
    bset = set(bonds)
    f2, s2 = R3.forcing(S, nb, K, {t: 0 for t in T})
    f3, s3 = R3.forcing(S, nb, K, T)
    return {"junctions": len(S), "distinctions": nb, "pairs only spans": s2, "pairs and triples span": s3,
            "every forced word a bond": all(f in bset for f in f2 + f3)}
