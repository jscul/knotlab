"""Run the disclosed pair, earn the trees, issue blind decisions, then open the scorer."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import resource
import sys
from time import monotonic


FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
TICKET = FAMILY.parent.name
ART = FAMILY.name.split("_")[0]
RECORD = ROOT / "research" / TICKET
ARCHIVE = ROOT / "artifacts" / TICKET / FAMILY.name
ANCHORS = RECORD / "phase_anchors.jsonl"
PANEL = FAMILY / "panel"
PRIOR_ID = "VARIED-LETTER-DRAWINGS-20261122-001"
PRIOR = ROOT / "experiments" / PRIOR_ID / (PRIOR_ID + "-E001_drawings")
PRIOR_FIT = ROOT / "artifacts" / PRIOR_ID / PRIOR.name / "fit"
TOOLS = PRIOR / "study.py"
if sha256(TOOLS.read_bytes()).hexdigest() != "3da5d429ac99d5e7c89698142eb420b8d05efb50b305022305fef7706fe75aee":
    raise ValueError("Changed predecessor's serialization and validation tools")
spec = spec_from_file_location("relative_read_phase_tools", TOOLS)
io = module_from_spec(spec)
spec.loader.exec_module(io)

ARMS = ("position", "window_tree", "window_group")
LAWS = ("parity", "nae")
BACKENDS = (*LAWS, "integer")
SCHEDULES = ("ordinary", "opposite")
FITS = [f"{arm}-{backend}-{schedule}" for arm in ARMS for backend in BACKENDS for schedule in SCHEDULES]
STAGES = ("sense", "fit", "pair", "blind", "scored")
FILES = {"sense": {"sensors.json"}, "fit": {"receipts.jsonl", "diagnostics.json", *(n + ".json" for n in FITS)},
         "pair": {"predictions.jsonl", "interventions.json"}, "blind": {"predictions.jsonl", "interventions.json"},
         "scored": {"scores.json"}}


def preflight():
    path, proposal = FAMILY / "contract.json", FAMILY / "proposed_contract.json"
    r0 = RECORD / "design_review/red_team_report.json"
    r1 = RECORD / "audit/R1/red_team_report.json"
    contract = io.load(path)
    if (contract["schema_version"], contract["status"], contract["ticket"], contract["artifact_id"]) != (1, "Frozen", TICKET, ART):
        raise ValueError("Wrong research contract")
    candidate = json.loads(io.checked_bytes(proposal, contract["approved_candidate_sha256"]))
    io.checked_bytes(r0, contract["design_review_sha256"])
    stripped = {k: v for k, v in contract.items() if k not in ("approved_candidate_sha256", "design_review_sha256", "frozen_utc")}
    if candidate != {**stripped, "status": "Proposed"}:
        raise ValueError("Detached freeze changed the scientific design")
    io.check_binding(r0, io.review(r0, "R0", "contract_freeze", ART), proposal)
    approval = io.review(r1, "R1", "run_authorization", ART)
    for bound in (path, proposal, r0):
        io.check_binding(r1, approval, bound)
    for code in (TOOLS, FAMILY / "study.py", io.PRIOR_HOLDING, io.PRIOR_GROUPS / "learner.py",
                 io.PRIOR_GROUPS / "ordinary.py", FAMILY / "reader.py", FAMILY / "ordinary.py",
                 FAMILY / "scoring.py", FAMILY / "identity.json"):
        io.source_bytes(contract, code)
    return contract, r1


def implementations(contract):
    tree = io.sealed_module(contract, FAMILY / "reader.py", "relative_knot_tree")
    ordinary = io.sealed_module(contract, FAMILY / "ordinary.py", "relative_ordinary_tree")
    group, numeric_group, _ = io.models(contract)
    return tree, ordinary, group, numeric_group


def blank(modules, arm, backend):
    tree, ordinary, group, numeric_group = modules
    if arm == "window_group":
        return numeric_group(training_limit=64) if backend == "integer" else group(backend, training_limit=64)
    sensor = "position" if arm == "position" else "window"
    return ordinary.IntegerTree(sensor) if backend == "integer" else tree.KnotTree(backend, sensor)


def parents(out, stage, contract, authority):
    previous = STAGES[:STAGES.index(stage)]
    upstream = {name: io.digest(out / name / "release.json") for name in previous}
    sources = {"sense": ("diagnostic",), "fit": ("train", "training_key"), "pair": ("diagnostic",),
               "blind": ("queries",), "scored": ("scorer_key",)}[stage]
    return {**upstream, "run_authorization": io.digest(authority), **{
        name: io.source_digest(contract, PANEL / (name + ".jsonl")) for name in sources}}


def check_upstream(out, stage, contract, authority):
    for name in STAGES[:STAGES.index(stage)]:
        folder = out / name
        seal = io.load(folder / "release.json")
        if (seal["parents"] != parents(out, name, contract, authority)
                or seal["contract"] != io.digest(FAMILY / "contract.json")
                or set(seal["files"]) != FILES[name]
                or {p.name for p in folder.iterdir()} != FILES[name] | {"release.json"}):
            raise ValueError(f"Invalid release chain at {name}")
        for file, expected in seal["files"].items():
            io.checked_bytes(folder / file, expected)


def check_anchors(out, stage, anchors):
    expected = {"sense": [], "fit": [], "pair": ["fit"], "blind": ["fit"], "scored": ["fit", "blind"]}[stage]
    rows = io.json_lines(anchors.read_bytes()) if anchors.exists() else []
    if [row["stage"] for row in rows] != expected:
        raise ValueError(f"Wrong external commitments for {stage}")
    for row in rows:
        name = row["stage"]
        next_stage = {"fit": "pair", "blind": "scored"}[name]
        if set(row) != {"stage", "sha256", "next_stage_absent", "utc"} or row["next_stage_absent"] != next_stage:
            raise ValueError(f"Malformed {name} commitment")
        seal = json.loads(io.checked_bytes(out / name / "release.json", row["sha256"]))
        a = datetime.fromisoformat(row["utc"])
        released = datetime.fromisoformat(seal["utc"])
        if a.tzinfo is None or released.tzinfo is None or not released <= a <= datetime.now(timezone.utc):
            raise ValueError("Invalid release commitment time")
        successor = out / next_stage / "release.json"
        if successor.is_file() and a > datetime.fromisoformat(io.load(successor)["utc"]):
            raise ValueError("Late external commitment")


def public(contract, name):
    return io.public_rows(io.source_bytes(contract, PANEL / (name + ".jsonl")))


def bits(row):
    return tuple(map(int, row["pixels"]))


def sense(contract, target, modules):
    rows = public(contract, "diagnostic")
    if len(rows) != 2:
        raise ValueError("Expected both disclosed inputs")
    result = {}
    for sensor in ("position", "window"):
        vectors = [modules[0].features(bits(row), sensor) for row in rows]
        numeric = modules[1].position_features if sensor == "position" else modules[1].window_features
        if any(list(vec) != numeric(bits(row)) for row, vec in zip(rows, vectors, strict=True)):
            raise ValueError(f"Mismatch between implementations of {sensor}")
        result[sensor] = {"equal": vectors[0] == vectors[1], "differing_indices": [
            i for i, (x, y) in enumerate(zip(*vectors, strict=True)) if x != y],
            "vectors": {row["id"]: vec for row, vec in zip(rows, vectors, strict=True)}}
    io.save(target / "sensors.json", result)
    return {"public_inputs": 2, "learned_states": 0, "training_updates": 0}


def train(contract, target, modules):
    rows = public(contract, "train")
    keys = io.json_lines(io.source_bytes(contract, PANEL / "training_key.jsonl"))
    if (len(rows) != 64 or len(keys) != 64 or Counter((k["label"], k["q"]) for k in keys) !=
            Counter({(label, q): 16 for label in "LT" for q in (0, 1)})):
        raise ValueError("Invalid teaching budget or orientations")
    devices = {name: blank(modules, *name.split("-")[:2]) for name in FITS}
    prefix = {n: io.memory_digest(d.export_memory()) for n, d in devices.items() if "-integer-" not in n}
    receipts = []
    for slot, (row, key) in enumerate(zip(rows, keys, strict=True)):
        if set(key) != io.TRAIN_KEY_FIELDS or key["id"] != row["id"] or key["slot"] != slot or key["condition"] != "train":
            raise ValueError("Misaligned teaching key")
        feedback = {}
        pixels = bits(row)
        for name, device in devices.items():
            target_bit = "LT".index(key["label"]) ^ int(name.endswith("-opposite"))
            guess = device.predict(pixels)
            correct = guess == target_bit
            device.learn(pixels, guess, correct)
            step = {"guess": guess, "correct": correct}
            if name in prefix:
                after = io.memory_digest(device.export_memory())
                step.update(before_sha256=prefix[name], after_sha256=after)
                prefix[name] = after
            feedback[name] = step
        for schedule in SCHEDULES:
            same = {(step["guess"], step["correct"]) for n, step in feedback.items() if n.endswith("-" + schedule)}
            if len(same) != 1:
                raise ValueError("Acquisition guesses and rewards differ between compared readers")
        receipts.append({"slot": slot, "id": row["id"], "readers": feedback})
    io.save_lines(target / "receipts.jsonl", receipts)
    diagnostics = {}
    for name, device in devices.items():
        reading = device.finalize()
        state = device.export_memory()
        diagnostics[name] = reading if reading is not None else device.selection()
        if name.startswith("window_group-"):
            old = PRIOR_FIT / (name.replace("window_group-", "varied-") + ".json")
            if state != json.loads(io.source_bytes(contract, old)):
                raise ValueError(f"Archived reader failed to reproduce its prior fitted state at {name}")
        io.save(target / (name + ".json"), state)
    io.save(target / "diagnostics.json", diagnostics)
    return {"models": len(devices), "presentations_per_model": 64, "reward_events": 64 * len(devices),
            "archived_state_matches": 6}


def issue(contract, target, modules):
    out, pair = target.parent, target.name == "pair"
    rows = public(contract, "diagnostic" if pair else "queries")
    train_ids = {r["id"] for r in io.json_lines((out / "fit/receipts.jsonl").read_bytes())}
    if not pair:
        train_ids.update(r["id"] for r in io.json_lines((out / "pair/predictions.jsonl").read_bytes()))
    if len(rows) != (2 if pair else contract["blind_images"]) or train_ids.intersection(r["id"] for r in rows):
        raise ValueError("Unexpected or overlapping query roster")
    xs = [bits(row) for row in rows]
    predictions = [{"id": row["id"], "actions": {}, "traces": {}} for row in rows]
    interventions = {}
    for arm in ARMS:
        for backend in BACKENDS:
            base = f"{arm}-{backend}"
            states = {s: io.load(out / "fit" / f"{base}-{s}.json") for s in SCHEDULES}
            constructor = type(blank(modules, arm, backend))
            recipients = {s: constructor.from_memory(states[s]) for s in SCHEDULES}

            def read(condition, recipient, donor):
                model = recipients[recipient]
                name = f"{base}-{condition}"
                expected = (states[donor] if donor in states else blank(modules, arm, backend).export_memory())
                if model.export_memory() != expected:
                    raise ValueError(f"Unexpected words before {name}")
                interventions[name] = {"recipient": f"{base}-{recipient}",
                                       "source": f"{base}-{donor}" if donor in states else "neutral",
                                       "sha256": io.memory_digest(expected)}
                for pixels, result in zip(xs, predictions, strict=True):
                    if backend == "parity" and condition == "ordinary":
                        trace = model.explain(pixels, detail=True) if arm == "window_group" else model.explain(pixels)
                        result["traces"][arm] = trace
                        result["actions"][name] = trace["guess"]
                    else:
                        result["actions"][name] = model.predict(pixels)
                if model.export_memory() != expected:
                    raise ValueError(f"A read changed the words at {name}")

            for schedule in SCHEDULES:
                read(schedule, schedule, schedule)
            if backend != "integer":
                ordinary, opposite = recipients["ordinary"], recipients["opposite"]
                ordinary.restore_memory(states["ordinary"])
                read("sham", "ordinary", "ordinary")
                ordinary.restore_memory(states["opposite"])
                read("swapped-ordinary", "ordinary", "opposite")
                opposite.restore_memory(states["ordinary"])
                read("swapped-opposite", "opposite", "ordinary")
                if ordinary.clear_memory() != states["opposite"]:
                    raise ValueError("Clear returned unexpected words")
                read("clear", "ordinary", "neutral")
                ordinary.restore_memory(states["ordinary"])
                read("restored", "ordinary", "ordinary")
    io.save_lines(target / "predictions.jsonl", predictions)
    io.save(target / "interventions.json", interventions)
    return {"images": len(rows), "action_columns": len(interventions), "reward_events": 0}


def score(contract, target):
    rows = io.json_lines((target.parent / "blind/predictions.jsonl").read_bytes())
    queries = public(contract, "queries")
    if len(rows) != contract["blind_images"] or [r["id"] for r in rows] != [r["id"] for r in queries]:
        raise ValueError("Blind roster was reordered or incomplete")
    keys = io.json_lines(io.source_bytes(contract, PANEL / "scorer_key.jsonl"))
    scorer = io.sealed_module(contract, FAMILY / "scoring.py", "relative_decision_scorer")
    io.save(target / "scores.json", scorer.summarize(rows, keys))
    return {"images": len(rows), "action_columns": len(rows[0]["actions"])}


def run(stage, out, anchors):
    start = monotonic()
    contract, authority = preflight()
    check_upstream(out, stage, contract, authority)
    check_anchors(out, stage, anchors)
    if any((out / s).exists() for s in STAGES[STAGES.index(stage):]):
        raise ValueError("This phase or a later phase already exists")
    target = io.open_phase(out, stage)
    if stage == "scored":
        observations = score(contract, target)
    else:
        action = {"sense": sense, "fit": train, "pair": issue, "blind": issue}[stage]
        observations = action(contract, target, implementations(contract))
    files = {p.name: io.digest(p) for p in sorted(target.iterdir())}
    if set(files) != FILES[stage]:
        raise ValueError(f"Incomplete {stage} file roster")
    io.save(target / "release.json", {"files": files, "parents": parents(out, stage, contract, authority),
            "contract": io.digest(FAMILY / "contract.json"), "observations": observations,
            "seconds": round(monotonic() - start, 6), "utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version.split()[0], "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("phase", choices=("sense", "train", "diagnose", "predict", "score"))
    cli.add_argument("--out", type=Path, default=ARCHIVE)
    cli.add_argument("--anchors", type=Path, default=ANCHORS)
    args = cli.parse_args()
    run(dict(sense="sense", train="fit", diagnose="pair", predict="blind", score="scored")[args.phase],
        args.out, args.anchors)
