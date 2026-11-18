"""Exact three-addition projection after signed states-only growth from the eight-cut law."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CUT_SOURCE = (
    ROOT / "artifacts" / "ERASE-SEPARATELY-20261117-001"
    / "ERASE-SEPARATELY-20261117-001-E001_erasure" / "results.json"
)
CUT_DIGEST = "65b8a87894afafc8464731432c42242d1b55b803370ddece9c7232c6e79e6d95"
RULE_SOURCE = (
    ROOT / "experiments" / "ERASE-SEPARATELY-20261117-001"
    / "ERASE-SEPARATELY-20261117-001-E001_erasure" / "enumerate_erasure.py"
)
RULE_DIGEST = "c800b09d648406ab25f6b585ffb48d7056c78b5c3d76d1563129d73d4d2202ea"
STARTS = ("fan6", "nonfan6")


def normalize(column: int, full: int) -> int:
    return min(column, column ^ full)


def cut_columns(rows: tuple[int, ...], width: int) -> tuple[tuple[int, ...], int]:
    """Choose one row from each antipodal pair, then forget column signs and names."""
    half = len(rows) // 2
    assert len(rows) == 2 * half and rows == tuple(sorted(set(rows)))
    complement = (1 << width) - 1
    assert tuple(row ^ complement for row in rows[:half]) == rows[half:][::-1]
    full = (1 << half) - 1
    columns = tuple(sorted(
        normalize(sum(((row >> bit) & 1) << i for i, row in enumerate(rows[:half])), full)
        for bit in range(width)
    ))
    assert len(set(columns)) == width
    return columns, full


def atom_forces(columns: tuple[int, ...], full: int) -> set[tuple[int, int]]:
    """Each atom forces 0 on one old value pair and 1 on the complementary pair."""
    out = set()
    for left, right in combinations(columns, 2):
        left_zero, right_zero = full ^ left, full ^ right
        for zero, one in ((left_zero & right_zero, left & right),
                          (left_zero & right, left & right_zero)):
            out.add((zero, one))
            out.add((one, zero))
    return out


def covers_with_three(coverage: set[int], full: int) -> bool:
    if full in coverage:
        return True
    # A larger compatible mask can replace a mask it contains in any cover.
    maximal = []
    for mask in sorted(coverage, key=int.bit_count, reverse=True):
        if mask and all(mask & kept != mask for kept in maximal):
            maximal.append(mask)
    for i, first in enumerate(maximal):
        for j in range(i + 1, len(maximal)):
            missing = full ^ (first | maximal[j])
            if not missing or any(missing & third == missing for third in maximal[j + 1:]):
                return True
    return False


@cache
def literal_extensions(columns: tuple[int, ...], full: int) -> tuple[int, ...]:
    """Return every literal zero-cost extension, including both members of a flip pair."""
    atoms = atom_forces(columns, full)
    out = []
    for column in range((full + 1) // 2):
        if column in columns:
            continue
        compatible = {
            zero | one for zero, one in atoms
            if not zero & column and one & column == one
        }
        # Every old row must have exactly one new value. A cover does this
        # on the representatives and therefore also on their complements.
        if covers_with_three(compatible, full):
            out.extend((column, column ^ full))
    return tuple(sorted(out))


def projected_words(three: tuple[int, ...], full: int) -> frozenset[int]:
    assert len(three) == 3
    rows = {
        sum(((column >> index) & 1) << bit for bit, column in enumerate(three))
        for index in range(full.bit_length())
    }
    return frozenset(rows | {row ^ 7 for row in rows})


def observed_class(three: tuple[int, ...], full: int) -> int:
    rows = projected_words(three, full)
    for left, right in combinations(range(3), 2):
        assert {((row >> left) & 1, (row >> right) & 1) for row in rows} == {
            (0, 0), (0, 1), (1, 0), (1, 1)
        }
    excluded = set(range(8)) - rows
    if excluded:
        assert len(excluded) == 2
        first, second = excluded
        assert first ^ second == 7
    # All two-row antipodal omissions are related by independent value swaps.
    # The number of rows therefore identifies the anonymous three-column class.
    return len(rows)


def grow(original: tuple[int, ...], full: int) -> dict:
    law = {original: Fraction(1)}
    histories = {original: 1}
    stages = []
    for _ in range(3):
        next_law = Counter()
        next_histories = Counter()
        branches = Counter()
        for current, mass in law.items():
            literal = literal_extensions(current, full)
            if not literal:
                raise RuntimeError(
                    f"No zero-cost extension at width {len(current)}. "
                    "A full legal-move check would be needed for this node."
                )
            quotient = Counter(normalize(column, full) for column in literal)
            assert len(literal) == len(set(literal)) and set(quotient.values()) == {2}
            assert not set(current).intersection(quotient)
            branches[len(literal)] += 1
            for column, multiplicity in sorted(quotient.items()):
                successor = tuple(sorted((*current, column)))
                next_law[successor] += mass * Fraction(multiplicity, len(literal))
                next_histories[successor] += histories[current] * multiplicity
        width = len(original) + len(stages)
        stages.append({
            "width_before": width,
            "reachable_nodes_with_zero_cost_extension": len(law),
            "literal_branch_count_histogram": dict(branches),
            "distinct_column_sets_after": len(next_law),
            "literal_histories_after": sum(next_histories.values()),
            "probability_sum": str(sum(next_law.values())),
            "stalled_probability": "0",
        })
        assert sum(next_law.values()) == 1
        law, histories = next_law, next_histories

    probabilities = Counter()
    observed_nodes = Counter()
    observed_histories = Counter()
    for current, mass in law.items():
        # The original columns are used only by this evaluator. The rule above
        # receives the unmarked set of all current columns.
        additions = tuple(column for column in current if column not in original)
        size = observed_class(additions, full)
        probabilities[size] += mass
        observed_nodes[size] += 1
        observed_histories[size] += histories[current]
    assert sum(probabilities.values()) == 1 and set(probabilities) <= {6, 8}
    return {
        "projection_probabilities": {size: str(probabilities[size]) for size in (6, 8)},
        "projected_column_set_counts": {size: observed_nodes[size] for size in (6, 8)},
        "projected_literal_history_counts": {size: observed_histories[size] for size in (6, 8)},
        "all_new_pairs_free": True,
        "no_equal_or_complementary_copies": True,
        "stages": stages,
    }


def verified_bytes(path: Path, digest: str) -> bytes:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f"Frozen input digest changed: {path}")
    return data


def controls() -> dict:
    verified_bytes(RULE_SOURCE, RULE_DIGEST)
    spec = importlib.util.spec_from_file_location("erasure_rule", RULE_SOURCE)
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    fixtures = []
    for width in (3, 4, 5):
        knots = tuple((0, mid, mid + 1) for mid in range(1, width - 1))
        rows = previous.seed_rows(width, knots)
        renamed = previous.recode(rows, tuple(reversed(range(width))), 2)
        fixtures.extend(((width, rows), (width, renamed)))
    fixtures.append((4, (0, 3, 6, 9, 12, 15)))
    compared = []
    for width, rows in fixtures:
        columns, full = cut_columns(rows, width)
        expected = set()
        for target, _ in previous.cheapest(rows, width, True):
            if len(target) != len(rows):
                continue
            ones = {row ^ (1 << width) for row in target if row & (1 << width)}
            expected.add(sum((row in ones) << i for i, row in enumerate(rows[:len(rows) // 2])))
        actual = set(literal_extensions(columns, full))
        # cut_columns can flip old columns, which leaves the signed grammar
        # unchanged and leaves the rows used to read the new column unchanged.
        assert actual == expected
        compared.append({"width": width, "literal_zero_cost_extensions": len(actual)})
    assert observed_class((0, 1, 2), 7) == 6
    assert observed_class((0, 3, 5), 15) == 8
    return {"frozen_rule_agreement": compared, "both_projection_classes_checked": True}


def run() -> dict:
    started = time.perf_counter()
    comparisons = controls()
    data = json.loads(verified_bytes(CUT_SOURCE, CUT_DIGEST))
    cut, = (layer for layer in data["eight_independent"]["layers"] if layer["width"] == 8)
    prior_records = cut["class_records"]
    assert len(prior_records) == 13
    assert cut["probability_sums"] == ["1", "1"] and cut["stalled_probability"] == ["0", "0"]
    rows_out = []
    total = {start: Counter() for start in STARTS}
    for index, record in enumerate(prior_records):
        rows = tuple(record["rows"])
        assert len(rows) == 12
        columns, full = cut_columns(rows, 8)
        conditional = grow(columns, full)
        prior = {start: Fraction(record[f"{start}_probability"]) for start in STARTS}
        for start, mass in prior.items():
            for size, frequency in conditional["projection_probabilities"].items():
                total[start][size] += mass * Fraction(frequency)
        rows_out.append({
            "cut_class": index,
            "cut_rows": rows,
            "cut_probabilities": {start: str(weight) for start, weight in prior.items()},
            **conditional,
        })
    assert all(sum(mass.values()) == 1 for mass in total.values())
    difference = sum(abs(total["fan6"][size] - total["nonfan6"][size]) for size in (6, 8)) / 2
    return {
        "cut_source_sha256": CUT_DIGEST,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "controls": comparisons,
        "cut_class_count": len(rows_out),
        "per_cut_class": rows_out,
        "by_start": {
            start: {
                "projection_probabilities": {size: str(mass[size]) for size in (6, 8)},
                "probability_sum": str(sum(mass.values())),
                "stalled_probability": "0",
            }
            for start, mass in total.items()
        },
        "total_variation": str(difference),
        "equal_prior_recognition": str((1 + difference) / 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="Run only synthetic checks")
    parser.add_argument("--output", type=Path, help="Write JSON to this path")
    args = parser.parse_args()
    result = controls() if args.smoke else run()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
