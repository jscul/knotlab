"""Shared-runner job: re-tuning and test cells of MEET-TRANSFER-20261117-001A, five runs per instance throughout.

Params:
  phase     screen | confirm | test   (the comparators' two-stage tuning, then the test)
  screened  (confirm) screen.json from analyze_meet.py screen: per cell, the settings to confirm
  retuned   (test) retuned.json from analyze_meet.py confirm: per cell, the settings to test
  policies  (test) policies.json: each learned arm's weights and flags
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

# (family, alpha, window, n): (test instances, flip cap, tuning cap)
CELLS = {("local", 4.0, 10, 3200): (50, 4 * 10**8, 10**8),      # primary: held out, 4x the training size
         ("local", 4.0, 10, 800): (100, 2 * 10**7, 2 * 10**7),
         ("local", 4.0, 40, 800): (100, 2 * 10**7, 2 * 10**7),     # untouched held-out windows
         ("local", 4.0, 160, 800): (100, 2 * 10**7, 2 * 10**7),
         ("heavy", 3.0, 10, 800): (100, 2 * 10**7, 2 * 10**7),     # untouched held-out degree distribution
         ("heavy", 3.0, 10, 3200): (50, 2 * 10**8, 2 * 10**7),
         ("rand", 2.1, 10, 3200): (50, 2 * 10**8, 2 * 10**7),      # training patterns at 4x the size
         ("rand", 4.0, 10, 3200): (50, 2 * 10**8, 2 * 10**7),
         ("block", 2.5, 20, 3200): (50, 2 * 10**8, 2 * 10**7)}
TEST_SEED0 = {"rand": 3_000_000, "local": 3_500_000, "block": 3_700_000, "heavy": 3_800_000}
TUNE_SEED0 = {"rand": 4_000_000, "local": 4_500_000, "block": 4_700_000, "heavy": 4_800_000}
CONFIRM_SEED0 = {"rand": 4_100_000, "local": 4_600_000, "block": 4_750_000, "heavy": 4_850_000}
TUNE_INSTANCES, TUNE_RUNS, CONFIRM_INSTANCES, RUNS = 8, 3, 20, 5
GRID = [("novelty_plus", (p, wp)) for p in (0.5, 0.6, 0.65, 0.7, 0.75, 0.8) for wp in (0.0, 0.005, 0.01, 0.02, 0.05)] + \
       [("probsat_poly", (cb, 1.0)) for cb in (1.0, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0)] + \
       [("probsat_exp", (cb,)) for cb in (1.5, 2.0, 2.5, 3.0, 3.5, 4.0)] + \
       [("walksat", (p,)) for p in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)]
# Added 2026-11-17 after the screen, before any learned arm was tested: several optima sat at the grid's edges (noise 0.8 at
# local window 10 n = 3200, 0.5 at windows 40 and 160 and rand 4.0, probSAT cb 1.0), so the screen is extended there. This can
# only strengthen the hand-written side (deviation recorded in the result note).
GRID_EDGE = [("novelty_plus", (p, wp)) for p in (0.3, 0.4, 0.85, 0.9) for wp in (0.0, 0.005, 0.01, 0.02, 0.05)] + \
            [("probsat_poly", (cb, 1.0)) for cb in (0.6, 0.8)]
LEARNED = [f"{a}_s{k}" for a, ks in (("D", 4), ("Dl", 4), ("Dr", 2), ("Dn", 2), ("L3sm", 2)) for k in range(ks)]

P = {}
_POL = {}


def setup(params):
    P.update(params)
    os.environ.setdefault("WHERE_NEXT_BUILD", str(Path.home() / ".cache" / "where_next_build"))
    import engine
    engine.lib()


def run_seed(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little")


def key(cell):
    fam, alpha, w, n = cell
    return f"{fam}{alpha}w{w}|{n}"


def cases():
    if P["phase"] in ("screen", "screen_edge"):
        for cell, (_, _, tcap) in CELLS.items():
            for algo, prm in (GRID if P["phase"] == "screen" else GRID_EDGE):
                for i in range(TUNE_INSTANCES):
                    s = TUNE_SEED0[cell[0]] + i
                    yield (f"screen|{key(cell)}|{algo}|{','.join(map(str, prm))}|{s}",
                           {"cell": list(cell), "seed": s, "arm": f"{algo}{prm}", "algo": algo, "params": list(prm),
                            "cap": tcap, "runs": TUNE_RUNS, "purpose": "screen"})
    elif P["phase"] == "confirm":
        Q = json.loads(Path(P["screened"]).read_text())
        for cell, (_, _, tcap) in CELLS.items():
            for algo, prm in Q[key(cell)]:
                for i in range(CONFIRM_INSTANCES):
                    s = CONFIRM_SEED0[cell[0]] + i
                    yield (f"confirm|{key(cell)}|{algo}|{','.join(map(str, prm))}|{s}",
                           {"cell": list(cell), "seed": s, "arm": f"{algo}{tuple(prm)}", "algo": algo, "params": list(prm),
                            "cap": tcap, "runs": RUNS, "purpose": "confirm"})
    elif P["phase"] == "test":
        R = json.loads(Path(P["retuned"]).read_text())
        for cell, (count, cap, _) in CELLS.items():
            arms = [(a, "policy", []) for a in LEARNED]
            for name, algo, prm in R[key(cell)]:
                arms.append((name, algo, prm))
            for i in range(count):
                s = TEST_SEED0[cell[0]] + i
                for name, algo, prm in arms:
                    yield (f"test|{key(cell)}|{name}|{s}",
                           {"cell": list(cell), "seed": s, "arm": name, "algo": algo, "params": list(prm), "cap": cap,
                            "runs": RUNS, "purpose": "test"})
    else:
        raise ValueError(P["phase"])


def policy(arm):
    import numpy as np
    if arm not in _POL:
        pol = json.loads(Path(P["policies"]).read_text())[arm]
        _POL[arm] = (np.load(pol["theta"]), int(pol["flags"]))
    return _POL[arm]


def run(case_id, payload):
    import engine as E
    fam, alpha, w, n = payload["cell"]
    s = payload["seed"]
    inst = E.planted(fam, n, alpha, s, w=w)
    out = []
    for rep in range(payload["runs"]):
        rs = run_seed(payload["purpose"], fam, alpha, n, s, rep)  # the same initial states for every arm
        if payload["algo"] == "policy":
            th, flags = policy(payload["arm"])
            r = E.run(inst, "policy", (), theta=th, flags=flags, seed=rs, max_flips=payload["cap"])
        else:
            r = E.run(inst, payload["algo"], tuple(payload["params"]), seed=rs, max_flips=payload["cap"])
        out.append({"flips": r["flips"], "solved": r["solved"], "minviol": r["minviol"], "cpu": r["cpu"], "work": r["work"],
                    "distinct_sum": r["distinct_sum"], "where_steps": r["where_steps"], "new_chosen": r["new_chosen"],
                    "new_avail": r["new_avail"]})
    return {"cell": payload["cell"], "seed": s, "arm": payload["arm"], "algo": payload["algo"], "params": payload["params"],
            "cap": payload["cap"], "runs": out}
