#!/usr/bin/env python3
"""Recompute relative-pixel releases from committed raw artifacts after scoring."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

from fitted_reader import (
    CONVENTIONS, LAWS, READERS, TREE_SENSORS, blank_words, evaluate_all, fitted_words, load,
    models_from_training, numeric_group,
)
from scorer_reference import score
from tree_oracle import (
    digest, equivalent, hash_memory, impurity, ranked_splits, read_jsonl, require, route, sensor_view,
)


STAGES = ("sense", "fit", "pair", "blind", "scored")
BACKENDS = (*LAWS, "integer")
FIT_NAMES = tuple(f"{reader}-{kind}-{schedule}" for reader, kind, schedule in product(READERS, BACKENDS, CONVENTIONS))
SOURCES = {"sense": ("diagnostic",), "fit": ("train", "training_key"), "pair": ("diagnostic",),
           "blind": ("queries",), "scored": ("scorer_key",)}
FILES = {"sense": {"sensors.json"}, "fit": {"receipts.jsonl", "diagnostics.json", *(name + ".json" for name in FIT_NAMES)},
         "pair": {"predictions.jsonl", "interventions.json"}, "blind": {"predictions.jsonl", "interventions.json"},
         "scored": {"scores.json"}}


def release_chain(producer, artifacts, anchor_file, external):
    audit = Path(__file__).resolve().parent
    authority = audit / "R1/red_team_report.json"
    anchors = read_jsonl(anchor_file)
    require([row["stage"] for row in anchors] == ["fit", "blind"], "Incorrect external anchor roster")
    archive = {stage: artifacts / stage / "release.json" for stage in STAGES}
    for anchor, successor in zip(anchors, ("pair", "scored"), strict=True):
        stage = anchor["stage"]
        require(external[stage] == anchor["sha256"] == digest(archive[stage].read_bytes()), f"Wrong external {stage} lock")
        low = datetime.fromisoformat(load(archive[stage])["utc"])
        high = datetime.fromisoformat(load(archive[successor])["utc"])
        require(low < datetime.fromisoformat(anchor["utc"]) < high and anchor["next_stage_absent"] == successor,
                f"Late or unexpected {stage} external lock")
    require(external["scored"] == digest(archive["scored"].read_bytes()), "Wrong authorized final release")
    require(external["sense"] == digest(archive["sense"].read_bytes()), "Wrong pre-fit public sensor release")
    if "pair" in external:
        require(external["pair"] == digest(archive["pair"].read_bytes()), "Wrong public diagnosis release")
    contract = digest((producer / "contract.json").read_bytes())
    reports = {}
    budgets = {"sense": {"public_inputs": 2, "learned_states": 0, "training_updates": 0},
               "fit": {"models": 18, "presentations_per_model": 64, "reward_events": 1152, "archived_state_matches": 6},
               "pair": {"images": 2, "action_columns": 48, "reward_events": 0},
               "blind": {"images": 1024, "action_columns": 48, "reward_events": 0},
               "scored": {"images": 1024, "action_columns": 48}}
    last_time = datetime.fromisoformat(load(authority)["audit_utc"])
    for stage in STAGES:
        receipt = load(archive[stage])
        require(receipt["contract"] == contract and receipt["observations"] == budgets[stage], f"Incorrect {stage} contract or budget")
        require(receipt["seconds"] >= 0 and receipt["max_rss_kib"] > 0, f"Missing {stage} resource observations")
        expected = {"run_authorization": authority, **{name: archive[name] for name in reports},
                    **{name: producer / "panel" / (name + ".jsonl") for name in SOURCES[stage]}}
        require(receipt["parents"] == {name: digest(path.read_bytes()) for name, path in expected.items()}, f"Incorrect {stage} parent binding")
        require(set(receipt["files"]) == FILES[stage] and set(p.name for p in archive[stage].parent.iterdir()) == FILES[stage] | {"release.json"},
                f"Incorrect {stage} output roster")
        require(receipt["files"] == {name: digest((archive[stage].parent / name).read_bytes()) for name in FILES[stage]},
                f"Invalid {stage} output digest")
        settled = datetime.fromisoformat(receipt["utc"])
        require(last_time < settled, "Out-of-order stage receipts")
        last_time = settled
        reports[stage] = receipt
    return reports


def redraw_pair_senses(pair, artifact):
    forward = {}
    for sensor, reader in (("position", "position"), ("window", "window_tree")):
        vectors = [sensor_view(reader, row["pixels"]) for row in pair]
        differing = [i for i, (x, y) in enumerate(zip(*vectors, strict=True)) if x != y]
        forward[sensor] = {"vectors": {row["id"]: features for row, features in zip(pair, vectors, strict=True)},
                           "equal": not differing, "differing_indices": differing}
    require(equivalent(load(artifact), forward), "Public-pair sensor reproduction differs")
    require(forward["window"]["equal"], "Documented predecessor collision did not reproduce")
    return forward


def endpoint(reader, law, model):
    if law != "integer":
        return fitted_words(reader, law, model)
    if reader == "window_group":
        return numeric_group(model)
    return {"schema": "relative-pixel-integer-tree-v1", "sensor": TREE_SENSORS[reader], "tree": model}


def verify_fit(producer, artifacts):
    rows = read_jsonl(producer / "panel/train.jsonl")
    key = read_jsonl(producer / "panel/training_key.jsonl")
    raw = [row["pixels"] for row in rows]
    require([row["id"] for row in rows] == [row["id"] for row in key] and len(rows) == 64, "Wrong 64-row teaching roster")
    targets = [int(row["label"] == "T") for row in key]
    models, expected = models_from_training(raw, targets)
    reference_receipts = []
    for index, public in enumerate(rows):
        outputs = {}
        for reader, backend, schedule in product(READERS, BACKENDS, CONVENTIONS):
            guess, correct, before, after = expected[reader, schedule][index]
            action = {"guess": guess, "correct": correct}
            if backend != "integer":
                action |= {"before_sha256": before[backend], "after_sha256": after[backend]}
            outputs[f"{reader}-{backend}-{schedule}"] = action
        reference_receipts.append({"slot": index, "id": public["id"], "readers": outputs})
    require(equivalent(read_jsonl(artifacts / "fit/receipts.jsonl"), reference_receipts), "Earned-action or exact prefix words differ")
    reconstructed = {}
    diagnostics = {}
    archive = artifacts.parents[1] / "VARIED-LETTER-DRAWINGS-20261122-001/VARIED-LETTER-DRAWINGS-20261122-001-E001_drawings/fit"
    for reader, backend, schedule in product(READERS, BACKENDS, CONVENTIONS):
        code = f"{reader}-{backend}-{schedule}"
        fitted = models[reader, schedule]
        state = endpoint(reader, backend, fitted)
        require(equivalent(state, load(artifacts / "fit" / (code + ".json"))), f"Endpoint difference in {code}")
        if reader == "window_group":
            older = archive / (f"varied-{backend}-{schedule}.json")
            require(equivalent(state, load(older)), f"Archived comparison endpoint differs in {code}")
        reconstructed[code] = state
        if reader != "window_group":
            diagnostics[code] = fitted
        elif backend == "integer":
            diagnostics[code] = state
        else:
            diagnostics[code] = {"masks": fitted["masks"], "smaller_side_cardinality": fitted["size"],
                 "class_counts": fitted["class_counts"], "class_totals": fitted["class_totals"],
                 "rank_numerator": fitted["score"][0], "rank_denominator": fitted["score"][1], "partitions_scored": 32767}
    require(equivalent(load(artifacts / "fit/diagnostics.json"), diagnostics), "Fitted diagnostics differ")
    return models, reconstructed, raw, targets


def verify_actions(input_rows, prefix, models, words):
    exact = []
    for item in input_rows:
        evaluation = evaluate_all(item["pixels"], models)
        actions = {}
        traces = {reader: evaluation[reader]["ordinary"] for reader in READERS}
        for reader, backend in product(READERS, BACKENDS):
            first = evaluation[reader]["ordinary"]["guess"]
            second = evaluation[reader]["opposite"]["guess"]
            conditions = {"ordinary": first, "opposite": second}
            if backend != "integer":
                conditions |= {"sham": first, "swapped-ordinary": second, "swapped-opposite": first, "clear": 0, "restored": first}
            for condition, choice in conditions.items():
                actions[f"{reader}-{backend}-{condition}"] = choice
        exact.append({"id": item["id"], "actions": actions, "traces": traces})
    require(equivalent(read_jsonl(prefix / "predictions.jsonl"), exact), f"Exact action or path divergence in {prefix.name}")

    receipts = {}
    for reader, backend in product(READERS, BACKENDS):
        base = f"{reader}-{backend}-"
        setup = {"ordinary": ("ordinary", "ordinary"), "opposite": ("opposite", "opposite")}
        if backend != "integer":
            setup |= {"sham": ("ordinary", "ordinary"), "swapped-ordinary": ("ordinary", "opposite"),
                       "swapped-opposite": ("opposite", "ordinary"), "clear": ("ordinary", None), "restored": ("ordinary", "ordinary")}
        for condition, (recipient, source) in setup.items():
            state = words[base + source] if source else blank_words(reader, backend)
            receipts[base + condition] = {"recipient": base + recipient, "source": base + source if source else "neutral",
                                          "sha256": hash_memory(state)}
    require(equivalent(load(prefix / "interventions.json"), receipts), f"Adaptive intervention digest differs in {prefix.name}")
    return exact


def exact_ratio(number):
    return [number.numerator, number.denominator]


def fit_paths(tree, training):
    diagnostics = {}

    def inspect(node, rows, index, depth):
        book = Counter(label for _, label in rows)
        histogram = [book[0], book[1]]
        baseline = impurity(histogram)
        if "vote" in node:
            diagnostics[str(index)] = {"depth": depth, "training_L_T_counts": histogram, "vote": node["vote"],
                "stop": "depth limit" if depth == 3 else "single class" if baseline == 0 else "no positive gain"}
            return
        eligible = ranked_splits(rows)
        loss, feature, cutoff = eligible[0]
        require((feature, cutoff) == (node["feature"], node["threshold"]), "Exact split rank disagrees with the fitted tree")
        diagnostics[str(index)] = {"depth": depth, "training_L_T_counts": histogram, "feature": feature, "threshold": cutoff,
              "weighted_Gini_gain": exact_ratio((baseline - loss) * Fraction(2, len(rows))),
              "nonempty_observed_threshold_splits": len(eligible),
              "positive_gain_splits": sum(quality < baseline for quality, _, _ in eligible),
              "equal_best_splits": [[dim, level] for rank, dim, level in eligible if rank == loss]}
        children = ([record for record in rows if record[0][feature] <= cutoff],
                    [record for record in rows if record[0][feature] > cutoff])
        inspect(node["left"], children[0], 2 * index + 1, depth + 1)
        inspect(node["right"], children[1], 2 * index + 2, depth + 1)

    inspect(tree, training, 0, 0)
    return diagnostics


def ceiling_counts(rows, keys, feature, held_only):
    roster = defaultdict(lambda: defaultdict(list))
    for row in rows:
        label = keys[row["id"]]
        if held_only and label["q"] not in (2, 3):
            continue
        unit = label["style"], label["label"], label["q"]
        roster[feature(row)][unit].append(row["id"])
    mixed = []
    ceiling = 0
    units = 0
    bitmaps = 0
    for signature, examples in roster.items():
        require(all(len(ids) == 16 for ids in examples.values()), "Translation support differs for a held shape")
        by_letter = Counter(example[1] for example in examples)
        bitmaps += sum(len(ids) for ids in examples.values())
        units += len(examples)
        ceiling += max(by_letter.values())
        if len(by_letter) > 1:
            mixed.append({"signature": signature, "units": [
                {"style": style, "label": label, "q": q, "example_bitmap": min(examples[style, label, q])}
                for style, label, q in sorted(examples)]})
    return {"distinct_signatures": len(roster), "drawing_letter_turn_units": units, "bitmaps": bitmaps,
            "deterministic_max_correct_units": ceiling, "identical_signature_opposite_label_cases": mixed}


def sensor_and_leaf_profiles(models, train, targets, queries, metadata):
    keys = {row["id"]: row for row in metadata}
    results = {}
    for reader in ("position", "window_tree"):
        tree = models[reader, "ordinary"]
        feature = lambda row: sensor_view(reader, row["pixels"])
        samples = [sensor_view(reader, raw) for raw in train]
        deployed = list(zip(samples, targets, strict=True))
        occupied = set(samples)
        paths = fit_paths(tree, deployed)
        leaves = defaultdict(lambda: Counter({"T": 0, "L": 0, "correct": 0, "total": 0}))
        overlap_association = defaultdict(set)
        for source, truth in deployed:
            overlap_association[source].add("LT"[truth])
        novelty = defaultdict(Counter)
        for row in queries:
            meta = keys[row["id"]]
            observed = feature(row)
            found = overlap_association.get(observed, set())
            tier = "new" if not found else "same_label" if found == {meta["label"]} else "different_or_mixed_label"
            novelty[meta["condition"]][tier] += 1
            if meta["q"] not in (2, 3):
                continue
            decision, index, _ = route(tree, observed)
            aggregate = leaves[str(index)]
            aggregate[meta["label"]] += 1
            aggregate["correct"] += int(meta["label"] == "LT"[decision])
            aggregate["total"] += 1
        results[reader] = {
            "all_sensory_signatures": ceiling_counts(queries, keys, feature, False),
            "held_sensory_signatures": ceiling_counts(queries, keys, feature, True),
            "held_tree_leaves": ceiling_counts(queries, keys, lambda row: route(tree, feature(row))[1], True),
            "training_distinct_signatures": len(occupied),
            "fresh_signature_novelty": novelty,
            "training_correct": sum(route(tree, value)[0] == label for value, label in deployed),
            "train_node_and_leaf_calibration": paths, "held_label_counts_by_leaf": leaves,
        }
    return results


def pair_profile(rows, metadata, tree_profiles):
    keys = {row["id"]: row for row in metadata}
    require(set(keys) == {row["id"] for row in rows} and len(rows) == 2, "Wrong public pair labels")
    results = {"instances": [{"id": row["id"], "label": keys[row["id"]]["label"], "q": keys[row["id"]]["q"],
                              "actions": row["actions"], "traces": row["traces"]} for row in rows],
             "correct": {column: sum(row["actions"][column] == (int(keys[row["id"]]["label"] == "T") ^ column.endswith("-opposite"))
                                      for row in rows) for column in rows[0]["actions"]}}
    readers = {}
    for reader in ("position", "window_tree"):
        paths = [row["traces"][reader]["path"] for row in rows]
        difference = next(([depth, first, second] for depth, (first, second) in enumerate(zip(*paths))
                           if first["branch"] != second["branch"]), None)
        leaves = []
        for steps in paths:
            cursor = 0
            for step in steps:
                cursor = 2 * cursor + (1 if step["branch"] == "left" else 2)
            leaves.append({"index": cursor, **tree_profiles[reader]["train_node_and_leaf_calibration"][str(cursor)]})
        readers[reader] = {"first_split_with_different_branches": difference, "leaves": leaves}
    results["paired_tree_routes"] = readers
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("producer", type=Path)
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("--anchors", type=Path, required=True)
    parser.add_argument("--sense-sha", required=True)
    parser.add_argument("--fit-sha", required=True)
    parser.add_argument("--pair-sha")
    parser.add_argument("--blind-sha", required=True)
    parser.add_argument("--scored-sha", required=True)
    args = parser.parse_args()
    expected = {"sense": args.sense_sha, "fit": args.fit_sha, "blind": args.blind_sha, "scored": args.scored_sha}
    if args.pair_sha:
        expected["pair"] = args.pair_sha
    release = release_chain(args.producer, args.artifacts, args.anchors, expected)
    inputs = args.producer / "panel"
    known = read_jsonl(inputs / "diagnostic.jsonl")
    sensed = redraw_pair_senses(known, args.artifacts / "sense/sensors.json")
    fitted, words, training, earned = verify_fit(args.producer, args.artifacts)
    diagnostic = verify_actions(known, args.artifacts / "pair", fitted, words)
    queries = read_jsonl(inputs / "queries.jsonl")
    blind = verify_actions(queries, args.artifacts / "blind", fitted, words)
    keys = read_jsonl(inputs / "scorer_key.jsonl")
    scores, additional = score(blind, keys)
    require(equivalent(scores, load(args.artifacts / "scored/scores.json")), "Independent fresh scorer differs")
    profiles = sensor_and_leaf_profiles(fitted, training, earned, queries, keys)
    results = {**scores, **additional,
        "fitted_state_summary": {f"{reader}-{convention}": state for (reader, convention), state in fitted.items()},
        "public_pair": pair_profile(diagnostic, read_jsonl(inputs / "diagnostic_key.jsonl"), profiles),
        "public_pair_sensors": sensed, "fresh_sensor_and_tree_diagnostics": profiles,
        "replay": {"train_receipts": 64, "train_decisions_and_rewards": 1152, "physical_prefix_digests": 1536,
            "fitted_states": 18, "public_pair_actions": 96, "fresh_actions": 49152, "states_per_issued_panel": 48,
            "authentic_external_digests": expected},
        "resources": {phase: {name: item[name] for name in ("seconds", "max_rss_kib", "observations")} for phase, item in release.items()}}
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
