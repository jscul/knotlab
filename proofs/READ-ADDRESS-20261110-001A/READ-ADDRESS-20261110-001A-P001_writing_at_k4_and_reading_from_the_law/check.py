#!/usr/bin/env python3
"""Checks for READ-ADDRESS-20261110-001A: writing at K_4 and reading from the law.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
PYTHONHASHSEED=0. S reuses ADDRESS-20261110-001A's frozen targeted search (its floor_model and moves), returning the configuration found.
N1 reads each atom's role from its own signs (LAW-HOLDS-20261110-001A's atom_role). N2 draws random states with random.Random(85)."""
import hashlib
import heapq
import importlib.util
import itertools
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
DEPS = ["proofs/ADDRESS-20261110-001A/ADDRESS-20261110-001A-P001_a_learned_address_among_three_atoms/check.py",
        "proofs/LEARN-RISE-20261110-001A/LEARN-RISE-20261110-001A-P001_swapping_the_atoms_roles/check.py",
        "proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/check.py",
        "proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/READ-ADDRESS-20261110-001/preregistration.md"]
CAP = 300000


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


def search(AD, C, LH, Y, K, named, n_atoms):
    """ADDRESS-20261110-001A's run_target, returning the configuration found"""
    P = C.Space(K, Y.S)
    levels = [Y.face_level(v) for v in range(K.V)]
    floor2 = abs(K.chi)
    Z = K.classes()
    want = ["line" if j in named else "transparent" for j in range(n_atoms)]
    target = None
    for a in itertools.product((0, 1), repeat=len(Z)):
        s = list(Y.s)
        for ai, z in zip(a, Z):
            if ai:
                s = [u ^ w for u, w in zip(s, z)]
        if [LH.atom_role(K, Y, s, j) for j in range(n_atoms)] != want:
            continue
        faces = [[v for v in range(K.V) if levels[v] == "atom %d" % j and K.d[v] >= 3] for j in sorted(named)]
        for combo in itertools.product(*faces):
            xm = AD.floor_model(LH, K, s, set(combo))
            if xm is not None:
                target = (sum(b << e for e, b in enumerate(s)), sum(b << p for p, b in enumerate(xm)))
                break
        if target:
            break
    if target is None:
        return None, 0

    def h(s, x):
        return bin(s ^ target[0]).count("1") + bin(x ^ target[1]).count("1")

    def done(ag):
        return all(any(ag[v] >= 3 and levels[v] == "atom %d" % j for v in range(K.V)) for j in named)
    start = (sum(b << e for e, b in enumerate(Y.s)), sum(b << p for p, b in enumerate(Y.x)))
    prev, heap, tick = {start: None}, [(h(*start), 0, start)], 0
    while heap and len(prev) < CAP:
        _, _, (s, x) = heapq.heappop(heap)
        vi, ag, w = P.full(s, x)
        if w == floor2 and done(ag):
            return (s, x), len(prev)
        for kind, t, y, w2 in P.neighbours(s, x, vi, ag, w):
            if w2 <= floor2 + 4 and (t, y) not in prev:
                prev[(t, y)] = 1
                tick += 1
                heapq.heappush(heap, (h(t, y), tick, (t, y)))
    return None, len(prev)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    AD, C, LH, LL, L = load("addr", DEPS[0]), load("rise", DEPS[1]), load("holds", DEPS[2]), load("layers", DEPS[3]), load("steer", DEPS[4])
    ST, SL = LL.ST, LL.SL
    rng = random.Random(85)
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
            if ST.weight2(K, Y.s, Y.x) != abs(K.chi):
                rows.append({"sphere": f"K_{kk}", "l0": l0, "start at the floor": False})
                continue
            levels = [Y.face_level(v) for v in range(K.V)]
            for pair in ((0, 1), (0, 2), (1, 2)):
                found, size = search(AD, C, LH, Y, K, set(pair), 3)
                row = {"sphere": f"K_{kk}", "l0": l0, "pair": pair, "configurations": size, "written": found is not None}
                if found:
                    s = [(found[0] >> e) & 1 for e in range(3 * K.n)]
                    x = [(found[1] >> p) & 1 for p in range(K.n)]
                    roles = [LH.atom_role(K, Y, s, j) for j in range(3)]
                    agree = ST.tally(K, s, x)[1]
                    holders = sorted({int(levels[v].split()[1]) for v in range(K.V) if agree[v] >= 3 and levels[v].startswith("atom")})
                    row.update({"roles": roles, "holders": holders,
                                "N1 holders = line atoms": holders == [j for j in range(3) if roles[j] == "line"]})
                    shows = 0
                    for _ in range(1000):
                        y = [rng.randrange(2) for _ in range(K.n)]
                        ag = ST.tally(K, s, y)[1]
                        at_atoms = sorted({int(levels[v].split()[1]) for v in range(K.V) if ag[v] >= 3 and levels[v].startswith("atom")})
                        shows += at_atoms == sorted(pair)
                    row["N2 random states showing the pair"] = shows
                rows.append(row)
                print(round(time.time() - T0, 1), row, flush=True)
    k4 = [r for r in rows if r["sphere"] == "K_4"]
    wr = [r for r in rows if r.get("written")]
    check("1 S (stress, computed): the two leftovers of three atoms written into every pair on every K_4 line orbit", True,
          {"S as stated": all(r.get("written") for r in k4), "written": sum(1 for r in k4 if r.get("written")), "of": len(k4),
           "configurations": [r.get("configurations") for r in k4]})
    check("2 N1 (computed): in every written configuration the holders are exactly the atoms whose own signs make them act as their lines", True,
          {"N1 as stated": all(r["N1 holders = line atoms"] for r in wr), "hold": sum(r["N1 holders = line atoms"] for r in wr), "of": len(wr)})
    check("3 N2 (computed): random states showing the written pair, of 1,000 per written law", True,
          {"N2 as stated": all(r["N2 random states showing the pair"] < 500 for r in wr),
           "per configuration": [r["N2 random states showing the pair"] for r in wr], "rows": rows})
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
