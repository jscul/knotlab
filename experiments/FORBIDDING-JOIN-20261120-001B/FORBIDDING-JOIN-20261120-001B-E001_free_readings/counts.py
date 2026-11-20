"""Exact support and weighting of a single possibly forbidding transition."""

from functools import cache
from math import prod

from exact_counts import Birth, Factor, NotAllEqualSupport, Parity, eliminate


def names(supports):
    return tuple(sorted({bit for support in supports for bit in support}))


def nae_factor(support):
    return Factor.from_function(support, lambda word: int("0" in word and "1" in word))


class StageCounts:
    def __init__(self, law, old, stage):
        self.law = law
        self.old_bits = names(old)
        self.bits = names(stage)
        self.supports = stage
        if law == "parity":
            self.recoding = {bit: i for i, bit in enumerate(self.bits)}
            self.linear = Parity(tuple(self._dense(support) for support in stage))
        else:
            old_set = set(self.old_bits)
            births = [Birth(tuple(bit for bit in support if bit in old_set),
                            tuple(bit for bit in support if bit not in old_set)) for support in stage[len(old):]]
            self.zero_fresh = [birth.consumed for birth in births if not birth.fresh]
            self.base = [nae_factor(support) for support in (*old, *self.zero_fresh)]
            self.positive_births = [birth for birth in births if birth.fresh]

    def _dense(self, marks):
        return tuple(self.recoding[bit] for bit in marks)

    @cache
    def retained(self):
        if self.law == "parity":
            rows = self.linear.projected_rows(self._dense(self.old_bits))
            return 1 << (len(self.old_bits) - len(rows))
        return eliminate(self.base, self.old_bits, ())[0][0]

    @cache
    def histogram(self, marks, weighting):
        if self.law == "parity":
            mass = self.linear.histogram(self._dense(marks))
            unit = self.linear.total // self.retained() if weighting == "L" else 1
            return mass, unit
        marked = set(marks)
        parts = [birth.factor(tuple(sorted(marked.intersection(birth.fresh))), weighting)
                 for birth in self.positive_births]
        factors = self.base + [factor for factor, _ in parts if factor is not None]
        mass, _ = eliminate(factors, set(self.old_bits) | marked, marks)
        return mass, prod(scale for _, scale in parts)

    @cache
    def total(self):
        return self.histogram((), "U")[0][0]

    def certify(self):
        if self.law == "nae":
            with NotAllEqualSupport(self.supports) as solver:
                assert solver.solver.solve() == bool(self.total())
                return [solver.certificate(support) for support in self.supports]
        certificates = []
        for support in self.supports:
            row = self.linear.certificate(self._dense(support))
            row["projected_equations"] = [tuple(bit for i, bit in enumerate(self.bits) if (equation >> i) & 1)
                                          for equation in row["projected_equations"]]
            certificates.append(row)
        return certificates

    def initial_survivors(self, initial):
        if self.law == "parity":
            return 1 << (len(initial) - len(self.linear.projected_rows(self._dense(initial))))
        # The only second transitions in this study have 9 or 10 initial distinctions.
        with NotAllEqualSupport(self.supports) as solver:
            return sum(solver.solver.solve(assumptions=[(bit + 1) if (word >> i) & 1 else -bit - 1
                                                       for i, bit in enumerate(initial)])
                       for word in range(1 << len(initial)))
