"""Finite counterexamples for reading signed sums, separate from the frozen census."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from math import comb, prod
from time import perf_counter

BITS = (0, 1)
WORDS = tuple(product(BITS, repeat=3))


def is_mixed(word):
    return len(set(word)) == 2


def reversal():
    mixed = [w for w in WORDS if is_mixed(w)]
    assert all((-1) ** comb(sum(w), 2) == -((-1) ** sum(w)) for w in mixed)
    even = [w for w in WORDS if sum(w) % 2 == 0]
    mass = Counter()
    for w in even:
        mass[w[0]] += (-1) ** comb(sum(w), 2)
    return {"mixed_ternary_words": len(mixed), "one_read_signed_counts": [mass[b] for b in BITS]}


def quadratic():
    # Four potential outputs (A0, A1, B0, B1); both local choices use the same source.
    weights = {w: (-1) ** (w[1] * (w[0] + w[2])) for w in product(BITS, repeat=4)}
    total = sum(weights.values())
    tables = {}
    for x, y in product(BITS, repeat=2):
        counts = Counter()
        for w, v in weights.items():
            counts[w[x], w[2 + y]] += v
        assert min(counts.values()) >= 0
        tables[f"{x}{y}"] = [str(Fraction(counts[key], total)) for key in product(BITS, repeat=2)]
    assert tables["00"] == ["1/2", "0", "0", "1/2"]
    return {"signed_total": total, "tables": tables}


def marked_sign():
    # Six cyclically indexed ternary holdings. The transposed system uses the same triples.
    triples = [tuple((i + j) % 6 for j in (-1, 0, 1)) for i in range(6)]
    coefficients = {}
    for w in product(BITS, repeat=6):
        if all(is_mixed([w[j] for j in t]) for t in triples):
            marks = [t for t in triples if 0 in t]
            signs = []
            for t in marks:
                s = 1 if [w[j] for j in t].count(w[0]) == 2 else -1
                assert s == -prod((-1) ** w[j] for j in t if j != 0)
                signs.append(s)
            coefficients["".join(map(str, w))] = sum(signs)
    assert coefficients["011011"] == -3 and coefficients["010110"] == 3
    return {"proper_words": len(coefficients), "at_011011": coefficients["011011"],
            "at_010110": coefficients["010110"]}


def three_copies():
    triples = ((0, 2, 3), (0, 1, 4), (1, 2, 5))
    sums, counts = Counter(), Counter()
    for w in product(BITS, repeat=6):
        weights = [sum(w[j] for j in t) for t in triples]
        if all(k % 2 == 0 for k in weights):
            ext = "".join(map(str, w[3:]))
            counts[ext] += 1
            sums[ext] += prod(1 if k == 0 else -1 for k in weights)
    assert set(counts.values()) == {2} and set(sums.values()) == {0}
    return {"even_exteriors": dict(counts), "signed_exterior_sums": dict(sums)}


def pointwise():
    ratios = {}
    for name, words in (("even", [w for w in WORDS if sum(w) % 2 == 0]),
                        ("mixed", [w for w in WORDS if is_mixed(w)])):
        for w in words:
            def marginal(indices):
                return Fraction(sum(all(v[i] == w[i] for i in indices) for v in words), len(words))
            ratio = prod(marginal(pair) for pair in combinations(range(3), 2))
            ratio /= marginal(range(3)) * prod(marginal([i]) for i in range(3))
            if name in ratios:
                assert ratios[name] == str(ratio)
            ratios[name] = str(ratio)
    return ratios


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="first full example with its unchanged inputs")
    pilot = parser.parse_args().pilot
    start = perf_counter()
    out = {"two_phases": reversal()}
    if not pilot:
        out.update(quadratic=quadratic(), marked_sign=marked_sign(),
                   coherent_sum=three_copies(), co_information_ratios=pointwise())
    out["elapsed_seconds"] = round(perf_counter() - start, 6)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
