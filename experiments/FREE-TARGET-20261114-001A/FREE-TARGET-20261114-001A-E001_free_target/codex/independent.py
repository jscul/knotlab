"""Gate (a): tuple enumeration and set-valued products, independently coded.

This module imports neither the production relation code nor its algebra.
Only the required, already-flattened input block and usual-limit G are read.
"""
from __future__ import annotations

from itertools import product


def derive(prep, dropped_side=None):
    flat = prep.flat(prep.S)
    indices = [j for j, (kind, _) in enumerate(flat["calls"]) if kind == prep.S]
    tables = []
    for onward in indices:
        allowed = set()
        for values in product((0, 1), repeat=flat["V"]):
            valid = True
            for number, (kind, actual) in enumerate(flat["calls"]):
                if number == onward or (number == dropped_side and kind != "K"):
                    continue
                state = tuple(values[x] for x in actual)
                if kind == "K":
                    if len(set(state)) == 1:
                        valid = False
                        break
                else:
                    position = sum(value * (2 ** slot) for slot, value in enumerate(state))
                    if not bool(prep.G[kind][position]):
                        valid = False
                        break
            if valid:
                source = sum(values[slot] * (2 ** slot) for slot in range(3))
                destination = sum(values[var] * (2 ** slot)
                                  for slot, var in enumerate(flat["calls"][onward][1]))
                allowed.add((source, destination))
        tables.append(frozenset(allowed))
    return tables


def multiply(first, second):
    image = {}
    for middle, last in second:
        image.setdefault(middle, set()).add(last)
    return frozenset((start, last) for start, middle in first for last in image.get(middle, ()))


def is_product(relation):
    left = {a for a, _ in relation}
    right = {b for _, b in relation}
    return relation == frozenset(product(left, right))


def packed(relation, size=8):
    return sum(2 ** (size * a + b) for a, b in relation)


def unpacked(value, size=8):
    return frozenset((a, b) for a in range(size) for b in range(size)
                     if value & (2 ** (size * a + b)))


def check_word(generators, word):
    mismatches = []
    prefix, cycle = word["prefix"], word["cycle"]
    if not cycle:
        return [dict(part="recurring_word", detail="empty cycle")]
    relation = frozenset((i, i) for i in range(8))
    for depth, letter in enumerate(prefix, 1):
        if not 0 <= letter < len(generators):
            return [dict(part="recurring_word", detail="invalid prefix call", depth=depth)]
        relation = multiply(relation, generators[letter])
        if is_product(relation):
            mismatches.append(dict(part="recurring_word", detail="rectangular prefix", depth=depth))
    seen, phase, depth = set(), 0, len(prefix)
    while (relation, phase) not in seen:
        seen.add((relation, phase))
        letter = cycle[phase]
        if not 0 <= letter < len(generators):
            return mismatches + [dict(part="recurring_word", detail="invalid cycle call")]
        relation = multiply(relation, generators[letter])
        depth += 1
        if is_product(relation):
            mismatches.append(dict(part="recurring_word", detail="rectangular cycle prefix", depth=depth))
        phase = (phase + 1) % len(cycle)
    return mismatches


def audit(prep, produced, semigroup_result, checkpoint=lambda: None):
    tables = derive(prep)
    mismatches = []
    if len(tables) != len(produced):
        mismatches.append(dict(part="R_i", detail="different call count"))
    for i, (table, value) in enumerate(zip(tables, produced)):
        actual = packed(table)
        expected = int(value["hex"], 16)
        if actual != expected:
            mismatches.append(dict(part="R_i", call=i, expected=value["hex"],
                                   independently_derived=f"0x{actual:016x}"))
    result = dict(passed=False, calls=len(tables),
                  R_i=[f"0x{packed(table):016x}" for table in tables],
                  mismatches=mismatches)
    if not semigroup_result.get("complete"):
        result.update(passed=not mismatches, products_status="no completed product certificate")
        return result
    current = frozenset(tables)
    seen, all_rectangular, counts, least_r, certifying = {}, [], [], None, None
    while current not in seen:
        n = len(seen) + 1
        seen[current] = n
        counts.append(len(current))
        full = all(is_product(table) for table in current)
        all_rectangular.append(full)
        if full and least_r is None:
            least_r, certifying = n, current
        following = set()
        for first in current:
            for second in tables:
                following.add(multiply(first, second))
                checkpoint()
        current = frozenset(following)
    repeat_start = seen[current]
    period = len(seen) + 1 - repeat_start
    observed = dict(r=least_r, length_set_sizes=counts,
                    all_rectangular_by_length=all_rectangular,
                    repeat_start=repeat_start, period=period)
    for field, value in observed.items():
        if value != semigroup_result.get(field):
            mismatches.append(dict(part="P_n", field=field,
                                   expected=semigroup_result.get(field), actual=value))
    if least_r is not None:
        direct_products = sorted(packed(table) for table in certifying)
        recorded_products = sorted(int(value, 16) for value in semigroup_result["P_r"])
        if direct_products != recorded_products:
            mismatches.append(dict(part="P_r", expected=semigroup_result["P_r"],
                                   actual=[f"0x{value:016x}" for value in direct_products]))
        if not all(all_rectangular[repeat_start - 1:]):
            mismatches.append(dict(part="persistence", detail="repeating part is not all rectangular"))
        result.update(certifying_products_checked=len(certifying), r=least_r)
    elif semigroup_result.get("recurring_word"):
        mismatches.extend(check_word(tables, semigroup_result["recurring_word"]))
        result["recurring_word_checked"] = True
    else:
        mismatches.append(dict(part="recurring_word", detail="missing for nonforgetting result"))
    result.update(passed=not mismatches, independently_derived=observed)
    return result
