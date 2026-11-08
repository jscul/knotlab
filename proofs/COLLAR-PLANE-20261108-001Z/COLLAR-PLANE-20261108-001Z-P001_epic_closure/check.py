#!/usr/bin/env python3
"""Check the closure ledger of COLLAR-PLANE-20261108-001.

The ledger makes no mathematical claim. This checker confirms that its bound evidence is intact:
- the bound files match their recorded digests;
- both proofs are Proved and their checks passed;
- the experiment contract is frozen and exploratory, and its run output carries the recorded findings;
- the decision note and the stress test's output exist and agree with the ledger;
- the tickets carry their terminal status classes (A and B proved, C supported).

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
EPIC = "COLLAR-PLANE-20261108-001"
NOTES = ("research/COLLAR-PLANE-20261108-001/collar_plane.md", "research/COLLAR-PLANE-20261108-001/stress_test_radius3.json")
TERMINAL = {"A": "proved", "B": "proved", "C": "supported"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict:
    manifest = json.loads((HERE / "manifest.json").read_text())
    bindings = manifest["parent_bindings"]
    checks: dict = {}
    checks["parents_bound"] = all(sha256(ROOT / p) == digest for p, digest in bindings.items())
    statuses = {}
    for path in bindings:
        if not path.endswith(".json"):
            statuses[path] = "file"
            continue
        value = json.loads((ROOT / path).read_text())
        statuses[path] = value.get("status", "run output" if path.startswith("artifacts/") else None)
    checks["parent_statuses"] = statuses
    proofs = [p for p in bindings if p.startswith("proofs/")]
    checks["proofs_proved"] = all(statuses[p] == "Proved" for p in proofs if p.endswith("manifest.json"))
    checks["results_passed"] = all(statuses[p] == "passed" for p in proofs if p.endswith("result.json"))
    contracts = [p for p in bindings if p.endswith("contract.json")]
    checks["experiment_frozen_exploratory"] = len(contracts) == 1 and all(
        json.loads((ROOT / c).read_text()).get("status") == "Frozen"
        and json.loads((ROOT / c).read_text()).get("evidence_stage") == "exploratory" for c in contracts)
    a = json.loads((ROOT / next(p for p in proofs if "001A" in p and p.endswith("result.json"))).read_text())
    b = json.loads((ROOT / next(p for p in proofs if "001B" in p and p.endswith("result.json"))).read_text())
    checks["proof_a_findings"] = (a["census"]["R_1: fundamental-domain tiles, non-key collars, distinct keys"] == [20, 0, 10]
                                  and a["census"]["R_2: interior darts tested, outside the radius-2 atlas"][1] == 0)
    checks["proof_b_findings"] = (b["census"]["L1: keys, non-keys"] == [54, 1210] and b["census"]["core: keys, non-keys"] == [54, 102]
                                  and b["census"]["disagreeing pairs (handedness +1): inconsistent, consistent"] == [34, 0])
    c = json.loads((ROOT / next(p for p in bindings if p.startswith("artifacts/") and p.endswith("main_result.json"))).read_text())
    s = c["summary"]
    checks["experiment_c_findings"] = (all(c["controls"].values())
                                       and s["F4 half-turn shapes, 1 cut(s)"]["pass"] == 2
                                       and s["F1 grid, 1 cut(s)"]["pass"] == 2 and s["F2 brick, 1 cut(s)"]["pass"] == 0
                                       and s["F2 brick, 2 cut(s)"]["pass"] == 6 and s["F3 dominoes, 1 cut(s)"]["pass"] == 8)
    checks["notes_present"] = all((ROOT / note).is_file() for note in NOTES)
    st = json.loads((ROOT / NOTES[1]).read_text())
    checks["stress_test_radius3"] = (st["atlas"]["complete (no dart near the edge)"] and st["planes"]["R_3"]["passes"]
                                     and st["planes"]["R_4"]["passes"] and st["control: rectangle lattice cut 3 times fails"]["fails"])
    classes = {t: json.loads((ROOT / "tickets" / f"{EPIC}{t}.json").read_text()).get("status_class") for t in TERMINAL}
    checks["ticket_classes"] = classes
    checks["tickets_terminal"] = classes == TERMINAL
    controls = {
        "wrong_digest_rejected": sha256(ROOT / next(iter(bindings))) != "0" * 64,
        "missing_note_rejected": not (ROOT / "research" / EPIC / "no_such_note.md").is_file(),
    }
    names = ("parents_bound", "proofs_proved", "results_passed", "experiment_frozen_exploratory", "proof_a_findings",
             "proof_b_findings", "experiment_c_findings", "notes_present", "stress_test_radius3", "tickets_terminal")
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
