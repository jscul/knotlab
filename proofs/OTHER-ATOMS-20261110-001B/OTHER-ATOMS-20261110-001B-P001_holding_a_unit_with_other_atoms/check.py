#!/usr/bin/env python3
"""Checks for OTHER-ATOMS-20261110-001B: holding a unit with other atoms (tier T2 of research/OTHER-ATOMS-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. For each atom passing T1 with at most 8 points (ticket A): on K_3, every line orbit l0, two atoms (at l0 and the first
line at distance 3) in all 16 classes and three atoms (at l0 and distances 2 and 3) in all 64, by SAT over every state:
R-a: if every atom acts as its line, no state satisfies every line;
R-b: in every state satisfying every line, each acting atom has a face with three agreeing corners in its region.
Also recorded: each atom's role read on its torus (line exactly in the torus's unsatisfiable class) against the role found."""
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
sys.path.insert(0, str(HERE))
T0 = time.time()
OUT = {}
A_DIR = "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom"
DEPS = [A_DIR + "/atoms_lib.py", A_DIR + "/result.json", "research/OTHER-ATOMS-20261110-001/preregistration.md",
        "proofs/OTHER-ATOMS-20261110-001B/OTHER-ATOMS-20261110-001B-P001_holding_a_unit_with_other_atoms/multi_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def relation(K, s, lines, ports, A):
    from pysat.solvers import Solver
    cl = []
    for i in lines:
        L = [A.lit(K, s, i, k) for k in range(3)]
        cl += [L, [-a for a in L]]
    out = []
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        for pat in itertools.product((0, 1), repeat=3):
            if so.solve(assumptions=[(p + 1) if b else -(p + 1) for p, b in zip(ports, pat)]):
                out.append(pat)
    return out


def sat_with_quiet_region(K, s, region, A):
    """a state satisfying every line with at most one agreeing corner at each face of region, or None"""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    cl, top = list(K.clauses(s)), K.n
    for v in region:
        gs = []
        for (i, c) in K.corners_at[v]:
            top += 1
            a, b = A.lit(K, s, i, (c + 1) % 3), A.lit(K, s, i, (c + 2) % 3)
            cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
            gs.append(top)
        enc = CardEnc.atmost(lits=gs, bound=1, top_id=top, encoding=EncType.seqcounter)
        top = max(top, enc.nv)
        cl += enc.clauses
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import multi_lib as M
    A, G, SL = M.A, M.G, M.SL
    L = A.load("steer", DEPS[4])
    passing = json.loads((ROOT / DEPS[1]).read_text())["checks"]["predictions"]["atoms passing T1 with at most 8 points (go to ticket B)"]
    params = [tuple(int(v) for v in name[6:-1].split(",")) for name in passing]
    S = SL.octahedral_sphere(3)
    sph = L.Sphere(S, "K_3")
    reps = G.line_orbits(S)[0]
    rows = []
    for t in params:
        atom = A.Atom(t)
        for l0 in reps:
            dist = G.line_distance(S, l0)
            at = {d: min(u for u, dd in dist.items() if dd == d) for d in (2, 3)}
            for lines in ([l0, at[3]], [l0, at[2], at[3]]):
                Y = M.Spaced(S, sph.s0)
                for l in lines:
                    Y.grow(l, atom)
                K = Y.K()
                parts = [Y.atom_parts(K, j) for j in range(len(lines))]
                tally = Counter()
                bad = []
                for s in Y.classes(K):
                    roles, predicted = [], []
                    for j, (al, inner, ports, own, region) in enumerate(parts):
                        rel = relation(K, s, al, ports, A)
                        roles.append(A.role(rel, own))
                        predicted.append("line" if list(Y.torus_label(K, j, s)) in [list(f) for f in atom.forced] else "transparent")
                    acting = [j for j, r in enumerate(roles) if r == "line"]
                    ra = rb = None
                    if len(acting) == len(lines):
                        ra = not K.sat(s)[0]
                    else:
                        rb = all(not sat_with_quiet_region(K, s, parts[j][4], A) for j in acting)
                    tally[(len(acting), ra, rb, roles == predicted)] += 1
                    if ra is False or rb is False or roles != predicted:
                        bad.append({"roles": roles, "predicted": predicted, "R-a": ra, "R-b": rb})
                row = {"atom": atom.name, "sphere": "K_3", "l0": l0, "atoms": len(lines), "lines": lines, "classes": sum(tally.values()),
                       "(acting atoms, R-a, R-b, role as read on the torus)": {str(k): v for k, v in sorted(tally.items(), key=str)}, "failures": bad[:3]}
                rows.append(row)
                print(round(time.time() - T0, 1), atom.name, l0, len(lines), row["(acting atoms, R-a, R-b, role as read on the torus)"], len(bad), flush=True)
    ok = all(not r["failures"] for r in rows)
    check("1 T2 (exact, SAT over every state): R-a and R-b in every class of every two- and three-atom space on K_3, for each atom passing T1 "
          "with at most 8 points", ok, {"spaces": len(rows), "classes": sum(r["classes"] for r in rows),
                                        "atoms": sorted({r["atom"] for r in rows}), "failing spaces": [(r["atom"], r["l0"], r["atoms"]) for r in rows if r["failures"]]})
    OUT["predictions"] = {"P3: every atom passing T1 passes T2": ok,
                          "atoms passing T2": sorted({r["atom"] for r in rows} - {r["atom"] for r in rows if r["failures"]})}
    OUT["rows"] = rows
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
