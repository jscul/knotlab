"""Readout of the referee's GROWN-PAIR check (runs/referee-grown-pair, from job_grown.py).

  ../../../.venv/bin/python -B grown_readout.py > referee_grown.json
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
rows = [json.loads(l) for l in open(ROOT / "runs/referee-grown-pair/results.jsonl")]
ok = [r["result"] for r in rows if r["status"] == "ok"]
c = Counter()
nx1, nx2 = Counter(), Counter()
mism = []
for x in ok:
    c["groups"] += 1
    c["every representative regrown to its recorded arrangement"] += all(x["regrown stage = recorded arrangement"])
    c["every start has two knots sharing two"] += all(x["start has two knots sharing two"])
    c["representatives from different starts"] += x["representatives from different starts"]
    for p in x["pairs"]:
        c["pairs"] += 1
        c["pairs: arrangements not isomorphic"] += not p["arrangements isomorphic"]
        c["pairs: tables isometric"] += p["tables isometric"]
        c["pairs: states differ (exact)"] += p["same states"] is False
        c["pairs: states undecided (search cap)"] += p["same states"] is None
    for d, cnt in (("round + 1", nx1), ("round + 2", nx2)):
        v = x["next"][d]
        if isinstance(v, str):
            cnt["out of range"] += 1
        else:
            cnt["tables isometric, states differ (every pair)"] += all(p["tables isometric"] and p["same states"] is False for p in v)
            cnt["tables differ (some pair)"] += any(not p["tables isometric"] for p in v)
            cnt["tables isometric, same states (some pair)"] += any(p["tables isometric"] and p["same states"] is True for p in v)
    st = x["study: next tables isomorphic, next states agree"]
    v = x["next"]["round + 1"]
    if not isinstance(v, str):
        mine = all(p["tables isometric"] for p in v)
        if st[0] is not None and mine != st[0]:
            mism.append(x)
print(json.dumps({"cases not ok": [r["case"] for r in rows if r["status"] != "ok"], **dict(c),
                  "next stage (round + 1)": dict(nx1), "two rounds on (round + 2)": dict(nx2),
                  "next stage: the referee's table verdict differs from the study's": len(mism)}, indent=1))
