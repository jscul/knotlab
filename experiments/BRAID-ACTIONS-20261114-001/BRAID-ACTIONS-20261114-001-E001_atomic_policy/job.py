"""Fit one checkpoint. Held-out scoring runs separately from this entry point."""

import json
import time
from hashlib import sha256

import actions
import reader


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def cases():
    yield "fit-one-policy", {}


def run(case_id, payload):
    started = time.perf_counter()
    acquisition = actions.fit(assess_after=False)
    gates, training = reader.fit(acquisition["checkpoint"])
    checkpoint = {"schema_version": 1, "moves": acquisition.pop("checkpoint"), "reader": gates}
    return {"checkpoint": checkpoint, "checkpoint_sha256": digest(checkpoint),
            "move_training": acquisition, "reader_training": training,
            "elapsed_seconds": time.perf_counter() - started}


if __name__ == "__main__":
    print(json.dumps(run("fit-one-policy", {}), sort_keys=True))
