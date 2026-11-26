"""Check the archived real factors directly, using signed integer sums of products."""

import argparse
import json
from fractions import Fraction
from itertools import combinations, product
from math import prod
from pathlib import Path


BITS = (0, 1)
PAIRS = tuple(product(BITS, repeat=2))
WORDS = tuple(product(BITS, repeat=3))
EVEN = tuple(w for w in WORDS if sum(w) % 2 == 0)
UNIT = (1, 1, 1, 1)
SIGNED = (1, -1, -1, -1)
ARCHIVE_CONTROL = (2, 1, 1, 1)


def name(word):
    return "".join(map(str, word))


def tensor(weights):
    return dict(zip(EVEN, weights))


def factor(x, y):
    return (-1) ** (x * y)


def pair_reconstruction(word):
    even_weight = sum(prod(factor(h, x) for x in word) for h in BITS)
    joint_sign = prod(factor(x, y) for x, y in combinations(word, 2))
    return even_weight, even_weight * joint_sign


def identity_from_copies(t):
    return [[sum(t.get((a, u, v), 0) * t.get((b, u, v), 0)
                 for u, v in PAIRS) for b in BITS] for a in BITS]


def sum_third(t, cap):
    return [[sum(t.get((x, y, z), 0) * cap[z] for z in BITS)
             for y in BITS] for x in BITS]


def gram(matrix):
    return [[sum(matrix[i][k] * matrix[j][k] for k in BITS)
             for j in BITS] for i in BITS]


def open_three_copies(t):
    def contraction(a, b, c):
        return sum(t.get((a, u, v), 0) * t.get((b, v, w), 0) * t.get((c, w, u), 0)
                   for u, v, w in WORDS)
    return [contraction(*word) for word in WORDS]


def output_row(source, kernels, setting):
    # Rows are input bits and columns are recorded bits. Sum histories before reading.
    return [sum(weight * prod(kernels[s][x][y] for s, x, y in zip(setting, word, outcome))
                for word, weight in source.items()) for outcome in WORDS]


def weight_row(coefficients, prescription):
    transforms = {
        "support": lambda x: int(x != 0),
        "absolute": abs,
        "square": lambda x: x * x,
    }
    weights = [transforms[prescription](x) for x in coefficients]
    total = sum(weights)
    return tuple(Fraction(n, total) for n in weights)


def target(setting):
    if sum(setting) % 2:
        return (Fraction(1, 8),) * 8
    return tuple(Fraction(int(sum(w) % 2 == int(any(setting))), 4) for w in WORDS)


def summary(probabilities):
    exact = sum(sum(x == y for x, y in zip(row, target(s)))
                for s, row in probabilities.items())
    win = sum(p for s in EVEN for w, p in zip(WORDS, probabilities[s])
              if sum(w) % 2 == int(any(s))) / 4
    return {"target_cells": exact, "win": str(win)}


def protocol(source, kernels):
    raw = {s: output_row(source, kernels, s) for s in WORDS}
    readings = {rule: summary({s: weight_row(row, rule) for s, row in raw.items()})
                for rule in ("support", "absolute", "square")}
    return {"raw_coefficients": {name(s): row for s, row in raw.items()}, "readings": readings}


def retained_record(source, detector, ordinary):
    """Each changed read has a distinct unreported third bit; trace after squaring."""
    probabilities = {}
    for setting in WORDS:
        counts = [0] * len(WORDS)
        for marks in product(BITS, repeat=sum(setting)):
            cap_bits = iter(marks)
            maps = []
            for choice in setting:
                if choice:
                    z = next(cap_bits)
                    maps.append(sum_third(detector, tuple(int(b == z) for b in BITS)))
                else:
                    maps.append(ordinary)
            for i, outcome in enumerate(WORDS):
                coefficient = sum(weight * prod(k[x][y] for k, x, y in zip(maps, word, outcome))
                                  for word, weight in source.items())
                counts[i] += coefficient ** 2
        total = sum(counts)
        probabilities[setting] = tuple(Fraction(n, total) for n in counts)
    return summary(probabilities)


def magnitude_control(kernels):
    source = tensor(ARCHIVE_CONTROL)
    rows = {s: output_row(source, kernels, s) for s in ((0, 0, 0), (0, 1, 1))}
    result = {}
    for rule in ("support", "absolute", "square"):
        ordinary, changed = [weight_row(row, rule) for row in rows.values()]
        result[rule] = {
            "ordinary_000": str(ordinary[0]),
            "A_zero_before": str(sum(ordinary[:4])),
            "A_zero_after_BC_change": str(sum(changed[:4])),
        }
    return result


def run():
    positive, signed = tensor(UNIT), tensor(SIGNED)
    for word in WORDS:
        assert pair_reconstruction(word) == (2 * positive.get(word, 0), 2 * signed.get(word, 0))
    h = [[factor(x, y) for y in BITS] for x in BITS]
    ordinary = identity_from_copies(signed)
    assert ordinary == identity_from_copies(positive) == gram(h) == [[2, 0], [0, 2]]
    flat = sum_third(signed, (1, 1))
    unsigned_flat = sum_third(positive, (1, 1))
    assert flat == [[1, -1], [-1, -1]] and gram(flat) == ordinary
    assert sum_third(signed, (1, -1)) == h and unsigned_flat == [[1, 1], [1, 1]]
    kernels = (ordinary, h)
    trials = {
        "signed_source_archived_pair": protocol(signed, kernels),
        "positive_source_same_pair": protocol(positive, kernels),
        "single_pair_source_same_pair": protocol(
            {w: factor(w[0], w[1]) for w in EVEN}, kernels),
        "signed_source_open_sum": protocol(signed, (ordinary, flat)),
        "positive_source_own_open_sum": protocol(positive, (ordinary, unsigned_flat)),
    }
    for key in ("signed_source_archived_pair", "signed_source_open_sum"):
        assert all(r == {"target_cells": 64, "win": "1"} for r in trials[key]["readings"].values())
    assert trials["positive_source_same_pair"]["readings"]["square"] == {"target_cells": 44, "win": "5/8"}
    assert trials["positive_source_own_open_sum"]["readings"]["square"]["win"] == "5/8"
    raw_signed = trials["signed_source_archived_pair"]["raw_coefficients"]
    raw_one_pair = trials["single_pair_source_same_pair"]["raw_coefficients"]
    assert tuple(map(abs, raw_signed["000"])) == tuple(map(abs, raw_one_pair["000"]))
    for word, a, b in zip(WORDS, raw_signed["011"], raw_one_pair["011"]):
        assert bool(a) == bool(sum(word) % 2)
        assert bool(b) == (sum(word) % 2 == 0)
    forgotten = retained_record(signed, signed, ordinary)
    assert forgotten == {"target_cells": 40, "win": "5/8"}
    open_positive = open_three_copies(positive)
    open_signed = open_three_copies(signed)
    assert open_positive == [2 * positive.get(w, 0) for w in WORDS] and not any(open_signed)
    control = magnitude_control(kernels)
    assert [control[k]["ordinary_000"] for k in ("support", "absolute", "square")] == ["1/4", "2/5", "4/7"]
    assert control["square"]["A_zero_before"] == control["square"]["A_zero_after_BC_change"] == "5/7"
    assert all(control[k]["A_zero_before"] != control[k]["A_zero_after_BC_change"] for k in ("support", "absolute"))
    return {
        "physical_word_order": [name(w) for w in WORDS], "fixed_pair": h,
        "two_copies_or_two_pairs": ordinary, "summed_third": flat,
        "positive_ternary_summed_third": unsigned_flat, "open_three_copies": {
            "positive": open_positive, "signed": open_signed,
        }, "protocols": trials, "retained_third_mark": forgotten,
        "positive_unequal_magnitude_control": control,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--check", type=Path, metavar="RECEIPT")
    args = parser.parse_args()
    if args.smoke:
        h = [[factor(x, y) for y in BITS] for x in BITS]
        result = protocol(tensor(SIGNED), (gram(h), h))
        print(json.dumps(result["readings"]))
        return
    contents = json.dumps(run(), indent=2) + "\n"
    if args.check:
        if contents != args.check.read_text():
            raise SystemExit("Real contraction receipt differs")
        print("Real contraction receipt matches")
    else:
        print(contents, end="")


if __name__ == "__main__":
    main()
