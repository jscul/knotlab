#!/usr/bin/env python3
"""Check KNOT-COMPETITION-20261019-001A-P001: which knots competing rules on pairs can make.

Re-derives every finite claim with its own enumeration, independently of
tools/knotlab and of the Lean source. Whether a relation is the least set of a
pairwise function is decided exactly: a function on the cube is pairwise when
its Moebius coefficients on three or more coordinates vanish, and the question
becomes a small linear feasibility problem, solved by Fourier-Motzkin
elimination over the rationals. The checker also compiles the Lean kernel with
a pinned toolchain, confirms it uses only the standard axioms, and runs each
check once on a deliberately wrong input to show that it can fail.

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
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAN = ["lean", "+leanprover/lean4:v4.32.2"]
KERNEL = HERE / "CompetitionKernel.lean"
KERNEL_THEOREMS = (
    "slice_vanishes", "opposite_in_slice", "no_knot_on_four_distinct", "no_knot_beyond_three",
    "cube_cover", "knot_is_nae", "frustrated_least", "nae_is_knot", "three_variable_classification",
    "strict_pairwise_no_knot", "competition_pairwise_no_knot", "readings_agree_when_satisfiable",
    "gadget_bound", "gadget_best", "gadget_projection", "every_relation_by_gadgets",
    "frustrated_triangle", "triangles_knot_iff_frustrated", "weighted_triangle_not_knot",
)
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

Point = tuple[int, ...]


def cube(m: int) -> list[Point]:
    return list(product((0, 1), repeat=m))


def full(points: set[Point], m: int) -> bool:
    return len(points) == 2 ** m


def is_knot(allowed: frozenset[Point], m: int) -> bool:
    """Forgetting reading: constrained, and forgetting any one coordinate frees the rest."""
    if full(set(allowed), m) or not allowed:
        return False
    return all(
        full({x[:i] + x[i + 1:] for x in allowed}, m - 1)
        for i in range(m)
    )


def knots(m: int) -> list[frozenset[Point]]:
    points = cube(m)
    out = []
    for mask in range(1, 2 ** len(points)):
        allowed = frozenset(p for k, p in enumerate(points) if mask >> k & 1)
        if is_knot(allowed, m):
            out.append(allowed)
    return out


def knots_on_four() -> list[frozenset[Point]]:
    """Knots on four variables, generated from their excluded sets and then verified by definition."""
    points = cube(4)
    found = []

    def grow(start: int, chosen: list[Point]) -> None:
        if chosen:
            found.append(frozenset(p for p in points if p not in chosen))
        for k in range(start, len(points)):
            if all(sum(a != b for a, b in zip(points[k], c)) > 1 for c in chosen):
                grow(k + 1, chosen + [points[k]])

    grow(0, [])
    return found


# Exact feasibility of "least set of a pairwise function".

def moebius_rows(m: int, excluded: list[Point], degree_from: int) -> list[list[Fraction]]:
    """Rows of the linear conditions 'Moebius coefficient on S is zero' for |S| >= degree_from.

    With E = 0 on the allowed points, the coefficient on S is the signed sum of
    E over excluded points whose support lies inside S.
    """
    rows = []
    for size in range(degree_from, m + 1):
        for S in combinations(range(m), size):
            row = []
            for x in excluded:
                support = [i for i in range(m) if x[i]]
                if set(support) <= set(S):
                    row.append(Fraction((-1) ** (size - len(support))))
                else:
                    row.append(Fraction(0))
            if any(row):
                rows.append(row)
    return rows


def feasible(equalities: list[list[Fraction]], count: int) -> bool:
    """Is there v with v_k >= 1 for all k and every equality row . v = 0?"""
    # Inequalities a . v >= b, stored as (a, b).
    inequalities = [([Fraction(int(j == k)) for j in range(count)], Fraction(1)) for k in range(count)]
    equalities = [row[:] for row in equalities]
    alive = list(range(count))
    while equalities:
        row = equalities.pop()
        pivot = next((k for k in alive if row[k] != 0), None)
        if pivot is None:
            continue  # 0 = 0
        # v_pivot = -(sum_{k != pivot} row_k v_k) / row_pivot
        def substitute(a: list[Fraction]) -> list[Fraction]:
            if a[pivot] == 0:
                return a
            factor = a[pivot] / row[pivot]
            return [a[k] - factor * row[k] if k != pivot else Fraction(0) for k in range(count)]
        equalities = [substitute(e) for e in equalities]
        inequalities = [(substitute(a), b) for a, b in inequalities]
        alive.remove(pivot)
    for k in list(alive):
        positive = [(a, b) for a, b in inequalities if a[k] > 0]
        negative = [(a, b) for a, b in inequalities if a[k] < 0]
        rest = [(a, b) for a, b in inequalities if a[k] == 0]
        combined = set()
        for ap, bp in positive:
            for an, bn in negative:
                sp, sn = -an[k], ap[k]
                a = tuple(sp * ap[j] + sn * an[j] for j in range(count))
                b = sp * bp + sn * bn
                combined.add((a, b))
        inequalities = rest + [(list(a), b) for a, b in combined]
        seen = set()
        unique = []
        for a, b in inequalities:
            key = (tuple(a), b)
            if key not in seen:
                seen.add(key)
                unique.append((a, b))
        inequalities = unique
    return all(b <= 0 for _, b in inequalities)


def is_least_set(allowed: frozenset[Point], m: int, degree_from: int = 3) -> bool:
    excluded = [x for x in cube(m) if x not in allowed]
    if not excluded:
        return True
    return feasible(moebius_rows(m, excluded, degree_from), len(excluded))


def opposite_pair(allowed: frozenset[Point], m: int) -> bool:
    excluded = [x for x in cube(m) if x not in allowed]
    return len(excluded) == 2 and all(a != b for a, b in zip(*excluded))


# Rules and their two readings.

def broken(rules: list[tuple[int, int, frozenset[tuple[int, int]]]], x: Point, weights=None) -> int:
    weights = weights or [1] * len(rules)
    return sum(w for (i, j, ok), w in zip(rules, weights) if (x[i], x[j]) not in ok)


def strict(rules, m: int) -> frozenset[Point]:
    return frozenset(x for x in cube(m) if broken(rules, x) == 0)


def competition(rules, m: int, weights=None) -> frozenset[Point]:
    counts = {x: broken(rules, x, weights) for x in cube(m)}
    low = min(counts.values())
    return frozenset(x for x, c in counts.items() if c == low)


AGREE = frozenset({(0, 0), (1, 1)})
DIFFER = frozenset({(0, 1), (1, 0)})


def triangle(differ: tuple[bool, bool, bool]):
    return [(i, j, DIFFER if d else AGREE) for (i, j), d in zip(((0, 1), (0, 2), (1, 2)), differ)]


def gadget_projection(allowed: frozenset[Point], drop: int | None = None) -> frozenset[Point]:
    """Least states of ten 2-clauses per excluded point, with hidden variables forgotten."""
    excluded = [x for x in cube(3) if x not in allowed]
    best, keep = None, set()
    for x in cube(3):
        for hidden in product((0, 1), repeat=len(excluded)):
            score = 0
            for b, w in zip(excluded, hidden):
                l0, l1, l2 = (x[0] != b[0]), (x[1] != b[1]), (x[2] != b[2])
                clauses = [l0, l1, l2, bool(w), not (l0 and l1), not (l1 and l2), not (l0 and l2),
                           l0 or not w, l1 or not w, l2 or not w]
                if drop is not None:
                    clauses.pop(drop)
                score += sum(not c for c in clauses)
            if best is None or score < best:
                best, keep = score, {x}
            elif score == best:
                keep.add(x)
    return frozenset(keep)


def random_rules(generator: random.Random, m: int) -> list:
    rules = []
    for _ in range(generator.randint(1, 2 * m)):
        i, j = generator.sample(range(m), 2)
        if generator.random() < 0.5:
            ok = generator.choice((AGREE, DIFFER))
        else:
            ok = frozenset(p for p in product((0, 1), repeat=2) if generator.random() < 0.6)
        rules.append((i, j, ok))
    return rules


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

    # (i) Three variables.
    three = knots(3)
    least3 = [k for k in three if is_least_set(k, 3)]
    checks["three_variable_knots"] = len(three)
    checks["three_variable_least_set_knots"] = len(least3)
    checks["least_set_knots_are_opposite_pairs"] = (
        {k for k in least3} == {k for k in three if opposite_pair(k, 3)})
    controls["cubic_terms_allowed_make_every_knot_a_least_set"] = all(
        is_least_set(k, 3, degree_from=4) for k in three)

    # (ii) Four variables: every knot, exactly.
    four = knots_on_four()
    checks["four_variable_knots"] = len(four)
    checks["four_variable_knots_verified"] = all(is_knot(k, 4) for k in four)
    checks["four_variable_least_set_knots"] = sum(is_least_set(k, 4) for k in four)
    clause = frozenset(x for x in cube(4) if x[0] or x[1])
    controls["pairwise_clause_on_four_is_a_least_set"] = is_least_set(clause, 4)
    controls["cubic_terms_allowed_on_four_admit_a_knot"] = any(
        is_least_set(k, 4, degree_from=4) for k in four)

    # (iii) Hidden variables: every knot through gadgets.
    checks["knots_made_by_gadgets"] = sum(gadget_projection(k) == k for k in three)
    controls["gadget_without_the_unit_clause_on_w_fails"] = any(
        gadget_projection(k, drop=3) != k for k in three)

    # (iv) Readings, and the strict reading never allows a knot.
    generator = random.Random(20261019)
    agree = differ = frustrated_seen = 0
    competition_knots = {3: [], 4: [], 5: []}
    strict_knots = 0
    for m in (3, 4, 5):
        for _ in range(600):
            rules = random_rules(generator, m)
            s, c = strict(rules, m), competition(rules, m)
            if s:
                agree += s == c
                differ += s != c
                strict_knots += is_knot(s, m)
            else:
                frustrated_seen += 1
            if is_knot(c, m):
                competition_knots[m].append(c)
    checks["satisfiable_systems_where_readings_agree"] = differ == 0 and agree > 0
    checks["frustrated_systems_sampled"] = frustrated_seen
    checks["strict_knots"] = strict_knots
    checks["competition_knots_on_three_are_opposite_pairs"] = all(
        opposite_pair(k, 3) for k in competition_knots[3]) and len(competition_knots[3]) > 0
    checks["competition_knots_on_four_or_five"] = len(competition_knots[4]) + len(competition_knots[5])
    pair_determined = [
        r for mask in range(1, 256)
        for r in [frozenset(p for k, p in enumerate(cube(3)) if mask >> k & 1)]
        if r == frozenset(x for x in cube(3) if all(
            (x[i], x[j]) in {(y[i], y[j]) for y in r} for i, j in combinations(range(3), 2)))
    ]
    checks["strict_pairwise_relations_on_three"] = len(pair_determined)
    checks["strict_pairwise_relations_that_are_knots"] = sum(is_knot(r, 3) for r in pair_determined)

    # Triangles and weights.
    by_sign = {}
    for signs in product((False, True), repeat=3):
        rules = triangle(signs)
        by_sign[signs] = (not strict(rules, 3), is_knot(competition(rules, 3), 3))
    checks["triangle_knot_iff_frustrated"] = all(
        knot == (sum(signs) % 2 == 1) and empty == (sum(signs) % 2 == 1)
        for signs, (empty, knot) in by_sign.items())
    nae = competition(triangle((True, True, True)), 3)
    checks["all_differ_triangle_least_set_size"] = len(nae)
    checks["weighted_triangle_is_knot"] = is_knot(
        competition(triangle((True, True, True)), 3, weights=[2, 1, 1]), 3)
    controls["even_frustration_rule_rejected"] = not all(
        knot == (sum(signs) % 2 == 0) for signs, (_, knot) in by_sign.items())
    hub = frozenset(x for x in cube(3) if (not x[0] or x[2]) and (not x[1] or x[2]))
    controls["knot_test_rejects_hub"] = not is_knot(hub, 3)

    # Lean kernel: compiles, standard axioms only, mutations rejected.
    source = KERNEL.read_text()
    compiled = subprocess.run([*LEAN, str(KERNEL)], capture_output=True, text=True, check=False)
    probe = lean(source + "".join(f"\n#print axioms CompetitionKernel.{name}" for name in KERNEL_THEOREMS))
    used: set[str] = set()
    for line in probe.stdout.splitlines():
        match = re.search(r"depends on axioms: \[(.*)\]", line)
        if match:
            used |= {name.strip() for name in match.group(1).split(",")}
    three_ok = source.replace("theorem no_knot_beyond_three {m : Nat} (hm : 4 ≤ m)",
                              "theorem no_knot_beyond_three {m : Nat} (hm : 3 ≤ m)")
    sign_flip = source.replace("E x - E (toggle x i) - E (toggle x j) - E (toggle x k)",
                               "E x + E (toggle x i) - E (toggle x j) - E (toggle x k)")
    checks["lean_version"] = subprocess.run(
        [*LEAN, "--version"], capture_output=True, text=True, check=False).stdout.strip()
    checks["lean_kernel_accepted"] = compiled.returncode == 0 and not compiled.stdout.strip()
    checks["lean_theorems_present"] = all(
        re.search(rf"theorem {name}\b", source) is not None for name in KERNEL_THEOREMS)
    checks["lean_axioms"] = sorted(used)
    checks["lean_axioms_standard_only"] = probe.returncode == 0 and used <= ALLOWED_AXIOMS
    checks["lean_source_free_of_escapes"] = not any(
        token in source for token in ("sorry", "admit", "axiom ", "native_decide"))
    controls["lean_rejects_three_variable_version"] = (
        three_ok != source and lean(three_ok).returncode != 0)
    controls["lean_rejects_sign_flip_in_slice"] = (
        sign_flip != source and lean(sign_flip).returncode != 0)

    manifest = json.loads((HERE / "manifest.json").read_text())
    checks["parents_bound"] = all(
        sha256(ROOT / path) == digest for path, digest in manifest["parent_bindings"].items())

    expected = {
        "three_variable_knots": 34,
        "three_variable_least_set_knots": 4,
        "least_set_knots_are_opposite_pairs": True,
        "four_variable_knots": 742,
        "four_variable_knots_verified": True,
        "four_variable_least_set_knots": 0,
        "knots_made_by_gadgets": 34,
        "satisfiable_systems_where_readings_agree": True,
        "strict_knots": 0,
        "competition_knots_on_three_are_opposite_pairs": True,
        "competition_knots_on_four_or_five": 0,
        "strict_pairwise_relations_that_are_knots": 0,
        "triangle_knot_iff_frustrated": True,
        "all_differ_triangle_least_set_size": 6,
        "weighted_triangle_is_knot": False,
        "lean_kernel_accepted": True,
        "lean_theorems_present": True,
        "lean_axioms_standard_only": True,
        "lean_source_free_of_escapes": True,
        "parents_bound": True,
    }
    failures = [name for name, value in expected.items() if checks.get(name) != value]
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
