#!/usr/bin/env python3
"""Check for ONE-BIT-20261108-001A-P001: joint consistency on the sixteen one-bit candidates' parent collars.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B check.py      (writes result.json and joint_table.pkl's digest)

Reuses ROUND-PRICE-20261108-001B's check (load_core, the unlabelled supports) and ROUND-PRICE-20261108-001A's decor_lib (laws).
- Q(s): labelled core level-one collars whose decorated cut is legal (as in ROUND-PRICE-20261108-001B).
- Arc consistency on Q(s), then the joint test: a labelled collar (Y, p) survives when its neighbours can all be given surviving
  labelled collars that agree with p on shared tiles and pairwise with each other: the two placed collars are compatible as collars
  of one tiling (each lists the other's tiles that touch its centre, no two distinct tiles overlap) and agree on shared tiles. The
  neighbour-pair compatibilities are geometric and the same for every decoration, so they are computed once.
- Iterated with arc consistency to a fixed point. Survivors split into labelled collars of L(s), keys outside L(s), and non-keys.
- A decoration whose survivors all lie in L(s) forces the pinwheel (ROUND-PRICE-20261108-001B, Theorem 1, with the joint test in
  place of arc consistency: a tiling's own collars pass the joint test).
Controls: every labelled key of each law survives; the constant decoration, which admits the rhombus crystal, keeps survivors
outside its law; the decoration 10001 / 01100, which admits a period-4 brick crystal, keeps survivors outside its law."""
from __future__ import annotations

import importlib.util
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


RB = _load("round_price_b_check", ROOT / "proofs/ROUND-PRICE-20261108-001B/ROUND-PRICE-20261108-001B-P001_labelled_composition_for_the_survivors/check.py")
D = RB.D
GE = RB.GE
A = D.A
BASE = D.BASE
CANDIDATES = [((0, 0, 0, 0, 1), (1, 0, 0, 1, 0)), ((0, 0, 0, 1, 0), (1, 0, 1, 1, 1)), ((0, 0, 1, 1, 1), (1, 0, 0, 1, 0)),
              ((0, 1, 1, 0, 0), (1, 0, 0, 0, 1)), ((1, 0, 0, 0, 0), (0, 0, 1, 0, 1)), ((1, 0, 1, 0, 1), (0, 0, 0, 0, 0)),
              ((1, 0, 1, 0, 1), (0, 0, 1, 1, 0)), ((1, 0, 1, 1, 0), (0, 0, 1, 0, 1))]
CONTROLS = [((0, 0, 0, 0, 0), (1, 1, 1, 1, 1)), ((1, 0, 0, 0, 1), (0, 1, 1, 0, 0))]
G = RB.G


def pair_table(yi):
    """for core collar yi: for each pair of its neighbours (a < b) and each pair of supporting collars (m at s_a, m2 at s_b), the
    shared-tile position pairs if the two placed collars are compatible, else absent"""
    sets, sup = G["sets"], G["sup"][yi]
    nbrs = sorted(sup, key=lambda s: sorted(s))
    placed = {}

    def P(s, m):
        if (s, m) not in placed:
            pl = [GE.tile_in(s, y) for y in sets[m]]
            placed[(s, m)] = (pl, set(pl), {t: k for k, t in enumerate(pl)})
        return placed[(s, m)]
    out = {}
    for a in range(len(nbrs)):
        for b in range(a + 1, len(nbrs)):
            sa, sb = nbrs[a], nbrs[b]
            for m, _ in sup[sa]:
                pa, Sa, ia = P(sa, m)
                for m2, _ in sup[sb]:
                    pb, Sb, ib = P(sb, m2)
                    if any(A.touch(x, sb) and x not in Sb for x in pa) or any(A.touch(y, sa) and y not in Sa for y in pb):
                        continue
                    if any(GE.interiors_meet(x, y) for x in Sa - Sb for y in Sb - Sa):
                        continue
                    out[(a, m, b, m2)] = tuple((ia[t], ib[t]) for t in Sa & Sb)
    return yi, [tuple(sorted(s)) for s in nbrs], out


def joint(sig):
    sk, core, sup, tables = G["sk"], G["core"], G["sup"], G["tables"]
    L = {n: set(v) for n, v in D.law(sk, sig).items()}
    Q = {}
    for yi, (Y, iskey) in enumerate(core):
        Yl = list(Y)
        kids = [(sk.index.get(t), src) for t, src in D.images(1, Yl)]
        need = [(src, L.get(n, set()), max(j for j, _ in src)) for n, src in kids]
        out, p = [], [0] * len(Yl)

        def rec(j):
            if j == len(Yl):
                out.append(tuple(p))
                return
            for bit in (0, 1):
                p[j] = bit
                if all(tuple(sig[p[jj]][mm] for jj, mm in src) in allowed for src, allowed, mj in need if mj == j):
                    rec(j + 1)
        rec(0)
        Q[yi] = out
    alive = {(yi, p): True for yi, ps in Q.items() for p in ps}

    def options(yi, p, s):
        return [(m, p2) for m, pairs in sup[yi][s] for p2 in Q.get(m, ()) if alive.get((m, p2)) and all(p[i] == p2[j] for i, j in pairs)]

    def ac():
        changed = True
        while changed:
            changed = False
            for k, ok in list(alive.items()):
                if ok and any(not options(k[0], k[1], s) for s in sup[k[0]]):
                    alive[k] = False
                    changed = True
    ac()
    after_ac = sum(alive.values())
    rounds = 0
    over = [0]
    while True:
        rounds += 1
        dead = []
        for (yi, p), ok in list(alive.items()):
            if not ok:
                continue
            nbr_order, table = tables[yi]
            nbrs = [tuple(sorted(s)) for s in sup[yi]]
            idx = {key: n for n, key in enumerate(nbr_order)}
            opts = sorted(((idx[tuple(sorted(s))], options(yi, p, s)) for s in sup[yi]), key=lambda x: len(x[1]))
            chosen = []
            budget = [200000]

            def ok_pair(a, m, pa, b, m2, pb):
                if a > b:
                    a, m, pa, b, m2, pb = b, m2, pb, a, m, pa
                pairs = table.get((a, m, b, m2))
                return pairs is not None and all(pa[i] == pb[j] for i, j in pairs)

            def dfs(i):
                budget[0] -= 1
                if budget[0] < 0:
                    return True          # undecided within the budget: kept, so no collar is removed without proof
                if i == len(opts):
                    return True
                a, o = opts[i]
                for m, p2 in o:
                    if all(ok_pair(a, m, p2, b, m2, q2) for b, m2, q2 in chosen):
                        chosen.append((a, m, p2))
                        if dfs(i + 1):
                            return True
                        chosen.pop()
                return False
            if not dfs(0):
                dead.append((yi, p))
            if budget[0] < 0:
                over[0] += 1
        for k in dead:
            alive[k] = False
        ac()
        if not dead:
            break
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
    keys_ok = all(alive.get((yi, p)) for yi, (Y, iskey) in enumerate(core) if iskey for p in L.get(sk.index[(1, Y)], ()))
    return {"sig": [list(sig[0]), list(sig[1])], "Q": sum(len(v) for v in Q.values()), "after arc consistency": after_ac,
            "joint rounds": rounds, "kept undecided at the search budget": over[0], "survivors: in L(s), keys outside L(s), non-keys": [inL, keynot, nonkey],
            "every labelled key survives": keys_ok, "forces the pinwheel": keynot == 0 and nonkey == 0}


def main():
    t0 = time.time()
    G["sk"] = D.Skeleton()
    core = RB.load_core()
    G["core"] = core
    sets = [Y for Y, _ in core]
    RB.init_sets(sets)
    with mp.Pool(16, initializer=RB.init_sets, initargs=(sets,)) as pool:
        G["sup"] = dict(pool.map(RB.supports_of, range(len(sets))))
    G["sets"] = sets
    t1 = time.time()
    with mp.Pool(16) as pool:
        tabs = pool.map(pair_table, range(len(sets)), chunksize=2)
    G["tables"] = {yi: (order, tab) for yi, order, tab in tabs}
    res = {"checks": {}, "controls": {}, "census": {"core collars": len(core), "supports seconds": round(t1 - t0, 1),
                                                    "pair table seconds": round(time.time() - t1, 1),
                                                    "compatible neighbour pairs": sum(len(t) for _, t in G["tables"].values())}}
    with mp.Pool(10) as pool:
        rows = pool.map(joint, CANDIDATES + CONTROLS)
    res["census"]["candidates"] = rows[:len(CANDIDATES)]
    res["census"]["controls"] = rows[len(CANDIDATES):]
    res["census"]["decorations that force the pinwheel"] = [r["sig"] for r in rows[:len(CANDIDATES)] if r["forces the pinwheel"]]
    res["controls"]["every labelled key of each law survives"] = all(r["every labelled key survives"] for r in rows)
    res["controls"]["both crystal-admitting decorations keep survivors outside their laws"] = all(
        sum(r["survivors: in L(s), keys outside L(s), non-keys"][1:]) > 0 for r in rows[len(CANDIDATES):])
    res["status"] = "passed" if all(res["controls"].values()) else "failed"
    res["failures"] = [k for k, v in res["controls"].items() if not v]
    res["runtime_seconds"] = round(time.time() - t0, 1)
    (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
