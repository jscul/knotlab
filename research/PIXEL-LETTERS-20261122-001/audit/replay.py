#!/usr/bin/env python3
"""Recompute letter experiment fits and outcomes without importing the producer."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

from verify import digest, equal_json_values, expected_files, independent_panel, load_json, local_census, read_jsonl, require


PREPARED = {"parity": {"110": 0, "011": 1}, "nae": {"110": 0, "001": 1}}
VERSIONS = ("ordinary", "opposite")
CONDITIONS = ("familiar", "position", "orientation", "combined")


def read_json(path):
    return load_json(path.read_bytes())


def memory_digest(memory):
    return digest(json.dumps(memory, sort_keys=True, separators=(",", ":")).encode("ascii"))


def encode_physical(banks, law):
    bits = {value: word for word, value in PREPARED[law].items()}
    return {
        "schema": "pixel-knot-histograms-v1",
        "law": law,
        "training_limit": 64,
        "words": [["".join(bits[int(bit)] for bit in reversed(f"{count:013b}")) for count in bank] for bank in banks],
    }


def decode_physical(memory, law):
    require(set(memory) == {"schema", "law", "training_limit", "words"}, "Unexpected memory fields")
    require(memory["law"] == law and memory["schema"] == "pixel-knot-histograms-v1", "Wrong law or schema")
    require(type(memory["training_limit"]) is int and memory["training_limit"] == 64, "Wrong memory budget")
    banks = memory["words"]
    require(len(banks) == 2 and all(len(bank) == 16 for bank in banks), "Wrong number of prepared registers")
    converted = []
    for bank in banks:
        counts = []
        for register in bank:
            require(len(register) == 39, "Wrong register width for 64 scheduled presentations")
            value = 0
            for index in range(13):
                triple = register[index * 3:index * 3 + 3]
                require(triple in PREPARED[law], f"Unrecognized preparation for {law}: {triple}")
                value += PREPARED[law][triple] * (2 ** index)
            counts.append(value)
        require(sum(counts) % 81 == 0, "The register totals do not count complete bitmaps")
        converted.append(tuple(counts))
    return tuple(converted)


def bank_totals(samples):
    by_action = [[], []]
    for pixels, action in samples:
        by_action[action].append(local_census(pixels))
    return tuple(tuple(sum(group) for group in zip(*descriptors, strict=True)) if descriptors else (0,) * 16
                 for descriptors in by_action)


def nearest_mean(features, banks):
    costs = {}
    for action, bank in enumerate(banks):
        presentations = Fraction(sum(bank), 81)
        require(presentations.denominator == 1, "Incomplete set of histograms")
        if presentations:
            means = [stored / presentations for stored in bank]
            costs[action] = sum((count - expectation) ** 2 for count, expectation in zip(features, means, strict=True))
    return min(costs, key=lambda action: (costs[action], action)) if costs else 0


def hamming_vote(pixels, samples):
    if not samples:
        return 0
    distances = [(sum(a != b for a, b in zip(sample, pixels, strict=True)), target) for sample, target in samples]
    best_distance = min(distance for distance, _ in distances)
    votes = Counter(action for distance, action in distances if distance == best_distance)
    return int(votes[1] > votes[0])


def signature_decisions(features, banks):
    signatures = defaultdict(list)
    decisions = {}
    for (label, style, turns), histogram in features.items():
        case = f"{style}/q{turns}/{label}"
        reading = readout(histogram, banks)
        signatures[histogram].append(case)
        decisions[case] = {
            "guess": "LT"[reading["guess"]],
            "squared_discrepancies": [str(Fraction(action["distance_numerator"], action["distance_denominator"]))
                                      for action in reading["actions"]],
        }
    return {"decisions_by_signature": decisions,
            "shared_signatures": [cases for cases in signatures.values() if len(cases) > 1]}


def verify_frozen_histograms(examples):
    seen = {}
    for fixture in examples.values():
        signature = fixture["label"], fixture["style"], fixture["q"]
        local_signature = local_census(fixture["pixels"])
        if signature in seen:
            require(seen[signature] == local_signature, "The frozen read leaked a position distinction")
        else:
            seen[signature] = local_signature
    require(len(seen) == 16, "Wrong number of labeled style/rotation combinations")
    require(all(sum(seen[label, style, q]) == 81
                for label, style, q in product(("L", "T"), ("S", "W"), range(4))), "Omitted padded window")
    return seen


def phase_seals(root, producer_dir, fit_anchor, blind_anchor):
    by_phase = {}
    expected_outputs = {
        "fit": {"receipts.jsonl", "nearest-ordinary.json"} | {
            f"{family}-{version}.json" for family, version in product((*PREPARED, "integer"), VERSIONS)
        },
        "blind": {"predictions.jsonl"},
        "scored": {"scores.json"},
    }
    gate = Path(__file__).resolve().parent / "R1/red_team_report.json"
    expected_inputs = {
        "fit": {"authorization": gate, "train": producer_dir / "panel/train.jsonl",
                "training_key": producer_dir / "panel/training_key.jsonl"},
        "blind": {"fit_release": root / "fit/release.json", "queries": producer_dir / "panel/queries.jsonl"},
        "scored": {"blind_release": root / "blind/release.json", "scorer_key": producer_dir / "panel/scorer_key.jsonl"},
    }
    for phase, anchor in (("fit", fit_anchor), ("blind", blind_anchor), ("scored", None)):
        folder = root / phase
        lock = folder / "release.json"
        if anchor:
            require(digest(lock.read_bytes()) == anchor, f"{phase} release differs from its pre-transition commitment")
        receipt = read_json(lock)
        require(receipt["contract_sha256"] == digest((producer_dir / "contract.json").read_bytes()),
                f"{phase} did not retain the frozen contract binding")
        require(set(receipt["files"]) == expected_outputs[phase], f"Unexpected {phase} output roster")
        require(receipt["inputs"] == {name: digest(path.read_bytes()) for name, path in expected_inputs[phase].items()},
                f"Unexpected {phase} input digests")
        for name, sha in receipt["files"].items():
            require(digest((folder / name).read_bytes()) == sha, f"{phase}/{name} digest mismatch")
        by_phase[phase] = receipt
    fit, blind, scored = (datetime.fromisoformat(by_phase[part]["closed_utc"]) for part in ("fit", "blind", "scored"))
    require(datetime.fromisoformat(read_json(gate)["audit_utc"]) < fit < blind < scored,
            "Expected gate and release ordering did not hold")
    require(by_phase["fit"]["observations"] == {"presentations_per_arm": 64, "arms": 7, "epochs": 1},
            "Unexpected fitting budget")
    require(by_phase["blind"]["observations"] == {"images": 336, "issued_arms_per_image": 23, "rewards": 0},
            "Unexpected blind inference budget")
    require(by_phase["scored"]["observations"]["images_joined"] == 336, "Wrong number of scored cases")
    return by_phase


def verify_fit(root, rows, examples):
    observed = read_jsonl((root / "fit/receipts.jsonl").read_bytes())
    require(len(observed) == len(rows) == 64, "Missing fit receipt")
    banks = {version: [[0] * 16, [0] * 16] for version in VERSIONS}
    samples = []
    for index, (row, receipt) in enumerate(zip(rows, observed, strict=True), start=1):
        label = int(examples[row["id"]]["label"] == "T")
        features = local_census(row["pixels"])
        turns = {}
        for version in VERSIONS:
            guess = nearest_mean(features, banks[version])
            correct = guess == (label ^ (version == "opposite"))
            action_memory = guess if correct else 1 - guess
            bank = banks[version][action_memory]
            for i, addition in enumerate(features):
                bank[i] += addition
            turns[f"integer-{version}"] = {
                "guess": guess, "correct": correct, "after_sha256": memory_digest(banks[version]),
            }
            for law in PREPARED:
                turns[f"{law}-{version}"] = {
                    "guess": guess, "correct": correct, "after_sha256": memory_digest(encode_physical(banks[version], law)),
                }
        guess = hamming_vote(row["pixels"], samples)
        correct = guess == label
        samples.append([row["pixels"], guess if correct else 1 - guess])
        turns["nearest-ordinary"] = {"guess": guess, "correct": correct, "after_sha256": memory_digest(samples)}
        require(equal_json_values(receipt, {"id": row["id"], "presentation": index, "arms": turns}),
                f"Feedback trace differs at {index}")

    require(read_json(root / "fit/nearest-ordinary.json") == samples, "Different conventional training-memory order")
    totals = bank_totals(samples)
    require(totals == tuple(map(tuple, banks["ordinary"])), "Exact batch totals differ from sequential replay")
    require(totals[::-1] == tuple(map(tuple, banks["opposite"])), "Opposite learning targeted different counts")
    for version in VERSIONS:
        trained = banks[version]
        require(read_json(root / f"fit/integer-{version}.json") == trained, "Numeric twin retained different state")
        for law in PREPARED:
            physical = read_json(root / f"fit/{law}-{version}.json")
            require(decode_physical(physical, law) == tuple(map(tuple, trained)), "The serialized marks hold different counts")
    return banks, samples


def readout(features, banks):
    reading = []
    for bank in banks:
        presentations = sum(bank) // 81
        differences = [presentations * value - count for value, count in zip(features, bank, strict=True)]
        reading.append({
            "total": sum(bank), "row_count": presentations, "per_word_differences": differences,
            "distance_numerator": sum(value * value for value in differences),
            "distance_denominator": presentations * presentations,
        })
    return {"counts": list(features), "actions": reading, "guess": nearest_mean(features, banks)}


def verify_blind(root, queries, banks, samples):
    actual = read_jsonl((root / "blind/predictions.jsonl").read_bytes())
    require(len(actual) == len(queries) == 336, "Prediction stream length mismatch")
    reconstructed = []
    for query, observed in zip(queries, actual, strict=True):
        feature = local_census(query["pixels"])
        choices = {version: nearest_mean(feature, banks[version]) for version in VERSIONS}
        actions = {f"integer-{version}": choices[version] for version in VERSIONS}
        actions["nearest-ordinary"] = hamming_vote(query["pixels"], samples)
        for law, version in product(PREPARED, VERSIONS):
            other = "opposite" if version == "ordinary" else "ordinary"
            for intervention in ("", "sham-", "restore-"):
                actions[f"{law}-{intervention}{version}"] = choices[version]
            actions[f"{law}-clear-{version}"] = 0
            actions[f"{law}-donor-into-{version}"] = choices[other]
        expectation = {"id": query["id"], "actions": actions, "reading": readout(feature, banks["ordinary"])}
        require(equal_json_values(observed, expectation), f"Blind action/readout mismatch for {query['id']}")
        reconstructed.append(expectation)
    return reconstructed


def verify_scores(root, predictions, fixtures, train):
    truth_histograms = defaultdict(set)
    for pixels, label in train:
        truth_histograms[local_census(pixels)].add("LT"[label])
    cells = defaultdict(lambda: defaultdict(Counter))
    controls = defaultdict(Counter)
    distinct = defaultdict(set)
    novelty = defaultdict(Counter)
    poses = defaultdict(Counter)
    representatives = {}
    nearest_errors = {}
    for row in sorted(predictions, key=lambda row: row["id"]):
        identity, actions = row["id"], row["actions"]
        case = fixtures[identity]
        condition, label, style, turns = (case[field] for field in ("condition", "label", "style", "q"))
        target = "LT".index(label)
        score = actions["parity-ordinary"] == target
        poses[f"{condition}/{style}/q{turns}/{label}"].update({"total": 1, "correct": int(score)})
        readings = row["reading"]["actions"]
        tie = len({Fraction(reading["distance_numerator"], reading["distance_denominator"]) for reading in readings}) == 1
        feature = tuple(row["reading"]["counts"])
        distinct[condition].add(feature)
        found = truth_histograms.get(feature, set())
        representation = "new" if not found else ("same" if found == {label} else "opposite_or_mixed")
        novelty[condition].update({representation: 1, "ties": int(tie)})
        category = f"{condition}/{label}/{'correct' if score else 'error'}"
        bitmap_rows = [case["pixels"][i:i + 8] for i in range(0, 64, 8)]
        image_record = {"id": identity, **{field: value for field, value in case.items() if field != "pixels"},
                        "guess": "LT"[actions["parity-ordinary"]], "nearest_guess": "LT"[actions["nearest-ordinary"]],
                        "bitmap_rows": bitmap_rows}
        representatives.setdefault(category, {**image_record, "histogram_overlap": representation, "reading": row["reading"]})
        if actions["nearest-ordinary"] != target:
            nearest_errors.setdefault(condition, image_record)
        for arm, guess in actions.items():
            wanted = target ^ arm.endswith("-opposite")
            cells[condition][arm].update({label + "_total": 1, label + "_correct": int(wanted == guess)})
        for law in PREPARED:
            variants = {arm.removeprefix(law + "-"): guess for arm, guess in actions.items() if arm.startswith(law + "-")}
            flips = variants["ordinary"] != variants["opposite"]
            donor_matches = variants["donor-into-ordinary"] == variants["opposite"] and variants["donor-into-opposite"] == variants["ordinary"]
            controls[law].update({
                "images": 1, "ordinary_opposite_disagreements": int(flips), "both_donor_reads_match": int(donor_matches),
                "both_reversed": int(flips and donor_matches),
                "both_shams_unchanged": int(all(variants["sham-" + v] == variants[v] for v in VERSIONS)),
                "both_restored": int(all(variants["restore-" + v] == variants[v] for v in VERSIONS)),
                "both_clear_to_zero": int(all(variants["clear-" + v] == 0 for v in VERSIONS)),
                "both_match_conventional_twin": int(all(variants[v] == actions["integer-" + v] for v in VERSIONS)),
            })
    exact = {
        "scores": cells,
        "interventions": controls,
        "histogram_overlap": {c: {**novelty[c], "distinct": len(distinct[c])} for c in CONDITIONS},
        "distinct_training_histograms": len(truth_histograms),
        "training_histograms_cross_label": sum(len(labels) > 1 for labels in truth_histograms.values()),
        "scores_by_style_q_class": poses,
        "representatives": representatives,
        "nearest_errors": nearest_errors,
    }
    require(equal_json_values(read_json(root / "scored/scores.json"), exact), "Independent scored output differs")
    return exact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("producer", type=Path)
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("--fit-anchor", required=True)
    parser.add_argument("--blind-anchor", required=True)
    args = parser.parse_args()
    seals = phase_seals(args.artifacts, args.producer, args.fit_anchor, args.blind_anchor)
    fixtures = independent_panel()
    inputs = expected_files(fixtures)
    features = verify_frozen_histograms(fixtures)
    banks, samples = verify_fit(args.artifacts, inputs["train.jsonl"], fixtures)
    predictions = verify_blind(args.artifacts, inputs["queries.jsonl"], banks, samples)
    summary = verify_scores(args.artifacts, predictions, fixtures, samples)
    summary["signatures"] = signature_decisions(features, banks["ordinary"])
    summary["resources"] = {phase: {key: release[key] for key in ("seconds", "max_rss_kib", "observations")}
                            for phase, release in seals.items()}
    summary["resources"]["state_bytes"] = {artifact.stem: artifact.stat().st_size
                                             for artifact in sorted((args.artifacts / "fit").glob("*.json"))
                                             if artifact.name != "release.json"}
    summary["balanced_chance"] = {condition: {label: {"expected_correct": cell["parity-ordinary"][label + "_total"] // 2,
                                                        "total": cell["parity-ordinary"][label + "_total"]}
                                                   for label in "LT"} for condition, cell in summary["scores"].items()}
    summary["exact_replay"] = {"training_rows": 64, "training_arms": 7, "blind_rows": len(predictions),
                               "blind_arms": len(predictions[0]["actions"]),
                               "anchor_invariant_signatures": len(features)}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
