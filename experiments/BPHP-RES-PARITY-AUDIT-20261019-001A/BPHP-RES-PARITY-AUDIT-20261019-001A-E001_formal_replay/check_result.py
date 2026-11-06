#!/usr/bin/env python3
"""Independent check of the formal replay's outputs; imports no producer code.

Parses result.json, the verifier's report and the replay log, and confirms the
frozen decision rule: pinned commit with no tracked changes, all three
published commands exit 0, every declaration the aggregate lists reports only
the standard axioms, the elaborated main statement has the expected shape, and
both controls failed as intended. A deliberately altered axiom report shows
that the axiom comparison can fail.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "artifacts/BPHP-RES-PARITY-AUDIT-20261019-001A/BPHP-RES-PARITY-AUDIT-20261019-001A-E001_formal_replay"
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
DECLARATIONS = {
    "MathResearch.bitPHP_exponential",
    "MathResearch.bitPHP_exponential_base_two",
    "MathResearch.bitPHP_superpolynomial",
    "MathResearch.PolynomialCalculus.generic_CNF_subspace_criterion",
    "MathResearch.PolynomialCalculus.generic_CNF_density_bound_simple",
    "MathResearch.generic_affine_subspace_consequence",
    "MathResearch.PolynomialCalculus.no_separated_subspace_of_complementary_pair",
}


def axiom_reports(text: str) -> dict[str, set[str]]:
    reports = {}
    flat = re.sub(r"\n\s+", " ", text)
    for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat):
        reports[match.group(1)] = {a.strip() for a in match.group(2).split(",") if a.strip()}
    return reports


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    verification = (ARTIFACT / "verification.txt").read_text()
    log = (ARTIFACT / "replay.log").read_text()
    assert result["status"] == "passed"
    assert result["checkout_matches_pin"] is True and result["checkout_tracked_changes"] == ""
    assert result["toolchain_pin"] == "leanprover/lean4:v4.34.0-rc2"
    steps = {s["label"]: s for s in result["steps"]}
    for label in ("cache_get", "verify", "leanchecker_fresh"):
        assert steps[label]["exit"] == 0, label
    assert "$ lake env leanchecker --fresh claims.BitPHPPreprintRevision1" in log
    assert re.search(r"^PASS: 1 proof files; 0 interface files .*; 7 audited declarations\.$",
                     verification, re.M)
    reports = axiom_reports(verification)
    assert set(reports) == DECLARATIONS, sorted(set(reports) ^ DECLARATIONS)
    assert all(axioms <= STANDARD for axioms in reports.values())
    statement = re.sub(r"\s+", " ", verification)
    for fragment in ("MathResearch.bitPHP_exponential : ∀ ℓ ≥ 32,",
                     "AffineDAG (MathResearch.PolynomialCalculus.usualBitPHPInitials (2 ^ ℓ + 1) ℓ) C)",
                     "C finish = ∅ → Real.exp (↑(2 ^ ℓ) / (32768 * ↑ℓ ^ 2)) < ↑S"):
        assert fragment in statement, fragment
    assert result["control_sorry_detected"] is True and "[sorryAx]" in steps["control_sorry"]["tail"]
    assert result["mutation_applied"] is True and result["control_mutated_rejected"] is True
    assert "MutatedExponential.lean:41" in log  # rejected inside the altered theorem itself
    supplementary = json.loads((ARTIFACT / "supplementary_controls.json").read_text())
    assert supplementary["exit"] == 1 and "AllConstantsOne.lean:125" in supplementary["first_error"]

    # The comparison can fail: a report naming sorryAx is not standard.
    altered = verification.replace("[propext, Classical.choice, Quot.sound]", "[propext, sorryAx]", 1)
    assert not all(axioms <= STANDARD for axioms in axiom_reports(altered).values())
    print("formal replay result passed: pinned commit, three commands exit 0, 7 declarations with standard "
          "axioms, expected statement, controls rejected (V1 parse; no theorem authority)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
