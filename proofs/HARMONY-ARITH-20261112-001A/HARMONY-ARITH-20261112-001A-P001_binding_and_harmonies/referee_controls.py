#!/usr/bin/env python3
"""After the run: negative controls showing that harm_referee.py can fail (it passed on the census). C-R1: a census row with its
periods altered is caught. C-R2: a stitch with a surviving offset removed is caught."""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import harm_referee as R  # noqa: E402

cells = json.loads((HERE / "result_harmonies.json").read_text())["checks"]["result"]["cells"]
B = json.loads((HERE / "result_stitches.json").read_text())["checks"]["result"]
bad = copy.deepcopy([c for c in cells if c["law"] == "NAE" and c["span"] == 4])
row = next(r for r in bad[0]["rows"] if "periods" in r)
row["periods"] = [3]
out = {"C-R1 altered periods caught": R.r1(bad)["number of disagreements"] == 1}
B2 = copy.deepcopy(B)
pair = next(r for r in B2["pairs"] if r["law"] == "NAE" and any(r["surviving"].values()))
name = next(k for k, v in pair["surviving"].items() if v)
pair["surviving"] = {name: pair["surviving"][name][1:]}
B2["pairs"] = [pair]
out["C-R2 removed offset caught"] = R.r2_r3(B2)[0]["number of disagreements"] == 1
print(json.dumps(out))
ok = all(out.values())
if "--write" in sys.argv:
    (HERE / "result_referee_controls.json").write_text(json.dumps({"controls": out, "passed": ok}, indent=1) + "\n")
sys.exit(0 if ok else 1)
