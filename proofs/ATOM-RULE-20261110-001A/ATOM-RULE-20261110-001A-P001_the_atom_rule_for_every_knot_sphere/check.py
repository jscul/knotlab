#!/usr/bin/env python3
"""Checks for ATOM-RULE-20261110-001A: the atom rule for every knot sphere.

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0.
O2: for every line orbit of K_2..K_4 and every line of K_5..K_7 (the automorphism search is slow there), every compatible splice (three bijections, two chiralities) of one Fano atom, and each of the atom's
four classes: the atom's allowed patterns on its outer points (and whether they equal the replaced line's), and the local SAT of its gadget
(every line with a corner at a region face satisfied, at most one agreeing corner at each region face).
O3: the sphere-side neighbourhoods of every line of K_2..K_8 (its three faces, every line with a corner at one of them, their points),
grouped up to isomorphism."""
import hashlib
import importlib.util
import itertools
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
DEPS = ["proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance/grow_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/ATOM-RULE-20261110-001/preregistration.md"]


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


def lit(K, s, i, k):
    return (K.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1)


def local_sat(K, s, region):
    """can every line with a corner at a region face be satisfied with at most one agreeing corner at each region face?"""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    lines = sorted({i for v in region for (i, c) in K.corners_at[v]})
    cl = []
    for i in lines:
        L = [lit(K, s, i, k) for k in range(3)]
        cl += [L, [-a for a in L]]
    top = K.n
    for v in region:
        gs = []
        for (i, c) in K.corners_at[v]:
            top += 1
            a, b = lit(K, s, i, (c + 1) % 3), lit(K, s, i, (c + 2) % 3)
            cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
            gs.append(top)
        enc = CardEnc.atmost(lits=gs, bound=1, top_id=top, encoding=EncType.seqcounter)
        top = max(top, enc.nv)
        cl += enc.clauses
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        return so.solve(), len(lines)


def classes_of(G, K, s_nat):
    """the four sign classes of a grown torus (GrownTorus without its SAT calls, which are exponential on the unsatisfiable class: the knot
    sphere's contradiction needs resolution size 2^Theta(sqrt n), SPHERE-SIZE-20261107-001)"""
    T = G.GrownTorus.__new__(G.GrownTorus)
    Z = [int("".join(str(b) for b in reversed(z)), 2) for z in K.classes()]
    gauge = K.gauge_vectors()
    m = 3 * K.n
    cs = []
    for j in range(2):
        sol = G.SL.solve_f2(gauge + Z, [0] * len(gauge) + [int(j == 0), int(j == 1)], m)
        cs.append([(sol >> e) & 1 for e in range(m)])
    T.n, T.contrib = K.n, [[cs[0][e], cs[1][e]] for e in range(m)]
    zs = [[(z >> e) & 1 for e in range(m)] for z in Z]
    out = {}
    for a in itertools.product((0, 1), repeat=2):
        s = list(s_nat)
        for ai, z in zip(a, zs):
            if ai:
                s = [u ^ w for u, w in zip(s, z)]
        out[T.label(s)] = s
    assert len(out) == 4
    return out


def neighbourhood_graph(S, l):
    """the sphere-side neighbourhood of line triangle l: its three faces, the line triangles with a corner at one of them, and their points"""
    faces = set(S.vert[l])
    lines = {t for t in range(S.nt) if S.colour[t] == 1 and set(S.vert[t]) & faces}
    G = nx.Graph()
    for t in lines:
        G.add_node(("t", t), kind="line", centre=(t == l))
        for k in range(3):
            p = S.side[t][k][0]
            G.add_node(("t", p), kind="point", centre=False)
            G.add_edge(("t", t), ("t", p))
        for c in range(3):
            v = S.vert[t][c]
            if v in faces:
                G.add_node(("f", v), kind="face", centre=False)
                G.add_edge(("t", t), ("f", v))
    return G


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    G, L = load("grow", DEPS[0]), load("steer", DEPS[1])
    SL = G.SL
    fano = SL.torus(7, 2, 1)
    P = next(t for t in range(fano.nt) if fano.colour[t] == 0)
    rows, bad = [], []
    for kk in range(2, 8):
        S = SL.octahedral_sphere(kk)
        sph = L.Sphere(S, f"K_{kk}")
        s0 = sph.s0
        reps = [t for t in range(S.nt) if S.colour[t] == 1] if kk >= 5 else G.line_orbits(S)[0]
        for l in reps:
            li = sph.K.lines.index(l)
            own = sorted(p for p in itertools.product((0, 1), repeat=3) if not (p[0] ^ s0[3 * li] == p[1] ^ s0[3 * li + 1] == p[2] ^ s0[3 * li + 2]))
            for chir in (0, 1):
                for sg in itertools.permutations(range(3)):
                    g = G.Growth(S, s0, l, fano, P, sg, chir)
                    if g.chi != 0:
                        continue
                    K = g.KG
                    assert K.even_faces(g.completions[0]) == []
                    classes = classes_of(G, K, g.completions[0])
                    atom_t = {i for i, name in enumerate(g.G.verts) if name[0] == "R"}
                    region = sorted({g.G.vert[t][c] for t in atom_t for c in range(3)})
                    res = []
                    for lab, s in sorted(classes.items()):
                        rel = sorted(map(tuple, g.atom_relation(s)))
                        role = "line" if len(rel) == 6 else "transparent" if len(rel) == 8 else str(len(rel))
                        sat, nlines = local_sat(K, s, region)
                        res.append((role, rel == own if role == "line" else None, sat))
                    acting = [r for r in res if r[0] == "line"]
                    ok = (len(acting) == 1 and acting[0][1] is True and acting[0][2] is False
                          and all(r[0] == "transparent" for r in res if r[0] != "line"))
                    if not ok:
                        bad.append((kk, l, chir, sg, res))
                    rows.append({"sphere": f"K_{kk}", "line": l, "chirality": chir, "sigma": sg, "region faces": len(region),
                                 "gadget lines": nlines, "classes": res, "ok": ok})
        print(round(time.time() - T0, 1), f"K_{kk}", len(reps), "lines" if kk >= 5 else "orbits", flush=True)
    tr = Counter((tuple(r[0] for r in row["classes"]).count("line"),
                  tuple(r[2] for r in row["classes"] if r[0] == "line"), tuple(r[2] for r in row["classes"] if r[0] != "line")) for row in rows)
    check("1 O2 (finite local check): on every line orbit of K_2-K_7 and every compatible splice, exactly one of the atom's four classes acts as the "
          "replaced line (its six patterns), and its gadget admits no state with at most one agreeing corner at every region face; the other three "
          "are transparent", not bad,
          {"splices": len(rows), "failures": bad[:5], "(acting classes, local SAT of acting, local SAT of transparent)": {str(k): v for k, v in tr.items()}})
    types, per_k = [], {}
    for kk in range(2, 9):
        S = SL.octahedral_sphere(kk)
        seen = []
        for l in (t for t in range(S.nt) if S.colour[t] == 1):
            H = neighbourhood_graph(S, l)
            idx = None
            for i, T_ in enumerate(types):
                if nx.is_isomorphic(H, T_, node_match=lambda a, b: a["kind"] == b["kind"] and a["centre"] == b["centre"]):
                    idx = i
                    break
            if idx is None:
                types.append(H)
                idx = len(types) - 1
            seen.append(idx)
        per_k[f"K_{kk}"] = dict(Counter(seen))
        print(round(time.time() - T0, 1), "O3", f"K_{kk}", per_k[f"K_{kk}"], flush=True)
    first = {}
    for kk in range(2, 9):
        for i in per_k[f"K_{kk}"]:
            first.setdefault(i, kk)
    check("2 O3 (classification): the sphere-side neighbourhoods of every line of K_2-K_8 up to isomorphism, and the first sphere each type appears in",
          True, {"types": len(types), "first appearance": first, "per sphere": per_k,
                 "types first seen beyond K_4": sorted(i for i, kk in first.items() if kk > 4)})
    OUT["rows"] = rows
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k not in ("seconds",) and json.dumps(old.get(k, {}).get("info") if isinstance(old.get(k), dict) and "info" in old.get(k, {}) else old.get(k), sort_keys=True)
                != json.dumps(fresh[k]["info"] if isinstance(fresh[k], dict) and "info" in fresh[k] else fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
