"""Whether the base logic has real alternatives (ticket KNOT-FOUNDATION-20261019-001C).

Under the forgetting reading a knot leaves every one of its variables open, so
alternatives come with emergence: a knot is a constraint on how open
distinctions combine, never a selection among them. Whether a knot reads as a
requirement ("A and B require c") or as a choice ("c requires A or B")
depends only on which value counts as 'exists', and the forgetting reading
privileges neither value.
"""

from __future__ import annotations

from itertools import product
from typing import Iterable, Mapping

from .patterns import hides_from_parts
from .relations import Relation
from .worlds import minimal_worlds

ABC = ("A", "B", "c")


def two_loop_knots() -> list[Relation]:
    """The 34 knots on two loops A, B and a contact c."""
    cube = list(product((False, True), repeat=3))
    relations = (
        Relation(ABC, frozenset(row for i, row in enumerate(cube) if mask >> i & 1))
        for mask in range(256)
    )
    return [relation for relation in relations if hides_from_parts(relation)]


def negate(relation: Relation, names: Iterable[str]) -> Relation:
    """The same relation with the named variables' values swapped."""
    names = set(names)
    flips = tuple(name in names for name in relation.variables)
    return Relation(
        relation.variables,
        frozenset(tuple(value != flip for value, flip in zip(row, flips)) for row in relation.rows),
    )


def open_variables(relation: Relation) -> list[str]:
    """The variables that take both values among the allowed states."""
    return [
        name for index, name in enumerate(relation.variables)
        if len({row[index] for row in relation.rows}) == 2
    ]


def is_or_closed(relation: Relation) -> bool:
    """Closed under OR: what requirements read with the other value as 'exists' define."""
    return all(
        tuple(a or b for a, b in zip(x, y)) in relation.rows
        for x in relation.rows for y in relation.rows
    )


def worlds_given(
    relation: Relation, given: Mapping[str, bool], exists: bool = True
) -> list[frozenset[str]]:
    """The minimal worlds that agree with ``given``.

    A world is the set of variables that exist in an allowed state; with
    exists=False the value false counts as existing. Minimal worlds are the
    ones that contain nothing beyond what the constraints require.
    """
    narrowed = Relation(
        relation.variables,
        frozenset(
            row for row in relation.rows
            if all(row[relation.variables.index(name)] == value for name, value in given.items())
        ),
    )
    if not exists:
        narrowed = negate(narrowed, narrowed.variables)
    return minimal_worlds(narrowed)
