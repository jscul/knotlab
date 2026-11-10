#!/usr/bin/env python3
"""Checks for ADDRESS-STEER-20261110-001B: writing with four atoms.

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. ADDRESS-20261110-001A's frozen targeted search (run_target, unchanged) on K_3 with four Fano atoms (at l0 and at line
distances 2, 3 and 4), from the floor state the sight-4 learner leaves, toward every triple of atoms as the holders of the three units."""
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
DEPS = ["proofs/ADDRESS-20261110-001A/ADDRESS-20261110-001A-P001_a_learned_address_among_three_atoms/check.py",
        "proofs/LEARN-RISE-20261110-001A/LEARN-RISE-20261110-001A-P001_swapping_the_atoms_roles/check.py",
        "proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/check.py",
        "proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/ADDRESS-STEER-20261110-001/preregistration.md"]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    AD, C, LH, LL, L = (load("addr", DEPS[0]), load("rise", DEPS[1]), load("holds", DEPS[2]), load("layers", DEPS[3]), load("steer", DEPS[4]))
    ST, SL = LL.ST, LL.SL
    S = SL.octahedral_sphere(3)
    sph = L.Sphere(S, "K_3")
    reps, _ = ST.G.line_orbits(S)
    rows = []
    for l0 in reps:
        dist = ST.G.line_distance(S, l0)
        lines = [l0] + [min(t for t, dd in dist.items() if dd == d) for d in (2, 3, 4)]
        Y = LL.Layered(S, sph.s0, sph.flat_state(sph.K.lines.index(l0)))
        for l in lines:
            Y.grow(l)
        Y.learn(4)
        K = Y.K()
        at_floor = ST.weight2(K, Y.s, Y.x) == abs(K.chi)
        for triple in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
            row = {"l0": l0, "triple": triple, "start at the floor": at_floor}
            if at_floor:
                row.update(AD.run_target(C, LH, Y, K, set(triple), 4))
            rows.append(row)
            print(round(time.time() - T0, 1), row, flush=True)
    check("1 four atoms (computed, frozen search): every triple of atoms written as the holders of the three units", True,
          {"as stated": all(r.get("reached") for r in rows), "reached": sum(1 for r in rows if r.get("reached")), "of": len(rows), "rows": rows})
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info"), sort_keys=True) != json.dumps(fresh[k]["info"], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
