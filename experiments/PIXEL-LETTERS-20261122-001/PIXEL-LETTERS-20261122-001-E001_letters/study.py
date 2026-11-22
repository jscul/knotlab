"""Replay the supervised fit, blind release and scorer join in separate processes."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import resource
import sys
from time import monotonic

from conventional import IntegerMeans, NearestBitmap, histogram
from learner import KnotLearner


FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
TICKET = FAMILY.parent.name
PANELS = FAMILY / "panel"
DEFAULT_OUT = ROOT / "artifacts" / TICKET / FAMILY.name
REVIEW = ROOT / "research" / TICKET
LAWS = ("parity", "nae")
VERSIONS = ("ordinary", "opposite")
CONDITIONS = ("familiar", "position", "orientation", "combined")
LIMIT = 64


def pack(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write_json(path, value):
    with path.open("x") as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")


def write_rows(path, records):
    with path.open("xb") as output:
        for record in records:
            output.write(pack(record) + b"\n")


def public_rows(path):
    records = rows(path)
    ids = set()
    for row in records:
        if set(row) != {"id", "pixels"}:
            raise ValueError("Unexpected field in public image")
        bitmap = row["pixels"]
        if len(bitmap) != 64 or set(bitmap) - {"0", "1"}:
            raise ValueError("Invalid raw bitmap")
        ident = sha256(bitmap.encode("ascii")).hexdigest()
        if ident != row["id"] or ident in ids:
            raise ValueError("Duplicate or mislabeled public image identifier")
        ids.add(ident)
    return records


def bind(path, expected):
    if digest(path) != expected:
        raise ValueError(f"Seal mismatch for {path}")


def verify_sources(*visible_inputs):
    lock = read_json(FAMILY / "contract.json")["frozen_files"]
    # Key custody is phase-specific. Only the scorer verifies the test-key bytes.
    for name in ("learner.py", "conventional.py", "study.py", *visible_inputs):
        bind(FAMILY / name, lock[name])


def phase_dir(out, name):
    out.mkdir(parents=True, exist_ok=True)
    target = out / name
    target.mkdir(exist_ok=False)
    return target


def release(target, files, parents, start, observations):
    receipt = {
        "files": {name: digest(target / name) for name in files},
        "inputs": {name: digest(path) for name, path in parents.items()},
        "contract_sha256": digest(FAMILY / "contract.json"),
        "closed_utc": datetime.now(timezone.utc).isoformat(),
        "seconds": round(monotonic() - start, 6),
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python": sys.version.split()[0],
        "observations": observations,
    }
    write_json(target / "release.json", receipt)
    return receipt


def check_release(folder):
    receipt = read_json(folder / "release.json")
    bind(FAMILY / "contract.json", receipt["contract_sha256"])
    for name, expected in receipt["files"].items():
        bind(folder / name, expected)
    return receipt


def models():
    result = {}
    for version in VERSIONS:
        for law in LAWS:
            result[f"{law}-{version}"] = KnotLearner(law, training_limit=LIMIT)
        result[f"integer-{version}"] = IntegerMeans()
    result["nearest-ordinary"] = NearestBitmap()
    return result


def train(out):
    start = monotonic()
    verify_sources("panel/train.jsonl", "panel/training_key.jsonl")
    gate = REVIEW / "audit/R1/red_team_report.json"
    authorization = read_json(gate)
    if authorization["gate"] != "run_authorization" or authorization["verdict"] != "PASS":
        raise ValueError("Run authorization is absent")
    bound = [item for item in authorization["input_digests"]
             if (gate.parent / item["path"]).resolve() == FAMILY / "contract.json"]
    if len(bound) != 1:
        raise ValueError("Run authorization must bind the frozen contract")
    bind(FAMILY / "contract.json", bound[0]["sha256"])
    training = public_rows(PANELS / "train.jsonl")
    keys = rows(PANELS / "training_key.jsonl")
    if len(training) != LIMIT or len(keys) != LIMIT or any(k["condition"] != "train" for k in keys):
        raise ValueError("Incomplete training split")
    answers = {k["id"]: {"L": 0, "T": 1}[k["label"]] for k in keys}
    if set(answers) != {row["id"] for row in training}:
        raise ValueError("Training key mismatch")
    target = phase_dir(out, "fit")
    devices = models()
    receipts = []
    for index, row in enumerate(training):
        pixels = tuple(map(int, row["pixels"]))
        turns = {}
        for arm, device in devices.items():
            action = device.predict(pixels)
            # The environment knows the convention. Only the bit goes back.
            target_bit = answers[row["id"]] ^ int(arm.endswith("-opposite"))
            correct = action == target_bit
            device.learn(pixels, action, correct)
            turns[arm] = {"guess": action, "correct": correct,
                          "after_sha256": sha256(pack(device.export_memory())).hexdigest()}
        receipts.append({"id": row["id"], "presentation": index + 1, "arms": turns})
    write_rows(target / "receipts.jsonl", receipts)
    for arm, device in devices.items():
        write_json(target / (arm + ".json"), device.export_memory())
    files = ["receipts.jsonl", *(arm + ".json" for arm in devices)]
    release(target, files, {"authorization": gate, "train": PANELS / "train.jsonl",
                            "training_key": PANELS / "training_key.jsonl"},
            start, {"presentations_per_arm": len(training), "arms": len(devices), "epochs": 1})


def arm_guesses(device, pixels):
    return [device.predict(p) for p in pixels]


def intervene(fit, law, pixels):
    memories = {v: read_json(fit / f"{law}-{v}.json") for v in VERSIONS}
    guesses = {}
    for version, other in (("ordinary", "opposite"), ("opposite", "ordinary")):
        receiver = KnotLearner.from_memory(memories[version])
        before = receiver.export_memory()
        guesses[version] = arm_guesses(receiver, pixels)
        receiver.restore_memory(before)
        guesses["sham-" + version] = arm_guesses(receiver, pixels)
        receiver.restore_memory(memories[other])
        guesses["donor-into-" + version] = arm_guesses(receiver, pixels)
        receiver.clear_memory()
        guesses["clear-" + version] = arm_guesses(receiver, pixels)
        receiver.restore_memory(before)
        guesses["restore-" + version] = arm_guesses(receiver, pixels)
        if receiver.export_memory() != before:
            raise ValueError("Incomplete memory restoration")
    return guesses


def predict(out):
    start = monotonic()
    verify_sources("panel/queries.jsonl")
    fit = out / "fit"
    check_release(fit)
    queries = public_rows(PANELS / "queries.jsonl")
    pixels = [tuple(map(int, row["pixels"])) for row in queries]
    target = phase_dir(out, "blind")
    armed = {}
    for law in LAWS:
        for variant, guesses in intervene(fit, law, pixels).items():
            armed[f"{law}-{variant}"] = guesses
    for v in VERSIONS:
        twin = IntegerMeans(read_json(fit / f"integer-{v}.json"))
        armed["integer-" + v] = arm_guesses(twin, pixels)
    baseline = NearestBitmap(read_json(fit / "nearest-ordinary.json"))
    armed["nearest-ordinary"] = arm_guesses(baseline, pixels)
    trace_reader = KnotLearner.from_memory(read_json(fit / "parity-ordinary.json"))
    records = [{"id": row["id"], "actions": {arm: values[i] for arm, values in armed.items()},
                "reading": trace_reader.explain(pixels[i])} for i, row in enumerate(queries)]
    write_rows(target / "predictions.jsonl", records)
    release(target, ["predictions.jsonl"], {"fit_release": fit / "release.json",
                                           "queries": PANELS / "queries.jsonl"}, start,
            {"images": len(pixels), "issued_arms_per_image": len(armed), "rewards": 0})


def summarize_keys(keys, predictions, out):
    score_table = defaultdict(lambda: defaultdict(Counter))
    novelty = defaultdict(Counter)
    unique = defaultdict(set)
    controls = defaultdict(Counter)
    by_pose = defaultdict(Counter)
    chosen = {}
    nearest_errors = {}
    train_examples = read_json(out / "fit/nearest-ordinary.json")
    seen = defaultdict(set)
    for raw, action in train_examples:
        seen[tuple(histogram(tuple(map(int, raw))))].add("LT"[action])
    for row in sorted(predictions, key=lambda p: p["id"]):
        key = keys[row["id"]]
        actual, cell = key["label"], key["condition"]
        readings = row["reading"]
        hist = tuple(readings["counts"])
        label_set = seen.get(hist, set())
        overlaps = "new" if not label_set else ("same" if label_set == {actual} else "opposite_or_mixed")
        unique[cell].add(hist)
        novelty[cell][overlaps] += 1
        actions = row["actions"]
        truth = int(actual == "T")
        for arm, guess in actions.items():
            # A transplant is scored in the unchanged recipient's convention.
            wanted = truth ^ int(arm.endswith("-opposite"))
            stat = score_table[cell][arm]
            stat[actual + "_total"] += 1
            stat[actual + "_correct"] += int(guess == wanted)
        normal = actions["parity-ordinary"]
        correct = normal == truth
        by_pose[f"{cell}/{key['style']}/q{key['q']}/{actual}"]["total"] += 1
        by_pose[f"{cell}/{key['style']}/q{key['q']}/{actual}"]["correct"] += int(correct)
        selection = f"{cell}/{actual}/" + ("correct" if correct else "error")
        if selection not in chosen:
            chosen[selection] = {"id": row["id"], **key, "guess": "LT"[normal],
                                  "nearest_guess": "LT"[actions["nearest-ordinary"]],
                                  "histogram_overlap": overlaps, "reading": readings}
        if actions["nearest-ordinary"] != truth and cell not in nearest_errors:
            nearest_errors[cell] = {"id": row["id"], **key, "guess": "LT"[normal],
                                    "nearest_guess": "LT"[actions["nearest-ordinary"]]}
        for law in LAWS:
            a, b = (actions[f"{law}-{v}"] for v in VERSIONS)
            counts = controls[law]
            counts["images"] += 1
            counts["ordinary_opposite_disagreements"] += int(a != b)
            counts["both_donor_reads_match"] += int(actions[f"{law}-donor-into-ordinary"] == b and
                                                      actions[f"{law}-donor-into-opposite"] == a)
            counts["both_reversed"] += int(a != b and actions[f"{law}-donor-into-ordinary"] != a and
                                           actions[f"{law}-donor-into-opposite"] != b)
            counts["both_shams_unchanged"] += int(actions[f"{law}-sham-ordinary"] == a and
                                                   actions[f"{law}-sham-opposite"] == b)
            counts["both_restored"] += int(actions[f"{law}-restore-ordinary"] == a and
                                           actions[f"{law}-restore-opposite"] == b)
            counts["both_clear_to_zero"] += int(actions[f"{law}-clear-ordinary"] ==
                                                 actions[f"{law}-clear-opposite"] == 0)
            counts["both_match_conventional_twin"] += int(a == actions["integer-ordinary"] and
                                                           b == actions["integer-opposite"])
        left, right = readings["actions"]
        tie = (left["distance_numerator"] * right["distance_denominator"] ==
               right["distance_numerator"] * left["distance_denominator"])
        novelty[cell]["ties"] += int(tie)
    return {"scores": score_table, "interventions": controls,
            "histogram_overlap": {c: {**novelty[c], "distinct": len(unique[c])} for c in CONDITIONS},
            "distinct_training_histograms": len(seen), "training_histograms_cross_label": sum(
                len(v) > 1 for v in seen.values()), "scores_by_style_q_class": by_pose,
            "representatives": chosen, "nearest_errors": nearest_errors}


def score(out):
    start = monotonic()
    verify_sources("panel/scorer_key.jsonl", "panel/queries.jsonl")
    fit, blind = out / "fit", out / "blind"
    check_release(fit)
    locked = check_release(blind)
    bind(fit / "release.json", locked["inputs"]["fit_release"])
    predictions = rows(blind / "predictions.jsonl")
    query_rows = public_rows(PANELS / "queries.jsonl")
    query_pixels = {row["id"]: row["pixels"] for row in query_rows}
    raw_keys = rows(PANELS / "scorer_key.jsonl")
    keys = {k["id"]: k for k in raw_keys}
    if (len(predictions) != len(keys) or len(keys) != len(raw_keys)
            or list(query_pixels) != [p["id"] for p in predictions] or set(keys) != set(query_pixels)
            or {k["condition"] for k in raw_keys} != set(CONDITIONS)):
        raise ValueError("Scoring roster does not match frozen predictions")
    target = phase_dir(out, "scored")
    summary = summarize_keys(keys, predictions, out)
    for rep in (*summary["representatives"].values(), *summary["nearest_errors"].values()):
        raw = query_pixels[rep["id"]]
        rep["bitmap_rows"] = [raw[i:i + 8] for i in range(0, 64, 8)]
    write_json(target / "scores.json", summary)
    release(target, ["scores.json"], {"blind_release": blind / "release.json",
            "scorer_key": PANELS / "scorer_key.jsonl"}, start,
            {"images_joined": len(keys), "weighting": "one per distinct bitmap per cell"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("train", "predict", "score"))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    {"train": train, "predict": predict, "score": score}[args.phase](args.out)

