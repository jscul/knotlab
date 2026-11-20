"""Shared-runner job for the referee's group-2 checks (the world line of 2026-11-19), with the referee's own engine (EXPLOSIVE-R1:
the program's rule, structural implied test) and its exact least-bond MILP.  The studies' literal starts are read as data; none of
their code is run.

Parts:
- EDDY: every case of EDDY-WORLD's stages.json regrown from its age-0 supports: per-round birth counts against the study's stages,
  to its last age or 20,000 knots; the background's 17 + 2t; growth factors from the last counts.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/EXPLOSIVE-20261119-001/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
PARAMS = {}
EW = ROOT / "artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/stages.json"


def setup(params):
    PARAMS.update(params)


def part_eddy(case):
    import job_expl as JX
    d = json.load(open(EW))["cases"][case]
    st = d["stages"]
    ages = sorted(int(a) for a in st)
    theirs = [len(st[str(a)]["stars"]) - len(st[str(ages[i - 1])]["stars"]) for i, a in enumerate(ages) if i]
    G = JX.grower([list(q) for q in st[str(ages[0])]["stars"]])
    mine, end = [], "alive"
    for t in range(1, ages[-1] + 1):
        r = G.step(JX.floored, None, None)
        if r != "ok":
            end = r
            break
        mine.append(sum(1 for j in range(len(G.bits)) if G.round[j] == t))
        if len(G.bits) > 20000:
            end = "cap"
            break
    m = min(len(mine), len(theirs))
    return {"case": case, "their births per round": theirs, "mine": mine, "end": end, "termination": d["termination"],
            "agree on common rounds": mine[:m] == theirs[:m], "common rounds": m,
            "last ratios": [round(mine[i] / mine[i - 1], 4) for i in range(max(1, len(mine) - 4), len(mine)) if mine[i - 1]]}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    for c in json.load(open(EW))["cases"]:
        if only is None or f"EDDY-{c}" in only:
            yield f"EDDY-{c}", {"part": "EDDY", "case": c}


def run(case_id, p):
    return part_eddy(p["case"])
