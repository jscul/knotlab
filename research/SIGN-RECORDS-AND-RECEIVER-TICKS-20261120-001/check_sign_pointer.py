"""Check the two preparation histories by following the ordinary pointer in both directions.

The coordinates are the two marks each of the data, memory, witness, and
reader, followed by three prepared marks. The instructions are the six
conditional swaps in study A. Run directly with Python's standard library.
"""
import json
from fractions import Fraction
from itertools import product


HOLDINGS = ((0, 1, 8), (0, 1, 2, 3), (2, 3, 4, 5, 6, 7, 9), (6, 7, 10))
# First coordinate of the pair to exchange, and the mark enabling the exchange.
SWAPS = {"F": (0, None), "C": (2, 0), "P": (6, 2),
         "L": (4, 2), "V": (6, 4), "B": (0, 2)}


def prepared_word(data, memory=0, witness=0, reader=0):
    return (data, 1-data, memory, 1-memory, witness, 1-witness, reader, 1-reader, 1, 1, 1)


def apply_swap(word, instruction):
    first, control = SWAPS[instruction]
    if control is not None and not word[control]:
        return word
    marks = list(word)
    marks[first], marks[first+1] = marks[first+1], marks[first]
    return tuple(marks)


def allowed(word, law):
    for holding in HOLDINGS:
        ones = sum(word[i] for i in holding)
        if law == "parity" and ones % 2:
            return False
        if law == "not-all-equal" and ones in (0, len(holding)):
            return False
    return True


def initial_event(support, event, instructions):
    for instruction in reversed(instructions):
        event = {word for word in support if apply_swap(word, instruction) in event}
    return event


def chance(event, preparation):
    return str(Fraction(sum(word in event for word in preparation), len(preparation)))


def inner(left, right):
    return sum(value * right.get(word, 0) for word, value in left.items())


def two_signs(columns, scale_squared=1):
    diagonal = sum(inner(column, column) for column in columns)
    cross = 2 * inner(*columns)
    return [str(Fraction(diagonal + sign*cross, 2*scale_squared)) for sign in (1, -1)]


def check(law):
    support = {word for word in product(range(2), repeat=11) if allowed(word, law)}
    for instruction in SWAPS:
        assert {apply_swap(word, instruction) for word in support} == support
    event = {word for word in support if word[6]}
    fixed = [prepared_word(data) for data in (0, 1)]
    fair = [prepared_word(data, memory) for data, memory in product(range(2), repeat=2)]
    assert set(fair) <= support
    results = {}
    for name, history in [("adjacent", "FFCC"), ("alternating", "FCFC")]:
        ordinary_chance = chance(initial_event(support, event, history+"P"), fixed)
        columns = []
        for word in fixed:
            for instruction in history+"P":
                word = apply_swap(word, instruction)
            columns.append({word: 1} if word in event else {})
        observed = two_signs(columns)
        assert observed == [ordinary_chance, ordinary_chance]
        results[name] = {
            "clean_register": ordinary_chance,
            "independently_signed_pointer": observed,
            "fair_without_copy": chance(initial_event(support, event, history+"PV"), fair),
            "fair_with_copy": chance(initial_event(support, event, "L"+history+"PV"), fair),
        }

    # In the supplied sum-and-difference comparison, the two input basis words
    # both contribute 1/sqrt(2) at this one output. Keep that common scale exact.
    marked_word = prepared_word(0, reader=1)
    results["supplied_sum_and_difference"] = two_signs([{marked_word: 1}]*2, scale_squared=2)
    return {"unconditioned_physical_words": len(support), "results": results}


if __name__ == "__main__":
    print(json.dumps({law: check(law) for law in ("parity", "not-all-equal")}, indent=2))
