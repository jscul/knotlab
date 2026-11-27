"""Validate four-clause patterns by exact conditional queries on a finite stage."""

from functools import lru_cache
from itertools import combinations, product

from pysat.solvers import Solver


LOWER_POSITIONS = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))
SIX_WORDS = tuple(
    word for word in product((0, 1), repeat=6)
    if all(not all(word[index] for index in triple) for triple in LOWER_POSITIONS)
)


def _bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def _add_agreement(solver, agrees, variables):
    first, *rest = variables
    for other in rest:
        solver.add_clause([-agrees, -first, other])
        solver.add_clause([-agrees, first, -other])
    solver.add_clause([agrees, *variables])
    solver.add_clause([agrees, *(-variable for variable in variables)])


def _upper_word(word, both_pair):
    upper = 0
    for pair, first in enumerate((0, 2, 4)):
        left, right = word[first:first + 2]
        value = left & right if pair == both_pair else left | right
        upper = (upper << 1) | value
    return upper


def _varies_at_lower_bond(lower_positions, six_words, upper_words):
    seen = {}
    varies = 0
    for lower, upper in zip(six_words, upper_words, strict=True):
        key = tuple(lower[index] for index in lower_positions)
        varies |= upper ^ seen.setdefault(key, upper)
        if varies == 7:
            return True
    return False


def _qualifying_upper_image(six_words, both_pair):
    upper_words = [_upper_word(word, both_pair) for word in six_words]
    image = sorted(set(upper_words))
    if 7 in image:
        raise AssertionError("Four valid lower bonds exclude upper word 111")
    if any(len({word & mask for word in image}) != 4 for mask in (3, 5, 6)):
        return None
    if not all(_varies_at_lower_bond(positions, six_words, upper_words)
               for positions in LOWER_POSITIONS):
        return None
    return image


class StageChecks:
    """Test ordered not-all-equal supports and index their laws from zero.

    Carrier mask bit d refers to distinction d. A signed reading takes value
    one exactly when agreement on its carrier equals the supplied value.
    Laws at indices below n_start are from the start. The rest are births.
    """

    def __init__(self, supports, n_start):
        supports = tuple(tuple(map(int, support)) for support in supports)
        names = sorted({name for support in supports for name in support})
        if not 0 <= n_start <= len(supports):
            raise ValueError("The initial-law count must be within the number of supports")
        self.n_start = n_start
        self._all_distinctions = sum(1 << name for name in names)
        self._variables = {name: index for index, name in enumerate(names, 1)}
        self._size = len(names)
        laws = [tuple(self._variables[name] for name in support) for support in supports]
        self._law_masks = tuple(sum(1 << name for name in set(support)) for support in supports)

        self._stage = Solver()
        self._paired = Solver()
        self._law_ids = tuple(range(self._size + 1, self._size + len(laws) + 1))
        self._next_stage_var = self._size + len(laws) + 1
        self._next_paired_var = 3 * self._size + 1
        self._agreements = {}
        self._read_at_one = {}
        self._lower = lru_cache(maxsize=131_072)(self._check_lower)

        for law, selector in zip(laws, self._law_ids, strict=True):
            for sign in (1, -1):
                self._stage.add_clause([-selector, *(sign * variable for variable in law)])
                for offset in (0, self._size):
                    self._paired.add_clause([sign * (offset + variable) for variable in law])
        for left in self._variables.values():
            right = left + self._size
            same = left + 2 * self._size
            self._paired.add_clause([-same, -left, right])
            self._paired.add_clause([-same, left, -right])

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def close(self):
        self._lower.cache_clear()
        self._stage.delete()
        self._paired.delete()

    def _disjoint_carriers(self, readings):
        used = 0
        for mask, value in readings:
            if (mask <= 0 or mask.bit_count() not in (2, 3) or value not in (0, 1)
                    or mask & used or mask & ~self._all_distinctions):
                return False
            used |= mask
        return True

    def _literal(self, reading):
        mask, value = reading
        if mask not in self._agreements:
            variable = self._next_stage_var
            self._next_stage_var += 1
            carrier = tuple(self._variables[distinction] for distinction in _bits(mask))
            _add_agreement(self._stage, variable, carrier)
            self._agreements[mask] = variable
        variable = self._agreements[mask]
        return variable if value else -variable

    def _determined_at_one_knot(self, mask):
        if mask not in self._read_at_one:
            self._read_at_one[mask] = self._check_determination(mask)
        return self._read_at_one[mask]

    def _check_determination(self, mask):
        if any(mask & law == mask for law in self._law_masks):
            return True

        # An ordered pair of states with the same knot values and different
        # readings has a witness in either copy order, so test only one order.
        left, right = self._next_paired_var, self._next_paired_var + 1
        self._next_paired_var += 2
        carrier = tuple(self._variables[distinction] for distinction in _bits(mask))
        _add_agreement(self._paired, left, carrier)
        _add_agreement(self._paired, right, tuple(var + self._size for var in carrier))
        for law in self._law_masks:
            shared = [self._variables[distinction] + 2 * self._size for distinction in _bits(law)]
            if not self._paired.solve(assumptions=[left, -right, *shared]):
                return True
        return False

    def _can_read(self, literals, deleted=None):
        active = self._law_ids
        if deleted is not None:
            active = (*active[:deleted], -active[deleted], *active[deleted + 1:])
        return self._stage.solve(assumptions=[*active, *literals])

    def _check_lower(self, readings):
        literals = tuple(map(self._literal, readings))
        if self._can_read(literals):
            return False
        if any(self._determined_at_one_knot(mask) for mask, _ in readings):
            return False
        for word in product((0, 1), repeat=3):
            if word == (1, 1, 1):
                continue
            if not self._can_read([literal if bit else -literal
                                   for literal, bit in zip(literals, word, strict=True)]):
                return False
        return True

    def is_lower_bond(self, triple):
        """Require exactly seven words and variation at each individual knot."""
        readings = tuple(sorted(tuple(map(int, reading)) for reading in triple))
        if len(readings) != 3:
            raise ValueError("A lower bond must have three readings")
        return self._disjoint_carriers(readings) and self._lower(readings)

    def _deletions(self, literals, both_pair):
        choices = []
        for pair, first in enumerate((0, 2, 4)):
            left, right = literals[first:first + 2]
            choices.append(((left, right),) if pair == both_pair else ((left,), (right,)))
        witnesses = [tuple(literal for group in groups for literal in group)
                     for groups in product(*choices)]
        return [law for law in range(len(self._law_ids))
                if any(self._can_read(readings, deleted=law) for readings in witnesses)]

    def check(self, pattern, stop_first=True):
        """Return qualifying upper readings and single-law restorations of 111.

        Input is three ordered pairs of (carrier mask, excluded value). The
        four candidate bonds take member indices whose sum is even. Upper
        words are integers from 0 to 7 with the first pair as the high bit.
        """
        pairs = tuple(tuple(tuple(map(int, reading)) for reading in pair) for pair in pattern)
        if len(pairs) != 3 or any(len(pair) != 2 for pair in pairs):
            raise ValueError("A pattern must have three pairs of readings")
        readings = tuple(reading for pair in pairs for reading in pair)
        if not self._disjoint_carriers(readings):
            return []
        if not all(self.is_lower_bond(readings[index] for index in positions)
                   for positions in LOWER_POSITIONS):
            return []

        literals = tuple(map(self._literal, readings))
        six_words = [word for word in SIX_WORDS
                     if self._can_read([literal if bit else -literal
                                        for literal, bit in zip(literals, word, strict=True)])]
        result = []
        for both_pair in range(3):
            image = _qualifying_upper_image(six_words, both_pair)
            if image is None:
                continue
            deletions = self._deletions(literals, both_pair)
            result.append({
                "both_pair": both_pair,
                "upper_words": image,
                "initial_law_deletions": [law for law in deletions if law < self.n_start],
                "birth_law_deletions": [law for law in deletions if law >= self.n_start],
            })
            if stop_first:
                break
        return result
