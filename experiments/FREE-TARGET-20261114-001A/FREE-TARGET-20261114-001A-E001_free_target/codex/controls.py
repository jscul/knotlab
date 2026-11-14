"""Small synthetic controls for production products and rectangularity."""
from __future__ import annotations

from itertools import combinations_with_replacement

import independent
import relations


def oracle(generators, size):
    tables = tuple(independent.unpacked(value, size) for value in generators)
    current, seen, counts, flags, least = frozenset(tables), {}, [], [], None
    while current not in seen:
        n = len(seen) + 1
        seen[current] = n
        counts.append(len(current))
        all_product = all(independent.is_product(table) for table in current)
        flags.append(all_product)
        if all_product and least is None:
            least = n
        current = frozenset(independent.multiply(first, second)
                            for first in current for second in tables)
    return dict(r=least, repeat_start=seen[current], period=len(seen) + 1 - seen[current],
                length_set_sizes=counts, all_rectangular_by_length=flags)


def run():
    mismatches, algebra_count, semigroup_count = [], 0, 0
    for size in (1, 2):
        for left in range(1 << (size * size)):
            source = independent.unpacked(left, size)
            if relations.rectangular(left, size) != independent.is_product(source):
                mismatches.append(dict(part="rectangular", size=size, relation=left))
            for right in range(1 << (size * size)):
                actual = relations.compose(left, right, size)
                expected = independent.packed(independent.multiply(source, independent.unpacked(right, size)), size)
                algebra_count += 1
                if actual != expected:
                    mismatches.append(dict(part="compose", size=size, left=left, right=right,
                                           actual=actual, expected=expected))
    for generators in combinations_with_replacement(range(16), 2):
        actual, expected = relations.semigroup(generators, size=2), oracle(generators, 2)
        semigroup_count += 1
        for field, value in expected.items():
            if actual[field] != value:
                mismatches.append(dict(part="semigroup", generators=generators, field=field,
                                       actual=actual[field], expected=value))
        if actual["recurring_word"] is not None:
            word = actual["recurring_word"]
            state = sum(1 << (2 * i + i) for i in range(2))
            for letter in word["prefix"]:
                state = relations.compose(state, generators[letter], 2)
                if relations.rectangular(state, 2):
                    mismatches.append(dict(part="word_prefix", generators=generators))
            seen, phase = set(), 0
            while (state, phase) not in seen:
                seen.add((state, phase))
                state = relations.compose(state, generators[word["cycle"][phase]], 2)
                phase = (phase + 1) % len(word["cycle"])
                if relations.rectangular(state, 2):
                    mismatches.append(dict(part="word_cycle", generators=generators))
    named = []
    for name, size, edges, expected_r in (
        ("proper_projection_rectangle", 3, ((0, 1), (0, 2)), 1),
        ("two_step_rectangle_not_full", 3, ((0, 1), (1, 2), (2, 2)), 2),
        ("identity_never_rectangular", 3, ((0, 0), (1, 1), (2, 2)), None),
        ("empty_is_product", 3, (), 1),
    ):
        encoded = independent.packed(frozenset(edges), size)
        actual = relations.semigroup((encoded,), size=size)
        named.append(dict(name=name, r=actual["r"], passed=actual["r"] == expected_r))
        if actual["r"] != expected_r:
            mismatches.append(dict(part="named", name=name, actual=actual["r"], expected=expected_r))
    return dict(passed=not mismatches, algebra_products=algebra_count,
                two_generator_semigroups=semigroup_count, named=named, mismatches=mismatches)
