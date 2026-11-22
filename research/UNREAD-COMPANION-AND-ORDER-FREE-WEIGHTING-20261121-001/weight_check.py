"""Independent fixed-prefix tests for ordinary finite supports, with exact arithmetic."""
from collections import Counter
from fractions import Fraction
from itertools import permutations, product
from math import prod


def possible_splits(n):
    """For every partial assignment and unasked name, get its two word masks."""
    pairs = []
    for prefix in product((-1, 0, 1), repeat=n):
        feasible = [w for w in range(1 << n)
                    if all((w >> i) & 1 == v for i, v in enumerate(prefix) if v != -1)]
        for j, v in enumerate(prefix):
            if v == -1:
                left = sum(1 << w for w in feasible if not w & (1 << j))
                right = sum(1 << w for w in feasible if w & (1 << j))
                pairs.append((left, right))
    return pairs


def balanced(mask, splits):
    for left, right in splits:
        a = (mask & left).bit_count()
        b = (mask & right).bit_count()
        if a and b and a != b:
            return False
    return True


def affine(mask):
    words = [i for i in range(mask.bit_length()) if mask & (1 << i)]
    translated = {w ^ words[0] for w in words}
    return all(a ^ b in translated for a in translated for b in translated)


def reveal(words, order):
    """Literal forward coin, with no completion counts used in the choice."""
    current = [(words, Fraction(1))]
    for j in order:
        next_groups = []
        for group, mass in current:
            parts = [[w for w in group if (w >> j) & 1 == bit] for bit in (0, 1)]
            nonempty = [part for part in parts if part]
            next_groups.extend((part, mass / len(nonempty)) for part in nonempty)
        current = next_groups
    return {group[0]: mass for group, mass in current}


def main():
    for n, count in enumerate((1, 3, 11, 51, 307)):
        masks = possible_splits(n)
        hits = 0
        for data in range(1, 1 << (1 << n)):
            passes = balanced(data, masks)
            assert passes == affine(data)
            hits += passes
        assert hits == count
        print(f"{n} names: {hits}/{(1 << (1 << n))-1} nonempty relations pass every prefix.")
    # Different five-name check from the proof study: exhaust Boolean functions
    # of four independent inputs. No rank shortcut is used by the prefix test.
    source = (1 << 16)-1
    splits = possible_splits(5)
    passed = {f for f in range(1 << 16) if balanced((f << 16) | (source ^ f), splits)}
    expected = {sum(1 << x for x in range(16) if ((x & a).bit_count() + b) % 2)
                for a in range(16) for b in (0, 1)}
    assert passed == expected and len(passed) == 32
    print("Five names with four independent inputs: 32/65,536 Boolean functions pass.")
    # Count affine subsets by choosing an ordered independent basis, dividing
    # by the number of bases in its span, then choosing a translate.
    by_dimension = [
        (1 << (5-k)) * prod((1 << 5)-(1 << i) for i in range(k))
        // prod((1 << k)-(1 << i) for i in range(k)) for k in range(6)
    ]
    assert by_dimension == [32, 496, 1240, 620, 62, 1] and sum(by_dimension) == 2451
    words = list(range(1, 7))
    hist = reveal(words, (2, 1, 0))
    assert hist == {w: Fraction(1, 4) if w in (1, 6) else Fraction(1, 8) for w in words}
    assert sum(abs(p-Fraction(1, 6)) for p in hist.values())/2 == Fraction(1, 6)
    average = Counter()
    for order in permutations(range(3)):
        average.update(reveal(words, order))
    assert all(average[w]/6 == Fraction(1, 6) for w in words)
    print("NAE: 001 and 110 each weigh 1/4 when a,b are first; the other four each weigh 1/8.")
    print("Averaging all six orders returns 1/6 to every word; equality in each fixed order fails.")


if __name__ == "__main__":
    main()
