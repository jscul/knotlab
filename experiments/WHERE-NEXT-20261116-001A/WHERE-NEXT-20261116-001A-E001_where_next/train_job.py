"""Shared-runner job: the eight ES trainings of WHERE-NEXT-20261116-001A (four learned arms, two seeds each).

Params: out (directory for the trained weights and logs), tuning (tuning.json), inner (workers per training).
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
    for arm in ("L3", "L2", "L2w", "L1"):
        for seed in (0, 1):
            yield f"{arm}_s{seed}", {"arm": arm, "seed": seed}


def run(case_id, payload):
    import train_es as T
    out = Path(P["out"]) / case_id
    wp = (1.8, 1.0)
    if payload["arm"] == "L2w":
        rows = json.loads(Path(P["tuning"]).read_text())["probsat"]["grid"]
        wp = tuple(min((r for r in rows if r["algo"] == "probsat_poly"), key=lambda r: r["mean_log_flips"])["params"])
    T.train(payload["arm"], payload["seed"], out, pairs=32, sigma=0.1, lr=0.05, workers=int(P.get("inner", 4)),
            what_params=wp)
    return json.loads((out / "summary.json").read_text())
