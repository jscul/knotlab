"""Loops written with 2-clauses, and what remains of them.

An implication loop forces every member to be equal, and a loop of
equal/unequal steps either collapses to one free bit or contradicts itself.
So a 2-clause loop has no interior beyond a single bit. Whether two of its
points show equal (00/11) or unequal (01/10) values is information about its
interior that can be read from outside: a witness.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import log2
from typing import Sequence

from .relations import Clause, Relation


def implication_loop(names: Sequence[str]) -> Relation:
    """x1 → x2 → … → xn → x1."""
    clauses: list[Clause] = [
        ((names[i], False), (names[(i + 1) % len(names)], True))
        for i in range(len(names))
    ]
    return Relation.from_cnf(clauses, names)


def signed_loop(names: Sequence[str], unequal: Sequence[bool]) -> Relation:
    """Step i joins names[i] and the next name as equal, or unequal if marked."""
    if len(unequal) != len(names):
        raise ValueError("give one step per loop member")
    clauses: list[Clause] = []
    for i, step in enumerate(unequal):
        x, y = names[i], names[(i + 1) % len(names)]
        if step:
            clauses += [((x, True), (y, True)), ((x, False), (y, False))]
        else:
            clauses += [((x, False), (y, True)), ((x, True), (y, False))]
    return Relation.from_cnf(clauses, names)


def signature(relation: Relation, first: str, second: str) -> frozenset[str]:
    """Which of "equal" (00/11) and "unequal" (01/10) the two points can show."""
    pair = relation.project([first, second])
    return frozenset("equal" if a == b else "unequal" for a, b in pair.rows)


@dataclass(frozen=True)
class LoopReport:
    states: int
    free_bits: float | None
    collapsed: bool
    contradictory: bool


def loop_report(relation: Relation) -> LoopReport:
    """How much of a loop survives: its states, free bits, and whether it collapsed."""
    if relation.is_empty():
        return LoopReport(0, None, True, True)
    collapsed = all(
        len(signature(relation, first, second)) == 1
        for first, second in combinations(relation.variables, 2)
    )
    return LoopReport(len(relation.rows), log2(len(relation.rows)), collapsed, False)
