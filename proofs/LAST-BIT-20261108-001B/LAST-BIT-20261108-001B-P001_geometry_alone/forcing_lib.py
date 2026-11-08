"""The forcing test on geometry alone for one decorated substitution (LAST-BIT-20261108-001B-P001).

Given a set S of labelled complete collars (keys with labels) that every tile of a plane must have, one level up:
  Q(S)      the labelled core level-one collars (Y, p) whose decorated cut gives every child of Y's central tile a collar in S;
  parents   whether, for every core Y, the central tile's five children can carry only s(0) or s(1) when their collars lie in S;
  joint(.)  arc consistency and the joint (radius-2) test on Q(S), as in ONE-BIT-20261108-001A;
  extend(.) exhaustive extension: a labelled collar survives when a patch in which every tile within tile distance d of its centre
            has a complete labelled collar of the current set can be built around it (a labelled version of the growth engine).
The iteration S_0 = L(s), S_{n+1} = survivors of Q(S_n) stops at a repeat. If every S_n consists of pinwheel keys and parents are
forced at every step, every plane obeying L(s) has a collar-legal parent tiling at every level, so it is a pinwheel tiling."""
from __future__ import annotations

import importlib.util
import itertools
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


OA = _load("one_bit_a_check", ROOT / "proofs/ONE-BIT-20261108-001A/ONE-BIT-20261108-001A-P001_joint_consistency_on_the_sixteen/check.py")
RB = OA.RB
D, GE, A = OA.D, OA.GE, OA.A
BASE = D.BASE
G = OA.G


def setup(pool_size=16):
    import multiprocessing as mp
    G["sk"] = D.Skeleton()
    core = RB.load_core()
    G["core"] = core
    sets = [Y for Y, _ in core]
    RB.init_sets(sets)
    with mp.Pool(pool_size, initializer=RB.init_sets, initargs=(sets,)) as pool:
        G["sup"] = dict(pool.map(RB.supports_of, range(len(sets))))
    G["sets"] = sets
    with mp.Pool(pool_size) as pool:
        tabs = pool.map(OA.pair_table, range(len(sets)), chunksize=2)
    G["tables"] = {yi: (order, tab) for yi, order, tab in tabs}
    G["kids"] = {yi: [(G["sk"].index.get(t), src) for t, src in D.images(1, list(Y))] for yi, Y in enumerate(sets)}


def law_as_sets(sig):
    """L(s) as {type index of a complete key: set of label tuples}"""
    return {n: set(v) for n, v in D.law(G["sk"], sig).items()}


def to_core(S):
    """a set of labelled keys given as {type index: labels} -> {core index: labels} for keys that are core collars (h = +1)"""
    sk, core = G["sk"], G["core"]
    out = defaultdict(set)
    for yi, (Y, iskey) in enumerate(core):
        if iskey:
            out[yi] |= S.get(sk.index[(1, Y)], set())
    return out


def Q_of(S, sig):
    """S: {type index: labels} for the children's collars. Returns {core index: [labellings]}"""
    Q = {}
    for yi, Y in enumerate(G["sets"]):
        need = [(src, S.get(n, set()), max(j for j, _ in src)) for n, src in G["kids"][yi]]
        out, p = [], [0] * len(Y)

        def rec(j):
            if j == len(Y):
                out.append(tuple(p))
                return
            for bit in (0, 1):
                p[j] = bit
                if all(tuple(sig[p[jj]][mm] for jj, mm in src) in allowed for src, allowed, mj in need if mj == j):
                    rec(j + 1)
        rec(0)
        Q[yi] = out
    return Q


def parents_forced(S, sig):
    """for every core collar: can the central tile's children carry a vector other than s(0), s(1) with collars in S?"""
    from pysat.solvers import Cadical153
    free = 0
    for yi, Y in enumerate(G["sets"]):
        var = {}
        cons = [([var.setdefault((j, m), len(var) + 1) for j, m in src], sorted(S.get(n, ()))) for n, src in G["kids"][yi]]
        if not all(allowed for _, allowed in cons):
            continue
        bpos = list(Y).index(BASE)
        centre = [var.setdefault((bpos, m), len(var) + 1) for m in range(5)]
        for vec in itertools.product((0, 1), repeat=5):
            if vec in sig:
                continue
            Sv = Cadical153()
            top = len(var)
            for vs, allowed in cons:
                ys = []
                for tup in allowed:
                    top += 1
                    ys.append(top)
                    for v, b in zip(vs, tup):
                        Sv.add_clause([-top, v if b else -v])
                Sv.add_clause(ys)
            for v, b in zip(centre, vec):
                Sv.add_clause([v if b else -v])
            hit = Sv.solve()
            Sv.delete()
            if hit:
                free += 1
                break
    return free


def joint(Q, alive=None):
    """arc consistency and the joint test on Q; returns the alive map"""
    sup, tables = G["sup"], G["tables"]
    if alive is None:
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
    while True:
        dead = []
        for (yi, p), ok in list(alive.items()):
            if not ok:
                continue
            order, table = tables[yi]
            idx = {key: n for n, key in enumerate(order)}
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
                    return True
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
        for k in dead:
            alive[k] = False
        ac()
        if not dead:
            return alive


# ---- exhaustive extension with labels ------------------------------------------------------------------------------------------------
class LabelledPatch(GE.Patch):
    """growth_engine.Patch with a label on every tile; keys are (handedness, frozenset of (tile in frame, label))"""

    def __init__(self, keys_by_h, seed, seed_label):
        self.labels = {}
        self.by_h = keys_by_h
        self.complete_set = {k for ks in keys_by_h.values() for k in ks}
        self.containing = defaultdict(list)
        for h, ks in keys_by_h.items():
            for k in ks:
                for item in k[1]:
                    self.containing[(h, item)].append(k)
        self.tiles, self.index, self.cells, self.touch = [], {}, defaultdict(set), []
        from fractions import Fraction as Fr
        self.cell = Fr(1)
        self.add_l(seed, seed_label)

    def add_l(self, t, label):
        self.labels[t] = label
        return GE.Patch.add(self, t)

    def pop(self):
        t = self.tiles[-1]
        GE.Patch.pop(self)
        del self.labels[t]

    def collar(self, i):
        t = self.tiles[i]
        return frozenset((tuple(A.to_frame(t, X) for X in self.tiles[j]), self.labels[self.tiles[j]]) for j in self.touch[i] | {i})

    def is_complete(self, i):
        return (self.handed(i), self.collar(i)) in self.complete_set

    def candidates(self, i):
        cur = self.collar(i)
        h = self.handed(i)
        centre = (BASE, self.labels[self.tiles[i]])
        return [k for k in self.containing.get((h, centre), ()) if cur <= k[1]], cur

    def realizable(self, i, key, cur=None):
        cur = self.collar(i) if cur is None else cur
        t = self.tiles[i]
        new = []
        for x, lab in key[1] - cur:
            g = GE.tile_in(t, x)
            if g in self.index or self.overlaps(g):
                return None
            new.append((g, lab))
        return new

    def consistent(self, i):
        cands, cur = self.candidates(i)
        if (self.handed(i), cur) in self.complete_set:
            return True
        return any(self.realizable(i, k, cur) is not None for k in cands)

    def try_move(self, i, key, keep=False):
        new = self.realizable(i, key)
        if new is None:
            return 0
        added = 0
        for g, lab in new:
            if g in self.index or self.overlaps(g):
                break
            self.add_l(g, lab)
            added += 1
        ok = added == len(new)
        if ok:
            affected = set()
            for k in range(len(self.tiles) - added, len(self.tiles)):
                affected.add(k)
                affected |= self.touch[k]
            ok = all(self.consistent(j) for j in affected)
        if not ok or not keep:
            for _ in range(added):
                self.pop()
        return added if ok else 0

    def legal_moves(self, i):
        cands, _ = self.candidates(i)
        return [k for k in cands if self.try_move(i, k) > 0]


def extends(keys_by_h, start_key, depth, budget):
    """can the labelled collar start_key (handedness +1, at BASE) be extended so that every tile within tile distance depth of
    BASE has a complete labelled collar? True / False / None (budget exhausted)"""
    h, items = start_key
    lab = dict(items)[BASE]
    P = LabelledPatch(keys_by_h, BASE, lab)
    for x, l in items:
        if x != BASE:
            if P.overlaps(x):
                return False
            P.add_l(x, l)
    if not all(P.consistent(i) for i in range(len(P.tiles))):
        return False
    steps = [budget]

    def dist():
        d = {0: 0}
        q = [0]
        for u in q:
            for w in P.touch[u]:
                if w not in d:
                    d[w] = d[u] + 1
                    q.append(w)
        return d

    def dfs():
        steps[0] -= 1
        if steps[0] < 0:
            return None
        dd = dist()
        inc = [i for i in range(len(P.tiles)) if dd.get(i, 99) <= depth and not P.is_complete(i)]
        if not inc:
            return True
        best = None
        for i in inc:
            lm = P.legal_moves(i)
            if best is None or len(lm) < len(best[1]):
                best = (i, lm)
                if len(lm) <= 1:
                    break
        i, lm = best
        for k in lm:
            n0 = len(P.tiles)
            if P.try_move(i, k, keep=True) == 0:
                continue
            r = dfs()
            while len(P.tiles) > n0:
                P.pop()
            if r is not False:
                return r
        return False
    return dfs()


def keys_from(alive):
    """the labelled collars alive at level one, as labelled keys of both handednesses"""
    out = {1: [], -1: []}
    for (yi, p), ok in alive.items():
        if ok:
            items = frozenset(zip(G["sets"][yi], p))
            out[1].append((1, items))
            out[-1].append((-1, items))
    return out
