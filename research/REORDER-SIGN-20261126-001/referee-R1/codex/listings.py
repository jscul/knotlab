"""Independently check the fixed-reading listing-order claims P1 and P2.

Only the mathematical specifications in preregistration.md and results.md
are used. Distinction i is represented by bit i, starting from 0. Correlations
are integer numerators with common denominator 2**(n - 1).

The uniform explanation is separate from the enumeration. On the group V
of even words, write the swap sign as (-1)**q(x) and let B be the polar form
of q. Translating x by the even flip t gives the correlation (-1)**q(t)
times the average of (-1)**(B(x,t) + x·t) over V. Thus every correlation has
unit magnitude exactly when B restricted to V equals the dot product. This
form is nonzero for n >= 3, witnessed by two pairs sharing one distinction,
so the resulting signs are not a character. The empty correlation is +1.
Any assignment of local X and Z answers gives c(t) equal to c(0) times the
product over t of local X answers divided by local Z answers, a character
when c(0) is +1.

Reversal has that polar form. A zero-diagonal difference matrix D from
the reversal form vanishes on V exactly when D[i,j] = b[i] + b[j] over F2,
by testing the basis e[0]+e[i]. Thus an order preserves the reference
order across classes of b and reverses within each class. Alternating class
membership for any i < j < k would force i before j before k and k before i.
So b has at most one switch, and the eligible orders are exactly the n
different orders that reverse a prefix and its complementary suffix.
These are the rotations of the reversal listing. More generally, two orders
give the same polar form exactly when one is a rotation of the other. Apply
the same argument with the first order as the reference, with the within-class
comparisons preserved and the across-class comparisons reversed.
"""

import argparse
import json
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path


def sign(exponent):
    return -1 if exponent % 2 else 1


def even_words(n):
    return tuple(word for word in range(1 << n) if word.bit_count() % 2 == 0)


def inversions(order):
    return sum(left > right for left, right in combinations(order, 2))


def amplitudes(order, words, swap_cost=-1):
    order = tuple(order)
    return {
        word: swap_cost ** inversions([i for i in order if word & (1 << i)])
        for word in words
    }


def correlations(amplitude, words, n):
    """Apply Z on the complement of the flip and X on the flip."""
    all_distinctions = (1 << n) - 1
    return {
        flip: sum(
            amplitude[word ^ flip]
            * amplitude[word]
            * sign((word & (all_distinctions ^ flip)).bit_count())
            for word in words
        )
        for flip in words
    }


def noncharacter_witness(numerators, denominator):
    """Find a multiplicativity failure after checking every magnitude and c(0)."""
    assert numerators[0] == denominator
    if any(abs(value) != denominator for value in numerators.values()):
        return None
    for left, right in combinations(numerators, 2):
        joint = left ^ right
        if numerators[left] * numerators[right] != denominator * numerators[joint]:
            flips = [left, right, joint]
            return {
                "flips": flips,
                "correlations": [numerators[flip] // denominator for flip in flips],
            }
    return None


def polar_form(amplitude, n):
    basis = [1 | (1 << i) for i in range(1, n)]
    return tuple(
        amplitude[left] * amplitude[right] * amplitude[left ^ right]
        for left, right in combinations(basis, 2)
    )


def prefix_suffix_orders(n):
    reference = tuple(range(n))
    return {reference[:cut][::-1] + reference[cut:][::-1] for cut in range(n)}


def order_census(n):
    words = even_words(n)
    denominator = len(words)
    expected_orders = prefix_suffix_orders(n)
    positive_control = correlations(amplitudes(range(n), words, swap_cost=1), words, n)
    all_distinctions = (1 << n) - 1
    assert positive_control == {
        flip: denominator if flip in (0, all_distinctions) else 0 for flip in words
    }
    assert noncharacter_witness(positive_control, denominator) is None

    carrying_orders = set()
    carrying_transpositions = []
    by_parity = {"even": [0, 0], "odd": [0, 0]}
    nonzero_polar_count = 0
    rotation_by_polar_form = {}
    unit_correlation_counts = Counter()
    ternary_details = []
    for order in permutations(range(n)):
        amplitude = amplitudes(order, words)
        numerators = correlations(amplitude, words, n)
        witness = noncharacter_witness(numerators, denominator)
        has_full_contradiction = witness is not None
        if has_full_contradiction:
            carrying_orders.add(order)
            moved = [i for i in range(n) if order[i] != i]
            if len(moved) == 2:
                carrying_transpositions.append({
                    "order": order,
                    "adjacent": moved[1] == moved[0] + 1,
                })
        parity = "odd" if inversions(order) % 2 else "even"
        by_parity[parity][0] += 1
        by_parity[parity][1] += int(has_full_contradiction)
        form = polar_form(amplitude, n)
        assert has_full_contradiction == all(entry == -1 for entry in form)
        cut = order.index(0)
        rotation = order[cut:] + order[:cut]
        assert rotation_by_polar_form.setdefault(form, rotation) == rotation
        nonzero_polar_count += -1 in form
        unit_count = sum(abs(value) == denominator for value in numerators.values())
        unit_correlation_counts[unit_count] += 1
        if n == 3:
            # Read the words as 000, 011, 101, 110 for distinctions 0, 1, 2.
            lexical_words = (0, 6, 5, 3)
            ternary_details.append({
                "order": order,
                "amplitude_signs": [amplitude[word] for word in lexical_words],
                "correlation_numerators": [numerators[flip] for flip in lexical_words],
                "noncharacter_witness": witness,
            })

    assert carrying_orders == expected_orders
    assert len(set(rotation_by_polar_form.values())) == len(rotation_by_polar_form)
    return {
        "n": n,
        "orders_checked": sum(total for total, _ in by_parity.values()),
        "correlation_denominator": denominator,
        "full_contradictions": len(carrying_orders),
        "full_contradiction_orders": sorted(carrying_orders),
        "full_contradiction_transpositions": carrying_transpositions,
        "parity_counts_total_then_carrying": by_parity,
        "orders_with_nonzero_polar_form": nonzero_polar_count,
        "distinct_polar_forms_including_zero": len(rotation_by_polar_form),
        "orders_by_number_of_unit_correlations_including_empty": unit_correlation_counts,
        "positive_control_nonempty_unit_correlations": sum(
            abs(value) == denominator for flip, value in positive_control.items() if flip
        ),
        "ternary_details": ternary_details,
    }


def reversal_case(n):
    words = even_words(n)
    denominator = len(words)
    amplitude = amplitudes(reversed(range(n)), words)
    for word in words:
        # The even powers of -i alternate between 1 and -1.
        assert amplitude[word] == (1, -1)[(word.bit_count() // 2) % 2]

    numerators = correlations(amplitude, words, n)
    for flip, value in numerators.items():
        # Y on the flipped distinctions contributes i**|T| and each Y or Z
        # contributes -1 on an occupied distinction. Even words cancel the latter.
        y_numerator = sum(sign(flip.bit_count() // 2 + word.bit_count()) for word in words)
        assert value == y_numerator
    witness = noncharacter_witness(numerators, denominator)
    assert witness is not None
    unit_count = sum(abs(value) == denominator for value in numerators.values())
    return {
        "n": n,
        "words_compared_to_quarter_turn": denominator,
        "correlations_compared_to_positive_preparation_with_Y": len(numerators),
        "empty_flip_correlation": numerators[0] // denominator,
        "unit_correlations_including_empty": unit_count,
        "noncharacter_witness": witness,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order-max", type=int, choices=range(3, 8), default=7)
    parser.add_argument("--reversal-max", type=int, choices=range(3, 10), default=9)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "method": "Direct occupied-subsequence inversion counts and exact X/Z correlation sums",
        "order_and_flip_labels": "Zero-based distinctions, bit i selects distinction i",
        "permutation_census": [order_census(n) for n in range(3, args.order_max + 1)],
        "reversal": [reversal_case(n) for n in range(3, args.reversal_max + 1)],
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
