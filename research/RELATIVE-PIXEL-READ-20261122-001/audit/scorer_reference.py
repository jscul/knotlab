"""Separate exact score and intervention aggregation for the fresh panel."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product

from fitted_reader import LAWS, READERS, require


BACKENDS = (*LAWS, "integer")
STYLES = tuple(f"{base}-relative-{i}" for base, i in product("EF", range(1, 5)))


def measurements(rows):
    count = {letter: sum(row["letter"] == letter for row in rows) for letter in "LT"}
    return {"total": len(rows), "true_letters": count, "always_zero_ordinary_correct": count["L"],
            "correct": {action: sum(row["correct"][action] for row in rows) for action in rows[0]["correct"]}}


def tally_pairs(rows, left, right):
    names = {(False, False): "both_incorrect", (False, True): "gains", (True, False): "losses", (True, True): "both_correct"}
    score = {name: 0 for name in names.values()}
    first = {}
    for row in rows:
        status = names[row["correct"][left], row["correct"][right]]
        score[status] += 1
        first.setdefault(status, row["id"])
    return {"total": len(rows), **score, "ties": score["both_correct"] + score["both_incorrect"], "example_ids": first}


def compare_all(rows):
    return {f"position_vs_{other}": {backend: tally_pairs(rows, f"{other}-{backend}-ordinary", f"position-{backend}-ordinary")
                 for backend in BACKENDS} for other in ("window_tree", "window_group")}


def state_controls(row, reader, law):
    all_actions = row["actions"]
    prefix = f"{reader}-{law}-"
    options = {key[len(prefix):]: value for key, value in all_actions.items() if key.startswith(prefix)}
    first, second = options["ordinary"], options["opposite"]
    response = (options["swapped-ordinary"], options["swapped-opposite"])
    left, right = response[0] == second, response[1] == first
    twins = (first == all_actions[f"{reader}-integer-ordinary"], second == all_actions[f"{reader}-integer-opposite"])
    return {
        "originals_disagree": first != second, "ordinary_swap_follows_opposite_donor": left,
        "opposite_swap_follows_ordinary_donor": right, "both_swaps_follow_donors": left and right,
        "both_swaps_reverse": left and right and first != second,
        "sham_preserves_ordinary": options["sham"] == first, "blank_memory_emits_zero": options["clear"] == 0,
        "clearing_changes_ordinary": options["clear"] != first, "restore_recovers_ordinary": options["restored"] == first,
        "ordinary_twin_agrees": twins[0], "opposite_twin_agrees": twins[1], "both_twins_agree": all(twins),
    }


def interventions(rows, reader, law):
    scores, witnesses = Counter(), defaultdict(dict)
    for row in rows:
        outcomes = state_controls(row, reader, law)
        scores.update(outcomes)
        for event, ok in outcomes.items():
            witnesses[event].setdefault("yes" if ok else "no", row["id"])
    return {"total": len(rows), **scores, "example_ids": witnesses}


def check_gate(scores, requirements):
    gates = defaultdict(dict)
    for reader, law in product(READERS, LAWS):
        key = f"{reader}-{law}-ordinary"
        miss_at = [name for name in requirements if 2 * scores[name]["correct"][key] <= scores[name]["total"]]
        gates[reader][law] = {"passed": not miss_at, "cell_count": len(requirements), "failed_cells": miss_at}
    return gates


def unit_rates(groups):
    group_count = len(groups)
    partition = {}
    for action in groups[0][0]["correct"]:
        correct = sum(Fraction(sum(row["correct"][action] for row in group), len(group)) for group in groups)
        equal_bits = sum(len({row["actions"][action] for row in group}) == 1 for group in groups)
        rate = correct / group_count
        partition[action] = {"effective_correct_units": [correct.numerator, correct.denominator],
                             "accuracy": [rate.numerator, rate.denominator], "uniform_decision_units": equal_bits,
                             "correct_uniform_units": correct.numerator if equal_bits == group_count else None}
    return {"total_units": group_count, "total_translations": sum(map(len, groups)),
            "translations_per_unit": Counter(str(len(rows)) for rows in groups), "actions": partition}


def paired_units(units):
    result = {}
    for comparator in ("window_tree", "window_group"):
        backends = {}
        for backend in BACKENDS:
            tally = dict.fromkeys(("gains", "losses", "both_correct", "both_incorrect", "tied_mixed"), 0)
            consistent = 0
            witnesses = {}
            for (design, letter, q), group in units:
                left = sum(row["correct"][f"{comparator}-{backend}-ordinary"] for row in group)
                right = sum(row["correct"][f"position-{backend}-ordinary"] for row in group)
                if left == right:
                    outcome = "both_incorrect" if left == 0 else "both_correct" if left == len(group) else "tied_mixed"
                else:
                    outcome = "gains" if right > left else "losses"
                consistent += left in (0, len(group)) and right in (0, len(group))
                tally[outcome] += 1
                witnesses.setdefault(outcome, f"{design}/{letter}/q{q}")
            backends[backend] = {"total_units": len(units), "translation_consistent_units": consistent, **tally,
                                 "ties": len(units) - tally["gains"] - tally["losses"], "example_units": witnesses}
        result[f"position_vs_{comparator}"] = backends
    return result


def score(predictions, metadata):
    keys = {row["id"]: row for row in metadata}
    require(len(keys) == len(metadata) == len(predictions) == 1024, "Incomplete scorer key")
    cells, summary, units = defaultdict(list), defaultdict(list), defaultdict(list)
    for blind in sorted(predictions, key=lambda row: row["id"]):
        known = keys[blind["id"]]
        style, letter, q, condition = (known[name] for name in ("style", "label", "q", "condition"))
        position = "new" if condition in ("position", "combined") else "familiar"
        split = "held_turns" if q >= 2 else "training_turns"
        actions = blind["actions"]
        truth = int(letter == "T")
        row = {"id": blind["id"], "letter": letter, "position": position, "actions": actions,
               "correct": {name: choice == (truth ^ name.endswith("-opposite")) for name, choice in actions.items()}}
        cells[f"{style}/{letter}/q{q}/{position}"].append(row)
        units[style, letter, q].append(row)
        for name in ("all", split, f"q{q}", f"q{q}/{letter}", f"q{q}/{position}", f"q{q}/{letter}/{position}",
                     f"{split}/{letter}", f"{split}/{position}", f"letter/{letter}", f"position/{position}",
                     f"design/{style}", f"condition/{condition}"):
            summary[name].append(row)
    require(len(cells) == 128 and {len(rows) for rows in cells.values()} == {8}, "Wrong score-cell coverage")

    primary = [f"{style}/{letter}/q{turn}/{position}" for style, letter, turn, position in
               product(STYLES, "LT", (2, 3), ("familiar", "new"))]
    pooled = [f"q{turn}/{letter}" for turn, letter in product((2, 3), "LT")]
    cell_counts = {name: measurements(rows) for name, rows in cells.items()}
    aggregates = {name: measurements(rows) for name, rows in summary.items()}
    samples = {}
    for cell in primary:
        for row in cells[cell]:
            for reader, law in product(READERS, LAWS):
                name = f"{reader}-{law}-ordinary"
                outcome = "correct" if row["correct"][name] else "incorrect"
                samples.setdefault(f"{cell}/{name}/{outcome}", row["id"])

    case_groups = defaultdict(list)
    for key, rows in sorted(units.items()):
        _, letter, turn = key
        for name in ("all", f"q{turn}", f"q{turn}/{letter}"):
            case_groups[name].append((key, rows))
        if turn >= 2:
            case_groups["held_turns"].append((key, rows))
        for position in ("familiar", "new"):
            group = [row for row in rows if row["position"] == position]
            case_groups[f"q{turn}/{letter}/{position}"].append((key, group))
            if turn >= 2:
                case_groups[f"held_turns/{position}"].append((key, group))
    flag_groups = ("all", "held_turns", "training_turns", "q0", "q1", "q2", "q3", "held_turns/familiar", "held_turns/new")
    output = {
        "cells": cell_counts, "aggregates": aggregates, "primary_gate": check_gate(cell_counts, primary),
        "descriptive_pooled_held_letter_turn_gate": check_gate(aggregates, pooled),
        "paired": {"cells": {name: compare_all(rows) for name, rows in cells.items()},
                   "aggregates": {name: compare_all(rows) for name, rows in summary.items()},
                   "unshifted_unit_aggregates": {name: paired_units(rows) for name, rows in case_groups.items()}},
        "interventions": {name: {reader: {law: interventions(summary[name], reader, law) for law in LAWS} for reader in READERS}
                          for name in flag_groups},
        "unshifted_design_letter_turn_weighting": {
            "units": {f"{style}/{letter}/q{q}": measurements(rows) for (style, letter, q), rows in units.items()},
            "aggregates": {name: unit_rates([rows for _, rows in groups]) for name, groups in case_groups.items()},
        },
        "example_ids": samples,
    }
    held_representatives = []
    for _, group in case_groups["held_turns"]:
        require(len({tuple(sorted(row["actions"].items())) for row in group}) == 1, "Translation changed a fitted action")
        held_representatives.append(group[0])
    extras = {"held_pairs_by_drawing_letter_turn": compare_all(held_representatives)}
    return output, extras
