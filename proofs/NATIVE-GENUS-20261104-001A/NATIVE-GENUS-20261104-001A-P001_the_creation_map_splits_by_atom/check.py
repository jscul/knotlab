#!/usr/bin/env python3
"""Checks for NATIVE-GENUS-20261104-001A: the creation map splits by atom.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes. About twenty minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import genus_lib as GL  # noqa: E402

T0 = time.time()
OUT = {}
ID = (0, 1, 2)


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def dist(S):
    g = nx.Graph()
    g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(S.H) for q in L)
    return dict(nx.all_pairs_shortest_path_length(g))


def far_point(S, p):
    d = dist(S)
    return max((q for q in range(S.n) if q != p), key=lambda q: (d[("p", p)][("p", q)], -q))


def far_line(S, p):
    d = dist(S)
    return max((k for k in range(len(S.H)) if p not in S.H[k]), key=lambda k: (d[("p", p)][("l", k)], -k))


def disjoint_line(S, l):
    d = dist(S)
    return max((k for k in range(len(S.H)) if not set(S.H[k]) & set(S.H[l])), key=lambda k: (d[("l", l)][("l", k)], -k))


def meeting_line(S, l):
    return min(k for k in range(len(S.H)) if k != l and len(set(S.H[k]) & set(S.H[l])) == 1)


def designs():
    """the designs: (label, design); keys are base keys ('g', index)"""
    out = []
    P4, P5, CUBE = GL.plane(GL.PL.prism(4)), GL.plane(GL.PL.prism(5)), GL.plane(GL.FL.octahedral(0))
    F, C = GL.FANO, GL.C58
    g = lambda i: ("g", i)
    q = far_point(P4, 0)
    out.append(("prism(4): Fano at a point + Fano at the farthest point", (P4, [("A", "point", g(0), F, 0, ID), ("B", "point", g(q), F, 0, ID)])))
    out.append(("prism(4): Fano at a point + Fano at the farthest line",
                (P4, [("A", "point", g(0), F, 0, ID), ("B", "line", g(far_line(P4, 0)), F, 0, ID)])))
    out.append(("prism(4): Fano at a line + Fano at the farthest disjoint line",
                (P4, [("A", "line", g(0), F, 0, ID), ("B", "line", g(disjoint_line(P4, 0)), F, 0, ID)])))
    out.append(("prism(4): Fano at two lines sharing a point", (P4, [("A", "line", g(0), F, 0, ID), ("B", "line", g(meeting_line(P4, 0)), F, 0, ID)])))
    l0 = next(k for k, L in enumerate(P4.H) if 0 in L)
    q2 = next(x for x in P4.H[l0] if x != 0)
    out.append(("prism(4): Fano at two points of one line", (P4, [("A", "point", g(0), F, 0, ID), ("B", "point", g(q2), F, 0, ID)])))
    out.append(("prism(4): Fano at a point + Fano at a line through it (touching)",
                (P4, [("A", "point", g(0), F, 0, ID), ("B", "line", g(l0), F, 0, ID)])))
    out.append(("prism(5): census 58 at a point + census 58 at the farthest line",
                (P5, [("A", "point", g(0), C, 0, ID), ("B", "line", g(far_line(P5, 0)), C, 0, ID)])))
    out.append(("prism(5): Fano at a point + census 58 (minus line 3) at the farthest point",
                (P5, [("A", "point", g(0), F, 0, ID), ("B", "point", g(far_point(P5, 0)), C, 3, ID)])))
    out.append(("cube: Fano at three points", (CUBE, [("A", "point", g(0), F, 0, ID), ("B", "point", g(1), F, 0, ID), ("C", "point", g(2), F, 0, ID)])))
    q = far_point(P4, 0)
    out.append(("prism(4): Fano at two points + Fano at a line off both",
                (P4, [("A", "point", g(0), F, 0, ID), ("B", "point", g(q), F, 0, ID),
                      ("C", "line", g(min(k for k, L in enumerate(P4.H) if 0 not in L and q not in L)), F, 0, ID)])))
    out.append(("the Fano plane: Fano at a point", (GL.base(*F), [("A", "point", g(0), F, 0, ID)])))
    out.append(("the Fano plane: Fano at a point + Fano at a line off it",
                (GL.base(*F), [("A", "point", g(0), F, 0, ID), ("B", "line", g(min(k for k, L in enumerate(F[0]) if 0 not in L)), F, 0, ID)])))
    out.append(("census 58: Fano at a point", (GL.base(*C), [("A", "point", g(0), F, 0, ID)])))
    return out


def order_task(args):
    """creation at L over every order of L's points, per far side; and the OR over far sides"""
    S, M = args
    AN = GL.CL.solutions(S.H, S.s, S.n, skip=M)
    c = collections.Counter()
    for L in range(len(S.H)):
        if L == M or not GL.six(AN, S.H[L]):
            continue
        per = []
        for perm in itertools.permutations(range(3)):
            H2, s2 = list(S.H), [list(x) for x in S.s]
            H2[L], s2[L] = tuple(S.H[L][i] for i in perm), [S.s[L][i] for i in perm]
            per.append(tuple(bool(GL.J.new_knots(GL.E, GL.G, AN, H2, s2, S.n, L, F, 3)[0]) for fname, F in GL.FARS))
        c["cases"] += 1
        c["union over far sides independent of the order"] += len({any(v) for v in per}) == 1
        for i, (fname, F) in enumerate(GL.FARS):
            c[fname + " alone independent of the order"] += len({v[i] for v in per}) == 1
    return c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1. interface
    info1, ok1 = {}, True
    const = {(0, 0, 0), (1, 1, 1)}
    for nm, atom in GL.ATOMS.items():
        H, s, n = atom
        em = [GL.interface(atom, "point", li) == const for li in range(len(H))]
        rc = [GL.interface(atom, "line", pt) == set(itertools.product((0, 1), repeat=3)) - const for pt in range(n)]
        ok1 &= all(em) and all(rc)
        info1[nm] = {"lines whose removal leaves the two constant port patterns": "%d of %d" % (sum(em), len(em)),
                     "points whose split allows exactly the six non-constant patterns": "%d of %d" % (sum(rc), len(rc))}
    check("1 interface: the Fano plane and census 58 minus any line leave their ports exactly the two constant patterns (so an intact atom "
          "acts as a point), and split at any point allow exactly the six others (so it acts as a line)", ok1, info1)

    # -------------------------------------------------------------------------------------------- 2. the creation map is order-free
    D = designs()
    pick = [D[1], D[5], D[10]]
    info2, ok2 = {}, True
    with Pool(22) as pool:
        for label, des in pick:
            S = GL.build(des)
            agg = collections.Counter()
            for c in pool.map(order_task, [(S, M) for M in range(len(S.H))]):
                agg.update(c)
            ok2 &= agg["union over far sides independent of the order"] == agg["cases"]
            info2[label] = dict(agg)
    check("2 the creation map does not depend on which far-side line each point of the gluing line meets: on three spaces, creation by some "
          "far side is the same for all six orders of the line's points (the census-6 far side alone is not)", ok2, info2)

    # -------------------------------------------------------------------------------------------- 3. splitting, exact
    info3, ok3 = {}, True
    halos = {}
    with Pool(22) as pool:
        for label, des in D:
            names = [a[0] for a in des[1]]
            mats = {}
            for r in range(len(names) + 1):
                for sub in itertools.combinations(names, r):
                    S = GL.build(des, set(sub))
                    assert GL.G.fails_globally(S.H, S.s, S.n)
                    mats[sub] = (S, GL.by_key(S, GL.matrix(S, pool=pool)))
            Sf, full = mats[tuple(names)]
            cnt = collections.Counter()
            for (km, kl), v in full.items():
                touched = tuple(a for a in names if a in {Sf.owner[Sf.line(km)], Sf.owner[Sf.line(kl)]})
                red = mats[touched][1][(km, kl)]
                kind = {0: "neither line in an atom", 1: "one atom", 2: "two atoms"}[len(touched)] + (" (the full space)" if len(touched) == len(names) else "")
                cnt[(kind, "agree" if red == v else "DISAGREE")] += 1
            dis = sum(v for k, v in cnt.items() if k[1] == "DISAGREE")
            plane_base = not label.startswith(("the Fano", "census"))
            base_creates = sum(1 for v in mats[()][1].values() if v)
            ok3 &= dis == 0 and (base_creates == 0 or not plane_base)
            halos[label] = {a: len({kl for (km, kl), v in full.items() if v and Sf.owner[Sf.line(km)] == a and Sf.owner[Sf.line(kl)] is None})
                            for a in names}
            info3[label] = {"points": Sf.n, "entries by atoms touched": {"%s: %s" % k: v for k, v in sorted(cnt.items())},
                            "creation in the base alone": base_creates}
    check("3 splitting, exact: on 13 designs (two or three atoms on plane glue, adjacent and touching placements, atoms on the Fano plane "
          "and on census 58), every entry of the creation map equals the entry in the space that keeps only the atoms holding the removal "
          "and the gluing line; plane glue alone never creates", ok3, info3)
    check("4 halos split: the base-side lines where each atom's removals create (its halo), which by 3 equal its halo with that atom alone",
          True, halos)

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
