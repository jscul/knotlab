"""Whether contact structure becomes space-like (ticket KNOT-FOUNDATION-20261019-001D).

A system's contact structure is read from its allowed states alone:

- a set of variables is *free* when the system allows every assignment of it;
  the free sets form a simplicial complex, the system's *shape*;
- a *bond* is a set of three or more variables that the system constrains
  while every smaller part is free: a knot inside the system;
- a *tie* is a constrained pair whose variables are each free.

A single knot is a hollow simplex in its shape: the two-loop knot is a circle.
In the language of learning theory, free sets are the sets a family of
assignments shatters, and bonds are the minimal sets of three or more that it
does not shatter.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterable, Sequence

from .patterns import hides_from_parts
from .relations import Relation


def free_sets(relation: Relation) -> list[frozenset[str]]:
    """Every set of variables whose assignments the relation all allows."""
    names = relation.variables
    return [
        frozenset(chosen)
        for size in range(len(names) + 1)
        for chosen in combinations(names, size)
        if relation.project(list(chosen)).is_full()
    ]


def bonds(relation: Relation) -> list[frozenset[str]]:
    """The knots inside the relation: constrained sets of three or more with free parts."""
    names = relation.variables
    return [
        frozenset(chosen)
        for size in range(3, len(names) + 1)
        for chosen in combinations(names, size)
        if hides_from_parts(relation.project(list(chosen)))
    ]


def ties(relation: Relation) -> list[frozenset[str]]:
    """Constrained pairs whose two variables are each free."""
    names = relation.variables
    return [
        frozenset(pair)
        for pair in combinations(names, 2)
        if not relation.project(list(pair)).is_full()
        and all(relation.project([name]).is_full() for name in pair)
    ]


def homology(faces: Iterable[frozenset[str]]) -> dict[int, int]:
    """Reduced Betti numbers over GF(2) of a simplicial complex given by all its faces.

    The empty face counts in dimension -1, so a single point has no reduced
    homology, two points have one 0-dimensional class, a circle one
    1-dimensional class, and so on.
    """
    by_dimension: dict[int, list[tuple[str, ...]]] = {}
    for face in faces:
        by_dimension.setdefault(len(face) - 1, []).append(tuple(sorted(face)))
    index = {d: {face: i for i, face in enumerate(fs)} for d, fs in by_dimension.items()}
    top = max(by_dimension)

    def rank(rows: list[int]) -> int:
        basis: dict[int, int] = {}
        for row in rows:
            while row:
                lead = row.bit_length() - 1
                if lead in basis:
                    row ^= basis[lead]
                else:
                    basis[lead] = row
                    break
        return len(basis)

    ranks = {}
    for d in range(0, top + 1):
        rows = []
        for face in by_dimension.get(d, []):
            mask = 0
            for vertex in face:
                mask |= 1 << index[d - 1][tuple(v for v in face if v != vertex)]
            rows.append(mask)
        ranks[d] = rank(rows)
    betti = {
        d: len(by_dimension.get(d, [])) - ranks.get(d, 0) - ranks.get(d + 1, 0)
        for d in range(-1, top + 1)
    }
    return {d: value for d, value in betti.items() if value}


def complex_relation(variables: Sequence[str], faces: Iterable[frozenset[str]]) -> Relation:
    """The relation whose allowed states are the indicator vectors of the faces."""
    names = tuple(variables)
    return Relation(names, frozenset(tuple(name in face for name in names) for face in faces))


def compose(first: Relation, second: Relation) -> Relation:
    """Two bonds that share exactly one variable, with the shared variable forgotten."""
    shared = set(first.variables) & set(second.variables)
    if len(shared) != 1:
        raise ValueError("compose takes two relations that share exactly one variable")
    names = tuple(dict.fromkeys(first.variables + second.variables))
    joined = Relation.from_predicate(
        names,
        lambda value: tuple(value[n] for n in first.variables) in first.rows
        and tuple(value[n] for n in second.variables) in second.rows,
    )
    return joined.project([name for name in names if name not in shared])


def smallest_bond(relation: Relation, first: str, second: str) -> int | None:
    """The size of the smallest bond containing both variables, if any."""
    sizes = [len(bond) for bond in bonds(relation) if first in bond and second in bond]
    return min(sizes) if sizes else None
