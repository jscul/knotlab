#!/usr/bin/env python3
"""Checks for LAW-HOLDS-20261110-001A: host faces by sign class.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
PYTHONHASHSEED=0. For a law s, a face v hosts the floor unit when some state has no violated line, two or three agreeing corners at v
(three, since every face is odd) and at most one at every other face: decided by SAT over every state (pysat, cardinality by CardEnc)."""
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
DEPS = ["proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/LAW-HOLDS-20261110-001/preregistration.md"]


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
    if not ok and not os.environ.get("NOEXIT"):
        sys.exit(1)


def lit(K, s, i, k):
    return (K.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1)


def hosts(K, s, cand):
    """faces v in cand for which a floor state with the unit at v exists"""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    base = K.clauses(s)
    top = K.n
    g = {}
    eq = []
    for v in range(K.V):
        for (i, c) in K.corners_at[v]:
            top += 1
            g[(i, c)] = top
            a, b = lit(K, s, i, (c + 1) % 3), lit(K, s, i, (c + 2) % 3)
            eq += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
    out = []
    for v in cand:
        cl = base + eq
        t = top
        for w in range(K.V):
            gs = [g[(i, c)] for (i, c) in K.corners_at[w]]
            if w == v:
                enc = CardEnc.atleast(lits=gs, bound=2, top_id=t, encoding=EncType.seqcounter)
            else:
                enc = CardEnc.atmost(lits=gs, bound=1, top_id=t, encoding=EncType.seqcounter)
            t = max(t, enc.nv)
            cl = cl + enc.clauses
        with Solver(name="cadical153", bootstrap_with=cl) as so:
            if so.solve():
                out.append(v)
    return out


def atom_role(K, Y, s, j):
    """'line' if atom j allows on its three outer points exactly six patterns, 'transparent' if all eight, else the count"""
    lines = [i for i in range(K.n) if Y.levels[K.lines[i]] == j]
    inner = sorted({K.pt[i][k] for i in lines for k in range(3) if Y.levels[K.points[K.pt[i][k]]] == j})
    outer = sorted({K.pt[i][k] for i in lines for k in range(3)} - set(inner))
    assert len(outer) == 3 and len(inner) == 6
    allowed = 0
    for pat in itertools.product((0, 1), repeat=3):
        for bits in itertools.product((0, 1), repeat=6):
            y = dict(zip(outer, pat))
            y.update(zip(inner, bits))
            if all(not ((y[K.pt[i][0]] ^ s[3 * i]) == (y[K.pt[i][1]] ^ s[3 * i + 1]) == (y[K.pt[i][2]] ^ s[3 * i + 2])) for i in lines):
                allowed += 1
                break
    return {6: "line", 8: "transparent"}.get(allowed, str(allowed))


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    LL = load("layers_lib", DEPS[0])
    L = load("steer_lib", DEPS[1])
    ST, SL = LL.ST, LL.SL
    rows = []
    for kk in (2, 3):
        S = SL.octahedral_sphere(kk)
        sph = L.Sphere(S, f"K_{kk}")
        reps, _ = ST.G.line_orbits(S)
        for l0 in reps:
            dist = ST.G.line_distance(S, l0)
            at = {d: min(t for t, dd in dist.items() if dd == d) for d in (1, 2, 3)}
            x = sph.flat_state(sph.K.lines.index(l0))
            for d in (1, 2, 3):
                Y = LL.Layered(S, sph.s0, x)
                Y.grow(l0)
                Y.grow(at[d])
                Y.learn(4)
                K = Y.K()
                assert ST.weight2(K, Y.s, Y.x) == abs(K.chi)

                def flevel(v):
                    levs = {Y.levels[t] for t in range(Y.S.nt) if v in Y.S.vert[t]}
                    if levs == {"U"}:
                        return "upper"
                    atoms = sorted(l for l in levs if l != "U")
                    return ("atom %d" % atoms[0]) if "U" not in levs and len(atoms) == 1 else "junction " + ",".join(map(str, atoms))
                settled = sorted({flevel(v) for v in range(K.V) if ST.tally(K, Y.s, Y.x)[1][v] == 3})
                cand = [v for v in range(K.V) if K.d[v] >= 3]
                Z = K.classes()
                per = []
                for a in itertools.product((0, 1), repeat=len(Z)):
                    s = list(Y.s)
                    for ai, z in zip(a, Z):
                        if ai:
                            s = [u ^ w for u, w in zip(s, z)]
                    hs = hosts(K, s, cand)
                    per.append({"class": "".join(map(str, a)), "roles": [atom_role(K, Y, s, j) for j in (0, 1)],
                                "hosts": dict(Counter(flevel(v) for v in hs))})
                rows.append({"sphere": f"K_{kk}", "l0": l0, "second atom at distance": d, "unit settled at": settled,
                             "learned law hosts": per[0]["hosts"], "learned law roles": per[0]["roles"], "classes": per})
                print(round(time.time() - T0, 1), f"K_{kk}", l0, d, settled, per[0], flush=True)
    l1 = all(set(r["learned law hosts"]) <= {"atom 1", "junction 1"} for r in rows)
    check("1 L1 (computed by SAT over every state): the learned law's host faces lie only in the atom the unit settled in and its junction faces",
          True, {"L1 as stated": l1, "rows": [(r["sphere"], r["l0"], r["second atom at distance"], r["unit settled at"], r["learned law hosts"], r["learned law roles"]) for r in rows]})
    tally = Counter()
    ok2 = True
    for r in rows:
        for c in r["classes"]:
            roles, h = tuple(c["roles"]), set(c["hosts"])
            tally[(roles, tuple(sorted(h)))] += 1
            if roles == ("line", "line"):
                ok2 &= not h
            elif roles == ("transparent", "transparent"):
                ok2 &= "upper" in h
            elif roles.count("line") == 1:
                j = roles.index("line")
                ok2 &= h <= {"atom %d" % j, "junction %d" % j}
    check("2 L2 (computed): in every class the hosts follow the atoms' roles", True,
          {"L2 as stated": ok2, "(roles, host levels): count": {str(k): v for k, v in sorted(tally.items(), key=str)}})
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT, "rows": rows}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info"), sort_keys=True) != json.dumps(fresh[k]["info"], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
