"""Count states and independently expand the weighting on the shared distinctions."""

import argparse
from fractions import Fraction
from itertools import product
from time import perf_counter


def allowed(values):
    return min(values) != max(values)


def old_words(size, count):
    """Check the identity on each old word, including ones the old rule forbids."""
    bob = size // 2
    # The first two columns count equal/unequal values in Alice's pair.
    counts = {name: [0, 0] for name in ("old", "deleted", "edited")}
    for word in range(count):
        shared = [(word >> i) & 1 for i in range(size)]
        loose = [(word >> (size + i)) & 1 for i in range(size)]
        places = [(shared[i-1], shared[i], loose[i]) for i in range(size)]
        rest = all(allowed(knot) for i, knot in enumerate(places) if i != bob)
        old = int(rest and allowed(places[bob]))
        deleted = int(rest)
        edited = sum(rest and allowed((*places[bob], fresh)) for fresh in (0, 1))
        assert edited == old + deleted, (size, word, old, deleted, edited)
        unequal = int(shared[-1] != shared[0])
        for name, multiplicity in (("old", old), ("deleted", deleted), ("edited", edited)):
            counts[name][unequal] += multiplicity
    return counts


def local_coefficients(loose_count):
    """Read the two coefficients from counts of loose completions at fixed pair values."""
    equal, unequal = (
        sum(allowed((0, second, *tail)) for tail in product((0, 1), repeat=loose_count))
        for second in (0, 1)
    )
    return Fraction(equal + unequal, 2), Fraction(equal - unequal, 2)


def signed_terms(size, edited, count):
    # Multiply one constant or one signed pair product per knot. A term sums
    # to zero over shared distinctions unless every exponent is even.
    bob = size // 2
    factors = [local_coefficients(2 if edited and i == bob else 1) for i in range(size)]
    alice_pair = 1 | (1 << (size - 1))
    terms = {"count": [], "Alice sum": []}
    for selection in range(count):
        odd = 0
        coefficient = Fraction(1)
        for i, (constant, pair) in enumerate(factors):
            if selection & (1 << i):
                coefficient *= pair
                odd ^= (1 << ((i - 1) % size)) | (1 << i)
            else:
                coefficient *= constant
        if odd in (0, alice_pair):
            contribution = coefficient * (1 << size)
            assert contribution.denominator == 1
            terms["count" if odd == 0 else "Alice sum"].append((selection, int(contribution)))
    return terms


def check(size, pilot):
    divisor = 8 if pilot else 1
    word_count = 2 ** (2 * size) // divisor
    term_count = 2 ** size // divisor
    before = perf_counter()
    counts = old_words(size, word_count)
    middle = perf_counter()
    terms = {name: signed_terms(size, name == "edited", term_count) for name in ("old", "edited")}
    after = perf_counter()
    print(f"{size} knots, {word_count} old words in {middle-before:.6f}s, "
          f"{term_count} selections per setting in {after-middle:.6f}s")
    if pilot:
        print(f"  projected full computation {(after-before)*divisor:.4f}s")
        return
    for name, (equal, unequal) in counts.items():
        total, numerator = equal + unequal, equal - unequal
        print(f"  {name} equal={equal} unequal={unequal} N={total} "
              f"Alice sum={numerator} mean={Fraction(numerator, total)}")
        if name in terms:
            for observable, target in (("count", total), ("Alice sum", numerator)):
                parts = terms[name][observable]
                assert sum(value for selection, value in parts) == target
                print(f"    {observable} contributions {parts}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="time the first eighth of each computation")
    pilot = parser.parse_args().pilot
    for size in (3, 4, 5):
        check(size, pilot)
