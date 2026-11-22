"""Fit the paired drawing arms, issue blind actions, then score the sealed predictions."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import resource
import subprocess
import sys
from time import monotonic


FAMILY = Path(__file__).resolve().parent
TICKET = FAMILY.parent.name
ROOT = FAMILY.parents[2]
RECORD = ROOT / "research" / TICKET
ARCHIVE = ROOT / "artifacts" / TICKET / FAMILY.name
PANEL = FAMILY / "panel"
ANCHORS = RECORD / "phase_anchors.jsonl"
PRIOR_GROUPS = (ROOT / "experiments/LEARNED-PATCH-GROUPS-20261122-001"
                / "LEARNED-PATCH-GROUPS-20261122-001-E001_groups")
PRIOR_HOLDING = (ROOT / "experiments/PIXEL-LETTERS-20261122-001"
                 / "PIXEL-LETTERS-20261122-001-E001_letters" / "learner.py")
REVIEW_VALIDATOR = ROOT / ".codex/skills/red-team-experiment/scripts/validate_red_team_report.py"
ARMS = ("narrow", "varied")
LAWS = ("parity", "nae")
BACKENDS = (*LAWS, "integer")
SCHEDULES = ("ordinary", "opposite")
LIMIT = 64
QUERY_COUNT = 1024
TRAIN_KEY_FIELDS = {"id", "label", "condition", "style", "base_style", "style_stratum",
                    "row", "col", "q", "slot"}
FIT_CHECKPOINTS = {f"{arm}-{backend}-{schedule}.json" for arm in ARMS
                   for backend in BACKENDS for schedule in SCHEDULES}
STAGE_FILES = {
    "fit": {"receipts.jsonl", "diagnostics.json", *FIT_CHECKPOINTS},
    "blind": {"predictions.jsonl", "group_order.json", "interventions.json"},
    "scored": {"scores.json"},
}


def packed(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def memory_digest(memory):
    return sha256(packed(memory)).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def json_lines(raw):
    return [json.loads(line) for line in raw.splitlines()]


def save(path, obj):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, sort_keys=True, indent=2)
        stream.write("\n")


def save_lines(path, rows):
    with path.open("xb") as stream:
        for row in rows:
            stream.write(packed(row) + b"\n")


def checked_bytes(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f"Content seal mismatch for {path}")
    return raw


def source_digest(contract, path):
    return contract["source_sha256"][str(path.relative_to(ROOT))]


def source_bytes(contract, path):
    return checked_bytes(path, source_digest(contract, path))


def sealed_module(contract, path, name):
    raw = source_bytes(contract, path)
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def models(contract):
    learner = sealed_module(contract, PRIOR_GROUPS / "learner.py", "varied_drawings_frozen_learner")
    ordinary = sealed_module(contract, PRIOR_GROUPS / "ordinary.py", "varied_drawings_frozen_ordinary")
    return learner.KnotLearner, ordinary.NumericGroups, learner.PARTITION_COUNT


def review(report_path, tier, gate, experiment):
    report = load(report_path)
    if (report["experiment_id"], report["tier"], report["gate"], report["verdict"]) != (
            experiment, tier, gate, "PASS") or not report["attack_plan_frozen_before_results"]:
        raise ValueError(f"Missing passing {tier} {gate} for {experiment}")
    # Validate report structure without verifying source files out of phase.
    result = subprocess.run([sys.executable, "-B", str(REVIEW_VALIDATOR), str(report_path),
                             "--minimum-tier", tier, "--gate", gate], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"Invalid {tier} report for {experiment}: {result.stderr.strip()}")
    return report


def check_binding(report_path, report, bound_path):
    exact = [item for item in report["input_digests"]
             if (report_path.parent / item["path"]).resolve() == bound_path.resolve()]
    if len(exact) != 1:
        raise ValueError(f"Expected exactly one review binding for {bound_path}")
    checked_bytes(bound_path, exact[0]["sha256"])


def preflight():
    path = FAMILY / "contract.json"
    contract = load(path)
    if (contract["schema_version"], contract["status"], contract["ticket"], contract["artifact_id"]) != (
            1, "Frozen", TICKET, FAMILY.name.split("_")[0]):
        raise ValueError("Execution requires this family's frozen contract")
    proposal = FAMILY / "proposed_contract.json"
    r0 = RECORD / "design_review/red_team_report.json"
    r1 = RECORD / "audit/R1/red_team_report.json"
    reviewed = json.loads(checked_bytes(proposal, contract["approved_candidate_sha256"]))
    checked_bytes(r0, contract["design_review_sha256"])
    freeze_fields = {"approved_candidate_sha256", "design_review_sha256", "frozen_utc", "status"}
    if reviewed != {**{key: value for key, value in contract.items() if key not in freeze_fields},
                    "status": "Proposed"}:
        raise ValueError("Scientific contract differs from the reviewed proposal")
    check_binding(r0, review(r0, "R0", "contract_freeze", contract["artifact_id"]), proposal)
    approval = review(r1, "R1", "run_authorization", contract["artifact_id"])
    for bound in (path, proposal, r0):
        check_binding(r1, approval, bound)
    for source in (PRIOR_HOLDING, PRIOR_GROUPS / "learner.py", PRIOR_GROUPS / "ordinary.py",
                   FAMILY / "identity.json", FAMILY / "study.py", FAMILY / "scoring.py"):
        source_bytes(contract, source)
    return contract, r1


def open_phase(out, name):
    target = out / name
    target.mkdir(exist_ok=False, parents=True)
    return target


def release(target, parents, start, observations):
    files = {path.name: digest(path) for path in sorted(target.iterdir())}
    if files.keys() != STAGE_FILES[target.name]:
        raise ValueError(f"Incomplete file roster for {target.name} release")
    save(target / "release.json", {
        "files": files,
        "parents": parents,
        "contract": digest(FAMILY / "contract.json"),
        "observations": observations,
        "utc": datetime.now(timezone.utc).isoformat(),
        "seconds": round(monotonic() - start, 6),
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python": sys.version.split()[0],
    })


def check_release(target):
    obj = load(target / "release.json")
    checked_bytes(FAMILY / "contract.json", obj["contract"])
    expected = STAGE_FILES[target.name]
    if obj["files"].keys() != expected or {path.name for path in target.iterdir()} != {*expected, "release.json"}:
        raise ValueError(f"Incomplete or unexpected file roster for {target.name}")
    for name, hash_value in obj["files"].items():
        checked_bytes(target / name, hash_value)
    return obj


def check_anchors(out, through, anchors=ANCHORS):
    stages = ("fit",) if through == "fit" else ("fit", "blind")
    rows = json_lines(anchors.read_bytes())
    if [row["stage"] for row in rows] != list(stages):
        raise ValueError(f"Expected external anchors through {through}")
    previous = None
    successors = {"fit": "blind", "blind": "scored"}
    for stage, row in zip(stages, rows, strict=True):
        if set(row) != {"stage", "sha256", "next_stage_absent", "utc"} or row["next_stage_absent"] != successors[stage]:
            raise ValueError(f"Malformed external {stage} anchor")
        raw = checked_bytes(out / stage / "release.json", row["sha256"])
        released = datetime.fromisoformat(json.loads(raw)["utc"])
        anchored = datetime.fromisoformat(row["utc"])
        if (released.tzinfo is None or anchored.tzinfo is None or released > anchored
                or (previous is not None and previous > released)):
            raise ValueError("Phase anchors are out of chronological order")
        previous = anchored


def public_rows(raw):
    data = json_lines(raw)
    seen = set()
    for row in data:
        if type(row) is not dict or set(row) != {"id", "pixels"}:
            raise ValueError("Public row has undeclared fields")
        pixels = row["pixels"]
        if type(pixels) is not str or len(pixels) != 64 or set(pixels) - {"0", "1"}:
            raise ValueError("Invalid row-major 64-bit input")
        if row["id"] != sha256(pixels.encode("ascii")).hexdigest() or row["id"] in seen:
            raise ValueError("Public row identity does not match a distinct bitmap")
        seen.add(row["id"])
    return data


def training_source_paths():
    return [PANEL / f"{kind}_{arm}.jsonl" for arm in ARMS for kind in ("train", "training_key")]


def training_data(contract):
    bank = {}
    roster = Counter({(label, turn): 16 for label in "LT" for turn in (0, 1)})
    for arm in ARMS:
        rows = public_rows(source_bytes(contract, PANEL / f"train_{arm}.jsonl"))
        keys = json_lines(source_bytes(contract, PANEL / f"training_key_{arm}.jsonl"))
        if len(rows) != LIMIT or len(keys) != LIMIT:
            raise ValueError(f"Expected 64 acquisition slots in {arm}")
        for index, (row, key) in enumerate(zip(rows, keys, strict=True)):
            if (set(key) != TRAIN_KEY_FIELDS or key["id"] != row["id"] or type(key["slot"]) is not int
                    or key["slot"] != index or key["condition"] != "train" or type(key["q"]) is not int):
                raise ValueError(f"Invalid teaching row for {arm} slot {index}")
        if Counter((key["label"], key["q"]) for key in keys) != roster:
            raise ValueError(f"Unbalanced class or turn roster in {arm}")
        bank[arm] = list(zip(rows, keys, strict=True))
    matched = ("slot", "label", "q", "row", "col")
    for (_, left), (_, right) in zip(*(bank[arm] for arm in ARMS), strict=True):
        if any(left[field] != right[field] for field in matched):
            raise ValueError("Acquisition arms are not matched by slot, class, turn and position")
    ids = [{row["id"] for row, _ in bank[arm]} for arm in ARMS]
    if len(ids[0] & ids[1]) != 16:
        raise ValueError("Expected exactly 16 shared training bitmaps")
    return bank


def fit_parents(contract, authorization):
    return {"run_authorization": digest(authorization), **{
        path.stem: source_digest(contract, path) for path in training_source_paths()}}


def train(out):
    start = monotonic()
    contract, authority = preflight()
    target = open_phase(out, "fit")
    bank = training_data(contract)
    knot, numeric, _ = models(contract)
    devices = {f"{arm}-{backend}-{schedule}": (
        numeric(training_limit=LIMIT) if backend == "integer" else knot(backend, training_limit=LIMIT))
        for arm in ARMS for backend in BACKENDS for schedule in SCHEDULES}
    prefixes = {name: memory_digest(device.export_memory()) for name, device in devices.items()
                if "-integer-" not in name}
    receipts = []
    for index in range(LIMIT):
        slot_receipts = {}
        for arm in ARMS:
            row, teacher = bank[arm][index]
            pixels = tuple(map(int, row["pixels"]))
            earned = "LT".index(teacher["label"])
            readings = {}
            for backend in BACKENDS:
                for schedule in SCHEDULES:
                    name = f"{arm}-{backend}-{schedule}"
                    device = devices[name]
                    guess = device.predict(pixels)
                    correct = guess == (earned if schedule == "ordinary" else 1 - earned)
                    device.learn(pixels, guess, correct)
                    receipt = {"guess": guess, "correct": correct}
                    if name in prefixes:
                        after = memory_digest(device.export_memory())
                        receipt.update(before_sha256=prefixes[name], after_sha256=after)
                        prefixes[name] = after
                    readings[name] = receipt
            slot_receipts[arm] = readings
            receipts.append({"arm": arm, "slot": teacher["slot"], "presentation": index + 1,
                             "id": row["id"], "arms": readings})
        for backend in BACKENDS:
            for schedule in SCHEDULES:
                left, right = (slot_receipts[arm][f"{arm}-{backend}-{schedule}"] for arm in ARMS)
                if (left["guess"], left["correct"]) != (right["guess"], right["correct"]):
                    save_lines(target / "receipts.jsonl", receipts)
                    raise ValueError("Matched arms received different action or correctness prefixes")

    save_lines(target / "receipts.jsonl", receipts)
    diagnostics = {}
    for name, device in devices.items():
        audit_read = device.finalize()
        diagnostics[name] = audit_read if audit_read is not None else device.selection()
        save(target / f"{name}.json", device.export_memory())
    save(target / "diagnostics.json", diagnostics)
    release(target, fit_parents(contract, authority), start,
            {"presentations_per_arm": LIMIT, "training_arms": len(ARMS), "readers": len(devices),
             "updates": LIMIT * len(devices), "epochs": 1, "matched_receipt_prefixes": True})


def check_fit(out, contract, authority):
    fit = check_release(out / "fit")
    if fit["parents"] != fit_parents(contract, authority):
        raise ValueError("Fit does not bind this authorization and both acquisition banks")
    return fit


def frozen_checkpoint(fit, name, fit_release):
    file_name = f"{name}.json"
    return json.loads(checked_bytes(fit / file_name, fit_release["files"][file_name]))


def record_actions(xs, arm, law, knot, checkpoints, partition_count, actions, details, interventions, mask_order):
    name = f"{arm}-{law}"
    other = next(candidate for candidate in ARMS if candidate != arm)
    original, reversed_fit = (checkpoints[f"{name}-{mode}"] for mode in SCHEDULES)
    cross_name = f"{other}-{law}-ordinary"
    cross = checkpoints[cross_name]
    ordinary_recipient = knot.from_memory(original)
    opposite_recipient = knot.from_memory(reversed_fit)
    ordinary_selection = ordinary_recipient.selection()
    if law == "parity":
        mask_order[arm] = ordinary_selection["masks"]

    def read(condition, recipient, expected, source, *, opposite=False):
        key = f"{name}-{condition}"
        held = recipient.export_memory()
        if held != expected:
            raise ValueError(f"Physical checkpoint differs at {key}")
        recipient_name = f"{name}-{'opposite' if opposite else 'ordinary'}"
        interventions[key] = {"recipient": recipient_name, "source": source, "sha256": memory_digest(held)}
        if condition == "ordinary" and law == "parity":
            details[arm] = [recipient.explain(pixels, detail=True) for pixels in xs]
            actions[key] = [row["guess"] for row in details[arm]]
        else:
            actions[key] = [recipient.predict(pixels) for pixels in xs]
        if recipient.export_memory() != held:
            raise ValueError(f"Blind reads changed the checkpoint at {key}")

    read("ordinary", ordinary_recipient, original, f"{name}-ordinary")
    read("opposite", opposite_recipient, reversed_fit, f"{name}-opposite", opposite=True)
    ordinary_recipient.restore_memory(original)
    read("sham-ordinary", ordinary_recipient, original, f"{name}-ordinary")
    ordinary_recipient.restore_memory(reversed_fit)
    read("swapped-ordinary", ordinary_recipient, reversed_fit, f"{name}-opposite")
    opposite_recipient.restore_memory(original)
    read("swapped-opposite", opposite_recipient, original, f"{name}-ordinary", opposite=True)
    if ordinary_recipient.clear_memory() != reversed_fit:
        raise ValueError("Clear did not return the prior physical words")
    neutral = knot(law, training_limit=LIMIT).export_memory()
    read("clear-ordinary", ordinary_recipient, neutral, "neutral")
    ordinary_recipient.restore_memory(original)
    read("restored-ordinary", ordinary_recipient, original, f"{name}-ordinary")

    last_flags = 2 * partition_count  # each holding takes two hexadecimal characters
    ordinary_recipient.erase_selection()
    erased = {**original, "words": original["words"][:-last_flags] + neutral["words"][-last_flags:]}
    read("erase-ordinary", ordinary_recipient, erased, "recipient with neutral flags")
    ordinary_recipient.restore_memory(cross)
    cross_selection = ordinary_recipient.selection()
    read("cross-ordinary", ordinary_recipient, cross, cross_name)
    hybrid = {**original, "words": original["words"][:-last_flags] + cross["words"][-last_flags:]}
    ordinary_recipient.restore_memory(hybrid)
    hybrid_selection = ordinary_recipient.selection()
    if (hybrid_selection["masks"] != cross_selection["masks"] or
            any(hybrid_selection[field] != ordinary_selection[field] for field in ("class_counts", "class_totals"))):
        raise ValueError("Membership exchange changed class calibration or lost the donor groups")
    read("other-groups-ordinary", ordinary_recipient, hybrid, f"{cross_name} flags only")


def predict(out, *, anchors=ANCHORS):
    start = monotonic()
    contract, authority = preflight()
    fit = out / "fit"
    fit_release = check_fit(out, contract, authority)
    check_anchors(out, "fit", anchors)
    target = open_phase(out, "blind")
    query_path = PANEL / "queries.jsonl"
    queries = public_rows(source_bytes(contract, query_path))
    receipts = json_lines(checked_bytes(fit / "receipts.jsonl", fit_release["files"]["receipts.jsonl"]))
    if len(queries) != QUERY_COUNT or {row["id"] for row in queries} & {row["id"] for row in receipts}:
        raise ValueError("Blind queries have the wrong count or overlap acquisition")
    xs = [tuple(map(int, row["pixels"])) for row in queries]
    knot, numeric, partition_count = models(contract)
    checkpoints = {Path(file_name).stem: frozen_checkpoint(fit, Path(file_name).stem, fit_release)
                   for file_name in sorted(FIT_CHECKPOINTS)}
    actions, details, interventions, mask_order = {}, {}, {}, {}
    for arm in ARMS:
        for law in LAWS:
            record_actions(xs, arm, law, knot, checkpoints, partition_count,
                           actions, details, interventions, mask_order)
        for schedule in SCHEDULES:
            name = f"{arm}-integer-{schedule}"
            twin = numeric.from_memory(checkpoints[name])
            actions[name] = [twin.predict(pixels) for pixels in xs]
            if twin.export_memory() != checkpoints[name]:
                raise ValueError(f"Blind reads changed the integer checkpoint at {name}")
            interventions[name] = {"recipient": name, "source": name, "sha256": memory_digest(checkpoints[name])}
    save(target / "group_order.json", {"law": "parity", "by_arm": mask_order})
    save(target / "interventions.json", interventions)
    save_lines(target / "predictions.jsonl", (
        {"id": query["id"], "actions": {name: vector[index] for name, vector in actions.items()},
         "details": {arm: details[arm][index] for arm in ARMS}}
        for index, query in enumerate(queries)))
    release(target, {"fitted_state_release": digest(fit / "release.json"),
                     "queries": source_digest(contract, query_path)}, start,
            {"images": len(xs), "issued_readers": len(actions), "feedback_events": 0})


def score(out, *, anchors=ANCHORS):
    start = monotonic()
    contract, authority = preflight()
    fit, blind = out / "fit", out / "blind"
    check_fit(out, contract, authority)
    blind_release = check_release(blind)
    if blind_release["parents"] != {"fitted_state_release": digest(fit / "release.json"),
                                     "queries": source_digest(contract, PANEL / "queries.jsonl")}:
        raise ValueError("Blind predictions do not bind this fit and query stream")
    check_anchors(out, "blind", anchors)
    target = open_phase(out, "scored")
    query_raw = source_bytes(contract, PANEL / "queries.jsonl")
    queries = public_rows(query_raw)
    predictions = json_lines(checked_bytes(blind / "predictions.jsonl", blind_release["files"]["predictions.jsonl"]))
    if len(queries) != QUERY_COUNT or [row["id"] for row in predictions] != [row["id"] for row in queries]:
        raise ValueError("Blind decision stream is incomplete or reordered")

    scorer_key = PANEL / "scorer_key.jsonl"
    key = json_lines(source_bytes(contract, scorer_key))
    scorer = sealed_module(contract, FAMILY / "scoring.py", "varied_drawings_scoring")
    summary = scorer.summarize(predictions, key)
    save(target / "scores.json", summary)
    release(target, {"blind_release": digest(blind / "release.json"),
                     "scorer_key": source_digest(contract, scorer_key)}, start,
            {"images": len(predictions), "issued_readers": len(predictions[0]["actions"])})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("train", "predict", "score"))
    parser.add_argument("--out", type=Path, default=ARCHIVE)
    parser.add_argument("--anchors", type=Path, default=ANCHORS)
    args = parser.parse_args()
    if args.phase == "train":
        train(args.out)
    else:
        {"predict": predict, "score": score}[args.phase](args.out, anchors=args.anchors)
