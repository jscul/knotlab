#!/usr/bin/env python3
"""Checks for COMPOSITE-FN-20261110-001B: a search outside the proved class (research/COMPOSITE-FN-20261110-001/preregistration.md, B).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. The frozen family: double covers of K_2 and K_3 branched at four vertices (three branch sets each: the first four
corners; the first two corners and the first two regular vertices; the first four regular vertices), and double covers of the Fano torus
(7,2,1) and the thin torus (4,3,2) branched at vertex 0 and the lowest-index vertex not adjacent to it. For each: a Kasteleyn law, every
class, its satisfiability, and in each unsatisfiable class whether every line is critical; for a non-critical line, the functions of
two-line placements by lemma M."""
import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NA = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(NA))
T0 = time.time()
OUT = {}
DEPS = ["proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py",
        "proofs/COUNT-SURFACES-20261107-001A/COUNT-SURFACES-20261107-001A-P001_the_count_reads_the_euler_characteristic/surface_lib.py",
        "research/COMPOSITE-FN-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def sat_without(N, K, s, deleted):
    from pysat.solvers import Solver
    cl = [c for i in range(K.n) if i not in deleted for c in ([N.lit(K, s, i, k) for k in range(3)], [-N.lit(K, s, i, k) for k in range(3)])]
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import spaces_lib as SP
    N, SL, L = SP.N, SP.SL, SP.L
    hosts = []
    for k in (2, 3):
        sp = L.octahedral(k)
        cor = sp.corners()
        reg = [v for v in range(sp.V) if len(sp.lines_at[v]) == 3]
        for name, br in (("four corners", cor[:4]), ("two corners, two regular", cor[:2] + reg[:2]), ("four regular", reg[:4])):
            hosts.append((f"cover(K_{k}; {name})", SL.double_cover(sp.S, br)))
    undefined = []
    for t in ((7, 2, 1), (4, 3, 2)):
        S = SL.torus(*t)
        adj = {u for tri in range(S.nt) if 0 in S.vert[tri] for u in S.vert[tri]}
        far = [u for u in range(S.nv) if u not in adj]
        if not far:
            # the frozen rule names no vertex: on the 7-vertex torus (the K_7 triangulation) every vertex is adjacent to vertex 0
            undefined.append({"torus": t, "vertices": S.nv, "reason": "every vertex is adjacent to vertex 0"})
            continue
        hosts.append((f"cover(torus{t}; 0 and {far[0]})", SL.double_cover(S, [0, far[0]])))
    rows, found = [], []
    for name, S in hosts:
        K = SL.KnotSpace(S)
        distinct = all(len({S.vert[t][c] for c in range(3)}) == 3 for t in K.lines)
        rows_f = K._face_rows()
        target = [(K.d[v] + 1) % 2 for v in range(K.V)]
        sol = SL.solve_f2(rows_f, target, 3 * K.n)
        assert sol is not None
        s0 = [(sol >> e) & 1 for e in range(3 * K.n)]
        assert K.even_faces(s0) == []
        Z = K.classes()
        g = len(Z) // 2
        row = {"host": name, "genus": g, "chi": K.chi, "points": K.n, "simple": K.simple(), "three distinct faces per line": distinct,
               "classes": 4 ** g, "unsatisfiable classes": 0, "non-critical lines": 0}
        for a in itertools.product((0, 1), repeat=len(Z)):
            s = list(s0)
            for ai, z in zip(a, Z):
                if ai:
                    s = [u ^ w for u, w in zip(s, z)]
            if K.sat(s)[0]:
                continue
            row["unsatisfiable classes"] += 1
            nc = [i for i in range(K.n) if not N.one_violated(K, s, i)]
            row["non-critical lines"] += len(nc)
            for l1 in nc[:3]:
                fns = {}
                for l2 in range(K.n):
                    if l2 == l1:
                        continue
                    f = (1, int(not sat_without(N, K, s, {l1})), int(not sat_without(N, K, s, {l2})), int(not sat_without(N, K, s, {l1, l2})))
                    kind = {(1, 0, 0, 0): "AND", (1, 1, 0, 0): "projection", (1, 0, 1, 0): "projection", (1, 1, 1, 0): "OR"}.get(f, "constant" if f[3] else str(f))
                    fns[kind] = fns.get(kind, 0) + 1
                found.append({"host": name, "class": a, "line": l1, "functions over the other lines": fns})
        rows.append(row)
        print(round(time.time() - T0, 1), row, flush=True)
    check("1 the frozen family: classes, satisfiability, and criticality in every unsatisfiable class (exhaustive per host)", True,
          {"hosts": rows, "non-critical lines found": found[:20], "hosts the frozen rule leaves undefined": undefined})
    OUT["predictions"] = {"S1: every line of every unsatisfiable class critical": all(r["non-critical lines"] == 0 for r in rows),
                          "hosts with an unsatisfiable class": sum(1 for r in rows if r["unsatisfiable classes"]),
                          "non-critical lines": sum(r["non-critical lines"] for r in rows)}
    print(json.dumps(OUT["predictions"]), flush=True)
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info") if isinstance(old.get(k), dict) and "info" in old.get(k, {}) else old.get(k), sort_keys=True)
                != json.dumps(fresh[k]["info"] if isinstance(fresh[k], dict) and "info" in fresh[k] else fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
