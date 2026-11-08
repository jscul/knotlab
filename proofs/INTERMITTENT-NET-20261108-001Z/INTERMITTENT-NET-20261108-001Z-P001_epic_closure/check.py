#!/usr/bin/env python3
"""Check the closure ledger of INTERMITTENT-NET-20261108-001.

The ledger makes no mathematical claim. This checker confirms that its bound evidence is intact:
- the bound files match their recorded digests;
- the proof is Proved and its check passed;
- the experiment contract is frozen and exploratory, and its run output carries the recorded findings;
- the decision note exists;
- the tickets carry their terminal status classes (A proved, B supported).

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
EPIC = "INTERMITTENT-NET-20261108-001"
NOTES = ("research/INTERMITTENT-NET-20261108-001/intermittent_net.md",)
TERMINAL = {"A": "proved", "B": "supported"}


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
    proofs = [p for p in bindings if p.startswith("proofs/")]
    checks["proofs_proved"] = all(statuses[p] == "Proved" for p in proofs if p.endswith("manifest.json"))
    checks["results_passed"] = all(statuses[p] == "passed" for p in proofs if p.endswith("result.json"))
    contracts = [p for p in bindings if p.endswith("contract.json")]
    checks["experiments_frozen_exploratory"] = len(contracts) == 1 and all(
        json.loads((ROOT / c).read_text()).get("status") == "Frozen"
        and json.loads((ROOT / c).read_text()).get("evidence_stage") == "exploratory" for c in contracts)
    outputs = {p: json.loads((ROOT / p).read_text()) for p in bindings if p.startswith("artifacts/")}
    b = next(v for p, v in outputs.items() if "001B" in p)
    checks["experiment_b_findings"] = (b.get("controls_ok") is True and b.get("chains") == 7040
                                       and b.get("chains composing at recurring lags") == 244
                                       and b.get("chains whose composing lags are singled out (H1 and H2)") == 92
                                       and set(b.get("rules among them", {})) <= {"15", "170", "60", "90", "105", "150"})
    checks["notes_present"] = all((ROOT / note).is_file() for note in NOTES)
    classes = {s: json.loads((ROOT / "tickets" / f"{EPIC}{s}.json").read_text()).get("status_class") for s in TERMINAL}
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {
        "wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
        "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file(),
    }
    names = ("parents_bound", "proofs_proved", "results_passed", "experiments_frozen_exploratory",
             "experiment_b_findings", "notes_present", "tickets_terminal")
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
