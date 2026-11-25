"""Two workload-specific exact routes to whole-stage Boolean projections."""

from itertools import combinations
from functools import cache


class NaeProjection:
    def __init__(self):
        from pysat.solvers import Solver

        self.solver = Solver(name="minisat22")
        self.calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.solver.delete()

    def add(self, supports):
        for support in supports:
            row = [d + 1 for d in support]
            self.solver.add_clause(row)
            self.solver.add_clause([-d for d in row])

    def project(self, variables):
        width = len(variables)
        full_word = (1 << width) - 1
        result = 0
        for word in range(1 << (width - 1)):
            assumptions = [
                d + 1 if word >> (width - i - 1) & 1 else -d - 1
                for i, d in enumerate(variables)
            ]
            self.calls += 1
            if self.solver.solve(assumptions=assumptions):
                result |= (1 << word) | (1 << (full_word ^ word))
        return result


class ParityProjection:
    """Project by finding every dual equation supported on the chosen places."""

    def __init__(self):
        self.pivots = {}
        self.cache = {}
        self.calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def reduce(self, support):
        row = set(support)
        while row:
            pivot = max(row)
            prior = self.pivots.get(pivot)
            if prior is None:
                break
            row.symmetric_difference_update(prior)
        return row

    def add(self, supports):
        self.cache.clear()
        for support in supports:
            row = self.reduce(support)
            if row:
                self.pivots[max(row)] = frozenset(row)

    def implied(self, support):
        key = tuple(sorted(support))
        if key not in self.cache:
            self.calls += 1
            self.cache[key] = not self.reduce(key)
        return self.cache[key]

    def project(self, variables):
        width = len(variables)
        equations = []
        for size in range(1, width + 1):
            for positions in combinations(range(width), size):
                if self.implied(variables[i] for i in positions):
                    equations.append(sum(1 << (width - i - 1) for i in positions))
        return sum(
            1 << word for word in range(1 << width)
            if all(not ((word & equation).bit_count() % 2) for equation in equations)
        )


def ordered_mask(variables, by_order):
    """Reorder a cached projection on the increasing tuple of distinction IDs."""
    ordered = tuple(sorted(variables))
    mask = by_order[ordered]
    if ordered == variables or mask in (0, (1 << (1 << len(variables))) - 1):
        return mask
    return permute_mask(mask, tuple(ordered.index(d) for d in variables))


@cache
def permute_mask(mask, order):
    width = len(order)
    result = 0
    for word in range(1 << width):
        if mask >> word & 1:
            renamed = sum(
                (word >> (width - old - 1) & 1) << (width - new - 1)
                for new, old in enumerate(order)
            )
            result |= 1 << renamed
    return result
