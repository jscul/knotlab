"""Replay the single-mark freedom calculation without importing the producer.

Every nonempty Boolean relation through three names is tested. This checks
the algebra on unrestricted finite relations, including the two knot laws.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import json


def subsets(bits):
    current = bits
    while current:
        yield current
        current = (current - 1) & bits
    yield 0


def sign(bits):
    return -1 if bits.bit_count() % 2 else 1


def moments(words, flip, read, global_changes=None):
    if global_changes is not None and flip not in global_changes:
        return 0
    return sum(sign(word & read) for word in words if (word ^ flip) in words)


def probability_from_freedom(words, xmask, zmask, answers, group=None):
    numerator = sum(sign(answers & (d | r)) * moments(words, d, r, group)
                    for d in subsets(xmask) for r in subsets(zmask))
    return Fraction(numerator, len(words) * (1 << (xmask | zmask).bit_count()))


def probability_with_projections(words, xmask, zmask, answers, group=None):
    sums = {}
    for word in words:
        if (word ^ answers) & zmask:
            continue
        orbit = min(word ^ delta for delta in group) if group is not None else 0
        key = (word & ~xmask, orbit)
        sums[key] = sums.get(key, 0) + sign(word & xmask & answers)
    return Fraction(sum(v*v for v in sums.values()), len(words) * (1 << xmask.bit_count()))


def audit():
    total = cases = different = 0
    for width in (1, 2, 3):
        size = 1 << width
        for support in range(1, 1 << size):
            words = {i for i in range(size) if support >> i & 1}
            group = {d for d in range(size) if all(w ^ d in words for w in words)}
            cases += 1
            for choices in product("IXZ", repeat=width):
                x = sum(1 << i for i, c in enumerate(choices) if c == "X")
                z = sum(1 << i for i, c in enumerate(choices) if c == "Z")
                mass = rival_mass = 0
                for outputs in subsets(x | z):
                    p = probability_from_freedom(words, x, z, outputs)
                    p2 = probability_from_freedom(words, x, z, outputs, group)
                    assert p == probability_with_projections(words, x, z, outputs)
                    assert p2 == probability_with_projections(words, x, z, outputs, group)
                    assert min(p, p2) >= 0
                    different += p != p2
                    mass += p
                    rival_mass += p2
                    total += 1
                assert mass == rival_mass == 1
    nae = set(range(1, 7))
    parity = {0, 3, 5, 6}
    examples = {}
    for law, words in (("not-all-equal", nae), ("parity", parity)):
        group = {d for d in range(8) if all(w ^ d in words for w in words)}
        f = Fraction(moments(words, 1, 0), len(words))
        scores = {}
        for label, g in (("count rule", None), ("orbit mixture", group)):
            numerator = moments(words, 7, 0, g)
            numerator -= sum(moments(words, bit, 7 ^ bit, g) for bit in (1, 2, 4))
            scores[label] = str(Fraction(numerator, len(words)))
        examples[law] = {"fraction free": str(f), "change plus": str((1 + f) / 2), "three-reader scores": scores}
    return {"nonempty relations": cases, "probabilities per rule compared": total,
            "probabilities different between the two rules": different, "isolated ternaries": examples}


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
