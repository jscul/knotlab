"""Shared-runner job: the ten ES trainings of SCALE-MEMORY-20261116-001A (five arms, two seeds each).

Params: out (directory for the trained weights and logs), inner (workers per training).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

P = {}


def setup(params):
    P.update(params)
    os.environ.setdefault("WHERE_NEXT_BUILD", str(Path.home() / ".cache" / "where_next_build"))
    import engine
    engine.lib()  # build once before the workers fork


def cases():
    for arm in ("L3sm", "L3m", "L3c", "L2m", "L3s"):
        for seed in (0, 1):
            yield f"{arm}_s{seed}", {"arm": arm, "seed": seed}


def run(case_id, payload):
    import train_es as T
    out = Path(P["out"]) / case_id
    cur, val = T.CURRICULA[payload["arm"]]
    T.train(payload["arm"], payload["seed"], out, pairs=32, sigma=0.1, lr=0.05, workers=int(P.get("inner", 4)),
            what_params=(), curriculum=cur, val=val)
    return json.loads((out / "summary.json").read_text())
