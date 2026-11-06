"""Forced worlds: what must exist when requirements only add things.

A rule says that a thing exists whenever all of its premises exist. The atom
is the rule with two premises, X ∧ Y → Z; rules with one premise or none are
allowed too. Given which things are present, the forced world is the least set
closed under the rules: everything required and nothing more. It is unique
because rules only ever add things, and propagation computes it in time
linear in the size of the rules.

Choice is different: a constraint such as c → A ∨ B can leave several
minimal worlds, none of them singled out by the constraints.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import combinations, product
from typing import Callable, Iterable, Sequence

from .relations import Clause, Relation


@dataclass(frozen=True)
class Rule:
    premises: frozenset[str]
    result: str


def atom(first: str, second: str, result: str) -> Rule:
    """The two-premise rule first ∧ second → result."""
    return Rule(frozenset((first, second)), result)


def forced_world(rules: Iterable[Rule], present: Iterable[str]) -> frozenset[str]:
    """Everything the rules require, given what is present, and nothing more."""
    rules = list(rules)
    waiting = [len(rule.premises) for rule in rules]
    watchers: dict[str, list[int]] = defaultdict(list)
    for index, rule in enumerate(rules):
        for premise in rule.premises:
            watchers[premise].append(index)
    known: set[str] = set()
    queue: deque[str] = deque()

    def add(thing: str) -> None:
        if thing not in known:
            known.add(thing)
            queue.append(thing)

    for thing in present:
        add(thing)
    for rule in rules:
        if not rule.premises:
            add(rule.result)
    while queue:
        for index in watchers.get(queue.popleft(), ()):
            waiting[index] -= 1
            if waiting[index] == 0:
                add(rules[index].result)
    return frozenset(known)


def essential(rules: Sequence[Rule], present: Sequence[str], target: str) -> frozenset[str]:
    """The present things whose erasure removes ``target`` from the forced world."""
    if target not in forced_world(rules, present):
        return frozenset()
    return frozenset(
        thing
        for thing in present
        if target not in forced_world(rules, [other for other in present if other != thing])
    )


def existence_profile(
    rules: Sequence[Rule], loops: Sequence[str], target: str
) -> dict[frozenset[str], bool]:
    """For every set of present loops, whether ``target`` exists."""
    return {
        frozenset(chosen): target in forced_world(rules, chosen)
        for size in range(len(loops) + 1)
        for chosen in combinations(loops, size)
    }


def knot_tree(depth: int, contact: str = "c") -> tuple[list[Rule], list[str]]:
    """Atoms joining 2**depth loops pairwise, level by level, into one contact."""
    if depth < 1:
        raise ValueError("a tree of knots needs at least two loops")
    loops = [f"L{index}" for index in range(2**depth)]
    rules: list[Rule] = []
    level, counter = loops, 0
    while len(level) > 1:
        joined = []
        for index in range(0, len(level), 2):
            counter += 1
            name = contact if len(level) == 2 else f"w{counter}"
            rules.append(atom(level[index], level[index + 1], name))
            joined.append(name)
        level = joined
    return rules, loops


def thread(length: int) -> tuple[list[Rule], list[str]]:
    """An open-ended chain: L1 ∧ L2 → w1, then wk ∧ L(k+2) → w(k+1)."""
    loops = [f"L{index}" for index in range(1, length + 2)]
    rules = [atom(loops[0], loops[1], "w1")]
    rules += [atom(f"w{k}", loops[k + 1], f"w{k + 1}") for k in range(1, length)]
    return rules, loops


def dual_rail_gate(
    x: str, y: str, z: str, function: Callable[[bool, bool], bool]
) -> list[Rule]:
    """Four atoms that make z = function(x, y), each bit carried on two rails.

    Bit x is present as "x=0" or "x=1"; there is one atom per input pair.
    """
    return [
        atom(f"{x}={int(a)}", f"{y}={int(b)}", f"{z}={int(function(a, b))}")
        for a, b in product((False, True), repeat=2)
    ]


def dual_rail_adder(bits: int) -> list[Rule]:
    """Atoms that add two numbers, each bit carried as which of two things exists.

    Bit i of a is present as "a{i}=0" or "a{i}=1"; the carry into bit 0 is
    "carry0=0". The forced world then contains exactly one of "s{i}=0" and
    "s{i}=1" for every sum bit, and one of "carry{bits}=0" and "carry{bits}=1".
    """
    rules: list[Rule] = []
    for i in range(bits):
        a0, a1, b0, b1 = f"a{i}=0", f"a{i}=1", f"b{i}=0", f"b{i}=1"
        t0, t1 = f"t{i}=0", f"t{i}=1"
        c0, c1 = f"carry{i}=0", f"carry{i}=1"
        rules += [
            atom(a1, b0, t1), atom(a0, b1, t1), atom(a0, b0, t0), atom(a1, b1, t0),
            atom(t1, c0, f"s{i}=1"), atom(t0, c1, f"s{i}=1"),
            atom(t0, c0, f"s{i}=0"), atom(t1, c1, f"s{i}=0"),
            atom(a1, b1, f"carry{i + 1}=1"), atom(t1, c1, f"carry{i + 1}=1"),
            atom(a0, b0, f"carry{i + 1}=0"), atom(t1, c0, f"carry{i + 1}=0"),
        ]
    return rules


def add_by_forced_world(first: int, second: int, bits: int) -> int:
    """Add two numbers by computing the forced world of the dual-rail adder."""
    present = [f"a{i}={first >> i & 1}" for i in range(bits)]
    present += [f"b{i}={second >> i & 1}" for i in range(bits)]
    world = forced_world(dual_rail_adder(bits), present + ["carry0=0"])
    total = 0
    for position, name in enumerate([f"s{i}" for i in range(bits)] + [f"carry{bits}"]):
        one, zero = f"{name}=1" in world, f"{name}=0" in world
        if one == zero:
            raise AssertionError(f"{name} is not determined exactly once")
        total |= one << position
    return total


def choices_reaching(
    rules: Sequence[Rule],
    distinctions: Sequence[tuple[str, str]],
    target: Iterable[str],
    given: Iterable[str] = (),
) -> list[frozenset[str]]:
    """Every way of making the open distinctions whose forced world holds ``target``.

    A distinction is a pair of alternatives of which exactly one is present.
    Checking one way is a forced world, computed in linear time; the number of
    ways doubles with every distinction left open.
    """
    target, given = frozenset(target), tuple(given)
    return [
        frozenset(picks)
        for picks in product(*distinctions)
        if target <= forced_world(rules, given + picks)
    ]


def from_atoms_and_distinctions(relation: Relation) -> Relation:
    """Rebuild a three-place relation from atoms and distinctions alone.

    Each excluded state becomes one atom ¬X ∨ ¬Y ∨ Z over the variables or
    their opposites, and each opposite v′ is tied to v by a distinction:
    exactly one of v and v′ exists. The opposites are witnesses.
    """
    if len(relation.variables) != 3:
        raise ValueError("this construction takes a relation on three variables")
    x, y, z = relation.variables
    opposite = {name: f"{name}′" for name in relation.variables}
    clauses: list[Clause] = []
    for a, b, c in relation.excluded():
        # Exclude (a, b, c) as: x = a and y = b force z ≠ c.
        first = x if a else opposite[x]
        second = y if b else opposite[y]
        result = opposite[z] if c else z
        clauses.append(((first, False), (second, False), (result, True)))
    for name in relation.variables:
        clauses += [((name, True), (opposite[name], True)),
                    ((name, False), (opposite[name], False))]
    return Relation.from_cnf(clauses, relation.variables, tuple(opposite.values()))


def minimal_worlds(relation: Relation) -> list[frozenset[str]]:
    """The allowed states that are minimal by inclusion of what is present."""
    states = [
        frozenset(name for name, value in zip(relation.variables, row) if value)
        for row in relation.rows
    ]
    return sorted(
        (state for state in states if not any(other < state for other in states)),
        key=sorted,
    )


def gate_relation(function: Callable[[bool, bool], bool]) -> Relation:
    """The three-place relation z = function(x, y) of a two-input gate."""
    return Relation.from_predicate(
        ("x", "y", "z"), lambda value: value["z"] == function(value["x"], value["y"])
    )
