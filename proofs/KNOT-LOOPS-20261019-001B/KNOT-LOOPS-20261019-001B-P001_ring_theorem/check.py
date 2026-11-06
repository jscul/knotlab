#!/usr/bin/env python3
"""Check KNOT-LOOPS-20261019-001B-P001: the ring theorem.

Compiles RingKernel.lean with the pinned toolchain (core Lean, no Mathlib),
confirms that every main theorem uses only the standard axioms, and runs four
controls that change the mathematics; each must be rejected:

- a ring excludes a pattern with an even number of swaps;
- links without the middle-distinction separation (not knots);
- a ring of k copies remembers some pattern whenever the link has a swap,
  whatever k and the identity tables;
- parity links with the middle distinctions left out of the parity.

It then confirms that the theorems agree with the exact census
KNOT-LOOPS-20261019-001A-E001 on every placement it covers.

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
KERNEL = HERE / "RingKernel.lean"
CENSUS = ROOT / "artifacts/KNOT-LOOPS-20261019-001A/KNOT-LOOPS-20261019-001A-E001_ring_census"
THEOREMS = ("transfer_cases", "ring_excludes_iff", "ring_one_flip", "all_permutations_iff_parity",
            "ring_memory", "parity3_every_length")
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
IDENTITY, SWAP = 9, 6


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
    probe = lean(source + "".join(f"\n#print axioms RingKernel.{name}" for name in THEOREMS) + "\n")
    used: dict[str, list[str]] = {}
    for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", re.sub(r"\n\s+", " ", probe.stdout)):
        used[match.group(1)] = sorted(a.strip() for a in match.group(2).split(",") if a.strip())
    for match in re.finditer(r"'([^']+)' does not depend on any axioms", probe.stdout):
        used[match.group(1)] = []
    checks["theorem_axioms"] = used
    checks["theorem_axioms_standard"] = (set(used) == {f"RingKernel.{n}" for n in THEOREMS}
                                         and all(set(v) <= STANDARD for v in used.values()))

    controls["even_swaps_rejected"] = lean(mutate(
        source, "ringCloses cs = false ↔ (∀ c ∈ cs, IsPerm c.transfer) ∧ swaps (cs.map Copy.transfer) = true",
        "ringCloses cs = false ↔ (∀ c ∈ cs, IsPerm c.transfer) ∧ swaps (cs.map Copy.transfer) = false")).returncode != 0
    controls["links_that_are_not_knots_rejected"] = lean(mutate(
        source, "  sep_mid : ∀ a m b n, m.length = d → n < d → allowed a m b = false →\n"
                "    allowed a (flipAt m n) b = false → False\n", "")).returncode != 0
    controls["memory_without_identity_condition_rejected"] = lean(mutate(
        source, "        (k % 2 = 1 ∨ ∃ m, m.length = d ∧ L.transfer m = idT)) := by",
        "        True) := by")).returncode != 0
    controls["parity_without_middles_rejected"] = lean(mutate(
        source, "  ∃ c : Bool, ∀ a m b, m.length = d → L.allowed a m b = ((a ^^ b ^^ parity m) == c)",
        "  ∃ c : Bool, ∀ a m b, m.length = d → L.allowed a m b = ((a ^^ b) == c)")).returncode != 0

    # agreement with the census
    rows = [json.loads(line) for line in (CENSUS / "raw_rows.jsonl").read_text().splitlines()]
    rings = [r for r in rows if r["part"] == "ring"]
    census = json.loads((CENSUS / "result.json").read_text())
    agree = {"exclusion_rule": census["P2_excluded_sets_match"] and census["mixed_rings"]["P2_mismatches"] == 0,
             "knot_or_free": census["P1_no_other_or_contradiction"] and census["mixed_rings"]["P1_violations"] == 0}
    lengths_ok = parity_ok = cases_ok = 0
    for r in rings:
        tables = list(r["transfers"].values())
        has_swap, has_id = SWAP in tables, IDENTITY in tables
        max_k = 8 if r["n"] == 3 else 6
        theorem_lengths = [k for k in range(1, max_k + 1) if has_swap and (k % 2 == 1 or has_id)]
        lengths_ok += theorem_lengths == r["constrained_lengths"]
        parity_ok += r["all_permutations"] == r["parity_knot"]
        cases_ok += all(t in (IDENTITY, SWAP) or bin(t).count("1") >= 3 for t in tables)
    agree["memory_lengths"] = lengths_ok == len(rings)
    agree["permutations_iff_parity"] = parity_ok == len(rings)
    agree["transfer_cases"] = cases_ok == len(rings)
    checks["census_placements"] = len(rings)
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
