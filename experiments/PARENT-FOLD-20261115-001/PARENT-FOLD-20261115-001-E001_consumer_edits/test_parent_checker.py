"""Focused synthetic acceptance and falsification checks; no study panel."""

from copy import deepcopy
from itertools import combinations
from pathlib import Path
import sys

from parent_checker import Checker
from wire_return import attach_physical


JOINT = Path(__file__).resolve().parents[2] / "FOLD-TWO-OUTPUT-20261115-001" / "FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"
sys.path.insert(0, str(JOINT))
from joint_solver import JointSolver


def fixture():
    # Four independent stage inputs.  The first is produced by a real prefix
    # using two additional raw inputs, so a stage-only replay misses work.
    n, m = 6, 4
    prefix = [[0, 4], [8, 5]]
    stage = [[1, 2], [6, 6], [0, 7], [0, 8], [7, 8], [9, 10],
             [11, 3], [11, 12], [3, 12], [13, 14],
             [11, 11], [3, 3], [16, 17]]
    frontier = [9, 1, 2, 3]
    lift = frontier + [n, n + 1]
    gates = deepcopy(prefix)
    for a, b in stage:
        gates.append([lift[a], lift[b]])
        lift.append(n + 1 + len(gates))
    case = dict(id="synthetic-parent", n=n, gates=gates, upstream_count=2,
                frontier=frontier, outputs=[lift[15], lift[18]],
                pieces=[dict(inputs=[0, 1, 2], bit=lift[11], ports=[lift[15], lift[18]])])
    case["edits"] = [dict(id="a", gate=lift[12], pin=1, to=frontier[2]),
                     dict(id="b", gate=lift[18], pin=1, to=frontier[2])]
    return case, dict(n=m, gates=stage, outputs=[15, 18])


def scalar_targets(case, edit):
    """Independent scalar replay, including every raw row and the prefix."""
    n, m = case["n"], len(case["frontier"])
    found = {}
    for row in range(1 << n):
        values = [*((row >> i) & 1 for i in range(n)), 0, 1]
        for index, pair in enumerate(case["gates"]):
            a, b = pair
            if edit is not None and n + 2 + index == edit["gate"]:
                a, b = (edit["to"], b) if edit["pin"] == 0 else (a, edit["to"])
            values.append(1 ^ (values[a] & values[b]))
        local = sum(values[wire] << i for i, wire in enumerate(case["frontier"]))
        observed = tuple(values[wire] for wire in case["outputs"])
        assert local not in found or found[local] == observed
        found[local] = observed
    assert len(found) == 1 << m
    return tuple(sum(found[row][output] << row for row in range(1 << m)) for output in range(2))


def scalar_classes(n, targets, group):
    outside = [axis for axis in range(n) if axis not in group]
    residuals = set()
    for local in range(8):
        offset = sum(((local >> i) & 1) << axis for i, axis in enumerate(group))
        residual = []
        for z in range(1 << len(outside)):
            row = offset | sum(((z >> i) & 1) << axis for i, axis in enumerate(outside))
            residual.append(tuple((truth >> row) & 1 for truth in targets))
        residuals.add(tuple(residual))
    return len(residuals)


def scalar_raw_columns(n, gates):
    """Pack an independent scalar replay for every raw wire, not just outputs."""
    columns = [0] * (n + 2 + len(gates))
    for row in range(1 << n):
        values = [*((row >> i) & 1 for i in range(n)), 0, 1]
        for a, b in gates:
            values.append(1 ^ (values[a] & values[b]))
        for wire, value in enumerate(values):
            columns[wire] |= value << row
    return columns


def check_raw_history(case):
    checker = Checker(case)
    history_size = len(checker._historical_raw_expressions)
    histories = []
    # Changing a gate leaves all numeric IDs intact.  Its descendants retain
    # the same pairs of numeric inputs but must get different expression IDs.
    for edit in case["edits"]:
        gates = deepcopy(case["gates"])
        gates[edit["gate"] - case["n"] - 2][edit["pin"]] = edit["to"]
        before = checker.work_counters()
        observed = checker._replay_raw_return(gates)
        after = checker.work_counters()
        hits = after["raw_return_history_expression_hits"] - before.get("raw_return_history_expression_hits", 0)
        misses = after["raw_return_history_expression_misses"] - before.get("raw_return_history_expression_misses", 0)
        assert hits > 0 and misses > 0
        assert hits + misses == len(gates) - case["upstream_count"]
        assert observed == scalar_raw_columns(case["n"], gates)
        assert observed[edit["gate"]] != checker._original_raw_values[edit["gate"]]
        histories.append((hits, misses))
    # Insert a new gate at an old numeric ID and shift every later source
    # gate.  Existing expressions must still hit despite their new wire IDs.
    first = case["n"] + 2 + case["upstream_count"]
    gates = deepcopy(case["gates"][:case["upstream_count"]])
    gates.append([case["n"], case["n"]])
    gates += [[wire + (wire >= first) for wire in pair]
              for pair in case["gates"][case["upstream_count"]:]]
    before = checker.work_counters()
    observed = checker._replay_raw_return(gates)
    after = checker.work_counters()
    assert observed == scalar_raw_columns(case["n"], gates)
    assert after["raw_return_history_expression_hits"] - before["raw_return_history_expression_hits"] == len(case["gates"]) - case["upstream_count"]
    assert after["raw_return_history_expression_misses"] - before["raw_return_history_expression_misses"] == 1
    assert observed[first] != checker._original_raw_values[first]
    assert len(checker._historical_raw_expressions) == history_size
    direct = Checker(case, raw_replay="direct")
    assert direct._replay_raw_return(gates) == observed
    return histories


def rejected(fn, contains):
    try:
        fn()
    except ValueError as exc:
        assert contains in str(exc), str(exc)
    else:
        raise AssertionError("invalid return was accepted")


def check():
    case, source_stage = fixture()
    history_hits_and_misses = check_raw_history(case)
    checker = Checker(case)
    assert checker.setup_work["frontier_assignments_verified"] == 16
    assert checker.setup_work["raw_frontier_assignments_covered"] == 64
    original_tables = scalar_targets(case, None)
    answer = attach_physical(case, JointSolver(4).solve(original_tables))
    paid = checker.verify(None, answer)
    assert paid["exact"] and paid["width"] == 1
    assert paid["raw_assignments"] == 64
    assert paid["raw_return_output_bits_compared"] == 128
    assert checker.verify(None, answer)["original_verification_cache_hits"] == 1

    submitted_hits_and_misses = []
    for edit in case["edits"]:
        tables = scalar_targets(case, edit)
        returned = attach_physical(case, JointSolver(4).solve(tables))
        for _ in range(2):
            receipt = checker.verify(edit, returned)
            assert receipt["exact"]
            assert not receipt.get("original_verification_cache_hits")
            assert receipt["raw_source_NAND_evaluations"] >= 1
            assert receipt["raw_source_NAND_evaluations"] + receipt["raw_source_unchanged_NANDs_reused"] == len(source_stage["gates"])
            assert receipt["raw_source_NAND_evaluations"] == receipt["source_stage_NAND_evaluations"]
            submitted_hits_and_misses.append((receipt["raw_return_history_expression_hits"],
                                             receipt["raw_return_history_expression_misses"]))
    assert any(hits > 0 and misses > 0 for hits, misses in submitted_hits_and_misses)
    # A child is always branched from the original, irrespective of call order.
    for edit in reversed(case["edits"]):
        tables = scalar_targets(case, edit)
        checker.verify(edit, attach_physical(case, JointSolver(4).solve(tables)))
    direct = Checker(case, raw_replay="direct")
    for edit in case["edits"]:
        returned = attach_physical(case, JointSolver(4).solve(scalar_targets(case, edit)))
        receipt = direct.verify(edit, returned)
        assert receipt["raw_return_NAND_evaluations"] == len(returned["circuit"]["gates"])
        assert receipt["raw_return_history_expression_hits"] == 0

    bad = deepcopy(answer)
    bad["physical"]["gates"][0] = [0, 0]
    rejected(lambda: checker.verify(None, bad), "unchanged prefix")
    bad = deepcopy(answer)
    bad["physical"]["outputs"].reverse()
    rejected(lambda: checker.verify(None, bad), "do not match the stage lift")
    bad = deepcopy(answer)
    bad["summary_wires"] = [bad["triple"][0]]
    bad = attach_physical(case, bad)
    rejected(lambda: checker.verify(None, bad), "bypasses")

    # This circuit is exact and the selected group's reported local width is
    # right, but another eligible triple has a strictly smaller width.
    for group in combinations(range(4), 3):
        count = scalar_classes(4, original_tables, group)
        width = (count - 1).bit_length()
        if width > 1:
            bad = dict(status="exact", n=4, width=width, class_count=count,
                       triple=list(group), summary_wires=list(group[:width]),
                       circuit=source_stage)
            rejected(lambda: checker.verify(None, attach_physical(case, bad)), "smaller sufficient summary")
            break
    else:
        raise AssertionError("missing nonminimal synthetic group")
    stale = dict(case["edits"][0], to=case["frontier"][1])
    rejected(lambda: checker.verify(stale, answer), "immutable public case")
    rejected(lambda: checker.verify(case["edits"][0], answer), "incorrect")

    alias = dict(id="dependent-frontier", n=5, upstream_count=4,
                 gates=[[0, 1], [0, 7], [1, 7], [8, 9]],
                 frontier=[0, 1, 10], outputs=[10, 10], pieces=[])
    rejected(lambda: Checker(alias), "not jointly independently attainable")
    # Constructor owns its immutable wiring, not a borrowed mutable case list.
    case["gates"][0] = [0, 0]
    checker.verify(None, answer)
    assert checker.work_counters()["verification_calls"] >= 10
    return dict(original_and_edited_raw_replays="passed", unique_parent_edit_raw_rows=192,
                forbidden_prefix_and_tap_changes="rejected", structural_bypass="rejected",
                locally_correct_nonminimum_group="rejected", stale_edit="rejected",
                dependent_frontier="rejected", sibling_answer_cache="absent",
                changed_source_hits_and_misses=history_hits_and_misses,
                submitted_return_hits_and_misses=submitted_hits_and_misses,
                numeric_wire_rebinding="recomputed", direct_raw_replay="matched")


if __name__ == "__main__":
    print(check())
