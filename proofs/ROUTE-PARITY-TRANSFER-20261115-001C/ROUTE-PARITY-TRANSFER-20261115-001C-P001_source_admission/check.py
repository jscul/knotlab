"""Replay the admission and the local proof-rule bridge. No network is required."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from external_evidence_admission_schema_model import validate_admission_record

SOURCE_SHA256 = "9f7eb894da07496b4cba14cbf7a4a109d64e994837fc0478be541cc4aaa57306"
TRUE = frozenset({0})  # An integer denotes the affine polynomial in an atom [a=0].


class Cube:
    def __init__(self, n):
        self.n = n
        self.full = (1 << (1 << n)) - 1
        self.atoms = []
        for form in range(2 << n):
            values = [((x & (form >> 1)).bit_count() ^ form) & 1 for x in range(1 << n)]
            self.atoms.append(sum(1 << x for x, value in enumerate(values) if value == 0))

    @lru_cache(maxsize=4096)
    def truth(self, clause):
        answer = 0
        for atom in clause:
            answer |= self.atoms[atom]
        return answer


def echelon(rows):
    """Carry combination witnesses in a basis on affine coefficient vectors."""
    basis = {}
    for i, original in enumerate(rows):
        value, mask = reduce_row(basis, original, 1 << i)
        if value:
            basis[value.bit_length()] = value, mask
    return basis


def reduce_row(basis, value, mask=0):
    while value and value.bit_length() in basis:
        row, witness = basis[value.bit_length()]
        value ^= row
        mask ^= witness
    return value, mask


def compact(clause):
    # The falsifying equations are [atom+1=0]. Span containing 1 certifies inconsistency.
    basis = echelon(atom ^ 1 for atom in sorted(clause))
    if reduce_row(basis, 1)[0] == 0:
        return TRUE
    return frozenset(row ^ 1 for row, _ in basis.values())


class SyntacticProof:
    """Emit only Pang axioms, weakening, linear combination, contraction and deletion."""

    def __init__(self, cube, inputs=()):
        self.cube = cube
        self.inputs = set(inputs)
        self.lines = []
        self.nodes = 0
        self.rules = Counter()
        self.excluded_middle_cache = {}

    def record(self, clause, rule, parents=(), cost=1):
        truth = self.cube.full
        for p in parents:
            truth &= self.cube.truth(self.lines[p])
        if parents or rule != "input":
            assert truth & ~self.cube.truth(clause) == 0, (rule, parents, clause)
        self.nodes += cost
        self.rules[rule] += cost
        self.lines.append(clause)
        return len(self.lines) - 1

    def input(self, clause):
        assert clause in self.inputs
        return self.record(clause, "input")

    def weaken(self, p, target):
        original = self.lines[p]
        assert original <= target, (original, target)
        if target == original:
            return p
        return self.record(target, "syntactic_weakening", (p,), len(target - original))

    def combine(self, p, a, q, b):
        left, right = self.lines[p], self.lines[q]
        assert a in left and b in right
        raw = [*(left - {a}), *(right - {b}), a ^ b]
        result = frozenset(raw)
        contracted = len(raw) - len(result)
        self.nodes += contracted
        self.rules["contraction"] += contracted
        return self.record(result, "linear_combination", (p, q))

    def cut(self, p, q, pivot):
        line = self.combine(p, pivot, q, pivot ^ 1)
        assert 1 in self.lines[line]
        return self.record(self.lines[line] - {1}, "delete_false_constant", (line,))

    def excluded_middle(self, form):
        support = form & ~1
        if support in self.excluded_middle_cache:
            return self.excluded_middle_cache[support]
        coords = [1 << k for k in range(1, self.cube.n + 1) if support & (1 << k)]
        if not coords:
            node = self.weaken(self.record(TRUE, "true_axiom"), frozenset({0, 1}))
        else:
            f = coords[0]
            node = self.record(frozenset({f, f ^ 1}), "boolean_axiom")
            for g in coords[1:]:
                other = self.record(frozenset({g, g ^ 1}), "boolean_axiom")
                h = f ^ g
                excluded = frozenset({h, h ^ 1})
                halves = []
                for i in (0, 1):
                    quarters = []
                    for j in (0, 1):
                        add = self.combine(node, f ^ i, other, g ^ j)
                        clause = excluded | {f ^ i ^ 1, g ^ j ^ 1}
                        quarters.append(self.weaken(add, clause))
                    halves.append(self.cut(*quarters, g ^ 1))
                node = self.cut(*halves, f ^ 1)
                assert self.lines[node] == excluded
                f = h
        self.excluded_middle_cache[support] = node
        return node

    def imply(self, p, target):
        """Primitive syntactic derivation of a short entailed clause."""
        given = self.lines[p]
        if target == TRUE:
            return self.record(TRUE, "true_axiom")
        if given <= target:
            return self.weaken(p, target)
        assert self.cube.truth(target) != self.cube.full
        rows = [atom ^ 1 for atom in sorted(target)]
        basis = echelon(rows)
        for atom in sorted(given - target):
            row = atom ^ 1
            residual, witness = reduce_row(basis, row)
            if residual:
                raise ValueError("invalid semantic weakening")
            selected = [g for k, g in enumerate(rows) if witness & (1 << k)]
            if selected:
                partial = selected[0]
                cond = self.weaken(self.excluded_middle(partial), target | {partial})
                for g in selected[1:]:
                    summand = self.weaken(self.excluded_middle(g), target | {g})
                    cond = self.combine(cond, partial, summand, g)
                    partial ^= g
                    cond = self.weaken(cond, target | {partial})
                assert partial == row
            else:
                cond = self.weaken(self.record(TRUE, "true_axiom"), target | {0})
            p = self.cut(p, cond, atom)
        return self.weaken(p, target)

    def semantic_cut(self, left, right, pivot, goal):
        if goal == TRUE:
            return self.record(TRUE, "true_axiom"), "tautological_goal"
        false_goal = self.cube.full ^ self.cube.truth(goal)
        if (false_goal & self.cube.atoms[pivot]) == 0:
            return self.imply(left, goal), "pivot_false_on_goal_falsifiers"
        if (false_goal & self.cube.atoms[pivot ^ 1]) == 0:
            return self.imply(right, goal), "pivot_true_on_goal_falsifiers"
        a = self.imply(left, goal | {pivot})
        b = self.imply(right, goal | {pivot ^ 1})
        return self.weaken(self.cut(a, b, pivot), goal), "pivot_takes_both_values"


def all_flats(cube):
    flats = {cube.full: frozenset()}
    for atom, truth in enumerate(cube.atoms):
        for false_space, clause in tuple(flats.items()):
            smaller = false_space & ~truth
            if smaller not in flats:
                flats[smaller] = compact(clause | {atom})
    return flats


def test_small_cubes():
    result = {}
    for n in (1, 2, 3):
        cube = Cube(n)
        flats = all_flats(cube)
        for mask, clause in flats.items():
            assert cube.full ^ cube.truth(clause) == mask and (clause == TRUE or len(clause) <= n)
        checked, max_cost = 0, 0
        for source_false, source in flats.items():
            for target_false, target in flats.items():
                if target_false & ~source_false:
                    continue
                test = SyntacticProof(cube, [source])
                node = test.imply(test.input(source), target)
                assert test.lines[node] == target
                checked += 1
                max_cost = max(max_cost, test.nodes)
        result[str(n)] = {"affine_falsifying_sets": len(flats), "all_valid_unary_implications": checked,
                          "max_observed_nodes": max_cost}
    return result


def test_raw_and_cuts():
    cube = Cube(3)
    taut_count = 0
    for mask in range(1 << len(cube.atoms)):
        clause = frozenset(i for i in range(len(cube.atoms)) if mask & (1 << i))
        reduced = compact(clause)
        assert cube.truth(clause) == cube.truth(reduced)
        assert reduced == TRUE or len(reduced) <= cube.n
        taut_count += reduced == TRUE
    # All two-variable pairs of contexts, all affine pivots including constants.
    cube2 = Cube(2)
    flats = list(all_flats(cube2).values())
    branches = Counter()
    for a, b, f in product(flats, flats, range(len(cube2.atoms))):
        parents = [compact(a | {f}), compact(b | {f ^ 1})]
        goal = compact(a | b)
        test = SyntacticProof(cube2, parents)
        out, branch = test.semantic_cut(*map(test.input, parents), f, goal)
        assert test.lines[out] == goal
        branches[branch] += 1
    return {"raw_three_variable_clauses": 1 << len(cube.atoms), "semantically_true": taut_count,
            "two_variable_cut_cases": sum(branches.values()), "cut_cases_by_branch": dict(branches)}


def test_larger():
    cube = Cube(5)
    x = [1 << i for i in range(1, 6)]
    five = sum(x)
    target = frozenset(x)
    # False(target) is all ones, where the sum of all five coordinates equals 1.
    source = frozenset({five})
    test = SyntacticProof(cube, [source])
    witness = test.imply(test.input(source), target)
    assert test.lines[witness] == target
    row_sum_nodes = test.nodes
    assert compact(frozenset({x[0], x[1], x[0] ^ x[1]})) == TRUE
    try:
        test.imply(test.input(source), frozenset({x[0]}))
    except ValueError:
        rejected = True
    else:
        raise AssertionError("a genuinely invalid weakening passed")
    excluded = SyntacticProof(cube)
    node = excluded.excluded_middle(five)
    assert excluded.lines[node] == frozenset({five, five ^ 1})
    flat_count = len(all_flats(cube))
    assert flat_count == 2452
    return {"five_variable_affine_falsifying_sets": flat_count,
            "five_coordinate_row_sum_nodes": row_sum_nodes,
            "five_coordinate_excluded_middle_nodes": excluded.nodes,
            "wrong_target_rejected": rejected}


def test_complete_proof():
    cube = Cube(3)
    levels = [frozenset((2 << i) ^ sign for i, sign in enumerate(signs))
              for signs in product((0, 1), repeat=3)]
    test = SyntacticProof(cube, levels)
    frontier = [test.input(clause) for clause in levels]
    for pivot in (8, 4, 2):
        following = []
        for left, right in zip(frontier[::2], frontier[1::2]):
            goal = compact((test.lines[left] - {pivot}) | (test.lines[right] - {pivot ^ 1}))
            result, _ = test.semantic_cut(left, right, pivot, goal)
            following.append(result)
        frontier = following
    assert len(frontier) == 1 and test.lines[frontier[0]] == frozenset()
    return {"initial_strict_clauses": 8, "semantic_dag_nodes": 15, "syntactic_nodes": test.nodes,
            "syntactic_rule_counts": dict(sorted(test.rules.items()))}


def test_sample_law():
    answer = {}
    for n in range(3, 8):
        cube = Cube(n)
        clauses = [frozenset((2 << v) ^ sign for v, sign in zip(variables, signs))
                   for variables in combinations(range(n), 3) for signs in product((0, 1), repeat=3)]
        assert len(set(clauses)) == 8 * comb(n, 3)
        counts = [sum((cube.truth(c) >> x) & 1 for c in clauses) for x in range(1 << n)]
        assert set(counts) == {7 * comb(n, 3)}
        answer[str(n)] = {"clauses": len(clauses), "assignments": len(counts)}
    base = 2 * Fraction(7, 8) ** 8
    assert 0 < base < 1
    return {"uniform_populations": answer, "first_moment_base_at_density_eight": str(base)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, help="verify a downloaded copy of the exact primary PDF")
    args = parser.parse_args()
    if args.source_pdf and hashlib.sha256(args.source_pdf.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("source digest mismatch")
    record = json.loads((HERE / "admission.json").read_text())
    schema = json.loads((ROOT / "schemas/external_evidence_admission.schema.json").read_text())
    verdict = validate_admission_record(ROOT, schema, record)
    assert verdict.accepted, verdict.errors
    assert {Path(path).parts[1] for path in record["local_dependencies"]} == {
        "EVIDENCE-001A", "COMPRESSION-ROBUST-PROOF-COMPLEXITY-001HDW"}
    assert len(record) == 22 and not any(record["contact_first_safe_conclusions"].values())
    assert SOURCE_SHA256 in (HERE / "proof.md").read_text()
    results = {"status": "passed", "admission": {"accepted": verdict.accepted, "fields": len(record),
                             "proved_local_parents": verdict.checked_local_dependencies,
                             "primary_pdf_sha256": SOURCE_SHA256},
               "sampling": test_sample_law(), "small_cubes": test_small_cubes(),
               "rule_cases": test_raw_and_cuts(), "larger_control": test_larger(),
               "whole_refutation": test_complete_proof()}
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

