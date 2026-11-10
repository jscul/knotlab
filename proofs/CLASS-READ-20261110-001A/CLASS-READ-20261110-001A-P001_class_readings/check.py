#!/usr/bin/env python3
"""Checks for CLASS-READ-20261110-001A: class readings (research/CLASS-READ-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. G1: one closed thin torus (3,2,2) in each of its four classes, three names (a multiset of its point pairs), one of 10 tops:
the set of classes where the network has no satisfying state. G2: two such tori, y_0 a pair of the first, y_1 of the second, y_2 of either:
the set of class pairs where it has none. Then R0, R1 and R2."""
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
T0 = time.time()
OUT = {}
A_DIR = "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom"
DEPS = [A_DIR + "/atoms_lib.py", "research/CLASS-READ-20261110-001/preregistration.md"]
TOPS = [("nae", sg) for sg in itertools.product((0, 1), repeat=3)] + [("xor", 0), ("xor", 1)]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def space_clauses(K, s, off):
    cl = []
    for i in range(K.n):
        L = [(K.pt[i][k] + 1 + off) * (1 if s[3 * i + k] == 0 else -1) for k in range(3)]
        cl += [L, [-a for a in L]]
    return cl


def read_triple(base, top_var, tri):
    """O for each of the 10 tops, the names of tri (pairs of variables) defined afresh"""
    from pysat.solvers import Solver
    cl = list(base)
    ys = []
    v = top_var
    for a, b in tri:
        v += 1
        cl += [[-v, a, b], [-v, -a, -b], [v, -a, b], [v, a, -b]]
        ys.append(v)
    out = []
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        for t in TOPS:
            v += 1
            sel = v
            if t[0] == "nae":
                L = [y if b == 0 else -y for y, b in zip(ys, t[1])]
                so.add_clause([-sel] + L)
                so.add_clause([-sel] + [-a for a in L])
            else:
                for bits in itertools.product((0, 1), repeat=3):
                    if sum(bits) % 2 != t[1]:
                        so.add_clause([-sel] + [(-ys[k] if bits[k] else ys[k]) for k in range(3)])
            out.append(int(not so.solve(assumptions=[sel])))
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    sys.path.insert(0, str(ROOT / A_DIR))
    import atoms_lib as A
    H = A.H
    T = H.Torus(3, 2, 2)
    K = T.K
    labs = [tuple(l) for l in H.LABELS]
    w = tuple(T.forced[0])
    lines_through_w = [frozenset({w, tuple(a ^ b for a, b in zip(w, v))}) for v in ((0, 1), (1, 0), (1, 1))]
    n = K.n
    pairs = list(itertools.combinations(range(n), 2))
    # G1
    reads1 = {}
    for lab in labs:
        base = space_clauses(K, T.classes[lab], 0)
        for tri in itertools.combinations_with_replacement(pairs, 3):
            vt = [(a + 1, b + 1) for a, b in tri]
            for t, o in zip(TOPS, read_triple(base, n, vt)):
                reads1.setdefault((tri, t), set())
                if o:
                    reads1[(tri, t)].add(lab)
    sets1 = Counter(frozenset(s) for s in reads1.values())
    r0_1 = all(w in s for s in reads1.values())
    r1 = [sorted(L) for L in lines_through_w if sets1.get(L, 0)]
    check("1 G1: the sets of classes read by one-leaf networks", r0_1,
          {"networks": len(reads1), "acting class": w, "sets read (networks)": {str(sorted(k)): v for k, v in sets1.items()},
           "lines through the acting class read": r1})
    print(round(time.time() - T0, 1), "G1 done", flush=True)
    # G2
    reads2 = {}
    tri2 = [(x, y, z) for x in pairs for y in pairs for z in [("A",) + p for p in pairs] + [("B",) + p for p in pairs]]
    for la, lb in itertools.product(labs, labs):
        base = space_clauses(K, T.classes[la], 0) + space_clauses(K, T.classes[lb], n)
        for x, y, z in tri2:
            zz = (z[1] + 1, z[2] + 1) if z[0] == "A" else (z[1] + 1 + n, z[2] + 1 + n)
            vt = [(x[0] + 1, x[1] + 1), (y[0] + 1 + n, y[1] + 1 + n), zz]
            for t, o in zip(TOPS, read_triple(base, 2 * n, vt)):
                key = (x, y, z, t)
                reads2.setdefault(key, set())
                if o:
                    reads2[key].add((la, lb))
        print(round(time.time() - T0, 1), "G2 class pair", la, lb, flush=True)
    nonact = [(a, b) for a in labs for b in labs if a != w and b != w]
    acting_pairs = {(a, b) for a in labs for b in labs if a == w or b == w}
    r0_2 = all(acting_pairs <= s for s in reads2.values())
    patterns = Counter(frozenset(p for p in s if p in nonact) for s in reads2.values())
    minterms = {str(p): patterns.get(frozenset({p}), 0) for p in nonact}
    r2 = all(v > 0 for v in minterms.values())
    check("2 G2: readings of two-leaf networks on the nine non-acting class pairs", r0_2,
          {"networks": len(reads2), "distinct readings on the non-acting pairs (of 512)": len(patterns),
           "networks reading each joint minterm": minterms, "most common readings": {str(sorted(k)): v for k, v in patterns.most_common(8)}})
    OUT["predictions"] = {"R0: every reading 1 where a leaf acts": r0_1 and r0_2, "R1: some G1 network reads a line through the acting class": bool(r1),
                          "R2: every joint minterm of the non-acting pairs read in G2": r2, "failure line crossed": not (r0_1 and r0_2)}
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
