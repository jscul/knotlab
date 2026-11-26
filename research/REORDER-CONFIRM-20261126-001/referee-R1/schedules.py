"""Rebuild the general-schedule and immediate-birth checks from the definitions.

Repeated reader labels encode a schedule. The first occurrence creates the
old distinction, and the second applies its birth. All expectations below use
integer occupation amplitudes and the stated Majorana operators.
"""

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations, islice, permutations
import json
from math import factorial
from pathlib import Path
import random
import resource
from time import perf_counter


RECEIPT = (
    Path(__file__).resolve().parents[3]
    / "artifacts/REORDER-CONFIRM-20261126-001"
    / "REORDER-CONFIRM-20261126-001-E001_schedules/results.json"
)
FLIPS = ("F1", "F3")
SAMPLE_SEED = 20261130


def schedule_count(n):
    return factorial(2 * n) // (2**n)


def schedule_at(n, rank):
    """Unrank the lexicographic multiset words of two occurrences per label."""
    available = [2] * n
    total = schedule_count(n)
    schedule = []
    for remaining in range(2 * n, 0, -1):
        for reader, copies in enumerate(available):
            suffixes = total * copies // remaining
            if rank < suffixes:
                schedule.append(reader)
                available[reader] -= 1
                total = suffixes
                break
            rank -= suffixes
        else:
            raise ValueError("Schedule rank out of range")
    return tuple(schedule)


def alternates(first, second):
    start, finish = first
    other_start, other_finish = second
    return (start < other_start < finish) != (start < other_finish < finish)


def alternating_pairs(schedule, n):
    positions = [[] for _ in range(n)]
    for index, reader in enumerate(schedule):
        positions[reader].append(index)
    return tuple(
        (i, j) for i, j in combinations(range(n), 2)
        if alternates(positions[i], positions[j])
    )


def predicted_class(pairs, n):
    """The triples must all have odd parity for F1 or even parity for F3.

    On two even words supported on pairs that share a reader, the polar form
    is the parity of the three alternating-pair indicators. Using the same
    shared reader throughout gives a basis for all even words.
    """
    pairs = set(pairs)
    parities = {
        ((a, b) in pairs) ^ ((a, c) in pairs) ^ ((b, c) in pairs)
        for a, b, c in combinations(range(n), 3)
    }
    return {"F1": parities == {True}, "F3": parities == {False}}


def creator_sign(state, mode):
    preceding = state & ((1 << mode) - 1)
    return (-1) ** (preceding.bit_count() % 2)


def add_creator(term, mode):
    state, sign = term
    bit = 1 << mode
    if state & bit:
        raise ValueError("Creation requires a fresh mode")
    return state | bit, sign * creator_sign(state, mode)


def prepare(schedule, old_words):
    seen = set()
    events = []
    for reader in schedule:
        events.append((reader, reader in seen))
        seen.add(reader)

    amplitudes = {}
    for old in old_words:
        terms = [(0, 1)]
        for reader, is_birth in events:
            x, y, z = 3 * reader, 3 * reader + 1, 3 * reader + 2
            occupied = (old >> reader) & 1
            if not is_birth:
                if occupied:
                    terms = [add_creator(term, x) for term in terms]
            elif occupied:
                terms = [add_creator(term, mode) for term in terms for mode in (y, z)]
            else:
                # The written product c_y^+ c_z^+ applies its right factor first.
                terms = terms + [add_creator(add_creator(term, z), y) for term in terms]
        amplitudes.update(terms)
    return amplitudes


def majorana_action(state, mode, primed=False):
    """Return the occupation after one Majorana and the exponent of i."""
    bit = 1 << mode
    phase = 0 if creator_sign(state, mode) == 1 else 2
    if primed:
        phase += 3 if state & bit else 1
    return state ^ bit, phase


class ExactReadings:
    def __init__(self, n):
        self.old_words = tuple(old for old in range(1 << n) if old.bit_count() % 2 == 0)
        self.support = {}
        for old in self.old_words:
            for fresh in range(1 << n):
                state = 0
                for reader in range(n):
                    x = (old >> reader) & 1
                    y = (fresh >> reader) & 1
                    state |= (x | (y << 1) | ((x ^ y) << 2)) << (3 * reader)
                self.support[state] = old
        indices = {state: idx for idx, state in enumerate(self.support)}
        self.operations = {}
        for flipped in self.old_words:
            self.operations[flipped] = tuple(
                self.scored_operation(state, n, flipped, indices) for state in self.support
            )

    @staticmethod
    def scored_operation(state, n, flipped, indices):
        phase1 = phase3 = 0
        for reader in range(n):
            x, y = 3 * reader, 3 * reader + 1
            if flipped & (1 << reader):
                state, phase_y = majorana_action(state, y)
                target, phase_x_prime = majorana_action(state, x, primed=True)
                state, phase_x = majorana_action(state, x)
                assert state == target
                phase1 += 3 + phase_y + phase_x_prime  # -i gamma'_x gamma_y
                phase3 += 1 + phase_y + phase_x        # +i gamma_x gamma_y
            elif state & (1 << x):
                phase1 += 2
                phase3 += 2
        assert phase1 % 2 == phase3 % 2 == 0
        return indices[state], (-1) ** ((phase1 // 2) % 2), (-1) ** ((phase3 // 2) % 2)

    def correlations(self, amplitudes):
        assert amplitudes.keys() == self.support.keys()
        coefficients = tuple(amplitudes[state] for state in self.support)
        norm = sum(value * value for value in coefficients)
        sums = {flip: {} for flip in FLIPS}
        for flipped, operation in self.operations.items():
            value1 = value3 = 0
            for before, (after, sign1, sign3) in zip(coefficients, operation):
                product = before * coefficients[after]
                value1 += product * sign1
                value3 += product * sign3
            sums["F1"][flipped] = value1
            sums["F3"][flipped] = value3
        return {
            flip: {flipped: Fraction(value, norm) for flipped, value in values.items()}
            for flip, values in sums.items()
        }


def full_contradiction(values):
    return all(abs(value) == 1 for value in values.values()) and any(
        values[a ^ b] != values[a] * values[b] for a, b in combinations(values, 2)
    )


def verify_panel(n, schedules):
    started = perf_counter()
    readings = ExactReadings(n)
    tally = {
        "checked": 0,
        "carrying_checked": dict.fromkeys(FLIPS, 0),
        "disagreements": dict.fromkeys(FLIPS, 0),
        "occupation_coefficients_checked": 0,
        "occupation_sign_disagreements": 0,
        "neither": 0,
        "both": 0,
    }
    first_failure = None
    for schedule in schedules:
        pairs = alternating_pairs(schedule, n)
        want = predicted_class(pairs, n)
        amplitudes = prepare(schedule, readings.old_words)
        correlations = readings.correlations(amplitudes)
        got = {flip: full_contradiction(values) for flip, values in correlations.items()}
        expected = {
            old: (-1) ** sum(bool(old & (1 << i)) and bool(old & (1 << j)) for i, j in pairs)
            for old in readings.old_words
        }
        differences = sum(amplitudes[state] != expected[old] for state, old in readings.support.items())
        if first_failure is None and (differences or got != want):
            first_failure = {"schedule": schedule, "pairs": pairs, "expected_class": want, "observed_class": got}
        tally["checked"] += 1
        tally["occupation_coefficients_checked"] += len(amplitudes)
        tally["occupation_sign_disagreements"] += differences
        tally["neither"] += not any(got.values())
        tally["both"] += all(got.values())
        for flip in FLIPS:
            tally["carrying_checked"][flip] += got[flip]
            tally["disagreements"][flip] += got[flip] != want[flip]
    tally["seconds"] = round(perf_counter() - started, 4)
    tally["first_failure"] = first_failure
    return tally


def pairings(unassigned):
    """List pairings of event positions with readers forgotten."""
    if not unassigned:
        yield ()
        return
    first = unassigned[0]
    for index, later in enumerate(unassigned[1:], 1):
        remainder = unassigned[1:index] + unassigned[index + 1:]
        for tail in pairings(remainder):
            yield ((first, later),) + tail


def schedules_up_to_renaming(n):
    for pairing in pairings(tuple(range(2 * n))):
        schedule = [0] * (2 * n)
        for reader, (start, finish) in enumerate(pairing):
            schedule[start] = schedule[finish] = reader
        yield tuple(schedule)


def count_panel(n, limit):
    started = perf_counter()
    counts = dict.fromkeys(FLIPS, 0)
    checked = 0
    for pairing in islice(pairings(tuple(range(2 * n))), limit):
        first, *rest = pairing
        across_first = [alternates(first, interval) for interval in rest]
        odd = even = False
        for i, j in combinations(range(n - 1), 2):
            parity = across_first[i] ^ across_first[j] ^ alternates(rest[i], rest[j])
            odd |= parity
            even |= not parity
            if odd and even:
                break
        counts["F1"] += odd and not even
        counts["F3"] += even and not odd
        checked += 1
    labels = factorial(n)
    out = {
        "unlabelled_pairings": checked,
        "total": labels * checked,
        "seconds": round(perf_counter() - started, 4),
    }
    if limit is None:
        assert out["total"] == schedule_count(n)
    for flip, count in counts.items():
        out[flip] = labels * count
        out[f"share_{flip}"] = str(Fraction(count, checked)) if limit is None else None
    return out


def verify_renaming_classes(n, census, smoke):
    schedules = schedules_up_to_renaming(n)
    checks = verify_panel(n, islice(schedules, 32) if smoke else schedules)
    # Renaming permutes reader triples in both preparation and measurement.
    # In the final support each triple has even occupation, so this reorder
    # has sign +1. It relabels the correlations and preserves the verdict.
    multiplicity = factorial(n)
    weighted = {flip: count * multiplicity for flip, count in checks["carrying_checked"].items()}
    return {
        **checks,
        "label_multiplicity": multiplicity,
        "represented_labelled_schedules": checks["checked"] * multiplicity,
        "represented_labelled_carrying": weighted,
        "census_agreement": None if smoke else (
            checks["checked"] == census["unlabelled_pairings"]
            and all(weighted[flip] == census[flip] for flip in FLIPS)
        ),
    }


def controls():
    n = 4
    readings = ExactReadings(n)
    cases = {
        "identical_creation_and_commit_orders": (0, 1, 2, 3, 0, 1, 2, 3),
        "immediate_births": (0, 0, 1, 1, 2, 2, 3, 3),
        "complex_carrying_nonempty_split": (0, 1, 2, 3, 0, 3, 2, 1),
        "neither_flip_carries": (0, 1, 0, 1, 2, 2, 3, 3),
        "same_state_immediate_birth_for_reader_0": (0, 0, 1, 2, 3, 1, 2, 3),
        "same_state_latest_birth_for_reader_0": (0, 1, 2, 3, 1, 2, 3, 0),
    }
    states = {name: prepare(schedule, readings.old_words) for name, schedule in cases.items()}
    rows = {}
    for name, schedule in cases.items():
        values = readings.correlations(states[name])
        rows[name] = {
            "schedule": schedule,
            "alternating_pairs": alternating_pairs(schedule, n),
            "full_contradiction": {flip: full_contradiction(values[flip]) for flip in FLIPS},
            "correlations_by_flip_mask": {
                flip: {flipped: str(value) for flipped, value in values[flip].items()}
                for flip in FLIPS
            },
        }
    a = states["same_state_immediate_birth_for_reader_0"]
    b = states["same_state_latest_birth_for_reader_0"]
    assert a == b
    values = readings.correlations({state: a[state] + b[state] for state in a})
    return {
        "examples": rows,
        "distinct_schedules_same_state": a == b,
        "equal_mixture_F1_carries": rows["same_state_immediate_birth_for_reader_0"]["full_contradiction"]["F1"],
        "equal_coherent_sum_F1_carries": full_contradiction(values["F1"]),
    }


def compare_receipt(out):
    receipt = json.loads(RECEIPT.read_text())
    matches = {}
    for n in range(3, 6):
        name = f"n{n}"
        current = out["P3"][name]
        matches[f"P3_{name}"] = all(
            current[field] == receipt["P3"][name][field]
            for field in ("schedules", "checked", "carrying_checked", "disagreements")
        )
        current = out["P4"][name]
        archived = receipt["P4"][name]
        matches[f"P4_{name}"] = (
            current["checked"] == archived["sigmas"]
            and all(current["carrying_checked"][flip] == archived[f"carrying_{flip}"] for flip in FLIPS)
        )
    for n in range(3, 7):
        name = f"n{n}"
        current = out["uniform_over_labelled_schedules"][name]
        archived = receipt["P3"]["shares_uniform_over_schedules"][name]
        matches[f"P3_uniform_{name}"] = all(
            current[field] == archived[field] for field in ("total", "F1", "F3", "share_F1", "share_F3")
        )
    return matches


def run(smoke):
    started = perf_counter()
    sample = random.Random(SAMPLE_SEED).sample(range(schedule_count(5)), 2000)
    out = {
        "P3": {},
        "P4": {},
        "uniform_over_labelled_schedules": {},
        "P3_n5_sample": {
            "seed": SAMPLE_SEED,
            "index_order": "Lexicographic on reader labels, each appearing twice",
            "receipt_comparison": "The receipt retains only aggregates. The seed and index order reconstruct the sample.",
            "first_eight_zero_based_indices": sample[:8],
            "sha256_of_comma_separated_indices": hashlib.sha256(
                ",".join(map(str, sample)).encode()
            ).hexdigest(),
        },
    }
    for n in range(3, 6):
        ranks = sample if n == 5 else range(schedule_count(n))
        schedules = (schedule_at(n, rank) for rank in ranks)
        if smoke and n > 3:
            schedules = islice(schedules, 32)
        out["P3"][f"n{n}"] = {"schedules": schedule_count(n), **verify_panel(n, schedules)}
    for n in range(3, 7):
        schedules = (tuple(reader for reader in order for _ in range(2)) for order in permutations(range(n)))
        if smoke:
            schedules = islice(schedules, 32)
        out["P4"][f"n{n}"] = verify_panel(n, schedules)
    for n in range(3, 8):
        out["uniform_over_labelled_schedules"][f"n{n}"] = count_panel(n, 1000 if smoke and n > 5 else None)
    census = out["uniform_over_labelled_schedules"]
    out["P3_direct_up_to_reader_renaming"] = {
        f"n{n}": verify_renaming_classes(n, census[f"n{n}"], smoke) for n in (5, 6)
    }
    out["controls"] = controls()
    if not smoke:
        out["receipt_aggregate_fields_match"] = compare_receipt(out)
    out["elapsed_seconds"] = round(perf_counter() - started, 4)
    out["peak_resident_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    out = run(args.smoke)
    contents = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(contents, end="")
    else:
        args.output.write_text(contents)
    renaming_checks = out["P3_direct_up_to_reader_renaming"].values()
    panels = [*out["P3"].values(), *out["P4"].values(), *renaming_checks]
    if any(row["first_failure"] is not None for row in panels):
        raise SystemExit("A preparation or reading differs from the alternating-event prediction")
    if any(row["census_agreement"] is False for row in renaming_checks) or not all(
        out.get("receipt_aggregate_fields_match", {}).values()
    ):
        raise SystemExit("The independent totals differ from the archived aggregate or census")


if __name__ == "__main__":
    main()
