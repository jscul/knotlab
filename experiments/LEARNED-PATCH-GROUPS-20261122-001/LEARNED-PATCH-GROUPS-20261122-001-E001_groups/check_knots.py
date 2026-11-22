"""Check the held laws, exact selection and feedback path on synthetic data."""

from fractions import Fraction
from itertools import combinations, product
import json
from math import comb
import os
from pathlib import Path
import subprocess
import sys

from learner import (
    HOLDING_COUNT,
    OPEN_RELATIONS,
    PARTITION_COUNT,
    KnotLearner,
    _CLASS_TOTALS_START,
    _FLAGS_START,
    _STATS_START,
    _fit_masks,
    _holding,
    _rule_vote,
    pattern_counts,
)


ROOT = Path(__file__).resolve().parents[3]
EMPTY = (0,) * 64
SINGLE = (1, *EMPTY[1:])
MOVED = (*EMPTY[:-1], 1)
DENSE = (1,) * 64
ALL_MASK = (1 << 16) - 1
PREPARED = {"parity": {"110", "011"}, "nae": {"110", "001"}}
OPEN = {"parity": {"000", "011", "101", "110"},
        "nae": {"001", "010", "011", "100", "101", "110"}}


def rejection(operation, *inputs):
    try:
        operation(*inputs)
    except ValueError:
        return
    raise AssertionError(f"{operation.__name__} accepted a rejected fixture")


def canonical_check(rows):
    clauses = [" ".join(("~" if bit == "1" else "") + name
                        for bit, name in zip(row, ("mark", "dock", "read"), strict=True))
               for row in map("".join, product("01", repeat=3)) if row not in rows]
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "; ".join(clauses),
               "--loops", "mark", "dock", "--contact", "read", "--json"]
    result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / "tools")),
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def projection(law, address):
    receiver = KnotLearner(law)
    neutral = receiver.export_memory()
    observed = set()
    for word in product((0, 1), repeat=3):
        before = receiver.export_memory()
        try:
            receiver.prepare_holding(address, word)
        except ValueError:
            assert receiver.export_memory() == before
        else:
            triple = "".join(map(str, word))
            packed = f"{int(triple, 2):02x}"
            observed.add(triple)
            offset = 2 * address
            assert receiver.export_memory()["words"] == (
                neutral["words"][:offset] + packed + neutral["words"][offset + 2:])
    assert observed == OPEN[law]
    verdict = canonical_check(observed)
    assert verdict["is_knot"] and verdict["minimum_width"] == 3
    return verdict


def check_open_laws():
    free = {"".join(row) for row in product("01", repeat=3)}
    free_report = canonical_check(free)
    assert not free_report["binding"] and not free_report["is_knot"]
    free_relation = frozenset(tuple(map(int, row)) for row in free)
    laws = {}
    for law in OPEN_RELATIONS:
        for word in PREPARED[law]:
            mark, dock, read = map(int, word)
            assert _holding._admit_word(law, mark, dock) == (mark, dock, read)
            rejection(_holding._complete_read, free_relation, mark, dock)
        prepared = canonical_check(PREPARED[law])
        assert not prepared["loss_on_erasure"] and not prepared["is_knot"]
        laws[law] = {
            "receipt": projection(law, 3),
            "class_total": projection(law, _CLASS_TOTALS_START + 3),
            "partition_flag": projection(law, _FLAGS_START + 3),
            "prepared_only": prepared,
        }
    return {"laws": laws, "unconstrained_negative": free_report}


def reference_fit(classes):
    masks = []
    best = None
    for width in range(1, 16):
        for indices in combinations(range(15), width):
            values = [[sum(row[index] for index in indices) for row in group] for group in classes]
            means = [Fraction(sum(group), len(group)) for group in values]
            diff = means[0] - means[1]
            if not diff:
                continue
            variance = sum(Fraction(sum(value * value for value in group), len(group)) - mean * mean
                           for group, mean in zip(values, means, strict=True))
            rank = (variance == 0, diff * diff / variance if variance else 0, -min(width, 16 - width))
            mask = sum(1 << index for index in indices)
            if best is None or rank > best:
                best, masks = rank, [mask]
            elif rank == best:
                masks.append(mask)
    assert best is not None
    rank = (1, 0) if best[0] else (best[1].numerator, best[1].denominator)
    return sorted(masks), *rank


def fit(learner, examples):
    for pixels, rewarded in examples:
        guess = learner.predict(pixels)
        learner.learn(pixels, guess, guess == rewarded)
    return learner.finalize()


def exact_search():
    classes = [[pattern_counts(EMPTY), pattern_counts(SINGLE)],
               [pattern_counts(SINGLE), pattern_counts(DENSE)]]
    expected = reference_fit(classes)
    actual = _fit_masks(classes)
    assert actual == expected and 0 < actual[2]
    assert _fit_masks(classes[::-1]) == actual
    rename = (13, 5, 15, 2, 9, 8, 6, 4, 10, 0, 3, 1, 14, 11, 7, 12)

    def relabel_counts(row):
        return tuple(row[rename.index(index)] for index in range(16))

    relabeled = [[relabel_counts(row) for row in group] for group in classes]
    renamed_masks = []
    for mask in actual[0]:
        mapped = sum(1 << target for index, target in enumerate(rename) if mask & (1 << index))
        renamed_masks.append(ALL_MASK ^ mapped if mapped > PARTITION_COUNT else mapped)
    assert sorted(renamed_masks) == _fit_masks(relabeled)[0]
    assert _fit_masks(relabeled)[1:] == actual[1:]
    totals = [tuple(map(sum, zip(*group, strict=True))) for group in classes]
    remapped_totals = [relabel_counts(row) for row in totals]
    for mask, mapped in zip(actual[0], renamed_masks, strict=True):
        for pixels in (EMPTY, SINGLE, DENSE):
            histogram = pattern_counts(pixels)
            vote = _rule_vote(mask, histogram, (2, 2), totals)
            assert vote == _rule_vote(ALL_MASK ^ mask, histogram, (2, 2), totals)
            assert vote == _rule_vote(mapped, relabel_counts(histogram), (2, 2), remapped_totals)
    assert _rule_vote(1, (1, 80, *[0] * 14), (1, 1), [[0] * 16, [2, *[0] * 15]]) is None
    return {"masks": actual[0], "rank": list(actual[1:]), "independent_partitions": PARTITION_COUNT,
            "canonical_relabeling": True, "complement_votes_match": True, "midpoint_abstains": True}


def round_trip(law):
    learner = KnotLearner(law)
    neutral = learner.export_memory()
    rejection(learner.finalize)
    rejection(learner.learn, EMPTY, 1, False)
    assert learner.export_memory() == neutral
    learner.learn(EMPTY, learner.predict(EMPTY), True)
    acquisition = learner.export_memory()
    assert acquisition != neutral
    receiver = KnotLearner.from_memory(json.loads(json.dumps(acquisition)))
    assert receiver.export_memory() == acquisition
    assert receiver.explain(DENSE)["votes"] == [1, 0]
    receipt_fit = fit(receiver, [(EMPTY, 0), (SINGLE, 1), (MOVED, 1)])
    assert receipt_fit["rank_numerator"] == 1 and receipt_fit["rank_denominator"] == 0
    assert receipt_fit["masks"] == [1, 2, 4, 16, 256]
    assert receipt_fit["class_counts"] == [2, 2]
    frozen = receiver.export_memory()
    assert frozen["words"][2:2 * _STATS_START] == neutral["words"][2:2 * _STATS_START]
    assert (receiver.predict(EMPTY), receiver.predict(SINGLE)) == (0, 1)
    assert receiver.explain(SINGLE, detail=True)["rule_votes"] == [1] * 5
    rejection(receiver.learn, EMPTY, 0, True)
    rejection(receiver.finalize)
    assert receiver.export_memory() == frozen

    donor = KnotLearner(law)
    fit(donor, [(EMPTY, 1), (EMPTY, 1), (SINGLE, 0), (MOVED, 0)])
    receiver.swap_actions()
    assert receiver.export_memory() == donor.export_memory()
    assert (receiver.predict(EMPTY), receiver.predict(SINGLE)) == (1, 0)
    receiver.swap_actions()
    assert receiver.export_memory() == frozen
    donor.restore_memory(frozen)
    assert donor.explain(SINGLE, detail=True) == receiver.explain(SINGLE, detail=True)

    receiver.erase_selection()
    erased = receiver.export_memory()
    assert erased["words"][:2 * _FLAGS_START] == frozen["words"][:2 * _FLAGS_START]
    assert receiver.selection()["masks"] == [] and receiver.predict(SINGLE) == 0
    receiver.restore_memory(frozen)
    receiver.use_all_same_size()
    larger = receiver.export_memory()
    assert larger["words"][:2 * _FLAGS_START] == frozen["words"][:2 * _FLAGS_START]
    assert len(receiver.selection()["masks"]) == comb(16, 1)
    assert receiver.clear_memory() == larger
    assert receiver.export_memory() == neutral and receiver.predict(SINGLE) == 0
    receiver.restore_memory(frozen)
    corrupted = {**frozen, "words": "ff" + frozen["words"][2:]}
    rejection(receiver.restore_memory, corrupted)
    assert receiver.export_memory() == frozen and receiver.predict(SINGLE) == 1
    unprepared = min(OPEN[law] - PREPARED[law])
    receiver.prepare_holding(_FLAGS_START, tuple(map(int, unprepared)))
    rejection(receiver.predict, SINGLE)
    receiver.restore_memory(frozen)

    zero_signal = KnotLearner(law)
    assert fit(zero_signal, [(EMPTY, 0), (EMPTY, 1)])["masks"] == []
    assert zero_signal.predict(EMPTY) == 0
    return {"fixtures": 4, "infinite_rank_ties": receipt_fit["masks"], "receipt_words_erased": True,
            "zero_signal_empty_family": True, "separate_reversed_fit_matches_physical_swap": True,
            "same_size_and_erased_controls_touch_only_flags": True,
            "deployed_read_rejects_unprepared_open_flag": True}


def capacity():
    learner = KnotLearner("parity")
    for _ in range(64):
        learner.learn(EMPTY, 0, True)
    acquired = learner.export_memory()
    rejection(learner.learn, EMPTY, 0, True)
    assert learner.export_memory() == acquired
    assert learner.finalize()["class_counts"] == [64, 0]
    return True


if __name__ == "__main__":
    print(json.dumps({**check_open_laws(), "physical_holdings": HOLDING_COUNT,
                      "search": exact_search(), "capacity_guard": capacity(),
                      "synthetic": {law: round_trip(law) for law in OPEN_RELATIONS}},
                     indent=2, sort_keys=True))
