"""Check a supplied weighting on the 13 words of the pair lift by integer sums.

Bits in a printed word are ordered 0 through 8 from left to right. Each word's
probability is the square of its amplitude divided by the squared norm.
"""

from fractions import Fraction
from itertools import product
import json


LAWS = ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8))
READER_A = (0, 1, 3, 4, 5, 6)
READER_B = (7, 8)
UNREAD = (2,)
# Each product of X and Z reads is (flipped distinctions, signed distinctions).
READS_A = (((3, 4), ()), ((), (3,)))
READS_B = (((7, 8), ()), ((), (7,)))


def reached(word):
    old = word[:3]
    if sum(old) % 2:
        return False
    for i, left, right in LAWS[1:]:
        # A 1 passes one occupied distinction. A 0 takes both for an active
        # founder and neither for the quiet founder.
        count = 1 if old[i] else 2 * any(old)
        if word[left] + word[right] != count:
            return False
    return True


def amplitudes():
    words = (w for w in product((0, 1), repeat=9) if reached(w))
    return {w: 10 if w[:3] == (1, 0, 1) and (w[3], w[7]) != (1, 1) else 1
            for w in words}


def numerator(state, a, b):
    flips = set(a[0] + b[0])
    signed = a[1] + b[1]
    total = 0
    for w, amplitude in state.items():
        partner = tuple(bit ^ (i in flips) for i, bit in enumerate(w))
        sign = (-1) ** (sum(w[i] for i in signed) % 2)
        total += sign * amplitude * state.get(partner, 0)
    return total


def certificate():
    assert sorted(READER_A + READER_B + UNREAD) == list(range(9))
    assert all(not (set(law).intersection(READER_A) and
                    set(law).intersection(READER_B)) for law in LAWS)
    state = amplitudes()
    assert len(state) == 13
    norm_squared = sum(amplitude ** 2 for amplitude in state.values())
    entries = [numerator(state, a, b) for a in READS_A for b in READS_B]
    score = Fraction(entries[0] + entries[1] + entries[2] - entries[3], norm_squared)
    assert score > 2
    lift_counts = [[0, 0], [0, 0]]
    for w, amplitude in state.items():
        if w[:3] == (1, 0, 1):
            lift_counts[w[3]][w[7]] += amplitude ** 2
    determinant = lift_counts[0][0] * lift_counts[1][1] - lift_counts[0][1] * lift_counts[1][0]
    assert determinant != 0
    return {
        "weighting": "externally supplied on the pair lift's 13 reached words",
        "word_order": "distinctions 0 through 8, left to right",
        "positive_integer_counts": {"".join(map(str, w)): v * v for w, v in state.items()},
        "total_count": norm_squared,
        "founder_101_counts_by_bit_3_then_bit_7": lift_counts,
        "founder_101_count_determinant": determinant,
        "reader_A": READER_A,
        "reader_B": READER_B,
        "unread": UNREAD,
        "A0_A1": ["X3 X4", "Z3"],
        "B0_B1": ["X7 X8", "Z7"],
        "E00_E01_E10_E11_numerators_over_total_count": entries,
        "CHSH_E00_plus_E01_plus_E10_minus_E11": str(score),
    }


if __name__ == "__main__":
    print(json.dumps(certificate(), indent=2))
