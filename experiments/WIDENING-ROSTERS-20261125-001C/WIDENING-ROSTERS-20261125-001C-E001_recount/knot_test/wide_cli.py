"""Run the canonical CLI with exact faster table construction for visible CNFs."""

import json
import sys

from knotlab import cli
from knotlab.relations import Relation, as_clause


class VisibleRelation(Relation):
    @classmethod
    def from_cnf(cls, clauses, visible, witnesses=()):
        names = tuple(visible)
        witnesses = tuple(witnesses)
        parsed = tuple(as_clause(clause) for clause in clauses)
        if witnesses or len(set(names)) != len(names):
            return Relation.from_cnf(parsed, names, witnesses)
        positions = {name: 1 << i for i, name in enumerate(names)}
        if any(name not in positions for clause in parsed for name, _ in clause):
            return Relation.from_cnf(parsed, names)
        full = (1 << len(names)) - 1
        allowed = bytearray([1]) * (full + 1)
        for clause in parsed:
            zero = one = 0
            for name, positive in clause:
                if positive:
                    zero |= positions[name]
                else:
                    one |= positions[name]
            if zero & one:
                continue  # A tautological clause has no falsifying assignments.
            free = full ^ (zero | one)
            extension = free
            while True:
                allowed[one | extension] = 0
                if not extension:
                    break
                extension = (extension - 1) & free
        return cls(names, frozenset(
            tuple(bool(word & positions[name]) for name in names)
            for word, value in enumerate(allowed) if value
        ))

    def minimum_width(self):
        if self.is_full():
            return 0
        if all(
            self.project([name for name in self.variables if name != dropped]).is_full()
            for dropped in self.variables
        ):
            # Every proper subset is free, so no shorter clause is implied.
            # One full-width clause per excluded word defines the relation.
            return len(self.variables)
        return super().minimum_width()


if __name__ == "__main__":
    # The CLI's check_knot call, projection, K1–K3 tests, and output stay
    # unchanged. The substitute supplies the same allowed rows and width.
    cli.Relation = VisibleRelation
    raise SystemExit(cli.main(json.load(sys.stdin)))
