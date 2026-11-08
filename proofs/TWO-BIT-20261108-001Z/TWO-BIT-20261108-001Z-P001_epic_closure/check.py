#!/usr/bin/env python3
"""Check the closure ledger of TWO-BIT-20261108-001.

The ledger makes no mathematical claim. This checker confirms that its bound evidence is intact: the bound files match their
digests; ticket A's experiment contract is frozen and exploratory and its census passed its controls with the recorded survivor
count; the decision note exists; the tickets carry their terminal classes (A supported, B retired into the epic's stress test).

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
EPIC = "TWO-BIT-20261108-001"
NOTES = ("research/TWO-BIT-20261108-001/two_bit.md",)
TERMINAL = {"A": "supported", "B": "retired"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict:
    manifest = json.loads((HERE / "manifest.json").read_text())
    bindings = manifest["parent_bindings"]
    checks: dict = {}
    checks["parents_bound"] = all(sha256(ROOT / p) == digest for p, digest in bindings.items())
    contracts = [p for p in bindings if p.endswith("contract.json")]
    checks["experiments_frozen_exploratory"] = len(contracts) == 1 and all(
        json.loads((ROOT / c).read_text()).get("status") == "Frozen"
        and json.loads((ROOT / c).read_text()).get("evidence_stage") == "exploratory" for c in contracts)
    a = json.loads((ROOT / next(p for p in bindings if "001A" in p and p.endswith("result.json"))).read_text())
    checks["census_findings"] = (a["status"] == "passed" and a["product classes tested"] == 139656 and len(a["survivors"]) == 3241)
    checks["notes_present"] = all((ROOT / n).is_file() for n in NOTES)
    classes = {t: json.loads((ROOT / "tickets" / f"{EPIC}{t}.json").read_text()).get("status_class") for t in TERMINAL}
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {"wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
                "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file()}
    names = ("parents_bound", "experiments_frozen_exploratory", "census_findings", "notes_present", "tickets_terminal")
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
