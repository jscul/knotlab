"""Readout of the referee's parts E and S check (runs/referee-loop-eddies, from job_eddies.py): each start's class from the
referee's own counts (as referee_loop.classify; a start stopped at a cap with its last four ratios at least 1.2 is called
explosive), against the rule's verdict.

  ../../../.venv/bin/python -B eddies_readout.py > referee_loop_eddies.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import referee_loop as RL  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
rows = []
for line in open(ROOT / "runs/referee-loop-eddies/results.jsonl"):
    r = json.loads(line)
    x = r["result"]
    c = x["counts"]
    ratios = [c[i] / c[i - 1] for i in range(max(1, len(c) - 4), len(c)) if c[i - 1]]
    if x["outcome"] in ("cap", "live cap") and ratios and min(ratios) >= 1.2:
        cls = "explosive"
    else:
        cls = RL.classify(c, x["outcome"]).split(" (")[0]
    rows.append({"case": r["case"], "rule": x["rule"], "study": x["study growth"], "class": cls, "equal": x["counts equal the study's"]})
ed = [r for r in rows if r["rule"] == "True"]
non = [r for r in rows if r["rule"] != "True"]
print(json.dumps({"rule-eddies": len(ed), "rule-eddies: the referee's class": dict(Counter(r["class"] for r in ed)),
                  "rule-eddies: counts equal the study's": sum(r["equal"] for r in ed),
                  "non-eddies (every 8th grown)": len(non), "non-eddies: the referee's class": dict(Counter(r["class"] for r in non)),
                  "non-eddies: counts equal the study's": sum(r["equal"] for r in non),
                  "non-eddies the referee calls exponential or explosive": [r for r in non if r["class"] in ("exponential", "explosive")],
                  "eddies the referee does not call exponential": [r for r in ed if r["class"] not in ("exponential", "explosive")]}, indent=1))
