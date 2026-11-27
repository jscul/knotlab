"""Exact product moments and certainty consistency for the Part D referee check.

Each mode covers one amplitude and menu size. The amplitude calculation applies
each Pauli to each supported word. The separate local list enumerates allowed
words and their dual laws. Menu consistency uses only the amplitude moments.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, islice, product
import json
from math import comb, prod
import resource
from time import perf_counter


MODES = {
    "positive-1x2": (1, 2, False),
    "positive-2x2": (2, 2, False),
    "positive-2x3": (2, 3, False),
    "signed-1x2": (1, 2, True),
}

# Each entry gives the resulting bit and the exponent of i for an input bit.
PAULI_ACTION = {
    "I": ((0, 0), (1, 0)),
    "X": ((1, 0), (0, 0)),
    "Y": ((1, 1), (0, 3)),
    "Z": ((0, 0), (1, 2)),
}


def real_paulis(copies):
    return tuple(
        "".join(letters)
        for letters in product("IXYZ", repeat=copies)
        if letters.count("Y") % 2 == 0
    )


def amplitude_moment(reads, amplitudes, copies):
    numerator = 0
    for word, amplitude in amplitudes.items():
        image = []
        phase = 0
        for local_word, read in zip(word, reads):
            local_image = 0
            for place, name in enumerate(read):
                bit = local_word >> place & 1
                image_bit, exponent = PAULI_ACTION[name][bit]
                local_image |= image_bit << place
                phase += exponent
            image.append(local_image)
        assert phase % 2 == 0
        numerator += (-1) ** (phase // 2) * amplitude * amplitudes.get(tuple(image), 0)
    return Fraction(numerator, sum(amplitude**2 for amplitude in amplitudes.values()))


def dot(left, right):
    return (left & right).bit_count() % 2


def local_answers(paulis, support, copies):
    masks = tuple(
        (
            sum(1 << place for place, name in enumerate(read) if name in "XY"),
            sum(1 << place for place, name in enumerate(read) if name in "YZ"),
            read.count("Y") // 2,
        )
        for read in paulis
    )
    laws = [
        law
        for law in product(range(1 << copies), repeat=3)
        if all(sum(dot(a, b) for a, b in zip(law, word)) % 2 == 0 for word in support)
    ]
    return [
        tuple(
            tuple((-1) ** (phase + dot(word_part, z) + dot(law_part, x)) for x, z, phase in masks)
            for word_part, law_part in zip(word, law)
        )
        for word, law in product(support, laws)
    ]


def inconsistent(equations, available_reads):
    pivots = {}
    for read_mask, answer_bit in equations:
        if read_mask & available_reads != read_mask:
            continue
        row = (read_mask << 1) | answer_bit
        while row >= 2:
            pivot = row.bit_length()
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
        if row == 1:
            return True
    return False


def signed_control(moments, paulis, equations):
    certainty_signs = {
        "".join(paulis[index] for index in context): int(moment)
        for context, moment in moments.items()
        if all(context) and abs(moment) == 1
    }
    assert certainty_signs == {"XZZ": 1, "ZXZ": 1, "ZZX": 1, "XXX": -1}
    winning_weights = {}
    for reads, sign in certainty_signs.items():
        context = tuple(map(paulis.index, reads))
        probabilities = []
        for outcomes in product((1, -1), repeat=3):
            total = Fraction(0)
            for subset in product((False, True), repeat=3):
                chosen = tuple(index if use else 0 for index, use in zip(context, subset))
                coefficient = prod(outcome for outcome, use in zip(outcomes, subset) if use)
                total += coefficient * moments[chosen]
            probability = total / 8
            assert probability == (Fraction(1, 4) if prod(outcomes) == sign else 0)
            if prod(outcomes) == sign:
                probabilities.append(probability)
        winning_weights[reads] = str(sum(probabilities))

    score_counts = Counter(
        sum((assignment & mask).bit_count() % 2 == answer for mask, answer in equations if mask)
        for assignment in range(1 << (3 * (len(paulis) - 1)))
    )
    return {
        "amplitude_phase_polynomial": "a*b + b*c + c*a (mod 2)",
        "signs": certainty_signs,
        "winning_weight_by_question": winning_weights,
        "local_assignment_counts_by_questions_won": dict(sorted(score_counts.items())),
        "best_local_score_under_uniform_questions": str(Fraction(max(score_counts), len(certainty_signs))),
    }


def run_mode(mode, limit):
    copies, settings, signed = MODES[mode]
    started = perf_counter()
    if signed:
        amplitudes = {
            (a, b, c): (-1) ** (a * b + b * c + c * a)
            for a, b, c in product(range(2), repeat=3)
        }
    else:
        amplitudes = {(word, word, word): 1 for word in range(1 << copies)}

    paulis = real_paulis(copies)
    local_width = len(paulis) - 1
    identity = "I" * copies
    assert paulis[0] == identity
    answers = [] if signed else local_answers(paulis, tuple(amplitudes), copies)
    moments = {}
    agreements = 0
    equations = []
    moment_counts = Counter()
    certainty_counts = Counter()
    for context in product(range(len(paulis)), repeat=3):
        reads = tuple(paulis[index] for index in context)
        moment = amplitude_moment(reads, amplitudes, copies)
        moments[context] = moment
        active_readers = sum(index != 0 for index in context)
        moment_counts[active_readers] += 1
        if answers:
            answer_sum = sum(row[0][context[0]] * row[1][context[1]] * row[2][context[2]] for row in answers)
            assert moment == Fraction(answer_sum, len(answers)), (reads, moment, answer_sum)
            agreements += 1
        if abs(moment) == 1:
            read_mask = sum(
                1 << (reader * local_width + index - 1)
                for reader, index in enumerate(context)
                if index
            )
            equations.append((read_mask, int(moment < 0)))
            certainty_counts[active_readers] += 1

    moment_seconds = perf_counter() - started
    menu_started = perf_counter()
    menus = [sum(1 << index for index in menu) for menu in combinations(range(local_width), settings)]
    possibilities = product(menus, repeat=3)
    examined = 0
    inconsistent_menus = 0
    for left, middle, right in islice(possibilities, limit):
        examined += 1
        available_reads = left | (middle << local_width) | (right << (2 * local_width))
        inconsistent_menus += inconsistent(equations, available_reads)

    expected = comb(local_width, settings) ** 3
    assert examined == (expected if limit is None else min(limit, expected))
    summary = {
        "copies": copies,
        "nonidentity_real_local_reads": paulis[1:],
        "settings_per_reader": settings,
        "product_moments_by_active_reader_count": dict(sorted(moment_counts.items())),
        "certainty_moments_by_active_reader_count": dict(sorted(certainty_counts.items())),
        "local_list_rows": len(answers),
        "product_moments_matching_local_list": agreements,
        "menu_triples_expected": expected,
        "menu_triples_examined": examined,
        "menu_triples_inconsistent": inconsistent_menus,
        "moment_seconds": moment_seconds,
        "menu_seconds": perf_counter() - menu_started,
    }
    if signed:
        summary["signed_control"] = signed_control(moments, paulis, equations)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", default="all", choices=("all", *MODES))
    parser.add_argument("--limit", type=int, help="Limit the number of menu triples per mode for timing.")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    modes = MODES if args.mode == "all" else (args.mode,)
    results = {mode: run_mode(mode, args.limit) for mode in modes}
    print(json.dumps({"results": results, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}, indent=2))


if __name__ == "__main__":
    main()
