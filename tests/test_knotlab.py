"""Invariants of the bound-loop knot formalization (INTUITIONS.md)."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab import (
    GuardedSystem,
    Relation,
    Rule,
    add_by_forced_world,
    atom,
    check_knot,
    choices_reaching,
    dual_rail_adder,
    dual_rail_gate,
    essential,
    existence_profile,
    forced_world,
    from_atoms_and_distinctions,
    gate_relation,
    implication_loop,
    knot_relation,
    knot_tree,
    leak_report,
    loop_report,
    minimal_worlds,
    signature,
    signed_loop,
    thread,
    witness_chain,
)
from knotlab.examples import examples, guarded_examples
from knotlab.space import bonds, complex_relation, compose, free_sets, homology, smallest_bond, ties
from knotlab.choice import is_or_closed, negate, open_variables, two_loop_knots, worlds_given
from knotlab.rings import bits, memory, network, predicted_excluded, ring
from knotlab.depth import charge_depth, cubic, cutwidth, scope_hole_rank, toggle_width
from knotlab.holonomy import (
    allowed,
    allowed_fraction,
    basic_relaxation_accepts,
    knot_among_loops,
    nerve,
    orbit_sizes,
    selector_relation,
    star,
)
from knotlab.competition import (
    allowed_states,
    least_set_knot,
    separation_levels,
    triangle,
    triangle_strip,
)
from knotlab.patterns import (
    co_information,
    controls,
    emergent_information,
    entwines,
    fewest_states_hiding_pairs,
    hides_from_parts,
    information,
    least_violation,
    parity,
    parity_chain,
    three_variable_shapes,
)
from knotlab.presence import (
    CONTACTS,
    TwoLoops,
    conserved,
    copy_ring,
    frozen_states,
    inverter_ring,
    reader_is_exact,
)

ABC = ("A", "B", "c")
CUBE = list(product((False, True), repeat=3))


def all_relations_on_three() -> list[Relation]:
    return [
        Relation(ABC, frozenset(row for index, row in enumerate(CUBE) if mask >> index & 1))
        for mask in range(256)
    ]


class AtomTest(unittest.TestCase):
    def test_two_loop_knots_are_the_patterns_hidden_from_their_pairs(self) -> None:
        knots = [r for r in all_relations_on_three() if check_knot(r, ("A", "B"), "c").is_knot]
        self.assertEqual(len(knots), 34)
        self.assertTrue(all(hides_from_parts(r) for r in knots))
        self.assertIn(knot_relation(("A", "B"), "c"), knots)
        self.assertIn(parity(("A", "B", "c"), False), [Relation(r.variables, r.rows) for r in knots])

    def test_under_the_absence_reading_only_the_atom_is_a_knot(self) -> None:
        knots = [r for r in all_relations_on_three()
                 if check_knot(r, ("A", "B"), "c", erasure="absence").is_knot]
        self.assertEqual(
            {tuple(r.excluded()) for r in knots},
            {((True, True, False),), ((True, True, True),)},
        )

    def test_the_knot_is_invisible_in_every_pair(self) -> None:
        knot = knot_relation(("A", "B"), "c")
        for pair in (("A", "B"), ("A", "c"), ("B", "c")):
            self.assertTrue(knot.project(pair).is_full())
        self.assertTrue(check_knot(knot, ("A", "B"), "c").invisible_in_parts)

    def test_no_pairwise_relation_is_a_knot(self) -> None:
        for relation in all_relations_on_three():
            self.assertEqual(relation.is_majority_closed(), relation.is_pairwise_determined())
            if relation.is_majority_closed():
                self.assertFalse(check_knot(relation, ("A", "B"), "c").is_knot)


class PairwiseTest(unittest.TestCase):
    def test_two_cnf_with_witnesses_stays_pairwise(self) -> None:
        generator = random.Random(20261019)
        for _ in range(400):
            witnesses = tuple(f"w{i}" for i in range(generator.randint(0, 3)))
            names = ABC + witnesses
            clauses = []
            for _ in range(generator.randint(1, 8)):
                chosen = generator.sample(names, generator.choice((1, 2)))
                clauses.append(tuple((name, generator.random() < 0.5) for name in chosen))
            relation = Relation.from_cnf(clauses, ABC, witnesses)
            self.assertTrue(relation.is_pairwise_determined())
            self.assertFalse(check_knot(relation, ("A", "B"), "c").is_knot)


class ThresholdTest(unittest.TestCase):
    def test_width_three_with_witnesses_binds_any_number_of_loops(self) -> None:
        for size in range(2, 6):
            loops = tuple(f"L{i}" for i in range(1, size + 1))
            clauses, witnesses = witness_chain(loops, "c")
            self.assertTrue(all(len({name for name, _ in clause}) == 3 for clause in clauses))
            built = Relation.from_cnf(clauses, loops + ("c",), witnesses)
            target = knot_relation(loops, "c")
            self.assertTrue(built.equivalent(target))
            self.assertTrue(check_knot(built, loops, "c").is_knot)
            self.assertFalse(target.is_majority_closed())
            self.assertEqual(target.minimum_width(), size + 1)
            self.assertEqual(len(witnesses), size - 2)


class CaseTest(unittest.TestCase):
    def test_reference_cases_have_their_expected_verdicts(self) -> None:
        for example in examples():
            report = check_knot(example.relation, example.loops, example.contact)
            self.assertEqual(report.is_knot, example.expected_knot, example.name)
            absence = check_knot(example.relation, example.loops, example.contact, erasure="absence")
            self.assertEqual(absence.is_knot, example.expected_under_absence, example.name)

    def test_presentation_does_not_change_the_verdict(self) -> None:
        plain = Relation.from_cnf(["-A -B c"], ABC)
        reordered = Relation.from_cnf(["c -B -A", "A -A B"], ABC)
        through_witnesses = Relation.from_cnf(["w -A -B", "-w c x", "-w c -x"], ABC, ("w", "x"))
        reports = [check_knot(r, ("A", "B"), "c") for r in (plain, reordered, through_witnesses)]
        self.assertEqual({report.as_dict()["is_knot"] for report in reports}, {True})
        self.assertTrue(plain.equivalent(reordered) and plain.equivalent(through_witnesses))

    def test_other_variables_must_be_declared_as_witnesses(self) -> None:
        relation = Relation.from_cnf(["w -A -B", "-w c"], ("A", "B", "c", "w"))
        with self.assertRaises(ValueError):
            check_knot(relation, ("A", "B"), "c")


class LoopTest(unittest.TestCase):
    def test_implication_loops_collapse_to_one_bit(self) -> None:
        for size in range(2, 7):
            report = loop_report(implication_loop([f"x{i}" for i in range(size)]))
            self.assertEqual((report.states, report.free_bits, report.collapsed), (2, 1.0, True))

    def test_equal_unequal_loops_collapse_or_contradict(self) -> None:
        names = ("x1", "x2", "x3", "x4")
        for steps in product((False, True), repeat=4):
            report = loop_report(signed_loop(names, steps))
            if sum(steps) % 2:
                self.assertTrue(report.contradictory)
            else:
                self.assertEqual((report.states, report.collapsed), (2, True))

    def test_signature_reads_the_interior_from_outside(self) -> None:
        loop = signed_loop(("x1", "x2", "x3", "x4"), (False, True, True, False))
        self.assertEqual(signature(loop, "x1", "x2"), frozenset({"equal"}))
        self.assertEqual(signature(loop, "x1", "x3"), frozenset({"unequal"}))


class LeakTest(unittest.TestCase):
    def test_role_gating_supplies_the_missing_literal(self) -> None:
        systems = guarded_examples()
        cross = leak_report(systems["cross-wired 2-clause guards"])
        self.assertFalse(cross.relational.is_knot)
        self.assertTrue(cross.gated.is_knot)
        self.assertTrue(cross.leaks)
        honest = leak_report(systems["knot clause as both guards"])
        self.assertTrue(honest.relational.is_knot and honest.gated.is_knot)
        self.assertFalse(honest.leaks)

    def test_gating_changes_nothing_when_guards_name_their_loop(self) -> None:
        system = GuardedSystem(("A", "B"), "c", {"A": ("-A c",), "B": ("-B c",)})
        self.assertFalse(leak_report(system).leaks)


def gate_from_table(table: int):
    return lambda x, y: bool(table >> (2 * x + y) & 1)


class WorldTest(unittest.TestCase):
    def test_the_contact_exists_exactly_when_both_loops_do(self) -> None:
        def existing(rules: list[Rule]) -> set[frozenset[str]]:
            return {chosen for chosen, exists in existence_profile(rules, "AB", "c").items() if exists}

        self.assertEqual(existing([atom("A", "B", "c")]), {frozenset("AB")})
        hub = [Rule(frozenset("A"), "c"), Rule(frozenset("B"), "c")]
        self.assertEqual(existing(hub), {frozenset("A"), frozenset("B"), frozenset("AB")})

    def test_the_forced_world_is_the_least_world(self) -> None:
        generator = random.Random(20261019)
        names = list("ABCDEFG")
        for _ in range(300):
            rules = []
            for _ in range(generator.randint(1, 8)):
                premises = frozenset(generator.sample(names, generator.choice((0, 1, 2))))
                result = generator.choice([name for name in names if name not in premises])
                rules.append(Rule(premises, result))
            present = generator.sample(names, generator.randint(0, 3))
            worlds = [
                world
                for row in product((False, True), repeat=len(names))
                for world in [frozenset(name for name, value in zip(names, row) if value)]
                if set(present) <= world
                and all(not rule.premises <= world or rule.result in world for rule in rules)
            ]
            least = frozenset.intersection(*worlds)
            self.assertIn(least, worlds)
            self.assertEqual(forced_world(rules, present), least)

    def test_choice_leaves_several_minimal_worlds(self) -> None:
        bound = Relation.from_cnf(["-A -B c"], ABC).restrict({"A": True, "B": True})
        self.assertEqual(minimal_worlds(bound), [frozenset({"c"})])
        choice = Relation.from_cnf(["-c A B"], ABC).restrict({"c": True})
        self.assertEqual(minimal_worlds(choice), [frozenset({"A"}), frozenset({"B"})])


class BuildingTest(unittest.TestCase):
    def test_a_tree_of_atoms_is_a_knot_of_all_its_loops(self) -> None:
        for depth in (1, 2, 3):
            rules, loops = knot_tree(depth)
            clauses = [tuple((premise, False) for premise in sorted(rule.premises))
                       + ((rule.result, True),) for rule in rules]
            witnesses = sorted({rule.result for rule in rules} - {"c"})
            relation = Relation.from_cnf(clauses, [*loops, "c"], witnesses)
            self.assertTrue(relation.equivalent(knot_relation(tuple(loops), "c")))

    def test_every_loop_of_a_tree_is_essential_and_redundancy_is_not(self) -> None:
        rules, loops = knot_tree(6)
        self.assertEqual(essential(rules, loops, "c"), frozenset(loops))
        redundant = [atom("A", "B", "c"), atom("C", "D", "c")]
        self.assertEqual(essential(redundant, "ABCD", "c"), frozenset())

    def test_everything_in_a_thread_rests_on_finitely_many_loops(self) -> None:
        rules, loops = thread(60)
        for k in (1, 7, 30, 60):
            self.assertEqual(essential(rules, loops, f"w{k}"), frozenset(loops[: k + 1]))


class DistinctionTest(unittest.TestCase):
    def test_atoms_and_pins_define_only_requirements(self) -> None:
        generator = random.Random(20261019)
        names = ("A", "B", "C", "w1", "w2", "w3")
        for _ in range(200):
            clauses = [tuple(zip(generator.sample(names, 3), (False, False, True)))
                       for _ in range(generator.randint(1, 7))]
            clauses += [((generator.choice(names), generator.random() < 0.5),)
                        for _ in range(generator.randint(0, 2))]
            self.assertTrue(Relation.from_cnf(clauses, names[:3], names[3:]).is_and_closed())

    def test_atoms_and_distinctions_define_every_three_place_relation(self) -> None:
        for relation in all_relations_on_three():
            self.assertEqual(from_atoms_and_distinctions(relation).rows, relation.rows)

    def test_a_gate_is_pairwise_exactly_when_it_ignores_an_input(self) -> None:
        for table in range(16):
            gate = gate_from_table(table)
            uses_both = any(gate(False, y) != gate(True, y) for y in (False, True)) and any(
                gate(x, False) != gate(x, True) for x in (False, True))
            self.assertEqual(gate_relation(gate).is_majority_closed(), not uses_both)

    def test_and_is_its_two_place_parts_plus_the_atom(self) -> None:
        and_gate = gate_relation(lambda x, y: x and y)
        two_place = [clause for clause in and_gate.implied_clauses(2) if len(clause) == 2]
        self.assertNotEqual(Relation.from_cnf(two_place, ("x", "y", "z")).rows, and_gate.rows)
        self.assertEqual(
            Relation.from_cnf(two_place + ["-x -y z"], ("x", "y", "z")).rows, and_gate.rows)

    def test_a_group_table_is_invisible_in_every_pair(self) -> None:
        elements = list(permutations(range(3)))
        table = {(p, q, tuple(p[q[i]] for i in range(3))) for p in elements for q in elements}
        self.assertEqual(len(table), 36)
        for i, j in combinations(range(3), 2):
            self.assertEqual(len({(triple[i], triple[j]) for triple in table}), 36)


class ComputationTest(unittest.TestCase):
    def test_addition_is_a_forced_world(self) -> None:
        for first in range(16):
            for second in range(16):
                self.assertEqual(add_by_forced_world(first, second, 4), first + second)

    def test_every_circuit_is_a_forced_world(self) -> None:
        generator = random.Random(20261019)
        inputs = ("i0", "i1", "i2")
        for _ in range(100):
            wires, gates = list(inputs), []
            for index in range(8):
                first, second = generator.sample(wires, 2)
                gates.append((first, second, f"g{index}", gate_from_table(generator.randrange(16))))
                wires.append(f"g{index}")
            rules = [rule for gate in gates for rule in dual_rail_gate(*gate)]
            for bits in product((False, True), repeat=len(inputs)):
                value = dict(zip(inputs, bits))
                for first, second, output, function in gates:
                    value[output] = function(value[first], value[second])
                world = forced_world(rules, [f"{name}={int(value[name])}" for name in inputs])
                for wire, bit in value.items():
                    self.assertIn(f"{wire}={int(bit)}", world)
                    self.assertNotIn(f"{wire}={int(not bit)}", world)

    def test_running_the_adder_backward_needs_choice(self) -> None:
        open_bits = [(f"{x}{i}=0", f"{x}{i}=1") for x in "ab" for i in range(3)]
        target = ["s0=1", "s1=0", "s2=1", "carry3=0"]
        ways = choices_reaching(dual_rail_adder(3), open_bits, target, given=["carry0=0"])
        pairs = {tuple(sum(1 << i for i in range(3) if f"{x}{i}=1" in way) for x in "ab")
                 for way in ways}
        self.assertEqual(pairs, {(a, 5 - a) for a in range(6)})


class PresenceTest(unittest.TestCase):
    def test_a_static_loop_is_one_free_bit(self) -> None:
        cycle = Relation.from_cnf(["-A -X B", "-B -Y A"], ("A", "B", "X", "Y"))
        self.assertEqual(cycle.restrict({"X": True, "Y": True}).table(), ["00", "11"])
        self.assertEqual(len(cycle.restrict({"X": False, "Y": True}).rows), 3)
        contradictory = signed_loop(("x1", "x2", "x3"), (True, False, False))
        bound = Relation.from_cnf(["-a -b c"], ("a", "b", "c"))
        self.assertTrue(contradictory.is_empty())
        self.assertFalse(bound.is_empty())

    def test_running_is_conserved_and_read_by_neighbors(self) -> None:
        for size in range(2, 8):
            self.assertTrue(conserved(copy_ring, size))
            self.assertTrue(reader_is_exact(size))
            self.assertEqual(len(frozen_states(copy_ring, size)), 2)
            self.assertTrue(conserved(inverter_ring, size))
            self.assertEqual(len(frozen_states(inverter_ring, size)), 0 if size % 2 else 2)

    def test_the_latch_is_the_knot_over_computed_presence(self) -> None:
        for size_a, size_b in ((2, 2), (2, 3), (3, 3), (2, 4), (3, 4)):
            system = TwoLoops(size_a, size_b, "latch")
            self.assertTrue(system.relation().equivalent(knot_relation(("A", "B"), "c")))
            self.assertTrue(system.erasure_leaves_contact_free())

    def test_other_contact_rules_fail(self) -> None:
        for size_a, size_b in ((2, 2), (2, 3), (3, 3), (3, 4)):
            for contact in ("driven", "hub"):
                report = check_knot(TwoLoops(size_a, size_b, contact).relation(), ("A", "B"), "c",
                                    erasure="absence")
                self.assertFalse(report.loss_on_erasure, (contact, size_a, size_b))
            single = TwoLoops(size_a, size_b, "single point")
            self.assertFalse(single.erasure_leaves_contact_free())
            if size_a == size_b:
                self.assertFalse(check_knot(single.relation(), ("A", "B"), "c", erasure="absence").binding)
        self.assertEqual(set(CONTACTS), {"latch", "driven", "hub", "single point"})


class PatternTest(unittest.TestCase):
    XYZ = ("x", "y", "z")

    def all_patterns(self, names=XYZ) -> list[Relation]:
        return [Relation(names, r.rows) for r in all_relations_on_three()]

    def test_the_original_patterns(self) -> None:
        odd = Relation.from_cnf(["x y z", "x -y -z", "-x y -z", "-x -y z"], self.XYZ)
        even = Relation.from_cnf(["x y -z", "x -y z", "-x y z", "-x -y -z"], self.XYZ)
        self.assertTrue(odd.equivalent(parity(self.XYZ, True)))
        self.assertTrue(even.equivalent(parity(self.XYZ, False)))
        self.assertEqual(odd.restrict({"x": False}).table(), ["01", "10"])
        self.assertEqual(odd.restrict({"x": True}).table(), ["00", "11"])
        both = Relation.from_cnf(
            ["x y z", "x -y -z", "-x y -z", "-x -y z", "x y -z", "x -y z", "-x y z", "-x -y -z"], self.XYZ)
        self.assertTrue(both.is_empty())

    def test_controllers_need_three_places(self) -> None:
        for relation in self.all_patterns():
            flags = {controls(relation, name) for name in self.XYZ}
            if relation.rows:
                self.assertEqual(len(flags), 1)
            self.assertEqual(flags == {True}, not relation.is_majority_closed())

    def test_what_a_whole_hides_from_its_pairs(self) -> None:
        hidden = [r for r in self.all_patterns() if hides_from_parts(r)]
        self.assertEqual(len(hidden), 34)
        shapes = three_variable_shapes()
        self.assertEqual([(excluded, count) for excluded, count, _ in shapes],
                         [(1, 8), (2, 4), (2, 12), (3, 8), (4, 2)])
        most = max(emergent_information(r) for r in self.all_patterns() if r.rows)
        self.assertEqual(most, 1.0)
        tops = [r for r in self.all_patterns() if r.rows and emergent_information(r) == most]
        self.assertEqual({frozenset(r.rows) for r in tops},
                         {parity(self.XYZ, True).rows, parity(self.XYZ, False).rows})
        self.assertEqual([fewest_states_hiding_pairs(n) for n in (3, 4, 5)], [4, 5, 6])

    def test_patterns_of_patterns(self) -> None:
        seven = ("x", "y", "z", "u", "v", "w", "c")
        matched = Relation.from_predicate(seven, lambda v: v["c"] == (
            ((v["x"] + v["y"] + v["z"]) % 2 == 0) == ((v["u"] + v["v"] + v["w"]) % 2 == 1)))
        self.assertTrue(matched.equivalent(parity(seven, True)) or matched.equivalent(parity(seven, False)))
        self.assertTrue(hides_from_parts(matched))
        for size in range(2, 7):
            names = tuple(f"x{i}" for i in range(1, size + 1))
            for odd in (True, False):
                clauses, witnesses = parity_chain(names, odd)
                self.assertTrue(all(len(clause) <= 3 for clause in clauses))
                self.assertEqual(len(clauses), 4 * (size - 1) + 1)
                self.assertTrue(Relation.from_cnf(clauses, names, witnesses).equivalent(parity(names, odd)))

    def test_every_knot_is_synergy_but_not_every_synergy_is_a_knot(self) -> None:
        patterns = [r for r in self.all_patterns() if r.rows]
        knots = [r for r in patterns if hides_from_parts(r)]
        for knot in knots:
            self.assertLess(co_information(knot), 0)
            self.assertAlmostEqual(co_information(knot, "hartley"), -information(knot))

        def independent(relation: Relation, i: int, j: int) -> bool:
            rows = relation.rows
            count = lambda test: sum(1 for row in rows if test(row))
            return all(
                len(rows) * count(lambda r: r[i] == a and r[j] == b)
                == count(lambda r: r[i] == a) * count(lambda r: r[j] == b)
                for a in (False, True) for b in (False, True))

        pure = [k for k in knots if all(independent(k, i, j) for i, j in combinations(range(3), 2))]
        self.assertEqual({k.rows for k in pure}, {parity(self.XYZ, True).rows, parity(self.XYZ, False).rows})
        pairwise = [r for r in patterns if r.is_majority_closed()]
        synergistic = [r for r in pairwise if co_information(r) < -1e-12]
        self.assertEqual(len(synergistic), 8)
        at_most_one = Relation.from_cnf(["-x -y", "-x -z", "-y -z"], self.XYZ)
        self.assertLess(co_information(at_most_one), 0)
        self.assertFalse(hides_from_parts(at_most_one))
        and_gate = Relation.from_predicate(self.XYZ, lambda v: v["z"] == (v["x"] and v["y"]))
        self.assertLess(co_information(and_gate), 0)
        self.assertFalse(hides_from_parts(and_gate))
        self.assertFalse(and_gate.is_majority_closed())

    def test_competing_pairs_make_knots(self) -> None:
        knots = [r for r in self.all_patterns() if hides_from_parts(r)]
        opposite = {k.rows for k in knots if len({sum(row) % 2 for row in k.excluded()}) == 2}
        self.assertEqual(len(opposite), 4)
        frustrated = set()
        for differ in product((False, True), repeat=3):
            clauses = []
            for (a, b), apart in zip((("x", "y"), ("x", "z"), ("y", "z")), differ):
                clauses += [f"{a} {b}", f"-{a} -{b}"] if apart else [f"{a} -{b}", f"-{a} {b}"]
            odd = sum(differ) % 2 == 1
            self.assertEqual(Relation.from_cnf(clauses, self.XYZ).is_empty(), odd)
            best = least_violation(clauses, self.XYZ)
            self.assertEqual(hides_from_parts(best), odd)
            if odd:
                frustrated.add(best.rows)
        self.assertEqual(frustrated, opposite)

        # On four variables every knot meets some three-variable slice in states
        # that are not one opposite pair, which no pairwise energy allows.
        cube = list(product((False, True), repeat=4))

        def excluded_sets(chosen=(), start=0):
            if chosen:
                yield chosen
            for k in range(start, len(cube)):
                if all(sum(p != q for p, q in zip(cube[k], c)) != 1 for c in chosen):
                    yield from excluded_sets(chosen + (cube[k],), k + 1)

        def bad_slice(excluded) -> bool:
            for fixed in range(4):
                free = [i for i in range(4) if i != fixed]
                for value in (False, True):
                    meet = [e for e in excluded if e[fixed] == value]
                    if meet and not (len(meet) == 2 and all(meet[0][i] != meet[1][i] for i in free)):
                        return True
            return False

        four = ("a", "b", "c", "d")
        found = list(excluded_sets())
        self.assertEqual(len(found), 742)
        for excluded in found:
            self.assertTrue(hides_from_parts(Relation(four, frozenset(cube) - frozenset(excluded))))
            self.assertTrue(bad_slice(excluded))

        for n in (4, 5):
            names = tuple(f"c{i}" for i in range(n))
            clauses = [f"{names[0]} {names[1]}", f"-{names[0]} -{names[1]}"]
            for i in range(1, n):
                a, b = names[i], names[(i + 1) % n]
                clauses += [f"{a} -{b}", f"-{a} {b}"]
            best = least_violation(clauses, names)
            self.assertFalse(hides_from_parts(best))
            self.assertEqual(set(bonds(best)), {frozenset(t) for t in combinations(names, 3)})
            self.assertEqual(ties(best), [])

        def negated(literal: str) -> str:
            return literal[1:] if literal.startswith("-") else f"-{literal}"

        for knot in knots:
            clauses, hidden = [], []
            for k, row in enumerate(knot.excluded()):
                l1, l2, l3 = (f"-{name}" if value else name for name, value in zip(self.XYZ, row))
                w = f"w{k}"
                hidden.append(w)
                clauses += [l1, l2, l3, w,
                            f"{negated(l1)} {negated(l2)}", f"{negated(l2)} {negated(l3)}",
                            f"{negated(l1)} {negated(l3)}", f"{l1} -{w}", f"{l2} -{w}", f"{l3} -{w}"]
            self.assertTrue(all(len(clause.split()) <= 2 for clause in clauses))
            self.assertEqual(least_violation(clauses, self.XYZ, hidden).rows, knot.rows)

    def test_two_readings_of_erasure(self) -> None:
        loops, contact = ("A", "B"), "c"
        patterns = self.all_patterns(("A", "B", "c"))
        forgetting = [r for r in patterns if entwines(r, loops, contact, "forgetting")]
        absence = [r for r in patterns if entwines(r, loops, contact, "absence")]
        self.assertEqual(len(forgetting), 34)
        self.assertEqual(len(absence), 2)
        self.assertTrue(all(r in forgetting for r in absence))
        self.assertFalse(any(r.is_majority_closed() for r in forgetting))
        par = parity(("A", "B", "c"), False)
        self.assertTrue(entwines(par, loops, contact, "forgetting"))
        self.assertFalse(entwines(par, loops, contact, "absence"))
        hub = Relation.from_cnf(["-A c", "-B c"], ("A", "B", "c"))
        self.assertFalse(entwines(hub, loops, contact, "forgetting"))
        with self.assertRaises(ValueError):
            entwines(par, loops, contact, "erased")


class ChoiceTest(unittest.TestCase):
    def test_knots_need_alternatives(self) -> None:
        knots = two_loop_knots()
        self.assertEqual(len(knots), 34)
        self.assertEqual(min(len(k.rows) for k in knots), 4)
        self.assertTrue(all(open_variables(k) == list(k.variables) for k in knots))
        names = ("p", "q", "r", "s")
        single = Relation(names, frozenset({(True, False, False, True)}))
        self.assertFalse(any(hides_from_parts(single.project(list(trio)))
                             for trio in combinations(names, 3)))

    def test_selecting_a_value_leaves_logic(self) -> None:
        for knot in two_loop_knots():
            for name in knot.variables:
                rests = [knot.restrict({name: value}) for value in (False, True)]
                self.assertTrue(all(len(rest.variables) == 2 for rest in rests))
                self.assertTrue(any(not rest.is_full() for rest in rests))

    def test_requirement_and_choice_are_two_readings(self) -> None:
        knots = two_loop_knots()
        rows = {k.rows for k in knots}
        for knot in knots:
            for flips in (("A",), ("B", "c"), ("A", "B", "c")):
                self.assertIn(negate(knot, flips).rows, rows)
        counts = (sum(k.is_and_closed() for k in knots), sum(is_or_closed(k) for k in knots),
                  sum(not k.is_and_closed() and not is_or_closed(k) for k in knots))
        self.assertEqual(counts, (8, 8, 18))
        for knot in knots:
            if knot.is_and_closed():
                self.assertTrue(is_or_closed(negate(knot, knot.variables)))
        atom = Relation.from_cnf(["-A -B c"], ("A", "B", "c"))
        self.assertEqual(worlds_given(atom, {"A": True, "B": True}), [frozenset("ABc")])
        self.assertEqual(worlds_given(atom, {"c": False}, exists=False),
                         [frozenset({"A", "c"}), frozenset({"B", "c"})])

    def test_every_three_literal_clause_is_a_knot(self) -> None:
        for signs in product((False, True), repeat=3):
            clause = tuple(zip(("x", "y", "z"), signs))
            relation = Relation.from_cnf([clause], ("x", "y", "z"))
            self.assertTrue(check_knot(relation, ("x", "y"), "z").is_knot)
            self.assertEqual(relation.is_and_closed(), sum(signs) <= 1)


class SpaceTest(unittest.TestCase):
    def test_bonds_come_from_allowed_states(self) -> None:
        two = Relation.from_cnf(["-A -B c", "-c -D e"], ("A", "B", "c", "D", "e"))
        self.assertEqual(set(bonds(two)), {frozenset("ABc"), frozenset("cDe"), frozenset("ABDe")})
        loops = ("L1", "L2", "L3", "L4")
        chain, witnesses = witness_chain(loops, "c")
        hidden = Relation.from_cnf(chain, (*loops, "c"), witnesses)
        self.assertEqual(bonds(hidden), [frozenset((*loops, "c"))])

    def test_a_knot_is_a_hollow_simplex(self) -> None:
        for size in (3, 4, 5):
            names = tuple(f"v{i}" for i in range(size))
            for knot in (knot_relation(names[:-1], names[-1]), parity(names, False)):
                self.assertEqual(homology(free_sets(knot)), {size - 2: 1})

    def test_bonds_compose_into_a_bond_or_nothing(self) -> None:
        outcomes = []
        for k1 in two_loop_knots():
            for k2 in two_loop_knots():
                composite = compose(Relation(("A", "B", "c"), k1.rows), Relation(("c", "D", "e"), k2.rows))
                self.assertTrue(hides_from_parts(composite) or composite.is_full())
                outcomes.append(hides_from_parts(composite))
        self.assertEqual((outcomes.count(True), outcomes.count(False)), (1084, 72))

    def test_separation_grows_along_a_chain(self) -> None:
        names = ("L1", "L2", "c1", "L3", "c2", "L4", "c3")
        atoms = Relation.from_cnf(["-L1 -L2 c1", "-c1 -L3 c2", "-c2 -L4 c3"], names)
        self.assertEqual([smallest_bond(atoms, "L1", end) for end in ("c1", "c2", "c3")], [3, 4, 5])

    def test_every_shape_is_some_systems_shape(self) -> None:
        generator = random.Random(20261019)
        for _ in range(100):
            size = generator.randint(3, 6)
            names = tuple(f"x{i}" for i in range(size))
            tops = [frozenset(generator.sample(names, generator.randint(1, size))) for _ in range(3)]
            faces = {frozenset(part) for top in tops for k in range(len(top) + 1)
                     for part in combinations(sorted(top), k)} | {frozenset({n}) for n in names}
            self.assertEqual(set(free_sets(complex_relation(names, faces))), faces)

    def test_two_clause_shapes_are_flag(self) -> None:
        generator = random.Random(20261019)
        names = tuple(f"x{i}" for i in range(5))
        for _ in range(150):
            witnesses = tuple(f"w{i}" for i in range(generator.randint(0, 2)))
            clauses = []
            for _ in range(generator.randint(2, 6)):
                first, second = generator.sample(names + witnesses, 2)
                clauses.append(((first, generator.random() < 0.5), (second, generator.random() < 0.5)))
            relation = Relation.from_cnf(clauses, names, witnesses)
            if relation.is_empty():
                continue
            self.assertEqual(bonds(relation), [])
            faces = set(free_sets(relation))
            for size in range(3, len(names) + 1):
                for chosen in combinations(names, size):
                    if all(frozenset(pair) in faces for pair in combinations(chosen, 2)):
                        self.assertIn(frozenset(chosen), faces)

    def test_holes_made_of_holes(self) -> None:
        separate = Relation.from_cnf(["-A -B c", "-D -E f"], ("A", "B", "c", "D", "E", "f"))
        shared = Relation.from_cnf(["-A -B c", "-c -D e"], ("A", "B", "c", "D", "e"))
        self.assertEqual(homology(free_sets(separate)), {3: 1})
        self.assertEqual(len(bonds(separate)), 2)
        self.assertEqual(homology(free_sets(shared)), {2: 2})
        self.assertEqual(len(bonds(shared)), 3)
        named = Relation.from_predicate(("A", "B", "w"), lambda v: v["w"] == (v["A"] != v["B"]))
        self.assertEqual(bonds(named), [frozenset("ABw")])

    def test_ties_alone_can_surround_a_hole(self) -> None:
        square = Relation.from_cnf(["-a c", "a -c", "-b d", "b -d"], ("a", "b", "c", "d"))
        self.assertEqual(bonds(square), [])
        self.assertEqual(set(ties(square)), {frozenset("ac"), frozenset("bd")})
        self.assertEqual(homology(free_sets(square)), {1: 1})


class CompetitionTest(unittest.TestCase):
    """Both readings of rules that cannot all hold (epic KNOT-COMPETITION-20261019-001)."""

    def test_two_readings_of_a_frustrated_triangle(self) -> None:
        self.assertTrue(triangle(reading="strict").is_empty())
        nae = triangle()
        self.assertEqual(len(nae.rows), 6)
        self.assertTrue(hides_from_parts(nae))
        self.assertTrue(least_set_knot(nae))
        self.assertFalse(hides_from_parts(triangle(weights=(2, 1, 1))))
        for differ in product((False, True), repeat=3):
            if sum(differ) % 2 == 0:
                self.assertEqual(triangle(differ), triangle(differ, reading="strict"))
                self.assertFalse(hides_from_parts(triangle(differ)))

    def test_which_knots_pairs_make(self) -> None:
        self.assertEqual(sum(least_set_knot(k) for k in two_loop_knots()), 4)
        self.assertFalse(least_set_knot(parity(("a", "b", "c", "d"), True)))
        with self.assertRaises(ValueError):
            least_set_knot(Relation.from_cnf(["-A c", "-B c"], ABC))

    def test_near_and_far_comes_from_a_triangulated_layout(self) -> None:
        self.assertEqual([len(separation_levels(triangle_strip(n))) for n in range(5, 10)], [2, 2, 3, 3, 4])
        for n in range(5, 10):
            names = tuple(f"v{i}" for i in range(n))
            nae_strip = Relation.from_predicate(
                names, lambda v, n=n, names=names: all(
                    len({v[names[i]], v[names[i + 1]], v[names[i + 2]]}) == 2 for i in range(n - 2)))
            self.assertTrue(triangle_strip(n).equivalent(nae_strip))
        self.assertEqual(len(triangle_strip(6, per_triangle=False).rows), 2)
        self.assertEqual(separation_levels(triangle_strip(6, per_triangle=False)), [2])
        seven = tuple(f"r{i}" for i in range(7))
        ring = allowed_states(seven, [(seven[i], seven[(i + 1) % 7], True) for i in range(7)])
        self.assertEqual(separation_levels(ring), [3])
        self.assertTrue(allowed_states(seven, [(seven[i], seven[(i + 1) % 7], True) for i in range(7)],
                                       reading="strict").is_empty())


class RingsTest(unittest.TestCase):
    """Which knots remember a loop (epic KNOT-LOOPS-20261019-001)."""

    def setUp(self) -> None:
        self.parity = Relation.from_predicate(("w", "m", "x"), lambda v: (v["w"] ^ v["m"] ^ v["x"]) is False)
        self.nae = Relation.from_predicate(("w", "m", "x"), lambda v: len({v["w"], v["m"], v["x"]}) == 2)

    def test_parity_rings_become_one_knot(self) -> None:
        for k in range(3, 7):
            composite = ring(self.parity, "w", "x", k)
            self.assertTrue(hides_from_parts(composite))
            self.assertAlmostEqual(bits(composite), 1.0)

    def test_not_all_equal_rings_dissolve(self) -> None:
        for k in range(1, 7):
            self.assertTrue(ring(self.nae, "w", "x", k).is_full())

    def test_ring_theorem_on_every_placement(self) -> None:
        for r in two_loop_knots():
            for a, b in permutations(r.variables, 2):
                for k in (1, 2, 3):
                    composite = ring(r, a, b, k)
                    excluded = frozenset(p for p in product((False, True), repeat=k) if p not in composite.rows)
                    self.assertEqual(excluded, predicted_excluded(r, a, b, k))

    def test_memory_kinds(self) -> None:
        self.assertEqual(memory(self.parity, "w", "x"), "every length")
        self.assertEqual(memory(self.nae, "w", "x"), "never")

    def test_parity_network_keeps_a_bit_per_loop(self) -> None:
        k4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        self.assertAlmostEqual(bits(network(self.parity, "w", "x", k4)), 3.0)
        square = [(0, 1), (1, 2), (2, 3), (0, 3)]
        self.assertAlmostEqual(bits(network(self.parity, "w", "x", square)), 1.0)


class HolonomyTest(unittest.TestCase):
    """What networks of permutation contact remember (epic HOLES-COHOMOLOGY-20261019-001)."""

    def test_network_rule_matches_brute_force(self) -> None:
        rng = random.Random(1)
        theta = [(0, 2), (2, 1), (0, 3), (3, 1), (0, 4), (4, 1)]
        for _ in range(100):
            perms = [tuple(rng.sample(range(3), 3)) for _ in theta]
            brute = any(all(w[b] == p[w[a]] for (a, b), p in zip(theta, perms))
                        for w in product(range(3), repeat=5))
            self.assertEqual(allowed(5, theta, perms), brute)

    def test_selector_shape_is_the_nerve(self) -> None:
        rng = random.Random(2)
        for _ in range(60):
            holonomies = [tuple(rng.sample(range(4), 4)) for _ in range(3)]
            self.assertEqual(set(free_sets(selector_relation(holonomies))), nerve(holonomies))

    def test_star_knots_loops_as_an_atom(self) -> None:
        for k in (2, 3, 4):
            self.assertTrue(knot_among_loops(star(k)))
        relation = selector_relation(star(3))
        self.assertTrue(check_knot(relation, ("s0", "s1"), "s2").is_knot)
        self.assertEqual(relation.excluded(), [(True, True, True)])
        self.assertEqual(homology(free_sets(relation)), {1: 1})

    def test_knot_among_k_loops_needs_k_plus_one_values(self) -> None:
        for k in (2, 3):
            self.assertFalse(any(knot_among_loops(h) for h in product(permutations(range(k)), repeat=k)))

    def test_free_contact_binds_nothing(self) -> None:
        shifts = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
        for holonomies in product(shifts, repeat=3):
            relation = selector_relation(holonomies)
            self.assertEqual(ties(relation), [])
            self.assertEqual(bonds(relation), [])

    def test_memory_depends_only_on_the_loop_count(self) -> None:
        s3 = list(permutations(range(3)))
        self.assertEqual(allowed_fraction(s3, 1), Fraction(2, 3))
        self.assertEqual(allowed_fraction(s3, 2), Fraction(5, 18))
        z3 = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
        self.assertEqual(allowed_fraction(z3, 3), Fraction(1, 27))

    def test_coprime_tie_fools_integer_reasoning(self) -> None:
        bouquet = [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]
        identity = (0, 1, 2, 3, 4)
        tie = [identity, identity, (1, 0, 2, 3, 4), identity, identity, (0, 1, 3, 4, 2)]
        self.assertFalse(allowed(5, bouquet, tie))
        self.assertEqual(orbit_sizes(5, bouquet, tie), [2, 3])
        self.assertTrue(basic_relaxation_accepts([2, 3], "Z"))
        self.assertFalse(basic_relaxation_accepts([2, 2], "Z"))
        self.assertTrue(basic_relaxation_accepts([2], "F3"))
        self.assertFalse(basic_relaxation_accepts([2], "F2"))


class DepthTest(unittest.TestCase):
    """How deep a network's hole is (epic DEEP-HOLES-20261020-001)."""

    def test_every_non_atom_knot_is_a_local_hole(self) -> None:
        for relation in two_loop_knots():
            self.assertEqual(scope_hole_rank(relation), len(relation.excluded()) - 1)

    def test_depth_is_three_for_matched_rings(self) -> None:
        for name in ("K4", "K33", "cube"):
            self.assertEqual(charge_depth(*cubic(name), 2, 2), 3)

    def test_depth_is_the_toggle_width_otherwise(self) -> None:
        expected = {"K4": 5, "prism": 5, "K33": 6, "cube": 6, "wagner": 6, "petersen": 7}
        for name, width in expected.items():
            self.assertEqual(charge_depth(*cubic(name), 2, 0), width)
            self.assertEqual(toggle_width(*cubic(name)), cutwidth(*cubic(name)) + 1)
            self.assertEqual(toggle_width(*cubic(name)), toggle_width(*cubic(name), monotone=True))


class CommandLineTest(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = {**os.environ, "PYTHONPATH": str(ROOT / "tools")}
        return subprocess.run(
            [sys.executable, "-B", "-m", "knotlab", *arguments],
            capture_output=True, text=True, env=environment, check=False,
        )

    def test_check_reports_a_knot(self) -> None:
        result = self.run_cli("check", "--cnf", "~A ~B c", "--loops", "A", "B",
                              "--contact", "c", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["is_knot"])

    def test_demo_verdicts_match(self) -> None:
        result = self.run_cli("demo")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all reference verdicts match", result.stdout)

    def test_ring_checks_match(self) -> None:
        result = self.run_cli("rings")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all ring checks match", result.stdout)

    def test_holonomy_checks_match(self) -> None:
        result = self.run_cli("holonomy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all holonomy checks match", result.stdout)

    def test_depth_checks_match(self) -> None:
        result = self.run_cli("depth")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all depth checks match", result.stdout)

    def test_competition_checks_match(self) -> None:
        result = self.run_cli("competition")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all competition checks match", result.stdout)

    def test_space_checks_match(self) -> None:
        result = self.run_cli("space")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all space checks match", result.stdout)

    def test_choice_checks_match(self) -> None:
        result = self.run_cli("choice")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all choice checks match", result.stdout)

    def test_pattern_checks_match(self) -> None:
        result = self.run_cli("patterns")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all pattern checks match", result.stdout)

    def test_presence_checks_match(self) -> None:
        result = self.run_cli("presence")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all presence checks match", result.stdout)

    def test_world_checks_match(self) -> None:
        result = self.run_cli("worlds")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all world checks match", result.stdout)


if __name__ == "__main__":
    unittest.main()
