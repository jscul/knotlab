"""Shared-runner job: the three shapes the referee's six-knot search found fast and the catalogue's verdict calls 'no eddy'
(outside the rule's scope, no loop through distinct blocks), one representative spare placement each, at the study's own sizes
(read from referee_loop_newshapes.json); grown by the referee's engine round by round to 36 rounds, stopping before a round with
more than 1,500 live junctions or past 20,000 junctions.

  .venv/bin/python -B scripts/longrun.py launch research/LOOP-CATALOGUE-20261119-001/referee-R1/job_newshapes.py \\
      --out runs/referee-loop-newshapes --unit referee-loop-newshapes --workers 3 --case-timeout 300 --case-mem 3G --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))


def cases():
    d = json.load(open(HERE / "referee_loop_newshapes.json"))
    seen = set()
    for x in d["catalogue's verdict False but fast"]:
        k = len(x["edges"])
        if k in seen:
            continue
        seen.add(k)
        yield f"edges{k}", {"sizes": x["study sizes"], "edges": x["edges"], "spares": x["spares"]}


def run(case_id, p):
    import referee_first as RFK
    import referee_touch as RT
    sizes, edges = p["sizes"], p["edges"]
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RT.stars(sizes, M))
    out = "alive"
    for _ in range(36):
        if len([j for j in G.live if G.loose(j)]) > 1500:
            out = "live cap"
            break
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            out = r
            break
        if len(G.bits) > 20000:
            out = "cap"
            break
    return {"edges": edges, "spares": p["spares"], "sizes": sizes, "outcome": out, "counts": G.counts()}
