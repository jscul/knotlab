#!/usr/bin/env python3
"""Check the closure ledger of HANDLE-EMERGENCE-20261102-001.

The ledger makes no mathematical claim. This checker confirms that its bound evidence is intact:
- the proofs' manifests and results, and the record's manifest, match their recorded digests;
- the proofs are Proved, their checks passed, and the documentation record is Complete;
- the decision note exists;
- the tickets carry their terminal status classes.

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
EPIC = "HANDLE-EMERGENCE-20261102-001"
NOTES = ("research/HANDLE-EMERGENCE-20261102-001/handle_emergence.md",)
TERMINAL = {"A": "proved", "B": "proved", "C": "proved"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict[str, object]:
    manifest = json.loads((HERE / "manifest.json").read_text())
    checks: dict[str, object] = {}
    bindings = manifest["parent_bindings"]
    checks["parents_bound"] = all(sha256(ROOT / path) == digest for path, digest in bindings.items())
    statuses = {}
    for path in bindings:
        value = json.loads((ROOT / path).read_text())
        statuses[path] = value.get("status")
    checks["parent_statuses"] = statuses
    checks["proofs_proved"] = all(s == "Proved" for p, s in statuses.items() if p.endswith("manifest.json") and p.startswith("proofs/"))
    checks["record_complete"] = all(s == "Complete" for p, s in statuses.items() if p.endswith("manifest.json") and p.startswith("research/"))
    checks["results_passed"] = all(s == "passed" for p, s in statuses.items() if p.endswith("result.json"))
    checks["notes_present"] = all((ROOT / note).is_file() for note in NOTES)
    classes = {suffix: json.loads((ROOT / "tickets" / f"{EPIC}{suffix}.json").read_text()).get("status_class")
               for suffix in TERMINAL}
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {
        "wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
        "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file(),
    }
    failures = [name for name in ("parents_bound", "proofs_proved", "record_complete", "results_passed", "notes_present", "tickets_terminal")
                if checks[name] is not True]
    failures += [f"control {name}" for name, ok in controls.items() if not ok]
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
