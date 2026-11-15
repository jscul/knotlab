#!/usr/bin/env python3
"""Verify private tests, the rank certificate and common-state reads by actual crossings."""

import argparse
import json
from collections import Counter
from itertools import product
from math import comb
from pathlib import Path


LABELS = list(product(range(3), repeat=2))
FIVE_STATES = [(0, 0), (0, 1), (0, 2), (1, 1), (2, 0)]
FIVE_TESTS = [(1, 0), (1, 1), (2, 1), (0, 1), (0, 2)]
SIX_STATES = [(1, 0), (2, 2), (1, 1), (0, 0), (1, 2), (0, 1)]
SIX_TESTS = [(2, 1), (0, 2), (1, 2), (2, 0), (0, 1), (1, 1)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def literal(test, state):
    k, t = test
    a, d = state
    u, v = a, (a + d) % 3
    for _ in range(k):
        u, v = v, (2 * v - u) % 3
    return int(u == t)


def matrix(tests, states):
    return [[literal(test, state) for state in states] for test in tests]


def field_rank(rows, prime):
    work = [row.copy() for row in rows]
    rank = 0
    for j in range(len(work[0])):
        pivot = next((i for i in range(rank, len(work)) if work[i][j] % prime), None)
        if pivot is None:
            continue
        work[pivot], work[rank] = work[rank], work[pivot]
        scale = pow(work[rank][j], -1, prime)
        work[rank] = [scale * value % prime for value in work[rank]]
        for i in range(rank + 1, len(work)):
            multiple = work[i][j]
            work[i] = [(x - multiple * y) % prime for x, y in zip(work[i], work[rank])]
        rank += 1
    return rank


def subset_census(rows):
    row_masks = [sum(bit << j for j, bit in enumerate(row)) for row in rows]
    private = Counter()
    triangular = Counter()
    ordered_subsets = {0}
    for selected in range(1 << len(LABELS)):
        singletons = {row & selected for row in row_masks if (row & selected).bit_count() == 1}
        size = selected.bit_count()
        if len(singletons) == size:
            private[size] += 1
        if any((selected ^ only) in ordered_subsets for only in singletons):
            ordered_subsets.add(selected)
        if selected in ordered_subsets:
            triangular[size] += 1
    return [private[i] for i in range(10)], [triangular[i] for i in range(10)]


def is_identity(rows):
    return all(value == int(i == j)
               for i, row in enumerate(rows) for j, value in enumerate(row))


def two_levels(rows):
    return all(value == int(i == j or (i >= 3 and j < 3 and i - 3 != j))
               for i, row in enumerate(rows) for j, value in enumerate(row))


def private_word_checks(words, tests, states):
    """Test every joint public query against every selected joint state, by literal crossing."""
    for u in words:
        for v in words:
            hit = all(literal(tests[i], states[j]) for i, j in zip(u, v))
            require(hit == (u == v), "product query lost privacy on two selected words")
    return len(words)


def product_certificates():
    out = {}
    for b in (2, 3, 4):
        digits = list(product(range(6), repeat=b))
        equal_sum = [w for w in digits if sum(w) == (5 * b) // 2]
        equal_high = [w for w in digits if sum(i >= 3 for i in w) == b // 2]
        # The five-letter product is checked through three pairs. Its per-coordinate
        # identity has already been verified and therefore proves every later power.
        n_five = 5 ** b
        if b <= 3:
            n_five = private_word_checks(list(product(range(5), repeat=b)), FIVE_TESTS, FIVE_STATES)
        n_sum = private_word_checks(equal_sum, SIX_TESTS, SIX_STATES)
        n_high = private_word_checks(equal_high, SIX_TESTS, SIX_STATES)
        require(n_high == comb(b, b // 2) * 3 ** b, "wrong high-letter count")
        out[str(b)] = {"five_letter_product": n_five, "equal_digit_sum": n_sum,
                       "equal_high_count": n_high}
    # Integer convolution evaluates the sum-layer size without enumerating sixteen-letter words.
    coeffs = [1]
    crossover_sum = crossover_high = None
    for b in range(1, 17):
        new = [0] * (len(coeffs) + 5)
        for i, n in enumerate(coeffs):
            for digit in range(6):
                new[i + digit] += n
        coeffs = new
        high = comb(b, b // 2) * 3 ** b
        if high > 5 ** b and crossover_high is None:
            crossover_high = [b, high, 5 ** b]
        if max(coeffs) > 5 ** b and crossover_sum is None:
            crossover_sum = [b, max(coeffs), 5 ** b]
    return out, crossover_sum, crossover_high


def passes(table, tests):
    return any(all(literal(q, cell) for q, cell in zip(tests, row)) for row in table)


def marginal_checks(rows):
    p, q = (0, 0), (0, 1)
    same = [(p, p), (q, q)]
    switched = [(p, q), (q, p)]
    probes = ((1, 0), (1, 0))
    marginals_same = all({row[i] for row in same} == {row[i] for row in switched} for i in (0, 1))
    require(marginals_same and passes(same, probes) and not passes(switched, probes),
            "matched marginal example no longer separates the joint query")

    controls = 0
    for left, right in product(([], [p], [q], [p, q]), repeat=2):
        joined = list(product(left, right))
        for ltest, rtest in product(LABELS, repeat=2):
            expected = any(literal(ltest, c) for c in left) and any(literal(rtest, c) for c in right)
            require(passes(joined, (ltest, rtest)) == expected, "product-input factorization failed")
            controls += 1

    reports = set()
    for bits in range(512):
        reports.add(tuple(i for i, row in enumerate(rows)
                          if any(cell and bits & (1 << j) for j, cell in enumerate(row))))
    independent_reports = {tuple(product(left, right)) for left, right in product(reports, repeat=2)}
    require(len(independent_reports) == 1 + (len(reports) - 1) ** 2,
            "the independent-product class count changed")
    return {"matched_marginals": marginals_same, "same_answer": passes(same, probes),
            "switched_answer": passes(switched, probes), "product_control_cases": controls,
            "one_copy_existence_reports": len(reports), "two_copy_independent_reports": len(independent_reports)}


def compute():
    rows = matrix(LABELS, LABELS)
    by_formula = [[int((a + k * d) % 3 == t) for a, d in LABELS] for k, t in LABELS]
    require(rows == by_formula, "closed crossing formula disagrees with repeated crossing")
    for i, (k, t) in enumerate(LABELS):
        coefficients = (1 - t * t, 2 * t, 2 * t * k, -1, -2 * k, -k * k)
        for j, (a, d) in enumerate(LABELS):
            values = (1, a, d, a * a, a * d, d * d)
            require(sum(x * y for x, y in zip(coefficients, values)) % 3 == rows[i][j],
                    "six-term factorization over F3 failed")
    private, triangular = subset_census(rows)
    rank = field_rank(rows, 3)
    require(is_identity(matrix(FIVE_TESTS, FIVE_STATES)), "five-state private certificate failed")
    six = matrix(SIX_TESTS, SIX_STATES)
    require(two_levels(six), "ordered two-level certificate failed")
    require(max(i for i, n in enumerate(private) if n) == len(FIVE_STATES),
            "private maximum lacks matching exhaustive support")
    require(rank == len(SIX_STATES) == max(i for i, n in enumerate(triangular) if n),
            "rank and triangular maximum disagree")
    # Both altered tests still accept their assigned states. They now accept
    # another selected state as well, changing the mathematical certificate.
    wrong_five = [(0, 0)] + FIVE_TESTS[1:]
    wrong_six = SIX_TESTS[:3] + [(0, 0)] + SIX_TESTS[4:]
    require(literal(wrong_five[0], FIVE_STATES[0]) and not is_identity(matrix(wrong_five, FIVE_STATES)),
            "wrong private query escaped detection")
    require(literal(wrong_six[3], SIX_STATES[3]) and not two_levels(matrix(wrong_six, SIX_STATES)),
            "wrong level query escaped detection")
    high_low = [w for w in product(range(6), repeat=2) if sum(i >= 3 for i in w) == 1]
    mixed = [(0, 0), *high_low]
    # Use an admitted product query demonstrating why a second high-count level
    # cannot simply be added to the certificate.
    collisions = [(u, v) for u in mixed for v in mixed if u != v
                  and all(literal(SIX_TESTS[i], SIX_STATES[j]) for i, j in zip(u, v))]
    require(collisions, "wrong mixed-level control was accidentally private")
    products, sum_cross, high_cross = product_certificates()
    return {
        "matrix": rows, "rank_F3": rank, "rank_F2_control": field_rank(rows, 2),
        "private_subsets_by_size": private, "triangular_subsets_by_size": triangular,
        "private_max": len(FIVE_STATES), "triangular_max": len(SIX_STATES), "two_level_matrix": six,
        "literal_product_certificates": products,
        "first_equal_digit_sum_exceeding_five_power": sum_cross,
        "first_equal_high_count_exceeding_five_power": high_cross,
        "wrong_mixed_level_confusion": [list(w) for w in collisions[0]],
        "marginals": marginal_checks(rows),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emit", action="store_true")
    p.add_argument("--expected", type=Path, default=Path(__file__).with_name("certificates.json"))
    args = p.parse_args()
    data = compute()
    if args.emit:
        print(json.dumps(data, indent=2))
        return
    require(data == json.loads(args.expected.read_text()), "recomputed certificate differs from receipt data")
    print(json.dumps({"status": "passed", **data}, sort_keys=True))


if __name__ == "__main__":
    main()
