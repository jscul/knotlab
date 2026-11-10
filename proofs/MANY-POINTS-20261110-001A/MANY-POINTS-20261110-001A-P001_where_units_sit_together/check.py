#!/usr/bin/env python3
"""Checks for MANY-POINTS-20261110-001A: where units sit together (research/MANY-POINTS-20261110-001/preregistration.md, ticket A).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Space (b) of NEST-ATOMS-20261110-001 for the Fano and thin (2,1,2) leaves. In every class, by SAT over every state:
which distributions (u_0, u_1, u_2) of the floor's three units over the regions R0, R1, R2 are realized (A1, A2); where a composite acts,
whether a leaf region can hold other than one unit or the composite's sphere part any (A3); where a composite holds two units without
acting, which of its parts can hold them (A4)."""
import hashlib
import itertools
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NA = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(NA))
T0 = time.time()
OUT = {}
DEPS = ["proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py",
        "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "research/MANY-POINTS-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def floor_with(N, K, s, fixed):
    """a state satisfying every line with exactly k units in each region of fixed = [(region faces, k)], or None"""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    cl, top = list(K.clauses(s)), K.n
    for faces, k in fixed:
        gs = []
        for v in faces:
            for (i, c) in K.corners_at[v]:
                top += 1
                a, b = N.lit(K, s, i, (c + 1) % 3), N.lit(K, s, i, (c + 2) % 3)
                cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
                gs.append(top)
        enc = CardEnc.equals(lits=gs, bound=len(faces) + 2 * k, top_id=top, encoding=EncType.seqcounter)
        top = max(top, enc.nv)
        cl += enc.clauses
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import spaces_lib as SP
    N = SP.N
    dists = [d for d in itertools.product(range(4), repeat=3) if sum(d) == 3]
    rows = []
    for leaf in ("Fano", "thin"):
        O = SP.outer_with([SP.C2(leaf), SP.C2(leaf)])
        K = O.K()
        P1, P2 = O.group_parts(K, (0,)), O.group_parts(K, (1,))
        R1, R2 = P1[2], P2[2]
        assert not set(R1) & set(R2)
        R0 = sorted(set(range(K.V)) - set(R1) - set(R2))
        leafreg = {q: O.group_parts(K, q)[2] for q in O.leaves()}
        host = {t: sorted(set(O.group_parts(K, t)[2]) - {v for q in O.leaves() if q[:1] == t for v in leafreg[q]}) for t in ((0,), (1,))}
        tally, a1bad, a2bad, a3bad, a4 = Counter(), [], [], [], Counter()
        for s in O.classes(K):
            acts = tuple(N.group_role(K, s, *O.group_parts(K, t)[:2]) == "line" for t in ((0,), (1,)))
            real = tuple(d for d in dists if floor_with(N, K, s, [(R0, d[0]), (R1, d[1]), (R2, d[2])]))
            if acts == (True, False):
                allowed = {(0, 2, 1)}
            elif acts == (False, True):
                allowed = {(0, 1, 2)}
            elif acts == (False, False):
                allowed = {(1, 1, 1), (0, 2, 1), (0, 1, 2)}
            else:
                allowed = set()
            tally[(acts, real)] += 1
            if set(real) - allowed:
                a1bad.append((acts, real))
            if allowed - set(real):
                a2bad.append((acts, real))
            for ti, t in enumerate(((0,), (1,))):
                Rt = R1 if ti == 0 else R2
                if acts[ti]:
                    for q in O.leaves():
                        if q[:1] == t:
                            for k in (0, 2):
                                if floor_with(N, K, s, [(leafreg[q], k)]):
                                    a3bad.append((acts, str(q), k))
                    if floor_with(N, K, s, [(host[t], 1)]) or floor_with(N, K, s, [(host[t], 2)]):
                        a3bad.append((acts, str(t), "sphere part"))
                elif floor_with(N, K, s, [(Rt, 2)]):
                    where = []
                    for q in O.leaves():
                        if q[:1] == t:
                            for k in (1, 2):
                                if floor_with(N, K, s, [(Rt, 2), (leafreg[q], k)]):
                                    where.append("leaf %s: %d" % (str(q), k))
                    for k in (1, 2):
                        if floor_with(N, K, s, [(Rt, 2), (host[t], k)]):
                            where.append("sphere part: %d" % k)
                    a4[tuple(where)] += 1
        row = {"leaf": leaf, "classes": sum(tally.values()), "(composites acting, distributions realized)": {str(k): v for k, v in sorted(tally.items(), key=str)},
               "A1 violations": a1bad[:5], "A2 misses": len(a2bad), "A2 miss examples": a2bad[:5], "A3 violations": a3bad[:5],
               "A4: where two units of a non-acting composite can sit (part: units), with how many class-composite cases": {str(k): v for k, v in a4.items()}}
        rows.append(row)
        print(round(time.time() - T0, 1), leaf, row["classes"], "A1", len(a1bad), "A2 misses", len(a2bad), "A3", len(a3bad), flush=True)
    check("1 A1 (proved; exact check): no distribution the theorem excludes is realized", all(not r["A1 violations"] for r in rows), {"rows": rows})
    OUT["predictions"] = {"A1 held": all(not r["A1 violations"] for r in rows), "A2 held": all(r["A2 misses"] == 0 for r in rows),
                          "A3 held": all(not r["A3 violations"] for r in rows)}
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
