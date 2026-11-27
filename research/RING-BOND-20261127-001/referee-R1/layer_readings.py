"""Exact finite tables for the referee's agreement-reading checks.

Bit s of a column gives that reading on the state numbered s. The raw
distinction of index j is bit j of the state number. Printed words list the
readings in their declared order, most significant first.
"""

from itertools import combinations


def truth_columns(arity):
    rows = 1 << arity
    universe = (1 << rows) - 1
    columns = []
    for j in range(arity):
        width = 1 << j
        pattern = ((1 << width) - 1) << width
        span = width * 2
        while span < rows:
            pattern |= pattern << span
            span *= 2
        columns.append(pattern)
    return universe, columns


def agreement(universe, columns):
    all_true = all_false = universe
    for column in columns:
        all_true &= column
        all_false &= ~column
    return all_true | all_false


def fibers(rows, columns):
    parts = [rows]
    for column in columns:
        parts = [child for part in parts for child in (part & ~column, part & column)]
    return parts


def occurring(rows, columns):
    return frozenset(i for i, group in enumerate(fibers(rows, columns)) if group)


def mixed_fibers(column, parts):
    """A positive count certifies two states of the same local values that disagree."""
    return sum(bool(group & column) and bool(group & ~column) for group in parts)


def candidates(rows, columns, knots):
    """Every pair/triple agreement left unread by each single listed knot."""
    local = [fibers(rows, [columns[i] for i in knot]) for knot in knots]
    choices = {}
    for size in (2, 3):
        for carrier in combinations(range(len(columns)), size):
            value = agreement(rows, [columns[i] for i in carrier])
            if value and rows & ~value and all(mixed_fibers(value, fixes) for fixes in local):
                choices[carrier] = value
    return choices


def bonds(rows, columns, knots):
    readings = candidates(rows, columns, knots)
    compatible = {carrier: set() for carrier in readings}
    for one, two in combinations(readings, 2):
        if set(one).isdisjoint(two) and len(occurring(rows, (readings[one], readings[two]))) == 4:
            compatible[one].add(two)
            compatible[two].add(one)
    result = {}
    for first, neighbours in compatible.items():
        for second in neighbours:
            if second <= first:
                continue
            for third in neighbours & compatible[second]:
                if third <= second:
                    continue
                selected = first, second, third
                values = [readings[c] for c in selected]
                missing = frozenset(range(8)) - occurring(rows, values)
                if missing:
                    result[selected] = missing
    return result, readings


def source_table(knots):
    universe, columns = truth_columns(1 + max(max(k) for k in knots))
    obey = [universe & ~agreement(universe, [columns[i] for i in k]) for k in knots]
    rows = universe
    for law in obey:
        rows &= law
    return universe, columns, obey, rows
