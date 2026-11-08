#!/usr/bin/env python3
"""CONTRA-READ-P2, summarized: for each 12-line glue and each line, how many classes of the glue without the line share the
contradictory class's row. usage: stress_test_p2_summary.py OUT.json ROWS1.json [ROWS2.json ...]"""
import json
import sys

out = {}
for p in sys.argv[2:]:
    d = json.load(open(p))
    out[str(d["seed"])] = {"lines": d["lines"], "cycle rank": d["cycle rank"],
                           "classes of the glue without each line": sorted({x["classes of the glue without the line"] for x in d["per line"]}),
                           "classes sharing the contradictory row, per line": [x["sharing the Pfaffian row"] for x in d["per line"]],
                           "distinct rows, per line": [x["distinct rows"] for x in d["per line"]]}
summary = {"every row singles out the contradictory class on every glue": all(
    all(c == 1 for c in v["classes sharing the contradictory row, per line"]) for v in out.values()), "glues": out}
json.dump(summary, open(sys.argv[1], "w"), indent=1)
print(json.dumps(summary, indent=1))
