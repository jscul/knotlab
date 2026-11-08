#!/usr/bin/env python3
"""Check for ROUND-PRICE-20261108-001B-P001: do the eighteen surviving one-bit decorations force composition?

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B check.py      (writes result.json)

Uses ticket A's decor_lib.py (the skeleton of the cut, decorated laws) and COLLAR-PLANE-20261108-001B's level_one_law.json (the
level-one law L1 with its arc-consistent core of 156 collars per handedness).
For each of the nine survivors of ticket A up to exchanging the labels, and two controls:
  (1) parent labels: for every core collar Y, SAT decides whether the labels of Y's central tile's five children can differ from
      s(0) and s(1) while every child's collar is in the law L(s);
  (2) Q(s): the labellings p of Y's tiles whose decorated cut gives every child a collar of L(s);
  (3) arc consistency on Q(s): a labelled collar survives while every neighbour has a surviving compatible labelled collar whose
      labels agree on the tiles they share (unlabelled compatibility as in COLLAR-PLANE-20261108-001B);
  (4) the survivors are split into labelled collars of L(s), labelled pinwheel keys outside L(s), and non-key collars.
  (5) a third crystal: the 16 brick-row planes with diagonals of period 4 that COLLAR-PLANE-20261108-001C found collar-legal after
      one cut (big1_rows.jsonl), each cut k = 1, 2, 3 times, admitted or excluded as in ticket A.
Controls: the constant decoration (which admits the rhombus crystal, ticket A) keeps survivors outside its law; every labelled key of
each law is in Q(s) and survives; the laws and Q(s) are mirror symmetric."""
from __future__ import annotations

import itertools
import json
import multiprocessing as mp
import sys
import time
from collections import defaultdict
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/ROUND-PRICE-20261108-001A/ROUND-PRICE-20261108-001A-P001_one_hidden_bit_against_the_crystal"))
import decor_lib as D  # noqa: E402
sys.path.insert(0, str(ROOT / "experiments/GROWTH-LAW-20261107-001B/GROWTH-LAW-20261107-001B-E001_pinwheel_grown_outward"))
import growth_engine as GE  # noqa: E402

A = D.A
BASE = D.BASE
L1_JSON = ROOT / "proofs/COLLAR-PLANE-20261108-001B/COLLAR-PLANE-20261108-001B-P001_the_collar_law_forces_one_level/level_one_law.json"
SURVIVORS = [((0, 0, 0, 0, 1), (1, 0, 0, 1, 0)), ((0, 0, 0, 1, 0), (1, 0, 1, 1, 1)), ((0, 0, 1, 1, 1), (1, 0, 0, 1, 0)),
             ((0, 1, 1, 0, 0), (1, 0, 0, 0, 1)), ((1, 0, 0, 0, 0), (0, 0, 1, 0, 1)), ((1, 0, 0, 0, 1), (0, 1, 1, 0, 0)),
             ((1, 0, 1, 0, 1), (0, 0, 0, 0, 0)), ((1, 0, 1, 0, 1), (0, 0, 1, 1, 0)), ((1, 0, 1, 1, 0), (0, 0, 1, 0, 1))]
CONTROL = ((0, 0, 0, 0, 0), (1, 1, 1, 1, 1))
BIG1 = ROOT / "artifacts/COLLAR-PLANE-20261108-001C/COLLAR-PLANE-20261108-001C-E001_periodic_planes_after_cutting/run/big1_rows.jsonl"
G = {}


def period4_planes(sk):
    """the passing planes of COLLAR-PLANE-C1 with two collar types (the brick rows with period-4 diagonals), as decor_lib Planes"""
    def rect_h(x, y, d):
        a, b, c, e = (x, y), (x + 2, y), (x + 2, y + 1), (x, y + 1)
        return [(a, b, e), (c, e, b)] if d == 0 else [(b, a, c), (e, c, a)]

    def rect_v(x, y, d):
        a, b, c, e = (x, y), (x + 1, y), (x + 1, y + 2), (x, y + 2)
        return [(b, c, a), (e, a, c)] if d == 0 else [(a, e, b), (c, b, e)]
    out = []
    seen = set()
    for line in BIG1.read_text().splitlines():
        r = json.loads(line)
        if not r["passes"] or r["plane"] in seen:
            continue
        seen.add(r["plane"])
        m, n, doms, diags = json.loads(r["plane"])
        cell = []
        for (kind, i, j), d in zip(doms, diags):
            cell += rect_h(i, j, d) if kind == "h" else rect_v(i, j, d)
        P = D.Plane(sk, cell, ((m, 0), (0, n)))
        if len({sk.types[t][1] for t, _ in P.root}) == 2:
            out.append((r["plane"], P))
    return out


def load_core():
    d = json.loads(L1_JSON.read_text())
    out = []
    for c in d["collars"]:
        if c["core"]:
            tiles = [((Fr(t[0]), Fr(t[1])), (Fr(t[2]), Fr(t[3])), (Fr(t[4]), Fr(t[5]))) for t in c["tiles"]]
            out.append((tuple(D.canon(tiles)), c["key"]))
    return out


def supports_of(n):
    sets, idx = G["sets"], G["idx"]
    S = sets[n]
    Sset = set(S)
    out = {}
    for s in S:
        if s == BASE:
            continue
        b = tuple(A.to_frame(s, X) for X in BASE)
        need = [x for x in S if x != s and A.touch(x, s)]
        lst = []
        for m in idx.get(b, ()):
            placed = [GE.tile_in(s, y) for y in sets[m]]
            pset = set(placed)
            if any(x not in pset for x in need) or any(A.touch(y, BASE) and y not in Sset for y in placed):
                continue
            if any(GE.interiors_meet(x, y) for y in pset - Sset for x in Sset - pset):
                continue
            lst.append((m, tuple((S.index(y), k) for k, y in enumerate(placed) if y in Sset)))
        out[s] = lst
    return n, out


def init_sets(sets):
    G["sets"] = sets
    idx = defaultdict(list)
    for n, S in enumerate(sets):
        for t in S:
            idx[t].append(n)
    G["idx"] = idx


def analyse(sig):
    sk, core, sup = G["sk"], G["core"], G["sup"]
    from pysat.solvers import Cadical153
    L = {n: set(v) for n, v in D.law(sk, sig).items()}
    flat = {(m, l) for m, ls in L.items() for l in ls}
    mirror = all((sk.index[(-sk.types[n][0], sk.types[n][1])], lab) in flat for n, lab in flat)
    res = {"sig": [list(sig[0]), list(sig[1])], "labelled keys": sum(len(v) for v in L.values()), "law mirror symmetric": mirror}
    Q = {}
    free_parent = 0
    q_mirror = True
    for yi, (Y, iskey) in enumerate(core):
        Yl = list(Y)
        kids = {}
        for h in (1, -1):
            kids[h] = [(sk.index.get(t), src) for t, src in D.images(h, Yl)]
        # (1) can the centre's children avoid s(0), s(1)?
        var = {}
        cons = [([var.setdefault((j, m), len(var) + 1) for j, m in src], sorted(L.get(n, ()))) for n, src in kids[1]]
        bpos = Yl.index(BASE)
        centre = [var.setdefault((bpos, m), len(var) + 1) for m in range(5)]
        for vec in itertools.product((0, 1), repeat=5):
            if vec in sig:
                continue
            S = Cadical153()
            top = len(var)
            ok = all(allowed for _, allowed in cons)
            if ok:
                for vs, allowed in cons:
                    ys = []
                    for tup in allowed:
                        top += 1
                        ys.append(top)
                        for v, b in zip(vs, tup):
                            S.add_clause([-top, v if b else -v])
                    S.add_clause(ys)
                for v, b in zip(centre, vec):
                    S.add_clause([v if b else -v])
                if S.solve():
                    free_parent += 1
                    S.delete()
                    break
            S.delete()
        # (2) Q: labellings of Y with a legal decorated cut, for both handednesses
        def legal(h):
            need = [(src, L.get(n, set()), max(j for j, _ in src)) for n, src in kids[h]]
            out, p = [], [0] * len(Yl)

            def rec(j):
                if j == len(Yl):
                    out.append(tuple(p))
                    return
                for b in (0, 1):
                    p[j] = b
                    if all(tuple(sig[p[jj]][m] for jj, m in src) in allowed for src, allowed, mj in need if mj == j):
                        rec(j + 1)
            rec(0)
            return out
        Q[yi] = legal(1)
        q_mirror &= Q[yi] == legal(-1)
    res["core collars whose centre's children can avoid s(0), s(1)"] = free_parent
    res["Q mirror symmetric"] = q_mirror
    res["Q (labelled level-one collars)"] = sum(len(v) for v in Q.values())
    # (3) arc consistency
    alive = {(yi, p): True for yi, ps in Q.items() for p in ps}
    rounds = 0
    while True:
        rounds += 1
        dead = [(yi, p) for (yi, p), ok in alive.items() if ok and any(
            not any(alive.get((m, p2)) and all(p[a] == p2[b] for a, b in pairs) for m, pairs in lst for p2 in Q.get(m, ()))
            for lst in sup[yi].values())]
        for k in dead:
            alive[k] = False
        if not dead:
            break
    # (4) split the survivors
    inL = keynot = nonkey = 0
    for (yi, p), ok in alive.items():
        if not ok:
            continue
        Y, iskey = core[yi]
        if not iskey:
            nonkey += 1
        elif p in L.get(sk.index[(1, Y)], set()):
            inL += 1
        else:
            keynot += 1
    res["arc consistency rounds"] = rounds
    res["survivors: in L(s), keys outside L(s), non-keys"] = [inL, keynot, nonkey]
    keys_ok = all(alive.get((yi, p)) for yi, (Y, iskey) in enumerate(core) if iskey
                  for p in L.get(sk.index[(1, Y)], ()))
    res["every labelled key of the law survives"] = keys_ok
    res["rhombus collar survives with some labelling"] = any(alive.get((G["rh"], p)) for p in Q.get(G["rh"], ()))
    res["forces composition at every level"] = keynot == 0 and nonkey == 0 and free_parent == 0
    allowed = {n: sorted(v) for n, v in L.items()}
    first = None
    for name, P in G["p4"]:
        for k in (1, 2, 3):
            hit = None
            for Lt in [L2 for m in (1, 2) for L2 in D.sublattices(m)]:
                ok, model = D.periodic(P, allowed, k, Lt, want_model=True)
                if ok:
                    hit = Lt
                    break
            if hit:
                if first is None or k < first[1]:
                    first = (name, k, list(hit))
                break
    res["period-4 brick crystals: first admitted (plane, k, torus)"] = first
    return res


def main():
    t0 = time.time()
    G["sk"] = D.Skeleton()
    core = load_core()
    G["core"] = core
    sets = [Y for Y, _ in core]
    rhombus = D.Plane(G["sk"], D.RHOMBUS, D.RHOMBUS_LATTICE)
    X = G["sk"].types[rhombus.root[0][0]][1]
    G["rh"] = sets.index(X)
    G["p4"] = period4_planes(G["sk"])
    for _, P in G["p4"]:
        for k in range(4):
            for sp in P.descendants(k):
                P.tile(*sp)
    init_sets(sets)
    with mp.Pool(16, initializer=init_sets, initargs=(sets,)) as pool:
        G["sup"] = dict(pool.map(supports_of, range(len(sets))))
    res = {"checks": {}, "controls": {}, "census": {"core collars (handedness +1), keys": [len(core), sum(k for _, k in core)],
                                                    "supports seconds": round(time.time() - t0, 1)}}
    with mp.Pool(11) as pool:
        rows = pool.map(analyse, SURVIVORS + [CONTROL])
    res["census"]["survivors"] = rows[:-1]
    res["census"]["control (constant decoration)"] = rows[-1]
    res["checks"]["laws and Q are mirror symmetric"] = all(r["law mirror symmetric"] and r["Q mirror symmetric"] for r in rows)
    res["controls"]["every labelled key of each law survives"] = all(r["every labelled key of the law survives"] for r in rows)
    res["controls"]["the constant decoration keeps the rhombus collar and survivors outside its law"] = (
        rows[-1]["rhombus collar survives with some labelling"] and sum(rows[-1]["survivors: in L(s), keys outside L(s), non-keys"][1:]) > 0)
    res["census"]["period-4 brick planes tested"] = len(G["p4"])
    res["census"]["survivors admitting a period-4 brick crystal"] = [[r["sig"], r["period-4 brick crystals: first admitted (plane, k, torus)"]]
                                                                    for r in rows[:-1] if r["period-4 brick crystals: first admitted (plane, k, torus)"]]
    res["census"]["decorations forcing composition at every level (by this test)"] = [r["sig"] for r in rows[:-1]
                                                                                      if r["forces composition at every level"]]
    res["status"] = "passed" if all(res["checks"].values()) and all(res["controls"].values()) else "failed"
    res["failures"] = [k for k, v in {**res["checks"], **res["controls"]}.items() if not v]
    res["runtime_seconds"] = round(time.time() - t0, 1)
    (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
