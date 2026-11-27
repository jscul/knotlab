"""Small exact controls for what the reported tables can establish."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import islice, product
from time import perf_counter


def square_lists(prefix):
    # List every valid row report and column report before the settings are drawn.
    triples = list(product((1, -1), repeat=3))
    plus = [t for t in triples if t[0] * t[1] * t[2] == 1]
    minus = [t for t in triples if t[0] * t[1] * t[2] == -1]
    rows = product(plus, repeat=3)
    cols = product(plus, plus, minus)
    scores = Counter()
    for r, c in islice(product(rows, cols), prefix):
        scores[sum(r[i][j] == c[j][i] for i, j in product(range(3), repeat=2))] += 1
    if prefix is None:
        assert sum(scores.values()) == 4096 and max(scores) == 8 and scores[8] == 144
    return sorted(scores.items())


def loose_local_list(prefix):
    # Reader order A, middle, B. B's setting 0 labels the two certain products.
    checked = 0
    for x, y, z in islice(product(range(2), repeat=3), prefix):
        hist = Counter()
        for a0, a1, b0, b1 in product((1, -1), repeat=4):
            a = (a0, a1)[x]
            m = (a0 * b0, -a1 * b0)[y]
            b = (b0, b1)[z]
            hist[a, m, b] += 1
        sign = {(0, 0, 0): 1, (1, 1, 0): -1}.get((x, y, z), 0)
        for a, m, b in product((1, -1), repeat=3):
            assert Fraction(hist[a, m, b], 16) == Fraction(1 + a * m * b * sign, 8)
            checked += 1
    return checked


def nonuniform_pauli(prefix):
    # |00>, |01>, |10>, |11>. Every coefficient is strictly positive.
    amp = (4, 2, 1, 4)
    norm = sum(v * v for v in amp)
    expectations = {}
    masks = {"XX": (3, 0), "ZZ": (0, 3), "ZX": (1, 2), "XZ": (2, 1)}
    for op, (flip, value) in islice(masks.items(), prefix):
        numerator = sum(a * amp[i ^ flip] * (-1) ** ((i & value).bit_count())
                        for i, a in enumerate(amp))
        expectations[op] = Fraction(numerator, norm)
    if len(expectations) == 4:
        score = sum(expectations.values()) - 2 * expectations["XZ"]
        assert score == Fraction(79, 37)
    return {op: str(value) for op, value in expectations.items()}


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--pilot", action="store_true")
    pilot = args.parse_args().pilot
    for check, limit in ((square_lists, 128), (loose_local_list, 1), (nonuniform_pauli, 1)):
        start = perf_counter()
        result = check(limit if pilot else None)
        print(check.__name__, result, f"{perf_counter() - start:.6f} s")
