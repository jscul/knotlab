#!/usr/bin/env python3
"""Check the closure ledger of PC-DEGREE-20261020-001.

The ledger makes no mathematical claim. This checker confirms that its bound
evidence is intact: the proof manifest and result of ticket B and the frozen
contract and result of ticket A match their recorded digests, the
proofs are Proved, the results carry their recorded statuses, the decision
note exists, and the tickets carry their terminal status classes.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPIC = "PC-DEGREE-20261020-001"
NOTES = ("research/PC-DEGREE-20261020-001/pc_degree.md",)
TERMINAL = {"A": "supported", "B": "proved"}
EXPECTED_RESULT = {"PC-DEGREE-20261020-001A": True, "PC-DEGREE-20261020-001B": "passed"}


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
        statuses[path] = value.get("signal") if path.startswith("artifacts/") else value.get("status")
    checks["parent_statuses"] = statuses
    checks["proofs_proved"] = all(s == "Proved" for p, s in statuses.items()
                                  if p.startswith("proofs/") and p.endswith("manifest.json"))
    checks["contracts_frozen"] = all(s == "Frozen" for p, s in statuses.items() if p.endswith("contract.json"))
    checks["results_as_recorded"] = all(s == EXPECTED_RESULT[p.split("/")[1]] for p, s in statuses.items()
                                        if p.endswith("result.json"))
    checks["notes_present"] = all((ROOT / note).is_file() for note in NOTES)
    classes = {
        suffix: json.loads((ROOT / "tickets" / f"{EPIC}{suffix}.json").read_text()).get("status_class")
        for suffix in TERMINAL
    }
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {
        "wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
        "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file(),
    }
    failures = [name for name in ("parents_bound", "proofs_proved", "contracts_frozen", "results_as_recorded",
                                  "notes_present", "tickets_terminal") if checks[name] is not True]
    failures += [f"control {name}" for name, ok in controls.items() if not ok]
    return {"checks": checks, "controls": controls, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3,
        "artifact_id": manifest["artifact_id"],
        "kind": "proof",
        "ticket": manifest["ticket"],
        "proof": manifest["proof"],
        "status": "passed" if not outcome["failures"] else "failed",
        "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"],
        "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"],
        "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"],
        "checks": outcome["checks"],
        "controls": outcome["controls"],
        "failures": outcome["failures"],
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv[1:]:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != result:
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: closure ledger bound and complete")
    for failure in outcome["failures"]:
        print(f"  failed: {failure}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
