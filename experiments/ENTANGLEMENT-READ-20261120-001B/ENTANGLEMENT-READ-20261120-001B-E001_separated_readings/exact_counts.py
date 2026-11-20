"""Integer model counts for the initial and first grown presentations."""

from dataclasses import dataclass
from math import prod

import numpy as np
from pysat.solvers import Minisat22


def mask(distinctions):
    return sum(1 << bit for bit in distinctions)


def boolean_words(width):
    return [format(value, f"0{width}b") for value in range(1 << width)] if width else [""]


class Parity:
    def __init__(self, supports):
        self.nbits = 1 + max(map(max, supports))
        self.rows = tuple(map(mask, supports))
        self.rank = len(self._basis(0))
        self.total = 1 << (self.nbits - self.rank)

    def _basis(self, keep):
        basis = {}
        for row in self.rows:
            while row:
                pivot = (row & ~keep or row).bit_length() - 1
                if pivot not in basis:
                    basis[pivot] = row
                    break
                row ^= basis[pivot]
        return basis

    def projected_rows(self, marks):
        keep = mask(marks)
        return tuple(row for row in self._basis(keep).values() if not row & ~keep)

    def histogram(self, marks):
        rows = self.projected_rows(marks)
        count = self.total >> (len(marks) - len(rows))
        result = []
        for word in boolean_words(len(marks)):
            assignment = mask(bit for bit, value in zip(marks, word, strict=True) if value == "1")
            result.append(count if all((row & assignment).bit_count() % 2 == 0 for row in rows) else 0)
        return result

    def certificate(self, support):
        rows = self.projected_rows(support)
        full_law = rows == (mask(support),)
        return {
            "projected_count": 1 << (len(support) - len(rows)),
            "expected_count": 1 << (len(support) - 1),
            "full_law": full_law,
            "k1": bool(rows),
            "k2": full_law or not rows,
            "k3": True,
            "eligible": len(support) >= 3 and full_law,
            "projected_equations": list(rows),
        }


class NotAllEqualSupport:
    def __init__(self, supports):
        self.solver = Minisat22()
        for support in supports:
            self.solver.add_clause([bit + 1 for bit in support])
            self.solver.add_clause([-bit - 1 for bit in support])

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.solver.delete()

    def certificate(self, support):
        width = len(support)
        full = (1 << width) - 1
        positive = []
        # Global complementation pairs each pattern with a pattern starting with the opposite bit.
        for word in range(1, 1 << (width - 1)):
            pins = [(bit + 1) if (word >> i) & 1 else (-bit - 1) for i, bit in enumerate(support)]
            if self.solver.solve(assumptions=pins):
                positive.extend((word, word ^ full))
        k2 = all(len({word & ~(1 << i) for word in positive}) == 1 << (width - 1) for i in range(width))
        full_law = len(positive) == (1 << width) - 2
        return {
            "projected_count": len(positive),
            "expected_count": (1 << width) - 2,
            "full_law": full_law,
            "k1": len(positive) < 1 << width,
            "k2": k2,
            "k3": bool(positive),
            "eligible": width >= 3 and full_law and k2 and bool(positive),
            "projected_patterns": sorted(positive),
        }


@dataclass(frozen=True)
class Factor:
    scope: tuple
    values: np.ndarray

    @classmethod
    def from_function(cls, scope, evaluate):
        scope = tuple(sorted(scope))
        values = [evaluate(word) for word in boolean_words(len(scope))]
        return cls(scope, np.asarray(values, dtype=object).reshape((2,) * len(scope)))


def product(factors, scope):
    values = np.ones((2,) * len(scope), dtype=object)
    for factor in factors:
        shape = tuple(2 if bit in factor.scope else 1 for bit in scope)
        values *= factor.values.reshape(shape)
    return values


def eliminate(factors, universe, marks):
    """Sum unmarked distinctions, using integer object arrays throughout."""
    factors = list(factors)
    peak = max((len(factor.scope) for factor in factors), default=0)
    remaining = set(universe) - set(marks)
    while remaining:
        scopes = {bit: set() for bit in remaining}
        for factor in factors:
            for bit in remaining.intersection(factor.scope):
                scopes[bit].update(factor.scope)
        bit = min(remaining, key=lambda value: (len(scopes[value]), value))
        bucket = [factor for factor in factors if bit in factor.scope]
        factors = [factor for factor in factors if bit not in factor.scope]
        scope = tuple(sorted(scopes[bit]))
        if scope:
            peak = max(peak, len(scope))
            values = product(bucket, scope).sum(axis=scope.index(bit))
        else:
            values = 2
        factors.append(Factor(tuple(d for d in scope if d != bit), np.asarray(values, dtype=object)))
        remaining.remove(bit)

    retained = tuple(sorted(marks))
    values = product(factors, retained).transpose(tuple(retained.index(bit) for bit in marks))
    return [int(value) for value in values.flat], peak


@dataclass(frozen=True)
class Birth:
    consumed: tuple
    fresh: tuple

    def factor(self, selected, weighting):
        # A birth's consumed distinctions predate all its fresh distinctions. Since all chosen
        # parents are distinct, this factor has one input for each consumed distinction.
        fresh_count = len(self.fresh)
        marked = len(selected)
        scope = self.consumed + selected
        different_old = 1 << fresh_count
        same_old = different_old - 1
        free = 1 << (fresh_count - marked)
        if weighting == "L" and not marked:
            return None, 1
        scale = different_old * same_old if weighting == "L" else 1
        assert self.consumed and fresh_count, "the NAE growth lemma requires a fresh distinction"

        def value(word):
            old = word[:len(self.consumed)]
            old_equal = old == old[0] * len(old)
            one_bad_completion = old_equal and word[len(old):] == old[0] * marked
            count = free - int(one_bad_completion)
            if weighting == "L":
                count *= scale // (same_old if old_equal else different_old)
            return count

        return Factor.from_function(scope, value), scale


class NotAllEqual:
    def __init__(self, old_supports, supports):
        self.old_nbits = 1 + max(map(max, old_supports))
        self.old_factors = [Factor.from_function(support, lambda word: int("0" in word and "1" in word))
                            for support in old_supports]
        self.births = [Birth(tuple(bit for bit in support if bit < self.old_nbits),
                             tuple(bit for bit in support if bit >= self.old_nbits))
                       for support in supports[len(old_supports):]]

    def histogram(self, marks, weighting):
        requested = set(marks)
        extras = [birth.factor(tuple(sorted(requested.intersection(birth.fresh))), weighting)
                  for birth in self.births]
        factors = self.old_factors + [factor for factor, _ in extras if factor is not None]
        units_per_state = prod(scale for _, scale in extras)
        universe = set(range(self.old_nbits)) | requested
        histogram, peak = eliminate(factors, universe, marks)
        return histogram, units_per_state, peak
