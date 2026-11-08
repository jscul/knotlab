#!/usr/bin/env python3
"""One size past LAST-BIT-20261108-001B: exhaustive extension of every off-law labelled parent collar of s = 10101 / 00110 that
survived it (153 non-pinwheel collars and 50 pinwheel collars with labels the law does not list) to tile distance 3, then 4.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/CRYSTAL-UP-20261108-001/stress_distance4.py
LAST-BIT-20261108-001B tested only the non-pinwheel collars, at distance 2 (3 on a sample of 16). The first step of a forcing proof
needs every off-law parent collar to die, the off-law pinwheel collars included: a parent tiling whose collars are pinwheel collars
with other labels obeys the collar law but not the labelled one, so the argument cannot be repeated one level up. Starting from
that ticket's survivors (its survivors.json and the law's own labelled keys), each round tests every off-law collar still alive at
the current distance with its forcing_lib (unchanged; a collar that reaches the step budget is kept), removes the dead, reruns the
joint test, and repeats until nothing dies; then the distance goes up. Writes stress_distance4.json beside this file after each
round."""
import importlib.util
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LB = ROOT / "proofs/LAST-BIT-20261108-001B/LAST-BIT-20261108-001B-P001_geometry_alone"
spec = importlib.util.spec_from_file_location("last_bit_b_check", LB / "check.py")
CB = importlib.util.module_from_spec(spec)
sys.modules["last_bit_b_check"] = CB
spec.loader.exec_module(CB)
F = CB.F
OUT = HERE / "stress_distance4.json"
WORKERS = 10
BUDGET = {3: 20000, 4: 60000}


def job(args):
    yi, p, depth, budget = args
    key = (1, frozenset(zip(F.G["sets"][yi], p)))
    return (yi, p), F.extends(CB.X["keys"], key, depth, budget)


def main():
    t0 = time.time()
    F.setup(WORKERS)
    L = F.law_as_sets(CB.SIG)
    Q = F.Q_of(L, CB.SIG)
    surv = json.loads((LB / "survivors.json").read_text())
    sk, core = F.G["sk"], F.G["core"]
    alive = {(yi, p): False for yi, ps in Q.items() for p in ps}
    for yi, (Y, iskey) in enumerate(core):
        if iskey:
            for p in L.get(sk.index[(1, Y)], ()):
                alive[(yi, tuple(p))] = True
    for yi, p in surv["non-keys"] + surv["keys outside L(s)"]:
        assert (yi, tuple(p)) in alive
        alive[(yi, tuple(p))] = True
    before = sum(alive.values())
    alive = F.joint(Q, alive)
    out = {"start: in L(s), keys outside L(s), non-keys": [len(x) for x in CB.survivors_split(alive, L)],
           "start is a fixed point of the joint test": sum(alive.values()) == before, "rounds": [], "done": False,
           "setup seconds": round(time.time() - t0, 1)}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    for depth in (3, 4):
        while True:
            _, keyout, nonkey = CB.survivors_split(alive, L)
            CB.X["keys"] = F.keys_from(alive)
            todo = [(yi, p, depth, BUDGET[depth]) for yi, p in nonkey + keyout]
            with mp.Pool(WORKERS) as pool:
                res = dict(pool.map(job, todo, chunksize=1))
            dead = [k for k, r in res.items() if r is False]
            out["rounds"].append({"distance": depth, "tested: keys outside L(s), non-keys": [len(keyout), len(nonkey)],
                                  "died: keys outside L(s), non-keys": [sum(1 for k in keyout if res[k] is False), sum(1 for k in nonkey if res[k] is False)],
                                  "budget reached": sum(1 for r in res.values() if r is None), "seconds": round(time.time() - t0, 1)})
            OUT.write_text(json.dumps(out, indent=1) + "\n")
            if not dead:
                break
            for k in dead:
                alive[k] = False
            alive = F.joint(Q, alive)
        inL, keyout, nonkey = CB.survivors_split(alive, L)
        out["after distance %d: in L(s), keys outside L(s), non-keys" % depth] = [len(inL), len(keyout), len(nonkey)]
        out["survivors after distance %d" % depth] = {"non-keys": [[yi, list(p)] for yi, p in nonkey],
                                                      "keys outside L(s)": [[yi, list(p)] for yi, p in keyout]}
        OUT.write_text(json.dumps(out, indent=1) + "\n")
    _, keyout, nonkey = CB.survivors_split(alive, L)
    out.update({"done": True, "seconds": round(time.time() - t0, 1),
                "first step of the forcing proof holds (no off-law parent collar survives)": not keyout and not nonkey})
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if not k.startswith("survivors")}, indent=1))


if __name__ == "__main__":
    main()
