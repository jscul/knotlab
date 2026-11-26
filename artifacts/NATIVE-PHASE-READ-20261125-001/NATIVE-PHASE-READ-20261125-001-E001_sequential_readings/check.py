"""Census of sequential readings of one four-state parity knot."""

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from functools import reduce
from itertools import islice, permutations, product
from operator import and_
from pathlib import Path


READERS = "ABC"
WORDS = tuple(product((0, 1), repeat=len(READERS)))
OUTCOME_INDEX = {word: index for index, word in enumerate(WORDS)}
STATES = tuple(word for word in WORDS if sum(word) % 2 == 0)
STATE_INDEX = {state: index for index, state in enumerate(STATES)}
ORDERS = tuple(permutations(range(len(READERS))))
TARGET = {
    setting: tuple(int(sum(outcome) % 2 == int(any(setting))) for outcome in WORDS)
    for setting in STATES
}
NONZERO_SETTINGS = STATES[1:]
ACTIVE_PAIRS = tuple(tuple(i for i, choice in enumerate(s) if choice)
                     for s in NONZERO_SETTINGS)


@dataclass(frozen=True)
class Action:
    complement: int
    image: tuple[int, ...]


ACTIONS = tuple(Action(complement, image)
                for complement in (0, 1) for image in permutations(range(len(STATES))))
IDENTITY_IMAGE = tuple(range(len(STATES)))
IDENTITY = Action(0, IDENTITY_IMAGE)


def bit_string(word):
    return "".join(map(str, word))


def order_name(order):
    return "".join(READERS[reader] for reader in order)


def trial(order, setting, actions, state):
    answers = [0] * len(READERS)
    for reader in order:
        answers[reader] = STATES[state][reader]
        if setting[reader]:
            action = actions[reader]
            answers[reader] ^= action.complement
            state = action.image[state]
    return tuple(answers), state


def row(order, setting, actions):
    counts = [0] * len(WORDS)
    for state in range(len(STATES)):
        answers, _ = trial(order, setting, actions, state)
        counts[OUTCOME_INDEX[answers]] += 1
    return tuple(counts)


def pair_scores(orders):
    """Cache complete-table matches for each order and pair of active reads."""
    matrices = []
    for order in orders:
        by_setting = []
        for setting, (first, second) in zip(NONZERO_SETTINGS, ACTIVE_PAIRS):
            actions = [IDENTITY] * len(READERS)
            matrix = []
            for left in ACTIONS:
                actions[first] = left
                line = []
                for right in ACTIONS:
                    actions[second] = right
                    line.append(row(order, setting, actions) == TARGET[setting])
                matrix.append(line)
            by_setting.append(matrix)
        matrices.append(by_setting)
    return matrices


def candidate_masks(matrices, a, b, c):
    # A mask records the matching nonzero settings in order 011, 101, 110.
    return tuple(bc[b][c] + 2 * ac[a][c] + 4 * ab[a][b] for bc, ac, ab in matrices)


def census(matrices, choices, limit=None):
    order_histograms = [Counter() for _ in matrices]
    worst_histogram = Counter()
    common_histogram = Counter()
    joint_histogram = Counter()
    contenders = islice(product(choices, repeat=len(READERS)), limit)
    for candidate in contenders:
        masks = candidate_masks(matrices, *candidate)
        # All candidates match 000 since it leaves the ordinary word unchanged.
        scores = [1 + mask.bit_count() for mask in masks]
        for histogram, score in zip(order_histograms, scores):
            histogram[score] += 1
        worst = min(scores)
        common = 1 + reduce(and_, masks).bit_count()
        worst_histogram[worst] += 1
        common_histogram[common] += 1
        joint_histogram[f"{scores[0]},{worst},{common}"] += 1
    return {
        "candidate_count": sum(worst_histogram.values()),
        "matched_tables_histogram_by_order": {
            order_name(order): histogram for order, histogram in zip(ORDERS, order_histograms)
        },
        "worst_order_matched_tables_histogram": worst_histogram,
        "same_settings_matched_in_every_order_histogram": common_histogram,
        "joint_histogram_ABC_worst_common": joint_histogram,
        "max_matched_tables_in_ABC": max(order_histograms[0]),
        "max_worst_order_matched_tables": max(worst_histogram),
        "max_same_settings_matched_in_every_order": max(common_histogram),
        "perfect_in_ABC": order_histograms[0][len(STATES)],
        "perfect_in_every_order": worst_histogram[len(STATES)],
    }


def xor_words(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


TRANSLATIONS = {
    tuple(STATE_INDEX[xor_words(state, shift)] for state in STATES): shift
    for shift in STATES
}


def verify_translation_masks(matrices, translations):
    """An independent parity formula for the full translation comparison."""
    for candidate in product(translations, repeat=len(READERS)):
        actions = tuple(ACTIONS[index] for index in candidate)
        actual = candidate_masks(matrices, *candidate)
        expected = []
        for order in ORDERS:
            tails = {reader: order[i + 1:] for i, reader in enumerate(order)}
            contribution = [
                action.complement + sum(TRANSLATIONS[action.image][later]
                                        for later in tails[reader])
                for reader, action in enumerate(actions)
            ]
            # With constant shifts the answer word is a constant translation
            # of the initial uniform word, so parity alone decides the match.
            mask = sum((sum(contribution[i] for i in pair) % 2) << index
                       for index, pair in enumerate(ACTIVE_PAIRS))
            expected.append(mask)
        assert actual == tuple(expected)


def candidate_receipt(actions, matrices):
    cache_masks = candidate_masks(matrices, *(ACTIONS.index(action) for action in actions))
    tables, matched, final_state = {}, {}, {}
    for order, mask in zip(ORDERS, cache_masks):
        name = order_name(order)
        tables[name] = {bit_string(s): row(order, s, actions) for s in STATES}
        matches = [s for s in STATES if tables[name][bit_string(s)] == TARGET[s]]
        assert matches == [STATES[0]] + [s for i, s in enumerate(NONZERO_SETTINGS)
                                         if mask & (1 << i)]
        matched[name] = list(map(bit_string, matches))
        final_state[name] = {
            bit_string(s): [bit_string(STATES[trial(order, s, actions, i)[1]])
                            for i in range(len(STATES))]
            for s in STATES
        }
    return {
        "actions_by_reader": {
            reader: {"complement": action.complement,
                     "state_image": [bit_string(STATES[i]) for i in action.image]}
            for reader, action in zip(READERS, actions)
        },
        "matched_settings_by_order": matched,
        "table_numerators_by_order": tables,
        "final_state_by_order_and_setting": final_state,
    }


def record_read(state, records, reader, setting, toggle):
    f, g = records
    if setting:
        return state[reader] ^ f, (f ^ toggle, g ^ toggle)
    return state[reader], records


def record_control(initial_records, toggle):
    """Read one shared record and preserve the added parity rule C XOR f XOR g."""
    tables = {}
    weight = 2 // len(initial_records)
    for order in ORDERS:
        by_setting = {}
        for setting in WORDS:
            counts = [0] * len(WORDS)
            for state, f in product(STATES, initial_records):
                records = (f, state[2] ^ f)
                answers = [0] * len(READERS)
                for reader in order:
                    answers[reader], records = record_read(
                        state, records, reader, setting[reader], toggle
                    )
                    assert records[0] ^ records[1] == state[2]
                assert records[0] == f ^ (toggle * (sum(setting) % 2))
                counts[OUTCOME_INDEX[tuple(answers)]] += weight
            by_setting[setting] = tuple(counts)
        tables[order_name(order)] = by_setting
    return tables


def repeated_record_read(initial_records):
    counts_by_reader = {}
    for reader, name in enumerate(READERS):
        counts = Counter()
        for state, f in product(STATES, initial_records):
            records = (f, state[2] ^ f)
            first, records = record_read(state, records, reader, 1, toggle=1)
            second, records = record_read(state, records, reader, 1, toggle=1)
            assert records == (f, state[2] ^ f)
            counts[bit_string((first, second))] += 1
        assert counts == {"01": 2 * len(initial_records), "10": 2 * len(initial_records)}
        counts_by_reader[name] = {bit_string(word): counts[bit_string(word)]
                                  for word in product((0, 1), repeat=2)}
    return counts_by_reader


def matched_settings(tables, target):
    return {
        name: [bit_string(s) for s, numerators in table.items() if numerators == target[s]]
        for name, table in tables.items()
    }


def record_receipt():
    target = {
        setting: tuple(2 * p for p in TARGET[setting]) if setting in TARGET else (1,) * 8
        for setting in WORDS
    }
    fair = record_control((0, 1), toggle=1)
    reset = record_control((0,), toggle=1)
    frozen = record_control((0, 1), toggle=0)
    assert all(table == target for table in fair.values())
    assert all(matches == list(map(bit_string, STATES))
               for matches in matched_settings(reset, target).values())
    assert all(matches == ["000", "001", "010", "100", "111"]
               for matches in matched_settings(frozen, target).values())
    cases = {}
    for name, tables in (("fair_record", fair), ("reset_record_to_zero", reset),
                         ("frozen_fair_record_mutation", frozen)):
        assert all(table == tables["ABC"] for table in tables.values())
        cases[name] = {
            "table_numerators_identical_in_every_order": {
                bit_string(setting): counts for setting, counts in tables["ABC"].items()
            },
            "matched_settings_by_order": matched_settings(tables, target),
        }
    return {
        "probability_denominator": 8,
        "target_numerators": {bit_string(s): counts for s, counts in target.items()},
        "cases": cases,
        "same_site_setting_1_repeated": {
            "fair": {"denominator": 8, "answer_pair_counts": repeated_record_read((0, 1))},
            "reset": {"denominator": 4, "answer_pair_counts": repeated_record_read((0,))},
        },
    }


def alternative_change(reader, state):
    a, b, c = state
    if reader == 0:
        return a, (1 ^ c, b, 1 ^ a)
    if reader == 1:
        return b, (1 ^ c, 1 ^ b, a)
    # Swap A and C, then report the new C, which is the previous A.
    return a, (c, b, a)


def alternative_receipt():
    tables = {}
    images = {}
    for reader, name in enumerate(READERS):
        images[name] = [alternative_change(reader, word)[1] for word in STATES]
        assert set(images[name]) == set(STATES)
    for order in ORDERS:
        by_setting = {}
        for setting in STATES:
            counts = [0] * len(WORDS)
            for state in STATES:
                answers = [0] * len(READERS)
                for reader in order:
                    if setting[reader]:
                        answers[reader], state = alternative_change(reader, state)
                    else:
                        answers[reader] = state[reader]
                counts[OUTCOME_INDEX[tuple(answers)]] += 1
            by_setting[setting] = tuple(counts)
        tables[order_name(order)] = by_setting
    # In ABC, each nonzero setting returns the original word with C flipped.
    odd_answers = {state[:2] + (state[2] ^ 1,) for state in STATES}
    assert all(tables["ABC"][s] == tuple(int(answer in odd_answers) for answer in WORDS)
               for s in NONZERO_SETTINGS)
    assert tables["ABC"] == TARGET
    matches = matched_settings(tables, TARGET)
    assert matches == {
        "ABC": ["000", "011", "101", "110"],
        "ACB": ["000", "101"],
        "BAC": ["000", "101"],
        "BCA": ["000", "011", "110"],
        "CAB": ["000"],
        "CBA": ["000"],
    }
    return {
        "state_images_by_reader": {name: list(map(bit_string, image))
                                   for name, image in images.items()},
        "readout_by_reader": {"A": "old A", "B": "old B", "C": "old A"},
        "table_numerators_by_order": {
            name: {bit_string(s): counts for s, counts in table.items()}
            for name, table in tables.items()
        },
        "matched_settings_by_order": matches,
    }


def results():
    matrices = pair_scores(ORDERS)
    all_actions = census(matrices, range(len(ACTIONS)))
    identities = [i for i, action in enumerate(ACTIONS) if action.image == IDENTITY_IMAGE]
    translations = [i for i, action in enumerate(ACTIONS) if action.image in TRANSLATIONS]
    identity_stats = census(matrices, identities)
    translation_stats = census(matrices, translations)
    verify_translation_masks(matrices, translations)
    assert all_actions["candidate_count"] == (2 * 24)**3
    assert translation_stats["candidate_count"] == (2 * 4)**3
    assert identity_stats["candidate_count"] == 2**3
    assert all(stats["max_matched_tables_in_ABC"] ==
               stats["max_worst_order_matched_tables"] == 3
               for stats in (all_actions, identity_stats, translation_stats))
    assert all_actions["perfect_in_ABC"] == all_actions["perfect_in_every_order"] == 0
    # Independent counting uses the three possible images of the first read
    # under A's permutation, with 8 permutations for each image direction.
    assert all_actions["matched_tables_histogram_by_order"]["ABC"] == {
        1: 70_656, 2: 30_720, 3: 9_216,
    }
    # Matching across orders forces both changes in each matched pair to
    # preserve the third bit and act as the required constant translation.
    assert all_actions["same_settings_matched_in_every_order_histogram"] == {
        1: 110_022, 2: 564, 3: 6,
    }
    assert all(hist == all_actions["matched_tables_histogram_by_order"]["ABC"]
               for hist in all_actions["matched_tables_histogram_by_order"].values())
    # B flips A and C after reading. This is visible in the final state,
    # and flips exactly one later answer in ABC when B uses setting 1.
    shift = next(image for image, word in TRANSLATIONS.items() if word == (1, 0, 1))
    fixed_witness = candidate_receipt((IDENTITY, Action(0, shift), IDENTITY), matrices)
    stable_witness = candidate_receipt((IDENTITY, IDENTITY, Action(1, IDENTITY_IMAGE)),
                                       matrices)
    return {
        "reader_order_in_words": READERS,
        "initial_word_order_and_scored_settings": list(map(bit_string, STATES)),
        "outcome_order": list(map(bit_string, WORDS)),
        "probability_denominator": len(STATES),
        "target_numerators": {bit_string(s): counts for s, counts in TARGET.items()},
        "all_reversible_actions": all_actions,
        "identity_transitions": identity_stats,
        "translation_transitions": translation_stats,
        "state_changing_ABC_witness": fixed_witness,
        "all_order_identity_witness": stable_witness,
        "added_record_control": record_receipt(),
        "alternative_readout_control": alternative_receipt(),
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
