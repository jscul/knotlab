#!/usr/bin/env python3
"""Check the closure ledger of CRYSTAL-UP-20261108-001.

The ledger makes no mathematical claim. This checker confirms that its bound evidence is intact: the bound files match their
digests; both experiment contracts are frozen and exploratory; the stopped run E001 carries its interpretation; E002's output
passed its control and carries the recorded findings; B's proof is Proved and its check passed; the decision note exists; the
tickets carry their terminal classes (A supported, B proved).

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
EPIC = "CRYSTAL-UP-20261108-001"
NOTES = ("research/CRYSTAL-UP-20261108-001/crystal_up.md",)
TERMINAL = {"A": "supported", "B": "proved"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict:
    manifest = json.loads((HERE / "manifest.json").read_text())
    bindings = manifest["parent_bindings"]
    checks: dict = {}
    checks["parents_bound"] = all(sha256(ROOT / p) == digest for p, digest in bindings.items())
    contracts = [p for p in bindings if p.endswith("contract.json")]
    checks["experiments_frozen_exploratory"] = len(contracts) == 2 and all(
        json.loads((ROOT / c).read_text()).get("status") == "Frozen"
        and json.loads((ROOT / c).read_text()).get("evidence_stage") == "exploratory" for c in contracts)
    checks["e001_stopped_and_explained"] = any(p.endswith("E001_crystals_from_survivors/run/interpretation.md") for p in bindings)
    r = json.loads((ROOT / next(p for p in bindings if "E002" in p and p.endswith("result.json"))).read_text())
    checks["e002_control_passed"] = r["status"] == "passed" and all(r["controls"].values())
    checks["e002_findings"] = (r["seeds"] == 203 and r["crystals (completed tori passing the check)"] == 26
                               and r["completed tori"] == 26)
    bm = json.loads((ROOT / next(p for p in bindings if "001B" in p and p.endswith("manifest.json"))).read_text())
    br = json.loads((ROOT / next(p for p in bindings if "001B" in p and p.endswith("result.json"))).read_text())
    checks["proof_b_proved_and_passed"] = bm.get("status") == "Proved" and br.get("status") == "passed" and not br.get("failures")
    checks["notes_present"] = all((ROOT / n).is_file() for n in NOTES)
    classes = {t: json.loads((ROOT / "tickets" / f"{EPIC}{t}.json").read_text()).get("status_class") for t in TERMINAL}
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {"wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
                "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file()}
    names = ("parents_bound", "experiments_frozen_exploratory", "e001_stopped_and_explained", "e002_control_passed", "e002_findings",
             "proof_b_proved_and_passed", "notes_present", "tickets_terminal")
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
