"""Exact allowed relations on the places of one support."""

from dataclasses import dataclass
from functools import cache


@dataclass(frozen=True)
class Projection:
    width: int
    kind: str
    data: tuple[int, ...] = ()

    def allows(self, word):
        if self.kind == "nae":
            return word not in (0, (1 << self.width) - 1)
        if self.kind == "even_groups":
            return all((word & group).bit_count() % 2 == 0 for group in self.data)
        return word in self.data

    def count(self):
        if self.kind == "nae":
            return (1 << self.width) - 2
        if self.kind == "even_groups":
            return 1 << (self.width - len(self.data))
        return len(self.data)

    def same_relation(self, other):
        if self == other:
            return True
        if self.width != other.width or self.count() != other.count():
            return False
        if self.kind == "table":
            return all(other.allows(word) for word in self.data)
        if other.kind == "table":
            return all(self.allows(word) for word in other.data)
        # In the parity form, each two-one word identifies a pair belonging
        # to the same group, so distinct partitions give distinct relations.
        return False

    def canonical_form(self):
        """An equivalent relation under a renaming of the places."""
        if self.kind != "even_groups":
            return self
        groups = []
        start = 0
        for size in sorted(mask.bit_count() for mask in self.data):
            groups.append(((1 << size) - 1) << start)
            start += size
        return Projection(self.width, self.kind, tuple(groups))

    def report(self):
        count = self.count()
        binding = count < 1 << self.width
        coexistence = count != 0
        if self.kind == "nae":
            loss = self.width >= 2
        elif self.kind == "even_groups":
            loss = len(self.data) == 1
        else:
            # K2 asks for the full projection after forgetting EACH place.
            for i in range(self.width):
                low = (1 << i) - 1
                shadow = {(word & low) | ((word >> (i + 1)) << i) for word in self.data}
                if len(shadow) != 1 << (self.width - 1):
                    loss = False
                    break
            else:
                loss = True
        return {
            "binding": binding,
            "loss_on_erasure": loss,
            "coexistence": coexistence,
            "is_knot": self.width >= 3 and binding and loss and coexistence,
            "eligible_arity": self.width >= 3,
            "allowed_count": count,
        }

    def spec(self):
        return {"width": self.width, "kind": self.kind, "data": self.data}

    @staticmethod
    def from_spec(spec):
        return Projection(spec["width"], spec["kind"], tuple(spec["data"]))


@cache
def own_relation(width, law):
    if law == "nae":
        return Projection(width, "nae")
    if law == "parity":
        return Projection(width, "even_groups", ((1 << width) - 1,))
    raise ValueError(f"unknown knot law: {law}")


class ExactSolver:
    """Resolve exceptional relations by querying every locally possible word."""

    def __init__(self, supports, distinctions, law, backend):
        from pysat.solvers import Solver

        self.law = law
        self.solver = Solver(name=backend)
        self.calls = 0
        next_var = distinctions + 1
        for support in supports:
            variables = [d + 1 for d in support]
            if law == "nae":
                self.solver.add_clause(variables)
                self.solver.add_clause([-d for d in variables])
                continue
            if len(variables) == 1:
                self.solver.add_clause([-variables[0]])
                continue
            running = variables[0]
            for step in variables[1:-1]:
                result = next_var
                next_var += 1
                self.solver.add_clause([running, step, -result])
                self.solver.add_clause([running, -step, result])
                self.solver.add_clause([-running, step, result])
                self.solver.add_clause([-running, -step, -result])
                running = result
            last = variables[-1]
            self.solver.add_clause([-running, last])
            self.solver.add_clause([running, -last])

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.solver.delete()

    def projection(self, support):
        width = len(support)
        own = own_relation(width, self.law)
        allowed = []
        for word in range(1 << width):
            if not own.allows(word):
                continue   # The target rule is a conjunct.
            assumptions = [
                d + 1 if word & (1 << i) else -d - 1 for i, d in enumerate(support)
            ]
            self.calls += 1
            if self.solver.solve(assumptions=assumptions):
                allowed.append(word)
        if len(allowed) == own.count():
            return own
        return Projection(width, "table", tuple(allowed))
