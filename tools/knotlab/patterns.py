"""Patterns, controllers and entwinement: the question that started the program.

A pattern is a relation: the joint states it allows, for example the
solutions of a CNF. The information a pattern holds is what it rules out.
Emergent information is what the whole rules out that no smaller part does.

A variable *controls* two others when fixing it changes how those two relate,
beyond restricting each of them separately: in the odd pattern
x xor y xor z = 1, x = 1 makes y and z match and x = 0 makes them differ.
Controllers need three places. Every relation definable by 2-CNF, even with
witnesses, is determined by its pairs, so fixing one variable can only
restrict the others one at a time.
"""

from __future__ import annotations

from itertools import combinations, permutations, product
from math import log2
from typing import Iterable, Sequence

from .knots import check_knot
from .relations import Clause, Literal, Relation, as_clause


def information(relation: Relation) -> float:
    """Bits the pattern rules out: the number of variables minus log2 of its states."""
    if relation.is_empty():
        raise ValueError("an empty pattern rules out everything")
    return len(relation.variables) - log2(len(relation.rows))


def emergent_information(relation: Relation) -> float:
    """Bits the pattern rules out that its two-variable shadows do not."""
    if relation.is_empty():
        raise ValueError("an empty pattern rules out everything")
    return log2(len(relation.pairwise_closure().rows) / len(relation.rows))


def hides_from_parts(relation: Relation) -> bool:
    """Constrained as a whole while every shadow on fewer variables is unconstrained."""
    if relation.is_full() or relation.is_empty():
        return False
    names = relation.variables
    return all(
        relation.project([name for name in names if name != left_out]).is_full()
        for left_out in names
    )


def co_information(relation: Relation, kind: str = "shannon") -> float:
    """Co-information of a three-variable relation: negative means synergy.

    kind="shannon" uses the uniform distribution over the allowed states;
    kind="hartley" counts possibilities, log2 of the number of allowed values.
    I(x;y;z) = H(x)+H(y)+H(z) - H(x,y) - H(x,z) - H(y,z) + H(x,y,z).
    """
    if len(relation.variables) != 3 or relation.is_empty():
        raise ValueError("co_information takes a nonempty relation on three variables")
    rows = sorted(relation.rows)

    def entropy(positions: tuple[int, ...]) -> float:
        counts: dict[tuple[bool, ...], int] = {}
        for row in rows:
            key = tuple(row[i] for i in positions)
            counts[key] = counts.get(key, 0) + 1
        if kind == "hartley":
            return log2(len(counts))
        if kind != "shannon":
            raise ValueError(f"unknown kind {kind!r}")
        return -sum(c / len(rows) * log2(c / len(rows)) for c in counts.values())

    singles = sum(entropy((i,)) for i in range(3))
    pairs = sum(entropy(pair) for pair in ((0, 1), (0, 2), (1, 2)))
    return singles - pairs + entropy((0, 1, 2))


def least_violation(
    clauses: Iterable[str | Iterable[Literal]],
    visible: Sequence[str],
    witnesses: Sequence[str] = (),
) -> Relation:
    """The states of ``visible`` that break as few clauses as possible.

    Conjunction allows the states that break none. Competition allows the
    states that break the fewest, so a frustrated system, whose clauses cannot
    all hold, still allows something. Witnesses are quantified away after the
    count, as in ``Relation.from_cnf``.
    """
    parsed = tuple(as_clause(clause) for clause in clauses)
    shown = tuple(visible)
    names = shown + tuple(witnesses)
    unknown = {name for clause in parsed for name, _ in clause} - set(names)
    if unknown:
        raise ValueError(f"undeclared variables: {', '.join(sorted(unknown))}")
    fewest, rows = None, set()
    for row in product((False, True), repeat=len(names)):
        value = dict(zip(names, row))
        broken = sum(not any(value[name] == positive for name, positive in clause) for clause in parsed)
        if fewest is None or broken < fewest:
            fewest, rows = broken, {row[: len(shown)]}
        elif broken == fewest:
            rows.add(row[: len(shown)])
    return Relation(shown, frozenset(rows))


def controls(relation: Relation, variable: str) -> bool:
    """Whether fixing ``variable`` changes how the other two variables relate.

    The relation must have exactly three variables. Fixing the variable to a
    value allows some (y, z) pairs; the variable controls the pair when those
    are not just the pairs of the (y, z) shadow whose parts are each allowed.
    """
    if len(relation.variables) != 3:
        raise ValueError("controls takes a relation on three variables")
    others = [name for name in relation.variables if name != variable]
    shadow = relation.project(others).rows
    for value in (False, True):
        fixed = relation.restrict({variable: value})
        first = {row[0] for row in fixed.rows}
        second = {row[1] for row in fixed.rows}
        separate = {(y, z) for y, z in shadow if y in first and z in second}
        if separate != set(fixed.rows):
            return True
    return False


def parity(names: Sequence[str], odd: bool = True) -> Relation:
    """The pattern 'an odd (or even) number of the variables are true'."""
    return Relation.from_predicate(names, lambda value: (sum(value[n] for n in names) % 2 == 1) == odd)


def parity_chain(names: Sequence[str], odd: bool = True) -> tuple[list[Clause], list[str]]:
    """Parity in clauses of at most three literals, naming each partial match.

    Witness a1 says whether x1 and x2 differ, a2 whether a1 and x3 differ, and
    so on; the last witness is fixed. This is the 'represent the pattern as a
    new variable' step repeated.
    """
    if len(names) < 2:
        raise ValueError("parity of fewer than two variables is a unit clause")
    clauses: list[Clause] = []
    witnesses: list[str] = []
    previous = names[0]
    for index, name in enumerate(names[1:], start=1):
        out = f"a{index}"
        clauses += [
            ((out, False), (previous, True), (name, True)),
            ((out, False), (previous, False), (name, False)),
            ((out, True), (previous, False), (name, True)),
            ((out, True), (previous, True), (name, False)),
        ]
        witnesses.append(out)
        previous = out
    clauses.append(((previous, odd),))
    return clauses, witnesses


def entwines(relation: Relation, loops: Sequence[str], contact: str, erasure: str) -> bool:
    """Whether the relation binds the loops through the contact.

    erasure="forgetting": erasing a loop removes it, so its variable becomes
    unconstrained. The loops are entwined when the whole is constrained and
    forgetting any one variable leaves the rest unconstrained.
    This is the canonical K1-K3 test (check_knot's default).
    erasure="absence": the earlier reading; a loop's variable is its presence
    and erasing it sets it to absent.
    """
    if set(relation.variables) != {*loops, contact} or len(relation.variables) != len(loops) + 1:
        raise ValueError("the relation must be over exactly the loops and the contact")
    if erasure == "forgetting":
        return hides_from_parts(relation)
    if erasure == "absence":
        return check_knot(relation, loops, contact, erasure="absence").is_knot
    raise ValueError(f"unknown erasure reading {erasure!r}")


def three_variable_shapes() -> list[tuple[int, int, float]]:
    """The patterns on three variables that hide everything from their pairs.

    Grouped under renaming and negating variables. Each entry is
    (excluded states, number of patterns, emergent bits), least to most.
    """
    names = ("x", "y", "z")
    cube = list(product((False, True), repeat=3))
    classes: dict[tuple, list[Relation]] = {}
    for mask in range(256):
        relation = Relation(names, frozenset(row for i, row in enumerate(cube) if mask >> i & 1))
        if not hides_from_parts(relation):
            continue
        key = min(
            tuple(sorted(tuple(row[order[i]] ^ flips[i] for i in range(3)) for row in relation.rows))
            for order in permutations(range(3))
            for flips in product((False, True), repeat=3)
        )
        classes.setdefault(key, []).append(relation)
    shapes = [
        (8 - len(members[0].rows), len(members), emergent_information(members[0]))
        for members in classes.values()
    ]
    return sorted(shapes)


def fewest_states_hiding_pairs(size: int) -> int:
    """The fewest states of a pattern on ``size`` variables with every pair unconstrained."""
    cube = list(product((0, 1), repeat=size))
    for count in range(1, len(cube) + 1):
        for rows in combinations(cube, count):
            if all(len({(row[i], row[j]) for row in rows}) == 4
                   for i, j in combinations(range(size), 2)):
                return count
    raise AssertionError("the full cube hides nothing")
