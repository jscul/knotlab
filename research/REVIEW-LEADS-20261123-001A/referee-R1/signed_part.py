"""Check the literal two-valued operator witness and the classical word counts."""
import argparse
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2] / "artifacts/REVIEW-LEADS-20261123-001A"
HOLDINGS = [
    (0, 1, 4, 5), (0, 2, 3, 6), (1, 2, 7, 8), (3, 9, 10),
    (5, 6, 8, 11), (4, 10, 12), (7, 9, 13), (11, 12, 13),
]
# The nine tensor products are repeated wherever one of the intervening
# two-holder equalities requires it. The signs on 1 and 7 select knot 0.
LABELS = "II -IX II IZ IX II IZ -XX XI ZZ ZI XZ ZX YY".split()


def check_operators():
    basic = dict(I=np.eye(2, dtype=complex), X=np.array([[0, 1], [1, 0]]),
                 Y=np.array([[0, -1j], [1j, 0]]), Z=np.diag([1, -1]))
    operators = []
    identity = np.eye(4, dtype=complex)
    for label in LABELS:
        first, second = label.lstrip("-")
        matrix = np.kron(basic[first], basic[second])
        if label.startswith("-"):
            matrix = -matrix
        assert np.array_equal(matrix, matrix.T.conj())
        assert np.array_equal(matrix @ matrix, identity)
        operators.append(matrix)
    signs = []
    pairs = 0
    for knot in HOLDINGS:
        for i, j in itertools.combinations(knot, 2):
            assert np.array_equal(operators[i] @ operators[j], operators[j] @ operators[i])
            pairs += 1
        product = identity
        for d in knot:
            product = product @ operators[d]
        assert any(np.array_equal(product, s * identity) for s in (1, -1))
        signs.append(int(product[0, 0].real))
    assert signs == [-1] + [1] * 7
    # Tensor by an even word on one extra binary factor. This keeps the
    # products and makes each observable attain both values, including II.
    flipped = {0, 2, 5, 8}
    assert all(len(flipped.intersection(row)) % 2 == 0 for row in HOLDINGS)
    extended = [np.kron(matrix, basic["Z"] if d in flipped else basic["I"])
                for d, matrix in enumerate(operators)]
    for matrix in extended:
        assert np.array_equal(matrix.T.conj(), matrix)
        assert np.array_equal(matrix @ matrix, np.eye(8)) and matrix.trace() == 0
    for sign, row in zip(signs, HOLDINGS):
        for i, j in itertools.combinations(row, 2):
            assert np.array_equal(extended[i] @ extended[j], extended[j] @ extended[i])
        product = np.eye(8)
        for i in row:
            product = product @ extended[i]
        assert np.array_equal(product, sign * np.eye(8))
    return dict(operator_labels=LABELS, products=signs, commuting_pairs_at_knots=pairs,
                extra_Z_factor_on=sorted(flipped), eight_dimensional_two_valued_observables=len(extended))


def count_words(limit):
    masks = [sum(1 << d for d in knot) for knot in HOLDINGS]
    counts = Counter()
    for word in range(limit):
        signature = sum((((word & m).bit_count() % 2) << k) for k, m in enumerate(masks))
        counts[signature] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    limit = 256 if args.pilot else 2 ** len(LABELS)
    start = time.process_time()
    result = check_operators()
    counts = count_words(limit)
    assert all(value == 2 for value in Counter(d for knot in HOLDINGS for d in knot).values())
    # Verify the literal fixture matches the deposited exceptional row.
    with next(SOURCE.glob("*/*parity_arm1*jsonl")).open() as stream:
        recorded = [row for line in stream if (row := json.loads(line)).get("admits")]
    assert len(recorded) == 1 and recorded[0]["stars"] == [list(k) for k in HOLDINGS]
    if not args.pilot:
        assert len(counts) == 128 and set(counts.values()) == {128}
    result.update(words_checked=limit, all_even_words=counts[0],
                  single_odd_words=[counts[1 << k] for k in range(8)],
                  attained_sign_patterns=len(counts), process_seconds=time.process_time() - start)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
