"""Train on the training-panel answers only."""

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = "ANSWER-COMPOSE-20261115-001"
sys.path[:0] = [str(HERE), str(HERE.parents[2] / "research" / STUDY)]
import learner
import panels

TRAIN_RAW = tuple(mask for mask in range(512) if mask.bit_count() % 2 == 0)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def setup(params):
    if params:
        raise ValueError("This fit has no runtime hyperparameter overrides")


def cases():
    yield "packet_nand", {}


def run(case_id, payload):
    if case_id != "packet_nand" or payload:
        raise ValueError("Unexpected training case")
    start = time.perf_counter()
    cpu = time.process_time()
    rows = panels.training_panel()
    examples = [(w, [panels.truth(w, m) for m in TRAIN_RAW]) for _, w, _ in rows]
    checkpoint, history = learner.fit(examples, TRAIN_RAW)
    return {"checkpoint":checkpoint, "checkpoint_sha256":digest(checkpoint), "history":history,
            "training_ids":[i for i,_,_ in rows], "training_data_sha256":digest(examples),
            "fit_wall_seconds":time.perf_counter() - start, "fit_cpu_seconds":time.process_time()-cpu}
