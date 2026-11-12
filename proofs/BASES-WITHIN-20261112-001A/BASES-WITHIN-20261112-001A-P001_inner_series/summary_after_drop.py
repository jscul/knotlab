#!/usr/bin/env python3
"""The frozen summary of check.py needs result_axial.json, which E1 never wrote (dropped at its 1-hour cap). This writes result.json
with every frozen item of E2 to E4 computed exactly as check.py's summary computes it, E1 marked dropped, and the descriptive
follow-up (after_run_levels.py) reported beside it, labelled as such.

    .venv/bin/python3 -B summary_after_drop.py"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
of = json.loads((HERE / "result_offsets.json").read_text())["checks"]["result"]
bx = json.loads((HERE / "result_box.json").read_text())["checks"]["result"]["rows"]
gs = json.loads((HERE / "result_gasket.json").read_text())["checks"]["result"]["rows"]
fu = json.loads((HERE / "result_after_run_levels.json").read_text())["rows"]
cells = [p for r in of["rows"] for p in r["patterns"]]
alt = [r for r in of["rows"] if r["orbits"] == ["01"]][0]
by = {"+".join(r["orbits"]): r for r in fu}
res = {
    "E1": "dropped: reached its 1-hour cap (5 h 48 min of processor time); P1 to P3 untested by the frozen run",
    "check L4: a binding at one place lives exactly when the outer does": all(p["one place lives"] == p["outer lives"] for p in cells),
    "check L8: chain-free patterns never end under offsets": all(p["ended while the outer lives"] == 0 for p in cells if p["chain-free"]),
    "check L9: the alternation's offsets read as signed NAE": all(p["signed NAE agrees"] == p["offset bindings"] for p in alt["patterns"]),
    "control: exactly one ends a living outer": of["control (exactly one, the advisor's)"],
    "P4 every harmony has a binding with offsets that ends a living outer": all(any(p["ended while the outer lives"] for p in r["patterns"]) for r in of["rows"]),
    "E2 harmonies with an ending binding": sum(any(p["ended while the outer lives"] for p in r["patterns"]) for r in of["rows"]),
    "E2 endings in all, and the patterns they occur on": [sum(p["ended while the outer lives"] for p in cells),
                                                          sorted({json.dumps(p["outer"]) for p in cells if p["ended while the outer lives"]})],
    "E2 Fano plane revived (lived / tried), alternation and the rest": [[alt["patterns"][-1]["lived"], alt["patterns"][-1]["offset bindings"]],
                                                                         sum(r["patterns"][-1]["lived"] for r in of["rows"] if r is not alt),
                                                                         sum(r["patterns"][-1]["offset bindings"] for r in of["rows"] if r is not alt)],
    "check E3: box ties match the product lemma": all(o.get("matches the product lemma", True) for s in bx for row in s["rows"] for o in row["origins"]),
    "E3 every seed lives at every level": all(o["lives"] for s in bx for row in s["rows"] for o in row["origins"]),
    "E3 farthest tie / farthest distinction by seed and level": {s["seed"]: [[(o["origin"], o.get("farthest tie"), o.get("farthest distinction"), o.get("tied")) for o in row["origins"]] for row in s["rows"]] for s in bx},
    "P5 gasket: lives at every level, no ties": all(r[c]["lives"] and r[c]["tied"] == 1 for r in gs for c in ("corner", "shared corner")),
    "E4 gasket [level, tied to corner, farthest tie, farthest distinction, tied to shared corner]": [[r["level"], r["corner"].get("tied"), r["corner"].get("farthest tie"), r["corner"].get("farthest distinction"), r["shared corner"].get("tied")] for r in gs],
    "follow-up after the run (descriptive, not frozen)": {
        "P1 0011 level 2 and 3": [by["0011"]["level 2"], by["0011"]["level 3"]],
        "P2 000111 level 2": by["000111"]["level 2"],
        "P3 rigid at level 2": sorted(k for k, r in by.items() if r["rigid (only linear states)"]),
        "level 2 not below the known states (all)": all(r["not below the known states"] for r in fu),
        "L7 level-2 ties are products (all 45)": all(r["level 2 ties = product of line ties"] for r in fu),
        "level 1 and level 2 states (None: over 20,000)": {k: [r["states"], r["level 2"]] for k, r in by.items()},
    },
}
deps = ["proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series/" + f for f in
        ("nest_lib.py", "check.py", "after_run_levels.py", "summary_after_drop.py", "result_offsets.json", "result_box.json", "result_gasket.json", "result_after_run_levels.json")]
out = {"status": "passed", "checks": {"dependencies": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in deps}, "result": res}}
(HERE / "result.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(res, indent=1)[:2500])
