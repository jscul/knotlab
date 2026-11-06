"""Finite Boolean relations over named variables.

A relation is the set of allowed assignments of an ordered tuple of variables.
Clauses define one, with witness variables quantified away. Shadows, erasure,
majority closure, pairwise determination and clause width are all computed
from the allowed states, so no verdict depends on how the constraints were
written.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement, product
from typing import Callable, Iterable, Mapping, Sequence

Literal = tuple[str, bool]
Clause = tuple[Literal, ...]
NEGATIONS = "-~¬!"


def parse_clause(text: str) -> Clause:
    """Parse a clause such as ``"-A -B c"``; a leading -, ~, ¬ or ! negates."""
    literals: list[Literal] = []
    for token in text.replace(",", " ").split():
        negated = token[0] in NEGATIONS
        name = token[1:] if negated else token
        if not name:
            raise ValueError(f"empty literal in clause {text!r}")
        literals.append((name, not negated))
    if not literals:
        raise ValueError("a clause needs at least one literal")
    return tuple(literals)


def parse_cnf(text: str) -> tuple[Clause, ...]:
    """Parse clauses separated by semicolons or newlines."""
    parts = text.replace("\n", ";").split(";")
    return tuple(parse_clause(part) for part in parts if part.strip())


def as_clause(clause: str | Iterable[Literal]) -> Clause:
    return parse_clause(clause) if isinstance(clause, str) else tuple(clause)


def format_clause(clause: Clause) -> str:
    return " ∨ ".join(name if positive else f"¬{name}" for name, positive in clause)


def format_row(names: Sequence[str], row: Sequence[bool]) -> str:
    return ", ".join(f"{name}={int(value)}" for name, value in zip(names, row))


@dataclass(frozen=True)
class Relation:
    """The allowed assignments of an ordered tuple of variables."""

    variables: tuple[str, ...]
    rows: frozenset[tuple[bool, ...]]

    def __post_init__(self) -> None:
        if len(set(self.variables)) != len(self.variables):
            raise ValueError("variables must be distinct")

    @classmethod
    def from_predicate(
        cls,
        variables: Iterable[str],
        predicate: Callable[[dict[str, bool]], bool],
    ) -> Relation:
        names = tuple(variables)
        return cls(
            names,
            frozenset(
                row
                for row in product((False, True), repeat=len(names))
                if predicate(dict(zip(names, row)))
            ),
        )

    @classmethod
    def from_cnf(
        cls,
        clauses: Iterable[str | Iterable[Literal]],
        visible: Iterable[str],
        witnesses: Iterable[str] = (),
    ) -> Relation:
        """The allowed states of ``visible`` once the witnesses are quantified away."""
        parsed = tuple(as_clause(clause) for clause in clauses)
        shown = tuple(visible)
        names = shown + tuple(witnesses)
        if len(set(names)) != len(names):
            raise ValueError("visible and witness variables must be distinct")
        unknown = {name for clause in parsed for name, _ in clause} - set(names)
        if unknown:
            raise ValueError(f"undeclared variables: {', '.join(sorted(unknown))}")
        rows = set()
        for row in product((False, True), repeat=len(names)):
            assignment = dict(zip(names, row))
            if all(
                any(assignment[name] == positive for name, positive in clause)
                for clause in parsed
            ):
                rows.add(row[: len(shown)])
        return cls(shown, frozenset(rows))

    def _positions(self, names: Sequence[str]) -> list[int]:
        missing = [name for name in names if name not in self.variables]
        if missing:
            raise ValueError(f"unknown variables: {', '.join(missing)}")
        return [self.variables.index(name) for name in names]

    def project(self, keep: Sequence[str]) -> Relation:
        """The shadow of the relation on ``keep``."""
        positions = self._positions(keep)
        return Relation(
            tuple(keep),
            frozenset(tuple(row[i] for i in positions) for row in self.rows),
        )

    def restrict(self, values: Mapping[str, bool]) -> Relation:
        """Fix some variables, keep the agreeing rows, and drop those variables."""
        fixed = dict(zip(values, self._positions(list(values))))
        keep = [name for name in self.variables if name not in values]
        kept = self._positions(keep)
        return Relation(
            tuple(keep),
            frozenset(
                tuple(row[i] for i in kept)
                for row in self.rows
                if all(row[fixed[name]] == bool(value) for name, value in values.items())
            ),
        )

    def is_full(self) -> bool:
        return len(self.rows) == 2 ** len(self.variables)

    def is_empty(self) -> bool:
        return not self.rows

    def excluded(self) -> list[tuple[bool, ...]]:
        """The forbidden assignments, in a fixed order."""
        return sorted(set(product((False, True), repeat=len(self.variables))) - self.rows)

    def equivalent(self, other: Relation) -> bool:
        """Same variables and same allowed states, in any variable order."""
        if set(self.variables) != set(other.variables):
            return False
        return self.rows == other.project(self.variables).rows

    def is_and_closed(self) -> bool:
        """True exactly when requirements (Horn clauses) define the relation."""
        return all(
            tuple(a and b for a, b in zip(x, y)) in self.rows
            for x, y in combinations(self.rows, 2)
        )

    def is_majority_closed(self) -> bool:
        """True exactly when some 2-CNF with witnesses defines the relation."""
        for x, y, z in combinations_with_replacement(sorted(self.rows), 3):
            if tuple(a + b + c >= 2 for a, b, c in zip(x, y, z)) not in self.rows:
                return False
        return True

    def pairwise_closure(self) -> Relation:
        """Everything the relation's two-variable shadows allow together."""
        if len(self.variables) < 2:
            return self
        allowed = {
            (i, j): {(row[i], row[j]) for row in self.rows}
            for i, j in combinations(range(len(self.variables)), 2)
        }
        return Relation(
            self.variables,
            frozenset(
                row
                for row in product((False, True), repeat=len(self.variables))
                if all((row[i], row[j]) in pairs for (i, j), pairs in allowed.items())
            ),
        )

    def is_pairwise_determined(self) -> bool:
        return self.pairwise_closure().rows == self.rows

    def implied_clauses(self, max_width: int) -> list[Clause]:
        """Every clause of width at most ``max_width`` that all allowed states satisfy."""
        clauses: list[Clause] = []
        for width in range(1, max_width + 1):
            for names in combinations(self.variables, width):
                positions = self._positions(names)
                for signs in product((False, True), repeat=width):
                    if all(
                        any(row[i] == sign for i, sign in zip(positions, signs))
                        for row in self.rows
                    ):
                        clauses.append(tuple(zip(names, signs)))
        return clauses

    def minimum_width(self) -> int:
        """The narrowest clause width that defines the relation without witnesses."""
        if self.is_full():
            return 0
        for width in range(1, len(self.variables) + 1):
            defined = Relation.from_cnf(self.implied_clauses(width), self.variables)
            if defined.rows == self.rows:
                return width
        raise AssertionError("a relation is always defined by its full-width clauses")

    def table(self) -> list[str]:
        return [
            "".join(str(int(value)) for value in row) for row in sorted(self.rows)
        ]
