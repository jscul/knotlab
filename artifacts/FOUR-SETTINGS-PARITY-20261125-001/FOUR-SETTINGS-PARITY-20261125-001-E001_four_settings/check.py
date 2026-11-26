"""Replay the four promised settings and controls using exact integer counts."""

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import islice, product
from pathlib import Path


WORDS = tuple(product((0, 1), repeat=3))
ALLOWED_WORDS = tuple(word for word in WORDS if sum(word) % 2 == 0)
PROMISE = {(0, 0, 0): 0, (0, 1, 1): 1, (1, 0, 1): 1, (1, 1, 0): 1}
I_POWERS = ((1, 0), (0, 1), (-1, 0), (0, -1))
DENOMINATOR = 32


def bit_string(word):
    return "".join(map(str, word))


def born_table(flip, coherent):
    """Numerators from products of local eigenbras and the Born rule."""
    # The non-Z eigenbra has coefficients (1, (-1)^answer * phase)
    # before normalization. phase is -i for Y and 1 for X.
    phase = 3 if flip == "Y" else 0
    table = {}
    for settings in WORDS:
        # Source amplitude 1/2 and one 1/sqrt(2) per non-Z read.
        scale = DENOMINATOR // (4 * 2**sum(settings))
        row = []
        for outcomes in WORDS:
            terms = []
            for word in ALLOWED_WORDS:
                if any(choice == 0 and bit != answer
                       for choice, bit, answer in zip(settings, word, outcomes)):
                    continue
                power = sum((phase + 2 * answer) * bit
                            for choice, bit, answer in zip(settings, word, outcomes)
                            if choice)
                terms.append(I_POWERS[power % 4])
            if coherent:
                real = sum(part[0] for part in terms)
                imaginary = sum(part[1] for part in terms)
                row.append(scale * (real**2 + imaginary**2))
            else:
                # The unequal-word cross terms vanish after dephasing.
                row.append(scale * len(terms))
        assert sum(row) == DENOMINATOR
        table[settings] = row
    return table


def target_table(promise):
    return {
        settings: [
            DENOMINATOR // 8 if settings not in promise
            else DENOMINATOR // 4 * (sum(outcomes) % 2 == promise[settings])
            for outcomes in WORDS
        ]
        for settings in WORDS
    }


def win_probability(table):
    wins = sum(table[settings][index]
               for settings, parity in PROMISE.items()
               for index, outcomes in enumerate(WORDS)
               if sum(outcomes) % 2 == parity)
    return Fraction(wins, DENOMINATOR * len(PROMISE))


def deterministic_lists(target):
    wins = Counter()
    optimal = {settings: Counter() for settings in WORDS}
    for answers in product((0, 1), repeat=6):
        outputs = {
            settings: tuple(answers[2 * reader + choice]
                            for reader, choice in enumerate(settings))
            for settings in WORDS
        }
        score = sum(sum(outputs[settings]) % 2 == parity
                    for settings, parity in PROMISE.items())
        wins[score] += 1
        if score == 3:
            for settings, output in outputs.items():
                optimal[settings][output] += 1
    assert wins == {1: 32, 3: 32}
    mixture = {settings: [counts[outcome] for outcome in WORDS]
               for settings, counts in optimal.items()}
    tv = {settings: Fraction(sum(abs(p - q) for p, q in zip(target[settings], row)),
                             2 * DENOMINATOR)
          for settings, row in mixture.items()}
    assert win_probability(mixture) == Fraction(3, 4)
    assert all(distance == (Fraction(1, 4) if settings in PROMISE else 0)
               for settings, distance in tv.items())
    return {
        "win_count_histogram": wins,
        "uniform_three_win_mixture_numerators": named_rows(mixture),
        "total_variation_from_target": {bit_string(s): str(d) for s, d in tv.items()},
        "maximum_uniform_promised_win_probability": "3/4",
    }


def native_sample_functions(target, limit=None):
    """Try every local (setting, own bit) truth table on the uniform sample."""
    matched_counts = Counter()
    best_score = 0
    witness = None
    for answers in islice(product((0, 1), repeat=12), limit):
        rows = {}
        for settings in PROMISE:
            output_counts = Counter(
                tuple(answers[4 * reader + 2 * choice + bit]
                      for reader, (choice, bit) in enumerate(zip(settings, word)))
                for word in ALLOWED_WORDS
            )
            rows[settings] = [DENOMINATOR // 4 * output_counts[outcome]
                              for outcome in WORDS]
        matches = [bit_string(s) for s, row in rows.items() if row == target[s]]
        matched_counts[len(matches)] += 1
        if witness is None or len(matches) > best_score:
            best_score = len(matches)
            witness = {
                "truth_tables_by_reader": [bit_string(answers[i:i + 4])
                                           for i in range(0, len(answers), 4)],
                "matched_settings": matches,
                "promised_numerators": named_rows(rows),
            }
    return {
        "truth_table_entry_order": ["setting 0 bit 0", "setting 0 bit 1",
                                    "setting 1 bit 0", "setting 1 bit 1"],
        "matched_table_count_histogram": matched_counts,
        "maximum_complete_promised_tables_matched": best_score,
        "first_maximum_witness": witness,
    }


def named_rows(table):
    return {bit_string(settings): row for settings, row in table.items()}


def results():
    target = target_table(PROMISE)
    turned = born_table("Y", coherent=True)
    unturned = born_table("X", coherent=True)
    dephased = born_table("Y", coherent=False)
    assert turned == target
    assert win_probability(turned) == 1
    assert win_probability(unturned) == win_probability(dephased) == Fraction(5, 8)
    wrong_target = target_table(PROMISE | {(0, 1, 1): 0})
    assert [s for s in WORDS if turned[s] != wrong_target[s]] == [(0, 1, 1)]
    native = native_sample_functions(target)
    assert sum(native["matched_table_count_histogram"].values()) == 4096
    assert native["maximum_complete_promised_tables_matched"] == 3
    return {
        "bit_order": "readers A, B, C from left to right",
        "setting_bits": {"0": "Z", "1": "Y (X for the unturned control)"},
        "outcome_bits": {"0": "+1", "1": "-1"},
        "setting_and_outcome_order": list(map(bit_string, WORDS)),
        "probability_denominator": DENOMINATOR,
        "allowed_words": list(map(bit_string, ALLOWED_WORDS)),
        "required_outcome_parity": {bit_string(s): parity for s, parity in PROMISE.items()},
        "target_numerators": named_rows(target),
        "born_numerators": named_rows(turned),
        "dephased_numerators": named_rows(dephased),
        "unturned_numerators": named_rows(unturned),
        "uniform_promised_win_probabilities": {
            "coherent_ZY": str(win_probability(turned)),
            "dephased_ZY": str(win_probability(dephased)),
            "coherent_ZX": str(win_probability(unturned)),
        },
        "deliberate_wrong_target": {
            "setting": "011", "substituted_parity": 0, "rejected": True,
        },
        "deterministic_local_lists": deterministic_lists(target),
        "deterministic_native_sample_functions": native,
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
