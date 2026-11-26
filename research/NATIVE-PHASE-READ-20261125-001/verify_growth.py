"""Replay the first fewest-birth parity round and its alternative readouts.

Run with the repository's .venv/bin/python -B. Results are printed as JSON.
"""

import json
import sys
from collections import Counter
from itertools import permutations, product
from pathlib import Path
from runpy import run_path


ROOT = Path(__file__).resolve().parents[2]
READERS = "ABC"
ORDERS = tuple(permutations(range(len(READERS))))
OUTCOMES = tuple(product((0, 1), repeat=len(READERS)))
OUTCOME_INDEX = {word: i for i, word in enumerate(OUTCOMES)}
TARGET_DENOMINATOR = 8
TARGET = {
    setting: tuple(
        1 if sum(setting) % 2 else 2 * (sum(outcome) % 2 == int(any(setting)))
        for outcome in OUTCOMES
    )
    for setting in OUTCOMES
}


def bit_string(word):
    return "".join(map(str, word))


def growth():
    source = ROOT / "experiments" / "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A"
    archive = next(source.glob("*-E001_*"))
    sys.path.insert(0, str(archive))
    try:
        from ordinary import advance
    finally:
        sys.path.remove(str(archive))
    root = (0, 1, 2)
    event, holdings = advance((root,), "parity")
    assert event["status"] == "grown" and event["births"] == 3
    assert all(child["parents"] == 1 and child["demand"] == child["fresh"] == 2
               for child in event["new"])
    referee = run_path(str(ROOT / "research" / "FRESH-COUNT-20261118-001" /
                           "referee-R1" / "referee_fresh.py"))
    reconstruction = referee["Growth"](3)
    assert reconstruction.step(referee["fewest"]) == "ok"
    assert holdings == reconstruction.bits
    pairs = tuple(tuple(bit for bit in child["places"] if bit not in root)
                  for child in event["new"])
    assert [tuple(b for b in child["places"] if b in root)
            for child in event["new"]] == [(0,), (1,), (2,)]
    assert not set.intersection(*(set(holding) for holding in holdings[1:]))
    return event, holdings, pairs


def check_growth(holdings, pairs, words):
    conditional = {}
    for root in OUTCOMES:
        fresh_counts = Counter(bit_string(word[pair[0]] for pair in pairs)
                               for word in words if word[:len(READERS)] == root)
        independent = {bit_string(word): 1 for word in OUTCOMES}
        assert fresh_counts == (independent if sum(root) % 2 == 0 else {})
        if fresh_counts:
            conditional[bit_string(root)] = fresh_counts
    for i, (f, g) in enumerate(pairs):
        assert all(word[f] ^ word[g] == word[i] for word in words)
        assert all(f not in held and g not in held
                   for j, held in enumerate(holdings) if j != i + 1)

    # Every permutation of the three root names extends to the grown holdings.
    held_sets = {frozenset(row) for row in holdings}
    for order in ORDERS:
        renamed = dict(enumerate(order))
        for old, new in zip(pairs, (pairs[i] for i in order)):
            renamed.update(zip(old, new))
        assert {frozenset(renamed[b] for b in held) for held in holdings} == held_sets
    return conditional


def read(word, reader, setting, pair, toggle):
    answer = word[reader]
    if setting:
        f, g = pair
        answer ^= word[f]
        updated = list(word)
        updated[f] ^= toggle
        updated[g] ^= toggle
        word = tuple(updated)
    return answer, word


def treatment(pairs, initial, lawful, toggle=1):
    match_by_order, tables = {}, {}
    for order in ORDERS:
        name = "".join(READERS[i] for i in order)
        table = {}
        match_by_order[name] = []
        for setting in OUTCOMES:
            counts = [0] * len(OUTCOMES)
            for initial_word in initial:
                word = initial_word
                answers = [0] * len(READERS)
                for reader in order:
                    answers[reader], word = read(
                        word, reader, setting[reader], pairs[reader], toggle
                    )
                    assert word in lawful and word[:len(READERS)] == initial_word[:len(READERS)]
                counts[OUTCOME_INDEX[tuple(answers)]] += 1
            table[bit_string(setting)] = counts
            if all(TARGET_DENOMINATOR * actual == len(initial) * expected
                   for actual, expected in zip(counts, TARGET[setting])):
                match_by_order[name].append(bit_string(setting))
        tables[name] = table
    assert all(table == tables["ABC"] for table in tables.values())
    repeats = {}
    for reader, name in enumerate(READERS):
        counts = dict.fromkeys(("00", "01", "10", "11"), 0)
        for initial_word in initial:
            first, word = read(initial_word, reader, 1, pairs[reader], toggle)
            second, word = read(word, reader, 1, pairs[reader], toggle)
            assert word == initial_word and first ^ second == toggle
            counts[bit_string((first, second))] += 1
        repeats[name] = counts
    return {
        "initial_word_count": len(initial),
        "chosen_pairs_by_reader": dict(zip(READERS, pairs)),
        "numerators_identical_in_every_order": tables["ABC"],
        "matched_settings_by_order": match_by_order,
        "same_site_setting_1_pair_counts": repeats,
    }


def verify():
    event, holdings, pairs = growth()
    words = tuple(word for word in product((0, 1), repeat=event["distinctions"])
                  if all(sum(word[b] for b in held) % 2 == 0 for held in holdings))
    assert len(words) == 32
    lawful = set(words)
    conditional = check_growth(holdings, pairs, words)
    local = treatment(pairs, words, lawful)
    local_matches = ["000", "001", "010", "100", "111"]
    assert all(matches == local_matches for matches in local["matched_settings_by_order"].values())
    # Swapping which member reports the pair's bit at any reader changes no
    # table. Conditional on the root it complements an independent fair bit.
    for choices in OUTCOMES:
        recoded = tuple(pair[::(-1 if choice else 1)] for pair, choice in zip(pairs, choices))
        assert treatment(recoded, words, lawful)["numerators_identical_in_every_order"] == (
            local["numerators_identical_in_every_order"]
        )
    shared = {}
    for name, pair in zip(READERS, pairs):
        result = treatment((pair,) * len(READERS), words, lawful)
        assert all(matches == list(map(bit_string, OUTCOMES))
                   for matches in result["matched_settings_by_order"].values())
        shared[name] = result
    pair = pairs[0]
    reset = treatment((pair,) * len(READERS), [w for w in words if w[pair[0]] == 0], lawful)
    assert all(matches == ["000", "011", "101", "110"]
               for matches in reset["matched_settings_by_order"].values())
    frozen = treatment((pair,) * len(READERS), words, lawful, toggle=0)
    assert all(matches == local_matches for matches in frozen["matched_settings_by_order"].values())
    return {
        "growth": event,
        "holdings": holdings,
        "allowed_word_count": len(words),
        "free_bit_counts_conditioned_on_root_word": conditional,
        "checked_root_relabellings": len(ORDERS),
        "common_holding_among_child_readers": [],
        "outcome_order": list(map(bit_string, OUTCOMES)),
        "target_denominator": TARGET_DENOMINATOR,
        "target_numerators": {bit_string(s): row for s, row in TARGET.items()},
        "own_pair": local,
        "own_pair_report_bit_recodings_checked": len(OUTCOMES),
        "one_shared_pair_by_designated_child": shared,
        "shared_reset_control": reset,
        "shared_hold_still_mutation": frozen,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
