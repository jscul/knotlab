"""Shared-runner job for the referee's check of JUNCTION-MAP-20261119-001.  For each of the study's 94 starts (sizes and touches
read from runs/junction-map as data): the referee grows the start with its own engine (complete rounds, fewest counts, GF(2)
implication) and takes its stage after s = 1, 2, 3 rounds as a start (junction sizes and shared distinctions).  The object under
test, the study's junction map (maplib.lifted_analyse and maplib.lifted, run read-only), reads that stage; its status (clean,
overlap, a break, or a stall) and its predicted counts are compared with the referee's continued growth for up to 8 rounds:
the first round at which they differ.

  .venv/bin/python -B scripts/longrun.py launch research/JUNCTION-MAP-20261119-001/referee-R1/job_jmap.py \\
      --out runs/referee-jmap --unit referee-jmap --workers 6 --case-timeout 1800 --case-mem 2G --mem-max 16G
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
MAP = ROOT / "experiments/JUNCTION-MAP-20261119-001B/JUNCTION-MAP-20261119-001B-E001_map"
CASES = {}


def setup(params):
    for line in open(ROOT / "runs/junction-map/results.jsonl"):
        r = json.loads(line)
        if r["status"] == "ok":
            CASES[r["case"]] = {"sizes": r["result"]["sizes"], "edges": r["result"]["edges"],
                                "study": [[s["s"], s["status"], s["map"]] for s in r["result"]["stages"]]}


def cases():
    yield from sorted(CASES.items())


def run(case_id, p):
    import referee_first as RFK
    import referee_touch as RT
    sys.path.insert(0, str(MAP))
    import maplib as M
    E = M.SL.E
    n = len(p["sizes"])
    Mx = [[0] * n for _ in range(n)]
    for a, b in p["edges"]:
        Mx[a][b] += 1
        Mx[b][a] += 1
    S0 = RT.stars(p["sizes"], Mx)
    out = []
    for s in (1, 2, 3):
        G = RFK.Start(S0)
        if not all(G.step(RFK.fewest, None, None) == "ok" for _ in range(s)):
            break
        own = defaultdict(list)
        for j, b in enumerate(G.bits):
            for x in b:
                own[x].append(j)
        sz = [len(b) for b in G.bits]
        e = sorted(tuple(sorted(o)) for o in own.values() if len(o) == 2)
        A = M.lifted_analyse(sz, e)
        A0 = E.Cl.analyse(sz, e)
        status = "stall" if A0.get("stall") else ("clean" if A0["scope"] and E.exact(A0) else ("overlap" if not A0["scope"] else "break"))
        H = RFK.Start([list(b) for b in G.bits])
        grown = []
        for _ in range(8):
            if H.step(RFK.fewest, None, None) != "ok" or len(H.bits) > 60000:
                break
            grown.append(sum(1 for j in range(len(H.bits)) if H.round[j] == H.rounds))
        pred = M.lifted(sz, e, len(grown) + 1)
        pred = pred[1:] if isinstance(pred, list) else pred
        if isinstance(pred, list):
            k = min(len(pred), len(grown))
            first = next((i for i in range(k) if pred[i] != grown[i]), None)
        else:
            first, k = str(pred), 0
        out.append({"s": s, "status": status, "lifted scope": A.get("scope"), "first difference": first, "rounds compared": k,
                    "map": pred[:4] if isinstance(pred, list) else pred, "growth": grown[:4]})
    return {"stages": out, "study": p["study"]}
