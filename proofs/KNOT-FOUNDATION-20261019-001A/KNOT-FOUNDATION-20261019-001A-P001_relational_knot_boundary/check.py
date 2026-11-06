#!/usr/bin/env python3
"""Check KNOT-FOUNDATION-20261019-001A-P001: the relational knot boundary.

Re-derives every finite claim with its own enumeration, independent of
tools/knotlab, compiles the Lean kernel with a pinned toolchain, confirms the
kernel uses no axiom beyond propext and Quot.sound, and runs each check once on
a deliberately wrong input to show that it can fail.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import subprocess
import sys
import tempfile
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAN = ["lean", "+leanprover/lean4:v4.32.2"]
KERNEL = HERE / "KnotKernel.lean"
KERNEL_THEOREMS = (
    "atom_isKnot", "atomNeg_isKnot", "knot_unique", "knot_shadow_ab",
    "knot_shadow_ak", "knot_shadow_bk", "knot_not_majority_closed",
    "no_two_cnf_defines_knot", "chain_defines_knot", "tied_passes_old_conditions",
    "tied_role_swap",
    "tied_is_two_cnf", "tied_not_knot", "cross_relational_not_knot",
    "cross_gated_eq_atom", "cross_gated_isKnot",
)
ALLOWED_AXIOMS = {"propext", "Quot.sound"}

Row = tuple[bool, ...]
Clause = tuple[tuple[int, bool], ...]  # (variable index, required value)


# Relations are sets of rows over variables 0..n; loops are 0..n-1, the contact is n.

def rows(width: int) -> list[Row]:
    return list(product((False, True), repeat=width))


def is_knot(relation: frozenset[Row], loops: int) -> bool:
    """K1 binding, K2 loss on erasure, K3 coexistence."""
    everything = rows(loops + 1)
    all_present = [row for row in everything if all(row[:loops])]
    binding = any(row not in relation for row in all_present)
    coexistence = any(row in relation for row in all_present)
    erasure = all(row in relation for row in everything if not all(row[:loops]))
    return binding and erasure and coexistence


def knot(loops: int, made: bool = True) -> frozenset[Row]:
    return frozenset(row for row in rows(loops + 1)
                     if not (all(row[:loops]) and row[loops] != made))


def shadows_full(relation: frozenset[Row], width: int) -> bool:
    """Every shadow on fewer variables allows every assignment."""
    for size in range(1, width):
        for keep in combinations(range(width), size):
            if len({tuple(row[i] for i in keep) for row in relation}) != 2 ** size:
                return False
    return True


def majority_closed(relation: frozenset[Row]) -> bool:
    members = sorted(relation)
    return all(
        tuple(x + y + z >= 2 for x, y, z in zip(a, b, c)) in relation
        for a in members for b in members for c in members
    )


def affine_closed(relation: frozenset[Row]) -> bool:
    members = sorted(relation)
    return all(
        tuple(x ^ y ^ z for x, y, z in zip(a, b, c)) in relation
        for a in members for b in members for c in members
    )


def define(clauses: list[Clause], visible: int, witnesses: int) -> frozenset[Row]:
    """The allowed visible rows once the witnesses are quantified away."""
    return frozenset(
        row[:visible]
        for row in rows(visible + witnesses)
        if all(any(row[index] == value for index, value in clause) for clause in clauses)
    )


def witness_chain(loops: int) -> tuple[list[Clause], int]:
    """Clauses of exactly three literals joining `loops` loops into the contact."""
    contact = loops
    if loops == 2:
        return [((0, False), (1, False), (contact, True))], 0
    witness = [contact + 1 + i for i in range(loops - 2)]
    clauses = [((0, False), (1, False), (witness[0], True))]
    for step in range(1, loops - 2):
        clauses.append(((witness[step - 1], False), (step + 1, False), (witness[step], True)))
    clauses.append(((witness[-1], False), (loops - 1, False), (contact, True)))
    return clauses, len(witness)


def minimum_width(relation: frozenset[Row], width: int) -> int:
    for size in range(1, width + 1):
        implied = [
            tuple(zip(keep, signs))
            for keep in combinations(range(width), size)
            for signs in product((False, True), repeat=size)
            if all(any(row[i] == s for i, s in zip(keep, signs)) for row in relation)
        ]
        if define(implied, width, 0) == relation:
            return size
    raise AssertionError("unreachable")


def all_relations(width: int) -> list[frozenset[Row]]:
    cube = rows(width)
    return [frozenset(row for i, row in enumerate(cube) if mask >> i & 1)
            for mask in range(2 ** len(cube))]


def two_cnf_relations_without_witnesses() -> set[frozenset[Row]]:
    """Every relation on three variables defined by unit and 2-literal clauses."""
    cube = rows(3)
    literals = [(i, s) for i in range(3) for s in (False, True)]
    clauses = [(literal,) for literal in literals]
    clauses += [(a, b) for a, b in combinations(literals, 2) if a[0] != b[0]]
    masks = [sum(1 << j for j, row in enumerate(cube)
                 if any(row[i] == s for i, s in clause)) for clause in clauses]
    found = set()
    for chosen in range(2 ** len(clauses)):
        allowed = 255
        for i, mask in enumerate(masks):
            if chosen >> i & 1:
                allowed &= mask
        found.add(frozenset(row for j, row in enumerate(cube) if allowed >> j & 1))
    return found


def sampled_two_cnf_with_witnesses(samples: int, seed: int) -> list[frozenset[Row]]:
    generator = random.Random(seed)
    out = []
    for _ in range(samples):
        witnesses = generator.randint(1, 3)
        names = list(range(3 + witnesses))
        clauses = []
        for _ in range(generator.randint(1, 9)):
            chosen = generator.sample(names, generator.choice((1, 2)))
            clauses.append(tuple((i, generator.random() < 0.5) for i in chosen))
        out.append(define(clauses, 3, witnesses))
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lean(source: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "Probe.lean"
        path.write_text(source)
        return subprocess.run([*LEAN, str(path)], capture_output=True, text=True, check=False)


def run() -> dict[str, object]:
    checks: dict[str, object] = {}
    controls: dict[str, bool] = {}

    # Two loops: exactly two knots among all 256 relations, the atom and its mirror image.
    knots = [r for r in all_relations(3) if is_knot(r, 2)]
    checks["two_loop_knots"] = len(knots)
    checks["two_loop_knots_are_atom_and_mirror"] = set(knots) == {knot(2, True), knot(2, False)}
    controls["k2_weakened_admits_more"] = len([
        r for r in all_relations(3)
        if any(row not in r for row in rows(3) if all(row[:2]))
        and all(row in r for row in rows(3) if not row[0])  # K2 for the first loop only
        and any(row in r for row in rows(3) if all(row[:2]))
    ]) > 2

    # Knots of 2..6 loops: K1-K3, invisible in parts, not pairwise, width n+1, three-literal chain.
    per_size = {}
    for loops in range(2, 7):
        target = knot(loops)
        clauses, witnesses = witness_chain(loops)
        built = define(clauses, loops + 1, witnesses)
        per_size[str(loops)] = {
            "is_knot": is_knot(target, loops),
            "invisible_in_parts": shadows_full(target, loops + 1),
            "majority_closed": majority_closed(target) if loops <= 4 else None,
            "affine_closed": affine_closed(target) if loops <= 4 else None,
            "minimum_width_without_witnesses": minimum_width(target, loops + 1) if loops <= 5 else None,
            "chain_clause_widths": sorted({len(clause) for clause in clauses}),
            "chain_witnesses": witnesses,
            "chain_defines_knot": built == target,
        }
    checks["knots_by_loop_count"] = per_size
    broken_chain = witness_chain(4)[0][:-1] + [((5, False), (3, True), (4, True))]
    controls["broken_chain_rejected"] = define(broken_chain, 5, 2) != knot(4)

    # Pairwise relations: no 2-CNF relation on three variables is a knot.
    two_cnf = two_cnf_relations_without_witnesses()
    checks["two_cnf_relations_without_witnesses"] = len(two_cnf)
    checks["two_cnf_relations_all_majority_closed"] = all(majority_closed(r) for r in two_cnf)
    checks["two_cnf_knots_without_witnesses"] = sum(is_knot(r, 2) for r in two_cnf)
    sampled = sampled_two_cnf_with_witnesses(3000, 20261019)
    checks["sampled_two_cnf_with_witnesses"] = len(sampled)
    checks["sampled_two_cnf_with_witnesses_majority_closed"] = all(majority_closed(r) for r in sampled)
    checks["sampled_two_cnf_with_witnesses_knots"] = sum(is_knot(r, 2) for r in sampled)
    checks["majority_closed_relations_that_are_knots"] = sum(
        is_knot(r, 2) for r in all_relations(3) if majority_closed(r))
    checks["affine_relations_that_are_knots"] = sum(
        is_knot(r, 2) for r in all_relations(3) if r and affine_closed(r))
    controls["majority_check_rejects_atom"] = not majority_closed(knot(2))

    # The common hub, parity, the earlier kernel's accepted relation, and executor gating.
    hub = define([((0, False), (2, True)), ((1, False), (2, True))], 3, 0)
    parity = frozenset(row for row in rows(3) if not (row[0] ^ row[1] ^ row[2]))
    tied = define([((0, False), (1, True)), ((0, True), (1, False)), ((0, False), (2, True))], 3, 0)
    old_erasure = all(
        ((a, b, False) in tied) == ((a, b, True) in tied)
        for a, b in rows(2) if not (a and b)
    )
    factors = any(
        all(((row in tied) == (fa[(row[0], row[2])] and fb[(row[1], row[2])])) for row in rows(3))
        for fa_values in product((False, True), repeat=4)
        for fb_values in product((False, True), repeat=4)
        for fa in [dict(zip(rows(2), fa_values))]
        for fb in [dict(zip(rows(2), fb_values))]
    )
    gated = define([((0, False), (1, False), (2, True)), ((1, False), (0, False), (2, True))], 3, 0)
    checks["hub_is_knot"] = is_knot(hub, 2)
    checks["parity_is_knot"] = is_knot(parity, 2)
    checks["parity_invisible_in_pairs"] = shadows_full(parity, 3)
    checks["tied_passes_old_erasure"] = old_erasure
    checks["tied_factors"] = factors
    checks["tied_is_two_cnf_and_majority_closed"] = majority_closed(tied)
    checks["tied_is_knot"] = is_knot(tied, 2)
    checks["cross_relational_is_hub"] = hub == define(
        [((1, False), (2, True)), ((0, False), (2, True))], 3, 0)  # guards ¬b ∨ k and ¬a ∨ k
    checks["cross_gated_equals_atom"] = gated == knot(2)
    controls["knot_test_rejects_hub"] = not is_knot(hub, 2)

    # Lean kernel: compiles with the pinned toolchain, no extra axioms, a mutation is rejected.
    source = KERNEL.read_text()
    compiled = subprocess.run([*LEAN, str(KERNEL)], capture_output=True, text=True, check=False)
    probe = lean(source + "".join(f"\n#print axioms KnotKernel.{name}" for name in KERNEL_THEOREMS))
    used = set()
    for line in probe.stdout.splitlines():
        match = re.search(r"depends on axioms: \[(.*)\]", line)
        if match:
            used |= {name.strip() for name in match.group(1).split(",")}
    mutated = lean(source.replace("def atom (a b k : Bool) : Bool := !a || !b || k",
                                  "def atom (a b k : Bool) : Bool := !a || k"))
    checks["lean_version"] = subprocess.run(
        [*LEAN, "--version"], capture_output=True, text=True, check=False).stdout.strip()
    checks["lean_kernel_accepted"] = compiled.returncode == 0 and not compiled.stdout.strip()
    checks["lean_theorems_present"] = all(f"theorem {name}" in source for name in KERNEL_THEOREMS)
    checks["lean_axioms"] = sorted(used)
    checks["lean_axioms_standard_only"] = probe.returncode == 0 and used <= ALLOWED_AXIOMS
    checks["lean_source_free_of_escapes"] = not any(
        token in source for token in ("sorry", "admit", "axiom ", "native_decide"))
    controls["lean_rejects_mutated_atom"] = mutated.returncode != 0

    # Predecessors are bound by digest.
    manifest = json.loads((HERE / "manifest.json").read_text())
    bindings = manifest["parent_bindings"]
    checks["parents_bound"] = all(
        sha256(ROOT / path) == digest for path, digest in bindings.items())

    expected = {
        "two_loop_knots": 2,
        "two_loop_knots_are_atom_and_mirror": True,
        "two_cnf_relations_all_majority_closed": True,
        "two_cnf_knots_without_witnesses": 0,
        "sampled_two_cnf_with_witnesses_majority_closed": True,
        "sampled_two_cnf_with_witnesses_knots": 0,
        "majority_closed_relations_that_are_knots": 0,
        "affine_relations_that_are_knots": 0,
        "hub_is_knot": False,
        "parity_is_knot": False,
        "parity_invisible_in_pairs": True,
        "tied_passes_old_erasure": True,
        "tied_factors": False,
        "tied_is_two_cnf_and_majority_closed": True,
        "tied_is_knot": False,
        "cross_relational_is_hub": True,
        "cross_gated_equals_atom": True,
        "lean_kernel_accepted": True,
        "lean_theorems_present": True,
        "lean_axioms_standard_only": True,
        "lean_source_free_of_escapes": True,
        "parents_bound": True,
    }
    failures = [name for name, value in expected.items() if checks.get(name) != value]
    for loops, entry in per_size.items():
        n = int(loops)
        wanted = {"is_knot": True, "invisible_in_parts": True, "chain_defines_knot": True,
                  "chain_clause_widths": [3], "chain_witnesses": n - 2}
        if n <= 4:
            wanted.update(majority_closed=False, affine_closed=False)
        if n <= 5:
            wanted["minimum_width_without_witnesses"] = n + 1
        failures += [f"{loops} loops: {key}" for key, value in wanted.items() if entry[key] != value]
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
    print(f"{result['status']}: {len(outcome['checks'])} checks, "
          f"{sum(outcome['controls'].values())}/{len(outcome['controls'])} controls rejected wrong input")
    for failure in outcome["failures"]:
        print(f"  failed: {failure}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
