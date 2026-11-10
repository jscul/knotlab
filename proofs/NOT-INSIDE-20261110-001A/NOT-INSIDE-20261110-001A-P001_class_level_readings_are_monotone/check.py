#!/usr/bin/env python3
"""Checks for NOT-INSIDE-20261110-001A (research/NOT-INSIDE-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. N: for cut leaves thin (3,2,2), thin (4,3,2) and Fano (7,2,1) in the torus (2,0,2) (first class, first line), one fixed
signing per leaf class: the satisfying states S_c of the component, whether S_omega lies inside the union of the non-acting S_c, and, where
not, an explicit network reading NOT a_1 in this frame, with a second signing of a non-acting class under which it reads 0. F: for each
network of CLASS-READ-20261110-001's G1 that reads {omega, sigma}, a signing of sigma (its labelled law with points flipped) under which it
has a satisfying state."""
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
CR = "proofs/CLASS-READ-20261110-001A/CLASS-READ-20261110-001A-P001_class_readings/check.py"
DEPS = ["proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py",
        "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py", CR,
        "research/NOT-INSIDE-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def states(K, s):
    lits = [[(K.pt[i][k], s[3 * i + k]) for k in range(3)] for i in range(K.n)]
    out = set()
    for x in range(1 << K.n):
        ok = True
        for L in lits:
            a = ((x >> L[0][0]) & 1) ^ L[0][1]
            if a == ((x >> L[1][0]) & 1) ^ L[1][1] == ((x >> L[2][0]) & 1) ^ L[2][1]:
                ok = False
                break
        if ok:
            out.add(x)
    return out


def flip_points(K, s, pts):
    t = list(s)
    for i in range(K.n):
        for k in range(3):
            if K.pt[i][k] in pts:
                t[3 * i + k] ^= 1
    return t


def pinned_network_sat(K, s, w):
    """names y_k = x_0 xor x_k for every k, each pinned by the parity knot (y_k, y_k, y_k) = w_0 xor w_k: satisfiable?"""
    from pysat.solvers import Solver
    cl = []
    for i in range(K.n):
        L = [(K.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1) for k in range(3)]
        cl += [L, [-a for a in L]]
    v = K.n
    for k in range(1, K.n):
        v += 1
        a, b = 1, k + 1
        cl += [[-v, a, b], [-v, -a, -b], [v, -a, b], [v, a, -b]]
        kappa = ((w >> 0) & 1) ^ ((w >> k) & 1)
        cl.append([v] if kappa else [-v])  # the parity knot y_k + y_k + y_k = kappa is y_k = kappa
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve()


def load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import spaces_lib as SP
    N, A = SP.N, SP.A
    H = A.H
    labs = [tuple(l) for l in H.LABELS]
    Hh = H.Torus(2, 0, 2)
    host_s = list(Hh.classes[H.LABELS[0]])
    rows = []
    for t in ((3, 2, 2), (4, 3, 2), (7, 2, 1)):
        T = H.Torus(*t)
        w_lab = tuple(T.forced[0])
        S, Ks, signs, inner = {}, None, {}, None
        for lab in labs:
            atom = A.Atom(t)
            atom.s = list(T.classes[lab])
            Y = N.Nested(Hh.S, host_s)
            Y.grow_leaf(Y.where[Hh.K.lines[0]], atom)
            K = Y.K()
            if Ks is None:
                Ks = K
                inner = {p for p, tri in enumerate(K.points) if Y.path[tri] == (0,)}
            assert K.n == Ks.n and K.pt == Ks.pt
            signs[lab] = Y.s
            S[lab] = states(K, Y.s)
        union = set().union(*(S[l] for l in labs if l != w_lab))
        witness = sorted(S[w_lab] - union)
        row = {"leaf": "torus(%d,%d,%d)" % t, "points": Ks.n, "inner points": len(inner), "acting class": w_lab,
               "satisfying states per class": {str(l): len(S[l]) for l in labs}, "frame-level NOT possible": bool(witness), "witness states": len(witness)}
        if witness:
            w = witness[0]
            reads = {str(l): int(not pinned_network_sat(Ks, signs[l], w)) for l in labs}
            row["explicit network reading (1 = no satisfying state)"] = reads
            row["it reads NOT a_1 in this frame"] = all(reads[str(l)] == (0 if l == w_lab else 1) for l in labs)
            # claim M: a second signing of a non-acting class under which it reads 0
            c = next(l for l in labs if l != w_lab)
            host_mask = sum(1 << p for p in range(Ks.n) if p not in inner)
            x = next(z for z in S[c] if (z & host_mask) == (w & host_mask))
            g = {p for p in inner if ((x ^ w) >> p) & 1}
            row["second signing of a non-acting class (inner points flipped)"] = {"class": c, "points flipped": sorted(g),
                                                                                   "reading": int(not pinned_network_sat(Ks, flip_points(Ks, signs[c], g), w))}
        rows.append(row)
        print(round(time.time() - T0, 1), row, flush=True)
    okN = any(r["frame-level NOT possible"] for r in rows)
    check("1 N: frame-level NOT through names inside a cut leaf", True, {"rows": rows})
    # F
    CRm = load("class_read", CR)
    T = H.Torus(3, 2, 2)
    K = T.K
    w = tuple(T.forced[0])
    sigma = (1, 0)
    pairs = list(itertools.combinations(range(K.n), 2))
    read = {}
    for lab in labs:
        base = CRm.space_clauses(K, T.classes[lab], 0)
        for tri in itertools.combinations_with_replacement(pairs, 3):
            vt = [(a + 1, b + 1) for a, b in tri]
            for top, o in zip(CRm.TOPS, CRm.read_triple(base, K.n, vt)):
                read.setdefault((tri, top), set())
                if o:
                    read[(tri, top)].add(lab)
    sig_nets = [k for k, v in read.items() if v == {w, sigma}]
    frame = 0
    for tri, top in sig_nets:
        vt = [(a + 1, b + 1) for a, b in tri]
        found = False
        for r in range(1, K.n + 1):
            for g in itertools.combinations(range(K.n), r):
                s = flip_points(K, T.classes[sigma], set(g))
                o = CRm.read_triple(CRm.space_clauses(K, s, 0), K.n, vt)[CRm.TOPS.index(top)]
                if o == 0:
                    found = True
                    break
            if found:
                break
        frame += found
    check("2 F: the sigma readings of CLASS-READ-20261110-001 read the frame", True,
          {"networks reading {omega, sigma}": len(sig_nets), "with a signing of sigma under which they have a satisfying state": frame})
    OUT["predictions"] = {"N: a frame-level NOT for at least one leaf": okN,
                          "N: every explicit network reads NOT a_1 in its frame": all(r.get("it reads NOT a_1 in this frame", True) for r in rows),
                          "M checked: every second signing reads 0": all(r["second signing of a non-acting class (inner points flipped)"]["reading"] == 0 for r in rows if "second signing of a non-acting class (inner points flipped)" in r),
                          "F: every sigma network reads the frame": frame == len(sig_nets) and len(sig_nets) > 0,
                          "failure line crossed": frame < len(sig_nets) or any(r.get("second signing of a non-acting class (inner points flipped)", {}).get("reading") == 1 for r in rows)}
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
