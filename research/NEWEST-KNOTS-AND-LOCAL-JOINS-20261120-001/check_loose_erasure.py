"""Exact pair-only certificate against the sole newest knot (8, 29, 30)."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import sys


def constant_mass(names, correlations):
    """Indicator of equality on two or three signs, averaged over their words."""
    assert len(names) in (2, 3)
    return (1 + sum(correlations[pair] for pair in combinations(names, 2))) / 2 ** (len(names) - 1)


def summarize(row):
    minimum = min(row.values())
    return {
        "minimum": str(minimum),
        "minimizers": [name for name, value in row.items() if value == minimum],
        "value_counts": {str(value): count for value, count in sorted(Counter(row.values()).items())},
    }


def main(path):
    raw = path.read_bytes()
    rates = [Fraction(entry) for entry in json.loads(raw)]
    pairs = list(combinations(range(31), 2))
    assert len(rates) == len(pairs)
    correlations = {pair: 1 - 2 * rate for pair, rate in zip(pairs, rates)}

    def row(name, carrier):
        return {other: correlations[tuple(sorted((name, other)))] for other in carrier if other != name}

    older = range(29)
    row_eight = row(8, older)
    min_eight = min(row_eight.values())
    companions = tuple(name for name, value in row_eight.items() if value == min_eight)
    assert companions == (3, 5, 6, 7)
    q = -min_eight
    proper_masses = {
        group: constant_mass(group, correlations)
        for size in (2, 3) for group in combinations(companions, size)
    }
    assert min(proper_masses.values()) > q

    remainder = [name for name in older if name != 8]
    row_five = row(5, remainder)
    erased = {name: (value - row_eight[name]) / (1 + q) for name, value in row_five.items()}
    targets = (23, 24, 25)
    erased_minimum = min(erased.values())
    inherited_minimum = min(row_five.values())
    assert tuple(name for name, value in erased.items() if value == erased_minimum) == targets
    assert tuple(name for name, value in row_five.items() if value == inherited_minimum) == targets
    triple_mass = constant_mass(targets, correlations)
    uniform_lower = triple_mass / (1 + q)
    assert uniform_lower > -erased_minimum and triple_mass > -inherited_minimum
    return {
        "input_sha256": sha256(raw).hexdigest(),
        "assumed_current_sole_newest": [8, 29, 30],
        "old_loose_name": 8,
        "old_row_eight": summarize(row_eight),
        "forced_companion_set": list(companions),
        "constant_mass_required_by_eight": str(q),
        "all_proper_eligible_companion_constant_masses": {
            ",".join(map(str, group)): str(mass) for group, mass in proper_masses.items()
        },
        "test_triple": list(targets),
        "observed_triple_constant_mass": str(triple_mass),
        "uniform_founder": {
            "row_after_erasing_eights_holder": summarize(erased),
            "constant_mass_required_for_actual_companions": str(-erased_minimum),
            "lower_bound_for_test_triple_constant_mass": str(uniform_lower),
            "excess": str(uniform_lower + erased_minimum),
        },
        "positive_age_predecessor": {
            "preceding_inherited_row": summarize(row_five),
            "constant_mass_required_for_actual_companions": str(-inherited_minimum),
            "observed_test_triple_constant_mass": str(triple_mass),
            "excess": str(triple_mass + inherited_minimum),
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(Path(sys.argv[1])), indent=2))
