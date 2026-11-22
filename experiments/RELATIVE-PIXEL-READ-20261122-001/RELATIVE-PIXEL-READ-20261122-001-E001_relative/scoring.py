"""Score the matched blind roster and its physical memory controls."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product


READERS = ("position", "window_tree", "window_group")
LAWS = ("parity", "nae")
BACKENDS = (*LAWS, "integer")
CONTROLS = ("ordinary", "opposite", "sham", "swapped-ordinary", "swapped-opposite", "clear", "restored")
LETTERS = ("L", "T")
TURNS = (0, 1, 2, 3)
HELD_TURNS = (2, 3)
POSITIONS = ("familiar", "new")
DESIGNS = tuple(f"{base}-relative-{number}" for base in ("E", "F") for number in range(1, 5))
CONDITIONS = {
    "familiar": ("familiar", False),
    "position": ("new", False),
    "orientation": ("familiar", True),
    "combined": ("new", True),
}
ACTION_COLUMNS = tuple(f"{reader}-{backend}-{condition}" for reader, backend in product(READERS, BACKENDS)
                       for condition in (CONTROLS if backend in LAWS else ("ordinary", "opposite")))
_ACTION_SET = frozenset(ACTION_COLUMNS)
_OPPOSITE = frozenset(name for name in ACTION_COLUMNS if name.endswith("-opposite"))
_ANCHORS = {position: frozenset((row, col) for row, col in product(range(4), repeat=2)
                                if (row + col) % 2 == (position == "familiar"))
            for position in POSITIONS}


def _indexed(rows):
    result = {}
    for row in rows:
        identity = row["id"]
        if not isinstance(identity, str) or not identity or identity in result:
            raise ValueError("missing or duplicate bitmap ID")
        result[identity] = row
    return result


def _joined(predictions, key_rows):
    blind, keys = _indexed(predictions), _indexed(key_rows)
    if blind.keys() != keys.keys():
        raise ValueError("released actions and reserved key have different bitmap IDs")
    for identity, key in sorted(keys.items()):
        design, letter, turn = key["style"], key["label"], key["q"]
        condition, row, col = key["condition"], key["row"], key["col"]
        if (design not in DESIGNS or key["base_style"] != design[0]
                or key["style_stratum"] != "blind" or letter not in LETTERS
                or type(turn) is not int or turn not in TURNS or condition not in CONDITIONS
                or type(row) is not int or type(col) is not int):
            raise ValueError(f"unregistered blind key row {identity}")
        position, held = CONDITIONS[condition]
        if (row, col) not in _ANCHORS[position] or held != (turn in HELD_TURNS):
            raise ValueError(f"key condition contradicts the turn or anchor on {identity}")
        actions = blind[identity]["actions"]
        if actions.keys() != _ACTION_SET or any(type(bit) is not int or bit not in (0, 1) for bit in actions.values()):
            raise ValueError(f"incorrect action roster or action bit on {identity}")
        truth = int(letter == "T")
        correct = {name: action == (truth ^ int(name in _OPPOSITE)) for name, action in actions.items()}
        yield {"id": identity, "design": design, "letter": letter, "turn": turn, "position": position,
               "condition": condition, "anchor": (row, col), "actions": actions, "correct": correct}


def _counts(rows):
    letters = {letter: sum(row["letter"] == letter for row in rows) for letter in LETTERS}
    return {"total": len(rows), "true_letters": letters, "always_zero_ordinary_correct": letters["L"],
            "correct": {name: sum(row["correct"][name] for row in rows) for name in ACTION_COLUMNS}}


def _paired(rows, baseline_action, position_action):
    counts = dict.fromkeys(("gains", "losses", "both_correct", "both_incorrect"), 0)
    examples = {}
    for row in rows:
        baseline, position = row["correct"][baseline_action], row["correct"][position_action]
        if baseline:
            outcome = "both_correct" if position else "losses"
        else:
            outcome = "gains" if position else "both_incorrect"
        counts[outcome] += 1
        examples.setdefault(outcome, row["id"])
    return {"total": len(rows), **counts, "ties": counts["both_correct"] + counts["both_incorrect"],
            "example_ids": examples}


def _contrasts(rows):
    return {f"position_vs_{comparison}": {
        backend: _paired(rows, f"{comparison}-{backend}-ordinary", f"position-{backend}-ordinary")
        for backend in BACKENDS}
        for comparison in ("window_tree", "window_group")}


def _paired_units(groups, baseline_action, position_action):
    labels = ("gains", "losses", "both_correct", "both_incorrect", "tied_mixed")
    counts, examples = dict.fromkeys(labels, 0), {}
    uniform = 0
    for (design, letter, turn), rows in groups:
        baseline = sum(row["correct"][baseline_action] for row in rows)
        position = sum(row["correct"][position_action] for row in rows)
        uniform += int(baseline in (0, len(rows)) and position in (0, len(rows)))
        if position > baseline:
            outcome = "gains"
        elif position < baseline:
            outcome = "losses"
        elif position == len(rows):
            outcome = "both_correct"
        else:
            outcome = "tied_mixed" if position else "both_incorrect"
        counts[outcome] += 1
        examples.setdefault(outcome, f"{design}/{letter}/q{turn}")
    return {"total_units": len(groups), "translation_consistent_units": uniform, **counts,
            "ties": counts["both_correct"] + counts["both_incorrect"] + counts["tied_mixed"],
            "example_units": examples}


def _unit_contrasts(groups):
    return {f"position_vs_{comparison}": {
        backend: _paired_units(groups, f"{comparison}-{backend}-ordinary", f"position-{backend}-ordinary")
        for backend in BACKENDS}
        for comparison in ("window_tree", "window_group")}


def _control_flags(actions, reader, law):
    prefix = f"{reader}-{law}-"
    ordinary, opposite = actions[prefix + "ordinary"], actions[prefix + "opposite"]
    ordinary_tracks_donor = actions[prefix + "swapped-ordinary"] == opposite
    opposite_tracks_donor = actions[prefix + "swapped-opposite"] == ordinary
    ordinary_twin_agrees = actions[f"{reader}-integer-ordinary"] == ordinary
    opposite_twin_agrees = actions[f"{reader}-integer-opposite"] == opposite
    return {
        "originals_disagree": ordinary != opposite,
        "ordinary_swap_follows_opposite_donor": ordinary_tracks_donor,
        "opposite_swap_follows_ordinary_donor": opposite_tracks_donor,
        "both_swaps_follow_donors": ordinary_tracks_donor and opposite_tracks_donor,
        "both_swaps_reverse": ordinary != opposite and ordinary_tracks_donor and opposite_tracks_donor,
        "sham_preserves_ordinary": actions[prefix + "sham"] == ordinary,
        "blank_memory_emits_zero": actions[prefix + "clear"] == 0,
        "clearing_changes_ordinary": actions[prefix + "clear"] != ordinary,
        "restore_recovers_ordinary": actions[prefix + "restored"] == ordinary,
        "ordinary_twin_agrees": ordinary_twin_agrees,
        "opposite_twin_agrees": opposite_twin_agrees,
        "both_twins_agree": ordinary_twin_agrees and opposite_twin_agrees,
    }


def _interventions(rows, reader, law):
    counts, examples = Counter(), defaultdict(dict)
    for row in rows:
        flags = _control_flags(row["actions"], reader, law)
        counts.update(flags)
        for flag, applies in flags.items():
            examples[flag].setdefault("yes" if applies else "no", row["id"])
    return {"total": len(rows), **counts, "example_ids": dict(examples)}


def _gate(counts, names):
    gates = defaultdict(dict)
    for reader, law in product(READERS, LAWS):
        action = f"{reader}-{law}-ordinary"
        failed = [name for name in names if 2 * counts[name]["correct"][action] <= counts[name]["total"]]
        gates[reader][law] = {"passed": not failed, "cell_count": len(names), "failed_cells": failed}
    return dict(gates)


def _cell(design, letter, turn, position):
    return f"{design}/{letter}/q{turn}/{position}"


def _aggregate_names(row):
    turn, position, letter = (row[column] for column in ("turn", "position", "letter"))
    split = "held_turns" if turn in HELD_TURNS else "training_turns"
    return ("all", split, f"q{turn}", f"q{turn}/{letter}", f"q{turn}/{position}",
            f"q{turn}/{letter}/{position}", f"{split}/{letter}", f"{split}/{position}",
            f"letter/{letter}", f"position/{position}", f"design/{row['design']}", f"condition/{row['condition']}")


def _unit_weighted(groups):
    total = len(groups)
    by_action = {}
    for name in ACTION_COLUMNS:
        correct = Fraction(0)
        inconsistent = 0
        for rows in groups:
            correct += Fraction(sum(row["correct"][name] for row in rows), len(rows))
            inconsistent += int(len({row["actions"][name] for row in rows}) > 1)
        rate = correct / total
        by_action[name] = {"effective_correct_units": [correct.numerator, correct.denominator],
                           "accuracy": [rate.numerator, rate.denominator],
                           "uniform_decision_units": total - inconsistent,
                           "correct_uniform_units": correct.numerator if inconsistent == 0 else None}
    return {"total_units": total, "total_translations": sum(map(len, groups)),
            "translations_per_unit": dict(sorted(Counter(str(len(rows)) for rows in groups).items())),
            "actions": by_action}


def _unit_subsets(unshifted):
    units = sorted(unshifted.items())
    subsets = {"all": units, "held_turns": [(key, rows) for key, rows in units if key[2] in HELD_TURNS]}
    for turn in TURNS:
        at_turn = [(key, rows) for key, rows in units if key[2] == turn]
        subsets[f"q{turn}"] = at_turn
        for letter in LETTERS:
            by_letter = [(key, rows) for key, rows in at_turn if key[1] == letter]
            subsets[f"q{turn}/{letter}"] = by_letter
            for position in POSITIONS:
                subsets[f"q{turn}/{letter}/{position}"] = _unit_positions(by_letter, position)
    for position in POSITIONS:
        subsets[f"held_turns/{position}"] = _unit_positions(subsets["held_turns"], position)
    return subsets


def _unit_positions(units, position):
    return [(key, [row for row in rows if row["position"] == position]) for key, rows in units]


def _representatives(primary, exact):
    examples = {}
    for cell in primary:
        for row in exact[cell]:
            for reader, law in product(READERS, LAWS):
                name = f"{reader}-{law}-ordinary"
                outcome = "correct" if row["correct"][name] else "incorrect"
                examples.setdefault(f"{cell}/{name}/{outcome}", row["id"])
    return examples


def summarize(predictions, keys):
    """Join and score the registered blind panel, with each held cell counting separately."""
    exact, aggregates, unshifted = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in _joined(predictions, keys):
        design, letter, turn, position = (row[column] for column in ("design", "letter", "turn", "position"))
        exact[_cell(design, letter, turn, position)].append(row)
        unshifted[design, letter, turn].append(row)
        for name in _aggregate_names(row):
            aggregates[name].append(row)

    for design, letter, turn, position in product(DESIGNS, LETTERS, TURNS, POSITIONS):
        name, expected = _cell(design, letter, turn, position), _ANCHORS[position]
        rows = exact[name]
        if len(rows) != len(expected) or {row["anchor"] for row in rows} != expected:
            raise ValueError(f"missing or unbalanced reserved cell {name}")

    cells = {name: _counts(rows) for name, rows in sorted(exact.items())}
    aggregate_counts = {name: _counts(rows) for name, rows in sorted(aggregates.items())}
    primary = [_cell(*columns) for columns in product(DESIGNS, LETTERS, HELD_TURNS, POSITIONS)]
    pooled = [f"q{turn}/{letter}" for turn, letter in product(HELD_TURNS, LETTERS)]
    intervention_groups = ("all", "held_turns", "training_turns", *(f"q{turn}" for turn in TURNS),
                           *(f"held_turns/{position}" for position in POSITIONS))
    unit_subsets = _unit_subsets(unshifted)
    return {
        "cells": cells,
        "aggregates": aggregate_counts,
        "primary_gate": _gate(cells, primary),
        "descriptive_pooled_held_letter_turn_gate": _gate(aggregate_counts, pooled),
        "paired": {"cells": {name: _contrasts(rows) for name, rows in sorted(exact.items())},
                   "aggregates": {name: _contrasts(rows) for name, rows in sorted(aggregates.items())},
                   "unshifted_unit_aggregates": {name: _unit_contrasts(groups)
                                                 for name, groups in unit_subsets.items()}},
        "interventions": {name: {reader: {law: _interventions(aggregates[name], reader, law) for law in LAWS}
                                  for reader in READERS}
                          for name in intervention_groups},
        "unshifted_design_letter_turn_weighting": {
            "units": {f"{design}/{letter}/q{turn}": _counts(rows)
                      for (design, letter, turn), rows in sorted(unshifted.items())},
            "aggregates": {name: _unit_weighted([rows for _, rows in groups])
                           for name, groups in unit_subsets.items()},
        },
        "example_ids": _representatives(primary, exact),
    }
