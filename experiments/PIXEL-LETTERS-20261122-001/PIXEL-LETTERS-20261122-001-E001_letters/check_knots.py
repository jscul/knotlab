"""Check the open memory laws and exercise the learner on synthetic bits only."""

from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys

from learner import (
    MEMORY_SCHEMA,
    OPEN_RELATIONS,
    KnotLearner,
    _admit_word,
    _complete_read,
    _read_register,
    _write_register,
    pattern_counts,
)


ROOT = Path(__file__).resolve().parents[3]
OPEN_CNF = {
    "parity": "mark dock ~read; mark ~dock read; ~mark dock read; ~mark ~dock ~read",
    "nae": "mark dock read; ~mark ~dock ~read",
}
PREPARED_CNF = {
    "parity": "dock; mark read; ~mark ~read",
    "nae": "~mark dock; mark ~dock; mark read; ~mark ~read",
}
CODES = {"parity": ("110", "011"), "nae": ("110", "001")}
EMPTY = (0,) * 64
SINGLE = (1, *EMPTY[1:])
MOVED = (*EMPTY[:-1], 1)
DENSE = (1,) * 64
EMPTY_COUNTS = (81, *(0,) * 15)
SINGLE_COUNTS = tuple(77 if index == 0 else int(index in (1, 2, 4, 8)) for index in range(16))
DENSE_COUNTS = (0, 1, 1, 7, 1, 7, 0, 0, 1, 0, 7, 0, 7, 0, 0, 49)


def canonical_check(cnf):
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
               "--loops", "mark", "dock", "--contact", "read", "--json"]
    result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / "tools")),
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def expect_rejection(operation, *inputs):
    try:
        operation(*inputs)
    except ValueError:
        return
    raise AssertionError(f"{operation.__name__} accepted a rejected fixture")


def checked_projection(law):
    learner = KnotLearner(law, training_limit=64)
    neutral = learner.export_memory()
    address = (1, 9, 12)
    action, pattern, position = address
    offset = 3 * position
    observed = set()
    for word in product((0, 1), repeat=3):
        before = learner.export_memory()
        try:
            learner.prepare_holding(*address, word)
        except ValueError:
            assert learner.export_memory() == before
        else:
            code = "".join(map(str, word))
            observed.add(code)
            expected = deepcopy(neutral)
            register = neutral["words"][action][pattern]
            expected["words"][action][pattern] = register[:offset] + code + register[offset + 3:]
            assert learner.export_memory() == expected
            if code not in CODES[law]:
                expect_rejection(learner.predict, EMPTY)
    clauses = [" ".join(("~" if bit == "1" else "") + name
                        for bit, name in zip(row, ("mark", "dock", "read"), strict=True))
               for row in map("".join, product("01", repeat=3)) if row not in observed]
    return address, canonical_check("; ".join(clauses))


def checked_laws():
    reports = {}
    free = canonical_check("")
    assert not free["binding"] and free["loss_on_erasure"] and free["coexistence"]
    assert not free["is_knot"]
    free_relation = frozenset(tuple(int(bit) for bit in word) for word in free["allowed"])

    for law, cnf in OPEN_CNF.items():
        report = canonical_check(cnf)
        assert report["is_knot"] and report["minimum_width"] == 3
        assert report["binding"] and report["loss_on_erasure"] and report["coexistence"]
        assert OPEN_RELATIONS[law] == frozenset(tuple(int(bit) for bit in word) for word in report["allowed"])
        address, actual_projection = checked_projection(law)
        assert actual_projection == report
        prepared = canonical_check(PREPARED_CNF[law])
        assert not prepared["is_knot"] and not prepared["loss_on_erasure"]
        assert set(prepared["allowed"]) == set(CODES[law])

        for before, old in enumerate(CODES[law]):
            old_word = tuple(int(bit) for bit in old)
            assert _read_register(law, (old_word,)) == before
            expect_rejection(_complete_read, free_relation, *old_word[:2])
            for after, new in enumerate(CODES[law]):
                written, = _write_register(law, (old_word,), after)
                assert "".join(map(str, written)) == new
                assert written in OPEN_RELATIONS[law]
                assert _read_register(law, (written,)) == after

        expect_rejection(_admit_word, law, 1, 0)
        reports[law] = {"open": report, "checked_holding_address": list(address),
                        "other_holdings_fixed": True, "prepared_words": prepared["allowed"],
                        "prepared_only_loss_on_erasure": prepared["loss_on_erasure"],
                        "prepared_transitions_checked": 4}

    assert _complete_read(OPEN_RELATIONS["parity"], 0, 1) == 1
    expect_rejection(_complete_read, OPEN_RELATIONS["nae"], 0, 1)
    assert _complete_read(OPEN_RELATIONS["nae"], 0, 0) == 1
    assert _complete_read(OPEN_RELATIONS["parity"], 0, 0) == 0
    reports["unconstrained_negative"] = free
    return reports


def fixed_memory(law, rows, limit=3):
    """Encode independently specified synthetic totals using the fixture words."""
    zero, one = CODES[law]
    width = (81 * limit).bit_length()
    return {
        "schema": MEMORY_SCHEMA,
        "law": law,
        "training_limit": limit,
        "words": [["".join(one if bit == "1" else zero for bit in f"{count:0{width}b}"[::-1])
                   for count in row] for row in rows],
    }


def check_centroids(learner, pixels, expected_counts, totals, rows):
    explanation = learner.explain(pixels)
    assert explanation["counts"] == list(expected_counts)
    distances = []
    for action, count_row, n in zip(explanation["actions"], totals, rows, strict=True):
        assert action["total"] == n * 81 and action["row_count"] == n
        differences = [n * seen - count for seen, count in zip(expected_counts, count_row, strict=True)]
        assert action["per_word_differences"] == differences
        expected = sum((Fraction(count, n) - seen) ** 2
                       for seen, count in zip(expected_counts, count_row, strict=True))
        assert Fraction(action["distance_numerator"], action["distance_denominator"]) == expected
        distances.append(expected)
    assert explanation["guess"] == int(distances[1] < distances[0])


def check_learner(law):
    learner = KnotLearner(law, training_limit=3)
    neutral = learner.export_memory()
    assert learner.predict(DENSE) == 0
    assert pattern_counts(EMPTY) == EMPTY_COUNTS
    assert pattern_counts(SINGLE) == pattern_counts(MOVED) == SINGLE_COUNTS
    assert pattern_counts(DENSE) == DENSE_COUNTS
    expect_rejection(pattern_counts, EMPTY[:-1])
    expect_rejection(pattern_counts, (2, *EMPTY[1:]))
    expect_rejection(learner.learn, EMPTY, 1, True)
    assert learner.export_memory() == neutral

    assert learner.predict(EMPTY) == 0
    learner.learn(EMPTY, 0, True)
    assert learner.predict(SINGLE) == 0
    learner.learn(SINGLE, 0, False)
    assert learner.predict(MOVED) == 1
    learner.learn(MOVED, 1, True)

    totals = (EMPTY_COUNTS, tuple(2 * count for count in SINGLE_COUNTS))
    learned = learner.export_memory()
    assert learned == fixed_memory(law, totals)
    for pixels, histogram in ((EMPTY, EMPTY_COUNTS), (SINGLE, SINGLE_COUNTS), (DENSE, DENSE_COUNTS)):
        check_centroids(learner, pixels, histogram, totals, (1, 2))
    expect_rejection(learner.learn, EMPTY, 0, True)
    assert learner.export_memory() == learned

    reverse = fixed_memory(law, totals[::-1])
    donor = KnotLearner.from_memory(json.loads(json.dumps(reverse)))
    assert (donor.predict(EMPTY), donor.predict(SINGLE)) == (1, 0)
    assert donor.export_memory() == reverse
    learner.restore_memory(reverse)
    assert (learner.predict(EMPTY), learner.predict(SINGLE)) == (1, 0)
    assert learner.clear_memory() == reverse
    assert learner.export_memory() == neutral
    assert (learner.predict(EMPTY), learner.predict(SINGLE)) == (0, 0)
    learner.restore_memory(learned)
    assert learner.export_memory() == learned
    assert (learner.predict(EMPTY), learner.predict(SINGLE)) == (0, 1)

    reversed_fit = KnotLearner(law, training_limit=3)
    for pixels, rewarded in ((MOVED, 1), (SINGLE, 1), (EMPTY, 0)):
        guess = reversed_fit.predict(pixels)
        reversed_fit.learn(pixels, guess, guess == rewarded)
    assert reversed_fit.export_memory() == learned

    unknown_zero = KnotLearner.from_memory(fixed_memory(law, ((0,) * 16, EMPTY_COUNTS)))
    equal = KnotLearner.from_memory(fixed_memory(law, ((162, *(0,) * 15), EMPTY_COUNTS)))
    assert unknown_zero.predict(SINGLE) == 1 and equal.predict(SINGLE) == 0

    invalid = deepcopy(learned)
    invalid["words"][0][0] = "100" + invalid["words"][0][0][3:]
    expect_rejection(learner.restore_memory, invalid)
    expect_rejection(learner.restore_memory, fixed_memory(law, ((1, *(0,) * 15), totals[1])))
    expect_rejection(learner.restore_memory, fixed_memory(law, ((0, 81, *(0,) * 14), totals[1])))
    expect_rejection(learner.restore_memory, fixed_memory(law, (totals[1], totals[1])))
    assert learner.export_memory() == learned

    return {"trained_guess": [0, 1], "exchanged_guess": [1, 0], "cleared_guess": [0, 0],
            "restored_guess": [0, 1], "reversed_order_same_words": True,
            "exact_rational_cases": 3, "all_expected_rejections": True}


if __name__ == "__main__":
    print(json.dumps({"relations": checked_laws(),
                      "synthetic_learner": {law: check_learner(law) for law in OPEN_RELATIONS}},
                     indent=2, sort_keys=True))
