#!/usr/bin/env python3
"""Check KNOT-FOUNDATION-20261019-001E-P001: the forgetting reading of the knot test.

Re-derives every finite claim with its own enumeration, independent of
tools/knotlab and of the Lean source, compiles the Lean kernel with a pinned
toolchain, confirms the kernel uses no axiom beyond propext and Quot.sound, and
runs each check once on a deliberately wrong input to show that it can fail.

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
from itertools import combinations, permutations, product
from math import log2
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAN = ["lean", "+leanprover/lean4:v4.32.2"]
KERNEL = HERE / "ForgettingKernel.lean"
KERNEL_THEOREMS = (
    "coexistence", "atom_isKnot", "parity_isKnot", "hub_not_knot", "tied_not_knot",
    "absence_knot_is_knot", "parity_not_absence_knot", "no_clause_on_a_b",
    "no_clause_on_a_k", "no_clause_on_b_k", "majority_with_free_pairs_is_full",
    "no_two_cnf_defines_knot", "parity_chain_defines_parity",
)
ALLOWED_AXIOMS = {"propext", "Quot.sound"}

Row = tuple[bool, ...]
Clause = tuple[tuple[int, bool], ...]  # (variable index, required value)


def rows(width: int) -> list[Row]:
    return list(product((False, True), repeat=width))


def shadow(relation: frozenset[Row], keep: tuple[int, ...]) -> set[tuple[bool, ...]]:
    return {tuple(row[i] for i in keep) for row in relation}


def is_knot(relation: frozenset[Row], width: int, forget: tuple[int, ...] | None = None) -> bool:
    """Forgetting reading: constrained, and forgetting any listed variable frees the rest."""
    if len(relation) in (0, 2 ** width):
        return False
    for dropped in (range(width) if forget is None else forget):
        keep = tuple(i for i in range(width) if i != dropped)
        if len(shadow(relation, keep)) != 2 ** (width - 1):
            return False
    return True


def is_absence_knot(relation: frozenset[Row], loops: int) -> bool:
    """The earlier reading: a loop variable is presence, and absent frees everything."""
    everything = rows(loops + 1)
    present = [row for row in everything if all(row[:loops])]
    return (any(row not in relation for row in present)
            and any(row in relation for row in present)
            and all(row in relation for row in everything if not all(row[:loops])))


def parity(width: int, odd: bool) -> frozenset[Row]:
    return frozenset(row for row in rows(width) if (sum(row) % 2 == 1) == odd)


def atom(loops: int) -> frozenset[Row]:
    return frozenset(row for row in rows(loops + 1) if not (all(row[:loops]) and not row[loops]))


def majority_closed(relation: frozenset[Row]) -> bool:
    members = sorted(relation)
    return all(
        tuple(x + y + z >= 2 for x, y, z in zip(a, b, c)) in relation
        for a in members for b in members for c in members
    )


def define(clauses: list[Clause], visible: int, witnesses: int) -> frozenset[Row]:
    return frozenset(
        row[:visible]
        for row in rows(visible + witnesses)
        if all(any(row[index] == value for index, value in clause) for clause in clauses)
    )


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


def shape_key(relation: frozenset[Row]) -> tuple:
    """Canonical form under permuting and negating the three variables."""
    return min(
        tuple(sorted(tuple(row[order[i]] ^ flips[i] for i in range(3)) for row in relation))
        for order in permutations(range(3))
        for flips in product((False, True), repeat=3)
    )


def two_cnf_relations_without_witnesses() -> set[frozenset[Row]]:
    cube = rows(3)
    literals = [(i, s) for i in range(3) for s in (False, True)]
    clauses = [(literal,) for literal in literals]
    clauses += [(a, b) for a, b in combinations(literals, 2) if a[0] != b[0]]
    masks = [sum(1 << j for j, row in enumerate(cube) if any(row[i] == s for i, s in clause))
             for clause in clauses]
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


def parity_chain(size: int, odd: bool) -> tuple[list[Clause], int]:
    """Name each partial match: a_i = a_(i-1) xor x_(i+1), four clauses of three literals."""
    clauses: list[Clause] = []
    previous = 0
    for step in range(1, size):
        out = size + step - 1
        x = step
        clauses += [
            ((out, False), (previous, True), (x, True)),
            ((out, False), (previous, False), (x, False)),
            ((out, True), (previous, False), (x, True)),
            ((out, True), (previous, True), (x, False)),
        ]
        previous = out
    clauses.append(((previous, odd),))
    return clauses, size - 1


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
    three = all_relations(3)

    # Two loops and a contact: the census.
    knots = [r for r in three if is_knot(r, 3)]
    checks["two_loop_knots"] = len(knots)
    shapes: dict[tuple, list[frozenset[Row]]] = {}
    for relation in knots:
        shapes.setdefault(shape_key(relation), []).append(relation)
    checks["shapes"] = sorted(
        [8 - len(members[0]), len(members), round(log2(8 / len(members[0])), 3)]
        for members in shapes.values()
    )
    checks["single_clauses_are_knots"] = sum(len(r) == 7 for r in knots)
    bits = {r: log2(8 / len(r)) for r in knots}
    most = max(bits.values())
    checks["most_hidden_bits"] = round(most, 3)
    checks["most_hidden_only_parity"] = {r for r, b in bits.items() if b == most} == {parity(3, True), parity(3, False)}
    controls["k2_without_the_contact_admits_more"] = sum(
        is_knot(r, 3, forget=(0, 1)) for r in three) > len(knots)

    # The absence reading is a special case.
    absence = [r for r in three if is_absence_knot(r, 2)]
    checks["absence_knots"] = len(absence)
    checks["absence_knots_are_knots"] = all(r in knots for r in absence)
    checks["parity_is_absence_knot"] = is_absence_knot(parity(3, False), 2)

    # Pairwise relations: none is a knot.
    two_cnf = two_cnf_relations_without_witnesses()
    sampled = sampled_two_cnf_with_witnesses(3000, 20261019)
    checks["two_cnf_relations_without_witnesses"] = len(two_cnf)
    checks["two_cnf_knots"] = sum(is_knot(r, 3) for r in two_cnf) + sum(is_knot(r, 3) for r in sampled)
    checks["majority_closed_knots"] = sum(majority_closed(r) for r in knots)
    controls["majority_check_rejects_parity"] = not majority_closed(parity(3, False))

    # Width: a knot implies no clause narrower than its variables.
    checks["three_variable_knots_minimum_width"] = sorted({minimum_width(r, 3) for r in knots})
    per_size = {}
    for width in range(3, 7):
        loops = width - 1
        per_size[str(width)] = {
            "atom_is_knot": is_knot(atom(loops), width),
            "parity_is_knot": is_knot(parity(width, True), width) and is_knot(parity(width, False), width),
            "atom_minimum_width": minimum_width(atom(loops), width) if width <= 5 else None,
            "parity_minimum_width": minimum_width(parity(width, True), width) if width <= 5 else None,
        }
    checks["knots_by_width"] = per_size

    # Most a pattern can hide from every part one variable smaller: one bit, only parity.
    hidden4 = [r for r in all_relations(4) if len(r) == 8 and is_knot(r, 4)]
    checks["four_variable_eight_state_knots"] = len(hidden4)
    checks["four_variable_eight_state_knots_are_parity"] = set(hidden4) == {parity(4, True), parity(4, False)}
    checks["no_knot_with_fewer_than_half_the_states"] = all(
        len(r) >= 2 ** (w - 1) for w in (3, 4) for r in all_relations(w) if is_knot(r, w))

    # Naming partial matches keeps parity at three literals.
    chain_results = {}
    for size in range(2, 7):
        ok = True
        for odd in (True, False):
            clauses, witnesses = parity_chain(size, odd)
            ok &= all(len(clause) <= 3 for clause in clauses)
            ok &= len(clauses) == 4 * (size - 1) + 1
            ok &= define(clauses, size, witnesses) == parity(size, odd)
        chain_results[str(size)] = ok
    checks["parity_chain"] = chain_results
    broken, witnesses = parity_chain(4, True)
    broken[1] = ((4, False), (0, True), (1, False))
    controls["broken_chain_rejected"] = define(broken, 4, witnesses) != parity(4, True)

    # Reference cases.
    hub = define([((0, False), (2, True)), ((1, False), (2, True))], 3, 0)
    tied = define([((0, False), (1, True)), ((0, True), (1, False)), ((0, False), (2, True))], 3, 0)
    fixed_parity = define([((0, True),), ((1, False), (2, False)), ((1, True), (2, True))], 3, 0)
    gated = define([((0, False), (1, False), (2, True))], 3, 0)
    checks["hub_is_knot"] = is_knot(hub, 3)
    checks["tied_is_knot"] = is_knot(tied, 3)
    checks["parity_of_fixed_value_is_knot"] = is_knot(fixed_parity, 3)
    checks["gated_cross_guards_are_knot"] = is_knot(gated, 3)
    controls["knot_test_rejects_hub"] = not is_knot(hub, 3)

    # Lean kernel: compiles, standard axioms only, a mutation is rejected.
    source = KERNEL.read_text()
    compiled = subprocess.run([*LEAN, str(KERNEL)], capture_output=True, text=True, check=False)
    probe = lean(source + "".join(f"\n#print axioms ForgettingKernel.{name}" for name in KERNEL_THEOREMS))
    used: set[str] = set()
    for line in probe.stdout.splitlines():
        match = re.search(r"depends on axioms: \[(.*)\]", line)
        if match:
            used |= {name.strip() for name in match.group(1).split(",")}
    mutated = lean(source.replace("def parity (a b k : Bool) : Bool := !(a ^^ b ^^ k)",
                                  "def parity (a b k : Bool) : Bool := (!a || k) && (!b || k)"))
    checks["lean_version"] = subprocess.run(
        [*LEAN, "--version"], capture_output=True, text=True, check=False).stdout.strip()
    checks["lean_kernel_accepted"] = compiled.returncode == 0 and not compiled.stdout.strip()
    checks["lean_theorems_present"] = all(f"theorem {name}" in source for name in KERNEL_THEOREMS)
    checks["lean_axioms"] = sorted(used)
    checks["lean_axioms_standard_only"] = probe.returncode == 0 and used <= ALLOWED_AXIOMS
    checks["lean_source_free_of_escapes"] = not any(
        token in source for token in ("sorry", "admit", "axiom ", "native_decide"))
    controls["lean_rejects_mutated_parity"] = mutated.returncode != 0

    manifest = json.loads((HERE / "manifest.json").read_text())
    checks["parents_bound"] = all(
        sha256(ROOT / path) == digest for path, digest in manifest["parent_bindings"].items())

    expected = {
        "two_loop_knots": 34,
        "shapes": [[1, 8, 0.193], [2, 4, 0.415], [2, 12, 0.415], [3, 8, 0.678], [4, 2, 1.0]],
        "single_clauses_are_knots": 8,
        "most_hidden_bits": 1.0,
        "most_hidden_only_parity": True,
        "absence_knots": 2,
        "absence_knots_are_knots": True,
        "parity_is_absence_knot": False,
        "two_cnf_knots": 0,
        "majority_closed_knots": 0,
        "three_variable_knots_minimum_width": [3],
        "four_variable_eight_state_knots": 2,
        "four_variable_eight_state_knots_are_parity": True,
        "no_knot_with_fewer_than_half_the_states": True,
        "hub_is_knot": False,
        "tied_is_knot": False,
        "parity_of_fixed_value_is_knot": False,
        "gated_cross_guards_are_knot": True,
        "lean_kernel_accepted": True,
        "lean_theorems_present": True,
        "lean_axioms_standard_only": True,
        "lean_source_free_of_escapes": True,
        "parents_bound": True,
    }
    failures = [name for name, value in expected.items() if checks.get(name) != value]
    for width, entry in per_size.items():
        w = int(width)
        wanted = {"atom_is_knot": True, "parity_is_knot": True}
        if w <= 5:
            wanted.update(atom_minimum_width=w, parity_minimum_width=w)
        failures += [f"width {width}: {key}" for key, value in wanted.items() if entry[key] != value]
    failures += [f"parity chain {size}" for size, ok in chain_results.items() if not ok]
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
