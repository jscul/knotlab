#!/usr/bin/env python3
"""Check for COLLAR-PLANE-20261108-001B-P001: the collar law forces one level of composition.

    python3 -B check.py        (about four minutes with 22 workers; writes result.json and level_one_law.json)

Exact rational arithmetic, with PINWHEEL-ATLAS-20261107-001A's atlas_lib and GROWTH-LAW-20261107-001B's growth engine (Patch: placed
tiles, collars, consistency) and legality module (parent_of, the inverse of the cut on keys).
- Claims: every complete key has one child index and one parent among its preimages under the cut.
- Siblings: for every complete key K, every sibling s of the central tile that touches it, and every complete key Y for s that is
  compatible with K as collars of one tiling, either Y names the same parent, or placing K and Y leaves a tile inconsistent (no complete
  key contains its collar without overlapping a placed tile). The children of one triangle touch in a connected graph.
- L1: every complete collar X around a triangle whose cut gives all five children complete keys, enumerated exactly (handedness +1),
  with its arc-consistent core (the collars that can have, at every neighbour, a compatible L1 collar, iterated) and the radius-2 test.
- The rhombus lattice's collar (COLLAR-PLANE-20261108-001A) is in L1, in its core, and not a key.
- GROWTH-LAW-20261107-001B's four forced runs that left the pinwheel (stress_test_growth.json): no conflicting parent claim; their
  level-one complete collars that are not keys all lie in L1.
- Controls: compatibility alone does not force agreement; a genuine pair is consistent; the keys survive the core; L1 contains every
  key; the patches' level-one tiles include non-keys."""
from __future__ import annotations

import json
import multiprocessing as mp
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROWTH = ROOT / "experiments/GROWTH-LAW-20261107-001B/GROWTH-LAW-20261107-001B-E001_pinwheel_grown_outward"
sys.path.insert(0, str(GROWTH))
import growth_engine as E  # noqa: E402
import legality as L  # noqa: E402

A = E.A
BASE = E.BASE
PATCHES = ROOT / "research/GROWTH-LAW-20261107-001/stress_test_growth.json"
W = {}


# ---- the law and its claims ---------------------------------------------------------------------------------------------------------
def setup():
    keys, complete, by_h = E.law()
    W["keys"], W["complete"], W["by_h"] = keys, complete, by_h
    W["cset"] = set(complete)
    C = L.Climber(keys)
    W["inv"] = C.inv
    W["claim"] = {}
    for k in complete:
        pre = C.inv[k]
        W["claim"][k] = {(c, L.parent_of(BASE, c)) for _, c in pre}


def place(s, K):
    return [E.tile_in(s, x) for x in K[1]]


def compatible(S1, s1, S2, s2, touching=True):
    """tile sets S1 (collar of tile s1) and S2 (collar of tile s2), both placed: can both be collars in one tiling? With touching,
    s1 and s2 touch, so each must lie in the other's collar (for complete collars the other conditions already imply it)."""
    S1, S2 = set(S1), set(S2)
    if touching and (s2 not in S1 or s1 not in S2):
        return False
    for x in S1:
        if A.touch(x, s2) and x not in S2:
            return False
    for y in S2:
        if A.touch(y, s1) and y not in S1:
            return False
    for x in S1 - S2:
        for y in S2 - S1:
            if E.interiors_meet(x, y):
                return False
    return True


def patch_of(tiles, by_h):
    P = E.Patch(by_h)
    for x in tiles:
        if x != BASE and x not in P.index:
            if P.overlaps(x):
                return None
            P.add(x)
    return P


def siblings():
    """agreement of touching siblings; returns counts and the disagreeing configurations' consistency"""
    out = Counter()
    for K in W["complete"]:
        (c, a), = W["claim"][K]
        kids = A.cut(a)
        assert kids[c] == BASE
        for j, s in enumerate(kids):
            if j == c or not A.touch(s, BASE):
                continue
            assert s in K[1], "a touching sibling is missing from the key"
            hs = A.orient(s) * K[0]
            for Y in W["by_h"][hs]:
                if not compatible(K[1], BASE, place(s, Y), s):
                    continue
                (cy, ay), = W["claim"][Y]
                agree = cy == j and E.tile_in(s, ay) == a
                out[(K[0], "agree" if agree else "disagree")] += 1
                if agree or K[0] != 1:
                    continue
                P = patch_of(set(K[1]) | set(place(s, Y)), W["by_h"])
                consistent = P is not None and all(P.consistent(i) for i in range(len(P.tiles)))
                out["disagreeing and consistent"] += consistent
                out["disagreeing and inconsistent"] += not consistent
    return out


# ---- L1 ----------------------------------------------------------------------------------------------------------------------------
def enumerate_L1():
    kids = A.cut(BASE)
    cands = []
    for c in kids:
        h = A.orient(c)
        out = []
        for K in W["by_h"][h]:
            T = place(c, K)
            Ts = set(T)
            if any(A.touch(c, d) and d not in Ts for d in kids):
                continue
            if any(x not in kids and E.interiors_meet(x, BASE) for x in T):
                continue
            out.append(T)
        cands.append(out)

    def pair_ok(ci, Ti, cj, Tj):
        Si, Sj = set(Ti), set(Tj)
        if any(A.touch(x, cj) and x not in Sj for x in Ti) or any(A.touch(y, ci) and y not in Si for y in Tj):
            return False
        return not any(E.interiors_meet(x, y) for x in Si - Sj for y in Sj - Si)

    combos = []

    def dfs(i, chosen):
        if i == 5:
            combos.append(list(chosen))
            return
        for T in cands[i]:
            if all(pair_ok(kids[j], chosen[j], kids[i], T) for j in range(i)):
                chosen.append(T)
                dfs(i + 1, chosen)
                chosen.pop()
    dfs(0, [])
    results = set()

    def parents(U, idx, B, keytiles, Tlist):
        while idx < len(U) and any(U[idx] in set(A.cut(b)) for b in B):
            idx += 1
        if idx == len(U):
            X = (1, frozenset([BASE] + B))
            if A.complete(X):
                results.add(X)
            return
        u = U[idx]
        for j in range(5):
            b = L.parent_of(u, j)
            if E.interiors_meet(b, BASE) or any(b != b2 and E.interiors_meet(b, b2) for b2 in B):
                continue
            ch = A.cut(b)
            if any(A.touch(x, ci) and x not in set(T) for x in ch for ci, T in zip(kids, Tlist)):
                continue
            if any(x != y and E.interiors_meet(x, y) for x in ch for y in keytiles):
                continue
            B.append(b)
            parents(U, idx + 1, B, keytiles, Tlist)
            B.pop()
    for combo in combos:
        keytiles = set().union(*map(set, combo))
        U = sorted(x for x in keytiles if x not in kids)
        parents(U, 0, [], keytiles, combo)
    return [len(c) for c in cands], len(combos), sorted(results, key=lambda X: sorted(X[1]))


def init_core(sets):
    W["sets"] = sets
    idx = defaultdict(list)
    for n, S in enumerate(sets):
        for t in S:
            idx[t].append(n)
    W["idx"] = idx
    W["touch"] = [{b: frozenset(x for x in S if x != b and A.touch(x, b)) for b in S} for S in sets]


def supports(n):
    S = W["sets"][n]
    out = {}
    for s in S:
        if s == BASE:
            continue
        b = tuple(A.to_frame(s, X) for X in BASE)
        need = [x for x in S if x != s and A.touch(x, s)]
        comp = []
        for m in W["idx"].get(b, ()):
            if any(E.tile_in(s, y) not in S for y in W["touch"][m][b]):
                continue
            placed = {E.tile_in(s, y) for y in W["sets"][m]}
            if any(x not in placed for x in need):
                continue
            if any(E.interiors_meet(x, y) for y in placed - S for x in S - placed):
                continue
            comp.append(m)
        out[s] = comp
    return n, out


def radius2(args):
    n, alive, sup = args
    S = W["sets"][n]
    opts = []
    for s in S:
        if s == BASE:
            continue
        o = [m for m in sup[s] if alive[m]]
        if not o:
            return n, False
        opts.append((s, o))
    opts.sort(key=lambda so: len(so[1]))
    cache = {}

    def P(s, m):
        if (s, m) not in cache:
            cache[(s, m)] = frozenset(E.tile_in(s, y) for y in W["sets"][m])
        return cache[(s, m)]
    chosen = []

    def dfs(i):
        if i == len(opts):
            return True
        s, o = opts[i]
        for m in o:
            if all(compatible(P(s, m), s, P(s2, m2), s2, touching=False) for s2, m2 in chosen):
                chosen.append((s, m))
                if dfs(i + 1):
                    return True
                chosen.pop()
        return False
    return n, dfs(0)


def core(sets, pool):
    sup = dict(pool.imap_unordered(supports, range(len(sets)), chunksize=4))
    alive = [True] * len(sets)

    def ac():
        changed = True
        while changed:
            changed = False
            for n in range(len(sets)):
                if alive[n] and any(not any(alive[m] for m in comp) for comp in sup[n].values()):
                    alive[n] = False
                    changed = True
    ac()
    after_ac = sum(alive)
    rounds = 0
    while True:
        rounds += 1
        dead = [n for n, ok in pool.imap_unordered(radius2, [(n, alive, sup[n]) for n in range(len(sets)) if alive[n]]) if not ok]
        for n in dead:
            alive[n] = False
        ac()
        if not dead:
            break
    return alive, after_ac, rounds


# ---- the patches that left the pinwheel ------------------------------------------------------------------------------------------------
def level_one(tiles):
    """parent claims of complete tiles; conflicts; the level-one complete collars (of parents whose five children claim them)"""
    P = E.Patch(W["by_h"])
    for t in tiles[1:]:
        P.add(t)
    parent = {}
    for i, t in enumerate(P.tiles):
        if P.is_complete(i):
            (c, a), = W["claim"][(P.handed(i), P.collar(i))]
            parent[i] = (c, E.tile_in(t, a))
    groups = defaultdict(list)
    for i, (c, a) in parent.items():
        groups[a].append(c)
    conflicts = 0
    for a in groups:
        for j, s in enumerate(A.cut(a)):
            if s in P.index:
                i = P.index[s]
                if i in parent and parent[i] != (j, a):
                    conflicts += 1
            elif any(E.interiors_meet(s, P.tiles[q]) for q in P.near(s)):
                conflicts += 1
    full = [a for a, cs in groups.items() if sorted(cs) == [0, 1, 2, 3, 4]]
    Q = E.Patch(W["by_h"], seed=full[0]) if full else None
    collars = []
    if Q is not None:
        for a in full[1:]:
            Q.add(a)
        for i, a in enumerate(Q.tiles):
            K = (A.orient(a), frozenset(tuple(A.to_frame(a, X) for X in Q.tiles[j]) for j in Q.touch[i] | {i}))
            if A.complete(K):
                collars.append(K)
    return len(parent), conflicts, len(full), collars


def main():
    t0 = time.time()
    setup()
    res = {"checks": {}, "controls": {}, "census": {}}
    res["checks"]["108 complete keys"] = len(W["complete"]) == 108
    res["checks"]["every complete key names one child index and one parent"] = all(len(v) == 1 for v in W["claim"].values())
    kids = A.cut(BASE)
    adj = {i: {j for j in range(5) if j != i and A.touch(kids[i], kids[j])} for i in range(5)}
    seen, stack = {0}, [0]
    while stack:
        for j in adj[stack.pop()]:
            if j not in seen:
                seen.add(j)
                stack.append(j)
    res["checks"]["the five children of a triangle touch in a connected graph"] = len(seen) == 5

    sib = siblings()
    res["census"]["sibling pairs (central handedness, outcome)"] = {f"{k[0]} {k[1]}": v for k, v in sib.items() if isinstance(k, tuple)}
    res["census"]["disagreeing pairs (handedness +1): inconsistent, consistent"] = [sib["disagreeing and inconsistent"],
                                                                                  sib["disagreeing and consistent"]]
    res["checks"]["every disagreeing compatible sibling pair leaves a tile inconsistent"] = sib["disagreeing and consistent"] == 0
    res["checks"]["the counts are mirror symmetric"] = (sib[(1, "agree")] == sib[(-1, "agree")]
                                                         and sib[(1, "disagree")] == sib[(-1, "disagree")])
    res["controls"]["compatibility alone does not force agreement"] = sib[(1, "disagree")] > 0

    # a genuine pair is consistent: two touching siblings of the level-5 patch, with their genuine keys
    G = E.Genuine(5)
    gs = [t for t in G.tiles if A.touch(t, BASE) and t != BASE]
    Kb = G.key(BASE)
    (c0, a0), = W["claim"][Kb]
    sib0 = [s for j, s in enumerate(A.cut(a0)) if j != c0 and s in gs][0]
    Pg = patch_of(set(Kb[1]) | set(place(sib0, G.key(sib0))), W["by_h"])
    res["controls"]["a genuine sibling pair is consistent"] = Pg is not None and all(Pg.consistent(i) for i in range(len(Pg.tiles)))

    # L1
    cand_counts, ncombos, L1 = enumerate_L1()
    keys_plus = {K for K in W["complete"] if K[0] == 1}
    nk = sum(1 for X in L1 if X in W["cset"])
    res["census"]["L1: candidate keys per child, consistent assignments, collars (handedness +1)"] = [cand_counts, ncombos, len(L1)]
    res["census"]["L1: keys, non-keys"] = [nk, len(L1) - nk]
    res["controls"]["L1 contains every key of handedness +1"] = keys_plus <= set(L1)

    sets = [X[1] for X in L1]
    with mp.Pool(22, initializer=init_core, initargs=(sets,)) as pool:
        init_core(sets)
        alive, after_ac, rounds = core(sets, pool)
    core_keys = sum(1 for n, X in enumerate(L1) if alive[n] and X in W["cset"])
    res["census"]["core: after arc consistency, after the radius-2 test (rounds)"] = [after_ac, sum(alive), rounds]
    res["census"]["core: keys, non-keys"] = [core_keys, sum(alive) - core_keys]
    res["controls"]["every key survives the core"] = core_keys == len(keys_plus)

    # the rhombus lattice's collar (tiles legs 1, 2 around the origin; collar of the tile ((0,0),(0,2),(1,0)))
    rh = [((0, 0), (0, 2), (1, 0)), ((0, 0), (0, 2), (-1, 0)), ((0, 0), (0, -2), (1, 0)), ((0, 0), (0, -2), (-1, 0))]
    plane = [tuple((Fr(p[0] + i + j), Fr(p[1] + 2 * i - 2 * j)) for p in t) for i in range(-2, 3) for j in range(-2, 3) for t in rh]
    t1 = plane[[n for n, t in enumerate(plane) if t == tuple((Fr(x), Fr(y)) for x, y in rh[0])][0]]
    col = {u for u in plane if u != t1 and A.touch(t1, u)} | {t1}
    X = frozenset(tuple(A.to_frame(t1, p) for p in u) for u in col)
    pos = [n for n, Y in enumerate(L1) if Y[1] == X]
    res["checks"]["the rhombus lattice's collar is in L1 and its core, and is not a key"] = (
        len(pos) == 1 and alive[pos[0]] and (1, X) not in W["cset"] and (-1, X) not in W["cset"])

    # the patches that left the pinwheel
    data = json.loads(PATCHES.read_text())
    L1sets = {Y[1] for Y in L1}
    rows = []
    found = set()
    for r in data["rows"]:
        if r["kind"] != "forced long":
            continue
        tiles = [tuple((Fr(p[0]), Fr(p[1])) for p in t) for t in r["tiles_list"]]
        ncl, conf, nfull, collars = level_one(tiles)
        nonkeys = [K for K in collars if K not in W["cset"]]
        found |= {K[1] for K in nonkeys}
        rows.append({"seed": r["seed"], "tiles": len(tiles), "claims": ncl, "conflicts": conf, "level-one tiles": nfull,
                     "level-one complete collars": len(collars), "of which not keys": len(nonkeys),
                     "non-keys outside L1": sum(1 for K in nonkeys if K[1] not in L1sets)})
    res["census"]["forced runs that left the pinwheel"] = rows
    res["census"]["distinct level-one non-key collars in them"] = len(found)
    res["checks"]["the four patches compose with no conflicting claim"] = all(x["conflicts"] == 0 for x in rows) and len(rows) == 4
    res["checks"]["their level-one non-key collars all lie in L1"] = all(x["non-keys outside L1"] == 0 for x in rows)
    res["controls"]["their level-one tiles include non-keys"] = len(found) > 0

    (HERE / "level_one_law.json").write_text(json.dumps({
        "about": "L1 for handedness +1: complete collars around a triangle whose cut gives all five children complete pinwheel keys "
                 "(the mirror collars are the same sets with handedness -1). Tiles are (O, P, Q) in the central tile's affine frame.",
        "collars": [{"tiles": sorted([[str(c) for p in t for c in p] for t in Y[1]]), "key": Y in W["cset"], "core": alive[n]}
                    for n, Y in enumerate(L1)]}, indent=0) + "\n")
    res["status"] = "passed" if all(res["checks"].values()) and all(res["controls"].values()) else "failed"
    res["failures"] = [k for k, v in {**res["checks"], **res["controls"]}.items() if not v]
    res["runtime_seconds"] = round(time.time() - t0, 1)
    (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
