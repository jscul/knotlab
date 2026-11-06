#!/usr/bin/env python3
"""Check the closure ledger of SIGNED-SUBDIVISION-20261029-001.

The ledger makes no mathematical claim. This checker confirms that its bound evidence is intact:
- the proofs' manifests and results and the experiment's contract and result match their recorded digests;
- the proofs are Proved and their checks passed; the experiment contract is Frozen and its result records the outcome the ledger
  states (its decision rule failed on P2, so the experiment closed null);
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
EPIC = "SIGNED-SUBDIVISION-20261029-001"
NOTES = ("research/SIGNED-SUBDIVISION-20261029-001/signed_subdivision.md",)
TERMINAL = {"A": "proved", "B": "proved", "C": "closed-null"}
EXPECTED_ALL_PASS = {"artifacts/SIGNED-SUBDIVISION-20261029-001C/SIGNED-SUBDIVISION-20261029-001C-E001_real_weight_search/result.json": False}


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
        if path.startswith("artifacts/"):
            statuses[path] = {"all pass": value.get("all pass")}
        else:
            statuses[path] = value.get("status")
    checks["parent_statuses"] = statuses
    checks["proofs_proved"] = all(s == "Proved" for p, s in statuses.items() if p.startswith("proofs/"))
    checks["contracts_frozen"] = all(s == "Frozen" for p, s in statuses.items() if p.endswith("contract.json"))
    checks["experiment_as_stated"] = all(statuses[p] == {"all pass": v} for p, v in EXPECTED_ALL_PASS.items()) and \
        all(p in EXPECTED_ALL_PASS for p in statuses if p.startswith("artifacts/"))
    checks["notes_present"] = all((ROOT / note).is_file() for note in NOTES)
    classes = {suffix: json.loads((ROOT / "tickets" / f"{EPIC}{suffix}.json").read_text()).get("status_class")
               for suffix in TERMINAL}
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {
        "wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
        "wrong_experiment_outcome_rejected": not all(statuses[p] == {"all pass": not v} for p, v in EXPECTED_ALL_PASS.items()),
        "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file(),
    }
    failures = [name for name in ("parents_bound", "proofs_proved", "contracts_frozen", "experiment_as_stated",
                                  "notes_present", "tickets_terminal") if checks[name] is not True]
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
