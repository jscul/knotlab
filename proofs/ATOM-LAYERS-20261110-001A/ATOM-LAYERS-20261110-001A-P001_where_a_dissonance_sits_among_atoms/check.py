#!/usr/bin/env python3
"""Checks for ATOM-LAYERS-20261110-001A: where a dissonance sits among atoms.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, PYTHONHASHSEED=0. Check 1 confirms B1 on every genus-2 floor state reached; checks 2-4 are computations."""
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import layers_lib as LL  # noqa: E402

ST, SL = LL.ST, LL.SL
T0 = time.time()
OUT = {}
DEPS = ["proofs/GROW-STUCK-20261110-001A/GROW-STUCK-20261110-001A-P001_a_learner_that_grows_only_when_stuck/stuck_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/ATOM-LAYERS-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok and not os.environ.get("NOEXIT"):
        sys.exit(1)


def kinds(defs):
    """which levels hold dissonance: a set of 'upper', 'lower', 'junction'"""
    return sorted({"lower" if lv.startswith("atom") else lv for (_, lv), c in defs.items() if c})


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    spec = importlib.util.spec_from_file_location("steer_lib", ROOT / DEPS[1])
    L = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(L)
    rows, b1 = [], []
    for k in (2, 3):
        S = SL.octahedral_sphere(k)
        sph = L.Sphere(S, f"K_{k}")
        reps, _ = ST.G.line_orbits(S)
        for l0 in reps:
            dist = ST.G.line_distance(S, l0)
            at = {d: min(t for t, dd in dist.items() if dd == d) for d in (1, 2, 3)}
            configs = [("at l0", [l0]), ("away (d = 2)", [at[2]]), ("at l0 and d = 1", [l0, at[1]]), ("at l0 and d = 2", [l0, at[2]]),
                       ("at l0 and d = 3", [l0, at[3]]), ("away (d = 2 and 3)", [at[2], at[3]])]
            x = sph.flat_state(sph.K.lines.index(l0))
            for name, lam in configs:
                Y = LL.Layered(S, sph.s0, x)
                for l in lam:
                    Y.grow(l)
                K = Y.K()
                w_start = ST.weight2(K, Y.s, Y.x) / 2
                path = Y.learn(4)
                K = Y.K()
                w_end = ST.weight2(K, Y.s, Y.x) / 2
                floor = abs(K.chi) / 2
                visited = sorted({lv for d in path for lv in kinds(d)})
                row = {"sphere": f"K_{k}", "l0": l0, "atoms": name, "genus": len(lam), "W start": w_start, "W end": w_end, "floor": floor,
                       "sign changes": len(path) - 1, "start levels": kinds(path[0]), "end levels": kinds(path[-1]),
                       "levels visited": visited, "end defects": {"%s, %s" % kk: v for kk, v in sorted(path[-1].items())}}
                if len(lam) == 2:
                    row["hosts"] = dict(Y.hosts())
                    if w_end == floor:
                        steps = ST.steps_at(Y.S, K, Y.s, Y.x)
                        viol, agree = ST.tally(K, Y.s, Y.x)
                        b1.append(not steps and not viol and sorted(agree).count(3) == 1 and all(a in (1, 3) for a in agree))
                rows.append(row)
            print("  K_%d line %d" % (k, l0), round(time.time() - T0, 1), flush=True)
    check("1 B1: every genus-2 floor state the learner reached has no violated line, exactly one face with three agreeing corners, every "
          "other face one, and no learning step", all(b1), {"floor states": len(b1), "hold": sum(b1)})
    g2 = [r for r in rows if r["genus"] == 2]
    check("2 B2 (computed): on every genus-2 space the faces that can hold the floor unit, by level", True,
          {"spaces with upper hosts": sum(1 for r in g2 if r["hosts"].get("upper")), "spaces with atom hosts": sum(1 for r in g2 if r["hosts"].get("atom")),
           "of": len(g2), "hosts by space": [(r["sphere"], r["l0"], r["atoms"], r["hosts"]) for r in g2]})
    g1 = [r for r in rows if r["genus"] == 1]
    check("3 B3 (computed): one atom, at l0 or away: resolved, and the levels the dissonance visited", True,
          {"resolved": sum(1 for r in g1 if r["W end"] == 0), "of": len(g1),
           "(atoms, start levels, levels visited)": {str(kk): v for kk, v in Counter((r["atoms"], tuple(r["start levels"]), tuple(r["levels visited"])) for r in g1).items()}})
    check("4 B4 (computed): two atoms: whether the learner reaches the floor, and where the remaining dissonance ends", True,
          {"reached the floor": sum(1 for r in g2 if r["W end"] == r["floor"]), "of": len(g2),
           "(atoms, end levels)": {str(kk): v for kk, v in Counter((r["atoms"], tuple(r["end levels"])) for r in g2).items()},
           "rows": rows})
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [kk for kk in OUT if kk != "seconds" and json.dumps(old.get(kk, {}).get("info"), sort_keys=True)
                != json.dumps(fresh[kk]["info"], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
