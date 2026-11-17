"""Shared-runner job for AGENT-LOOP-20261117-001A: the test, or a dry run of the pipeline on calibration instances (param
"dry": seeds from 9,600,000, a few instances, only cells already run before the freeze).

Arms (all from the same five initial states per instance):
  NOV, NOV8   Novelty+ (0.7, 0.01) and (0.8, 0.01) alone; F is the better of the two, re-chosen per resample
  GN          Novelty+ (0.7, 0.01) under the proof-based eager batched slow loop, random probe targets; the slow budget of an
              epoch is 3 times its own charged fast work (EARN-BUDGET's rule)
  GNf         the same with the slow budget at 3 x 50 incidences per flip (the same proof effort per flip for every fast loop)
  GNco        GN with co-flip probe targets (SPEC-MERGE's gate D signal as a guide for what to prove)
  SL          the slow loop alone, no fast loop: it solves only if the pattern collapses to no knots
  Dr0, Dr1    the learned agent Dr alone (both seeds of MEET-TRANSFER-20261117-001)
  DrC0, DrC1  Dr under the slow loop (EARN-BUDGET's rule), its memory carried across every rebuild
  DrR0, DrR1  the same with its memory restarted at every rebuild
  DrCf0/1, DrRf0/1  the same two under the per-flip budget (as GNf)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
P: dict = {}
ROOT = HERE.parents[2]
MT_POLICIES = ROOT / "artifacts/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer/policies.json"
# (name, family, density, window, n, cap)
CELLS = [
    ("local-w30-3200", "local", 4.0, 30, 3200, 2 * 10**8),   # primary: never run in the program before the freeze
    ("local-w10-3200", "local", 4.0, 10, 3200, 2 * 10**8),
    ("local-w20-3200", "local", 4.0, 20, 3200, 2 * 10**8),
    ("block-w20-3200", "block", 2.5, 20, 3200, 2 * 10**7),  # memory cell: run before in the program, fresh instances
    ("block-w40-3200", "block", 2.5, 40, 3200, 2 * 10**7),  # memory cell: never run in the program before the freeze
    ("rand-3200", "rand", 2.1, 10, 3200, 2 * 10**7),
]
CELL = {c[0]: c for c in CELLS}
SEED_TEST = 9_100_000
ARMS = ["NOV", "NOV8", "GN", "GNf", "GNco", "SL", "Dr0", "Dr1", "DrC0", "DrC1", "DrR0", "DrR1", "DrCf0", "DrCf1", "DrRf0",
        "DrRf1"]
UNIT = 50  # incidences per flip of the per-flip slow budget
_POL = {}


def setup(params):
    P.update(params)
    os.environ.setdefault("SLOW_LOOP_BUILD", str(Path.home() / ".cache" / "slow_loop_build"))
    import agent_loop  # noqa: F401
    import slow_loop
    slow_loop.lib()


SEED_DRY = 9_600_000
DRY_CELLS = ("local-w10-3200", "local-w20-3200", "block-w20-3200", "rand-3200")


def cases():
    dry = bool(P.get("dry"))
    for name, *_ in CELLS:
        if dry and name not in DRY_CELLS:
            continue
        for arm in P.get("arms", ",".join(ARMS)).split(","):
            for i in range(int(P.get("dry", 50))):
                yield f"{'dry' if dry else 'test'}|{name}|{arm}|{i}", {"cell": name, "arm": arm, "i": i}


def _dr(seed_ix):
    import numpy as np
    if seed_ix not in _POL:
        pol = json.loads(MT_POLICIES.read_text())[f"Dr_s{seed_ix}"]
        _POL[seed_ix] = (np.load(pol["theta"]), int(pol["flags"]))
    return _POL[seed_ix]


def run(case_id, payload):
    import agent_loop as G
    import slow_loop as S
    cell, arm, i = payload["cell"], payload["arm"], payload["i"]
    _, fam, a, w, n, cap = CELL[cell]
    seed = (SEED_DRY if P.get("dry") else SEED_TEST) + i
    inst = S.planted(fam, n, a, seed, w=w)
    keep = ("flips", "solved", "verified", "work", "work_fast", "work_slow", "work_rebuild", "cpu", "cpu_fast", "rebuilds",
            "probes", "n_final", "m_final", "epochs", "flips_first")
    out = []
    for r in range(5):
        rs = S.run_seed("test", cell, seed, r)
        if arm == "NOV":
            res = S.run_fast(inst, "novelty_plus", (0.7, 0.01), rs, cap)
        elif arm == "NOV8":
            res = S.run_fast(inst, "novelty_plus", (0.8, 0.01), rs, cap)
        elif arm == "GN":
            res = G.run_loop(inst, "nov", rs, cap, target="random")
        elif arm == "GNf":
            res = G.run_loop(inst, "nov", rs, cap, pol=dict(G.GPR, unit=UNIT), target="random")
        elif arm == "GNco":
            res = G.run_loop(inst, "nov", rs, cap, target="coflip")
        elif arm == "SL":
            res = G.run_loop(inst, "none", rs, cap, pol=dict(G.GPR, unit=UNIT))
        else:
            th, fl = _dr(int(arm[-1]))
            if arm[2].isdigit():
                res = G.run_agent_alone(inst, rs, cap, th, fl)
            else:
                pol = dict(G.GPR, unit=UNIT) if arm[3] == "f" else G.GPR
                res = G.run_loop(inst, "agent", rs, cap, pol=pol, memory="carry" if arm[2] == "C" else "restart",
                                 theta=th, flags=fl)
        out.append({k: res[k] for k in keep if k in res})
    return {"cell": cell, "arm": arm, "seed": seed, "runs": out}
