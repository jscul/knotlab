"""Shared-runner job: the post hoc five-run check of SCALE-MEMORY-20261116-001A (agreed with the coordinator before the
results were final; not part of the frozen protocol).

The scale-free arms (L3s, L3sm, both seeds), WHERE-NEXT's L3 (seed 1) and Novelty+ at three settings, including walk
probability 0 which the frozen grids lacked and the referee of WHERE-NEXT found best at n = 3200, each run five times per test
instance with fresh run seeds at rand n = 3200 and 12800 (100 instances each).
Params: policies (policies.json).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
P = {}
_POL = {}
ARMS = [("L3s_s0", None), ("L3s_s1", None), ("L3sm_s0", None), ("L3sm_s1", None), ("L3_s1", None),
        ("novelty_plus(0.7,0.05)", (0.7, 0.05)), ("novelty_plus(0.7,0.01)", (0.7, 0.01)), ("novelty_plus(0.7,0)", (0.7, 0.0))]


def setup(params):
    P.update(params)
    os.environ.setdefault("WHERE_NEXT_BUILD", str(Path.home() / ".cache" / "where_next_build"))
    import engine
    engine.lib()


def run_seed(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little")


def cases():
    for n in (3200, 12800):
        for i in range(100):
            s = 3_000_000 + i
            for arm, _ in ARMS:
                yield f"posthoc|rand|{n}|{arm}|{s}", {"n": n, "seed": s, "arm": arm}


def run(case_id, payload):
    import numpy as np
    import engine as E
    n, s, arm = payload["n"], payload["seed"], payload["arm"]
    inst = E.planted("rand", n, 2.1, s)
    cap = 2 * 10**8 if n == 3200 else 2 * 10**9
    out = []
    for rep in range(5):
        rs = run_seed("posthoc", n, s, rep)
        prm = dict(ARMS)[arm]
        if prm is None:
            if arm not in _POL:
                pol = json.loads(Path(P["policies"]).read_text())[arm]
                _POL[arm] = (np.load(pol["theta"]), int(pol["flags"]))
            th, flags = _POL[arm]
            r = E.run(inst, "policy", (), theta=th, flags=flags, seed=rs, max_flips=cap)
        else:
            r = E.run(inst, "novelty_plus", prm, seed=rs, max_flips=cap)
        out.append({"flips": r["flips"], "solved": r["solved"], "cpu": r["cpu"], "work": r["work"]})
    return {"n": n, "seed": s, "arm": arm, "runs": out}
