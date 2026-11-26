#!/usr/bin/env python3
"""Exact referee replay from the parity, order and measurement definitions.

Run with python3 -B block.py to emit the JSON receipt. No study code or
recorded outputs are read. Bits within a setting, outcome or parent word
are printed in reader order a, b, c. The baseline listing names the children
in production order, abc.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from math import prod


READERS = "abc"
ORDERS = tuple(map("".join, permutations(READERS)))
LABELS = range(8)
PARENT = dict(zip(READERS, (4, 2, 1)))
FRESH = {reader: (8 << (2 * index), 16 << (2 * index))
         for index, reader in enumerate(READERS)}
EVEN = tuple(label for label in LABELS if label.bit_count() % 2 == 0)
TARGET_SIGNS = {setting: 1 if setting == 0 else -1 for setting in EVEN}


def bit_string(value):
    return f"{value:03b}"


def nine_bits(word):
    pairs = ("".join(str(int(bool(word & bit))) for bit in FRESH[reader])
             for reader in READERS)
    return "|".join((bit_string(word & 7), *pairs))


def listing(order):
    return tuple(PARENT.values()) + tuple(bit for reader in order for bit in FRESH[reader])


def inversions(reference, order):
    ranks = {item: index for index, item in enumerate(order)}
    return tuple((a, b) for a, b in combinations(reference, 2) if ranks[a] > ranks[b])


def occupied_sign(word, crossed_pairs, swap):
    return swap ** sum((word & (left | right)) == (left | right) for left, right in crossed_pairs)


def grown_words():
    return tuple(word for word in range(512) if (word & 7) in EVEN
                 and all(bool(word & PARENT[reader]) == (word & (y | z)).bit_count() % 2
                         for reader, (y, z) in FRESH.items()))


def preparation(words, reference, order, swap=-1):
    crossings = inversions(listing(reference), listing(order))
    return {word: occupied_sign(word, crossings, swap) for word in words}


def projected_table(state, flip_by_reader):
    # In a flip orbit, set the active old bits of its representative to zero.
    # An outcome is a Walsh character on that orbit. Distinct orbits are
    # orthogonal, so square their signed sums separately before adding.
    flips = {label: sum(flip_by_reader[r] for r in READERS if label & PARENT[r])
             for label in LABELS}
    norm = sum(amplitude ** 2 for amplitude in state.values())
    rows = []
    for setting in LABELS:
        ordinary = 7 ^ setting
        denominator = norm << setting.bit_count()
        probabilities = []
        for outcome in LABELS:
            sums = defaultdict(int)
            for word, amplitude in state.items():
                if (word ^ outcome) & ordinary:
                    continue
                active = word & setting
                sums[word ^ flips[active]] += (-1) ** (active & outcome).bit_count() * amplitude
            probabilities.append(Fraction(sum(value ** 2 for value in sums.values()), denominator))
        assert sum(probabilities) == 1
        rows.append(tuple(probabilities))
    return tuple(rows)


def benchmark():
    return tuple(tuple(Fraction(1, 8) if setting not in EVEN
                       else Fraction(int((-1) ** outcome.bit_count() == TARGET_SIGNS[setting]), 4)
                       for outcome in LABELS) for setting in LABELS)


def dephased_benchmark():
    positive = benchmark()[0]
    uniform = (Fraction(1, 8),) * 8
    return (positive,) + (uniform,) * 7


def full_correlations(table):
    return tuple(sum((-1) ** outcome.bit_count() * row[outcome] for outcome in LABELS)
                 for row in table)


def fixed_mermin(correlations):
    return sum(sign * correlations[setting] for setting, sign in TARGET_SIGNS.items())


def correlated_outcome_flip(setting, z_mask, x_mask):
    return (z_mask & (7 ^ setting)) | (x_mask & setting)


def outcome_relabel(table, z_mask, x_mask):
    return tuple(tuple(row[outcome ^ correlated_outcome_flip(setting, z_mask, x_mask)]
                       for outcome in LABELS) for setting, row in enumerate(table))


def probability_record(table):
    return {bit_string(setting): list(map(str, row)) for setting, row in enumerate(table)}


def readout_record(table, target):
    correlations = full_correlations(table)
    product_even = prod(correlations[setting] for setting in EVEN)
    matches = tuple((z_mask, x_mask) for z_mask, x_mask in product(LABELS, repeat=2)
                    if outcome_relabel(table, z_mask, x_mask) == target)
    return {
        "probabilities": probability_record(table),
        "full_correlations": {bit_string(i): str(correlations[i]) for i in LABELS},
        "product_even_correlations": str(product_even),
        "full_contradiction": product_even == -1,
        "fixed_label_mermin": str(fixed_mermin(correlations)),
        "fixed_label_win": str(Fraction(1, 2) + fixed_mermin(correlations) / 8),
        "fixed_label_exact_cells": sum(p == q for row, goal in zip(table, target)
                                       for p, q in zip(row, goal)),
        "target_matching_x_outcome_relabels": [bit_string(x) for z, x in matches if z == 0],
        "target_matching_z_and_x_outcome_relabels": [{"z": bit_string(z), "x": bit_string(x)}
                                                     for z, x in matches],
    }


def mixture_record(tables):
    mean = tuple(tuple(sum(cell) / len(tables) for cell in zip(*setting_rows))
                 for setting_rows in zip(*tables))
    correlations = full_correlations(mean)

    # Choose outcome reversals and swaps of the two setting names once, with
    # no access to the order of any trial. The measurement operators stay Z, X.
    best = max(abs(sum(sign * (-1) ** correlated_outcome_flip(setting, z, x).bit_count()
                       * correlations[setting ^ switch] for setting, sign in TARGET_SIGNS.items()))
               for z, x, switch in product(LABELS, repeat=3))

    # Use A0=Z, A1=sign(t)*X and B0,B1 along Z-r*X,-Z-r*X, normalized.
    # C0=Z and C1=(24*Z+7*X)/25 give distinct real readings at every reader.
    # The B normalization is the same in all four terms, so verify the score
    # by rational multilinearity and compare its square to the local bound.
    t = correlations[6]
    r = abs(t)
    t_sign = 1 if t > 0 else -1
    directions = (((1, 0), (0, t_sign)), ((1, -r), (-1, -r)),
                  ((1, 0), (Fraction(24, 25), Fraction(7, 25))))
    numerator = sum(sign * correlations[term] * prod(
        directions[i][int(bool(setting & bit))][int(bool(term & bit))]
        for i, bit in enumerate(PARENT.values()))
        for setting, sign in TARGET_SIGNS.items() for term in LABELS)
    squared_norm = 1 + t ** 2
    squared_score = numerator ** 2 / squared_norm
    assert squared_score > 4
    return {
        "probabilities": probability_record(mean),
        "full_correlations": {bit_string(i): str(correlations[i]) for i in LABELS},
        "fixed_label_mermin": str(fixed_mermin(correlations)),
        "best_mermin_with_fixed_z_and_x_operators": str(best),
        "best_win_with_fixed_z_and_x_operators": str(Fraction(1, 2) + best / 8),
        "real_reading_change_witness": {
            "unnormalized_z_x_directions": [[[str(component) for component in direction]
                                              for direction in reader] for reader in directions],
            "mermin_numerator": str(numerator),
            "mermin_denominator_squared": str(squared_norm),
            "mermin_squared": str(squared_score),
        },
    }


def coherent_record(states, order_weights):
    amplitudes = {word: sum(order_weights[order] * state[word] for order, state in states.items())
                  for word in next(iter(states.values()))}
    survivors = {word: amplitude for word, amplitude in amplitudes.items() if amplitude}
    return {
        "parent_word_count": len({word & 7 for word in survivors}),
        "parent_words": sorted({bit_string(word & 7) for word in survivors}),
        "nine_bit_word_count": len(survivors),
        "unnormalized_nine_bit_amplitudes": dict(sorted((nine_bits(w), a) for w, a in survivors.items())),
    }


def main():
    words = grown_words()
    target = benchmark()
    block_flips = {r: PARENT[r] | FRESH[r][0] for r in READERS}
    tables_by_phase = {}
    reference_sweep = {}
    baseline_tables = {}
    baseline_states = {}
    positive_states = {}
    fresh_choices_matched = 0

    for reference in ORDERS:
        order_phases = {}
        for order in ORDERS:
            state = preparation(words, reference, order)
            reversed_parents = tuple(PARENT[a] | PARENT[b] for a, b in inversions(reference, order))
            assert all(state[word] == (-1) ** sum(word & pair == pair for pair in reversed_parents)
                       for word in words)
            parent_signs = {word & 7: amplitude for word, amplitude in state.items()}
            phase = "".join("+" if parent_signs[parent] == 1 else "-" for parent in EVEN)
            table = projected_table(state, block_flips)
            if phase not in tables_by_phase:
                tables_by_phase[phase] = readout_record(table, target)
            assert tables_by_phase[phase]["probabilities"] == probability_record(table)
            assert tables_by_phase[phase]["full_contradiction"] == (len(reversed_parents) % 2 == 1)
            assert projected_table(state, PARENT) == dephased_benchmark()
            order_phases[order] = phase
            if reference == READERS:
                baseline_tables[order] = table
                baseline_states[order] = state
                positive_states[order] = preparation(words, reference, order, swap=1)
                for choices in product((0, 1), repeat=3):
                    chosen_flips = {r: PARENT[r] | FRESH[r][i] for r, i in zip(READERS, choices)}
                    fresh_choices_matched += projected_table(state, chosen_flips) == table
        reference_sweep[reference] = order_phases

    assert len(words) == 32
    assert fresh_choices_matched == 48
    assert [order for order, table in baseline_tables.items() if table == target] == ["cba"]
    positive_table = projected_table(positive_states[READERS], block_flips)
    assert all(projected_table(state, block_flips) == positive_table for state in positive_states.values())
    odd_orders = [order for order in ORDERS if len(inversions(READERS, order)) % 2]
    weights_one = dict.fromkeys(ORDERS, 1)
    weights_parity = {order: (-1) ** len(inversions(READERS, order)) for order in ORDERS}
    coherent = coherent_record(baseline_states, weights_one)
    assert coherent["parent_words"] == ["000"] and coherent["nine_bit_word_count"] == 8
    return {
        "baseline_reference": READERS,
        "outcomes_in_probability_row": [bit_string(i) for i in LABELS],
        "parent_words_in_phase_string": [bit_string(i) for i in EVEN],
        "nine_bit_word_format": "abc|a's fresh pair|b's fresh pair|c's fresh pair",
        "grown_word_count": len(words),
        "target": probability_record(target),
        "reference_then_commit_to_phase": reference_sweep,
        "readout_by_phase": tables_by_phase,
        "controls": {
            "old_only_every_reference_and_order": readout_record(dephased_benchmark(), target),
            "swap_plus_one_every_baseline_order": readout_record(positive_table, target),
            "fresh_bit_choice_tables_matching_first": {"matched": fresh_choices_matched, "tested": 48},
        },
        "equal_mixtures_with_order_unavailable": {
            "odd_orders": {"orders": odd_orders, **mixture_record([baseline_tables[o] for o in odd_orders])},
            "all_orders": {"orders": ORDERS, **mixture_record(list(baseline_tables.values()))},
        },
        "coherent_order_sums": {
            "uniform": coherent,
            "sign_of_order": coherent_record(baseline_states, weights_parity),
            "uniform_swap_plus_one": coherent_record(positive_states, weights_one),
            "reason": "For each word, only inversions between its odd children contribute to the sign. "
                      "With two odd children, transposing those children pairs each order with an "
                      "opposite sign. This pairing also works with more than two odd children. "
                      "With zero or one odd child, every term has sign +1.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
