"""Shared-runner job for the referee's check of LOOP-CATALOGUE-20261119-001's parts E and S (one start per case): every
rule-eddy and every 8th grown non-eddy (runs/loop-catalogue, read as data), regrown by the referee's own engine for up to 36
rounds or 30,000 junctions, against the study's counts.

  .venv/bin/python -B scripts/longrun.py launch research/LOOP-CATALOGUE-20261119-001/referee-R1/job_eddies.py \\
      --out runs/referee-loop-eddies --unit referee-loop-eddies --workers 6 --case-timeout 300 --case-mem 2G --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))


def cases():
    non = 0
    for line in open(ROOT / "runs/loop-catalogue/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok" or r["case"].split("-")[0] not in ("E", "S"):
            continue
        for i, g in enumerate(r["result"]["grown"]):
            if g["rule"] != "True":
                non += 1
                if non % 8:
                    continue
            yield f"{r['case']}-{i:04d}", {"sizes": g["sizes"], "edges": g["edges"], "theirs": g["counts"], "rule": g["rule"],
                                            "growth": g["growth"]}


def run(case_id, payload):
    import referee_first as RFK
    import referee_touch as RT
    sizes, edges = payload["sizes"], payload["edges"]
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RT.stars(sizes, M))
    out = "alive"
    for _ in range(36):
        if len([j for j in G.live if G.loose(j)]) > 6000:
            out = "live cap"
            break
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            out = r
            break
        if len(G.bits) > 30000:
            out = "cap"
            break
    c = G.counts()
    m = min(len(c), len(payload["theirs"]))
    return {"rule": payload["rule"], "study growth": payload["growth"], "outcome": out, "counts": c,
            "counts equal the study's": c[:m] == payload["theirs"][:m]}
