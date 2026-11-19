"""Readout of the referee's part U run (runs/referee-loop-partu, from job_partu.py): each start's class from the referee's own
counts.  A tail is quasi-polynomial when (1 - y^p)^k annihilates its last 15 rounds for some p <= 12, k <= 5; a start that stops at
a junction or live cap, or at its 2 GB case limit, with every one of its last four ratios at least 1.2 is called explosive; one
that is neither, with at least 18 rounds, is called exponential.

  ../../../.venv/bin/python -B partu_readout.py > referee_loop_partu.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import referee_loop as RL  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
rows = []
for line in open(ROOT / "runs/referee-loop-partu/results.jsonl"):
    r = json.loads(line)
    if r["status"] != "ok":
        rows.append({"case": r["case"], "class": f"case limit reached ({r['status']})"})
        continue
    x = r["result"]
    c = x["counts"]
    ratios = [c[i] / c[i - 1] for i in range(max(1, len(c) - 4), len(c)) if c[i - 1]]
    if x["outcome"] in ("cap", "live cap") and ratios and min(ratios) >= 1.2:
        cls = "explosive"
    elif len(c) >= 18:
        cls = RL.quasi_poly(c).split(" (")[0]
    else:
        cls = f"short ({x['outcome']})"
    rows.append({"case": r["case"], "n": x["n"], "meet": x["meet"], "study": x["study growth"], "class": cls, "rounds": len(c) - 1,
                 "outcome": x["outcome"], "counts equal the study's": x["counts equal the study's"],
                 "last ratio": round(c[-1] / c[-2], 4) if len(c) > 2 and c[-2] else None})
meet = [r for r in rows if r.get("meet")]
print(json.dumps({"starts": len(rows), "with a meeting group of three": len(meet),
                  "classes (all)": dict(Counter(r["class"] for r in rows)),
                  "classes (meeting groups of three)": dict(Counter(r["class"] for r in meet)),
                  "counts equal the study's": sum(1 for r in rows if r.get("counts equal the study's")),
                  "six-knot starts": [r for r in rows if r.get("n") == 6], "rows": rows}, indent=1))
