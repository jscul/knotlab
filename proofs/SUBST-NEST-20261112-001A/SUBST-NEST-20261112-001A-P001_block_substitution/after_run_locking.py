#!/usr/bin/env python3
"""After the run, descriptive (not frozen): with the block's knots as cross set, does a root have ties outside its copy exactly when
its place is not loose, and does it then reach its farthest distinction? Read from result_blocks.json.

    .venv/bin/python3 -B after_run_locking.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
bl = json.loads((HERE / "result_blocks.json").read_text())["checks"]["result"]["rows"]
agree = disagree = nonloose = reach_full = 0
for b in bl:
    m, E = b["block"]
    x = [x for x in b["bindings"] if x["binding"] == "the block's knots"][0]
    loose = set(x["star places"])
    for t in x["tests"]:
        for r in t["roots"]:
            locked = r["tied outside the root's copy"] > 0
            agree += (r["column"] in loose) == (not locked)
            disagree += (r["column"] in loose) != (not locked)
            if r["column"] not in loose:
                nonloose += 1
                reach_full += r["farthest tie"] == r["farthest distinction"]
out = {"status": "descriptive, after the run", "roots": agree + disagree, "agree": agree, "disagree": disagree,
       "roots at places that are not loose": nonloose, "of them reaching the farthest distinction": reach_full}
(HERE / "result_after_run_locking.json").write_text(json.dumps(out, indent=1) + "\n")
print(out)
