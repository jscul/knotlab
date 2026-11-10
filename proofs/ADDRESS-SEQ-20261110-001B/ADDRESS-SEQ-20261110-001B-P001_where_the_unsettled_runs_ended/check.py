#!/usr/bin/env python3
"""Checks for ADDRESS-SEQ-20261110-001B: where the unsettled runs of ADDRESS-STEER-20261110-001C ended.

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Repeats ADDRESS-STEER-20261110-001C's loop exactly (random.Random(86), same order and moves) and records, for every run that
did not end with the written pair acting, its end: the acting atoms, the levels of the faces holding units, W, whether each acting atom's region
holds a unit (the exact rule of ADDRESS-STEER-20261110-001A), and for runs above the floor whether any move would still lower W."""
import importlib.util
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    RA = load("read", "proofs/READ-ADDRESS-20261110-001A/READ-ADDRESS-20261110-001A-P001_writing_at_k4_and_reading_from_the_law/check.py")
    AD = load("addr", "proofs/ADDRESS-20261110-001A/ADDRESS-20261110-001A-P001_a_learned_address_among_three_atoms/check.py")
    C = load("rise", "proofs/LEARN-RISE-20261110-001A/LEARN-RISE-20261110-001A-P001_swapping_the_atoms_roles/check.py")
    LH = load("holds", "proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/check.py")
    LL = load("layers", "proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py")
    L = load("steer", "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
    RULE = load("rule", "proofs/ADDRESS-STEER-20261110-001A/ADDRESS-STEER-20261110-001A-P001_the_rule_behind_the_exception/check.py")
    ST, SL = LL.ST, LL.SL
    rng = random.Random(86)
    ends, counts = [], Counter()
    for kk in (3, 4):
        S = SL.octahedral_sphere(kk)
        sph = L.Sphere(S, f"K_{kk}")
        reps, _ = ST.G.line_orbits(S)
        for l0 in reps:
            dist = ST.G.line_distance(S, l0)
            at = {d: min(t for t, dd in dist.items() if dd == d) for d in (2, 3)}
            Y = LL.Layered(S, sph.s0, sph.flat_state(sph.K.lines.index(l0)))
            for l in (l0, at[2], at[3]):
                Y.grow(l)
            Y.learn(4)
            K = Y.K()
            P = C.Space(K, Y.S)
            floor2 = abs(K.chi)
            levels = [Y.face_level(v) for v in range(K.V)]
            upper_points = [p for p in range(K.n) if Y.levels[K.points[p]] == "U"]
            for pair in ((0, 1), (0, 2), (1, 2)):
                found, _ = RA.search(AD, C, LH, Y, K, set(pair), 3)
                if not found:
                    continue
                written_acting = tuple(j for j in range(3) if LH.atom_role(K, Y, [(found[0] >> e) & 1 for e in range(3 * K.n)], j) == "line")
                for k in (1, 2, 3):
                    for _ in range(10):
                        s, x = found
                        for p in rng.sample(upper_points, k):
                            x ^= 1 << p
                        for _ in range(200):
                            vi, ag, w = P.full(s, x)
                            if w == floor2:
                                break
                            nb = P.neighbours(s, x, vi, ag, w)
                            low = [m for m in nb if m[3] < w]
                            keep = [m for m in nb if m[3] == w]
                            pick = low or keep
                            if not pick:
                                break
                            _, s, x, _ = rng.choice(pick)
                        vi, ag, w = P.full(s, x)
                        sl = [(s >> e) & 1 for e in range(3 * K.n)]
                        act = tuple(j for j in range(3) if LH.atom_role(K, Y, sl, j) == "line")
                        kept = w == floor2 and act == written_acting
                        counts[(k, "kept" if kept else "at the floor, changed" if w == floor2 else "above the floor")] += 1
                        if kept:
                            continue
                        units = sorted(levels[v] for v in range(K.V) if ag[v] >= 3)
                        rule = all(any(j in RULE.face_atoms(Y, v) for v in range(K.V) if ag[v] >= 3) for j in act)
                        nb = P.neighbours(s, x, vi, ag, w)
                        ends.append({"sphere": f"K_{kk}", "l0": l0, "written pair": pair, "written acting": written_acting, "k": k,
                                     "W": w / 2, "floor": floor2 / 2, "acting at the end": act, "unit faces": units,
                                     "each acting atom holds a unit": rule, "moves lowering W left": sum(1 for m in nb if m[3] < w),
                                     "violated lines": sum(vi)})
            print(round(time.time() - T0, 1), f"K_{kk}", l0, flush=True)
    floor_changed = [e for e in ends if e["W"] == e["floor"]]
    above = [e for e in ends if e["W"] > e["floor"]]
    OUT["1 B (computed)"] = {"pass": True, "info": {
        "outcomes by k": {"%d: %s" % kk_: v for kk_, v in sorted(counts.items())},
        "changed at the floor": len(floor_changed), "rule holds there": sum(e["each acting atom holds a unit"] for e in floor_changed),
        "acting atoms lost there": Counter("%s -> %s" % (e["written acting"], e["acting at the end"]) for e in floor_changed),
        "above the floor": len(above), "with no move lowering W": sum(1 for e in above if e["moves lowering W left"] == 0),
        "W above the floor": Counter(e["W"] - e["floor"] for e in above), "ends": ends}}
    print(json.dumps(OUT["1 B (computed)"]["info"], default=str)[:1500])
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        same = json.dumps(old["1 B (computed)"]["info"], sort_keys=True) == json.dumps(fresh["1 B (computed)"]["info"], sort_keys=True)
        print("result.json reproduced" if same else "result.json differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
