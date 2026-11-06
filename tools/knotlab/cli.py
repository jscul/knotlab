"""Command-line interface for the knot laboratory."""

from __future__ import annotations

import argparse
import json
import random
import sys
from fractions import Fraction
from itertools import combinations, permutations, product
from typing import Sequence

from .choice import is_or_closed, negate, open_variables, two_loop_knots, worlds_given
from .competition import allowed_states, least_set_knot, separation_levels, triangle, triangle_strip
from .examples import examples, guarded_examples
from .depth import charge_depth, cubic, cutwidth, scope_hole_rank, toggle_width
from .executor import leak_report
from .holonomy import (
    allowed,
    allowed_fraction,
    basic_relaxation_accepts,
    knot_among_loops,
    nerve,
    orbit_sizes,
    selector_relation,
    star,
)
from .knots import check_knot, knot_relation, witness_chain
from .loops import implication_loop, loop_report, signature, signed_loop
from .patterns import (
    controls,
    emergent_information,
    entwines,
    fewest_states_hiding_pairs,
    hides_from_parts,
    parity,
    parity_chain,
    three_variable_shapes,
)
from .presence import CONTACTS, TwoLoops, conserved, copy_ring, frozen_states, inverter_ring, reader_is_exact
from .relations import Relation, format_clause, parse_cnf
from .rings import bits, memory, network, predicted_excluded, ring
from .space import bonds, complex_relation, compose, free_sets, homology, smallest_bond, ties
from .worlds import (
    Rule,
    add_by_forced_world,
    atom,
    choices_reaching,
    dual_rail_adder,
    essential,
    existence_profile,
    forced_world,
    from_atoms_and_distinctions,
    gate_relation,
    knot_tree,
    minimal_worlds,
    thread,
)

YES = {True: "yes", False: "no"}


def _table(header: Sequence[str], rows: Sequence[Sequence[object]]) -> list[str]:
    widths = [max(len(str(cell)) for cell in column) for column in zip(header, *rows)]

    def line(row: Sequence[object]) -> str:
        return "  ".join(str(cell).ljust(width) for cell, width in zip(row, widths)).rstrip()

    return [line(header), line(["-" * width for width in widths]), *map(line, rows)]


def demo() -> int:
    mismatches = 0
    print("Knot definition (INTUITIONS.md)")
    print("K1 binding, K2 loss on erasure (forgetting a loop or the contact), K3 coexistence")
    print("'absence' is the earlier reading, where erasing sets a presence variable to absent\n")
    rows, notes = [], []
    for example in examples():
        report = check_knot(example.relation, example.loops, example.contact)
        absence = check_knot(example.relation, example.loops, example.contact, erasure="absence")
        mismatches += report.is_knot != example.expected_knot
        mismatches += absence.is_knot != example.expected_under_absence
        rows.append((
            example.name, YES[report.binding], YES[report.loss_on_erasure],
            YES[report.coexistence], YES[report.is_knot], YES[absence.is_knot],
            YES[report.pairwise_definable], report.minimum_width,
        ))
        if report.notes:
            notes.append(f"  {example.name}: {report.notes[0]}")
    header = ("case", "K1", "K2", "K3", "knot", "absence", "2-CNF definable", "min width")
    print("\n".join(_table(header, rows)))
    print("\nWhy the non-knots fail:")
    print("\n".join(notes))

    print("\nLoops written with 2-clauses")
    for size in range(2, 6):
        report = loop_report(implication_loop([f"x{i}" for i in range(1, size + 1)]))
        print(f"  implication loop of {size}: {report.states} states, "
              f"{report.free_bits:.0f} free bit, collapsed: {YES[report.collapsed]}")
    names = ("x1", "x2", "x3", "x4")
    even = signed_loop(names, (False, True, True, False))
    print(f"  equal/unequal loop with two unequal steps: {len(even.rows)} states; "
          f"x1 and x2 always show {'/'.join(sorted(signature(even, 'x1', 'x2')))}, "
          f"x1 and x3 always show {'/'.join(sorted(signature(even, 'x1', 'x3')))}")
    odd = signed_loop(names, (True, False, False, False))
    print(f"  equal/unequal loop with one unequal step: "
          f"contradictory: {YES[loop_report(odd).contradictory]}")

    print("\nEvaluation rules that supply an input")
    for name, system in guarded_examples().items():
        report = leak_report(system)
        print(f"  {name}: knot when read relationally: {YES[report.relational.is_knot]}; "
              f"knot when a loop's guard is checked only while it runs: "
              f"{YES[report.gated.is_knot]}; leak: {YES[report.leaks]}")
        for change in report.widened if report.leaks else ():
            print(f"    {change}")

    print("\nWidth threshold")
    for size in range(2, 6):
        loops = tuple(f"L{i}" for i in range(1, size + 1))
        clauses, witnesses = witness_chain(loops, "c")
        built = Relation.from_cnf(clauses, loops + ("c",), witnesses)
        target = knot_relation(loops, "c")
        print(f"  {size} loops: {len(clauses)} three-literal clause(s), "
              f"{len(witnesses)} witness(es), equals the knot: {YES[built.equivalent(target)]}; "
              f"without witnesses needs width {target.minimum_width()}; "
              f"2-CNF definable: {YES[target.is_majority_closed()]}")
    chain, _ = witness_chain(("L1", "L2", "L3"), "c")
    print("  three-loop chain: " + "; ".join(format_clause(clause) for clause in chain))

    print("\nall reference verdicts match" if not mismatches
          else f"\n{mismatches} reference verdicts did not match")
    return 1 if mismatches else 0


def _sets(profile: dict[frozenset[str], bool]) -> str:
    return ", ".join(
        "{" + ", ".join(sorted(chosen)) + "}"
        for chosen, exists in sorted(profile.items(), key=lambda item: (len(item[0]), sorted(item[0])))
        if exists
    )


def worlds() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    print("What exists, given which loops are present (INTUITIONS.md)")
    show("atom A ∧ B → c: c exists when", _sets(existence_profile([atom("A", "B", "c")], "AB", "c")), "{A, B}")
    hub = [Rule(frozenset({"A"}), "c"), Rule(frozenset({"B"}), "c")]
    show("common hub A → c, B → c: c exists when", _sets(existence_profile(hub, "AB", "c")), "{A}, {B}, {A, B}")

    print("\nBuilding from atoms")
    rules, loops = knot_tree(3)
    clauses = [tuple((premise, False) for premise in sorted(rule.premises)) + ((rule.result, True),)
               for rule in rules]
    witnesses = sorted({rule.result for rule in rules} - {"c"})
    as_relation = Relation.from_cnf(clauses, [*loops, "c"], witnesses)
    show(f"tree of {len(loops)} loops joined by {len(rules)} atoms, read as a relation: "
         f"a knot of all {len(loops)} loops", check_knot(as_relation, loops, "c").is_knot, True)
    rules, loops = knot_tree(8)
    show(f"tree of {len(loops)} loops joined by {len(rules)} atoms: root exists with every loop present",
         "c" in forced_world(rules, loops), True)
    show("erasing any single loop removes the root", essential(rules, loops, "c") == frozenset(loops), True)
    rules, loops = knot_tree(16)
    show(f"tree of {len(loops)} loops joined by {len(rules)} atoms: root exists",
         "c" in forced_world(rules, loops), True)
    show("the same tree with loop L12345 erased: root exists",
         "c" in forced_world(rules, [loop for loop in loops if loop != "L12345"]), False)
    redundant = [atom("A", "B", "c"), atom("C", "D", "c")]
    show("two ways to make c (A ∧ B → c, C ∧ D → c): c survives erasing A",
         "c" in forced_world(redundant, "BCD"), True)

    print("\nDistinctions and bonds")
    references = {
        "atom": Relation.from_cnf(["-A -B c"], ("A", "B", "c")),
        "choice c → A ∨ B": Relation.from_cnf(["-c A B"], ("A", "B", "c")),
        "parity": Relation.from_predicate(("A", "B", "c"), lambda v: v["A"] ^ v["B"] ^ v["c"]),
    }
    show("definable by requirements alone (closed under AND)",
         ", ".join(f"{name}: {YES[relation.is_and_closed()]}" for name, relation in references.items()),
         "atom: yes, choice c → A ∨ B: no, parity: no")
    cube = [(a, b, c) for a in (False, True) for b in (False, True) for c in (False, True)]
    rebuilt = sum(
        from_atoms_and_distinctions(relation).rows == relation.rows
        for relation in (Relation(("x", "y", "z"), frozenset(row for i, row in enumerate(cube) if mask >> i & 1))
                         for mask in range(256))
    )
    show("relations on three places rebuilt from atoms and distinctions alone", rebuilt, 256)

    print("\nBits carried as which of two things exists")
    show(f"4-bit addition by forced derivation from {len(dual_rail_adder(4))} atoms, correct for all 256 pairs",
         all(add_by_forced_world(a, b, 4) == a + b for a in range(16) for b in range(16)), True)
    open_bits = [(f"{x}{i}=0", f"{x}{i}=1") for x in "ab" for i in range(3)]
    target = [f"s{i}={5 >> i & 1}" for i in range(3)] + ["carry3=0"]
    ways = choices_reaching(dual_rail_adder(3), open_bits, target, given=["carry0=0"])
    pairs = sorted(tuple(sum(1 << i for i in range(3) if f"{x}{i}=1" in way) for x in "ab")
                   for way in ways)
    show(f"run backward, ways of making the {len(open_bits)} input distinctions "
         f"that reach the sum 5 (of {2 ** len(open_bits)})",
         " ".join(f"{a}+{b}" for a, b in pairs), "0+5 1+4 2+3 3+2 4+1 5+0")

    print("\nRequirement versus choice")
    show("atom with A and B present: minimal worlds",
         [sorted(world) for world in minimal_worlds(
             Relation.from_cnf(["-A -B c"], ("A", "B", "c")).restrict({"A": True, "B": True}))],
         [["c"]])
    show("choice c → A ∨ B with c present: minimal worlds",
         [sorted(world) for world in minimal_worlds(
             Relation.from_cnf(["-c A B"], ("A", "B", "c")).restrict({"c": True}))],
         [["A"], ["B"]])

    print("\nInfinite threads")
    rules, loops = thread(300)
    show("thread of 300 atoms: w_k depends on exactly the first k+1 loops (k = 1, 10, 100, 300)",
         all(essential(rules, loops, f"w{k}") == frozenset(loops[: k + 1]) for k in (1, 10, 100, 300)),
         True)
    print("  every thing in a forced world rests on finitely many loops, and by compactness no")
    print("  set of finite clauses binds infinitely many loops into one contact")

    print("\nTwo-input gates")
    using_both = pairwise = 0
    for table in range(16):
        def gate(x: bool, y: bool, table: int = table) -> bool:
            return bool(table >> (2 * x + y) & 1)
        both = any(gate(False, y) != gate(True, y) for y in (False, True)) and any(
            gate(x, False) != gate(x, True) for x in (False, True))
        using_both += both
        pairwise += gate_relation(gate).is_majority_closed() == (not both)
    show("gates that use both inputs", using_both, 10)
    show("gates whose relation is pairwise exactly when they ignore an input", pairwise, 16)
    and_gate = gate_relation(lambda x, y: x and y)
    two_place = [clause for clause in and_gate.implied_clauses(2) if len(clause) == 2]
    show("AND gate is its two-place parts plus the atom x ∧ y → z",
         Relation.from_cnf(two_place, ("x", "y", "z")).rows != and_gate.rows
         and Relation.from_cnf(two_place + ["-x -y z"], ("x", "y", "z")).rows == and_gate.rows,
         True)

    print("\nall world checks match" if not mismatches else f"\n{mismatches} world checks did not match")
    return 1 if mismatches else 0


def space() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    def named(sets: list[frozenset[str]]) -> str:
        return ", ".join("{" + ", ".join(sorted(s)) + "}" for s in sorted(sets, key=lambda s: (len(s), sorted(s))))

    print("Whether contact structure becomes space-like (ticket KNOT-FOUNDATION-20261019-001D)")
    print("\nBonds are read from allowed states, not from how the clauses are written")
    two = Relation.from_cnf(["-A -B c", "-c -D e"], ("A", "B", "c", "D", "e"))
    show("two atoms sharing c: bonds", named(bonds(two)), "{A, B, c}, {D, c, e}, {A, B, D, e}")
    loops = ("L1", "L2", "L3", "L4")
    chain, witnesses = witness_chain(loops, "c")
    hidden = Relation.from_cnf(chain, (*loops, "c"), witnesses)
    show("the four-loop witness chain with its witnesses forgotten: bonds", named(bonds(hidden)),
         "{L1, L2, L3, L4, c}")

    print("\nA knot is a hole in the system's shape (its complex of free sets)")
    shapes = []
    for size in (3, 4, 5):
        names = tuple(f"v{i}" for i in range(size))
        shapes.append(homology(free_sets(knot_relation(names[:-1], names[-1]))))
    show("knots on 3, 4 and 5 variables: holes by dimension", shapes, [{1: 1}, {2: 1}, {3: 1}])
    print("  the two-loop knot is a circle: its three pairs are free and the whole is not")

    print("\nBonds compose into a bond or into nothing")
    knots3 = two_loop_knots()
    outcomes = []
    for k1 in knots3:
        for k2 in knots3:
            first = Relation(("A", "B", "c"), k1.rows)
            second = Relation(("c", "D", "e"), k2.rows)
            composite = compose(first, second)
            outcomes.append("bond" if hides_from_parts(composite) else "nothing" if composite.is_full() else "other")
    show("pairs of two-loop knots sharing one distinction: bond / nothing / other",
         f"{outcomes.count('bond')} / {outcomes.count('nothing')} / {outcomes.count('other')}", "1084 / 72 / 0")
    opposite = Relation.from_cnf(["-A -B c"], ("A", "B", "c")), Relation.from_cnf(["-c -D e"], ("c", "D", "e"))
    same = Relation.from_cnf(["-A -B c"], ("A", "B", "c")), Relation.from_cnf(["c D e"], ("c", "D", "e"))
    show("single clauses compose when they hold the shared distinction to opposite values (resolution)",
         f"opposite: {YES[hides_from_parts(compose(*opposite))]}, same: {YES[hides_from_parts(compose(*same))]}",
         "opposite: yes, same: no")

    print("\nPaths and separation")
    names = ("L1", "L2", "c1", "L3", "c2", "L4", "c3")
    atoms = Relation.from_cnf(["-L1 -L2 c1", "-c1 -L3 c2", "-c2 -L4 c3"], names)
    show("chain of three atoms: smallest bond joining L1 to c1, c2, c3",
         [smallest_bond(atoms, "L1", end) for end in ("c1", "c2", "c3")], [3, 4, 5])

    print("\nLogic allows every shape")
    generator = random.Random(20261019)
    recovered = 0
    for _ in range(200):
        size = generator.randint(3, 6)
        names = tuple(f"x{i}" for i in range(size))
        tops = [frozenset(generator.sample(names, generator.randint(1, size))) for _ in range(generator.randint(1, 4))]
        faces = {frozenset(part) for top in tops for k in range(len(top) + 1) for part in combinations(sorted(top), k)}
        faces |= {frozenset({name}) for name in names}
        recovered += set(free_sets(complex_relation(names, faces))) == faces
    show("random shapes on 3-6 variables recovered exactly from a system built for them (of 200)", recovered, 200)

    print("\nThe shape's holes are not all knots")
    square = Relation.from_cnf(["-a c", "a -c", "-b d", "b -d"], ("a", "b", "c", "d"))
    show("ties a = c and b = d: bonds / ties / holes",
         f"{len(bonds(square))} / {named(ties(square))} / {homology(free_sets(square))}",
         "0 / {a, c}, {b, d} / {1: 1}")
    print("  two pairwise ties surround a circle, so knots are the shape's atomic holes,")
    print("  not every hole it has")

    print("\nall space checks match" if not mismatches else f"\n{mismatches} space checks did not match")
    return 1 if mismatches else 0


def competition() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    print("Knots from competition: both readings of question 10 (epic KNOT-COMPETITION-20261019-001)")
    print("\nA triangle whose three pairs should all differ cannot satisfy them all")
    show("strict reading (break no rule): anything allowed", not triangle(reading="strict").is_empty(), False)
    nae = triangle()
    show("competition (break the fewest): states allowed", len(nae.rows), 6)
    show("those six states form a knot (not all equal)", hides_from_parts(nae), True)
    settled = triangle(differ=(True, True, False))
    show("a triangle whose preferences can all hold: the two readings agree",
         settled == triangle(differ=(True, True, False), reading="strict"), True)
    show("weighting one preference twice leaves a knot", hides_from_parts(triangle(weights=(2, 1, 1))), False)

    print("\nWhich knots competing pairs make on their own variables (Lean: ticket A)")
    show("two-loop knots that are least sets of a sum of terms on pairs (of 34)",
         sum(least_set_knot(k) for k in two_loop_knots()), 4)
    show("parity on four variables", least_set_knot(parity(("a", "b", "c", "d"), True)), False)
    print("  none on four or more variables; with hidden variables, every knot (2-clause gadgets)")

    print("\nNear and far (ticket B): separation levels of competition on triangle strips")
    show("counted per triangle, n = 5..9", [len(separation_levels(triangle_strip(n))) for n in range(5, 10)],
         [2, 2, 3, 3, 4])
    show("counted per pair, n = 6: states allowed", len(triangle_strip(6, per_triangle=False).rows), 2)
    seven = tuple(f"r{i}" for i in range(7))
    ring = allowed_states(seven, [(seven[i], seven[(i + 1) % 7], True) for i in range(7)])
    show("a frustrated ring of seven: separation levels", separation_levels(ring), [3])
    strip = triangle_strip(7)
    names = strip.variables
    nae_strip = Relation.from_predicate(
        names, lambda v: all(len({v[names[i]], v[names[i + 1]], v[names[i + 2]]}) == 2 for i in range(5)))
    show("counted per triangle, the strip equals strict not-all-equal on its triangles",
         strip.equivalent(nae_strip), True)
    print("  so growing near and far comes from a triangulated layout, which competition")
    print("  turns into a chain of knots; it does not supply the layout")

    print("\nall competition checks match" if not mismatches else f"\n{mismatches} competition checks did not match")
    return 1 if mismatches else 0


def rings() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    print("Which knots remember a loop (epic KNOT-LOOPS-20261019-001)")
    par = Relation.from_predicate(("w", "m", "x"), lambda v: (v["w"] ^ v["m"] ^ v["x"]) is False)
    nae = Relation.from_predicate(("w", "m", "x"), lambda v: len({v["w"], v["m"], v["x"]}) == 2)
    print("\nRings: copies pass witness x on as the next copy's w; the witnesses are then forgotten")
    show("parity rings of length 3..6 compose into one knot",
         [hides_from_parts(ring(par, "w", "x", k)) for k in range(3, 7)], [True] * 4)
    show("bits a parity ring keeps, k = 1..6", [round(bits(ring(par, "w", "x", k)), 6) for k in range(1, 7)], [1.0] * 6)
    show("not-all-equal rings of length 1..6 keep nothing",
         [ring(nae, "w", "x", k).is_full() for k in range(1, 7)], [True] * 6)

    print("\nThe ring theorem (Lean, ticket B): excluded exactly when every transfer is a permutation")
    print("and an odd number of them swap")
    placements = [(r, a, b) for r in two_loop_knots() for a in r.variables for b in r.variables if a != b]
    agree = all(frozenset(p for p in product((False, True), repeat=k) if p not in ring(r, a, b, k).rows)
                == predicted_excluded(r, a, b, k) for r, a, b in placements for k in (1, 2, 3, 4))
    show("the rule holds for all 204 placements of the 34 two-loop knots, k = 1..4", agree, True)
    kinds = {}
    for r, a, b in placements:
        kinds[memory(r, a, b)] = kinds.get(memory(r, a, b), 0) + 1
    show("placements remembering every length / odd lengths / never",
         [kinds.get("every length", 0), kinds.get("odd lengths", 0), kinds.get("never", 0)], [12, 36, 156])

    print("\nNetworks (ticket C): one copy per edge of K4, witnesses at the vertices")
    k4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    show("bits a parity network keeps (one per independent loop: 3)", round(bits(network(par, "w", "x", k4)), 6), 3.0)
    nae_bits = bits(network(nae, "w", "x", k4))
    show("not-all-equal keeps a little, under one bit", 0 < nae_bits < 1, True)
    print(f"    ({nae_bits:.3f} bits: transfers that forbid one pair act like implications and frustrate)")

    print("\nall ring checks match" if not mismatches else f"\n{mismatches} ring checks did not match")
    return 1 if mismatches else 0


def holonomy() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    print("What networks of permutation contact remember (epic HOLES-COHOMOLOGY-20261019-001)")
    print("\nThe network rule: allowed exactly when the holonomy group has a common fixed point")
    rng = random.Random(20261019)
    k4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    agree = True
    for _ in range(200):
        perms = [tuple(rng.sample(range(3), 3)) for _ in k4]
        brute = any(all(w[b] == p[w[a]] for (a, b), p in zip(k4, perms)) for w in product(range(3), repeat=4))
        agree &= brute == allowed(4, k4, perms)
    show("the covering rule agrees with brute force on 200 random K4 networks", agree, True)
    s3 = list(permutations(range(3)))
    diamond = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
    share = Fraction(sum(allowed(4, diamond, perms) for perms in product(s3, repeat=5)), 6 ** 5)
    show("uniform S3 contact on a two-loop network allows 5/18 (depends only on the loop count)",
         share == allowed_fraction(s3, 2) == Fraction(5, 18), True)

    print("\nKnots among loops (Lean, ticket B): selectors on loops sharing one base witness")
    three = selector_relation(star(3))
    report = check_knot(three, ("s0", "s1"), "s2")
    show("(03), (13), (23) bind three loops into a knot", report.is_knot, True)
    show("the knot excludes only all three selected: an atom", three.excluded(), [(True, True, True)])
    show("its shape is the nerve of the fixed-point sets, a hollow triangle",
         set(free_sets(three)) == nerve(star(3)) and homology(free_sets(three)) == {1: 1}, True)
    show("no three permutations of three values knot three loops",
         sum(knot_among_loops(h) for h in product(s3, repeat=3)), 0)
    z3 = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
    show("free contact (shifts mod 3) never ties or knots loops",
         all(not ties(selector_relation(h)) and not bonds(selector_relation(h)) for h in product(z3, repeat=3)), True)

    print("\nLocal reasoning (ticket C): two loops with holonomies (01) and (234) on five values")
    bouquet = [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]
    identity = (0, 1, 2, 3, 4)
    tie = [identity, identity, (1, 0, 2, 3, 4), identity, identity, (0, 1, 3, 4, 2)]
    first = [identity, identity, (1, 0, 2, 3, 4), identity, identity, identity]
    second = [identity, identity, identity, identity, identity, (0, 1, 3, 4, 2)]
    show("each loop closes alone", allowed(5, bouquet, first) and allowed(5, bouquet, second), True)
    show("the two loops close together", allowed(5, bouquet, tie), False)
    sizes = orbit_sizes(5, bouquet, tie)
    show("holonomy-orbit sizes", sizes, [2, 3])
    show("two-witness linear reasoning accepts it over Q, F2, F3 and Z (3 - 2 = 1)",
         [basic_relaxation_accepts(sizes, r) for r in ("Q", "F2", "F3", "Z")], [True] * 4)
    print("    (pinning one witness, or holding three at once, refutes it over every ring)")

    print("\nall holonomy checks match" if not mismatches else f"\n{mismatches} holonomy checks did not match")
    return 1 if mismatches else 0


def depth() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    print("How deep a network's hole is (epic DEEP-HOLES-20261020-001)")
    print("\nLocal holes: the complex of partial solutions at one knot's scope")
    atom = Relation.from_predicate(("a", "b", "c"), lambda v: not (v["a"] and v["b"] and v["c"]))
    nae = Relation.from_predicate(("a", "b", "c"), lambda v: len({v["a"], v["b"], v["c"]}) == 2)
    par = Relation.from_predicate(("a", "b", "c"), lambda v: (v["a"] ^ v["b"] ^ v["c"]) is True)
    show("hole ranks of the atom, not-all-equal and parity", [scope_hole_rank(r) for r in (atom, nae, par)], [0, 1, 3])
    show("every two-loop knot has a hole of rank |excluded| - 1",
         all(scope_hole_rank(r) == len(r.excluded()) - 1 for r in two_loop_knots()), True)
    print("    (so the plain hole criterion certifies only level 2 on parity and not-all-equal networks)")

    print("\nCharge networks: parity knots at the vertices of cubic graphs, edges as distinctions")
    names = ("K4", "prism", "K33", "cube", "wagner", "petersen")
    widths = {g: toggle_width(*cubic(g)) for g in names}
    show("depth over F2 (computes mod 2) on every graph", {charge_depth(*cubic(g), 2, 2) for g in names}, {3})
    show("depth over Q, F3, F5: the toggle width", [charge_depth(*cubic(g), 2, 0) for g in names], [5, 5, 6, 6, 6, 7])
    show("toggle width is cutwidth + 1 (proved at degree <= 3)",
         all(widths[g] == cutwidth(*cubic(g)) + 1 for g in names), True)
    show("K4, the prism, K33 and the cube all have treewidth 3, but depths", [widths[g] for g in names[:4]], [5, 5, 6, 6])
    print("    (proofs: DEEP-HOLES-20261020-001B-P001, CUTWIDTH-DEPTH-20261020-001B-P001)")

    print("\nall depth checks match" if not mismatches else f"\n{mismatches} depth checks did not match")
    return 1 if mismatches else 0


def choice() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    knots = two_loop_knots()
    print("Whether the base logic has real alternatives (ticket KNOT-FOUNDATION-20261019-001C)")
    print("\nKnots need alternatives")
    show("two-loop knots", len(knots), 34)
    show("fewest allowed states of any knot (of 8)", min(len(k.rows) for k in knots), 4)
    names = ("p", "q", "r", "s", "t")
    single = Relation(names, frozenset({(True, False, True, True, False)}))
    show("a world with one allowed state: knots among any three of its variables",
         sum(hides_from_parts(single.project(list(trio))) for trio in combinations(names, 3)), 0)

    print("\nKnots never select; selecting a value turns the knot into logic")
    show("every variable of every knot takes both values (no knot forces anything)",
         all(open_variables(k) == list(k.variables) for k in knots), True)
    show("for every knot and loop, some selected value leaves the other two tied pairwise",
         all(any(not k.restrict({v: value}).is_full() for value in (False, True))
             for k in knots for v in k.variables), True)

    print("\nRequirement and choice are one knot read two ways")
    show("negating any variables of a knot gives a knot",
         all(any(negate(k, flips).rows == other.rows for other in knots)
             for k in knots for flips in (("A",), ("B", "c"), ("A", "B", "c"))), True)
    atom = Relation.from_cnf(["-A -B c"], ("A", "B", "c"))
    show("¬A ∨ ¬B ∨ c with true = exists, given A and B: minimal worlds",
         [sorted(w) for w in worlds_given(atom, {"A": True, "B": True})], [["A", "B", "c"]])
    show("the same relation with false = exists, given c: minimal worlds",
         [sorted(w) for w in worlds_given(atom, {"c": False}, exists=False)], [["A", "c"], ["B", "c"]])
    show("knots that are pure requirements (closed under AND) / pure choices (closed under OR) / neither",
         f"{sum(k.is_and_closed() for k in knots)} / {sum(is_or_closed(k) for k in knots)} / "
         f"{sum(not k.is_and_closed() and not is_or_closed(k) for k in knots)}", "8 / 8 / 18")
    show("negating every variable turns each pure requirement into a pure choice",
         all(is_or_closed(negate(k, k.variables)) for k in knots if k.is_and_closed()), True)
    show("parity is neither (it offers choices whichever value counts as exists)",
         not parity(("A", "B", "c"), False).is_and_closed() and not is_or_closed(parity(("A", "B", "c"), False)), True)

    print("\nSystems of knots")
    clauses = [(a, b, c) for a in range(4) for b in range(a + 1, 5) for c in range(b + 1, 6)]
    names6 = tuple(f"x{i}" for i in range(6))
    every = all(
        check_knot(Relation.from_cnf([[(names6[i], s1), (names6[j], s2), (names6[k], s3)]],
                                     (names6[i], names6[j], names6[k])),
                   (names6[i], names6[j]), names6[k]).is_knot
        for i, j, k in clauses for s1 in (False, True) for s2 in (False, True) for s3 in (False, True))
    show("every three-literal clause on three distinct variables is a knot", every, True)
    print("  so a system of knots can state any 3-SAT instance, and deciding whether it")
    print("  allows any world is NP-complete (Cook 1971); the absence reading's knots were")
    print("  requirements only, closed under AND, with one least world found in linear time")

    print("\nall choice checks match" if not mismatches else f"\n{mismatches} choice checks did not match")
    return 1 if mismatches else 0


def patterns() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    xyz = ("x", "y", "z")
    odd = Relation.from_cnf(["x y z", "x -y -z", "-x y -z", "-x -y z"], xyz)
    even = Relation.from_cnf(["x y -z", "x -y z", "-x y z", "-x -y -z"], xyz)
    print("The original post: patterns, controllers and entwinement (INTUITIONS.md)")
    print("\nThe two patterns")
    show("solutions of (x∨y∨z)(x∨¬y∨¬z)(¬x∨y∨¬z)(¬x∨¬y∨z)", ", ".join(odd.table()), "001, 010, 100, 111")
    show("solutions of (x∨y∨¬z)(x∨¬y∨z)(¬x∨y∨z)(¬x∨¬y∨¬z)", ", ".join(even.table()), "000, 011, 101, 110")
    show("odd pattern, y and z when x = 0 / x = 1",
         " / ".join(", ".join(odd.restrict({"x": v}).table()) for v in (False, True)), "01, 10 / 00, 11")
    show("odd and even together have solutions", not Relation.from_cnf(
        ["x y z", "x -y -z", "-x y -z", "-x -y z", "x y -z", "x -y z", "-x y z", "-x -y -z"], xyz).is_empty(), False)

    print("\nControllers need three places")
    cube = [(a, b, c) for a in (False, True) for b in (False, True) for c in (False, True)]
    relations = [Relation(xyz, frozenset(row for i, row in enumerate(cube) if mask >> i & 1)) for mask in range(256)]
    show("in every odd or even pattern each variable decides whether the other two match",
         all(controls(r, v) for r in (odd, even) for v in xyz), True)
    show("of all 256 patterns on three variables, those with a controller are exactly those 2-CNF cannot define",
         all(any(controls(r, v) for v in xyz) == (not r.is_majority_closed()) for r in relations), True)
    show("when one variable is a controller, all three are",
         all(len({controls(r, v) for v in xyz}) == 1 for r in relations if r.rows), True)

    print("\nWhat a whole can hide from its parts")
    shapes = three_variable_shapes()
    show("patterns on three variables that are constrained but unconstrained in every pair",
         sum(count for _, count, _ in shapes), 34)
    show("shapes up to renaming and negation (excluded states: patterns)",
         ", ".join(f"{excluded}: {count}" for excluded, count, _ in shapes), "1: 8, 2: 4, 2: 12, 3: 8, 4: 2")
    show("least hidden: one clause, the atom (bits)", round(shapes[0][2], 3), 0.193)
    show("most hidden: the odd and even patterns (bits)", round(max(bits for *_, bits in shapes), 3), 1.0)
    show("no pattern on three variables hides more than 1 bit from its pairs",
         max(emergent_information(r) for r in relations if r.rows), 1.0)
    show("fewest states keeping every pair unconstrained, 3 to 5 variables",
         [fewest_states_hiding_pairs(n) for n in (3, 4, 5)], [4, 5, 6])

    print("\nPatterns of patterns")
    seven = ("x", "y", "z", "u", "v", "w", "c")
    matched = Relation.from_predicate(
        seven, lambda v: v["c"] == (((v["x"] + v["y"] + v["z"]) % 2 == 0) == ((v["u"] + v["v"] + v["w"]) % 2 == 1)))
    show("c = whether the even pattern on x,y,z matches the odd one on u,v,w is a parity on all 7",
         matched.equivalent(parity(seven, True)) or matched.equivalent(parity(seven, False)), True)
    show("and is unconstrained in every part of 6 variables", hides_from_parts(matched), True)
    sizes = []
    for n in (3, 4, 5, 6):
        names = tuple(f"x{i}" for i in range(1, n + 1))
        clauses, witnesses = parity_chain(names)
        assert Relation.from_cnf(clauses, names, witnesses).equivalent(parity(names))
        sizes.append(f"{n}: {2 ** (n - 1)} vs {len(clauses)}")
    show("parity on n variables, clauses using only the variables vs naming each partial match",
         "; ".join(sizes), "3: 4 vs 9; 4: 8 vs 13; 5: 16 vs 17; 6: 32 vs 21")

    print("\nTwo readings of erasing a loop, over all 256 patterns on (A, B, c)")
    abc = ("A", "B", "c")
    relations = [Relation(abc, r.rows) for r in relations]
    forgetting = [r for r in relations if entwines(r, ("A", "B"), "c", "forgetting")]
    absence = [r for r in relations if entwines(r, ("A", "B"), "c", "absence")]
    show("forgetting (the loop's variable becomes unconstrained): patterns that entwine", len(forgetting), 34)
    show("absence (the loop's value becomes 'absent'; K1–K3): patterns that entwine", len(absence), 2)
    hub = Relation.from_cnf(["-A c", "-B c"], abc)
    par = parity(abc, False)
    show("common hub entwines under either reading",
         entwines(hub, ("A", "B"), "c", "forgetting") or entwines(hub, ("A", "B"), "c", "absence"), False)
    show("parity entwines under forgetting / under absence",
         f"{YES[entwines(par, ('A', 'B'), 'c', 'forgetting')]} / {YES[entwines(par, ('A', 'B'), 'c', 'absence')]}", "yes / no")
    show("any pattern 2-CNF can define entwines under either reading",
         any(r.is_majority_closed() for r in forgetting + absence), False)

    print("\nall pattern checks match" if not mismatches else f"\n{mismatches} pattern checks did not match")
    return 1 if mismatches else 0


def presence() -> int:
    mismatches = 0

    def show(label: str, value: object, expected: object) -> None:
        nonlocal mismatches
        mismatches += value != expected
        text = YES[value] if isinstance(value, bool) else value
        print(f"  {label}: {text}" + ("" if value == expected else f"   [expected {expected}]"))

    print("Where a loop's presence comes from (ticket KNOT-FOUNDATION-20261019-001B)")
    print("\nStatic loops")
    show("an implication loop of 4 leaves this many states",
         loop_report(implication_loop(["x1", "x2", "x3", "x4"])).states, 2)
    cycle = Relation.from_cnf(["-A -X B", "-B -Y A"], ("A", "B", "X", "Y"))
    show("a cycle of atoms with both side inputs present allows",
         ", ".join(cycle.restrict({"X": True, "Y": True}).table()), "00, 11")
    show("an odd equal/unequal loop allows this many states",
         len(signed_loop(("x1", "x2", "x3"), (True, False, False)).rows), 0)
    print("  so a static loop is one free bit, and making a loop contradictory empties")
    print("  every system that contains it rather than erasing the loop")

    print("\nRings under an update: running (a cycle of length >= 2) or frozen")
    sizes = range(2, 8)
    show("copy rings of 2-7: running is conserved by the ring's own update",
         all(conserved(copy_ring, n) for n in sizes), True)
    show("copy rings of 2-7: comparing neighbors reads running exactly",
         all(reader_is_exact(n) for n in sizes), True)
    show("copy rings of 2-7: frozen states per ring (all 0s, all 1s)",
         {len(frozen_states(copy_ring, n)) for n in sizes}, {2})
    show("inverter rings of odd length: frozen states (it can never stop)",
         {len(frozen_states(inverter_ring, n)) for n in (3, 5, 7)}, {0})

    print("\nTwo copy rings and a contact, over every initial state")
    expected = {
        "latch": (True, True), "driven": (False, False),
        "hub": (False, False), "single point": (False, False),
    }
    for contact in CONTACTS:
        results = []
        for size_a, size_b in ((2, 2), (2, 3), (3, 3), (3, 4)):
            system = TwoLoops(size_a, size_b, contact)
            report = check_knot(system.relation(), ("A", "B"), "c", erasure="absence")
            results.append((report.is_knot, system.erasure_leaves_contact_free()))
        knot = all(value for value, _ in results)
        strict = all(value for _, value in results)
        show(f"{contact}: knot over computed presence for rings 2+2, 2+3, 3+3, 3+4", knot, expected[contact][0])
        show(f"{contact}: contact free whatever is left of a frozen ring", strict, expected[contact][1])
    print("  latch: c' = c or (both running); driven: c' = both running; hub: c' = c or")
    print("  either running; single point: c' = c or (a1 and b1), which a ring frozen at")
    print("  all 1s still drives, and which depends on the rings' relative phase")

    print("\nall presence checks match" if not mismatches else f"\n{mismatches} presence checks did not match")
    return 1 if mismatches else 0


def check(cnf: str, loops: Sequence[str], contact: str,
          witnesses: Sequence[str], as_json: bool, erasure: str = "forgetting") -> int:
    relation = Relation.from_cnf(parse_cnf(cnf), [*loops, contact], witnesses)
    report = check_knot(relation, loops, contact, erasure)
    if as_json:
        print(json.dumps({**report.as_dict(), "allowed": relation.table(),
                          "variables": list(relation.variables)}, indent=2, sort_keys=True))
        return 0
    print(f"allowed states of {' '.join(relation.variables)}: {', '.join(relation.table())}")
    print(f"erasure read as: {report.erasure}")
    print(f"K1 binding: {YES[report.binding]}")
    print(f"K2 loss on erasure: {YES[report.loss_on_erasure]}")
    print(f"K3 coexistence: {YES[report.coexistence]}")
    print(f"knot: {YES[report.is_knot]}")
    print(f"invisible in every smaller part: {YES[report.invisible_in_parts]}")
    print(f"definable by 2-CNF with witnesses: {YES[report.pairwise_definable]}")
    print(f"narrowest clause width without witnesses: {report.minimum_width}")
    for note in report.notes:
        print(f"note: {note}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="knotlab",
        description="Test logical-knot ideas: bound loops, erasure, witnesses "
                    "and the 2-CNF/3-CNF threshold.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="run the reference cases")
    commands.add_parser(
        "worlds", help="forced worlds, building from atoms, choice and infinite threads"
    )
    commands.add_parser("presence", help="where a loop's presence comes from")
    commands.add_parser(
        "patterns", help="the original post: controllers, hidden information and entwinement"
    )
    commands.add_parser("choice", help="whether the base logic has real alternatives")
    commands.add_parser("space", help="whether contact structure becomes space-like")
    commands.add_parser("competition", help="both readings of rules that cannot all hold")
    commands.add_parser("rings", help="which knots remember a loop")
    commands.add_parser("holonomy", help="what networks of permutation contact remember")
    commands.add_parser("depth", help="how deep a network's hole is")
    check_parser = commands.add_parser("check", help="test a CNF system")
    check_parser.add_argument(
        "--cnf", required=True,
        help='clauses separated by ";", negation with ~ or -, e.g. "~A ~B c"',
    )
    check_parser.add_argument("--loops", nargs="+", required=True)
    check_parser.add_argument("--contact", required=True)
    check_parser.add_argument("--witnesses", nargs="*", default=[])
    check_parser.add_argument("--json", action="store_true")
    check_parser.add_argument(
        "--erasure", choices=("forgetting", "absence"), default="forgetting",
        help="forgetting (canonical): an erased loop's variable is unconstrained; "
             "absence: the earlier reading, an erased loop's presence variable is false",
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            return demo()
        if args.command == "worlds":
            return worlds()
        if args.command == "presence":
            return presence()
        if args.command == "patterns":
            return patterns()
        if args.command == "choice":
            return choice()
        if args.command == "space":
            return space()
        if args.command == "competition":
            return competition()
        if args.command == "rings":
            return rings()
        if args.command == "holonomy":
            return holonomy()
        if args.command == "depth":
            return depth()
        return check(args.cnf, args.loops, args.contact, args.witnesses, args.json, args.erasure)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
