"""Join released action bits to the reserved key and score the frozen two-arm comparison."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product


ARMS = ("narrow", "varied")
LAWS = ("parity", "nae")
BACKENDS = (*LAWS, "integer")
LETTERS = ("L", "T")
TURNS = (0, 1, 2, 3)
HELD_TURNS = (2, 3)
POSITIONS = ("familiar", "new")
DESIGNS = tuple(f"{base}-blind-{index}" for base in ("E", "F") for index in range(1, 5))
CONDITIONS = {
    "familiar": ("familiar", False),
    "position": ("new", False),
    "orientation": ("familiar", True),
    "combined": ("new", True),
}
KNOT_CONTROLS = (
    "ordinary", "opposite", "swapped-ordinary", "swapped-opposite", "sham-ordinary",
    "clear-ordinary", "restored-ordinary", "erase-ordinary", "cross-ordinary",
    "other-groups-ordinary",
)
ACTION_COLUMNS = tuple(
    f"{arm}-{backend}-{control}"
    for arm, backend in product(ARMS, BACKENDS)
    for control in (KNOT_CONTROLS if backend in LAWS else ("ordinary", "opposite"))
)
_ACTION_SET = frozenset(ACTION_COLUMNS)
_ANCHORS = {
    position: frozenset((row, col) for row, col in product(range(4), repeat=2)
                        if (row + col) % 2 == (position == "familiar"))
    for position in POSITIONS
}


def _indexed(rows):
    indexed = {}
    for row in rows:
        identity = row["id"]
        if not isinstance(identity, str) or not identity or identity in indexed:
            raise ValueError("missing or duplicate bitmap ID")
        indexed[identity] = row
    return indexed


def _committee(detail, action):
    rule_votes = detail["rule_votes"]
    if any(vote is not None and (type(vote) is not int or vote not in (0, 1))
           for vote in rule_votes):
        raise ValueError("invalid individual rule vote")
    zero, one, abstentions = (rule_votes.count(vote) for vote in (0, 1, None))
    if (detail["phase"] != "deployment" or detail["votes"] != [zero, one]
            or detail["abstentions"] != abstentions or detail["guess"] != action
            or action != int(one > zero)):
        raise ValueError("parity committee details disagree with the released action")
    return {
        "both_actions_received_votes": zero > 0 and one > 0,
        "at_least_one_abstention": abstentions > 0,
        "tied_with_split_votes": zero == one and zero > 0,
        "all_rules_abstained": bool(rule_votes) and zero == one == 0,
        "no_rules": not rule_votes,
        "action_zero_by_default": zero == one,
        "strict_majority_zero": zero > one,
        "strict_majority_one": one > zero,
    }


def _join(predictions, key_rows):
    blind = _indexed(predictions)
    keys = _indexed(key_rows)
    if blind.keys() != keys.keys():
        raise ValueError("released predictions and scorer key have different bitmap IDs")

    for identity, key in sorted(keys.items()):
        design, label, turn = key["style"], key["label"], key["q"]
        condition = key["condition"]
        row, col = key["row"], key["col"]
        if (design not in DESIGNS or key["base_style"] != design[0]
                or key["style_stratum"] != "blind" or label not in LETTERS
                or type(turn) is not int or turn not in TURNS
                or condition not in CONDITIONS or type(row) is not int or type(col) is not int):
            raise ValueError(f"unregistered reserved key row {identity}")
        position, held = CONDITIONS[condition]
        if (row, col) not in _ANCHORS[position] or held != (turn in HELD_TURNS):
            raise ValueError(f"condition contradicts turn or anchor for {identity}")

        prediction = blind[identity]
        actions, details = prediction["actions"], prediction["details"]
        if (actions.keys() != _ACTION_SET or details.keys() != set(ARMS)
                or any(type(action) is not int or action not in (0, 1) for action in actions.values())):
            raise ValueError(f"incomplete action columns or invalid action bits for {identity}")
        truth = int(label == "T")
        correct = {name: action == (truth ^ int(name.endswith("-opposite")))
                   for name, action in actions.items()}
        yield {
            "id": identity, "design": design, "letter": label, "turn": turn, "position": position,
            "condition": condition, "anchor": (row, col), "correct": correct, "actions": actions,
            "committee": {arm: _committee(details[arm], actions[f"{arm}-parity-ordinary"])
                          for arm in ARMS},
        }


def _counts(rows):
    return {"total": len(rows),
            "correct": {name: sum(row["correct"][name] for row in rows) for name in ACTION_COLUMNS}}


def _paired(rows, first, second):
    counts = dict.fromkeys(("gain", "loss", "both_correct", "both_incorrect"), 0)
    examples = {}
    for row in rows:
        before, after = row["correct"][first], row["correct"][second]
        if before:
            outcome = "both_correct" if after else "loss"
        else:
            outcome = "gain" if after else "both_incorrect"
        counts[outcome] += 1
        examples.setdefault(outcome, row["id"])
    return {"total": len(rows), **counts, "ties": counts["both_correct"] + counts["both_incorrect"],
            "example_ids": examples}


def _contrasts(rows):
    return {backend: _paired(rows, f"narrow-{backend}-ordinary", f"varied-{backend}-ordinary")
            for backend in BACKENDS}


def _membership_crosses(rows, law):
    narrow = f"narrow-{law}-ordinary"
    varied = f"varied-{law}-ordinary"
    narrow_calibration = f"narrow-{law}-other-groups-ordinary"
    varied_calibration = f"varied-{law}-other-groups-ordinary"
    return {
        "replace_narrow_groups_under_narrow_calibration": _paired(rows, narrow, narrow_calibration),
        "replace_varied_groups_under_varied_calibration": _paired(rows, varied, varied_calibration),
        "replace_narrow_calibration_under_narrow_groups": _paired(rows, narrow, varied_calibration),
        "replace_varied_calibration_under_varied_groups": _paired(rows, varied, narrow_calibration),
    }


def _intervention_flags(actions, arm, law):
    other = "varied" if arm == "narrow" else "narrow"
    prefix = f"{arm}-{law}-"
    ordinary, opposite = actions[prefix + "ordinary"], actions[prefix + "opposite"]
    tracks_opposite = actions[prefix + "swapped-ordinary"] == opposite
    tracks_ordinary = actions[prefix + "swapped-opposite"] == ordinary
    return {
        "original_schedules_disagree": ordinary != opposite,
        "swapped_ordinary_matches_donor": tracks_opposite,
        "swapped_opposite_matches_donor": tracks_ordinary,
        "both_swaps_match_donors": tracks_opposite and tracks_ordinary,
        "both_swaps_reverse": ordinary != opposite and tracks_opposite and tracks_ordinary,
        "sham_ordinary_preserves": actions[prefix + "sham-ordinary"] == ordinary,
        "restored_ordinary_preserves": actions[prefix + "restored-ordinary"] == ordinary,
        "clear_ordinary_emits_zero": actions[prefix + "clear-ordinary"] == 0,
        "erasure_changes_action": actions[prefix + "erase-ordinary"] != ordinary,
        "erasure_emits_zero": actions[prefix + "erase-ordinary"] == 0,
        "cross_arm_swap_matches_donor": actions[prefix + "cross-ordinary"] ==
                                        actions[f"{other}-{law}-ordinary"],
        "other_groups_change_action": actions[prefix + "other-groups-ordinary"] != ordinary,
        "ordinary_twin_agrees": ordinary == actions[f"{arm}-integer-ordinary"],
        "opposite_twin_agrees": opposite == actions[f"{arm}-integer-opposite"],
    }


def _interventions(rows, arm, law):
    counts = Counter()
    for row in rows:
        counts.update(_intervention_flags(row["actions"], arm, law))
    return {"total": len(rows), **counts}


def _committee_counts(rows, arm):
    counts = Counter()
    for row in rows:
        counts.update(row["committee"][arm])
    return {"total": len(rows), **counts}


def _key(cell):
    design, letter, turn, position = cell
    return f"{design}/{letter}/q{turn}/{position}"


def _aggregate_names(row):
    turn = row["turn"]
    return (
        "all", "held_turns" if turn in HELD_TURNS else "training_turns", f"q{turn}",
        f"letter/{row['letter']}", f"position/{row['position']}", f"design/{row['design']}",
        f"condition/{row['condition']}", f"q{turn}/{row['position']}",
        f"q{turn}/{row['letter']}", f"q{turn}/{row['position']}/{row['letter']}",
    )


def _weighted_accuracy(design_turn_letter, turn_set):
    units = [rows for (_, _, turn), rows in design_turn_letter.items() if turn in turn_set]
    multiplicities = Counter(str(len(rows)) for rows in units)
    accuracy = {}
    for name in ACTION_COLUMNS:
        rate = sum(Fraction(sum(row["correct"][name] for row in rows), len(rows))
                   for rows in units) / len(units)
        accuracy[name] = [rate.numerator, rate.denominator]
    return {"unit_count": len(units), "translation_multiplicities": dict(sorted(multiplicities.items())),
            "accuracy": accuracy}


def _primary_gate(cells, primary):
    result = {}
    for arm, law in product(ARMS, LAWS):
        name = f"{arm}-{law}-ordinary"
        failed = [cell for cell in primary if 2 * cells[cell]["correct"][name] <= cells[cell]["total"]]
        result.setdefault(arm, {})[law] = {
            "passed": not failed, "cell_count": len(primary), "failed_cells": failed,
        }
    return result


def _attribution(gates, held_counts):
    result = {}
    for law in LAWS:
        narrow = held_counts["correct"][f"narrow-{law}-ordinary"]
        varied = held_counts["correct"][f"varied-{law}-ordinary"]
        varied_passed, narrow_passed = (gates[arm][law]["passed"] for arm in ("varied", "narrow"))
        result[law] = {
            "passed": varied_passed and not narrow_passed and varied > narrow,
            "varied_passed": varied_passed, "narrow_passed": narrow_passed,
            "held_total": held_counts["total"], "held_correct_narrow": narrow, "held_correct_varied": varied,
            "held_correct_difference": varied - narrow,
        }
    return result


def _examples(primary, exact):
    examples = {}
    for cell in primary:
        for row in exact[cell]:
            for arm, law in product(ARMS, LAWS):
                name = f"{arm}-{law}-ordinary"
                outcome = "correct" if row["correct"][name] else "incorrect"
                examples.setdefault(f"{cell}/{name}/{outcome}", row["id"])
    return examples


def summarize(predictions, key_rows):
    """Score the full reserved roster, with strict majority required in each held cell."""
    exact = defaultdict(list)
    aggregates = defaultdict(list)
    design_turn_letter = defaultdict(list)
    for row in _join(predictions, key_rows):
        design, letter, turn, position = (row[name] for name in ("design", "letter", "turn", "position"))
        exact[_key((design, letter, turn, position))].append(row)
        design_turn_letter[design, letter, turn].append(row)
        for name in _aggregate_names(row):
            aggregates[name].append(row)

    for cell in product(DESIGNS, LETTERS, TURNS, POSITIONS):
        name, position = _key(cell), cell[3]
        expected_anchors = _ANCHORS[position]
        if (len(exact[name]) != len(expected_anchors)
                or {row["anchor"] for row in exact[name]} != expected_anchors):
            raise ValueError(f"missing or unbalanced reserved cell {name}")

    cells = {name: _counts(rows) for name, rows in sorted(exact.items())}
    aggregate_counts = {name: _counts(rows) for name, rows in sorted(aggregates.items())}
    primary = [_key(cell) for cell in product(DESIGNS, LETTERS, HELD_TURNS, POSITIONS)]
    gates = _primary_gate(cells, primary)
    attribution = _attribution(gates, aggregate_counts["held_turns"])
    checkpoints = ("all", "held_turns", "training_turns", *(f"q{turn}" for turn in TURNS))
    return {
        "cells": cells,
        "aggregates": aggregate_counts,
        "primary_gate": gates,
        "attribution_gate": attribution,
        "both_laws_pass_attribution": all(law["passed"] for law in attribution.values()),
        "paired": {
            "cells": {name: _contrasts(rows) for name, rows in sorted(exact.items())},
            "aggregates": {name: _contrasts(rows) for name, rows in sorted(aggregates.items())},
        },
        "membership_calibration_crosses": {
            name: {law: _membership_crosses(aggregates[name], law) for law in LAWS}
            for name in checkpoints
        },
        "interventions": {
            name: {arm: {law: _interventions(aggregates[name], arm, law) for law in LAWS} for arm in ARMS}
            for name in checkpoints
        },
        "committee": {name: {arm: _committee_counts(rows, arm) for arm in ARMS}
                      for name, rows in sorted(aggregates.items())},
        "design_turn_letter_weighting": {
            "cells": {f"{design}/{letter}/q{turn}": _counts(rows)
                      for (design, letter, turn), rows in sorted(design_turn_letter.items())},
            "all": _weighted_accuracy(design_turn_letter, TURNS),
            "held_turns": _weighted_accuracy(design_turn_letter, HELD_TURNS),
        },
        "example_ids": _examples(primary, exact),
    }
