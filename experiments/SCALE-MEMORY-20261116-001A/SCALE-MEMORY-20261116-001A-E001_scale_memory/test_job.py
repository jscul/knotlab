"""Shared-runner job: re-tuning and test cells of WHERE-NEXT-20261116-001A, copied and extended for
SCALE-MEMORY-20261116-001A (phase "scale": the new learned arms on the reused cells, and the n = 51200 cell; phase "retune"
with cells=c51200 re-tunes Novelty+ and sticky there).

Params:
  phase    retune | test | stress | cadical
  cells    (retune) pilot | stress;  rules  (retune) comma list, default all six
  tuning   tuning.json of the training-tuned rules (n = 800 training instances)
  retuned  (test, stress) retune analysis JSON: per cell and rule, the re-tuned params
  policies (test, stress) policies.json: per learned arm, the weights file chosen by validation
Every arm sees the same instances and the same run seed per instance, so the same initial state.
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

ALPHA = {"rand": 2.1, "local": 4.0}
CAP = {("rand", 200): 10**6, ("rand", 800): 10**7, ("rand", 3200): 2 * 10**8, ("rand", 12800): 2 * 10**9,
       ("rand", 51200): 2 * 10**9,
       ("local", 200): 10**6, ("local", 800): 2 * 10**7, ("local", 3200): 4 * 10**8}
PILOT_CELLS = [("rand", 200), ("rand", 800), ("rand", 3200), ("local", 200), ("local", 800), ("local", 3200)]
TEST_SEED0 = {"rand": 3_000_000, "local": 3_500_000}
RETUNE_SEED0 = {"rand": 4_000_000, "local": 4_500_000}
RULES = ["walksat", "probsat", "novelty_plus", "greedy_where", "sticky", "fms"]
LEARNED = {"L1": 0, "L2w": 1 | 8, "L2": 1, "L3": 1 | 2 | 4}
NEW_ARMS = [f"{a}_s{k}" for a in ("L3s", "L3m", "L3sm", "L2m", "L3c") for k in (0, 1)]
SCALE_CELLS = [("rand", 800, 100), ("rand", 3200, 100), ("local", 3200, 100), ("rand", 12800, 100), ("rand", 51200, 100)]
REUSED = {("rand", 12800): 50}  # WHERE-NEXT's stress cell already holds instances 0-49 for the rules and L3 (seed 1)

P = {}
_POL = {}


def setup(params):
    P.update(params)
    os.environ.setdefault("WHERE_NEXT_BUILD", str(Path.home() / ".cache" / "where_next_build"))
    import engine
    engine.lib()


def run_seed(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little")


def neighbours(rule: str, grid: list, best: dict) -> list:
    """The training-tuned optimum and its grid neighbours: five values for a one-parameter rule (probSAT: the
    poly form's cb), the optimum and its index neighbours in each parameter for a two-parameter rule."""
    if rule == "probsat":
        grid = [r for r in grid if r["algo"] == "probsat_poly"]
        if best["algo"] != "probsat_poly":
            best = min(grid, key=lambda r: r["mean_log_flips"])
    params = [tuple(r["params"]) for r in grid]
    algo = grid[0]["algo"]
    b = tuple(best["params"])
    free = [i for i in range(len(b)) if len({p[i] for p in params}) > 1]
    if len(free) == 1:
        vals = sorted({p[free[0]] for p in params})
        j = vals.index(b[free[0]])
        lo = max(0, min(j - 2, len(vals) - 5))
        pick = vals[lo:lo + 5]
        out = []
        for v in pick:
            q = list(b)
            q[free[0]] = v
            out.append(tuple(q))
        return [(algo, q) for q in out]
    out = [b]
    for i in free:
        vals = sorted({p[i] for p in params})
        j = vals.index(b[i])
        for jj in (j - 1, j + 1):
            if 0 <= jj < len(vals):
                q = list(b)
                q[i] = vals[jj]
                out.append(tuple(q))
    return [(algo, q) for q in out]


def tuned(rule: str) -> tuple:
    t = json.loads(Path(P["tuning"]).read_text())[rule]["best"]
    return t["algo"], tuple(t["params"])


def cases():
    phase = P["phase"]
    if phase == "retune":
        T = json.loads(Path(P["tuning"]).read_text())
        cells = {"pilot": PILOT_CELLS, "stress": [("rand", 12800)], "c51200": [("rand", 51200)]}[P.get("cells", "pilot")]
        rules = P["rules"].split(",") if P.get("rules") else RULES
        for fam, n in cells:
            for rule in rules:
                for algo, prm in neighbours(rule, T[rule]["grid"], T[rule]["best"]):
                    for i in range(16):
                        s = RETUNE_SEED0[fam] + i
                        yield (f"retune|{fam}|{n}|{rule}|{algo}|{','.join(map(str, prm))}|{s}",
                               {"fam": fam, "n": n, "seed": s, "arm": rule, "algo": algo, "params": list(prm),
                                "cap": CAP[(fam, n)]})
    elif phase == "cadical":
        for n, count in ((200, 20), (400, 20), (600, 20)):
            for i in range(count):
                s = TEST_SEED0["rand"] + i
                yield f"cadical|rand|{n}|{s}", {"fam": "rand", "n": n, "seed": s, "arm": "A5", "algo": "cadical"}
    elif phase == "scale":
        R = json.loads(Path(P["retuned"]).read_text())
        for fam, n, count in SCALE_CELLS:
            base = [(a, "policy", []) for a in NEW_ARMS] + [("L3_s0", "policy", [])]
            extra = []  # arms WHERE-NEXT did not run on these instances
            if n in (12800, 51200):
                extra.append(("L3_s1", "policy", []))
                for rule in R["stress_rules"]:
                    algo, prm = tuned(rule)
                    extra.append((f"{rule}@train", algo, list(prm)))
                    ra, rp = R["cells"][f"{fam}|{n}"][rule]
                    extra.append((f"{rule}@cell", ra, list(rp)))
            for i in range(count):
                s = TEST_SEED0[fam] + i
                arms = base + (extra if i >= REUSED.get((fam, n), 0) else [])
                for name, algo, prm in arms:
                    yield (f"scale|{fam}|{n}|{name}|{s}",
                           {"fam": fam, "n": n, "seed": s, "arm": name, "algo": algo, "params": prm, "cap": CAP[(fam, n)]})
    elif phase in ("test", "stress"):
        R = json.loads(Path(P["retuned"]).read_text())
        cells = PILOT_CELLS if phase == "test" else [("rand", 12800)]
        count = {"test": 100, "stress": 50}[phase]
        for fam, n in cells:
            arms = []
            if phase == "test" and n == 200:
                arms.append(("A0", "rw", []))
            rules = RULES if phase == "test" else R["stress_rules"]
            for rule in rules:
                algo, prm = tuned(rule)
                arms.append((f"{rule}@train", algo, list(prm)))
                ra, rp = R["cells"][f"{fam}|{n}"][rule]
                if (ra, tuple(rp)) != (algo, prm) or phase == "stress":
                    arms.append((f"{rule}@cell", ra, list(rp)))
            for arm in LEARNED:
                arms.append((arm, "policy", []))
            for i in range(count):
                s = TEST_SEED0[fam] + i
                for name, algo, prm in arms:
                    yield (f"{phase}|{fam}|{n}|{name}|{s}",
                           {"fam": fam, "n": n, "seed": s, "arm": name, "algo": algo, "params": prm,
                            "cap": CAP[(fam, n)]})
    else:
        raise ValueError(phase)


def policy(arm: str):
    import numpy as np
    if arm not in _POL:
        pol = json.loads(Path(P["policies"]).read_text())[arm]
        _POL[arm] = (np.load(pol["theta"]), int(pol["flags"]), tuple(pol["what_params"]))
    return _POL[arm]


def run(case_id, payload):
    import engine as E
    fam, n, s = payload["fam"], payload["n"], payload["seed"]
    inst = E.planted(fam, n, ALPHA[fam], s)
    if payload["algo"] == "cadical":
        r = E.cadical(inst, float(P.get("cadical_limit", 600)))
        return {"fam": fam, "n": n, "seed": s, "arm": "A5", **r}
    rs = run_seed("test", fam, n, s)
    if payload["algo"] == "policy":
        th, flags, wp = policy(payload["arm"])
        r = E.run(inst, "policy", wp, theta=th, flags=flags, seed=rs, max_flips=payload["cap"])
    else:
        r = E.run(inst, payload["algo"], tuple(payload["params"]), seed=rs, max_flips=payload["cap"])
    r.pop("state", None)
    score = math.log(r["flips"]) if r["solved"] else math.log(payload["cap"]) + math.log1p(r["minviol"])
    return {"fam": fam, "n": n, "seed": s, "arm": payload["arm"], "algo": payload["algo"],
            "params": payload["params"], "cap": payload["cap"], "score": score, **r}
