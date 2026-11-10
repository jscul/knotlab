#!/usr/bin/env python3
"""Checks for NAME-LAYERS-20261110-001A: cut and name, class by class (research/NAME-LAYERS-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. For each frozen lower-level space T and each of its classes: R_C, the relation T less a point offers K_2's line L0 when
spliced there (ports read by SAT), and R_N, the relation of the names q_k = a_k xor b_k of T's satisfying states, for the two frozen
namings (line pairs, far pairs). A naming the frozen rule cannot complete (fewer than three disjoint pairs) is recorded as undefined."""
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
        "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "research/NAME-LAYERS-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def namings(K):
    out = {}
    used, pairs = set(), []
    for i in range(K.n):
        if len(pairs) == 3:
            break
        if not set(K.pt[i]) & used:
            pairs.append((K.pt[i][0], K.pt[i][1]))
            used |= {K.pt[i][0], K.pt[i][1]}
    out["line pairs"] = pairs if len(pairs) == 3 else None
    share = {p: set() for p in range(K.n)}
    for i in range(K.n):
        for a in K.pt[i]:
            share[a] |= set(K.pt[i])
    used, pairs = set(), []
    while len(pairs) < 3:
        free = [p for p in range(K.n) if p not in used]
        if not free:
            break
        p = free[0]
        q = next((u for u in free if u != p and u not in share[p]), None)
        if q is None:
            break
        pairs.append((p, q))
        used |= {p, q}
    out["far pairs"] = pairs if len(pairs) == 3 else None
    return out


def name_relation(N, K, s, pairs):
    from pysat.solvers import Solver
    cl = list(K.clauses(s))
    ys = []
    for k, (a, b) in enumerate(pairs):
        y = K.n + 1 + k
        A, B = a + 1, b + 1
        cl += [[-y, A, B], [-y, -A, -B], [y, -A, B], [y, A, -B]]
        ys.append(y)
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return [pat for pat in itertools.product((0, 1), repeat=3) if so.solve(assumptions=[y if b else -y for y, b in zip(ys, pat)])]


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import spaces_lib as SP
    N, SL, A = SP.N, SP.SL, SP.A
    H = A.H
    S2, s2 = SP.SPH[2].S, SP.SPH[2].s0
    L0 = SP.lines_of(2)[0]
    spaces = []
    for t in ((7, 2, 1), (2, 1, 2), (3, 2, 2), (4, 3, 2), (2, 0, 2)):
        T = H.Torus(*t)
        spaces.append(("torus(%d,%d,%d)" % t, T.S, [T.classes[lab] for lab in H.LABELS], T.K.points[0]))
    for leaf in ("Fano", "thin"):
        C = SP.C2(leaf)
        spaces.append((f"C(2, {leaf})", C.S, C.classes(C.K()), SP.standard_point(C)))
    spaces.insert(5, ("K_2", S2, [s2], SP.SPH[2].K.points[0]))
    rows = []
    for name, S, signings, P in spaces:
        K = SL.KnotSpace(S)
        nm = namings(K)
        for ci, s in enumerate(signings):
            sat = K.sat(s)[0]
            GS, sg, _ = N.splice_closed(S2, s2, L0, S, s, P)
            KG = SL.KnotSpace(GS)
            pid = {t: i for i, t in enumerate(KG.points)}
            gv = {v: i for i, v in enumerate(GS.verts)}
            ports = [pid[gv[("A", S2.side[L0][k][0])]] for k in range(3)]
            lines = [i for i, gt in enumerate(KG.lines) if GS.verts[gt][0] == "R"]
            rc = N.relation(KG, sg, lines, ports)
            row = {"space": name, "class": ci, "satisfiable": sat, "R_C size": len(rc)}
            for nmname, pairs in nm.items():
                row["R_N size, " + nmname] = None if pairs is None else len(name_relation(N, K, s, pairs))
            rows.append(row)
        print(round(time.time() - T0, 1), name, {k: v for k, v in nm.items()}, [(r["satisfiable"], r["R_C size"], r["R_N size, line pairs"], r["R_N size, far pairs"]) for r in rows if r["space"] == name], flush=True)
    def nsizes(r):
        return [r[k] for k in r if k.startswith("R_N size") and r[k] is not None]
    n1 = all((not r["satisfiable"]) == all(v == 0 for v in nsizes(r)) for r in rows if nsizes(r))
    n1_fail = [r for r in rows if not r["satisfiable"] and any(v != 0 for v in nsizes(r))]
    d = all(r["R_C size"] == 6 for r in rows if not r["satisfiable"])
    n2 = all(v == 8 for r in rows if r["satisfiable"] for v in nsizes(r))
    check("1 the census: R_C and R_N in every class of every frozen space", True, {"rows": rows,
          "undefined namings": sorted({(r["space"], k) for r in rows for k in r if k.startswith("R_N size") and r[k] is None})})
    OUT["predictions"] = {"D: in every unsatisfiable class R_C is a line": d, "N1: R_N empty exactly in the unsatisfiable classes": n1,
                          "N2: R_N all eight in every satisfiable class": n2, "failure: nonempty R_N in an unsatisfiable class": bool(n1_fail),
                          "satisfiable classes where names carry a correlation": [(r["space"], r["class"], {k: r[k] for k in r if k.startswith("R_N")}) for r in rows if r["satisfiable"] and any(v != 8 for v in nsizes(r))]}
    print(json.dumps(OUT["predictions"], default=str)[:1500], flush=True)
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
