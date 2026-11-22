#!/usr/bin/env python3
"""Reconstruct the sealed paired experiment with independent count and rank code."""

from collections import Counter, defaultdict
from datetime import datetime
from fractions import Fraction
from itertools import product
import argparse
import json
from pathlib import Path

from reference import (
    ARMS, HOLDING_COUNT, LAWS, acquisition_prefixes, calibrate_conditions, check_fitted_checkpoint,
    check_numeric_checkpoint, committee, counts, digest, equivalent, expected_checkpoint_digests, fit_reference,
    hash_memory, load, physical_archive, read_groups, read_jsonl, require, vote_detail,
)


VERSIONS = ("ordinary", "opposite")
BACKENDS = (*LAWS, "integer")
DESIGNS = tuple(f"{base}-blind-{i}" for base, i in product("EF", range(1, 5)))
CHECKPOINTS = ("all", "held_turns", "training_turns", "q0", "q1", "q2", "q3")


def verify_fit(producer, outputs):
    panel = producer / "panel"
    fit_dir = outputs / "fit"
    receipt_rows = read_jsonl(fit_dir / "receipts.jsonl")
    views = {arm: read_jsonl(panel / f"train_{arm}.jsonl") for arm in ARMS}
    keys = {arm: {key["id"]: key for key in read_jsonl(panel / f"training_key_{arm}.jsonl")} for arm in ARMS}
    ordered = {arm: [keys[arm][row["id"]] for row in views[arm]] for arm in ARMS}
    signals = {arm: [counts(row["pixels"]) for row in rows] for arm, rows in views.items()}
    targets = {arm: [int(key["label"] == "T") for key in ordered[arm]] for arm in ARMS}
    require(targets["narrow"] == targets["varied"], "The acquisition arms used different target order")
    starts = {law: hash_memory(physical_archive(law, bytearray(HOLDING_COUNT))) for law in LAWS}
    prefixes = {}
    fits = defaultdict(dict)
    for arm, version in product(ARMS, VERSIONS):
        schedule = [target ^ (version == "opposite") for target in targets[arm]]
        prefixes[arm, version] = list(acquisition_prefixes(signals[arm], schedule))
        fitted = fit_reference(signals[arm], schedule)
        fits[arm][version] = fitted
        for law in LAWS:
            check_fitted_checkpoint(fit_dir / f"{arm}-{law}-{version}.json", law, fitted)
        check_numeric_checkpoint(fit_dir / f"{arm}-integer-{version}.json", fitted)

    expected = []
    for index, arm in product(range(64), ARMS):
        interactions = {}
        for version in VERSIONS:
            ledger = prefixes[arm, version]
            guess, correct, current = ledger[index]
            before = starts if index == 0 else ledger[index - 1][2]
            interactions[f"{arm}-integer-{version}"] = {"guess": guess, "correct": correct}
            for law in LAWS:
                interactions[f"{arm}-{law}-{version}"] = {"guess": guess, "correct": correct,
                                                            "before_sha256": before[law], "after_sha256": current[law]}
        expected.append({"arm": arm, "slot": ordered[arm][index]["slot"], "presentation": index + 1,
                         "id": ordered[arm][index]["id"], "arms": interactions})
    require(equivalent(receipt_rows, expected), "Physical training hashes or guess and reward records disagree")
    require(len(fits["narrow"]["ordinary"]["maximal_masks_before_size_preference"]) == 240,
            "The exact matched predecessor arm did not reproduce 240 maximal groups")
    for arm in ARMS:
        original, opposite = (fits[arm][version] for version in VERSIONS)
        require(original["masks"] == opposite["masks"] and original["class_totals"] == opposite["class_totals"][::-1],
                f"{arm}: action relabeling did not transport the fitted state")
    return fits, signals, targets, ordered


def verify_intervention_words(outputs, hashes):
    explanations = {}
    prov = {
        "ordinary": ("ordinary", "ordinary"), "opposite": ("opposite", "opposite"),
        "swapped-ordinary": ("ordinary", "opposite"), "swapped-opposite": ("opposite", "ordinary"),
        "sham-ordinary": ("ordinary", "ordinary"), "restored-ordinary": ("ordinary", "ordinary"),
    }
    for arm, law in product(ARMS, LAWS):
        other = ARMS[1 - ARMS.index(arm)]
        prefix = f"{arm}-{law}-"
        for method, (recipient, source) in prov.items():
            explanations[prefix + method] = {"recipient": prefix + recipient, "source": prefix + source}
        for method, source in {
            "erase-ordinary": "recipient with neutral flags", "clear-ordinary": "neutral",
            "cross-ordinary": f"{other}-{law}-ordinary", "other-groups-ordinary": f"{other}-{law}-ordinary flags only",
        }.items():
            explanations[prefix + method] = {"recipient": prefix + "ordinary", "source": source}
    for method, info in explanations.items():
        info["sha256"] = hashes[method]
    for arm, version in product(ARMS, VERSIONS):
        name = f"{arm}-integer-{version}"
        explanations[name] = {"recipient": name, "source": name, "sha256": hash_memory(load(outputs / f"fit/{name}.json"))}
    require(equivalent(load(outputs / "blind/interventions.json"), explanations), "Intervention checkpoint state or provenance differs")
    return explanations


def verify_blind(producer, outputs, fitted):
    cases = read_jsonl(producer / "panel/queries.jsonl")
    blind = outputs / "blind"
    records = read_jsonl(blind / "predictions.jsonl")
    design = {"law": "parity", "by_arm": {a: fitted[a]["ordinary"]["masks"] for a in ARMS}}
    require(equivalent(load(blind / "group_order.json"), design), "Witness group ordering differs")
    require(len(records) == len(cases) == 1024, "Incomplete blind census")
    configurations = calibrate_conditions(fitted)
    all_features = set()
    for row, released in zip(cases, records, strict=True):
        feature = counts(row["pixels"])
        all_features.add(feature)
        details = {arm: vote_detail(feature, configurations[arm]["ordinary"]) for arm in ARMS}
        choices = {}
        for arm, conditions in configurations.items():
            issued = {condition: committee(feature, groups)[0] for condition, groups in conditions.items()}
            for law, condition in product(LAWS, conditions):
                choices[f"{arm}-{law}-{condition}"] = issued[condition]
            for version in VERSIONS:
                choices[f"{arm}-integer-{version}"] = issued[version]
        reconstructed = {"id": row["id"], "actions": choices, "details": details}
        require(equivalent(reconstructed, released), f"Blind read differs for {row['id']}")
    interventions = verify_intervention_words(outputs, expected_checkpoint_digests(fitted))
    return records, len(all_features), interventions


def original_rule_training_counts(fitted, signals, targets, keys):
    profiles = {}
    compared = sorted({*fitted["narrow"]["ordinary"]["masks"], sum(1 << i for i in (7, 11, 13, 14))})
    for mask in compared:
        selected_bins = [i for i in range(15) if mask >> i & 1]
        result = {}
        for arm in ARMS:
            counts_by_class = [Counter(), Counter()]
            witness = [dict(), dict()]
            for row, label, key in zip(signals[arm], targets[arm], keys[arm], strict=True):
                value = sum(row[i] for i in selected_bins)
                counts_by_class[label][value] += 1
                witness[label].setdefault(value, key["id"])
            moments = []
            for label, tally in enumerate(counts_by_class):
                average = Fraction(sum(value * times for value, times in tally.items()), 32)
                variance = sum((value - average) ** 2 * times for value, times in tally.items()) / 32
                moments.append({"counts": dict(tally), "mean": str(average), "variance": str(variance),
                                "first_instance_by_count": witness[label]})
            left, right = moments
            separation = (Fraction(left["mean"]) - Fraction(right["mean"])) ** 2
            spread = Fraction(left["variance"]) + Fraction(right["variance"])
            result[arm] = {"L": left, "T": right,
                           "rank": str(separation / spread) if spread else ("infinite" if separation else "excluded")}
        profiles[str(mask)] = {"bins": selected_bins, "fits": result}
    return profiles


def ambiguity(producer, fitted, signals, predictions):
    private = {row["id"]: row for row in read_jsonl(producer / "panel/scorer_key.jsonl")}
    held = sorted((row for row in predictions if private[row["id"]]["q"] in (2, 3)), key=lambda row: row["id"])
    audit = {}
    for arm in ARMS:
        model = fitted[arm]["ordinary"]
        maximal = model["maximal_masks_before_size_preference"]
        original = set(model["masks"])
        candidates = read_groups(model, maximal)
        sections = {"calibrated_training_counts": defaultdict(list), "training_votes": defaultdict(list)}
        for mask, group in zip(maximal, candidates, strict=True):
            # Complement-equivalent raw sums are reflected into the same mean order.
            values = tuple(sum(row[i] for i in group.members) for row in signals[arm])
            if group.means[0] > group.means[1]:
                values = tuple(81 - value for value in values)
            sections["calibrated_training_counts"][values].append(mask)
            votes = tuple(vote_detail(row, [group])["rule_votes"][0] for row in signals[arm])
            sections["training_votes"][votes].append(mask)
        witness = None
        for row in held:
            if not candidates:
                break
            histogram = row["details"][arm]["counts"]
            choices = vote_detail(histogram, candidates)["rule_votes"]
            groups_for_choice = defaultdict(list)
            for mask, choice in zip(maximal, choices, strict=True):
                groups_for_choice[choice].append(mask)
            if 0 in groups_for_choice and 1 in groups_for_choice:
                witness = {"bitmap_id": row["id"], "q": private[row["id"]]["q"],
                           "fitted_committee_issued": row["actions"][f"{arm}-parity-ordinary"],
                           "one_mask_voting_each_bit": [groups_for_choice[0][0], groups_for_choice[1][0]],
                           "retained_masks_among_witnesses": [x for x in (groups_for_choice[0][0], groups_for_choice[1][0]) if x in original]}
                break
        audit[arm] = {"fit_equivalence_classes": {name: list(grouping.values()) for name, grouping in sections.items()},
                      "first_held_opposing_votes_among_maxima": witness}
    return audit


def total_scores(rows):
    return {"total": len(rows), "correct": {name: sum(row["correct"][name] for row in rows)
                                            for name in rows[0]["correct"]}}


def compare(rows, before, after):
    statuses = {(False, True): "gain", (True, False): "loss", (True, True): "both_correct", (False, False): "both_incorrect"}
    tally = dict.fromkeys(statuses.values(), 0)
    witnesses = {}
    for row in rows:
        cell = statuses[row["correct"][before], row["correct"][after]]
        tally[cell] += 1
        witnesses.setdefault(cell, row["id"])
    return {"total": len(rows), **tally, "ties": tally["both_correct"] + tally["both_incorrect"], "example_ids": witnesses}


def score_by_design(units, turns):
    options = [rows for key, rows in units.items() if key[2] in turns]
    accuracy = {}
    for arm in options[0][0]["correct"]:
        rates = [Fraction(sum(row["correct"][arm] for row in rows), len(rows)) for rows in options]
        mean = sum(rates) / len(options)
        accuracy[arm] = [mean.numerator, mean.denominator]
    return {"unit_count": len(options), "translation_multiplicities": Counter(map(len, options)), "accuracy": accuracy}


def control_flags(row, arm, law):
    issued = row["actions"]
    options = {name.split("-", 2)[2]: action for name, action in issued.items() if name.startswith(f"{arm}-{law}-")}
    normal, amended = (options[version] for version in VERSIONS)
    other = ARMS[1 - ARMS.index(arm)]
    left_donor = options["swapped-ordinary"] == amended
    right_donor = options["swapped-opposite"] == normal
    return {
        "original_schedules_disagree": normal != amended, "swapped_ordinary_matches_donor": left_donor,
        "swapped_opposite_matches_donor": right_donor, "both_swaps_match_donors": left_donor and right_donor,
        "both_swaps_reverse": left_donor and right_donor and normal != amended,
        "sham_ordinary_preserves": options["sham-ordinary"] == normal,
        "restored_ordinary_preserves": options["restored-ordinary"] == normal,
        "clear_ordinary_emits_zero": options["clear-ordinary"] == 0,
        "erasure_changes_action": options["erase-ordinary"] != normal,
        "erasure_emits_zero": options["erase-ordinary"] == 0,
        "cross_arm_swap_matches_donor": options["cross-ordinary"] == issued[f"{other}-{law}-ordinary"],
        "other_groups_change_action": options["other-groups-ordinary"] != normal,
        "ordinary_twin_agrees": normal == issued[f"{arm}-integer-ordinary"],
        "opposite_twin_agrees": amended == issued[f"{arm}-integer-opposite"],
    }


def vote_flags(detail):
    tally = Counter(detail["rule_votes"])
    first, second = tally[0], tally[1]
    empty = not detail["rule_votes"]
    return {"both_actions_received_votes": bool(first and second), "at_least_one_abstention": bool(tally[None]),
            "tied_with_split_votes": first == second and first > 0, "all_rules_abstained": not empty and first == second == 0,
            "no_rules": empty, "action_zero_by_default": first == second,
            "strict_majority_zero": first > second, "strict_majority_one": second > first}


def count_flags(rows, predictor):
    tally = Counter()
    for row in rows:
        tally.update(predictor(row))
    return {"total": len(rows), **tally}


def compare_membership(rows, law):
    narrow, varied = (f"{arm}-{law}-ordinary" for arm in ARMS)
    nx, vx = (f"{arm}-{law}-other-groups-ordinary" for arm in ARMS)
    return {name: compare(rows, first, second) for name, first, second in (
        ("replace_narrow_groups_under_narrow_calibration", narrow, nx),
        ("replace_varied_groups_under_varied_calibration", varied, vx),
        ("replace_narrow_calibration_under_narrow_groups", narrow, vx),
        ("replace_varied_calibration_under_varied_groups", varied, nx),
    )}


def verify_scores(producer, outputs, predictions):
    scorer_rows = read_jsonl(producer / "panel/scorer_key.jsonl")
    indices = {row["id"]: row for row in scorer_rows}
    require(len(indices) == len(scorer_rows) == len(predictions) == 1024, "Score key has wrong coverage")
    cells = defaultdict(list)
    buckets = defaultdict(list)
    units = defaultdict(list)
    for receipt in sorted(predictions, key=lambda row: row["id"]):
        metadata = indices[receipt["id"]]
        style, letter, angle, condition = (metadata[name] for name in ("style", "label", "q", "condition"))
        position = "new" if condition in ("position", "combined") else "familiar"
        q = f"q{angle}"
        expected = int(letter == "T")
        score = {arm: bit == (expected ^ arm.endswith("-opposite")) for arm, bit in receipt["actions"].items()}
        case = {"id": receipt["id"], "correct": score, "actions": receipt["actions"], "details": receipt["details"]}
        cells[f"{style}/{letter}/{q}/{position}"].append(case)
        units[style, letter, angle].append(case)
        for key in ("all", "held_turns" if angle >= 2 else "training_turns", q, f"letter/{letter}", f"position/{position}",
                    f"design/{style}", f"condition/{condition}", f"{q}/{position}", f"{q}/{letter}", f"{q}/{position}/{letter}"):
            buckets[key].append(case)

    def paired(all_rows):
        return {key: {backend: compare(rows, f"narrow-{backend}-ordinary", f"varied-{backend}-ordinary")
                      for backend in BACKENDS} for key, rows in all_rows.items()}

    primary = [f"{style}/{letter}/q{angle}/{position}" for style, letter, angle, position in
               product(DESIGNS, "LT", (2, 3), ("familiar", "new"))]
    require(len(cells) == 128 and set(map(len, cells.values())) == {8}, "Primary and diagnostic panels not balanced")
    totals_by_cell = {name: total_scores(group) for name, group in cells.items()}
    gates = defaultdict(dict)
    examples = {}
    for arm, law in product(ARMS, LAWS):
        target = f"{arm}-{law}-ordinary"
        fail = [name for name in primary if totals_by_cell[name]["correct"][target] <= 4]
        gates[arm][law] = {"passed": not fail, "cell_count": len(primary), "failed_cells": fail}
        for name in primary:
            for row in cells[name]:
                status = "correct" if row["correct"][target] else "incorrect"
                examples.setdefault(f"{name}/{target}/{status}", row["id"])

    aggregates = {name: total_scores(rows) for name, rows in buckets.items()}
    comparison = {}
    for law in LAWS:
        raw = aggregates["held_turns"]
        narrow, varied = (raw["correct"][f"{arm}-{law}-ordinary"] for arm in ARMS)
        narrow_pass, varied_pass = (gates[arm][law]["passed"] for arm in ARMS)
        comparison[law] = {"passed": varied_pass and not narrow_pass and varied > narrow,
                           "varied_passed": varied_pass, "narrow_passed": narrow_pass,
                           "held_total": raw["total"], "held_correct_narrow": narrow, "held_correct_varied": varied,
                           "held_correct_difference": varied - narrow}
    summaries = {"cells": totals_by_cell, "aggregates": aggregates, "primary_gate": gates, "attribution_gate": comparison,
        "both_laws_pass_attribution": all(detail["passed"] for detail in comparison.values()),
        "paired": {"cells": paired(cells), "aggregates": paired(buckets)},
        "membership_calibration_crosses": {name: {law: compare_membership(buckets[name], law) for law in LAWS}
                                            for name in CHECKPOINTS},
        "interventions": {name: {arm: {law: count_flags(buckets[name], lambda row: control_flags(row, arm, law))
                                         for law in LAWS} for arm in ARMS} for name in CHECKPOINTS},
        "committee": {name: {arm: count_flags(rows, lambda row: vote_flags(row["details"][arm])) for arm in ARMS}
                      for name, rows in buckets.items()},
        "design_turn_letter_weighting": {
            "cells": {f"{style}/{letter}/q{angle}": total_scores(rows) for (style, letter, angle), rows in units.items()},
            "all": score_by_design(units, range(4)), "held_turns": score_by_design(units, (2, 3)),
        },
        "example_ids": examples,
    }
    require(equivalent(load(outputs / "scored/scores.json"), summaries), "Independent scoring and production scores differ")

    representatives = []
    for (_, _, angle), translated in units.items():
        require(len({tuple(row["actions"].values()) for row in translated}) == 1, "Supplied translation sharing diverged")
        if angle in (2, 3):
            representatives.append(translated[0])
    summaries["held_turn_pairs_by_design_letter_turn"] = {
        backend: compare(representatives, f"narrow-{backend}-ordinary", f"varied-{backend}-ordinary") for backend in BACKENDS}
    return summaries


def validate_endpoint_diagnostics(outputs, fits):
    diagnostics = {}
    for arm, version in product(ARMS, VERSIONS):
        fitted = fits[arm][version]
        masks, sizes, sums = (fitted[name] for name in ("masks", "class_counts", "class_totals"))
        score = fitted["score"]
        calibration = {"masks": masks, "class_counts": sizes, "class_totals": sums,
                       "smaller_side_cardinality": fitted["size"], "partitions_scored": 32767,
                       "rank_numerator": score[0], "rank_denominator": score[1]}
        for law in LAWS:
            diagnostics[f"{arm}-{law}-{version}"] = calibration
        diagnostics[f"{arm}-integer-{version}"] = load(outputs / f"fit/{arm}-integer-{version}.json")
    require(equivalent(load(outputs / "fit/diagnostics.json"), diagnostics), "Calibrated rank diagnostics differ")


def verify_release_chain(producer, outputs, anchor_path, scored_sha):
    anchors = {row["stage"]: row for row in read_jsonl(anchor_path)}
    require(set(anchors) == {"fit", "blind"}, "Wrong external anchor roster")
    anchors["scored"] = {"sha256": scored_sha}
    root = producer.parents[2]
    authorization = root / "research" / producer.parent.name / "audit/R1/red_team_report.json"
    expected_parents = {
        "fit": {"run_authorization": authorization,
                **{f"{phase}_{arm}": producer / "panel" / f"{phase}_{arm}.jsonl"
                   for arm, phase in product(ARMS, ("train", "training_key"))}},
        "blind": {"fitted_state_release": outputs / "fit/release.json", "queries": producer / "panel/queries.jsonl"},
        "scored": {"blind_release": outputs / "blind/release.json", "scorer_key": producer / "panel/scorer_key.jsonl"},
    }
    expected_outputs = {
        "fit": {"diagnostics.json", "receipts.jsonl", *(f"{arm}-{backend}-{version}.json"
                  for arm, backend, version in product(ARMS, BACKENDS, VERSIONS))},
        "blind": {"interventions.json", "predictions.jsonl", "group_order.json"}, "scored": {"scores.json"},
    }
    releases = {}
    contract = digest((producer / "contract.json").read_bytes())
    for phase, parent_paths in expected_parents.items():
        folder = outputs / phase
        release_path = folder / "release.json"
        require(digest(release_path.read_bytes()) == anchors[phase]["sha256"], f"Wrong externally anchored {phase} release")
        stage = load(release_path)
        require(stage["contract"] == contract, f"Replaced contract at {phase}")
        require(stage["parents"] == {name: digest(path.read_bytes()) for name, path in parent_paths.items()},
                f"{phase} has wrong released parents")
        require(stage["files"] == {name: digest((folder / name).read_bytes()) for name in expected_outputs[phase]},
                f"Wrong output bindings in {phase}")
        require(set(p.name for p in folder.iterdir()) == expected_outputs[phase] | {"release.json"}, f"Unexpected output in {phase}")
        require(stage["seconds"] >= 0 and stage["max_rss_kib"] > 0, f"No resources recorded in {phase}")
        releases[phase] = stage
    for prior, later in (("fit", "blind"), ("blind", "scored")):
        times = (releases[prior]["utc"], anchors[prior]["utc"], releases[later]["utc"])
        begin, anchor, end = map(datetime.fromisoformat, times)
        require(begin < anchor < end and anchors[prior]["next_stage_absent"] == later, f"Late external anchor at {prior}")
    require(datetime.fromisoformat(load(authorization)["audit_utc"]) < datetime.fromisoformat(releases["fit"]["utc"]),
            "Run authorization postdates fit")
    expected_counts = {
        "fit": {"presentations_per_arm": 64, "training_arms": 2, "readers": 12, "updates": 768, "epochs": 1,
                "matched_receipt_prefixes": True},
        "blind": {"images": 1024, "issued_readers": 44, "feedback_events": 0},
        "scored": {"images": 1024, "issued_readers": 44},
    }
    require(all(releases[phase]["observations"] == observed for phase, observed in expected_counts.items()),
            "Released stage accounting differs from frozen budgets")
    return releases, anchors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("producer", type=Path)
    parser.add_argument("outputs", type=Path)
    parser.add_argument("--anchors", type=Path, required=True)
    parser.add_argument("--scored-sha", required=True)
    args = parser.parse_args()
    releases, anchors = verify_release_chain(args.producer, args.outputs, args.anchors, args.scored_sha)
    fitted, training_counts, targets, keys = verify_fit(args.producer, args.outputs)
    validate_endpoint_diagnostics(args.outputs, fitted)
    decisions, signatures, interventions = verify_blind(args.producer, args.outputs, fitted)
    scored = verify_scores(args.producer, args.outputs, decisions)
    scored["fit_reference"] = fitted
    scored["predecessor_learned_groups"] = original_rule_training_counts(fitted, training_counts, targets, keys)
    scored["fit_equivalence_and_first_held_ambiguity"] = ambiguity(args.producer, fitted, training_counts, decisions)
    scored["fit_overlap"] = {
        name: sorted(set(fitted["narrow"]["ordinary"][name]).intersection(fitted["varied"]["ordinary"][name]))
        for name in ("masks", "maximal_masks_before_size_preference", "quarter_turn_closed_maximal_masks")}
    scored["adaptive_intervention_words"] = interventions
    scored["exact_replay"] = {"pre_transition_anchors_match": True, "anchors": anchors, "training_fit_updates": 768,
        "train_physical_before_after_hashes": 1024, "separate_fitted_readers": 12,
        "blind_queries": len(decisions), "distinct_query_signatures": signatures, "blind_actions": 1024 * 44}
    scored["resources"] = {phase: {field: item[field] for field in ("seconds", "max_rss_kib", "observations")}
                           for phase, item in releases.items()}
    print(json.dumps(scored, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
