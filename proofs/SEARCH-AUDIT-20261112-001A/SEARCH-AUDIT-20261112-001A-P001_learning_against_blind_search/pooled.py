#!/usr/bin/env python3
"""After the run (not a frozen mark): the audit pooled across cases. For every run that found its target, the blind-search chance of
finding within the learner's probes, F = 1 - (1 - p)^n; blind search would make F about uniform (mean 1/2, half the runs within the blind
median). Reads result.json.

    .venv/bin/python3 -B pooled.py [--write]"""
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
r = json.loads((HERE / "result.json").read_text())
fam = {}
for x in r["cases"]:
    c = x["case"]
    f = "native writing" if c.startswith("native") else ("gates and deeper memories" if c[:2] in ("S3", "S4", "S5", "T1", "T2", "T3")
                                                          else "parity, the count of five, rest-set and graded learners")
    for n in x["learner probes when found"]:
        fam.setdefault(f, []).append(1 - (1 - x["p per draw"]) ** n)
out = {}
allF = []
for f, v in fam.items():
    allF += v
    out[f] = {"found runs": len(v), "mean F": round(statistics.mean(v), 3), "share within the blind median": round(sum(z <= 0.5 for z in v) / len(v), 3)}
out["all"] = {"found runs": len(allF), "mean F": round(statistics.mean(allF), 3), "share within the blind median": round(sum(z <= 0.5 for z in allF) / len(allF), 3)}
if "--write" in sys.argv:
    (HERE / "result_pooled.json").write_text(json.dumps(out, indent=1) + "\n")
    summary = {"by family": r["by family"], "all cases": r["all cases"], "any case learning by the frozen rule": r["any case learning"],
               "pooled after the run": out}
    (HERE / "result_summary.json").write_text(json.dumps({"status": "passed", "checks": {"result": summary}}, indent=1) + "\n")
print(json.dumps(out, indent=1))
