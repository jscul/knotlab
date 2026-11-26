"""Replay the documented even-ternary contraction in fixed and transported frames."""

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import islice, product
from math import prod
from pathlib import Path


WORDS = tuple(product((0, 1), repeat=3))
WORD_INDEX = {word: i for i, word in enumerate(WORDS)}
EVEN = tuple(word for word in WORDS if sum(word) % 2 == 0)
DENOMINATOR = 32
I_POWERS = ((1, 0), (0, 1), (-1, 0), (0, -1))
X_ANGLE = 0
Y_ANGLE = 1
NEGATIVE_Y_ANGLE = 3


def name(word):
    return "".join(map(str, word))


def named_rows(table):
    return {name(setting): row for setting, row in table.items()}


def dot_parity(first, second):
    return sum(a * b for a, b in zip(first, second)) % 2


def gaussian_terms(terms):
    real = sum(sign * I_POWERS[exponent % 4][0] for sign, exponent in terms)
    imaginary = sum(sign * I_POWERS[exponent % 4][1] for sign, exponent in terms)
    return real, imaginary


def target_table():
    table = {}
    for setting in WORDS:
        table[setting] = tuple(
            DENOMINATOR // 8 if sum(setting) % 2 else
            DENOMINATOR // 4 * (sum(outcome) % 2 == int(any(setting)))
            for outcome in WORDS
        )
    return table


def gaussian_projection(signs, angle):
    """Use the product of local eigenbras and square the integer amplitude."""
    table = {}
    for setting in WORDS:
        counts = []
        for answers in WORDS:
            terms = []
            for word, sign in zip(EVEN, signs):
                if any(not choice and bit != answer
                       for choice, bit, answer in zip(setting, word, answers)):
                    continue
                exponent = sum((2 * answer - angle) * bit
                               for choice, bit, answer in zip(setting, word, answers)
                               if choice)
                terms.append((sign, exponent))
            real, imaginary = gaussian_terms(terms)
            # Source amplitudes 1/2, one 1/sqrt(2) per changed question.
            counts.append((real**2 + imaginary**2) * (DENOMINATOR // (4 * 2**sum(setting))))
        assert sum(counts) == DENOMINATOR
        table[setting] = tuple(counts)
    return table


def pauli_moments(signs, angle, dephased=False):
    """Independent computation from ket action and binary moment inversion."""
    amplitudes = dict(zip(EVEN, signs))
    table = {}
    for setting in WORDS:
        moments = {}
        for subset in WORDS:
            terms = []
            for word, sign in amplitudes.items():
                moved = tuple(bit ^ (choice & include)
                              for bit, choice, include in zip(word, setting, subset))
                if moved not in amplitudes or (dephased and moved != word):
                    continue
                exponent = sum((angle * (1 - 2 * bit) if choice else 2 * bit)
                               for bit, choice, include in zip(word, setting, subset)
                               if include)
                terms.append((amplitudes[moved] * sign, exponent))
            real, imaginary = gaussian_terms(terms)
            assert imaginary == 0
            moments[subset] = real
        # The source norm squared is 4 and inversion adds a factor of 8.
        table[setting] = tuple(sum((1 - 2 * dot_parity(subset, outcome)) * value
                                   for subset, value in moments.items())
                               for outcome in WORDS)
    return table


def scores(table):
    target = target_table()
    moments = {}
    for setting, row in table.items():
        numerator = sum((1 - 2 * (sum(outcome) % 2)) * weight
                        for outcome, weight in zip(WORDS, row))
        moments[setting] = Fraction(numerator, DENOMINATOR)
    mermin = moments[EVEN[0]] - sum(moments[setting] for setting in EVEN[1:])
    wins = sum(weight for setting in EVEN for outcome, weight in zip(WORDS, table[setting])
               if sum(outcome) % 2 == int(any(setting)))
    success = Fraction(wins, len(EVEN) * DENOMINATOR)
    assert success == Fraction(1, 2) + mermin / 8
    return {
        "full_correlations": {name(setting): str(value) for setting, value in moments.items()},
        "mermin": str(mermin),
        "uniform_promised_win_probability": str(success),
        "target_tables_matched": sum(table[setting] == row for setting, row in target.items()),
        "target_cells_matched": sum(actual == expected for setting, row in target.items()
                                    for actual, expected in zip(table[setting], row)),
    }


def contract_witness():
    """The October one-witness parity form and the documented pairwise gauge."""
    rows = {}
    for word in WORDS:
        factors = [tuple((-1)**(h * bit) for bit in word) for h in (0, 1)]
        terms = tuple(prod(branch) for branch in factors)
        net = sum(terms)
        count_factor = (1 + (-1)**sum(word)) // 2
        assert net == 2 * count_factor
        # Move an h-dependent sign from one factor to the witness weight.
        # The terms are unchanged only when both sides are transported.
        compensated = tuple((-1)**h * ((-1)**h * branch[0]) * prod(branch[1:])
                            for h, branch in enumerate(factors))
        assert compensated == terms
        uncompensated = sum((-1)**h * term for h, term in enumerate(terms))
        assert uncompensated == 2 - net
        pair_gauge = (-1)**(word[0] * word[1])
        rows[name(word)] = {
            "visible_factors_by_hidden_bit": factors,
            "signed_terms_by_hidden_bit": terms,
            "net_integer_weight": net,
            "november_count_factor": count_factor,
            "compensated_internal_gauge_terms": compensated,
            "uncompensated_internal_gauge_net": uncompensated,
            "october_pair_gauge": pair_gauge,
            "net_weight_with_pair_gauge": net * pair_gauge,
        }
    canonical = tuple(rows[name(w)]["net_integer_weight"] // 2 for w in EVEN)
    historic = tuple(rows[name(w)]["net_weight_with_pair_gauge"] // 2 for w in EVEN)
    return rows, canonical, historic


def quarter_rephase(signs):
    """Apply diag(1,-i) at all three sites, restricted to the even words."""
    result = []
    for word, sign in zip(EVEN, signs):
        real, imaginary = I_POWERS[(-sum(word)) % 4]
        assert imaginary == 0
        result.append(sign * real)
    return tuple(result)


def local_character(signs):
    # The two representatives differ by the even support's all-ones check.
    return next(bits for bits in WORDS
                if all(sign == signs[0] * (-1)**dot_parity(bits, word)
                       for word, sign in zip(EVEN, signs)))


def local_mixture(flips):
    """Uniform allowed value word and independent common fair flip answer."""
    table = {}
    for setting in WORDS:
        row = [0] * len(WORDS)
        for word, shared_bit in product(EVEN, (0, 1)):
            answer = tuple((shared_bit ^ flip) if choice else bit
                           for bit, flip, choice in zip(word, flips, setting))
            row[WORD_INDEX[answer]] += DENOMINATOR // 8
        table[setting] = tuple(row)
    return table


def relabel_second_outcomes(table, flips):
    relabeled = {}
    for setting, source in table.items():
        row = []
        for word in WORDS:
            renamed = tuple(bit ^ (choice & flip)
                            for bit, choice, flip in zip(word, setting, flips))
            row.append(source[WORD_INDEX[renamed]])
        relabeled[setting] = tuple(row)
    return relabeled


def local_receipt(signs, angle, table):
    in_x_frame = signs if angle == X_ANGLE else quarter_rephase(signs)
    if prod(in_x_frame) == 1:
        flips = local_character(in_x_frame)
        assert local_mixture(flips) == table
        return {"admits_common_local_explanation": True, "local_list_second_setting_flips": flips}
    in_y_frame = signs if angle == Y_ANGLE else quarter_rephase(signs)
    flips = local_character(in_y_frame)
    assert relabel_second_outcomes(target_table(), flips) == table
    return {"admits_common_local_explanation": False, "relabeling_to_ideal_table": flips}


def classical_dephased():
    table = {}
    for setting in WORDS:
        row = []
        for outcome in WORDS:
            retained = sum(all(choice or bit == answer for choice, bit, answer in
                               zip(setting, word, outcome)) for word in EVEN)
            row.append(retained * (DENOMINATOR // (4 * 2**sum(setting))))
        table[setting] = tuple(row)
        assert sum(row) == DENOMINATOR
    return table


def local_bound():
    histogram = Counter()
    for answers in product((0, 1), repeat=6):
        wins = sum(sum(answers[2 * i + choice] for i, choice in enumerate(s)) % 2 == int(any(s))
                   for s in EVEN)
        histogram[wins] += 1
    assert histogram == {1: 32, 3: 32}
    return {
        "deterministic_assignment_win_count_histogram": histogram,
        "fixed_mermin_bound": 2,
        "uniform_promised_win_probability_bound": "3/4",
    }


def measured_table(signs, angle):
    table = gaussian_projection(signs, angle)
    assert table == pauli_moments(signs, angle)
    return table


def sign_label(signs):
    return "".join("+" if sign == 1 else "-" for sign in signs)


def census(limit=None):
    records = {}
    for signs in islice(product((1, -1), repeat=len(EVEN)), limit):
        key = sign_label(signs)
        paired = {}
        for menu, angle in (("ZX", X_ANGLE), ("ZY", Y_ANGLE)):
            table = measured_table(signs, angle)
            paired[menu] = {
                **scores(table),
                **local_receipt(signs, angle, table),
                "numerators": named_rows(table),
            }
        records[key] = paired
    return records


def results():
    contractions, canonical, historic = contract_witness()
    assert canonical == (1, 1, 1, 1) and historic == (1, 1, 1, -1)
    positive_control = quarter_rephase(canonical)
    # The archive gives orbit signs (1, -1) for the weight-zero and
    # weight-two even words independently of the calibration.
    historic_symmetric = tuple(1 if sum(word) == 0 else -1 for word in EVEN)
    assert positive_control == historic_symmetric
    assert positive_control == tuple((-1)**(a*b + a*c + b*c) for a, b, c in EVEN)
    rephase_input = measured_table(positive_control, Y_ANGLE)
    rephase_reader = measured_table(canonical, X_ANGLE)
    original = measured_table(canonical, Y_ANGLE)
    both = measured_table(positive_control, X_ANGLE)
    assert original == both == target_table()
    assert rephase_input == rephase_reader
    assert measured_table(canonical, NEGATIVE_Y_ANGLE) == original
    assert rephase_input != original and rephase_reader != original
    assert measured_table(historic, Y_ANGLE) != original
    records = census()
    assert len(records) == 16
    for table in ("ZX", "ZY"):
        assert sum(row[table]["admits_common_local_explanation"] for row in records.values()) == 8
        assert Counter(row[table]["mermin"] for row in records.values()) == {"0": 6, "1": 8, "4": 2}
    dephased = classical_dephased()
    assert all(dephased == pauli_moments(historic, angle, dephased=True)
               for angle in (X_ANGLE, Y_ANGLE))
    assert scores(dephased)["uniform_promised_win_probability"] == "5/8"
    frames = {
        "fixed_ZY_and_canonical_source": original,
        "source_only_rephased_fixed_ZY": rephase_input,
        "reader_only_rephased_canonical_source_ZX": rephase_reader,
        "source_and_reader_cotransported_ZX_all_real_control": both,
        "opposite_turn_Z_negative_Y_with_canonical_source": measured_table(canonical, NEGATIVE_Y_ANGLE),
    }
    return {
        "allowed_word_order": list(map(name, EVEN)),
        "setting_and_outcome_order": list(map(name, WORDS)),
        "word_and_setting_bits_ordered_by_reader": "ABC",
        "outcome_bits": {"0": "+1", "1": "-1"},
        "probability_denominator": DENOMINATOR,
        "target_numerators": named_rows(target_table()),
        "contraction_sources": [
            "proofs/INTERFERENCE-20261029-001A/INTERFERENCE-20261029-001A-P001_one_cancelling_witness_per_knot/proof.md",
            "proofs/INTERFERENCE-20261029-001B/INTERFERENCE-20261029-001B-P001_signed_laws_survive_native_coarse_graining/proof.md",
            "proofs/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A-P001_counts/proof.md",
        ],
        "contraction": contractions,
        "canonical_signs": canonical,
        "documented_october_pair_gauge_signs": historic,
        "documented_october_rotation_invariant_signs": [canonical, historic_symmetric],
        "transported_all_real_signs": positive_control,
        "named_sources_in_assignment_census": {
            "canonical_witness_and_positive_symmetric": sign_label(canonical),
            "october_signed_symmetric": sign_label(historic_symmetric),
            "october_single_pair_gauge": sign_label(historic),
        },
        "calibration_controls": {key: {**scores(table), "numerators": named_rows(table)}
                                 for key, table in frames.items()},
        "classical_fair_change_or_quantum_dephased": {
            **scores(dephased), "numerators": named_rows(dephased)
        },
        "local_bound": local_bound(),
        "all_real_sign_assignments": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with results.json")
    args = parser.parse_args()
    rendered = json.dumps(results(), indent=2, sort_keys=True) + "\n"
    if args.check:
        recorded = Path(__file__).with_name("results.json").read_text(encoding="utf-8")
        if recorded != rendered:
            raise SystemExit("results.json differs from the replay")
        print("results.json matches the exact replay")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
