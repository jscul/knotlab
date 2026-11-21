"""Check the cost of forcing a second zero at singly held names in a residual NAE system."""
from collections import Counter
from itertools import combinations
import json


def reductions(width):
    """List all distinct rules of arity at least three, using each name at most twice."""
    possible = [
        sum(1 << place for place in places)
        for size in range(3, width + 1)
        for places in combinations(range(width), size)
    ]

    def extend(start, used, used_twice, rules):
        yield rules, used_twice
        for index in range(start, len(possible)):
            rule = possible[index]
            if rule & used_twice:
                continue
            yield from extend(
                index + 1, used | rule, used_twice | (used & rule), (*rules, rule)
            )

    yield from extend(0, 0, 0, ())


def allowed_words(width, rules):
    return [
        word for word in range(1 << width)
        if all((word & rule) not in (0, rule) for rule in rules)
    ]


def check_pins(pinned_zeros, single_names, words):
    completions = [word for word in words if not (word & pinned_zeros)]
    if not completions:
        return None
    can_be_one = 0
    for word in completions:
        can_be_one |= word
    forced = single_names & ~pinned_zeros & ~can_be_one
    assert 4 * forced.bit_count() <= pinned_zeros.bit_count()
    return forced, len(completions)


def run():
    census = []
    for width in range(3, 7):
        count = Counter()
        all_names = (1 << width) - 1
        for rules, used_twice in reductions(width):
            single_names = all_names ^ used_twice  # Includes names unused after deletion.
            words = allowed_words(width, rules)
            pins = single_names
            while True:
                result = check_pins(pins, single_names, words)
                count["pin_sets"] += 1
                if result is None:
                    count["infeasible_pin_sets"] += 1
                else:
                    count["feasible_pin_sets"] += 1
                    count["nonempty_new_zero_sets"] += bool(result[0])
                if pins == 0:
                    break
                pins = (pins - 1) & single_names
            count["systems"] += 1
        census.append(dict(width=width, **count))

    # Each copy uses four pinned zeros to force two ones and then one further zero.
    sharp = []
    for copies in (1, 2):
        rules = []
        pins = single_names = expected = 0
        for copy in range(copies):
            shift = 7 * copy
            rules.extend(rule << shift for rule in (0b0010011, 0b0101100, 0b1110000))
            pins |= 0b0001111 << shift
            single_names |= 0b1001111 << shift
            expected |= 0b1000000 << shift
        forced, total = check_pins(pins, single_names, allowed_words(7 * copies, rules))
        assert forced == expected
        sharp.append(dict(
            initial_zeros=pins.bit_count(), further_forced_zeros=forced.bit_count(),
            remaining_completions=total,
        ))
    return dict(reduced_singly_held_controls=census, sharp_ternary_witnesses=sharp)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
