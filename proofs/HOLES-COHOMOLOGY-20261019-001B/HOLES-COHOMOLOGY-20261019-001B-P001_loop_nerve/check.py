#!/usr/bin/env python3
"""Check HOLES-COHOMOLOGY-20261019-001B-P001: what permutation contact remembers.

Compiles LoopNerve.lean with the pinned toolchain (core Lean, no Mathlib),
confirms that every main theorem uses only the standard axioms, and runs five
controls that change the mathematics; each must be rejected:

- a loop closes only if every witness value is fixed (instead of some);
- on a minimal non-face, any selected loop is excluded (instead of all);
- free contact allows no minimal non-face at all (single loops can be one);
- a knot among k loops needs k + 2 values (the star uses k + 1);
- every family of sets is a nerve, down-closed or not.

It then confirms that the theorems agree with the exact census
HOLES-COHOMOLOGY-20261019-001A-E001 on every case it covers.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAN = ["lean", "+leanprover/lean4:v4.32.2"]
KERNEL = HERE / "LoopNerve.lean"
CENSUS = ROOT / "artifacts/HOLES-COHOMOLOGY-20261019-001A/HOLES-COHOMOLOGY-20261019-001A-E001_holonomy_census"
THEOREMS = ("loop_rule", "bouquet_rule", "shape_is_nerve", "minimal_nonface_excludes_only_all",
            "minimal_nonface_is_knot", "free_contact_binds_nothing", "knot_needs_more_values", "star_is_knot",
            "star_injective", "three_loops_need_four_values", "four_values_knot_three_loops",
            "boolean_contact_never_ties", "flip_involutive", "every_complex_is_a_nerve")
STANDARD = {"propext", "Classical.choice", "Quot.sound"}


def lean(source: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "Probe.lean"
        path.write_text(source)
        return subprocess.run(LEAN + [str(path)], capture_output=True, text=True, timeout=1800, check=False)


def mutate(source: str, old: str, new: str) -> str:
    assert source.count(old) == 1, old
    return source.replace(old, new)


def run() -> dict[str, object]:
    source = KERNEL.read_text()
    checks: dict[str, object] = {}
    controls: dict[str, bool] = {}

    checks["lean_version"] = subprocess.run(LEAN + ["--version"], capture_output=True, text=True).stdout.strip()
    compiled = lean(source)
    checks["lean_kernel_accepted"] = compiled.returncode == 0 and not compiled.stdout.strip()
    checks["lean_source_free_of_escapes"] = re.search(
        r"\bsorry\b|\badmit\b|^\s*axiom\b|\bnative_decide\b|\bimplemented_by\b|\bunsafe\b", source, re.M) is None
    probe = lean(source + "".join(f"\n#print axioms LoopNerve.{name}" for name in THEOREMS) + "\n")
    used: dict[str, list[str]] = {}
    for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", re.sub(r"\n\s+", " ", probe.stdout)):
        used[match.group(1)] = sorted(a.strip() for a in match.group(2).split(",") if a.strip())
    for match in re.finditer(r"'([^']+)' does not depend on any axioms", probe.stdout):
        used[match.group(1)] = []
    checks["theorem_axioms"] = used
    checks["theorem_axioms_standard"] = (set(used) == {f"LoopNerve.{n}" for n in THEOREMS}
                                         and all(set(v) <= STANDARD for v in used.values()))

    controls["every_value_fixed_rejected"] = lean(mutate(
        source, "Closes (fs.map graphOf) ↔ ∃ a, run fs a = a := by",
        "Closes (fs.map graphOf) ↔ ∀ a, run fs a = a := by")).returncode != 0
    controls["any_selected_excluded_rejected"] = lean(mutate(
        source, "Proj h S t ↔ ¬ ∀ i, S i → t i = true := by",
        "Proj h S t ↔ ¬ ∃ i, S i ∧ t i = true := by")).returncode != 0
    controls["free_contact_without_single_loops_rejected"] = lean(mutate(
        source, "(S : ι → Prop) (hm : MinimalNonFace h S) : ∀ i j, S i → S j → i = j := by",
        "(S : ι → Prop) (hm : MinimalNonFace h S) : False := by")).returncode != 0
    controls["k_plus_two_values_rejected"] = lean(mutate(
        source, "(hinj : ∀ i a b, h i a = h i b → a = b) (hknot : KnotAmong h) : k + 1 ≤ n := by",
        "(hinj : ∀ i a b, h i a = h i b → a = b) (hknot : KnotAmong h) : k + 2 ≤ n := by")).returncode != 0
    controls["families_not_down_closed_rejected"] = lean(mutate(
        source, "    (hdown : DownClosed N) (hempty : N (fun _ => false)) (S : ι → Bool) :",
        "    (hdown : ∀ F, N F → N F) (hempty : N (fun _ => false)) (S : ι → Bool) :")).returncode != 0

    # agreement with the census
    census = json.loads((CENSUS / "result.json").read_text())
    selectors = census["selectors"]
    agree = {
        "loop_rule_and_network_rule": census["predictions"]["P1"],
        "shape_is_nerve": all(s.get("shape_mismatches", 0) == 0 for s in selectors.values()),
        "knots_among_loops_are_atoms": all(s.get("knot_check_failures", 0) == 0 and s.get("non_atom_knots", 0) == 0
                                           for s in selectors.values()),
        "free_contact_binds_nothing": all(s.get("ties_under_free_contact", 0) == 0
                                          and s.get("knots_under_free_contact", 0) == 0 for s in selectors.values()),
        "no_knot_among_three_loops_on_three_values": selectors["k3_n3"].get("knots_among_3_loops", 0) == 0,
        "knots_among_three_loops_on_four_values_are_the_24_stars": selectors["k3_n4"].get("knots_among_3_loops") == 24,
        "size_bound": all(b["knots_on_k_values"] == 0 and b["star_is_knot"] for b in census["size_bound"].values()),
        "every_complex_occurs": census["complexes"]["mismatches"] == 0,
    }
    checks["census_agreement"] = agree
    checks["census_agrees"] = all(agree.values())

    expected = ["lean_kernel_accepted", "lean_source_free_of_escapes", "theorem_axioms_standard", "census_agrees"]
    failures = [name for name in expected if checks.get(name) is not True]
    failures += [f"control {name}" for name, ok in controls.items() if not ok]
    if not checks["lean_kernel_accepted"]:
        checks["compile_output_tail"] = (compiled.stdout + compiled.stderr)[-3000:]
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
