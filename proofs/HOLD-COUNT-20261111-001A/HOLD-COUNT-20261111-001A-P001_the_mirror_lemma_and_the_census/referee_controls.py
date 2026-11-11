#!/usr/bin/env python3
"""After the run: negative controls showing that hold_referee.py can fail (it passed on the census).

C-R2: a space whose floor states are not closed under flipping every point (one point pinned to 0, as a reference would be) is
caught. C-R3: the least full adder with its output pair swapped for a non-reading pair, and the parity instance read at the wrong point,
are rejected."""
import copy
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hold_referee as R  # noqa: E402

spaces = json.loads((HERE / "spaces.json").read_text())["spaces"]
summary = json.loads((HERE / "result.json").read_text())["checks"]["result"]
out = {}

sp = next(s for s in spaces if s["label"] == "torus (2, 0, 4)")
orig = R.floor


def floor_pinned(space, signs):
    states = orig(space, signs)
    if space.get("pinned"):
        states = states[(states & 1) == 0]
    return states


bad = copy.deepcopy(sp)
bad["label"] = "control: point 0 pinned"
bad["pinned"] = True
R.floor = floor_pinned
out["C-R2 space with a pinned point flagged"] = bool(R.r2([bad])["not closed under flipping every point"])
R.floor = orig

s2 = copy.deepcopy(summary)
fa = s2["least"]["full adder, no reference"]["first instance"]
fa["out"] = [3, 7]
par = s2["least"]["parity, no reference"]["first instance"]
par["out"] = 6
s2["least"] = {"full adder, no reference": s2["least"]["full adder, no reference"], "parity, no reference": s2["least"]["parity, no reference"]}
rows = R.r3(spaces, s2)
out["C-R3 corrupted instances rejected"] = [not r["confirmed"] for r in rows]
print(json.dumps(out))
ok = out["C-R2 space with a pinned point flagged"] and all(out["C-R3 corrupted instances rejected"])
if "--write" in sys.argv:
    (HERE / "result_referee_controls.json").write_text(json.dumps({"controls": out, "passed": ok}, indent=1) + "\n")
sys.exit(0 if ok else 1)
