"""Shared-runner job for SPEC-MERGE-20261117-001A, one stage per launch (--param stage=...).

  gate    D: co-flip evidence against random co-knotted pairs on 30 fresh instances of rand 2.1 and local w10 at n = 3200
  policy  the 24 speculative-merge settings on 8 tuning instances x 3 runs of rand 2.1 (A) and local w10 (Aloc) at n = 3200,
          with Novelty+ (0.7, 0.01) from the same initial states ("base")
  test    the frozen arms on 50 fresh instances x 5 runs (20 at n = 12800)

Params: stage; policies (the policy stage's choice) and arms (comma list) for test.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
P: dict = {}

NOV = (0.7, 0.01)
# the re-tuned Novelty+ of EARN-BUDGET-20261117-001A's R1 (its own tuning instances) for each family at n = 3200
NOV_T = {"rand": (0.7, 0.005), "rand3": (0.6, 0.02), "local": (0.8, 0.01)}
# (name, family, density, window, n, cap, NOV_T key)
CELLS = [
    ("rand-3200", "rand", 2.1, 10, 3200, 2 * 10**7, "rand"),
    ("rand3-3200", "rand", 3.0, 10, 3200, 2 * 10**7, "rand3"),
    ("rand-12800", "rand", 2.1, 10, 12800, 10**8, "rand"),
    ("local-w10-3200", "local", 4.0, 10, 3200, 10**8, "local"),
]
CELL = {c[0]: c for c in CELLS}
A0 = {"e": 4.0, "s": 8, "mu": 0.02, "patience": 2, "warmup": 2, "max_rounds": 100}
AE = {"e": 2.0, "s": 4, "mu": 0.1, "patience": 1, "warmup": 2, "max_rounds": 100}  # the fixed eager arm (advisor)
GRID = [{"e": e, "s": s, "mu": mu, "patience": pt, "warmup": 2, "max_rounds": 100}
        for e in (2.0, 8.0) for s in (4, 8) for mu in (0.005, 0.02, 0.1) for pt in (1, 3)] + [A0]
SEED_GATE, SEED_TUNE, SEED_TEST = 8_700_000, 8_800_000, 8_900_000
# the proof-based reference: EARN-BUDGET's per-cell oracle on local w10 at 3200, a fixed batched budget of 3 times the
# search's work with tie probes (slow_loop.run_slow, charge v2)
GPR = {"e": 1.0, "rho": 3.0, "beta": 0.0, "J": 2, "pb": 4000, "backoff": False, "mode": 1, "rb": 0.003}
ARMS = ["NOV", "NOVt", "A0", "Arand0", "AE", "AErand", "A", "Arand", "Aloc", "Arandloc", "Gpr", "Dr0", "Dr1"]
# the learned fast loop offered by MEET-TRANSFER-20261117-001 (unrefereed): Dr, both seeds, alone, as context only (its engine
# reads unsigned knots, so the slow loop cannot run on it)
ROOT = HERE.parents[2]
MT_ENGINE = ROOT / "experiments/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer/engine.py"
MT_POLICIES = ROOT / "artifacts/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer/policies.json"
_MT = {}


def _mt():
    if "E" not in _MT:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mt_engine", MT_ENGINE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _MT["E"] = mod
        _MT["pol"] = json.loads(MT_POLICIES.read_text())
    return _MT["E"], _MT["pol"]


def setup(params):
    P.update(params)
    os.environ.setdefault("SLOW_LOOP_BUILD", str(Path.home() / ".cache" / "slow_loop_build"))
    import slow_loop
    slow_loop.lib()


def _inst(cell, seed):
    import slow_loop as S
    _, fam, a, w, n, cap, _k = CELL[cell]
    return S.planted(fam, n, a, seed, w=w), cap


def cases():
    st = P["stage"]
    if st == "gate":
        for cell in ("rand-3200", "local-w10-3200"):
            for i in range(30):
                yield f"gate|{cell}|{i}", {"cell": cell, "i": i}
    elif st == "policy":
        for cell in ("rand-3200", "local-w10-3200"):
            for i in range(8):
                yield f"policy|{cell}|base|{i}", {"cell": cell, "k": -1, "i": i}
                for k in range(len(GRID)):
                    yield f"policy|{cell}|{k}|{i}", {"cell": cell, "k": k, "i": i}
    elif st == "test":
        arms = P["arms"].split(",")
        for name, *_ in CELLS:
            for arm in arms:
                for i in range(20 if name.endswith("12800") else 50):
                    yield f"test|{name}|{arm}|{i}", {"cell": name, "arm": arm, "i": i}
    else:
        raise ValueError(st)


def _slim(r):
    keep = ("flips", "solved", "verified", "work", "work_fast", "work_slow", "work_rebuild", "cpu", "cpu_rebuild", "minviol",
            "epochs", "rounds", "merges", "undos", "stall_undos", "contra_undos", "active_merges", "n_final",
            "precision_all", "precision_active", "contradiction", "round_log")
    return {k: r[k] for k in keep if k in r}


def run(case_id, payload):
    import slow_loop as S
    import spec_merge as M
    st = P["stage"]
    cell, i = payload["cell"], payload["i"]
    if st == "gate":
        seed = SEED_GATE + i
        inst, _ = _inst(cell, seed)
        return {"cell": cell, "seed": seed,
                "gate": M.gate_d(inst, NOV, S.run_seed("gate", cell, seed), probe=cell.startswith("local"))}
    if st == "policy":
        seed = SEED_TUNE + i
        inst, cap = _inst(cell, seed)
        out = []
        for r in range(3):
            rs = S.run_seed("policy", cell, seed, r)
            if payload["k"] < 0:
                out.append(_slim(S.run_fast(inst, "novelty_plus", NOV, rs, cap)))
            else:
                out.append(_slim(M.run_spec(inst, NOV, rs, cap, GRID[payload["k"]], mode="coflip")))
        return {"cell": cell, "k": payload["k"], "seed": seed, "runs": out}
    if st == "test":
        seed = SEED_TEST + i
        inst, cap = _inst(cell, seed)
        arm = payload["arm"]
        pols = json.loads(Path(P["policies"]).read_text()) if P.get("policies") else {}
        out = []
        for r in range(5):
            rs = S.run_seed("test", cell, seed, r)
            if arm == "NOV":
                res = S.run_fast(inst, "novelty_plus", NOV, rs, cap)
            elif arm == "NOVt":
                res = S.run_fast(inst, "novelty_plus", NOV_T[CELL[cell][6]], rs, cap)
            elif arm == "Gpr":
                res = S.run_slow(inst, "novelty_plus", NOV, rs, cap, GPR)
            elif arm in ("Dr0", "Dr1"):
                import numpy as np
                E, mpol = _mt()
                pol = mpol[f"Dr_s{arm[-1]}"]
                _, fam, a, w, n, _cap, _k = CELL[cell]
                mi = E.planted(fam, n, a, seed, w=w)
                rr = E.run(mi, "policy", (), theta=np.load(pol["theta"]), flags=int(pol["flags"]), seed=rs, max_flips=cap,
                           want_state=True)
                res = {"flips": rr["flips"], "solved": rr["solved"], "work": rr["work"], "work_fast": rr["work"],
                       "cpu": rr["cpu"], "verified": inst.satisfied(rr["state"].astype(np.uint8)) if rr["solved"] else None}
            else:
                pol = {"A0": A0, "Arand0": A0, "AE": AE, "AErand": AE, "A": pols.get("A"), "Arand": pols.get("A"),
                       "Aloc": pols.get("Aloc"), "Arandloc": pols.get("Aloc")}[arm]
                mode = "random" if arm in ("Arand0", "AErand", "Arand", "Arandloc") else "coflip"
                res = M.run_spec(inst, NOV, rs, cap, pol, mode=mode)
            out.append(_slim(res))
        return {"cell": cell, "arm": arm, "seed": seed, "runs": out}
    raise ValueError(st)
