"""Exact word counts for the separability argument and the restricted reading."""

import argparse
import json
from collections import Counter
from itertools import combinations, product
from time import process_time


def parity(value):
    return value.bit_count() % 2


def words(laws, width):
    return {word for word in range(1 << width)
            if all(parity(word & law) == 0 for law in laws)}


def rectangle_count(allowed):
    """Two distinctions per reader and two in the middle."""
    nonempty = nonproducts = 0
    for middle in range(4):
        pairs = {(w & 3, (w >> 2) & 3) for w in allowed if w >> 4 == middle}
        if pairs:
            nonempty += 1
            left, right = zip(*pairs)
            nonproducts += pairs != set(product(set(left), set(right)))
    return nonempty, nonproducts


def separation_checks(limit):
    left, right, middle = {0, 1}, {2, 3}, {4, 5}
    triples = sorted(set(combinations(sorted(left | middle), 3))
                     | set(combinations(sorted(right | middle), 3)))
    laws = [sum(1 << slot for slot in triple) for triple in triples]
    summary = Counter()
    for pattern in range(min(limit, 1 << len(laws))):
        chosen = [law for j, law in enumerate(laws) if pattern & (1 << j)]
        nonempty, nonproducts = rectangle_count(words(chosen, 6))
        summary.update(patterns=1, admissible_middle_values=nonempty,
                       nonproduct_supports=nonproducts)
    assert summary["nonproduct_supports"] == 0
    # Comparison with a single ternary naming one distinction of each reader.
    straddling = (1 << 0) | (1 << 2) | (1 << 4)
    total, failed = rectangle_count(words([straddling], 6))
    assert total == failed == 4
    return dict(summary, straddling_nonproducts=failed)


def mixed_moments(limit):
    # Two ternaries, one per reader, have the same middle distinction.
    width = 5
    laws = [0b10011, 0b11100]
    allowed = words(laws, width)
    dual = {p for p in range(1 << width) if all(not parity(p & w) for w in allowed)}
    samples = list(product(allowed, dual))
    tested = 0
    for x in range(min(limit, 1 << width)):
        for z in range(1 << width):
            if parity(x & z):
                continue
            # Matrix element summed directly over the positive equal amplitudes.
            numerator = sum((-1) ** parity(w & z) for w in allowed if w ^ x in allowed)
            # Separate uniform draws give a joint answer for pure questions.
            list_sum = sum((-1) ** (parity(w & z) ^ parity(p & x)) for w, p in samples)
            assert len(samples) * numerator == len(allowed) * list_sum
            tested += 1
    # An individual proposed flip breaks the first law on every word.
    x = 1
    legal = sum(w ^ x in allowed for w in allowed)
    plus = sum(not parity(p & x) for _, p in samples)
    assert legal == 0 and 2 * plus == len(samples)
    # A and B know the same nonconstant parity even when the middle is unread.
    shares = Counter((parity(w & 3), parity(w & 12)) for w in allowed)
    assert shares == {(0, 0): 4, (1, 1): 4}
    return {"allowed_words": len(allowed), "dual_words": len(dual),
            "equally_weighted_draw_pairs": len(samples), "commuting_moments": tested,
            "legal_single_flips": legal, "plus_answers_for_that_flip": plus,
            "shared_parity_00_and_11_counts": [shares[(0, 0)], shares[(1, 1)]]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=256)
    args = parser.parse_args()
    start = process_time()
    result = {"separation": separation_checks(args.limit), "lists": mixed_moments(args.limit)}
    result["cpu_seconds"] = round(process_time() - start, 5)
    print(json.dumps(result, indent=2))
