#!/usr/bin/env python3
"""Check BPHP-RES-PARITY-AUDIT-20261019-001B-P001: definitional fidelity of the formal bit-PHP bound.

Binds the audit to the exact pinned sources (checkout commit, no tracked
changes, SHA-256 of every audited file), compiles the non-vacuity witnesses
against the author's built project, confirms they use only the standard
axioms, and runs two controls that change the mathematics: the unsatisfiability
witness with 2^l pigeons instead of 2^l + 1, and the refutation with one step
given the wrong premises. Both must be rejected.

Needs the checkout built by BPHP-RES-PARITY-AUDIT-20261019-001A-E001.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHECKOUT = Path("/home/jscul/external-audits/bit-php-check")
FORMAL = CHECKOUT / "formalization"
TMP = FORMAL / ".lake" / "audit_controls"
WITNESSES = HERE / "AuditWitnesses.lean"
THEOREMS = ("AuditWitnesses.usualBitPHP_unsat", "AuditWitnesses.usualBitPHP_no_model",
            "AuditWitnesses.smallest_instance_refuted")
STANDARD = {"propext", "Classical.choice", "Quot.sound"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lean(name: str, source: str) -> subprocess.CompletedProcess[str]:
    TMP.mkdir(parents=True, exist_ok=True)
    path = TMP / name
    path.write_text(source)
    return subprocess.run(["lake", "env", "lean", str(path)], cwd=FORMAL, capture_output=True, text=True,
                          check=False, timeout=3600)


def run() -> dict[str, object]:
    manifest = json.loads((HERE / "manifest.json").read_text())
    checks: dict[str, object] = {}
    controls: dict[str, bool] = {}
    head = subprocess.run(["git", "-C", str(CHECKOUT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    tracked = subprocess.run(["git", "-C", str(CHECKOUT), "status", "--porcelain", "--untracked-files=no"],
                             capture_output=True, text=True).stdout.strip()
    checks["checkout_is_pinned_commit"] = head == manifest["audited_source"]["commit"]
    checks["checkout_has_no_tracked_changes"] = tracked == ""
    digests = manifest["audited_source"]["files"]
    checks["audited_files_match_digests"] = all(
        sha256(FORMAL / name) == digest for name, digest in digests.items())

    source = WITNESSES.read_text()
    checks["witnesses_free_of_escapes"] = re.search(
        r"\bsorry\b|\badmit\b|^\s*axiom\b|\bnative_decide\b", source, re.M) is None
    probe = lean("AuditWitnessesProbe.lean",
                 source + "".join(f"\n#print axioms {name}" for name in THEOREMS) + "\n")
    used: dict[str, list[str]] = {}
    for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", probe.stdout):
        used[match.group(1)] = sorted(a.strip() for a in match.group(2).split(",") if a.strip())
    checks["witnesses_compile"] = probe.returncode == 0 and "error" not in probe.stdout.lower()
    checks["witness_axioms"] = used
    checks["witness_axioms_standard"] = set(used) == set(THEOREMS) and all(
        set(v) <= STANDARD for v in used.values())

    too_few = source.replace("2^ℓ+1", "2^ℓ")
    controls["unsat_with_two_pow_l_pigeons_rejected"] = (
        too_few != source and lean("ControlTooFewPigeons.lean", too_few).returncode != 0)
    wrong_step = source.replace(".binary 2 5", ".binary 2 2", 1)
    controls["refutation_with_wrong_premises_rejected"] = (
        wrong_step != source and lean("ControlWrongStep.lean", wrong_step).returncode != 0)

    expected = {
        "checkout_is_pinned_commit": True,
        "checkout_has_no_tracked_changes": True,
        "audited_files_match_digests": True,
        "witnesses_free_of_escapes": True,
        "witnesses_compile": True,
        "witness_axioms_standard": True,
    }
    failures = [name for name, value in expected.items() if checks.get(name) != value]
    failures += [f"control {name}" for name, ok in controls.items() if not ok]
    if not checks["witnesses_compile"]:
        checks["compile_output_tail"] = (probe.stdout + probe.stderr)[-3000:]
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
    print(f"{result['status']}: {len(outcome['checks'])} checks, "
          f"{sum(outcome['controls'].values())}/{len(outcome['controls'])} controls rejected wrong input")
    for failure in outcome["failures"]:
        print(f"  failed: {failure}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
