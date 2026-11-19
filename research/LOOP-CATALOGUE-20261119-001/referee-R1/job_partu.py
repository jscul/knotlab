"""Shared-runner job for the referee's part U check of LOOP-CATALOGUE-20261119-001 (one start per case, so the runner's per-case
memory limit isolates an explosive growth; the first in-process run of this check held too much memory and was stopped).

The starts: every part U start (runs/loop-catalogue, read as data) with a meeting group of three that the study classes as
exponential, and every exponential six-knot start (the theta).  Each is grown by the referee's own engine (FRESH-COUNT-R1 /
FIRST-KNOT-R1) for up to 36 rounds, stopping at 30,000 junctions or before a round with more than 6,000 live junctions.

  python3 -B scripts/longrun.py launch research/LOOP-CATALOGUE-20261119-001/referee-R1/job_partu.py \\
      --out runs/referee-loop-partu --unit referee-loop-partu --workers 6 --case-timeout 300 --case-mem 2G --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))


ONLY = None


def setup(params):
    global ONLY
    if params.get("only"):
        ONLY = set(params["only"].split(","))


def cases():
    for cid, p in _all():
        if ONLY is None or cid in ONLY:
            yield cid, p


def _all():
    for line in open(ROOT / "runs/loop-catalogue/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok" or not r["case"].startswith("U-"):
            continue
        for i, s in enumerate(r["result"]["starts"]):
            exp = str(s.get("growth", "")).startswith("exp")
            if exp and (s.get("meet") or s["n"] == 6):
                yield f"{r['case']}-{i:03d}", {"sizes": s["sizes"], "edges": s["edges"], "theirs": s["counts"], "growth": s["growth"],
                                               "meet": bool(s.get("meet")), "n": s["n"]}


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
    return {"n": payload["n"], "meet": payload["meet"], "study growth": payload["growth"], "outcome": out, "counts": c,
            "counts equal the study's": c[:m] == payload["theirs"][:m]}
