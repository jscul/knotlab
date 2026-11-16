"""Fit both policies from terminal labels, without importing assessment or constructing held menus."""
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
TICKET = "BIT-DECODER-20261114-001"
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / TICKET))
sys.path.insert(0, str(HERE))

import codec
import wirings

CONDITIONS = ("any_only", "varied")
RAW_MASKS = tuple(n for n in range(512) if n.bit_count() % 2 == 0)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def training_examples(condition):
    rows, ids = [], []
    for identity, wiring, metadata in wirings.training_panel():
        if condition == "any_only" and metadata["family"] != "any":
            continue
        labels = [wirings.truth(wiring, n) for n in RAW_MASKS]
        targets = tuple(sum(value << i for i, value in enumerate(col)) for col in zip(*labels))
        rows.append({"wiring": wiring, "answers": targets})
        ids.append(identity)
    return rows, ids


def setup(params):
    if params:
        raise ValueError("The fixed two-fit panel takes no runtime overrides")


def cases():
    for condition in CONDITIONS:
        yield condition, {"condition": condition}


def run(case_id, payload):
    if case_id not in CONDITIONS or payload != {"condition": case_id}:
        raise ValueError("Unknown training case")
    rows, ids = training_examples(case_id)
    start = time.perf_counter()
    checkpoint, evidence = codec.fit(rows, RAW_MASKS)
    return {"condition": case_id, "checkpoint": checkpoint, "fit": evidence,
            "training_wirings": ids, "training_inputs": len(RAW_MASKS),
            "training_examples_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
            "checkpoint_sha256": hashlib.sha256(canonical(checkpoint)).hexdigest(),
            "fit_seconds": time.perf_counter() - start}
