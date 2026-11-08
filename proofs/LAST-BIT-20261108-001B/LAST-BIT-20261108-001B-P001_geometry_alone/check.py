#!/usr/bin/env python3
"""Check for LAST-BIT-20261108-001B-P001: a forcing test on geometry alone for the last one-bit decoration, s = 10101 / 00110.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B check.py      (writes result.json and survivors.json)

With forcing_lib.py beside it:
  1. parents: at level 0, can the five children of any core collar's centre avoid s(0) and s(1)? (SAT)
  2. S1: the labelled level-one collars surviving the joint test (ONE-BIT-20261108-001A's method);
  3. extension: every non-key survivor is tested by exhaustive extension to tile distance 2 with the current survivors as the law;
     the dead are removed, the joint test is rerun, and the extension is repeated on the remaining non-keys until nothing dies;
  4. a sample of the final non-key survivors is tested at distance 3 (a record of the trend, with a step budget).
Controls: for the constant decoration 00000 / 11111, which admits the rhombus crystal, the rhombus lattice's collar (with a labelling
that occurs on the crystal) is in S1 and survives extension at distance 2; every labelled key of L(s) survives the joint test."""
from __future__ import annotations

import json
import multiprocessing as mp
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import forcing_lib as F  # noqa: E402

SIG = ((1, 0, 1, 0, 1), (0, 0, 1, 1, 0))
CONST = ((0, 0, 0, 0, 0), (1, 1, 1, 1, 1))
X = {}


def ext_job(args):
    yi, p, depth, budget = args
    key = (1, frozenset(zip(F.G["sets"][yi], p)))
    return (yi, p), F.extends(X["keys"], key, depth, budget)


def survivors_split(alive, L):
    core, sk = F.G["core"], F.G["sk"]
    inL, keyout, nonkey = [], [], []
    for (yi, p), ok in alive.items():
        if not ok:
            continue
        Y, iskey = core[yi]
        if not iskey:
            nonkey.append((yi, p))
        elif p in L.get(sk.index[(1, Y)], set()):
            inL.append((yi, p))
        else:
            keyout.append((yi, p))
    return inL, keyout, nonkey


def run_extension(alive, Q, L, depth, budget, rounds_log):
    while True:
        _, _, nonkey = survivors_split(alive, L)
        X["keys"] = F.keys_from(alive)
        with mp.Pool(16) as pool:
            res = pool.map(ext_job, [(yi, p, depth, budget) for yi, p in nonkey], chunksize=1)
        dead = [k for k, r in res if r is False]
        undecided = sum(1 for _, r in res if r is None)
        rounds_log.append({"non-key tested": len(nonkey), "died": len(dead), "budget reached": undecided})
        if not dead:
            return alive
        for k in dead:
            alive[k] = False
        alive = F.joint(Q, alive)


def main():
    t0 = time.time()
    F.setup(16)
    res = {"checks": {}, "controls": {}, "census": {"setup seconds": round(time.time() - t0, 1)}}
    L = F.law_as_sets(SIG)
    res["census"]["parents free at level 0"] = F.parents_forced(L, SIG)
    Q = F.Q_of(L, SIG)
    alive = F.joint(Q)
    inL, keyout, nonkey = survivors_split(alive, L)
    res["census"]["S1 after the joint test: in L(s), keys outside L(s), non-keys"] = [len(inL), len(keyout), len(nonkey)]
    res["controls"]["every labelled key of L(s) survives the joint test"] = all(
        alive.get((yi, p)) for yi, (Y, iskey) in enumerate(F.G["core"]) if iskey for p in L.get(F.G["sk"].index[(1, Y)], ()))
    log = []
    alive = run_extension(alive, Q, L, 2, 20000, log)
    inL, keyout, nonkey = survivors_split(alive, L)
    res["census"]["extension rounds at distance 2"] = log
    res["census"]["after extension at distance 2: in L(s), keys outside L(s), non-keys"] = [len(inL), len(keyout), len(nonkey)]
    random.seed(1)
    sample = random.sample(nonkey, min(16, len(nonkey)))
    X["keys"] = F.keys_from(alive)
    with mp.Pool(16) as pool:
        r3 = pool.map(ext_job, [(yi, p, 3, 6000) for yi, p in sample], chunksize=1)
    res["census"]["distance 3 on a sample of the final non-keys: extends, dies, budget"] = [
        sum(1 for _, r in r3 if r is True), sum(1 for _, r in r3 if r is False), sum(1 for _, r in r3 if r is None)]
    res["checks"]["parents are forced at level 0"] = res["census"]["parents free at level 0"] == 0
    res["census"]["the first step of the forcing proof holds (no non-key survivor)"] = len(nonkey) == 0
    (HERE / "survivors.json").write_text(json.dumps({
        "about": "Labelled level-one collars (core collar index in COLLAR-PLANE-20261108-001B's level_one_law.json order of core collars, "
                 "labels in canonical tile order) surviving the joint test and extension at distance 2, for s = 10101 / 00110.",
        "non-keys": [[yi, list(p)] for yi, p in nonkey], "keys outside L(s)": [[yi, list(p)] for yi, p in keyout]}) + "\n")
    # control: the constant decoration keeps the rhombus collar
    Lc = F.law_as_sets(CONST)
    Qc = F.Q_of(Lc, CONST)
    ac = F.joint(Qc)
    plane = F.D.Plane(F.G["sk"], F.D.RHOMBUS, F.D.RHOMBUS_LATTICE)
    rh = F.G["sets"].index(F.G["sk"].types[plane.root[0][0]][1])
    rh_alive = [p for (yi, p), ok in ac.items() if ok and yi == rh]
    X["keys"] = F.keys_from(ac)
    ok_ext = False
    for p in rh_alive[:4]:
        if F.extends(X["keys"], (1, frozenset(zip(F.G["sets"][rh], p))), 2, 20000) is True:
            ok_ext = True
            break
    res["controls"]["the constant decoration keeps the rhombus collar through extension at distance 2"] = bool(rh_alive) and ok_ext
    res["status"] = "passed" if all(res["checks"].values()) and all(res["controls"].values()) else "failed"
    res["failures"] = [k for k, v in {**res["checks"], **res["controls"]}.items() if not v]
    res["runtime_seconds"] = round(time.time() - t0, 1)
    (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
