"""Shared-runner job: one size past GROWN-PAIR.  Every grown stage of 15 and 16 junctions (rounds 1 to 8, the census's starts,
complete rounds) was rebuilt by GROWN-PAIR-R1's job_meetonce.py (--param all=1) into runs/referee-three-way-past, and grouped by
exact table and exact states by its job_meetonce_groups.py into runs/referee-three-way-past-groups.  Here, for each table group
with two or more state groups: whether its arrangements meet once, and, for every two state groups, an exact search for a renaming
that keeps the pair table, and one that keeps pairs and three-way readings.

  .venv/bin/python -B scripts/longrun.py launch research/THREE-WAY-20261119-001/referee-R1/job_past.py \\
      --out runs/referee-three-way-past-triples --unit referee-three-way-past-triples --workers 6 --case-timeout 1800 \\
      --case-mem 2G --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
CASES = {}


def setup(params):
    k = 0
    for line in open(ROOT / "runs/referee-three-way-past-groups/results.jsonl"):
        for g in json.loads(line)["result"]["table groups"]:
            if g["state groups"] > 1:
                CASES[f"past-{k:03d}"] = {"group": g}
                k += 1


def cases():
    yield from CASES.items()


def run(case_id, p):
    import referee_three as R3
    from job_meetonce import meet_once
    g = p["group"]
    reps = [g["stars"][m[0]] for m in g["state group members"]]
    nb = g["distinctions"]
    rd = [R3.readings(A, nb)[1:] for A in reps]
    out = []
    for a in range(len(reps)):
        for b in range(a + 1, len(reps)):
            (KA, TA), (KB, TB) = rd[a], rd[b]
            out.append({"pairs kept by a renaming": R3.iso_both(KA, KB, {t: 0 for t in TA}, {t: 0 for t in TB}, nb),
                        "pairs and triples kept by a renaming": R3.iso_both(KA, KB, TA, TB, nb)})
    return {"distinctions": nb, "junctions": [len(A) for A in reps], "state groups": len(reps),
            "meet once": [meet_once(A) for A in g["stars"]], "provenance": g["provenance"], "pairs": out}
