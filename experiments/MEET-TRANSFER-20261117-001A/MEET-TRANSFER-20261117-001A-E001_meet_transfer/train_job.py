"""Shared-runner job: the twelve ES trainings of MEET-TRANSFER-20261117-001A (D and Dl four seeds each, Dn and Dr two).

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
    engine.lib()


def cases():
    for arm, seeds in (("D", 4), ("Dl", 4), ("Dn", 2), ("Dr", 2)):
        for seed in range(seeds):
            yield f"{arm}_s{seed}", {"arm": arm, "seed": seed}


def run(case_id, payload):
    import train_mixed as M
    out = Path(P["out"]) / case_id
    M.train(payload["arm"], payload["seed"], out, workers=int(P.get("inner", 3)))
    return json.loads((out / "summary.json").read_text())
