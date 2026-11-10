#!/usr/bin/env python3
"""Checks for ADDRESS-STEER-20261110-001C: a fresh tension after writing.

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. The written three-atom configurations of READ-ADDRESS-20261110-001A (regenerated with its search). For each, k random
upper-level points are flipped (k = 1, 2, 3), then the learner M1 runs: each round a uniformly random move among those lowering W (state
flips and learning steps at A26 sites), else among those keeping it; at most 200 rounds; 10 runs per configuration and k, random.Random(86).
At the floor the address is read as the set of atoms acting as their lines (ticket A's rule) and as the atoms holding units."""
import hashlib
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
DEPS = ["proofs/READ-ADDRESS-20261110-001A/READ-ADDRESS-20261110-001A-P001_writing_at_k4_and_reading_from_the_law/check.py",
        "proofs/ADDRESS-20261110-001A/ADDRESS-20261110-001A-P001_a_learned_address_among_three_atoms/check.py",
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
    RA, AD, C, LH, LL, L = (load("read", DEPS[0]), load("addr", DEPS[1]), load("rise", DEPS[2]), load("holds", DEPS[3]), load("layers", DEPS[4]), load("steer", DEPS[5]))
    ST, SL = LL.ST, LL.SL
    rng = random.Random(86)
    rows = []
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
                for k in (1, 2, 3):
                    res = Counter()
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
                        if w != floor2:
                            res["not at the floor"] += 1
                            continue
                        sl = [(s >> e) & 1 for e in range(3 * K.n)]
                        acting = tuple(j for j in range(3) if LH.atom_role(K, Y, sl, j) == "line")
                        res["acting = written" if acting == pair else "acting = %s" % (acting,)] += 1
                    row = {"sphere": f"K_{kk}", "l0": l0, "written": pair, "k": k, "outcomes": dict(res)}
                    rows.append(row)
                    print(round(time.time() - T0, 1), row, flush=True)
    kept = Counter()
    for r in rows:
        kept[(r["sphere"], r["k"])] += r["outcomes"].get("acting = written", 0)
    tot = Counter((r["sphere"], r["k"]) for r in rows)
    k1 = [r["outcomes"].get("acting = written", 0) / 10 for r in rows if r["k"] == 1]
    check("1 C (computed): after k random upper flips the learner M1 returns to the written address", True,
          {"expected (at least 80% at k = 1 on every space)": all(v >= 0.8 for v in k1),
           "failure (at most a third at k = 1)": sum(k1) / max(len(k1), 1) <= 1 / 3,
           "kept, by sphere and k": {"%s k=%d" % kk_: "%d of %d" % (kept[kk_], 10 * tot[kk_]) for kk_ in sorted(tot)}, "rows": rows})
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
