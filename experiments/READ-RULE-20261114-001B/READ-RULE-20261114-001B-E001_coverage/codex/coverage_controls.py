"""Focused exact-row controls for READ coverage ties and quantifier meanings.

Tie controls call the producer's _ties.  Quantifier fixtures are separately
labelled mathematical truth-table controls: the producer currently exposes no
standalone quantifier aggregator, so those fixtures do not claim to execute
semantic_coverage.  This script starts no child processes and writes only its
owned coverage_controls.json when explicitly run.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
TARGET = HERE / "coverage.py"
OUTPUT = HERE / "coverage_controls.json"


def _load_target():
    name = "read_rule_focused_coverage_controls_target"
    spec = importlib.util.spec_from_file_location(name, TARGET)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {TARGET}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def tie_controls(target):
    """Literal allowed states; bit 0=p, bit 1=x, bit 2=z unless aliased."""
    fixtures = [
        dict(name="plain_NAE", labels=[0, 1, 2], rows=[1, 2, 3, 4, 5, 6],
             arguments=[0, 1, 2], expected=["free", False, False, False]),
        dict(name="killed_z_opposite_p", labels=[0, 1, 2], rows=[1, 3, 4, 6],
             arguments=[0, 1, 2], expected=["free", True, False, True]),
        dict(name="killed_z_opposite_x", labels=[0, 1, 2], rows=[2, 3, 4, 5],
             arguments=[0, 1, 2], expected=["free", False, True, True]),
        dict(name="both_opposite_so_p_equals_x", labels=[0, 1, 2], rows=[3, 4],
             arguments=[0, 1, 2], expected=["equal", True, True, False]),
        dict(name="identity_z_is_p", labels=[0, 1], rows=[1, 2],
             arguments=[0, 1, 0], expected=["opposite", False, True, False]),
        # Nonnumeric ordering and nonconsecutive labels check that identity
        # labels are looked up rather than treated as packed bit positions.
        dict(name="label_lookup_killed_z_opposite_p", labels=[31, 7, 19],
             rows=[1, 3, 4, 6], arguments=[31, 7, 19],
             expected=["free", True, False, True]),
    ]
    answers = []
    for fixture in fixtures:
        projection = dict(labels=fixture["labels"], allowed=fixture["rows"])
        actual = list(target._ties(projection, *fixture["arguments"]))
        answer = dict(fixture, actual=actual, passed=actual == fixture["expected"])
        # Each input is a nonempty complement-closed relation satisfying NAE
        # on its three supplied identities, including the repeated identity.
        width = len(fixture["labels"])
        mask = (1 << width) - 1
        rows = set(fixture["rows"])
        index = {label: bit for bit, label in enumerate(fixture["labels"])}
        complement_closed = bool(rows) and all((row ^ mask) in rows for row in rows)
        satisfies_NAE = all(len({(row >> index[label]) & 1
                                 for label in fixture["arguments"]}) == 2 for row in rows)
        answer.update(complement_closed=complement_closed, satisfies_NAE=satisfies_NAE)
        answer["passed"] &= complement_closed and satisfies_NAE
        answers.append(answer)
    return answers


def quantifier_reference(matrix):
    """Independent finite truth predicates, not the producer's aggregation.

    Each row is a Q state and each column one fixed oriented knot.  None
    means not carried, True means exception, and False means survives.
    Empty participation does not certify a surviving reading.
    """
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("quantifier fixture needs a nonempty rectangular truth table")
    columns = [tuple(row[j] for row in matrix) for j in range(len(matrix[0]))]
    participating = [tuple(value for value in col if value is not None)
                     for col in columns]
    participating = [col for col in participating if col]
    all_Q = any(all(value is False for value in col) for col in columns)
    carried_Q = any(all(value is False for value in col) for col in participating)
    killed_everywhere = bool(participating) and all(all(col) for col in participating)
    killed_somewhere_each = bool(participating) and all(any(col) for col in participating)
    return dict(all_Q_applies=all_Q, carried_Q_applies=carried_Q,
                official_applies=all_Q if all_Q == carried_Q else None,
                killed_in_every_carried_Q=killed_everywhere,
                each_knot_killed_in_some_carried_Q=killed_somewhere_each,
                official_Q1=killed_everywhere if killed_everywhere == killed_somewhere_each else None,
                forall_state_some_surviving_knot=all(any(value is False for value in row)
                                                   for row in matrix))


def quantifier_controls():
    fixtures = [
        dict(name="one_fixed_knot_survives_all", matrix=[[False], [False]],
             expected=[True, True, True, False, False, False, True]),
        dict(name="survivor_absent_from_one_state", matrix=[[False], [None]],
             expected=[False, True, None, False, False, False, False]),
        dict(name="one_knot_killed_in_one_state", matrix=[[True], [False]],
             expected=[False, False, False, False, True, None, False]),
        dict(name="different_knots_survive_different_states",
             matrix=[[False, True], [True, False]],
             expected=[False, False, False, False, True, None, True]),
        dict(name="every_reading_killed", matrix=[[True, True], [True, True]],
             expected=[False, False, False, True, True, True, False]),
        dict(name="no_carried_reading", matrix=[[None], [None]],
             expected=[False, False, False, False, False, False, False]),
    ]
    fields = ("all_Q_applies", "carried_Q_applies", "official_applies",
              "killed_in_every_carried_Q", "each_knot_killed_in_some_carried_Q",
              "official_Q1", "forall_state_some_surviving_knot")
    answers = []
    for fixture in fixtures:
        expected = dict(zip(fields, fixture["expected"]))
        actual = quantifier_reference(fixture["matrix"])
        answers.append(dict(name=fixture["name"], matrix=fixture["matrix"],
                            expected=expected, actual=actual, passed=actual == expected))
    return answers


def controls():
    started = time.monotonic()
    before = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    target = _load_target()
    ties = tie_controls(target)
    quantifiers = quantifier_controls()
    conjunction = []
    for values, expected in (([True, True], True), ([True, None], None),
                             ([False, None], False)):
        actual = target.conjunction(values)
        conjunction.append(dict(values=values, expected=expected, actual=actual,
                                passed=actual is expected))
    after = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    stable = before == after
    return dict(passed=stable and all(row["passed"] for row in ties + quantifiers + conjunction),
                tie_controls=ties, quantifier_truth_controls=quantifiers,
                producer_conjunction_controls=conjunction,
                producer_quantifier_aggregation_executed=False,
                quantifier_scope="Truth-table meanings only; semantic_coverage aggregation is not invoked.",
                coverage_source_sha256=before, coverage_source_stable=stable,
                controls_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                seconds=time.monotonic() - started,
                process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    answer = controls()
    OUTPUT.write_text(json.dumps(answer, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(dict(passed=answer["passed"], ties=len(answer["tie_controls"]),
                          quantifier_truth_fixtures=len(answer["quantifier_truth_controls"]),
                          conjunction=len(answer["producer_conjunction_controls"]),
                          coverage_source_stable=answer["coverage_source_stable"],
                          seconds=answer["seconds"], peak_rss_kib=answer["process_peak_rss_kib"]),
                     sort_keys=True))
    return 0 if answer["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
