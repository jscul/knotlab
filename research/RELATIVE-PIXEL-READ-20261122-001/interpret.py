"""Explain the sealed relative-pixel predictions without changing any fitted state."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path


RECORD = Path(__file__).resolve().parent
ROOT = RECORD.parents[1]
TICKET = RECORD.name
FAMILY = ROOT / "experiments" / TICKET / f"{TICKET}-E001_relative"
ARCHIVE = ROOT / "artifacts" / TICKET / FAMILY.name
TREE_SENSORS = {"position": "position", "window_tree": "window"}
LAWS = ("parity", "nae")
SCHEDULES = ("ordinary", "opposite")
PLACEMENTS = set(product(range(4), repeat=2))
HELD = (2, 3)


def study_module():
    spec = spec_from_file_location("relative_interpret_study", FAMILY / "study.py")
    study = module_from_spec(spec)
    spec.loader.exec_module(study)
    return study


def checked_scored(study, out, anchors):
    contract, authority = study.preflight()
    study.check_upstream(out, "scored", contract, authority)
    study.check_anchors(out, "scored", anchors)
    scored = out / "scored"
    release = study.io.load(scored / "release.json")
    if (release["parents"] != study.parents(out, "scored", contract, authority)
            or release["contract"] != study.io.digest(study.FAMILY / "contract.json")
            or set(release["files"]) != study.FILES["scored"]
            or {path.name for path in scored.iterdir()} != study.FILES["scored"] | {"release.json"}):
        raise ValueError("The score release does not bind the authenticated run")
    for name, expected in release["files"].items():
        study.io.checked_bytes(scored / name, expected)
    return contract


def earned_targets(receipts, checkpoint, initial_sha):
    earned = []
    counts = [0, 0]
    for slot, row in enumerate(receipts):
        step = row["readers"][checkpoint]
        guessed, correct = step["guess"], step["correct"]
        if (row["slot"] != slot or type(guessed) is not int or guessed != int(counts[1] > counts[0])
                or type(correct) is not bool or step["before_sha256"] != initial_sha):
            raise ValueError(f"Unexpected acquisition receipt at {checkpoint}/{slot}")
        action = guessed if correct else 1 - guessed
        earned.append(action)
        counts[action] += 1
        initial_sha = step["after_sha256"]
    if len(earned) != 64:
        raise ValueError("Expected exactly 64 earned targets")
    return earned


def weighted_impurity(zeroes, ones):
    return Fraction(2 * zeroes * ones, zeroes + ones)


def best_tests(rows, counts):
    """Compare exact weighted child impurities on the samples reaching one node."""
    baseline = weighted_impurity(*counts)
    best_gain = Fraction(0)
    winners = []
    legal = positive = 0
    for index in range(len(rows[0][0])):
        buckets = defaultdict(lambda: [0, 0])
        for vector, action in rows:
            buckets[vector[index]][action] += 1
        left0 = left1 = 0
        for threshold in sorted(buckets)[:-1]:
            count0, count1 = buckets[threshold]
            left0 += count0
            left1 += count1
            loss = weighted_impurity(left0, left1) + weighted_impurity(counts[0] - left0, counts[1] - left1)
            gain = (baseline - loss) / len(rows)
            legal += 1
            if gain > 0:
                positive += 1
                if gain > best_gain:
                    best_gain, winners = gain, []
                if gain == best_gain:
                    winners.append([index, threshold])
    return legal, positive, best_gain, winners


def inspect_tree(tree, training):
    """Follow the already fitted tree, verifying each choice from earned rows."""
    result = []

    def visit(node, rows, path):
        if not rows:
            raise ValueError(f"Stored fitted path {path!r} has no training witness")
        count1 = sum(action for _, action in rows)
        counts = [len(rows) - count1, count1]
        record = {"path": path or "root", "earned_actions": counts}
        result.append(record)
        if len(path) == 3:
            record["stop"] = "depth_limit"
        elif not all(counts):
            record["stop"] = "pure"
        else:
            legal, positive, gain, winners = best_tests(rows, counts)
            record.update(legal_tests=legal, positive_tests=positive, gain=[gain.numerator, gain.denominator],
                          equal_best_positive_tests=winners)
            if winners:
                selected = [node.get("feature"), node.get("threshold")]
                if selected != winners[0]:
                    raise ValueError(f"Stored decision at {path!r} disagrees with exact training rank")
                record["selected_test"] = selected
                feature, threshold = selected
                visit(node["left"], [row for row in rows if row[0][feature] <= threshold], path + "0")
                visit(node["right"], [row for row in rows if row[0][feature] > threshold], path + "1")
                return
            record["stop"] = "no_positive_gain"
        vote = int(counts[1] > counts[0])
        if node != {"vote": vote}:
            raise ValueError(f"Stored vote at {path!r} disagrees with earned majority")
        record["vote"] = vote

    visit(tree, training, "")
    return result


def fitted_readers(study, out, module, training_rows, receipts):
    if [row["id"] for row in training_rows] != [row["id"] for row in receipts]:
        raise ValueError("Released raw acquisition and receipts have different order")
    diagnostics = study.io.load(out / "fit/diagnostics.json")
    readers = {}
    training = {}
    for arm, sensor in TREE_SENSORS.items():
        vectors = [module.features(study.bits(row), sensor) for row in training_rows]
        for schedule in SCHEDULES:
            checks = {}
            for law in LAWS:
                name = f"{arm}-{law}-{schedule}"
                memory = study.io.load(out / "fit" / f"{name}.json")
                initial = study.io.memory_digest(module.KnotTree(law, sensor).export_memory())
                targets = earned_targets(receipts, name, initial)
                reader = module.KnotTree(law, sensor)
                reader.restore_memory(memory)
                described = reader.describe()
                if reader.export_memory() != memory or described != diagnostics[name]:
                    raise ValueError(f"Mature words and saved diagnosis disagree at {name}")
                nodes = inspect_tree(described, list(zip(vectors, targets, strict=True)))
                readers[name] = reader
                checks[law] = {"memory_sha256": study.io.memory_digest(memory), "nodes": nodes}
            entry = {"by_law": checks}
            if checks["parity"]["nodes"] == checks["nae"]["nodes"]:
                entry["nodes"] = checks["parity"].pop("nodes")
                checks["nae"].pop("nodes")
            training[f"{arm}-{schedule}"] = entry
    return readers, training


def join(views, predictions, keys):
    def by_id(rows):
        indexed = {row["id"]: row for row in rows}
        if len(indexed) != len(rows):
            raise ValueError("Duplicate row in a sealed input")
        return indexed

    view, predicted, key = (by_id(rows) for rows in (views, predictions, keys))
    if view.keys() != predicted.keys() or view.keys() != key.keys():
        raise ValueError("Released pixels, predictions and labels have different identities")
    return [(view[i], predicted[i], key[i]) for i in sorted(view)]


def branch_path(trace):
    return "".join("0" if step["branch"] == "left" else "1" for step in trace["path"]) or "root"


def actual_paths(study, readers, row, prediction):
    traces = {name: reader.explain(study.bits(row)) for name, reader in readers.items()}
    for name, trace in traces.items():
        arm = name.removesuffix("-parity-ordinary")
        if (trace["guess"] != prediction["actions"][name]
                or (arm in TREE_SENSORS and trace != prediction["traces"][arm])):
            raise ValueError(f"Live fitted read disagrees with recorded prediction at {row['id']}/{name}")
    return traces


def compress(study, module, readers, rows):
    groups = defaultdict(list)
    for joined in rows:
        row, prediction, key = joined
        groups[(key["style"], key["label"], key["q"])].append(joined)
    units = []
    for name, members in sorted(groups.items()):
        if len(members) != 16 or {(k["row"], k["col"]) for _, _, k in members} != PLACEMENTS:
            raise ValueError(f"Incomplete placement unit {name}")
        row, prediction, _ = members[0]
        traces = actual_paths(study, readers, row, prediction)
        signatures = {sensor: module.features(study.bits(row), sensor) for sensor in TREE_SENSORS.values()}
        for placed, emitted, _ in members:
            if (emitted["actions"] != prediction["actions"]
                    or any(emitted["traces"][arm] != traces[f"{arm}-parity-ordinary"] for arm in TREE_SENSORS)
                    or any(module.features(study.bits(placed), sensor) != pattern
                           for sensor, pattern in signatures.items())):
                raise ValueError(f"Decision, trace or feature signature varies by placement in {name}")
        units.append({"design": name[0], "letter": name[1], "q": name[2], "signatures": signatures,
                      "leaves": {model: branch_path(trace) for model, trace in traces.items()},
                      "actions": prediction["actions"]})
    return units


def describe_row(joined):
    row, _, key = joined
    return {"id": row["id"], "pixels": row["pixels"], "letter": key["label"], "design": key["style"],
            "q": key["q"], "anchor": [key["row"], key["col"]]}


def public_paths(study, readers, rows):
    if len(rows) != 2:
        raise ValueError("Expected exactly the two disclosed bitmaps")
    traces = [actual_paths(study, readers, row, prediction) for row, prediction, _ in rows]
    decisions = {}
    for name in readers:
        first, second = (trace[name] for trace in traces)
        correct = sum(trace[name]["guess"] == (int(joined[2]["label"] == "T") ^ int(name.endswith("-opposite")))
                      for trace, joined in zip(traces, rows, strict=True))
        decisions[name] = {"same_leaf": branch_path(first) == branch_path(second),
                           "same_path_trace": first["path"] == second["path"],
                           "same_guess": first["guess"] == second["guess"], "correct": correct}
    signatures = {}
    for arm, sensor in TREE_SENSORS.items():
        left, right = (trace[f"{arm}-parity-ordinary"]["features"] for trace in traces)
        differing = [i for i, (a, b) in enumerate(zip(left, right, strict=True)) if a != b]
        signatures[sensor] = {"equal": not differing, "differing_indices": differing}
    return {"sensor_signatures": signatures, "readings": decisions,
            "rows": [{**describe_row(joined), "traces": traced,
                                             "all_actions": joined[1]["actions"]}
                                            for joined, traced in zip(rows, traces, strict=True)]}


def unit_id(unit):
    return f"{unit['design']}/{unit['letter']}/q{unit['q']}"


def ceiling(groups, *, leaves=False):
    """Sum the larger label count in each representation class."""
    groups = list(groups.items())
    labelled = [(key, members, Counter(unit["letter"] for unit in members)) for key, members in groups]
    correct = sum(max(counts.values()) for _, _, counts in labelled)
    mixed = [{"label_counts": {letter: counts[letter] for letter in "LT"},
              "units": [unit_id(unit) for unit in members]}
             for _, members, counts in labelled if len(counts) == 2]
    result = {"max_correct_units": correct, "units": sum(len(members) for _, members in groups),
              "classes": len(groups), "mixed_classes": mixed}
    if leaves:
        result["at_leaf"] = {path: {letter: counts[letter] for letter in "LT"}
                             for path, _, counts in labelled}
    return result


def ceilings(units, reader_names):
    def group(field, key):
        by_signature = defaultdict(list)
        for unit in units:
            by_signature[unit[field][key]].append(unit)
        return by_signature

    sensor = {name: ceiling(group("signatures", name)) for name in TREE_SENSORS.values()}
    leaves = {}
    for name in reader_names:
        result = ceiling(group("leaves", name), leaves=True)
        result["read_correct_units"] = sum(unit["actions"][name] == (
            int(unit["letter"] == "T") ^ int(name.endswith("-opposite"))) for unit in units)
        leaves[name] = result
    return {"full_sensor_signatures": sensor, "reached_leaves": leaves}


def examples(rows):
    examples_by_case = {}
    selected = {}
    for joined in sorted(rows, key=lambda item: item[0]["id"]):
        row, prediction, key = joined
        for arm in TREE_SENSORS:
            guess = prediction["actions"][f"{arm}-parity-ordinary"]
            outcome = "correct" if guess == int(key["label"] == "T") else "incorrect"
            name = f"{arm}/q{key['q']}/{key['label']}/{outcome}"
            if name not in examples_by_case:
                examples_by_case[name] = row["id"]
                selected.setdefault(row["id"], {**describe_row(joined), "traces": prediction["traces"]})
    return {"index": examples_by_case, "rows_by_id": selected}


def interpret(out, anchors):
    study = study_module()
    contract = checked_scored(study, out, anchors)
    module = study.implementations(contract)[0]

    def run_rows(stage, name):
        return study.io.json_lines((out / stage / name).read_bytes())

    def panel_key(name):
        return study.io.json_lines(study.io.source_bytes(contract, study.PANEL / name))

    readers, training = fitted_readers(study, out, module, study.public(contract, "train"),
                                       run_rows("fit", "receipts.jsonl"))
    disclosed = join(study.public(contract, "diagnostic"), run_rows("pair", "predictions.jsonl"),
                     panel_key("diagnostic_key.jsonl"))
    fresh = join(study.public(contract, "queries"), run_rows("blind", "predictions.jsonl"),
                 panel_key("scorer_key.jsonl"))
    units = compress(study, module, readers, fresh)
    held_units = [unit for unit in units if unit["q"] in HELD]
    if len(units) != 64 or len(held_units) != 32 or len(fresh) != contract["blind_images"]:
        raise ValueError("Wrong compressed fresh roster")
    return {"schema_version": 1, "score_release_sha256": study.io.digest(out / "scored/release.json"),
            "training": training, "public_pair": public_paths(study, readers, disclosed),
            "unit_weighting": {"identity": ["design", "letter", "q"], "placements_per_unit": 16,
                               "fresh_units": len(units), "held_units": len(held_units),
                               "uniform_action_columns": len(units[0]["actions"])},
            "ceilings": {"held_turns": ceilings(held_units, readers), "all_fresh": ceilings(units, readers)},
            "representative_fresh_rows": examples(fresh)}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--out", type=Path, default=ARCHIVE, help="input run directory")
    cli.add_argument("--anchors", type=Path, default=RECORD / "phase_anchors.jsonl")
    cli.add_argument("--json", type=Path, help="exclusive destination for JSON")
    args = cli.parse_args()
    result = interpret(args.out, args.anchors)
    if args.json is None:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        with args.json.open("x", encoding="utf-8") as destination:
            json.dump(result, destination, sort_keys=True, separators=(",", ":"))
            destination.write("\n")
