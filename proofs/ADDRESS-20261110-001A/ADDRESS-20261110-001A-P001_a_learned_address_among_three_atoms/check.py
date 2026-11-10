#!/usr/bin/env python3
"""Checks for ADDRESS-20261110-001A: a learned address among three atoms.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
PYTHONHASHSEED=0. The frozen targeted search of research/LEARN-RISE-20261110-001/posthoc_targeted.py (moves: state flips and learning steps at
A26 sites; W <= floor + 2; best first by Hamming distance to a SAT-chosen target; at most 300,000 configurations), run on fresh two-atom
starts (F1) and toward every pair of atoms on three-atom spaces (F2)."""
import hashlib
import heapq
import importlib.util
import itertools
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
DEPS = ["proofs/LEARN-RISE-20261110-001A/LEARN-RISE-20261110-001A-P001_swapping_the_atoms_roles/check.py",
        "proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/check.py",
        "proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/LEARN-RISE-20261110-001/posthoc_targeted.py",
        "research/ADDRESS-20261110-001/preregistration.md"]
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


def floor_model(LH, K, s, hosts):
    """a floor state of law s with agree >= 2 at each face in hosts and <= 1 elsewhere, or None"""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    cl, top, g = list(K.clauses(s)), K.n, {}
    for w in range(K.V):
        for (i, c) in K.corners_at[w]:
            top += 1
            g[(i, c)] = top
            a, b = LH.lit(K, s, i, (c + 1) % 3), LH.lit(K, s, i, (c + 2) % 3)
            cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
    for w in range(K.V):
        gs = [g[(i, c)] for (i, c) in K.corners_at[w]]
        enc = (CardEnc.atleast(lits=gs, bound=2, top_id=top, encoding=EncType.seqcounter) if w in hosts
               else CardEnc.atmost(lits=gs, bound=1, top_id=top, encoding=EncType.seqcounter))
        top = max(top, enc.nv)
        cl += enc.clauses
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        if not so.solve():
            return None
        m = so.get_model()
    return [int(m[p] > 0) for p in range(K.n)]


def run_target(C, LH, Y, K, named, n_atoms):
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
            xm = floor_model(LH, K, s, set(combo))
            if xm is not None:
                target = (sum(b << e for e, b in enumerate(s)), sum(b << p for p, b in enumerate(xm)))
                break
        if target:
            break
    if target is None:
        return {"target found": False}

    def h(s, x):
        return bin(s ^ target[0]).count("1") + bin(x ^ target[1]).count("1")

    def done(ag):
        return all(any(ag[v] >= 3 and levels[v] == "atom %d" % j for v in range(K.V)) for j in named)
    start = (sum(b << e for e, b in enumerate(Y.s)), sum(b << p for p, b in enumerate(Y.x)))
    prev, heap, found, tick = {start: None}, [(h(*start), 0, start)], None, 0
    while heap and len(prev) < CAP:
        _, _, (s, x) = heapq.heappop(heap)
        vi, ag, w = P.full(s, x)
        if w == floor2 and done(ag):
            found = (s, x)
            break
        for kind, t, y, w2 in P.neighbours(s, x, vi, ag, w):
            if w2 <= floor2 + 4 and (t, y) not in prev:
                prev[(t, y)] = ((s, x), kind)
                tick += 1
                heapq.heappush(heap, (h(t, y), tick, (t, y)))
    row = {"target found": True, "configurations": len(prev), "reached": found is not None}
    if found:
        kinds, node = [], found
        while prev[node] is not None:
            node, kind = prev[node]
            kinds.append(kind)
        s_end = [(found[0] >> e) & 1 for e in range(3 * K.n)]
        row.update({"moves": len(kinds), "learning steps": kinds.count("learn"), "flips": kinds.count("flip"),
                    "roles at the end": [LH.atom_role(K, Y, s_end, j) for j in range(n_atoms)]})
    return row


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    C, LH, LL, L = load("rise", DEPS[0]), load("holds", DEPS[1]), load("layers", DEPS[2]), load("steer", DEPS[3])
    ST, SL = LL.ST, LL.SL
    S = SL.octahedral_sphere(3)
    sph = L.Sphere(S, "K_3")
    reps, _ = ST.G.line_orbits(S)
    f1, f2 = [], []
    for oi, l0 in enumerate(reps):
        dist = ST.G.line_distance(S, l0)
        at = {d: min(t for t, dd in dist.items() if dd == d) for d in (1, 2, 3)}
        x0 = sph.flat_state(sph.K.lines.index(l0))
        if oi >= 1:
            for d in (1, 2, 3):
                Y = LL.Layered(S, sph.s0, x0)
                Y.grow(l0)
                Y.grow(at[d])
                Y.learn(4)
                K = Y.K()
                at_floor = ST.weight2(K, Y.s, Y.x) == abs(K.chi)
                row = {"l0": l0, "second atom at distance": d, "start at the floor": at_floor}
                if at_floor:
                    row.update(run_target(C, LH, Y, K, {0}, 2))
                f1.append(row)
                print(round(time.time() - T0, 1), "F1", row, flush=True)
        Y = LL.Layered(S, sph.s0, x0)
        for l in (l0, at[2], at[3]):
            Y.grow(l)
        Y.learn(4)
        K = Y.K()
        w = ST.weight2(K, Y.s, Y.x)
        units = sorted(Y.face_level(v) for v in range(K.V) if ST.tally(K, Y.s, Y.x)[1][v] >= 3)
        for pair in ((0, 1), (0, 2), (1, 2)):
            row = {"l0": l0, "pair": pair, "start W": w / 2, "floor": abs(K.chi) / 2, "units at the start": units}
            if w == abs(K.chi):
                row.update(run_target(C, LH, Y, K, set(pair), 3))
            f2.append(row)
            print(round(time.time() - T0, 1), "F2", row, flush=True)
    check("1 F1 (frozen confirmation of LEARN-RISE-20261110-001): fresh two-atom starts, target the unit inside atom 0", True,
          {"F1 as stated": all(r.get("reached") for r in f1), "reached": sum(1 for r in f1 if r.get("reached")), "of": len(f1), "rows": f1})
    check("2 F2: three atoms, every pair of atoms as the holders of the two units", True,
          {"F2 as stated": all(r.get("reached") for r in f2), "reached": sum(1 for r in f2 if r.get("reached")), "of": len(f2), "rows": f2})
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
