"""Shared-runner job for EARN-BUDGET-20261117-001A, one stage per launch (--param stage=...).

  retune   R1: NOV (48 settings) and PS (10) on 8 tuning instances per cell, 3 runs each
  policy   P1: on rand 2.1, block 2.5 and local w10 at n = 800, 8 instances x 3 runs each: the 90 earned-budget settings
           (E, Erb), the 15 fixed batched settings (Gb), SLOW-LOOP's 48 fixed settings (Gm) and its 8 static settings (ST),
           with NOV from the same initial states ("base")
  oracle   O1: the 15 fixed batched settings on each test cell's own tuning instances (n = 3200), 8 x 3 runs, with NOV
           from the same initial states: the per-cell oracle GbO
  test     T1: the frozen arms on 50 fresh test instances per cell, 5 runs each; CDCL on 20 instances of each new local
           pattern
  retune12800  R2: NOV and PS re-tuned for the stress cells over the 3200 choice and its grid neighbours, 8 x 3 runs
  stress   T2: local w20 and heavy at n = 12800, 20 instances, NOV, PS (re-tuned by R2), E, Erb, Gb and ST

Params: stage; retuned (R1's choice) for policy/test/stress; policies (P1's choice) for test/stress; slow_loop_policies
(SLOW-LOOP-20261117-001A's policies.json, for G and GO) for test.
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
    ("local35-w15-3200", "local", 3.5, 15, 3200, 2 * 10**8),
    ("rand3-3200", "rand", 3.0, 10, 3200, 2 * 10**8),
    ("local-w20-3200", "local", 4.0, 20, 3200, 2 * 10**8),
    ("local3-w10-3200", "local", 3.0, 10, 3200, 2 * 10**8),
    ("heavy-3200", "heavy", 3.0, 10, 3200, 2 * 10**8),
    ("local-w40-3200", "local", 4.0, 40, 3200, 2 * 10**8),
    ("embed-3200", "embed", 0.0, 10, 3200, 2 * 10**8),
    ("local-w10-3200", "local", 4.0, 10, 3200, 2 * 10**8),
    ("rand-3200", "rand", 2.1, 10, 3200, 2 * 10**8),
    ("block-3200", "block", 2.5, 20, 3200, 2 * 10**8),
]
TUNE_CELLS = [
    ("rand-800", "rand", 2.1, 10, 800, 2 * 10**7),
    ("block-800", "block", 2.5, 20, 800, 2 * 10**7),
    ("local-w10-800", "local", 4.0, 10, 800, 2 * 10**7),
]
STRESS_CELLS = [
    ("local-w20-12800", "local", 4.0, 20, 12800, 2 * 10**9, "local-w20-3200"),
    ("heavy-12800", "heavy", 3.0, 10, 12800, 2 * 10**9, "heavy-3200"),
]
ALL = {c[0]: c for c in CELLS + TUNE_CELLS}
NOV_GRID = [(nz, wp) for nz in (0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9) for wp in (0.0, 0.005, 0.01, 0.02, 0.05, 0.1)]
PS_GRID = [(cb, 1.0) for cb in (0.6, 0.8, 1.0, 1.4, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0)]
EARN_GRID = [{"e": 1.0, "beta": 0.0, "J": 2, "pb": 4000, "backoff": False, "mode": 1, "earn": True, "theta": th,
              "rho_max": rmax, "rho_min": rmin, "rb": rb}
             for th in (0.01, 0.03, 0.1, 0.3, 1.0) for rmax in (3.0, 1.0, 0.3) for rmin in (0.03, 0.01)
             for rb in (0.003, 0.01, 0.03)]
FIXB_GRID = [{"e": 1.0, "rho": rho, "beta": 0.0, "J": 2, "pb": 4000, "backoff": False, "mode": 1, "rb": rb}
             for rho in (3.0, 1.0, 0.3, 0.1, 0.03) for rb in (0.003, 0.01, 0.03)]
SL_GRID = [{"e": e, "rho": rho, "beta": beta, "J": 2, "pb": 4000, "backoff": bo, "mode": 0}
           for e in (1.0, 4.0, 16.0) for rho in (0.03, 0.1, 0.3, 1.0) for beta in (0.0, 0.5) for bo in (True, False)]
STATIC_GRID = [{"e": 1.0, "rho": 0.0, "beta": beta, "J": 2, "pb": 4000, "backoff": False, "mode": 2, "passes": ps,
                "abort": ab} for ps in (1, 8) for beta in (0.0, 0.5) for ab in (0.0, 0.05)]
GRIDS = {"earn": EARN_GRID, "fixb": FIXB_GRID, "sl": SL_GRID, "st": STATIC_GRID}
EMBED = {"frac": 0.25, "alpha_r": 2.1, "alpha_l": 4.0, "alpha_c": 0.02, "w": 10}
CDCL_CELLS = ("local35-w15-3200", "local-w20-3200", "local3-w10-3200")
TUNE_CAP = 2 * 10**7
SEED_TUNE, SEED_POLICY, SEED_TEST, SEED_STRESS = 8_500_000, 8_000_000, 8_100_000, 8_200_000
ARMS = ["NOV", "PS", "E", "Erb", "ErbL", "Gb", "GbO", "Gm", "ST", "G", "GO"]


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
        for name, *_ in CELLS + TUNE_CELLS:
            for i in range(8):
                for j, prm in enumerate(NOV_GRID):
                    yield f"retune|{name}|NOV|{j}|{i}", {"cell": name, "algo": "novelty_plus", "prm": prm, "i": i}
                for j, prm in enumerate(PS_GRID):
                    yield f"retune|{name}|PS|{j}|{i}", {"cell": name, "algo": "probsat_poly", "prm": prm, "i": i}
    elif st == "policy":
        for name, *_ in TUNE_CELLS:
            for i in range(8):
                yield f"policy|{name}|base|{i}", {"cell": name, "grid": "base", "k": -1, "i": i}
                for g, grid in GRIDS.items():
                    for k in range(len(grid)):
                        yield f"policy|{name}|{g}{k}|{i}", {"cell": name, "grid": g, "k": k, "i": i}
    elif st == "oracle":
        for name, *_ in CELLS:
            for i in range(8):
                yield f"oracle|{name}|base|{i}", {"cell": name, "grid": "base", "k": -1, "i": i}
                for k in range(len(FIXB_GRID)):
                    yield f"oracle|{name}|fixb{k}|{i}", {"cell": name, "grid": "fixb", "k": k, "i": i}
    elif st == "retune12800":
        tun = _load("retuned")
        for name, fam, a, w, n, cap, src in STRESS_CELLS:
            for tag, algo, grid in (("NOV", "novelty_plus", NOV_GRID), ("PS", "probsat_poly", PS_GRID)):
                for prm in neighbours(grid, tuple(tun[src][tag])):
                    j = grid.index(prm)
                    for i in range(8):
                        yield f"retune12800|{name}|{tag}|{j}|{i}", {"cell": name, "algo": algo, "prm": prm, "i": i}
    elif st == "test":
        for name, *_ in CELLS:
            for arm in ARMS:
                for i in range(50):
                    yield f"test|{name}|{arm}|{i}", {"cell": name, "arm": arm, "i": i}
            if name in CDCL_CELLS:
                for i in range(20):
                    yield f"test|{name}|CDCL|{i}", {"cell": name, "arm": "CDCL", "i": i}
    elif st == "stress":
        for name, *_ in STRESS_CELLS:
            for arm in ("NOV", "PS", "E", "Erb", "Gb", "ST"):
                for i in range(20):
                    yield f"stress|{name}|{arm}|{i}", {"cell": name, "arm": arm, "i": i}
    else:
        raise ValueError(st)


def neighbours(grid, center):
    """The center and its neighbours along each axis of a product grid (NOV: noise and walk probability; PS: cb)."""
    axes = [sorted({g[d] for g in grid}) for d in range(len(center))]
    out = [tuple(center)]
    for d, ax in enumerate(axes):
        if len(ax) < 2:
            continue
        i = ax.index(center[d])
        for j in (i - 1, i + 1):
            if 0 <= j < len(ax):
                c = list(center)
                c[d] = ax[j]
                if tuple(c) in grid:
                    out.append(tuple(c))
    return out


def _inst(cell, seed):
    import slow_loop as S
    if cell in ALL:
        _, fam, a, w, n, cap = ALL[cell]
    else:
        _, fam, a, w, n, cap, _src = {c[0]: c for c in STRESS_CELLS}[cell]
    if fam == "embed":
        return S.planted_embed(n, seed, **EMBED), cap
    return S.planted(fam, n, a, seed, w=w), cap


def _slim(r):
    keep = ("flips", "solved", "verified", "work", "work_fast", "work_slow", "work_rebuild", "cpu", "cpu_fast",
            "cpu_slow", "cpu_rebuild", "minviol", "epochs", "rebuilds", "targets", "ties", "shadows", "n_final", "m_final",
            "contradiction", "rho_top", "doublings")
    return {k: r[k] for k in keep if k in r}


def run(case_id, payload):
    import slow_loop as S
    st = P["stage"]
    cell, i = payload["cell"], payload["i"]
    if st in ("retune", "retune12800"):
        seed = SEED_TUNE + i
        inst, _ = _inst(cell, seed)
        out = [_slim(S.run_fast(inst, payload["algo"], tuple(payload["prm"]), S.run_seed("retune", cell, seed, r),
                                TUNE_CAP)) for r in range(3)]
        return {"cell": cell, "algo": payload["algo"], "prm": payload["prm"], "seed": seed, "runs": out}
    if st in ("policy", "oracle"):
        seed = (SEED_POLICY if st == "policy" else SEED_TUNE) + i
        inst, cap = _inst(cell, seed)
        nov = tuple(_load("retuned")[cell]["NOV"])
        g, k = payload["grid"], payload["k"]
        out = []
        for r in range(3):
            rs = S.run_seed(st, cell, seed, r)
            if g == "base":
                out.append(_slim(S.run_fast(inst, "novelty_plus", nov, rs, cap)))
            else:
                out.append(_slim(S.run_slow(inst, "novelty_plus", nov, rs, cap, GRIDS[g][k], static=(g == "st"))))
        return {"cell": cell, "grid": g, "k": k, "seed": seed, "runs": out}  # policy and oracle
    if st in ("test", "stress"):
        arm = payload["arm"]
        if st == "test":
            seed, src = SEED_TEST + i, cell
        else:
            seed, src = SEED_STRESS + i, {c[0]: c for c in STRESS_CELLS}[cell][6]
        inst, cap = _inst(cell, seed)
        if arm == "CDCL":
            return {"cell": cell, "arm": arm, "seed": seed, "cdcl": S.cadical(inst, time_limit=60.0)}
        tun = _load("retuned")[src] if st == "test" else _load("retuned12800")[cell]
        nov, ps = tuple(tun["NOV"]), tuple(tun["PS"])
        pols = _load("policies")
        out = []
        for r in range(5):
            rs = S.run_seed(st, cell, seed, r)
            if arm == "NOV":
                res = S.run_fast(inst, "novelty_plus", nov, rs, cap)
            elif arm == "PS":
                res = S.run_fast(inst, "probsat_poly", ps, rs, cap)
            elif arm == "ST":
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, pols["ST"], static=True)
            elif arm in ("G", "GO"):
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, _load("slow_loop_policies")[arm])
            elif arm == "GbO":
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, _load("oracle_policies")[cell])
            else:
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, pols[arm])
            out.append(_slim(res))
        return {"cell": cell, "arm": arm, "seed": seed, "runs": out}
    raise ValueError(st)
