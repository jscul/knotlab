"""Shared-runner job for SLOW-LOOP-20261117-001A, one stage per launch (--param stage=...).

  retune   S1: NOV (30 settings) and PS (8) on 8 tuning instances per cell, 3 runs each
  retune2  S1b (deviation, decided after S1 and before any slow arm was tuned): where S1's best setting sat on an edge of
           its grid, the grid extended one step beyond it on the same instances (NOV: noise 0.85 and 0.9, walk probability
           0.1; PS: cb 0.8 and 0.6)
  policy   S2: the 48 slow-loop settings on 8 instances of rand 2.1 and block 2.5 (G) and of local w10 (GO) at n = 800,
           and the 8 static settings on rand 2.1 and block 2.5 (ST), 3 runs each, with NOV from the same initial states
           ("base" cases)
  test     S3: the frozen arms on 50 test instances per cell, 5 runs each; CDCL on all 50 of the local and embedded
           cells and the first 20 of the others
  stress   S4: local w10 and rand at n = 12800, 20 instances, NOV, PS, G, ST, GO at the n = 3200 settings
  pht      post hoc, not frozen (decided after the policy tuning gave G the laziest setting and before the test was
           complete): the 8 static settings scored on local w10 at n = 800 as GO was (STO)
  ph       post hoc, not frozen: RNDO (GO's policy with random targets: the attention counts at an eager policy) in every
           test cell, the test's instances and initial states. STO came out the same setting as ST, so its runs would
           repeat ST's and are not made

Params: stage; retuned (S1's choice, retuned.json) for policy/test/stress; policies (S2's choice, policies.json) for
test/stress.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
P: dict = {}

# (name, family, density, window, n, flip cap)
CELLS = [
    ("local-w10-3200", "local", 4.0, 10, 3200, 2 * 10**8),
    ("local-w40-3200", "local", 4.0, 40, 3200, 2 * 10**8),
    ("rand-3200", "rand", 2.1, 10, 3200, 2 * 10**8),
    ("block-3200", "block", 2.5, 20, 3200, 2 * 10**8),
    ("local-w10-800", "local", 4.0, 10, 800, 2 * 10**7),
    ("local-w40-800", "local", 4.0, 40, 800, 2 * 10**7),
    ("rand-800", "rand", 2.1, 10, 800, 2 * 10**7),
    ("block-800", "block", 2.5, 20, 800, 2 * 10**7),
    ("embed-3200", "embed", 0.0, 10, 3200, 2 * 10**8),
    ("embed-800", "embed", 0.0, 10, 800, 2 * 10**7),
]
STRESS_CELLS = [
    ("local-w10-12800", "local", 4.0, 10, 12800, 2 * 10**9, "local-w10-3200"),
    ("rand-12800", "rand", 2.1, 10, 12800, 2 * 10**9, "rand-3200"),
]
CELL = {c[0]: c for c in CELLS}
NOV_GRID = [(nz, wp) for nz in (0.5, 0.6, 0.65, 0.7, 0.75, 0.8) for wp in (0.0, 0.005, 0.01, 0.02, 0.05)]
PS_GRID = [(cb, 1.0) for cb in (1.0, 1.4, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0)]
POLICY_GRID = [{"e": e, "rho": rho, "beta": beta, "J": 2, "pb": 4000, "backoff": bo, "mode": 0}
               for e in (1.0, 4.0, 16.0) for rho in (0.03, 0.1, 0.3, 1.0) for beta in (0.0, 0.5) for bo in (True, False)]
STATIC_GRID = [{"e": 1.0, "rho": 0.0, "beta": beta, "J": 2, "pb": 4000, "backoff": False, "mode": 2, "passes": ps,
                "abort": ab} for ps in (1, 8) for beta in (0.0, 0.5) for ab in (0.0, 0.05)]
EMBED = {"frac": 0.25, "alpha_r": 2.1, "alpha_l": 4.0, "alpha_c": 0.02, "w": 10}
CDCL_ALL = ("local", "embed")
TUNE_CAP = 2 * 10**7
NOV_EXT = [(nz, wp) for nz in (0.85, 0.9) for wp in (0.0, 0.005, 0.01, 0.02, 0.05, 0.1)] + \
    [(nz, 0.1) for nz in (0.5, 0.6, 0.65, 0.7, 0.75, 0.8)]
PS_EXT = [(0.6, 1.0), (0.8, 1.0)]
EXT_NOV_CELLS = ("local-w10-3200", "local-w40-3200", "rand-3200", "block-3200", "embed-3200", "local-w10-800")
EXT_PS_CELLS = ("local-w10-3200", "local-w40-3200")
SEED_TUNE, SEED_POLICY, SEED_ORACLE, SEED_TEST, SEED_STRESS = 7_500_000, 7_000_000, 7_600_000, 7_100_000, 7_200_000
POLICY_PATTERNS = {"rand-800": "G", "block-800": "G", "local-w10-800": "GO"}
ARMS = ["NOV", "PS", "G", "Gx", "RND", "ST", "GO"]


def setup(params):
    P.update(params)
    os.environ.setdefault("SLOW_LOOP_BUILD", str(Path.home() / ".cache" / "slow_loop_build"))
    import slow_loop
    slow_loop.lib()


def _load(key):
    return json.loads(Path(P[key]).read_text())


def cases():
    st = P["stage"]
    if st == "retune":
        for name, *_ in CELLS:
            for i in range(8):
                for j, prm in enumerate(NOV_GRID):
                    yield f"retune|{name}|NOV|{j}|{i}", {"cell": name, "algo": "novelty_plus", "prm": prm, "i": i}
                for j, prm in enumerate(PS_GRID):
                    yield f"retune|{name}|PS|{j}|{i}", {"cell": name, "algo": "probsat_poly", "prm": prm, "i": i}
    elif st == "retune2":
        for name in EXT_NOV_CELLS:
            for i in range(8):
                for j, prm in enumerate(NOV_EXT):
                    yield f"retune2|{name}|NOV|{j}|{i}", {"cell": name, "algo": "novelty_plus", "prm": prm, "i": i}
        for name in EXT_PS_CELLS:
            for i in range(8):
                for j, prm in enumerate(PS_EXT):
                    yield f"retune2|{name}|PS|{j}|{i}", {"cell": name, "algo": "probsat_poly", "prm": prm, "i": i}
    elif st == "pht":
        for i in range(8):
            yield f"pht|local-w10-800|base|{i}", {"cell": "local-w10-800", "k": -1, "i": i}
            for k in range(len(STATIC_GRID)):
                yield f"pht|local-w10-800|st{k}|{i}", {"cell": "local-w10-800", "k": k, "static": True, "i": i}
    elif st == "ph":
        for name, *_ in CELLS:
            for i in range(50):
                yield f"ph|{name}|RNDO|{i}", {"cell": name, "arm": "RNDO", "i": i}
    elif st == "policy":
        for name in POLICY_PATTERNS:
            for i in range(8):
                yield f"policy|{name}|base|{i}", {"cell": name, "k": -1, "i": i}
                for k in range(len(POLICY_GRID)):
                    yield f"policy|{name}|{k}|{i}", {"cell": name, "k": k, "i": i}
                if POLICY_PATTERNS[name] == "G":
                    for k in range(len(STATIC_GRID)):
                        yield f"policy|{name}|st{k}|{i}", {"cell": name, "k": k, "static": True, "i": i}
    elif st == "test":
        for name, *_ in CELLS:
            for arm in ARMS:
                for i in range(50):
                    yield f"test|{name}|{arm}|{i}", {"cell": name, "arm": arm, "i": i}
            for i in range(50 if name.startswith(CDCL_ALL) else 20):
                yield f"test|{name}|CDCL|{i}", {"cell": name, "arm": "CDCL", "i": i}
    elif st == "stress":
        for name, fam, a, w, n, cap, src in STRESS_CELLS:
            for arm in ("NOV", "PS", "G", "ST", "GO"):
                for i in range(20):
                    yield f"stress|{name}|{arm}|{i}", {"cell": name, "arm": arm, "i": i}
    else:
        raise ValueError(st)


def _inst(cell, seed):
    import slow_loop as S
    if cell in CELL:
        _, fam, a, w, n, cap = CELL[cell]
    else:
        _, fam, a, w, n, cap, _src = {c[0]: c for c in STRESS_CELLS}[cell]
    if fam == "embed":
        return S.planted_embed(n, seed, **EMBED), cap
    return S.planted(fam, n, a, seed, w=w), cap


def _slim(r):
    keep = ("flips", "solved", "verified", "work", "work_fast", "work_slow", "work_rebuild", "cpu", "cpu_fast",
            "cpu_slow", "cpu_rebuild", "minviol", "epochs", "rebuilds", "targets", "ties", "shadows", "n_final", "m_final",
            "contradiction")
    return {k: r[k] for k in keep if k in r}


def run(case_id, payload):
    import slow_loop as S
    st = P["stage"]
    cell, i = payload["cell"], payload["i"]
    if st in ("retune", "retune2"):
        seed = SEED_TUNE + i
        inst, _ = _inst(cell, seed)
        out = [_slim(S.run_fast(inst, payload["algo"], tuple(payload["prm"]), S.run_seed("retune", cell, seed, r),
                                TUNE_CAP)) for r in range(3)]
        return {"cell": cell, "algo": payload["algo"], "prm": payload["prm"], "seed": seed, "runs": out}
    if st in ("policy", "pht"):
        seed = (SEED_ORACLE if POLICY_PATTERNS[cell] == "GO" else SEED_POLICY) + i
        inst, cap = _inst(cell, seed)
        nov = tuple(_load("retuned")[cell]["NOV"])
        k = payload["k"]
        out = []
        for r in range(3):
            rs = S.run_seed("policy", cell, seed, r)  # pht reuses the policy stage's seeds, so its base runs repeat S2's
            if k < 0:
                out.append(_slim(S.run_fast(inst, "novelty_plus", nov, rs, cap)))
            elif payload.get("static"):
                out.append(_slim(S.run_slow(inst, "novelty_plus", nov, rs, cap, STATIC_GRID[k], static=True)))
            else:
                out.append(_slim(S.run_slow(inst, "novelty_plus", nov, rs, cap, POLICY_GRID[k])))
        return {"cell": cell, "k": k, "static": bool(payload.get("static")), "seed": seed, "runs": out}
    if st in ("test", "stress", "ph"):
        arm = payload["arm"]
        if st in ("test", "ph"):
            seed = SEED_TEST + i
            src = cell
        else:
            seed = SEED_STRESS + i
            src = {c[0]: c for c in STRESS_CELLS}[cell][6]
        inst, cap = _inst(cell, seed)
        if arm == "CDCL":
            r = S.cadical(inst, time_limit=60.0)
            return {"cell": cell, "arm": arm, "seed": seed, "cdcl": r}
        tun = _load("retuned")[src]
        nov, ps = tuple(tun["NOV"]), tuple(tun["PS"])
        pols = _load("policies")
        out = []
        for r in range(5):
            rs = S.run_seed("test" if st == "ph" else st, cell, seed, r)
            if arm == "RNDO":
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, dict(pols["GO"], mode=1))
            elif arm == "STO":
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, _load("posthoc_policies")["STO"], static=True)
            elif arm == "NOV":
                res = S.run_fast(inst, "novelty_plus", nov, rs, cap)
            elif arm == "PS":
                res = S.run_fast(inst, "probsat_poly", ps, rs, cap)
            elif arm == "ST":
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, pols["ST"], static=True)
            else:
                pol = dict(pols[{"G": "G", "Gx": "G", "RND": "G", "GO": "GO"}[arm]])
                if arm == "Gx":
                    pol["beta"] = 0.5 if pol["beta"] == 0 else 0.0
                if arm == "RND":
                    pol["mode"] = 1
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, pol)
            out.append(_slim(res))
        return {"cell": cell, "arm": arm, "seed": seed, "runs": out}
    raise ValueError(st)
