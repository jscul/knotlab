"""I2 re-scored independently: each interface's recorded round-weight divided by its entry's, as power series (exact fractions,
the first terms the recorded 16-term series determine), against the frozen factor table: a spare 1 + y, a lone knot 1 + y, a lone
knot with a spare 1 + y + y^2, a hanging path of two (1 + y)/(1 - y).  Only interfaces at a knot of the loop with a recorded
round-weight (ring joins have two loops and none).

  ../../../.venv/bin/python -B i2_rescore.py > referee_loop_i2.json      (from this directory)
"""
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FAC = {"spare": [1, 1], "lone": [1, 1], "lone+spare": [1, 1, 1]}


def div(a, b):
    s = next(i for i, x in enumerate(b) if x != 0)
    a, b = [Fraction(x) for x in a[s:]], [Fraction(x) for x in b[s:]]
    q, r = [], a[:]
    for i in range(len(a)):
        c = r[i] / b[0]
        q.append(c)
        for j in range(len(b)):
            if i + j < len(r):
                r[i + j] -= c * b[j]
    return q


rows = []
for line in open(ROOT / "runs/loop-catalogue/results.jsonl"):
    r = json.loads(line)
    if not r["case"].startswith("I-") or r["status"] != "ok" or not r["result"].get("W"):
        continue
    base = r["result"]["W"]["W"]
    for it in r["result"]["interfaces"]:
        if it["kind"] == "ring5" or not it.get("W"):
            continue
        q = div(it["W"]["W"], base)
        k = min(len(q), 7)
        want = ([1] + [2] * 20) if it["kind"] == "path2" else FAC[it["kind"]] + [0] * 20
        rows.append({"case": r["case"], "kind": it["kind"], "knot": it["knot"], "on the loop": it.get("on_loop"),
                     "factor matches the table (first terms)": all(q[i] == want[i] for i in range(k)),
                     "factor, first terms": [str(x) for x in q[:k]]})
on = [x for x in rows if x["on the loop"]]
print(json.dumps({"interfaces with a recorded W": len(rows), "at a loop knot": len(on),
                  "... factor matches the frozen table": sum(x["factor matches the table (first terms)"] for x in on),
                  "off the loop (hung side knots)": len(rows) - len(on),
                  "mismatches at loop knots": [x for x in on if not x["factor matches the table (first terms)"]][:6],
                  "off-loop factors (first)": [x for x in rows if not x["on the loop"]][:4]}, indent=1))
