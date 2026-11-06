#!/usr/bin/env python3
"""Check HOLE-CRITERION-COLOURING-20261019-001B-P001: Braun's bound for more pigeons, and bit-colouring.

Binds the proof to the exact pinned sources (checkout commit, no tracked
changes, SHA-256 of every file whose declarations the proof uses), compiles
MorePigeonsColouring.lean against the author's built project, confirms that
every stated theorem uses only the standard axioms, and runs four controls that
change the mathematics; each must be rejected:

- the bound's constant lowered from 8192 to 2048 throughout its proof, which
  must fail exactly at the step that calibrates the kernel degree;
- the transfer without the properness hypothesis;
- unsatisfiability of bit-PHP claimed with as many pigeons as labels;
- unsatisfiability of bit-colouring claimed without a monochromatic edge.

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
CHECKOUT = Path("/home/jscul/external-audits/bit-php-check")
FORMAL = CHECKOUT / "formalization"
TMP = FORMAL / ".lake" / "audit_controls"
KERNEL = HERE / "MorePigeonsColouring.lean"
THEOREMS = tuple(f"MorePigeonsColouring.{name}" for name in (
    "bitPHP_more_pigeons", "colouring_refutation_transfer", "bitColouring_more_pigeons", "range_nonempty",
    "usualBitPHP_unsat_more", "bitColouring_unsat", "bitColouring_sat", "complete_graph_is_bitPHP"))
STANDARD = {"propext", "Classical.choice", "Quot.sound"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lean(name: str, source: str) -> subprocess.CompletedProcess[str]:
    TMP.mkdir(parents=True, exist_ok=True)
    path = TMP / name
    path.write_text(source)
    return subprocess.run(["lake", "env", "lean", str(path)], cwd=FORMAL, capture_output=True, text=True,
                          check=False, timeout=3600)


def first_error_line(output: str, name: str) -> int | None:
    match = re.search(rf"{re.escape(name)}:(\d+):\d+: error", output)
    return int(match.group(1)) if match else None


def block(source: str, start: str, end: str) -> tuple[int, int]:
    first = source.index(start)
    return first, source.index(end, first)


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
    checks["relied_on_files_match_digests"] = bool(digests) and all(
        sha256(FORMAL / name) == digest for name, digest in digests.items())

    source = KERNEL.read_text()
    checks["kernel_free_of_escapes"] = re.search(
        r"\bsorry\b|\badmit\b|^\s*axiom\b|\bnative_decide\b|\bimplemented_by\b|\bunsafe\b", source, re.M) is None
    probe = lean("MorePigeonsColouringProbe.lean",
                 source + "".join(f"\n#print axioms {name}" for name in THEOREMS) + "\n")
    used: dict[str, list[str]] = {}
    flat = re.sub(r"\n\s+", " ", probe.stdout)
    for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat):
        used[match.group(1)] = sorted(a.strip() for a in match.group(2).split(",") if a.strip())
    checks["kernel_compiles"] = probe.returncode == 0 and "error" not in probe.stdout.lower()
    checks["theorem_axioms"] = used
    checks["theorem_axioms_standard"] = set(used) == set(THEOREMS) and all(set(v) <= STANDARD for v in used.values())

    # Control 1: a four times larger exponent, with the proof adjusted consistently.
    start, end = block(source, "theorem bitPHP_more_pigeons", "/-! ## Bit-colouring")
    lowered = source[:start] + source[start:end].replace("8192", "2048").replace("4096", "1024") + source[end:]
    calibrate = lowered.index("nlinarith [sq_nonneg ((ℓ:ℝ)*(k:ℝ))]")
    calibrate_line = lowered[:calibrate].count("\n") + 1
    outcome = lean("ControlLargerExponent.lean", lowered)
    failed_at = first_error_line(outcome.stdout, "ControlLargerExponent.lean")
    checks["larger_exponent_first_error_line"] = failed_at
    checks["larger_exponent_calibration_line"] = calibrate_line
    controls["larger_exponent_rejected_at_calibration"] = (
        lowered != source and outcome.returncode != 0 and failed_at == calibrate_line)

    # Control 2: the transfer without properness.
    improper = source.replace("(hf : ∀ u w, G.Adj u w → f u ≠ f w) {C : FiniteParityClause (BitVar v ℓ)}",
                              "(hf : ∀ u w, G.Adj u w → True) {C : FiniteParityClause (BitVar v ℓ)}", 1)
    controls["transfer_without_properness_rejected"] = (
        improper != source and lean("ControlImproper.lean", improper).returncode != 0)

    # Control 3: as many pigeons as labels.
    equal = source.replace("(hm : 2^ℓ < m) (x : BitVar m ℓ → ZMod 2)", "(hm : 2^ℓ ≤ m) (x : BitVar m ℓ → ZMod 2)", 1)
    controls["unsat_with_as_many_pigeons_as_labels_rejected"] = (
        equal != source and lean("ControlEqualPigeons.lean", equal).returncode != 0)

    # Control 4: no monochromatic edge in the hypothesis.
    loose = source.replace("∃ u w, G.Adj u w ∧ c u = c w)", "∃ u w, G.Adj u w ∨ c u = c w)", 1)
    controls["colouring_unsat_without_conflict_rejected"] = (
        loose != source and lean("ControlLooseConflict.lean", loose).returncode != 0)

    expected = {
        "checkout_is_pinned_commit": True,
        "checkout_has_no_tracked_changes": True,
        "relied_on_files_match_digests": True,
        "kernel_free_of_escapes": True,
        "kernel_compiles": True,
        "theorem_axioms_standard": True,
    }
    failures = [name for name, value in expected.items() if checks.get(name) != value]
    failures += [f"control {name}" for name, ok in controls.items() if not ok]
    if not checks["kernel_compiles"]:
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
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
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
