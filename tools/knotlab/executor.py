"""Evaluation rules that supply inputs.

A guarded system gives each loop a guard: clauses that must hold for the loop
to continue. Read relationally, every guard always holds. Read with role
gating, a loop's guard is checked only while that loop runs, which quietly
adds the loop's own presence as an input. Comparing the two readings exposes
that leak.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .knots import KnotReport, check_knot
from .relations import Clause, Relation, as_clause, format_clause


@dataclass(frozen=True)
class GuardedSystem:
    loops: tuple[str, ...]
    contact: str
    guards: Mapping[str, tuple[str | Clause, ...]] = field(default_factory=dict)

    def effective_clauses(self, gated: bool) -> tuple[Clause, ...]:
        clauses: list[Clause] = []
        for loop in self.loops:
            for guard in self.guards.get(loop, ()):
                clause = as_clause(guard)
                if gated and (loop, False) not in clause:
                    clause = ((loop, False),) + clause
                clauses.append(clause)
        return tuple(clauses)

    def relation(self, gated: bool) -> Relation:
        return Relation.from_cnf(self.effective_clauses(gated), self.loops + (self.contact,))


@dataclass(frozen=True)
class LeakReport:
    relational: KnotReport
    gated: KnotReport
    leaks: bool
    widened: tuple[str, ...]


def leak_report(system: GuardedSystem) -> LeakReport:
    """Compare the relational and gated readings of a guarded system."""
    widened = tuple(
        f"{format_clause(as_clause(guard))}  becomes  "
        f"{format_clause(((loop, False),) + as_clause(guard))}"
        for loop in system.loops
        for guard in system.guards.get(loop, ())
        if (loop, False) not in as_clause(guard)
    )
    relational = system.relation(gated=False)
    gated = system.relation(gated=True)
    return LeakReport(
        relational=check_knot(relational, system.loops, system.contact),
        gated=check_knot(gated, system.loops, system.contact),
        leaks=relational.rows != gated.rows,
        widened=widened,
    )
