"""Verify the finite premises and controls for the marked width-22 obstruction."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from functools import cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREVIOUS = (
    HERE.parents[1] / "VARIABLE-OUTPUT-READER-20261118-001D"
    / "VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse"
)
FILES = {
    "check_span_controls.py": "ece53f8c0aa3f71c6be5984de374992d11c15bd3f4a20e9ff979d4c57e7cd6a2",
    "continuation.json": "8235526471d3b1348dc0a23bb07481ec699abb66fd6e3bf2eebf80af153c1066",
}
N = 22
OLD = tuple(range(N))
RADIUS = 7
LEFT = (14, 15, 20)
RIGHT = (14, 15, 16)


def checked_file(name):
    path = PREVIOUS / name
    assert sha256(path.read_bytes()).hexdigest() == FILES[name]
    return path


@cache
def inherited():
    path = checked_file("check_span_controls.py")
    spec = importlib.util.spec_from_file_location("equalizer_predecessor", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    controls = module.controls()
    scout, rules = module.scout_and_rules()
    return module, controls, scout, rules, controls.inherited()


def scopes(supports):
    return dict(enumerate(supports))


def measure(supports):
    kernel, _, scout, _, _ = inherited()
    width = len(set().union(*supports))
    return kernel.measure_every_pair(scout.parity_span(scopes(supports)), width)


def original():
    _, _, scout, rules, _ = inherited()
    data = json.loads(checked_file("continuation.json").read_text())
    witness = data["matched_retained_rows_control"]
    assert witness["same_arrangement"]
    assert witness["left"]["checks"] == witness["right"]["checks"]
    assert tuple(witness["left"]["marked"]) == LEFT and tuple(witness["right"]["marked"]) == RIGHT
    fixture = scout.Fixture((), (3,), ())
    history = tuple((tuple(parents), count) for parents, count in witness["left"]["history"])
    for parents, count in history:
        assert parents in {p for p, _ in scout.legal_parent_sets(rules, fixture.checks())}
        fixture = fixture.successor(parents, count)
    supports = tuple(fixture.checks().values())
    assert supports == tuple(tuple(row) for row in witness["left"]["checks"].values())
    return supports, history, dict(witness["retained_row_preserving_map"])


def marked_grade(supports, marks):
    _, _, scout, rules, _ = inherited()
    owners, neighbors = rules.incidence(scopes(supports))
    assert all(len(owners[bit]) == 1 for bit in marks)
    holders = tuple(owners[bit][0] for bit in marks)
    assert len(set(holders)) == 3
    pairs = tuple(tuple(sorted(neighbors[a] & neighbors[b])) for a, b in combinations(holders, 2))
    common = tuple(sorted(set.intersection(*(neighbors[holder] for holder in holders))))
    decision = all(pairs) and not common
    assert decision == rules.legal_local_move(scopes(supports), marks, scout.FRESH_FOR_PARENT_TEST)
    return {"marks": marks, "holders": holders, "pair_witnesses": pairs, "common_witnesses": common, "legal": decision}


def shortest_pair_shell(rows, marks):
    pairs = tuple(combinations(marks, 2))
    ordered = sorted(pairs, key=lambda p: rows[p[0]][p[1]])
    assert rows[ordered[0][0]][ordered[0][1]] < rows[ordered[1][0]][ordered[1][1]]
    center, = set(marks) - set(ordered[0])
    counted = tuple((a, b) for a, b in combinations((i for i in range(len(rows)) if i not in marks), 2)
                    if rows[a][b] == 5 and sorted((rows[center][a], rows[center][b])) == [6, 7])
    return {"mark_opposite_unique_minimum_pair": center, "count": len(counted), "pairs": counted}


def append(original_supports, moves, reserved, ignore_parent_test=False):
    _, _, scout, rules, _ = inherited()
    supports = original_supports
    width = N
    history = []
    for used, count in moves:
        owners, _ = rules.incidence(scopes(supports))
        assert not (set(used) & set(reserved)) and count in (2, 3)
        assert all(len(owners[bit]) == 1 for bit in used)
        parents = tuple(owners[bit][0] for bit in used)
        assert len(set(parents)) == len(parents)
        conventionally_legal = rules.legal_local_move(scopes(supports), used, scout.FRESH_FOR_PARENT_TEST)
        assert conventionally_legal != ignore_parent_test
        fresh = tuple(range(width, width + count))
        supports = (*supports, tuple(sorted((*used, *fresh))))
        history.append({"parents": parents, "used": used, "fresh": fresh, "legal_under_join_rule": conventionally_legal})
        width += count
    return supports, history


def radius_set(rows, marks):
    return tuple(i for i in range(len(rows)) if all(rows[m][i] <= RADIUS for m in marks))


def old_changes(before, after):
    return tuple((a, b, before[a][b], after[a][b]) for a, b in combinations(OLD, 2)
                 if before[a][b] != after[a][b])


def attachment_costs(supports, anchors, control_path):
    _, _, scout, _, _ = inherited()
    attached_to = {anchor: anchor for anchor in anchors}
    attachments = {anchor: [] for anchor in anchors}
    for junction, step in enumerate(control_path, start=len(supports) - len(control_path)):
        anchor, = {attached_to[parent] for parent in step["parents"]}
        attached_to[junction] = anchor
        attachments[anchor].append(junction)

    results = {}
    original_mask = (1 << N) - 1
    for anchor, selected in attachments.items():
        margins = {}
        for size in range(1, len(selected) + 1):
            smallest = None
            for subset in combinations(selected, size):
                support = 0
                for junction in subset:
                    support ^= scout.mask(supports[junction])
                old = (support & original_mask).bit_count()
                new = (support >> N).bit_count()
                assert old <= len(anchors[anchor])
                assert new >= min(size + 1, 4)
                difference = new - old
                assert difference > 0
                smallest = difference if smallest is None else min(smallest, difference)
            margins[size] = smallest
        results[anchor] = {"junctions": selected, "least_net_added_support_by_number_selected": margins}
    return results


def demonstration(supports, rows, anchors):
    _, controls, _, _, trim = inherited()
    # The first collection connects three initial loose distinctions and has
    # no bridge to the old arrangement. The other attaches by one bit.
    path = (((17,), 2), ((18,), 2), ((19,), 3), ((22, 24), 2), ((23, 26), 2), ((20,), 3))
    next_supports, steps = append(supports, path, RIGHT)
    grown = measure(next_supports)
    assert len(grown) == 36 and not old_changes(rows, grown)
    assert radius_set(grown, RIGHT) == OLD
    fresh_lower = {mark: min(grown[mark][i] for i in range(N, len(grown))) for mark in RIGHT[:2]}
    assert fresh_lower == {14: 8, 15: 8}
    finite, cuts = trim.scalar_cuts(grown)
    graph = controls.incidence_graph(next_supports, len(grown))
    physical, actual = controls.incidence_deletions(graph, len(grown))
    assert tuple(sorted(finite)) == physical and cuts == actual
    retained = trim.retained_part(grown, RIGHT)
    assert retained == tuple(range(33))
    right = marked_grade(next_supports, RIGHT)
    assert not right["legal"] and right["common_witnesses"] == (7,)
    return {
        "history": steps, "width": len(grown), "original_entries_verified": len(tuple(combinations(OLD, 2))),
        "new_distinctions_retained": tuple(i for i in retained if i >= N),
        "new_distinctions_removed": tuple(i for i in range(N, len(grown)) if i not in retained),
        "marked_radius_set": radius_set(grown, RIGHT), "minimum_new_distances_from_fixed_marks": fresh_lower,
        "attachment_boundary_cost_controls": attachment_costs(next_supports, anchors, steps),
    }


def negative_controls(supports, rows):
    left_supports, left_step = append(supports, (((16, 21), 2),), LEFT)
    left = measure(left_supports)
    delta = old_changes(rows, left)
    assert (16, 21, 6, 3) in delta and all(new < old for _, _, old, new in delta)
    left_grade = marked_grade(left_supports, LEFT)
    assert left_grade["legal"]
    assert radius_set(left, LEFT) == tuple(range(24))

    split_supports, split_step = append(supports, (((17, 20), 2),), RIGHT, ignore_parent_test=True)
    split = measure(split_supports)
    gap = old_changes(rows, split)
    assert (17, 20, 7, 3) in gap
    assert radius_set(split, RIGHT) == tuple(range(24))
    assert not marked_grade(split_supports, RIGHT)["legal"]
    return {
        "lawful_left_with_its_own_marks_preserved": {
            "history": left_step, "shortened_original_entries": delta,
            "new_distinctions_within_radius_on_all_marks": (22, 23),
        },
        "counterfactual_join_between_attachments_preserving_right_marks": {
            "history": split_step, "shortened_original_entries": gap,
            "new_distinctions_within_radius_on_all_marks": (22, 23),
        },
    }


def run():
    _, controls, scout, rules, trim = inherited()
    supports, history, previous_map = original()
    rows = measure(supports)
    assert len(rows) == N and all(trim.INFINITY not in row for row in rows)
    seed_table = scout.full_table(scout.parity_span(scopes(supports)), N)
    assert trim.matrix_from_pairs(seed_table, N) == rows
    baseline, cuts = controls.incidence_deletions(controls.incidence_graph(supports, N), N)
    assert baseline == ((1 << N) - 1,) and not cuts
    assert trim.scalar_cuts(rows) == (baseline, cuts)
    assert radius_set(rows, LEFT) == radius_set(rows, RIGHT) == OLD
    left_grade, right_grade = (marked_grade(supports, mark) for mark in (LEFT, RIGHT))
    assert left_grade["legal"] and not right_grade["legal"]

    owners, neighbors = rules.incidence(scopes(supports))
    ports = rules.loose_ports(owners)
    anchors = {u: tuple(i for i in available if i not in RIGHT) for u, available in ports.items()}
    anchors = {u: available for u, available in anchors.items() if available}
    assert anchors == {7: (17, 18, 19), 8: (20, 21)}
    assert 7 not in neighbors[8] and not (neighbors[7] & neighbors[8])
    assert all(len(supports[u]) <= 6 for u in anchors)
    anchor_distances = {u: [tuple(rows[m][i] for m in RIGHT[:2]) for i in old_loose]
                        for u, old_loose in anchors.items()}
    assert all(pair == (7, 7) for values in anchor_distances.values() for pair in values)
    shells = {key: shortest_pair_shell(rows, marks) for key, marks in (("left", LEFT), ("right", RIGHT))}
    assert [item["count"] for item in shells.values()] == [5, 0]
    disagreements = [(a, b) for a, b in combinations(OLD, 2)
                     if rows[a][b] != rows[previous_map[a]][previous_map[b]]]
    assert len(disagreements) == 10

    return {
        "dependencies": FILES,
        "initial_width": N, "initial_history": history, "initial_junctions": supports,
        "initial_true_and_false_marks": (left_grade, right_grade),
        "whole_original_incidence_has_no_single_distinction_separator": True,
        "original_old_distances_at_most_seven_from_every_mark": True,
        "right_legal_initial_ports_after_reserving_its_marks": anchors,
        "right_initial_holders_lack_meeting_and_common_witness": True,
        "right_anchor_loose_distances_from_14_and_15": anchor_distances,
        "original_three_row_map_disagreements": disagreements,
        "original_shell_invariant": shells,
        "lawful_right_example": demonstration(supports, rows, anchors),
        "matched_negative_controls": negative_controls(supports, rows),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the checked equalize_rows.json")
    args = parser.parse_args()
    result = json.dumps(run(), sort_keys=True, indent=2) + "\n"
    target = HERE / "equalize_rows.json"
    if args.write:
        target.write_text(result)
    else:
        assert target.read_text() == result
        print("Marked width-22 equalization controls reproduced.")
