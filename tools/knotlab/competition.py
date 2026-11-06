"""Knots from competition (epic KNOT-COMPETITION-20261019-001).

When a system's rules cannot all hold, it has two readings:

- strict: it allows the states that break no rule;
- competition: it allows the states that break the fewest.

The readings agree whenever some state breaks no rule. Rules on pairs never
make a knot under the strict reading. Under competition, on their own
variables, they make exactly one kind: the not-all-equal triangle, a loop of
preferences that cannot close (KNOT-COMPETITION-20261019-001A-P001). On a
strip or ring of triangles counted per triangle, competition equals strict
not-all-equal knots on the triangles. Separation then grows along the layout
(KNOT-COMPETITION-20261019-001B-E002).

Separation of a pair is the size of the smallest bond or tie containing it
(INTUITIONS.md, "Does contact structure become space-like?").
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product
from typing import Sequence

from .patterns import hides_from_parts
from .relations import Relation
from .space import bonds, ties

READINGS = ("strict", "competition")

#: A preference on a pair: (first, second, differ). With differ False the pair should agree.
Preference = tuple[str, str, bool]


def allowed_states(
    variables: Sequence[str],
    preferences: Sequence[Preference],
    reading: str = "competition",
    weights: Sequence[int] | None = None,
) -> Relation:
    """The states that agree-or-differ preferences allow under a reading."""
    if reading not in READINGS:
        raise ValueError(f"reading must be one of {READINGS}")
    names = tuple(variables)
    weights = list(weights) if weights is not None else [1] * len(preferences)
    if len(weights) != len(preferences):
        raise ValueError("one weight per preference")
    position = {name: i for i, name in enumerate(names)}
    pairs = [(position[a], position[b], differ) for a, b, differ in preferences]
    states = list(product((False, True), repeat=len(names)))
    costs = [sum(w for (i, j, differ), w in zip(pairs, weights) if (s[i] != s[j]) != differ) for s in states]
    target = 0 if reading == "strict" else min(costs)
    return Relation(names, frozenset(s for s, c in zip(states, costs) if c == target))


def triangle(
    differ: tuple[bool, bool, bool] = (True, True, True),
    weights: tuple[int, int, int] = (1, 1, 1),
    reading: str = "competition",
) -> Relation:
    """A triangle of preferences on x, y and z: the pairs xy, xz and yz."""
    preferences = [("x", "y", differ[0]), ("x", "z", differ[1]), ("y", "z", differ[2])]
    return allowed_states(("x", "y", "z"), preferences, reading, weights)


def least_set_knot(relation: Relation) -> bool:
    """Whether a knot is the least set of some function that is a sum of terms on pairs.

    By KNOT-COMPETITION-20261019-001A-P001 this happens only on three variables, and
    there exactly when the two excluded states are opposite (not-all-equal up to renaming).
    """
    if not hides_from_parts(relation):
        raise ValueError("least_set_knot takes a knot")
    excluded = relation.excluded()
    return (len(relation.variables) == 3 and len(excluded) == 2
            and all(a != b for a, b in zip(*excluded)))


def separation(relation: Relation) -> dict[frozenset[str], int]:
    """For each pair inside some bond or tie, the size of the smallest one containing it."""
    out: dict[frozenset[str], int] = {}
    for group in list(bonds(relation)) + list(ties(relation)):
        for pair in combinations(sorted(group), 2):
            key = frozenset(pair)
            out[key] = min(out.get(key, len(group)), len(group))
    return out


def separation_levels(relation: Relation) -> list[int]:
    """The distinct separations: near and far needs at least two."""
    return sorted(set(separation(relation).values()))


def triangle_strip(n: int, per_triangle: bool = True, ring: bool = False) -> Relation:
    """Competition on a strip (or ring) of triangles whose pairs should all differ.

    Counted per triangle, each pair weighs the number of triangles containing it;
    counted per pair, each broken pair costs one.
    """
    if n < (4 if ring else 3):
        raise ValueError("a strip needs three variables and a ring four")
    names = tuple(f"v{i}" for i in range(n))
    count: Counter = Counter()
    for i in range(n if ring else n - 2):
        for a, b in combinations((i % n, (i + 1) % n, (i + 2) % n), 2):
            count[tuple(sorted((a, b)))] += 1
    preferences = [(names[a], names[b], True) for a, b in count]
    weights = [count[key] if per_triangle else 1 for key in count]
    return allowed_states(names, preferences, "competition", weights)
