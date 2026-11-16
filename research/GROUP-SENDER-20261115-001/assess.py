"""Bind the training-only fits, then grade physical communication after freeze."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from functools import cache
from pathlib import Path


STUDY = "GROUP-SENDER-20261115-001"
FAMILY = STUDY + "-E001_atomic_switch"
PREDECESSOR = "BIT-DECODER-20261114-001"
PREV_FAMILY = PREDECESSOR + "-E001_atomic_codec"
ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / STUDY
EXPERIMENT = ROOT / "experiments" / STUDY / FAMILY
ORIGINAL = ROOT / "artifacts" / PREDECESSOR / PREV_FAMILY
DEFAULT_OUT = ROOT / "artifacts" / STUDY / FAMILY
sys.path.insert(0, str(EXPERIMENT))

import panels
import proposal
import sender


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def bind(path, value):
    data = canonical(value)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Bound data changed at {path}")
    else:
        with path.open("xb") as stream:
            stream.write(data)


def rosters():
    return {"train": panels.training_panel(), "held": panels.held_panel(),
            "historical": panels.historical_panel()}


def sources(out):
    paths = [EXPERIMENT / n for n in ("sender.py", "job.py", "contract.json")]
    paths += [RESEARCH / n for n in ("proposal.py", "panels.py", "assess.py", "preregistration.md")]
    paths += [ORIGINAL / n for n in ("varied_checkpoint.json", "result.json")]
    paths += [ROOT / "experiments" / PREDECESSOR / PREV_FAMILY / "codec.py",
              ROOT / "research" / PREDECESSOR / "wirings.py"]
    panels_by_split = rosters()
    train_wirings = {canonical(item[1]) for item in panels_by_split["train"]}
    for split in ("held", "historical"):
        if any(canonical(item[1]) in train_wirings for item in panels_by_split[split]):
            raise ValueError("Exact public test wiring occurs in training")
    path = out / "freeze.json"
    stamp = load(path)["utc"] if path.exists() else datetime.now(timezone.utc).isoformat()
    value = {"utc": stamp, "before_fits": True, "files_sha256": {
                 str(p.relative_to(ROOT)): file_hash(p) for p in paths},
             "rosters_sha256": {name: hashlib.sha256(canonical(records)).hexdigest()
                                for name, records in panels_by_split.items()},
             "roster_sizes": {name: len(records) for name, records in panels_by_split.items()}}
    bind(path, value)
    return value


def freeze(out):
    manifest = sources(out) if (out / "freeze.json").exists() else None
    if manifest is None:
        raise ValueError("A pre-fit source binding is required")
    rows = [json.loads(line) for line in (out / "results.jsonl").read_text().splitlines()]
    if len(rows) != 2 or {r["case"] for r in rows} != {"joint", "singleton"}:
        raise ValueError("Both successful training records required")
    hashes = {}
    for row in rows:
        name = row["case"]
        if row["status"] != "ok" or row["result"]["strategy"] != name:
            raise ValueError("A training case is missing or failed")
        assert datetime.fromisoformat(row["finished_at"]) >= datetime.fromisoformat(manifest["utc"])
        assert row["job_sha"] == file_hash(EXPERIMENT / "job.py")
        path = out / (name + ".json")
        bind(path, row["result"]["checkpoint"])
        hashes[name] = file_hash(path)
        assert hashes[name] == row["result"]["checkpoint_sha256"]
        if name == "joint":
            direct = {"trace_checkpoint_sha256": hashes["joint"], "head": row["result"]["direct"]["head"]}
            bind(out / "direct.json", direct)
            hashes["direct"] = file_hash(out / "direct.json")
    value = {"checkpoints": hashes, "source_freeze": file_hash(out / "freeze.json"),
             "training_output": file_hash(out / "results.jsonl")}
    bind(out / "checkpoints.json", value)
    return value


def public_plan(strategy, checkpoint, head, wiring):
    if strategy != "direct":
        return sender.plan(checkpoint, wiring)
    traced = sender.trace_public(checkpoint, wiring)
    mask = proposal.choose_mask(head, traced["support_masks"])
    return sender.plan_from_mask(checkpoint, wiring, mask, traced=traced)


def grammar(wiring, answers):
    supports = [sum(1 << i for i in range(9)
                    if any(v[p] != answers[raw ^ (1 << i)][p] for raw, v in enumerate(answers)))
                for p in range(4)]
    identities = [tuple(sorted(tuple(sorted(g)) for g in question)) for question in wiring]
    widths = []
    for mask in range(16):
        classes = {key for p, key in enumerate(identities) if mask & (1 << p)}
        need = 0
        for key, support in zip(identities, supports):
            if key not in classes:
                need |= support
        widths.append(len(classes) + need.bit_count())
    return supports, widths


def measure(strategy, sender_cp, receiver_cp, head, wiring, meta, ident, answers, semantic):
    # The receiver builds its own plan, exclusively from its copy and public inputs.
    outbound = public_plan(strategy, sender_cp, head, wiring)
    inbound = public_plan(strategy, receiver_cp, head, wiring)
    assert outbound["slots"] == inbound["slots"] and outbound["computed_mask"] == inbound["computed_mask"]
    @cache
    def receive(packet):
        return tuple(sender.receive_plan(receiver_cp, wiring, packet, port, inbound) for port in range(4))
    h = hashlib.sha256()
    width = outbound["width"]
    correct = odd = vectors = 0
    port_counts = [0] * 4
    first_error = None
    for raw, wanted in enumerate(answers):
        packet = tuple(sender.send_plan(sender_cp, wiring, raw, outbound))
        if len(packet) != width or any(type(b) not in (int, bool) or b not in (0, 1) for b in packet):
            raise ValueError("The physical channel emitted uncounted data")
        h.update(bytes((width,)) + bytes(packet))
        got = receive(packet)
        agreement = [a == b for a, b in zip(got, wanted, strict=True)]
        if any(type(b) not in (int, bool) or b not in (0, 1) for b in got):
            raise ValueError("A decoder output is not a bit")
        if first_error is None and not all(agreement):
            first_error = {"raw":raw, "wanted":wanted, "got":got, "packet":packet}
        correct += sum(agreement)
        if raw.bit_count() % 2:
            odd += sum(agreement)
        vectors += all(agreement)
        for port, match in enumerate(agreement):
            port_counts[port] += match
    supports, costs = semantic
    patterns = len(set(answers))
    return {
        "id": ident, "metadata": meta, "input_count": 512,
        "correct_vectors": vectors, "correct_bits": correct, "odd_correct_bits": odd,
        "correct_by_port": port_counts, "first_error": first_error, "width": width,
        "answer_patterns": patterns, "minimum": (patterns - 1).bit_length(),
        "grammar_minimum": min(costs), "mask_widths_by_true_support": costs,
        "physical_sha256": h.hexdigest(), "computed_mask": outbound["computed_mask"],
        "slots": outbound["slots"], "support_masks": list(outbound["support_masks"]),
        "semantic_support_masks": supports, "public_actions": outbound["public_actions"],
    }


def summarize(rows):
    return {
        "wirings":len(rows), "questions":2048*len(rows), "correct_bits":sum(r["correct_bits"] for r in rows),
        "odd_correct_bits":sum(r["odd_correct_bits"] for r in rows),
        "all_correct_wirings":sum(r["correct_bits"]==2048 for r in rows),
        "exact_and_minimum":sum(r["correct_bits"]==2048 and r["width"]==r["minimum"] for r in rows),
        "exact_and_grammar_minimum":sum(r["correct_bits"]==2048 and r["width"]==r["grammar_minimum"] for r in rows),
        "widths":dict(sorted(Counter(r["width"] for r in rows).items())),
    }


def assess(out):
    binding = load(out / "checkpoints.json")
    assert binding["source_freeze"] == file_hash(out / "freeze.json")
    assert binding["training_output"] == file_hash(out / "results.jsonl")
    sources(out)
    for strategy, digest in binding["checkpoints"].items():
        assert digest == file_hash(out / (strategy + ".json"))
    head = load(out / "direct.json")
    assert head["trace_checkpoint_sha256"] == binding["checkpoints"]["joint"]
    policies = {}
    for name in ("singleton", "joint", "direct"):
        path = out / (("joint" if name == "direct" else name) + ".json")
        policies[name] = (load(path), load(path))
    conditions = {k:{} for k in policies}
    schedules = rosters()
    for split in ("historical", "held"):
        for k in policies:
            conditions[k][split] = []
        for ident, wiring, meta in schedules[split]:
            answers = [tuple(panels.truth(wiring, raw)) for raw in range(512)]
            semantic = grammar(wiring, answers)
            for k, (cp1, cp2) in policies.items():
                row = measure(k, cp1, cp2, head["head"], wiring, meta, ident, answers, semantic)
                conditions[k][split].append(row)
    value = {"ticket":STUDY, "artifact_id":STUDY+"-E001", "schema_version":1,
             "kind":"experiment", "evidence_stage":"exploratory", "bindings":binding,
             "conditions":conditions, "summary":{k:{s:summarize(rows) for s,rows in v.items()}
                                                 for k,v in conditions.items()}}
    bind(out / "result.json", value)
    return value["summary"]


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("action", choices=("sources", "freeze", "assess"))
    cli.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = cli.parse_args()
    action = {"sources":sources, "freeze":freeze, "assess":assess}[args.action]
    print(json.dumps(action(args.out), indent=2))
