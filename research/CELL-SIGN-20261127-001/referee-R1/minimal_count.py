"""Independently enumerate strict choices from the earlier reconstructed holdings."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path
import resource
from time import monotonic

from minimal_measure import cross_pair, interleaves, steps


HERE = Path(__file__).resolve().parent
INPUT = HERE.parents[1] / "READER-SPLIT-20261127-001/referee-R1/rebuilt_inputs.jsonl"


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


@dataclass
class ChoiceCode:
    cycles: list
    columns: list
    checks: list
    used_values: list
    disjoint: list
    cost: int
    dimension: int
    usable: int


def reduce_column(column, pivots):
    while column:
        lead = column.bit_length()
        if lead not in pivots:
            break
        column ^= pivots[lead]
    return column


def relation_support(columns):
    pivots = {}
    usable = 0
    for i, column in enumerate(columns):
        word = 1 << i
        while column:
            lead = column.bit_length()
            if lead not in pivots:
                pivots[lead] = column, word
                break
            other, route = pivots[lead]
            column ^= other
            word ^= route
        else:
            # These returned words span the nullspace, so a column absent
            # from their union cannot occur in any commuting choice.
            usable |= word
    return len(columns) - len(pivots), usable


def reconstruct(source):
    holders = defaultdict(list)
    for knot, values in enumerate(source["supports"]):
        for value in values:
            holders[value].append(knot)
    assert all(len(knots) == 2 for knots in holders.values())
    knots = len(source["supports"])
    pairs = {pair: k for k, pair in enumerate(combinations(range(knots), 2))}
    cycles = []
    columns = []
    values_in_column = []
    at_value = defaultdict(int)
    checks = [0] * len(pairs)
    cost = 0
    for index, (x, y) in enumerate(source["pairs"]):
        a, b = holders[x]
        c, d = holders[y]
        cycle = (a, c, b, d)
        assert len(set(cycle)) == 4
        cycles.append(cycle)
        rows = [pairs[cross_pair(u, v)] for u, v in steps(cycle)]
        columns.append(sum(1 << row for row in rows))
        for row in rows:
            checks[row] |= 1 << index
        cost |= interleaves(cycle) << index
        values_in_column.append((1 << x) | (1 << y))
        at_value[x] |= 1 << index
        at_value[y] |= 1 << index
    dimension, usable = relation_support(columns)
    assert (checks, cost, dimension) == (source["checks"], source["cost"], source["dimension"])
    disjoint = [usable & ~(at_value[x] | at_value[y]) for x, y in source["pairs"]]
    return ChoiceCode(cycles, columns, checks, values_in_column, disjoint, cost, dimension, usable)


def minimal_words(code, maximum):
    """Find every strict inclusion-minimal nonempty commuting word through maximum."""
    by_column = defaultdict(int)
    for i in bits(code.usable):
        by_column[code.columns[i]] |= 1 << i
    circuits = []
    pivots = {}

    def visit(word, remaining, syndrome, room):
        if room == 1:
            for i in bits(remaining & by_column.get(syndrome, 0)):
                circuits.append(word | (1 << i))
            return
        if syndrome.bit_count() > 4 * room:
            return

        # An uncovered odd cross pair must occur again. Partition completions
        # by the first still-available failing pair they use at that cross pair.
        smallest = remaining.bit_count() + 1
        candidates = 0
        for row in bits(syndrome):
            present = code.checks[row] & remaining
            count = present.bit_count()
            if not count:
                return
            if count < smallest:
                smallest = count
                candidates = present
        while candidates:
            bit = candidates & -candidates
            i = bit.bit_length() - 1
            candidates ^= bit
            remaining ^= bit
            next_syndrome = syndrome ^ code.columns[i]
            if not next_syndrome:
                # The existing columns are independent, so their sum can
                # close only a minimal commuting collection.
                circuits.append(word | bit)
                continue
            if next_syndrome.bit_count() > 4 * (room - 1):
                continue
            reduced = reduce_column(code.columns[i], pivots)
            if reduced:
                # A dependent proper subset cannot extend to a minimal word.
                lead = reduced.bit_length()
                pivots[lead] = reduced
                visit(word | bit, remaining & code.disjoint[i], next_syndrome, room - 1)
                del pivots[lead]

    if maximum < 2:
        return []
    remaining = code.usable
    for first in bits(code.usable):
        bit = 1 << first
        remaining ^= bit
        column = code.columns[first]
        pivots[column.bit_length()] = column
        visit(bit, remaining & code.disjoint[first], column, maximum - 1)
        pivots.clear()
    assert len(circuits) == len(set(circuits))
    return sorted(circuits, key=lambda word: (word.bit_count(), word))


def all_words(code, circuits, maximum):
    """A strict commuting word is a disjoint union of strict minimal words."""
    entries = [
        (word, word.bit_count(), sum(code.used_values[i] for i in bits(word)))
        for word in circuits
    ]
    words = set(circuits)

    def extend(start, word, values, room):
        for i in range(start, len(entries)):
            new, size, used = entries[i]
            if size > room:
                break
            if values & used:
                continue
            union = word | new
            # Alternate minimal partitions can yield the same union.
            words.add(union)
            extend(i + 1, union, values | used, room - size)

    for i, (word, size, used) in enumerate(entries):
        extend(i + 1, word, used, maximum - size)
    return words


def raw_counts(words, cost):
    return Counter((word.bit_count(), (word & cost).bit_count() % 2) for word in words)


def sources():
    with INPUT.open() as stream:
        yield from map(json.loads, stream)


def pilot(ids, maximum):
    for source in sources():
        key = source["population"], source["key"]
        if key not in ids:
            continue
        start = monotonic()
        code = reconstruct(source)
        circuits = minimal_words(code, maximum)
        time_circuits = monotonic() - start
        raw = all_words(code, circuits, maximum)
        print(key, len(code.columns), code.dimension, raw_counts(circuits, code.cost),
              raw_counts(raw, code.cost), round(time_circuits, 3), round(monotonic() - start, 3),
              resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", nargs="+", required=True, help="Population and key joined by a colon.")
    parser.add_argument("--maximum", type=int, default=8)
    args = parser.parse_args()
    ids = {(population, int(key)) for population, key in (label.split(":") for label in args.pilot)}
    pilot(ids, args.maximum)
