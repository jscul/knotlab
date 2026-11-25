"""Second exact whole-stage projection for a meeting's retained distinctions."""

from functools import lru_cache
from random import Random


@lru_cache(maxsize=3)
def even_tables(width):
    states = range(1 << width)
    return [sum(1 << state for state in states if not (state & subset).bit_count() % 2)
            for subset in states]


class ParityProjector:
    def __init__(self, supports):
        basis = {}
        for support in supports:
            row = sum(1 << distinction for distinction in support)
            while row:
                pivot = row.bit_length() - 1
                if pivot not in basis:
                    basis[pivot] = row ^ (1 << pivot)
                    break
                row ^= basis[pivot] | (1 << pivot)

        size = max((d for support in supports for d in support), default=-1) + 1
        self.coordinates = []
        for distinction in range(size):
            if distinction not in basis:
                self.coordinates.append(1 << distinction)
                continue
            value = 0
            lower = basis[distinction]
            while lower:
                bit = lower & -lower
                value ^= self.coordinates[bit.bit_length() - 1]
                lower ^= bit
            self.coordinates.append(value)
        self.project = lru_cache(maxsize=65536)(self.compute)

    def compute(self, targets):
        width = len(targets)
        coefficient = [self.coordinates[target] for target in reversed(targets)]
        masks = even_tables(width)
        result = masks[0]
        combinations = [0]
        for subset in range(1, len(masks)):
            bit = subset & -subset
            combination = combinations[subset ^ bit] ^ coefficient[bit.bit_length() - 1]
            combinations.append(combination)
            if not combination:
                result &= masks[subset]
        return result

    def close(self):
        self.project.cache_clear()


def forward_completions(supports, start_count, choices=128):
    """Build actual NAE witnesses in parallel, even if a prefix has a birth with no fresh distinction."""
    generator = Random(20261125)
    all_choices = (1 << choices) - 1
    values = {}
    valid = all_choices
    for knot, support in enumerate(supports):
        fresh = []
        for distinction in support:
            if distinction not in values:
                values[distinction] = generator.getrandbits(choices)
                fresh.append(distinction)
        if not support:
            valid = 0
            continue
        ones = all_choices
        zeros = all_choices
        for distinction in support:
            value = values[distinction]
            ones &= value
            zeros &= all_choices ^ value
        monochromatic = ones | zeros
        if knot >= start_count and fresh and len(support) >= 2:
            values[fresh[-1]] ^= monochromatic
        else:
            valid &= ~monochromatic
    return valid, values


class NAEProjector:
    def __init__(self, supports, start_count):
        self.valid, self.values = forward_completions(supports, start_count)
        self.supports = supports
        self.solver = None
        self.cached = {}
        self.witnessed_pairs = 0
        self.sat_queries = 0

    def project(self, targets):
        if targets in self.cached:
            return self.cached[targets]
        state_count = 1 << len(targets)
        last = self.values[targets[-1]]
        normalized = [self.values[target] ^ last for target in targets[:-1]]
        result = 0
        for state in range(0, state_count, 2):
            remaining = self.valid
            for bit, ones in enumerate(reversed(normalized), 1):
                remaining &= ones if state & (1 << bit) else ~ones
            if remaining:
                self.witnessed_pairs += 1
            elif not self.solve(targets, state):
                continue
            result |= (1 << state) | (1 << (state_count - 1 - state))
        self.cached[targets] = result
        return result

    def solve(self, targets, state):
        if self.solver is None:
            from pysat.solvers import Minisat22

            self.solver = Minisat22()
            for support in self.supports:
                clause = [distinction + 1 for distinction in support]
                self.solver.add_clause(clause)
                self.solver.add_clause([-literal for literal in clause])
        self.sat_queries += 1
        width = len(targets)
        return self.solver.solve(assumptions=[
            (target + 1) if state & (1 << (width - 1 - index)) else -(target + 1)
            for index, target in enumerate(targets)
        ])

    def close(self):
        if self.solver is not None:
            self.solver.delete()
            self.solver = None


def shadows(triple):
    ab = ac = bc = 0
    for state in range(8):
        if triple & (1 << state):
            ab |= 1 << (state >> 1)
            ac |= 1 << ((state >> 1) & 2 | state & 1)
            bc |= 1 << (state & 3)
    return ab, ac, bc


@lru_cache(maxsize=256)
def read_projection(triple):
    ab, ac, bc = shadows(triple)
    factored = sum(1 << state for state in range(8)
                   if ac & (1 << ((state >> 1) & 2 | state & 1))
                   and bc & (1 << (state & 3))) == triple
    if triple == 0:
        kind = 'empty'
    elif triple == 255:
        kind = 'free'
    elif ab == ac == bc == 15:
        kind = 'joint'
    elif factored and ac != 15 and bc != 15:
        all_open = all(any(triple & (1 << state) for state in range(8) if bool(state & bit) == yes)
                       for bit in (1, 2, 4) for yes in (False, True))
        kind = 'two_sided_factor' if all_open else 'degenerate_factor'
    elif factored:
        kind = 'one_sided_factor'
    else:
        kind = 'other_constraint'
    return ab, ac, bc, factored, kind
