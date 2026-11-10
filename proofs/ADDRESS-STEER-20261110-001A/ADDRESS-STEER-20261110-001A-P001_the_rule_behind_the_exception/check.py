#!/usr/bin/env python3
"""Checks for ADDRESS-STEER-20261110-001A: the rule behind the exception (SAT over every state, every class).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. With no even face, a state with no violated line is at the floor (E = (n - V)/2 = g - 1), so floor states are exactly the
states satisfying every line. R-a: all atoms acting leaves none. R-b: each acting atom's region (its faces and junction faces) has a face
with three agreeing corners in every such state (UNSAT of 'every line satisfied and at most one agreeing corner at each face of the region').
R-c: when fewer atoms act than there are units, some such state has a unit at a face outside every acting region."""
import hashlib
import importlib.util
import itertools
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
DEPS = ["proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/check.py",
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


def face_atoms(Y, v):
    """the atoms whose region contains face v (its own atom, or every atom of a junction); empty for upper faces"""
    return {l for t in range(Y.S.nt) if v in Y.S.vert[t] for l in [Y.levels[t]] if l != "U"}


def solver_for(LH, K, s):
    from pysat.solvers import Solver
    cl, top, g = list(K.clauses(s)), K.n, {}
    for w in range(K.V):
        for (i, c) in K.corners_at[w]:
            top += 1
            g[(i, c)] = top
            a, b = LH.lit(K, s, i, (c + 1) % 3), LH.lit(K, s, i, (c + 2) % 3)
            cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
    return cl, top, g


def sat(cl):
    from pysat.solvers import Solver
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()


def card(gs, bound, top, atleast):
    from pysat.card import CardEnc, EncType
    enc = (CardEnc.atleast if atleast else CardEnc.atmost)(lits=gs, bound=bound, top_id=top, encoding=EncType.seqcounter)
    return enc.clauses, max(top, enc.nv)


def space(LL, L, kk, l0, dists):
    ST, SL = LL.ST, LL.SL
    S = SL.octahedral_sphere(kk)
    sph = L.Sphere(S, f"K_{kk}")
    dist = ST.G.line_distance(S, l0)
    lines = [l0] + [min(t for t, dd in dist.items() if dd == d) for d in dists]
    Y = LL.Layered(S, sph.s0, sph.flat_state(sph.K.lines.index(l0)))
    for l in lines:
        Y.grow(l)
    return Y, sph


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    LH, LL, L = load("holds", DEPS[0]), load("layers", DEPS[1]), load("steer", DEPS[2])
    rows = []
    cases = [(3, (2, 3)), (4, (2, 3)), (3, (2, 3, 4))]
    for kk, dists in cases:
        S = LL.SL.octahedral_sphere(kk)
        reps, _ = LL.ST.G.line_orbits(S)
        for l0 in reps:
            Y, sph = space(LL, L, kk, l0, dists)
            K = Y.K()
            g_ = len(dists) + 1
            region = {j: [v for v in range(K.V) if j in face_atoms(Y, v)] for j in range(g_)}
            Z = K.classes()
            tally = Counter()
            bad = []
            for a in itertools.product((0, 1), repeat=len(Z)):
                s = list(Y.s)
                for ai, z in zip(a, Z):
                    if ai:
                        s = [u ^ w for u, w in zip(s, z)]
                roles = [LH.atom_role(K, Y, s, j) for j in range(g_)]
                acting = [j for j in range(g_) if roles[j] == "line"]
                base, top, gv = solver_for(LH, K, s)
                any_floor = sat(base)
                if len(acting) == g_:
                    ok = not any_floor
                    tally[("all acting", "no floor state" if ok else "FLOOR EXISTS")] += 1
                    if not ok:
                        bad.append(("R-a", a))
                    continue
                if not any_floor:
                    tally[(len(acting), "no floor state")] += 1
                    continue
                okb = True
                for j in acting:
                    cl, t = list(base), top
                    for v in region[j]:
                        c2, t = card([gv[ic] for ic in K.corners_at[v]], 1, t, False)
                        cl += c2
                    if sat(cl):
                        okb = False
                        bad.append(("R-b", a, j))
                free = None
                if len(acting) < g_ - 1:
                    outside = [v for v in range(K.V) if not (face_atoms(Y, v) & set(acting)) and K.d[v] >= 3]
                    free = False
                    for v in outside:
                        c2, t = card([gv[ic] for ic in K.corners_at[v]], 2, top, True)
                        if sat(base + c2):
                            free = True
                            break
                tally[(len(acting), "R-b" if okb else "R-b FAILS", "free unit" if free else ("no free unit" if free is False else "no spare unit"))] += 1
            row = {"sphere": f"K_{kk}", "l0": l0, "atoms": g_, "classes": 2 ** len(Z), "tally": {str(k): v for k, v in sorted(tally.items(), key=str)}, "breaks": bad[:5], "n breaks": len(bad)}
            rows.append(row)
            print(round(time.time() - T0, 1), row["sphere"], l0, g_, row["tally"], len(bad), flush=True)
    ok = all(r["n breaks"] == 0 for r in rows)
    check("1 R-a and R-b (exact): every class of every space follows the rule (all acting: no floor state; otherwise each acting atom holds a unit)", ok,
          {"spaces": len(rows), "classes": sum(r["classes"] for r in rows), "breaks": sum(r["n breaks"] for r in rows)})
    check("2 R-c (exact): classes with fewer acting atoms than units, and whether a unit can sit outside every acting atom", True,
          {"rows": rows})
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
