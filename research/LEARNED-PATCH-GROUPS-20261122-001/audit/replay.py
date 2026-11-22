#!/usr/bin/env python3
"""Independently reproduce frozen learned-group receipts, state and outcomes."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path

from group_oracle import Group, committee, group_roster, mask_from_partition, selected_groups
from panel_census import digest, enumerate_panel, equivalent, expected_files, loads, read_jsonl, require
from pixel_counts import FIXED_CODING, TURN_BIN, counts


LAWS = ("parity", "nae")
SCHEDULES = ("ordinary", "opposite", "shifted")
PARTITIONS = 32767
RECEIPT_SIZE = 114
STATS_START = 1 + 64 * RECEIPT_SIZE
FLAG_START = STATS_START + 14 + 416
HOLDING_COUNT = FLAG_START + PARTITIONS
PHYSICAL_CODES = {"parity": (6, 3), "nae": (6, 1)}


def load(path):
    return loads(path.read_bytes())


def hash_memory(obj):
    return digest(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii"))


def write_value(holdings, address, width, value):
    require(0 <= value < 2 ** width, "Value cannot fit registered holdings")
    holdings[address:address + width] = [(value // 2 ** i) % 2 for i in range(width)]


def read_value(holdings, address, width):
    return sum(value * 2 ** i for i, value in enumerate(holdings[address:address + width]))


def physical_archive(law, binary):
    translation = bytes.maketrans(b"\x00\x01", bytes(PHYSICAL_CODES[law]))
    return {"schema": "pixel-knot-partitions-v1", "law": law, "training_limit": 64,
            "words": bytes(binary).translate(translation).hex()}


def check_physical(archive, law, selected, class_sizes, totals):
    require(set(archive) == {"law", "schema", "training_limit", "words"}, "Adaptive conventional data in physical export")
    require((archive["schema"], archive["law"], archive["training_limit"]) == ("pixel-knot-partitions-v1", law, 64),
            "Unexpected physical header")
    prepared = bytes.fromhex(archive["words"])
    require(len(prepared) == HOLDING_COUNT and set(prepared) <= set(PHYSICAL_CODES[law]), "Wrong physical holding roster")
    _, one = PHYSICAL_CODES[law]
    binary = tuple(code == one for code in prepared)
    require(binary[0] and not any(binary[1:STATS_START]), "Deployment retained acquisition words")
    actual_sizes = [read_value(binary, STATS_START + action * 7, 7) for action in range(2)]
    actual_totals = [[read_value(binary, STATS_START + 14 + (16 * action + i) * 13, 13) for i in range(16)]
                     for action in range(2)]
    actual_masks = [index for index, present in enumerate(binary[FLAG_START:], start=1) if present]
    require((actual_sizes, actual_totals, actual_masks) == (class_sizes, totals, selected),
            "Independent decode of class calibration or membership differs")


def previous_archive(law, previous):
    physical = tuple(f"{value:03b}" for value in PHYSICAL_CODES[law])
    return {"schema": "pixel-knot-histograms-v1", "law": law, "training_limit": 64,
            "words": [["".join(physical[int(bit)] for bit in f"{value:013b}"[::-1]) for value in row] for row in previous]}


def centroid(histogram, totals):
    distance = {}
    for action, bank in enumerate(totals):
        n = sum(bank) // 81
        if n:
            distance[action] = sum((value - Fraction(total, n)) ** 2 for value, total in zip(histogram, bank, strict=True))
    return min(distance, key=lambda action: (distance[action], action)) if distance else 0


def verify_releases(artifacts, producer, anchors):
    root = producer.parents[2]
    gate = root / "research" / producer.parent.name / "audit/R1/red_team_report.json"
    inputs = {
        "fit": {"run_authorization": gate, "image_stream": producer / "panel/train.jsonl",
                "training_rewards": producer / "panel/training_key.jsonl"},
        "blind": {"fitted_state_release": artifacts / "fit/release.json", "queries": producer / "panel/queries.jsonl"},
        "scored": {"blind_release": artifacts / "blind/release.json", "scorer_key": producer / "panel/scorer_key.jsonl"},
    }
    outputs = {
        "fit": {"diagnostics.json", "receipts.jsonl", *(f"previous-{law}.json" for law in LAWS),
                *(f"{kind}-{schedule}.json" for kind, schedule in product((*LAWS, "integer"), SCHEDULES))},
        "blind": {"predictions.jsonl", "rule_votes.json"}, "scored": {"scores.json"},
    }
    receipts = {}
    for phase, parent_files in inputs.items():
        folder = artifacts / phase
        lock = folder / "release.json"
        require(digest(lock.read_bytes()) == anchors[phase]["sha256"], f"{phase}: different externally anchored release")
        receipt = load(lock)
        require(receipt["contract"] == digest((producer / "contract.json").read_bytes()), f"{phase}: contract replaced")
        wanted_parents = {name: digest(path.read_bytes()) for name, path in parent_files.items()}
        require(receipt["parents"] == wanted_parents, f"{phase}: incorrect parent release or input")
        wanted_outputs = {name: digest((folder / name).read_bytes()) for name in outputs[phase]}
        require(receipt["files"] == wanted_outputs, f"{phase}: corrupt outputs or incomplete output roster")
        require(set(path.name for path in folder.iterdir()) == outputs[phase] | {"release.json"}, f"{phase}: side output")
        require(receipt["max_rss_kib"] > 0 and receipt["seconds"] >= 0, f"{phase}: incomplete resource record")
        receipts[phase] = receipt
    edges = (("fit", "blind"), ("blind", "scored"))
    for before, after in edges:
        close, checkpoint, next_close = map(datetime.fromisoformat,
            (receipts[before]["utc"], anchors[before]["utc"], receipts[after]["utc"]))
        require(close < checkpoint < next_close and anchors[before]["next_stage_absent"] == after,
                f"{before}: external anchor does not precede {after}")
    require(datetime.fromisoformat(load(gate)["audit_utc"]) < datetime.fromisoformat(receipts["fit"]["utc"]), "R1 postdates fit")
    require(receipts["fit"]["observations"] == {"presentations": 64, "arms": 11, "epochs": 1}, "Incorrect fit budget")
    return receipts


def calibrate(groups, label_counts, totals):
    for group in groups:
        means = tuple(Fraction(sum(totals[action][i] for i in group), label_counts[action]) for action in range(2))
        yield Group(group, means, (0, 1))


def verify_fit(artifacts, training, panel):
    fit = artifacts / "fit"
    receipts = read_jsonl(fit / "receipts.jsonl")
    require(len(receipts) == len(training) == 64, "Training stream not complete")
    literal = [int(panel[row["id"]]["label"] == "T") for row in training]
    targets = {"ordinary": literal, "opposite": [1 - action for action in literal], "shifted": literal[17:] + literal[:17]}
    physical_states = {v: bytearray(HOLDING_COUNT) for v in SCHEDULES}
    label_counts = {v: [0, 0] for v in SCHEDULES}
    class_histograms = {v: [Counter(), Counter()] for v in SCHEDULES}
    records = {v: [] for v in SCHEDULES}
    count_rows = []
    previous = [[0] * 16, [0] * 16]
    for index, (row, receipt) in enumerate(zip(training, receipts, strict=True)):
        signal = counts(row["pixels"])
        count_rows.append(signal)
        actions = {}
        for version in SCHEDULES:
            cohort = label_counts[version]
            guess = int(cohort[1] > cohort[0])
            correct = guess == targets[version][index]
            learned = guess if correct else 1 - guess
            records[version].append(learned)
            cohort[learned] += 1
            class_histograms[version][learned][signal] += 1
            binary = physical_states[version]
            start = 1 + index * RECEIPT_SIZE
            write_value(binary, start, 2, 1 + 2 * learned)
            for i, tally in enumerate(signal):
                write_value(binary, start + 2 + 7 * i, 7, tally)
            actions["integer-" + version] = {"guess": guess, "correct": correct}
            for law in LAWS:
                actions[f"{law}-{version}"] = {"guess": guess, "correct": correct,
                    "after_sha256": hash_memory(physical_archive(law, binary))}

        guess = centroid(signal, previous)
        correct = guess == literal[index]
        learned = guess if correct else 1 - guess
        previous[learned] = [value + tally for value, tally in zip(previous[learned], signal, strict=True)]
        for law in LAWS:
            actions[f"previous-{law}"] = {"guess": guess, "correct": correct,
                "after_sha256": hash_memory(previous_archive(law, previous))}
        expected = {"id": row["id"], "presentation": index + 1, "arms": actions}
        require(equivalent(receipt, expected), f"Training receipt differs at {index + 1}")

    chosen = {}
    calibrated = {}
    diagnostics = {}
    for version in SCHEDULES:
        cohort = label_counts[version]
        totals = [[sum(number * row[i] for row, number in class_histograms[version][action].items()) for i in range(16)]
                  for action in range(2)]
        ranked = selected_groups(list(group_roster(count_rows, records[version])))
        members = sorted(mask_from_partition(group.members) for group in ranked)
        frozen = [tuple(i for i in range(15) if mask & (1 << i)) for mask in members]
        chosen[version] = list(calibrate(frozen, cohort, totals))
        size = len(ranked[0].members) if ranked else None
        calibrated[version] = (totals, cohort, size)
        score = (Fraction(*ranked[0].score) if ranked and ranked[0].score[1] else None)
        score_pair = [score.numerator, score.denominator] if score is not None else ([1, 0] if ranked else [0, 1])
        numeric = {"class_totals": cohort, "class_bin_totals": totals, "masks": members,
                   "score": score_pair if ranked else None, "smaller_side_size": size}
        diagnostics[f"integer-{version}"] = numeric
        require(equivalent(load(fit / f"integer-{version}.json"), numeric), "Conventional checkpoint differs")
        for law in LAWS:
            check_physical(load(fit / f"{law}-{version}.json"), law, members, cohort, totals)
            diagnostics[f"{law}-{version}"] = {"masks": members, "smaller_side_cardinality": size,
                "class_counts": cohort, "class_totals": totals, "rank_numerator": score_pair[0],
                "rank_denominator": score_pair[1], "partitions_scored": PARTITIONS}

    diagnostics["shift_control"] = {
        "labels_changed": sum(a != b for a, b in zip(literal, targets["shifted"], strict=True)),
        "class_histogram_multisets_changed": [a != b for a, b in zip(class_histograms["ordinary"], class_histograms["shifted"], strict=True)],
        "distinct_train_histograms": len(set(count_rows)),
    }
    require(equivalent(load(fit / "diagnostics.json"), diagnostics), "Fitting diagnostics differ")
    for law in LAWS:
        require(equivalent(load(fit / f"previous-{law}.json"), previous_archive(law, previous)), "Previous learner checkpoint differs")
    return chosen, calibrated, previous, count_rows, records, diagnostics


def every_at_size(size):
    if size is None:
        return ()
    return (indices for indices in combinations(range(16), size) if size != 8 or 15 not in indices)


def vote_detail(histogram, groups):
    outcomes = []
    for group in groups:
        gap = abs(sum(histogram[i] for i in group.members) - group.means[0]) - abs(
            sum(histogram[i] for i in group.members) - group.means[1])
        outcomes.append(int(gap > 0) if gap else None)
    return {"phase": "deployment", "counts": list(histogram),
            "guess": int(outcomes.count(1) > outcomes.count(0)),
            "votes": [outcomes.count(0), outcomes.count(1)], "abstentions": outcomes.count(None),
            "rule_votes": outcomes}


def verify_blind(artifacts, queries, chosen, calibrated, previous, release):
    checked_rows = read_jsonl(artifacts / "blind/predictions.jsonl")
    require(len(checked_rows) == len(queries) == 704, "Blind bitmap roster incomplete")
    bankers, class_sizes, size = calibrated["ordinary"]
    all_size = list(calibrate(every_at_size(size), class_sizes, bankers))
    first_at_signature = {}
    score_by_signature = {}
    reconstructed = []
    for index, (raw, observed) in enumerate(zip(queries, checked_rows, strict=True)):
        signal = counts(raw["pixels"])
        if signal not in first_at_signature:
            features = {version: vote_detail(signal, chosen[version]) for version in SCHEDULES}
            prior = centroid(signal, previous)
            full_guess, _ = committee(signal, all_size)
            first_at_signature[signal] = str(index)
            score_by_signature[signal] = (features, prior, full_guess)
        features, prior, full_guess = score_by_signature[signal]
        actions = {"integer-" + version: data["guess"] for version, data in features.items()}
        for law in LAWS:
            for version, donor in (("ordinary", "opposite"), ("opposite", "ordinary")):
                own = features[version]["guess"]
                for name in ("", "sham-", "restored-"):
                    actions[f"{law}-{name}{version}"] = own
                actions[f"{law}-swapped-{version}"] = features[donor]["guess"]
                actions[f"{law}-clear-{version}"] = 0
            actions[f"{law}-shifted"] = features["shifted"]["guess"]
            actions[f"{law}-erase-ordinary"] = 0
            actions[f"{law}-allsize-ordinary"] = full_guess
            actions[f"previous-{law}"] = prior
        ordinary = features["ordinary"]
        record = {"id": raw["id"], "actions": actions, **{name: ordinary[name] for name in ("counts", "votes", "abstentions")}}
        require(equivalent(observed, record), f"Blind ledger differs: query {index}")
        reconstructed.append(record)

    details = {first_at_signature[signal]: features["ordinary"] for signal, (features, _, _) in score_by_signature.items()}
    literal = {"mask_order": [mask_from_partition(group.members) for group in chosen["ordinary"]], "by_first_index": details}
    require(equivalent(load(artifacts / "blind/rule_votes.json"), literal), "Per-rule votes differ")
    require(release["observations"] == {"images": len(queries), "arms": 31,
                                       "distinct_signatures": len(score_by_signature), "feedback_events": 0}, "Blind budget differs")
    return reconstructed, score_by_signature, len(all_size)


def verify_scores(artifacts, predictions, fixtures, training_signals, targets, release):
    train_classes = defaultdict(set)
    for signal, target in zip(training_signals, targets["ordinary"], strict=True):
        train_classes[signal].add("LT"[target])
    cells = defaultdict(lambda: {"total": 0, "correct": Counter()})
    novelty = defaultdict(Counter)
    committees = defaultdict(Counter)
    causal = defaultdict(Counter)
    representatives = {}
    for observed in sorted(predictions, key=lambda row: row["id"]):
        sample = fixtures[observed["id"]]
        actions = observed["actions"]
        letter = sample["label"]
        truth = int(letter == "T")
        turn = f"q{sample['q']}"
        stratum, condition = sample["style_stratum"], sample["condition"]
        cell = f"{stratum}/{condition}"
        key = f"{cell}/{turn}/{letter}"
        by_style = f"{stratum}/{sample['style']}/{condition}/{turn}/{letter}"
        locations = (key, f"{cell}/all/{letter}", f"{cell}/all/all", f"{cell}/{turn}/all", by_style)
        correct = {arm: int(decision == truth ^ arm.endswith("-opposite")) for arm, decision in actions.items()}
        for location in locations:
            cells[location]["total"] += 1
            cells[location]["correct"].update(correct)

        found = train_classes.get(tuple(observed["counts"]), set())
        overlap = "new" if not found else ("same_label" if found == {letter} else "different_or_mixed")
        novelty[cell][overlap] += 1
        votes = observed["votes"]
        committees[f"{cell}/{turn}"].update({"total": 1, "both_actions_received_votes": int(all(votes)),
                "at_least_one_abstention": int(observed["abstentions"] > 0), "final_tie": int(votes[0] == votes[1])})

        for law in LAWS:
            choice = {arm[len(law) + 1:]: guess for arm, guess in actions.items() if arm.startswith(law + "-")}
            ordinary, opposite = (choice[version] for version in SCHEDULES[:2])
            donor_match = choice["swapped-ordinary"] == opposite and choice["swapped-opposite"] == ordinary
            counts_here = {
                "total": 1, "originals_disagree": int(ordinary != opposite), "both_donors_match": int(donor_match),
                "both_reverse": int(donor_match and ordinary != opposite),
                "both_shams_preserve": int(all(choice[f"sham-{v}"] == choice[v] for v in SCHEDULES[:2])),
                "both_restored": int(all(choice[f"restored-{v}"] == choice[v] for v in SCHEDULES[:2])),
                "both_clear_to_zero": int(all(choice[f"clear-{v}"] == 0 for v in SCHEDULES[:2])),
                "erase_selection_changes": int(choice["erase-ordinary"] != ordinary),
                "all_size_agrees": int(choice["allsize-ordinary"] == ordinary),
                "ordinary_twin_matches_all_schedules": int(all(choice[v] == actions[f"integer-{v}"] for v in SCHEDULES)),
            }
            for location in ("all", stratum, f"{cell}/{turn}"):
                causal[f"{law}/{location}"].update(counts_here)

        category = f"{key}/{'correct' if correct['parity-ordinary'] else 'error'}"
        if category not in representatives:
            metadata = {name: value for name, value in sample.items() if name != "pixels"}
            bitmap = [sample["pixels"][i:i + 8] for i in range(0, 64, 8)]
            representatives[category] = {**metadata, "bitmap": bitmap, "guess": "LT"[actions["parity-ordinary"]],
                "previous": "LT"[actions["previous-parity"]], "donor_guess_in_ordinary_reader": "LT"[actions["parity-swapped-ordinary"]],
                "cleared_guess": "LT"[actions["parity-clear-ordinary"]], "votes": votes,
                "abstentions": observed["abstentions"], "counts": observed["counts"]}
    gate = {}
    primary = [f"blind/{style}/{cell}/q{turn}/{letter}" for style, cell, turn, letter in
               product("EF", ("orientation", "combined"), (2, 3), "LT")]
    require(all(cells[key]["total"] == 8 for key in primary), "Wrong primary subgroup census")
    for law in LAWS:
        failures = [key for key in primary if cells[key]["correct"][f"{law}-ordinary"] <= 4]
        gate[law] = {"passed": not failures, "cell_count": 16, "failed_cells": failures}
    result = {"cells": cells, "primary_gate": gate, "causal": causal, "novelty": novelty,
              "committee": committees, "representatives": representatives}
    require(equivalent(load(artifacts / "scored/scores.json"), result), "Independent scores differ")
    require(release["observations"] == {"images": 704, "primary_gate": gate}, "Scorer release summary differs")
    return result


def covariance_and_rotation(chosen, signals, targets, cases):
    def recoded(histogram):
        return tuple(histogram[i] for i in FIXED_CODING)

    fit_recoded = [recoded(row) for row in signals]
    result = {}
    for version, original in chosen.items():
        shifted = selected_groups(list(group_roster(fit_recoded, targets[version])))
        original_by_mask = {mask_from_partition(group.members): group for group in original}
        transported = {}
        for group in shifted:
            restored = tuple(FIXED_CODING[column] for column in group.members)
            mask = mask_from_partition(restored)
            means = tuple(81 - mean for mean in group.means) if 15 in restored else group.means
            transported[mask] = means
        require(transported == {mask: group.means for mask, group in original_by_mask.items()},
                f"{version}: arbitrary bin recoding changed fitted partitions or means")

        for observed in cases:
            for group in shifted:
                recovered = mask_from_partition(tuple(FIXED_CODING[column] for column in group.members))
                require(vote_detail(observed, [original_by_mask[recovered]])["rule_votes"] ==
                        vote_detail(recoded(observed), [group])["rule_votes"], f"{version}: a group vote is not ID-covariant")
            require(committee(observed, original) == committee(recoded(observed), shifted), f"{version}: committee changed under recoding")

        masks = set(original_by_mask)
        turned = {mask_from_partition(tuple(TURN_BIN[column] for column in group.members)) for group in original}
        individually_closed = sum(mask_from_partition(tuple(TURN_BIN[column] for column in group.members)) == mask
                                  for mask, group in original_by_mask.items())
        result[version] = {"partitions": len(masks), "transported_means_match": True,
                           "distinct_query_signatures_checked": len(cases),
                           "quarter_turn_closed_partitions": individually_closed,
                           "quarter_turn_closes_family": turned == masks}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("producer", type=Path)
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("--anchors", type=Path, required=True)
    parser.add_argument("--scored-sha", required=True)
    args = parser.parse_args()
    anchors = {row["stage"]: row for row in read_jsonl(args.anchors)}
    require(set(anchors) == {"fit", "blind"}, "Missing or ambiguous pre-transition anchors")
    anchors["scored"] = {"sha256": args.scored_sha}
    released = verify_releases(args.artifacts, args.producer, anchors)
    fixtures = enumerate_panel()
    files = expected_files(fixtures)
    chosen, calibrated, prior, train, targets, diagnostics = verify_fit(args.artifacts, files["train.jsonl"], fixtures)
    predictions, signatures, all_size = verify_blind(args.artifacts, files["queries.jsonl"], chosen, calibrated, prior,
                                                     released["blind"])
    scores = verify_scores(args.artifacts, predictions, fixtures, train, targets, released["scored"])
    covariance = covariance_and_rotation(chosen, train, targets, signatures)
    resources = {phase: {key: release[key] for key in ("seconds", "max_rss_kib", "observations")}
                 for phase, release in released.items()}
    resources["checkpoint_bytes"] = {path.stem: path.stat().st_size for path in sorted((args.artifacts / "fit").glob("*.json"))
                                     if path.name not in {"release.json", "diagnostics.json"}}
    resources["holdings_per_physical_group"] = HOLDING_COUNT
    mask_sets = {version: {mask_from_partition(group.members) for group in groups} for version, groups in chosen.items()}
    scores["fit_diagnostics"] = diagnostics
    scores["exact_replay"] = {
        "fit_arms": 11, "fit_rows": 64, "fit_actions_and_rewards": 64 * 11, "prefix_physical_hashes": 64 * 8,
        "blind_images": 704, "blind_arms": 31, "blind_actions": 704 * 31,
        "individual_rule_vote_rows": len(signatures), "pre_transition_anchors_match": True,
    }
    scores["feature_recoding"] = {"new_to_old": FIXED_CODING, "schedules": covariance}
    scores["fitted_comparison"] = {"all_groups_at_ordinary_selected_size": all_size,
        "opposite_has_same_selection": mask_sets["opposite"] == mask_sets["ordinary"],
        "shifted_membership_overlap": len(mask_sets["shifted"] & mask_sets["ordinary"])}
    scores["resources"] = resources
    print(json.dumps(scores, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
