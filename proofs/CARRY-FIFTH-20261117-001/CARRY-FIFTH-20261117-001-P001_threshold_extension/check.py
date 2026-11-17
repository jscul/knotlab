"""Enumerate exact ternary-knot attachments to the fixed four-bit relation."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from knotlab import Relation, check_knot


State = tuple[bool, ...]
Rows = frozenset[State]
Order = tuple[int, ...]
Recoding = tuple[Order, State]
DISPLAY = "abcde"
TERNARY_STATES = tuple(product((False, True), repeat=3))


def parse_rows(*rows: str) -> Rows:
    return frozenset(tuple(bit == "1" for bit in row) for row in rows)


OLD_ROWS = parse_rows("0000", "0001", "0011", "0111", "1000", "1100", "1110", "1111")


def state_text(state: State) -> str:
    return "".join("1" if bit else "0" for bit in state)


def table(rows: Rows) -> list[str]:
    return [state_text(row) for row in sorted(rows)]


def display(order: Order) -> str:
    return "".join(DISPLAY[index] for index in order)


def recode(row: State, order: Order, flips: State) -> State:
    result = [False] * len(row)
    for source, target in enumerate(order):
        result[target] = row[source] != flips[target]
    return tuple(result)


def recoding_record(action: Recoding) -> dict[str, str]:
    order, flips = action
    return {"order": display(order), "flip_mask": state_text(flips)}


def threshold(order: Order, flips: State) -> Rows:
    """Generate cuts in the given order and their simultaneous complements."""
    width = len(order)
    return frozenset(
        recode(tuple((position < cut) != complement for position in range(width)), order, flips)
        for cut in range(width + 1)
        for complement in (False, True)
    )


def signed_thresholds(width: int) -> dict[Rows, list[Recoding]]:
    by_rows = defaultdict(list)
    masks = tuple(product((False, True), repeat=width))
    for order in permutations(range(width)):
        for flips in masks:
            by_rows[threshold(order, flips)].append((order, flips))
    return dict(by_rows)


def knot_supports() -> list[Rows]:
    names = ("first", "second", "fresh")
    supports = []
    for mask in range(1 << len(TERNARY_STATES)):
        rows = frozenset(
            row for index, row in enumerate(TERNARY_STATES) if mask & (1 << index)
        )
        if check_knot(Relation(names, rows), names[:2], names[-1]).is_knot:
            supports.append(rows)
    return supports


def attach(old_rows: Rows, pair: tuple[int, int], support: Rows) -> Rows:
    first, second = pair
    return frozenset(
        row + (fresh,)
        for row in old_rows
        for fresh in (False, True)
        if (row[first], row[second], fresh) in support
    )


def symmetry_summary(actions: list[Recoding]) -> dict:
    coordinate_orbits = sorted(
        {tuple(sorted({order[index] for order, _ in actions})) for index in range(4)}
    )
    state_orbits = sorted(
        {tuple(sorted({recode(row, *action) for action in actions})) for row in OLD_ROWS}
    )
    endpoint_sets = sorted({tuple(sorted((order[0], order[-1]))) for order, _ in actions})
    return {
        "automorphism_count": len(actions),
        "automorphisms": [recoding_record(action) for action in actions],
        "coordinate_orbits": [display(orbit) for orbit in coordinate_orbits],
        "state_orbits": [[state_text(row) for row in orbit] for orbit in state_orbits],
        "fixed_coordinates": [display(orbit) for orbit in coordinate_orbits if len(orbit) == 1],
        "fixed_states": [state_text(orbit[0]) for orbit in state_orbits if len(orbit) == 1],
        "endpoint_coordinate_sets": [display(pair) for pair in endpoint_sets],
        "preserves_endpoint_set_ad": len(endpoint_sets) == 1,
        "fixing_d_coordinate": [
            recoding_record(action) for action in actions if action[0][3] == 3
        ],
        "fixing_d_coordinate_and_value": [
            recoding_record(action)
            for action in actions
            if action[0][3] == 3 and not action[1][3]
        ],
    }


def old_recoding_groups() -> dict[str, list[Recoding]]:
    actions = signed_thresholds(4)[OLD_ROWS]
    return {
        "permutations": [action for action in actions if not any(action[1])],
        "permutations_and_simultaneous_flip": [
            action for action in actions if len(set(action[1])) == 1
        ],
        "permutations_and_independent_flips": actions,
    }


def constituent_record(triple: Order, support: Rows) -> dict:
    outer_pairs = []
    for middle in range(3):
        first, last = (index for index in range(3) if index != middle)
        if all(row[first] != row[last] or row[middle] == row[first] for row in support):
            outer_pairs.append(display((triple[first], triple[last])))
    return {
        "triple": display(triple),
        "support": table(support),
        "excluded_patterns": table(frozenset(TERNARY_STATES) - support),
        "common_value_outer_pairs": outer_pairs,
    }


def retained_constituent_control(supports: list[Rows], groups: dict[str, list[Recoding]]) -> dict:
    """Retest choices with the unordered local allowed relations still visible."""
    old_cube = tuple(product((False, True), repeat=4))
    lifted_knots = [
        (
            triple,
            support,
            frozenset(
                row for row in old_cube if tuple(row[index] for index in triple) in support
            ),
        )
        for triple in combinations(range(4), 3)
        for support in supports
    ]
    presentations = []
    for first, second in combinations(lifted_knots, 2):
        if first[2] & second[2] != OLD_ROWS:
            continue
        constituents = [
            constituent_record(triple, support) for triple, support, _ in (first, second)
        ]
        lifted = {first[2], second[2]}
        stabilizers = {}
        for group, actions in groups.items():
            preserving = []
            for action in actions:
                transformed = {
                    frozenset(recode(row, *action) for row in relation)
                    for relation in lifted
                }
                if transformed == lifted:
                    preserving.append(action)
            stabilizers[group] = symmetry_summary(preserving)

        outer_pairs = [item["common_value_outer_pairs"] for item in constituents]
        occurrences = Counter(name for item in constituents for name in item["triple"])
        presentations.append(
            {
                "constituents": constituents,
                "common_value_outer_in_both": [
                    name for name in DISPLAY[:4]
                    if all(len(pairs) == 1 and name in pairs[0] for pairs in outer_pairs)
                ],
                "common_value_outer_in_its_only_constituent": [
                    name for name in DISPLAY[:4]
                    if occurrences[name] == 1
                    and any(len(pairs) == 1 and name in pairs[0] for pairs in outer_pairs)
                ],
                "presentation_preserving_symmetries": stabilizers,
            }
        )
    return {
        "classification": "post_census_sensitivity",
        "lifted_knot_count": len(lifted_knots),
        "unordered_pairs_tested": comb(len(lifted_knots), 2),
        "singletons_reproducing_old_relation": [
            constituent_record(triple, support)
            for triple, support, rows in lifted_knots
            if rows == OLD_ROWS
        ],
        "presentations_reproducing_old_relation": presentations,
    }


def common_value_endpoints(rows: list[str], orders: list[str]) -> str:
    disagreements = {
        display((left, right)): sum(row[left] != row[right] for row in rows)
        for left, right in combinations(range(len(DISPLAY)), 2)
    }
    largest = max(disagreements.values())
    (endpoints,) = (pair for pair, count in disagreements.items() if count == largest)
    assert all(endpoints == "".join(sorted((order[0], order[-1]))) for order in orders)
    return endpoints


def fifth_attachment_constituent_control(
    presentations: list[dict], attachments: list[dict]
) -> dict:
    """Retain three local relations as an unordered family without marking the fresh one."""
    cube = tuple(state_text(row) for row in product((False, True), repeat=len(DISPLAY)))
    presentations_report = []
    intersection_sizes = Counter()
    state_sizes = Counter()
    shared_value_roles = Counter()
    for presentation in presentations:
        old_knots = frozenset(
            (factor["triple"], frozenset(factor["support"]))
            for factor in presentation["constituents"]
        )
        cases = []
        for attachment in attachments:
            new_knot = (attachment["attachment_triple"], frozenset(attachment["support"]))
            family = old_knots | {new_knot}
            common = sorted(set.intersection(*(set(scope) for scope, _ in family)))
            constraints = [
                (tuple(DISPLAY.index(name) for name in scope), allowed)
                for scope, allowed in family
            ]
            joint = {
                row for row in cube
                if all(
                    "".join(row[index] for index in scope) in allowed
                    for scope, allowed in constraints
                )
            }
            assert joint == set(attachment["rows"])
            intersection_sizes[len(common)] += 1
            state_sizes[len(joint)] += 1
            orders = attachment["all_positive_orders"]
            endpoints = None
            common_role = None
            if orders:
                endpoints = common_value_endpoints(attachment["rows"], orders)
                if len(common) == 1:
                    common_role = "endpoint" if common[0] in endpoints else "interior"
                    shared_value_roles[common_role] += 1
            cases.append(
                {
                    "unordered_knot_scopes": sorted(scope for scope, _ in family),
                    "attachment_excluded_patterns": attachment["excluded_patterns"],
                    "common_distinctions": common,
                    "common_distinction_count": len(common),
                    "joint_state_count": len(joint),
                    "shared_value_insertion_slot": attachment["aligned_insertion_slot"],
                    "shared_value_endpoints": endpoints,
                    "shared_value_common_distinction_role": common_role,
                }
            )
        outward = sorted(
            (case for case in cases if case["shared_value_insertion_slot"] in (0, 4)),
            key=lambda case: case["shared_value_insertion_slot"],
        )
        presentations_report.append(
            {
                "old_knot_scopes": sorted(scope for scope, _ in old_knots),
                "cases": cases,
                "outward_choice_contrast": {
                    "same_common_distinctions": len(
                        {tuple(case["common_distinctions"]) for case in outward}
                    ) == 1,
                    "choices": [
                        {
                            "slot": case["shared_value_insertion_slot"],
                            "common_distinctions": case["common_distinctions"],
                            "endpoints": case["shared_value_endpoints"],
                            "common_distinction_role": (
                                case["shared_value_common_distinction_role"]
                            ),
                        }
                        for case in outward
                    ],
                },
            }
        )
    return {
        "classification": "post_census_sensitivity",
        "case_count": sum(intersection_sizes.values()),
        "common_distinction_count_histogram": dict(intersection_sizes),
        "joint_state_count_histogram": dict(state_sizes),
        "shared_value_common_distinction_roles": dict(shared_value_roles),
        "presentations": presentations_report,
    }


def mirror_histories() -> dict:
    support = frozenset(TERNARY_STATES) - parse_rows("010", "101")
    histories = []
    old_relations = []
    end_extensions = []
    for order in ((0, 1, 2, 3, 4), (3, 2, 1, 0, 4)):
        rows = frozenset(product((False, True), repeat=2))
        steps = []
        for width in (3, 4, 5):
            pair = (0, width - 2)
            rows = attach(rows, pair, support)
            assert rows == threshold(tuple(range(width)), (False,) * width)
            steps.append(display(tuple(order[index] for index in (*pair, width - 1))))
            if width == 4:
                old_relations.append(
                    frozenset(recode(row, order[:4], (False,) * 4) for row in rows)
                )
        extension = frozenset(recode(row, order, (False,) * 5) for row in rows)
        end_extensions.append(extension)
        histories.append(
            {
                "formation_order": display(order),
                "attachment_triples": steps,
                "old_rows": table(old_relations[-1]),
                "end_extension_rows": table(extension),
            }
        )
    first, second = end_extensions
    union = first | second
    return {
        "excluded_triples_at_each_step": table(frozenset(TERNARY_STATES) - support),
        "histories": histories,
        "old_relations_equal_fixed_relation": all(rows == OLD_ROWS for rows in old_relations),
        "end_extensions_equal": first == second,
        "end_choice_intersection_rows": table(first & second),
        "end_choice_union_rows": table(union),
        "end_choice_union_is_free_extension": union
        == frozenset(row + (bit,) for row in OLD_ROWS for bit in (False, True)),
    }


def run() -> dict:
    supports = knot_supports()
    assert threshold((0, 1, 2, 3), (False,) * 4) == OLD_ROWS
    targets = signed_thresholds(5)
    aligned_orders = [tuple(range(slot)) + (4,) + tuple(range(slot, 4)) for slot in range(5)]
    aligned_slots = {
        threshold(order, (False,) * 5): slot for slot, order in enumerate(aligned_orders)
    }
    candidates = [
        (pair, support, attach(OLD_ROWS, pair, support))
        for pair in combinations(range(4), 2)
        for support in supports
    ]
    size_counts = Counter(len(rows) for _, _, rows in candidates)
    passing = []
    for pair, support, rows in candidates:
        assert frozenset(row[:4] for row in rows) == OLD_ROWS
        if rows in targets:
            actions = targets[rows]
            passing.append(
                {
                    "attachment_triple": display((*pair, 4)),
                    "support": table(support),
                    "excluded_patterns": table(frozenset(TERNARY_STATES) - support),
                    "state_count": len(rows),
                    "rows": table(rows),
                    "aligned_insertion_slot": aligned_slots.get(rows),
                    "all_positive_orders": [
                        display(order) for order, flips in actions if not any(flips)
                    ],
                    "signed_presentation_count": len(actions),
                    "signed_presentation_example": recoding_record(actions[0]),
                }
            )
    aligned_counts = Counter(record["aligned_insertion_slot"] for record in passing)
    (threshold_size,) = {len(rows) for rows in targets}
    equal_size = size_counts[threshold_size]
    exact_matches = {
        "fixed_order_positive": len(passing) - aligned_counts[None],
        "all_orders_positive": sum(bool(record["all_positive_orders"]) for record in passing),
        "all_orders_and_signs": len(passing),
    }
    negative_support = frozenset(TERNARY_STATES) - parse_rows("000", "110")
    negative_rows = attach(OLD_ROWS, (0, 1), negative_support)
    groups = old_recoding_groups()
    constituent_control = retained_constituent_control(supports, groups)
    return {
        "fixed_old_rows": table(OLD_ROWS),
        "ternary_supports_tested": 1 << len(TERNARY_STATES),
        "ternary_knot_count": len(supports),
        "ternary_knot_sizes": dict(Counter(map(len, supports))),
        "attachment_count": len(candidates),
        "attachment_state_sizes": dict(size_counts),
        "threshold_state_count": threshold_size,
        "signed_threshold_relation_count": len(targets),
        "signed_threshold_presentation_count": sum(map(len, targets.values())),
        "comparison": {
            name: {
                "exact_matches": count,
                "exact_rejects": len(candidates) - count,
                "count_matches": equal_size,
                "count_rejects": len(candidates) - equal_size,
                "count_matches_that_fail_exact_equality": equal_size - count,
            }
            for name, count in exact_matches.items()
        },
        "positive_insertion_slots": [
            {
                "slot": slot,
                "kind": "end" if slot in (0, 4) else "interior",
                "order": display(order),
                "exact_matches": aligned_counts[slot],
            }
            for slot, order in enumerate(aligned_orders)
        ],
        "end_attachment_count": aligned_counts[0] + aligned_counts[4],
        "interior_attachment_count": sum(aligned_counts[slot] for slot in (1, 2, 3)),
        "signed_only_attachment_count": exact_matches["all_orders_and_signs"]
        - exact_matches["all_orders_positive"],
        "passing_attachments": passing,
        "equal_size_negative_control": {
            "attachment_triple": "abe",
            "excluded_patterns": table(frozenset(TERNARY_STATES) - negative_support),
            "is_ternary_knot": negative_support in supports,
            "state_count": len(negative_rows),
            "matches_signed_threshold": negative_rows in targets,
            "allowed_row": "00001",
            "allowed_row_present": bool(parse_rows("00001") & negative_rows),
            "complemented_row": "11110",
            "complemented_row_present": bool(parse_rows("11110") & negative_rows),
        },
        "old_symmetries": {group: symmetry_summary(actions) for group, actions in groups.items()},
        "mirror_histories": mirror_histories(),
        "retained_constituent_control": constituent_control,
        "fifth_attachment_constituent_control": fifth_attachment_constituent_control(
            constituent_control["presentations_reproducing_old_relation"], passing
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
