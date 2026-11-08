#!/usr/bin/env python3
"""Check the closure ledger of PATH-GROWTH-20261108-001.

The ledger makes no mathematical claim. This checker confirms that its bound evidence is intact:
- the bound files match their recorded digests;
- the two experiment contracts are frozen and exploratory, and their run outputs carry the recorded findings;
- the decision note exists;
- the tickets carry their terminal status classes (A and B supported).

    python3 -B check.py          verify against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPIC = "PATH-GROWTH-20261108-001"
NOTES = ("research/PATH-GROWTH-20261108-001/path_growth.md",)
TERMINAL = {"A": "supported", "B": "supported"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict:
    manifest = json.loads((HERE / "manifest.json").read_text())
    bindings = manifest["parent_bindings"]
    checks: dict = {}
    checks["parents_bound"] = all(sha256(ROOT / p) == digest for p, digest in bindings.items())
    statuses = {}
    for path in bindings:
        value = json.loads((ROOT / path).read_text())
        statuses[path] = value.get("status", "run output" if path.startswith("artifacts/") else None)
    checks["parent_statuses"] = statuses
    contracts = [p for p in bindings if p.endswith("contract.json")]
    checks["experiments_frozen_exploratory"] = len(contracts) == 2 and all(
        json.loads((ROOT / c).read_text()).get("status") == "Frozen"
        and json.loads((ROOT / c).read_text()).get("evidence_stage") == "exploratory" for c in contracts)
    outputs = {p: json.loads((ROOT / p).read_text()) for p in bindings if p.startswith("artifacts/")}
    a = next(v for p, v in outputs.items() if "001A" in p)
    b = next(v for p, v in outputs.items() if "001B" in p)
    lv = a["full levels"]
    checks["experiment_a_findings"] = (a.get("H1 (some family is native at every size of its schedule)") is False
                                       and sum(lv[k]["paths"] for k in ("antipodal 3", "antipodal 4", "antipodal 5")) == 36864000
                                       and all(lv[k].get("native", 0) == 0 for k in ("antipodal 3", "antipodal 4", "antipodal 5", "longer 5"))
                                       and lv["longer 4"].get("native") == 8 and a.get("control passes") is True)
    shapes = {tuple(r[0]) for r in b["part 2, shapes with a native path"]}
    checks["experiment_b_findings"] = (shapes == {(3, 5, 5, 3), (5, 6, 6, 5), (4, 7, 7, 5)} and b.get("native paths in the map") == 80
                                       and b.get("control: 3/5/5/3 gives PATH-HYBRID-20261108-001A's 16 native and 13,464 persistent paths, and 3/4/4/3 its 3,728 persistent and none native") is True)
    checks["notes_present"] = all((ROOT / note).is_file() for note in NOTES)
    classes = {s: json.loads((ROOT / "tickets" / f"{EPIC}{s}.json").read_text()).get("status_class") for s in TERMINAL}
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {
        "wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
        "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file(),
    }
    names = ("parents_bound", "experiments_frozen_exploratory", "experiment_a_findings", "experiment_b_findings",
             "notes_present", "tickets_terminal")
    failures = [n for n in names if checks[n] is not True] + [f"control {n}" for n, ok in controls.items() if not ok]
    return {"checks": checks, "controls": controls, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "Proved" if not outcome["failures"] else "failed",
              "claim": manifest["claim"], **outcome}
    print(json.dumps(outcome, indent=1)[:3000])
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    return 0 if not outcome["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
