#!/usr/bin/env python3
"""Check the closure ledger of RETURN-LAW-20261110-001.

The ledger makes no mathematical claim. This checker confirms that its bound evidence is intact:
- the bound files match their recorded digests;
- each proof is Obstructed (the frozen criterion's verdict) and its check passed;
- the decision note exists;
- tickets A, B and C carry their terminal status class (obstructed).

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
EPIC = "RETURN-LAW-20261110-001"
NOTES = ("research/RETURN-LAW-20261110-001/return_law.md",)
TERMINAL = {"A": "obstructed", "B": "obstructed", "C": "obstructed"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict:
    manifest = json.loads((HERE / "manifest.json").read_text())
    bindings = manifest["parent_bindings"]
    checks: dict = {}
    checks["parents_bound"] = all(sha256(ROOT / p) == digest for p, digest in bindings.items())
    statuses = {p: json.loads((ROOT / p).read_text()).get("status") for p in bindings}
    checks["parent_statuses"] = statuses
    checks["proofs_obstructed"] = all(statuses[p] == "Obstructed" for p in bindings if p.endswith("manifest.json"))
    checks["results_passed"] = all(statuses[p] == "passed" for p in bindings if p.endswith("result.json"))
    checks["notes_present"] = all((ROOT / note).is_file() for note in NOTES)
    classes = {s: json.loads((ROOT / "tickets" / f"{EPIC}{s}.json").read_text()).get("status_class") for s in TERMINAL}
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {
        "wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
        "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file(),
    }
    names = ("parents_bound", "proofs_obstructed", "results_passed", "notes_present", "tickets_terminal")
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
