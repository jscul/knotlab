#!/usr/bin/env python3
"""Checks for TWO-BIT-SCREEN-20261105-001B: what screening gives the brace dictionary.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import chain_lib as CH  # noqa: E402

GL, BL, DL = CH.GL, CH.BL, CH.DL
F = CH.F
T0 = time.time()
OUT = {}


def sat_solutions(lines, signs, n, skip=None):
    """all solutions by SAT model enumeration, in claim_lib.solutions order (identical rows; far faster above 20 points)"""
    import numpy as np
    from pysat.solvers import Solver
    clauses = []
    for i, (L, sg) in enumerate(zip(lines, signs)):
        if i == skip:
            continue
        lit = [(q + 1) if t == 0 else -(q + 1) for q, t in zip(L, sg)]
        clauses += [lit, [-x for x in lit]]
    with Solver(name="cadical153", bootstrap_with=clauses) as s:
        codes = sorted({sum(1 << (abs(v) - 1) for v in m if 0 < v <= n) for m in s.enum_models()})
    codes = np.array(codes, dtype=np.int64)
    if len(codes) == 0:
        return np.zeros((0, n), dtype=np.int8)
    return ((codes[:, None] >> np.arange(n)) & 1).astype(np.int8)


GL.CL.solutions = sat_solutions  # used by genus_lib.row_task


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def cut_positions(S, name):
    """(line, position) of the named atom's points on lines owned by the rest of the space"""
    return [(k, j) for k in range(len(S.H)) if S.owner[k] != name for j, q in enumerate(S.H[k]) if S.pkey[q][0] == name]


def normal(H, s):
    """lines with signs up to flipping all three signs of a line (not-all-equal is unchanged)"""
    return sorted((tuple(L), tuple(x ^ x0 for x in sg)) for L, sg in zip(H, s) for x0 in [sg[0]])


def task_twists(spec):
    S = CH.build_two(spec)
    cut = cut_positions(S, "E")
    knot = []
    for tw in itertools.product((0, 1), repeat=3):
        s2 = [list(x) for x in S.s]
        for (k, j), t in zip(cut, tw):
            s2[k][j] ^= t
        if len(sat_solutions(S.H, s2, S.n)) == 0 and all(len(sat_solutions(S.H, s2, S.n, skip=m)) > 0 for m in range(len(S.H))):
            knot.append(tw)
    # complementing every point of the atom turns twist 000 into 111
    atom_pts = {q for q in range(S.n) if S.pkey[q][0] == "E"}
    s3 = [[x ^ (q in atom_pts) for x, q in zip(sg, L)] for L, sg in zip(S.H, S.s)]
    s1 = [list(x) for x in S.s]
    for (k, j) in cut:
        s1[k][j] ^= 1
    return knot, normal(S.H, s3) == normal(S.H, s1)


def trees():
    """spaces built from Fano atoms alone, three atoms on a Fano plane (25 points)"""
    g = lambda i: ("g", i)  # noqa: E731
    off01 = min(k for k, L in enumerate(F[0]) if 0 not in L and 1 not in L)
    l0 = min(k for k, L in enumerate(F[0]) if 0 in L)
    ID = (0, 1, 2)
    A = lambda n, kind, key, x=0, perm=ID: (n, kind, key, F, x, perm)  # noqa: E731
    base = GL.base(*F)
    return {
        "a star: atoms at two points and at a line off them": (base, [A("X", "point", g(0)), A("Y", "point", g(1)), A("Z", "line", g(off01))]),
        "depth two through emitters: X at a point, Z at a point of X, Y at a line": (base, [A("X", "point", g(0)), A("Z", "point", ("X", 1)),
                                                                                         A("Y", "line", g(off01))]),
        "depth two through receivers: X at a line, Z at a line of X, Y at a point": (base, [A("X", "line", g(l0)), A("Z", "line", ("X", 2)),
                                                                                          A("Y", "point", g(6))]),
        "mixed: X at a point, Z at a line of X, Y at a point": (base, [A("X", "point", g(0), 0, (1, 0, 2)), A("Z", "line", ("X", 3)),
                                                                      A("Y", "point", g(3), 0, (0, 2, 1))]),
    }


def four_chains():
    """four atoms in a path A-B-C-D: B the base Fano plane, A and C attached at elements of B, D attached at an element of C; every
    direction of the three cuts, two port permutations"""
    g = lambda i: ("g", i)  # noqa: E731
    lA, lC = 0, next(k for k, L in enumerate(F[0]) if k != 0)
    out = {}
    for dA, dC, dD in itertools.product(("point", "line"), repeat=3):
        for perm in ((0, 1, 2), (2, 0, 1)):
            S = GL.base(*F)
            S = (GL.attach_point(S, g(0), F, 0, "A", perm) if dA == "point" else GL.attach_line(S, g(lA), F, 0, "A", perm))
            S = (GL.attach_point(S, g(3), F, 0, "C", perm) if dC == "point" else GL.attach_line(S, g(lC), F, 0, "C", perm))
            S = (GL.attach_point(S, ("C", 4), F, 0, "D", perm) if dD == "point" else GL.attach_line(S, ("C", 5), F, 0, "D", perm))
            out["A at a %s / C at a %s / D at a %s of C, permutation %s" % (dA, dC, dD, perm)] = S
    return out


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    bt = CH.brace_tree_dictionary()

    with Pool(22) as pool:
        # 1
        specs2 = CH.two_specs()
        tw = pool.map(task_twists, specs2, chunksize=4)
        kinds = collections.Counter(tuple(k) for k, same in tw)
        ok1 = set(kinds) == {((0, 0, 0), (1, 1, 1))} and all(same for k, same in tw)
        check("1 every gluing of two Fano atoms at one cut (7 base points x 7 atom lines x 6 port permutations) is a knot space for exactly "
              "two twists of the cut, and they differ by complementing the atom, so the chains below cover every gluing up to complementing "
              "points", ok1, {"twists giving knot spaces": {str(k): v for k, v in kinds.items()}})

        # 2
        S2 = [CH.build_two(sp) for sp in specs2]
        M2 = CH.matrices(S2, pool)
        t2 = CH.place_table(S2, M2)
        det2 = all(len(c) == 1 for c in t2.values())
        agree2 = {CH.name_place(p): (sorted(c), sorted(bt[p]) if p in bt else None) for p, c in t2.items()}
        ok2 = det2 and all(b is None or a == b for a, b in agree2.values()) and all(p in bt for p in t2 if p[0] == "apart")
        check("2 two atoms at one cut, all 294 gluings: every place has one relation, the same as in BRACE-TREE's dictionary",
              ok2, {"place: (relation here, relation in BRACE-TREE)": agree2,
                    "ordered pairs": sum(sum(c.values()) for c in t2.values())})

        # 3
        specs3 = CH.three_specs(removed=(0, 3))
        S3 = [CH.build_three(sp) for sp in specs3]
        M3 = CH.matrices(S3, pool, chunksize=2)
        t3 = CH.place_table(S3, M3)
        det3 = all(len(c) == 1 for c in t3.values())
        agree3 = {CH.name_place(p): (sorted(c), sorted(bt[p]) if p in bt else None) for p, c in t3.items()}
        ok3 = det3 and all(b is None or a == b for a, b in agree3.values()) and all(p in bt for p in t3 if p[0] == "apart")
        check("3 three atoms in a chain, all %d gluings (four kinds of element pairs on the middle atom, two removed elements on each end "
              "atom, every pair of port permutations): every place has one relation, the same as in BRACE-TREE's dictionary" % len(S3),
              ok3, {"place: (relation here, relation in BRACE-TREE)": agree3,
                    "ordered pairs": sum(sum(c.values()) for c in t3.values())})
        chain_rel = {p: next(iter(c)) for p, c in list(t2.items()) + list(t3.items())}

        # 4
        T = trees()
        ST = [GL.build(des) for des in T.values()]
        for S in ST:
            assert len(sat_solutions(S.H, S.s, S.n)) == 0
        MT = CH.matrices(ST, pool, chunksize=1)
        c4 = collections.Counter()
        for (label, des), S, r in zip(T.items(), ST, MT):
            t = DL.Tree(S)
            for a in range(len(S.H)):
                for b in range(len(S.H)):
                    if a == b:
                        continue
                    p = t.place(a, b)
                    if p[0] == "apart" and len(p[3]) > 2:
                        continue
                    pred = "mutual" if p[0] == "same" else chain_rel.get(p)
                    if pred is None:
                        c4["pairs at places no chain shows"] += 1
                        continue
                    have = BL.relation(r, a, b)
                    fwd_pred = pred in ("mutual", "forward")
                    bwd_pred = pred in ("mutual", "backward")
                    fwd, bwd = GL.creates(r, a, b), GL.creates(r, b, a)
                    c4["pairs"] += 1
                    c4["creation the chain shows is present"] += (fwd or not fwd_pred) and (bwd or not bwd_pred)
                    c4["relation equal to the chain's"] += have == pred
                    if p[0] == "same":
                        c4["same-atom pairs"] += 1
                        c4["same-atom pairs mutual"] += have == "mutual"
        ok4 = (c4["pairs"] == c4["creation the chain shows is present"] and c4["same-atom pairs"] == c4["same-atom pairs mutual"]
               and c4["pairs at places no chain shows"] == 0)
        check("4 four spaces built from Fano atoms alone (25 points): at every pair of lines in atoms at most two apart, the creation the "
              "chain shows is present (the contraction theorem), lines of one atom are mutual (the block lemma), and the relations equal "
              "the chain's in every pair (the non-creating entries too, as the lifting conjecture predicts)",
              ok4 and c4["pairs"] == c4["relation equal to the chain's"], dict(c4))

        # 5
        C4 = four_chains()
        S5 = list(C4.values())
        M5 = CH.matrices(S5, pool, chunksize=1)
        t5 = CH.place_table(S5, M5)
        far = {CH.name_place(p): dict(c) for p, c in t5.items() if p[0] == "apart" and len(p[3]) == 3}
        det5 = all(len(c) == 1 for p, c in t5.items())
        known = {CH.name_place(p): (sorted(c), sorted(bt[p]) if p in bt else None) for p, c in t5.items()
                 if p[0] == "apart" and len(p[3]) == 3}
        check("5 four atoms in a path (computed, every direction of the three cuts, two port permutations): at distance three every place "
              "has one relation, and it agrees with BRACE-TREE's dictionary where the dictionary has that place",
              det5 and all(b is None or a == b for a, b in known.values()),
              {"distance-three places: (relation here, relation in BRACE-TREE)": known, "spaces": len(S5)})

        # 6
        def touching(p):
            """the relation predicted by the touching rule: a line receives creation from another atom exactly when it touches its own
            atom's cut toward that atom (role emitter or cut line)"""
            if p[0] == "same":
                return "mutual"
            a_open, b_open = p[5] in ("emitter", "cut line"), p[6] in ("emitter", "cut line")
            return {(True, True): "mutual", (False, True): "forward", (True, False): "backward", (False, False): "silent"}[(a_open, b_open)]
        rows6 = collections.Counter()
        for name, t in (("two atoms", t2), ("three atoms", t3), ("four-atom paths", t5)):
            for p, c in t.items():
                rows6[(name, "agree" if set(c) == {touching(p)} else "DISAGREE")] += 1
        check("6 the touching rule: in every chain computed (distances one to three), a removal in one atom creates at a line of another "
              "atom exactly when that line touches its atom's cut toward the first atom (it lies on the receiving cut, or its atom emits "
              "there); the removed line's own role never matters; lines of one atom are mutual",
              all(k[1] == "agree" for k in rows6), {"%s: %s" % k: v for k, v in sorted(rows6.items())})

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
