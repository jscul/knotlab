"""Training-only entry point. Each case consumes anonymous training wirings."""

import hashlib
import json
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = "GROUP-SENDER-20261115-001"
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / STUDY))
sys.path.insert(0, str(HERE))

import panels
import proposal
import sender


RAW_MASKS = tuple(r for r in range(512) if r.bit_count() % 2 == 0)


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def setup(params):
    if params:
        raise ValueError("The two training conditions have no runtime selectors")


def cases():
    for strategy in ("singleton", "joint"):
        yield strategy, {"strategy": strategy}


def training_examples():
    records = panels.training_panel()
    return [name for name, _, _ in records], [
        (wiring, [panels.truth(wiring, raw) for raw in RAW_MASKS])
        for _, wiring, _ in records
    ]


def train_direct(joint, examples):
    rows, costs = [], []
    for wiring, answers in examples:
        trace = sender.trace_public(joint, wiring)
        rows.append(proposal.features(trace["support_masks"]))
        targets = tuple(sum(value << i for i, value in enumerate(column)) for column in zip(*answers))
        options = []
        for mask in range(16):
            plan = sender.plan_from_mask(joint, wiring, mask, traced=trace)
            predicted = sender.plan_answer_columns(joint, wiring, plan, RAW_MASKS)
            error = sum((p ^ t).bit_count() for p, t in zip(predicted, targets, strict=True))
            options.append((error, plan["width"]))
        costs.append(options)
    return proposal.fit(rows, costs)


def run(case_id, payload):
    if case_id not in ("singleton", "joint") or payload != {"strategy": case_id}:
        raise ValueError("Unknown training condition")
    names, examples = training_examples()
    start = time.perf_counter()
    checkpoint, history = sender.fit(examples, RAW_MASKS, variant=case_id)
    out = {
        "strategy": case_id, "training_ids": names, "raw_masks": len(RAW_MASKS),
        "examples_sha256": digest(examples), "checkpoint": checkpoint,
        "checkpoint_sha256": digest(checkpoint), "history": history,
        "fit_seconds": time.perf_counter() - start,
    }
    if case_id == "joint":
        start = time.perf_counter()
        head, history = train_direct(checkpoint, examples)
        out["direct"] = {"head": head, "history": history, "seconds": time.perf_counter() - start}
    return out
