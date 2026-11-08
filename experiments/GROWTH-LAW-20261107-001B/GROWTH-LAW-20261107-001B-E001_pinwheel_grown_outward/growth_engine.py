"""Outward growth of the pinwheel by its own collar law (GROWTH-LAW-20261107-001B-E001).

Tiles are (O, P, Q) as in PINWHEEL-ATLAS-20261107-001A's atlas_lib: the right angle, the end of the long leg, the end of the short
leg. All tiles live in the seed tile's affine frame (O at 0, Q at (1, 0), P at (0, 1)); incidence, touching and overlap are affine
notions, so nothing depends on the frame. The law is the list of the 108 complete collar keys of that ticket's Theorem 2: a tile's
collar is the tile with every tile that touches it, written in the tile's own frame with its handedness.

- A tile is *complete* when its collar is one of the 108 keys exactly.
- A tile is *consistent* when some complete key with its handedness contains its collar and the key's missing tiles overlap no
  tile already placed.
- A *move* completes one incomplete tile's collar with one complete key. It is *legal* when the tiles it adds overlap nothing and
  every tile it touches (old and new) stays consistent.
- A tile with no legal move is a *dead end*: no growth in any order can ever complete it.

Nothing else is remembered: no labels, levels, positions in a hierarchy, or coordinates beyond the placed tiles themselves (the
coordinates are bookkeeping for the planar map)."""
from __future__ import annotations

import random
import sys
from collections import defaultdict
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ATLAS = ROOT / "proofs/PINWHEEL-ATLAS-20261107-001A/PINWHEEL-ATLAS-20261107-001A-P001_the_complete_radius_2_atlas"
sys.path.insert(0, str(ATLAS))
import atlas_lib as A  # noqa: E402

BASE = A.BASE


def law():
    """the closure of collar keys and its complete ones, by handedness"""
    keys = A.closure()
    complete = [k for k in keys if A.complete(k)]
    by_h = defaultdict(list)
    for k in complete:
        by_h[k[0]].append(k)
    return keys, complete, by_h


def from_frame(c, x):
    O, P, Q = c
    return (O[0] + x[0] * (Q[0] - O[0]) + x[1] * (P[0] - O[0]), O[1] + x[0] * (Q[1] - O[1]) + x[1] * (P[1] - O[1]))


def tile_in(c, t):
    """the tile t (given in c's frame) in the frame where c is given"""
    return tuple(from_frame(c, x) for x in t)


def interiors_meet(S, T):
    """do two triangles' interiors intersect? (separating axis: some edge line of one has the other on its closed far side)"""
    for X, Y in ((S, T), (T, S)):
        for i in range(3):
            a, b, c = X[i], X[(i + 1) % 3], X[(i + 2) % 3]
            sc = A.cross(a, b, c)
            if sc == 0:
                continue
            if all(A.cross(a, b, p) * sc <= 0 for p in Y):
                return False
    return True


class Patch:
    def __init__(self, complete_by_h, seed=BASE, cell=Fr(1)):
        self.by_h = complete_by_h
        self.complete_set = {k for ks in complete_by_h.values() for k in ks}
        self.tiles = []
        self.index = {}
        self.cells = defaultdict(set)
        self.touch = []
        self.cell = cell
        self.add(seed)

    # ------------------------------------------------------------------ bookkeeping
    def _cells_of(self, t):
        xs = [p[0] for p in t]
        ys = [p[1] for p in t]
        c = self.cell
        for i in range(int(min(xs) // c), int(max(xs) // c) + 1):
            for j in range(int(min(ys) // c), int(max(ys) // c) + 1):
                yield (i, j)

    def near(self, t):
        out = set()
        for cl in self._cells_of(t):
            out |= self.cells.get(cl, set())
        return out

    def add(self, t):
        k = len(self.tiles)
        self.tiles.append(t)
        self.index[t] = k
        self.touch.append(set())
        for j in self.near(t):
            if A.touch(t, self.tiles[j]):
                self.touch[k].add(j)
                self.touch[j].add(k)
        for cl in self._cells_of(t):
            self.cells[cl].add(k)
        return k

    def pop(self):
        k = len(self.tiles) - 1
        t = self.tiles.pop()
        del self.index[t]
        for j in self.touch.pop():
            self.touch[j].discard(k)
        for cl in self._cells_of(t):
            self.cells[cl].discard(k)

    # ------------------------------------------------------------------ the law
    def collar(self, i):
        t = self.tiles[i]
        return frozenset(tuple(A.to_frame(t, X) for X in self.tiles[j]) for j in self.touch[i] | {i})

    def handed(self, i):
        return A.orient(self.tiles[i])

    def is_complete(self, i):
        return (self.handed(i), self.collar(i)) in self.complete_set

    def overlaps(self, new):
        for j in self.near(new):
            if self.tiles[j] != new and interiors_meet(new, self.tiles[j]):
                return True
        return False

    def realizable(self, i, key, cur=None):
        """the global tiles this key would add to tile i's collar, or None if one overlaps a placed tile"""
        cur = self.collar(i) if cur is None else cur
        t = self.tiles[i]
        new = [tile_in(t, x) for x in key[1] - cur]
        for n in new:
            if n in self.index or self.overlaps(n):
                return None
        return new

    def candidates(self, i):
        cur = self.collar(i)
        return [k for k in self.by_h[self.handed(i)] if cur <= k[1]], cur

    def consistent(self, i):
        cands, cur = self.candidates(i)
        if (self.handed(i), cur) in self.complete_set:
            return True
        return any(self.realizable(i, k, cur) is not None for k in cands)

    def try_move(self, i, key, keep=False):
        """apply key to tile i if legal; return the number of tiles added (0 if illegal). With keep=False it is undone."""
        new = self.realizable(i, key)
        if new is None:
            return 0
        added = 0
        for n in new:
            if n in self.index or self.overlaps(n):
                break
            self.add(n)
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
        cands, cur = self.candidates(i)
        return [k for k in cands if self.try_move(i, k) > 0]

    def incomplete(self):
        return [i for i in range(len(self.tiles)) if not self.is_complete(i)]


def tile_distance(P, src=0):
    """tile-graph distance (tiles adjacent when they touch) from the seed"""
    d = {src: 0}
    q = [src]
    for u in q:
        for w in P.touch[u]:
            if w not in d:
                d[w] = d[u] + 1
                q.append(w)
    return d


class MoveCache:
    """legal moves per tile, recomputed only for tiles near the last move. A tile's legal moves depend on placed tiles within a
    few tile sizes of it (its collar, the tiles a key would add, and their neighbours' collars), so a move invalidates the tiles
    in cells within `reach` of the tiles it added. check_cache=True recomputes everything and asserts agreement (a control)."""

    def __init__(self, P, reach=8, check_cache=False):
        self.P = P
        self.reach = reach
        self.memo = {}
        self.check = check_cache

    def get(self, i):
        if i not in self.memo:
            self.memo[i] = self.P.legal_moves(i)
        elif self.check:
            fresh = self.P.legal_moves(i)
            assert fresh == self.memo[i], ("stale cache", i)
        return self.memo[i]

    def moved(self, first_new):
        P = self.P
        dirty = set()
        for k in range(first_new, len(P.tiles)):
            for (ci, cj) in P._cells_of(P.tiles[k]):
                for di in range(-self.reach, self.reach + 1):
                    for dj in range(-self.reach, self.reach + 1):
                        dirty |= P.cells.get((ci + di, cj + dj), set())
        for j in dirty:
            self.memo.pop(j, None)


def grow(complete_by_h, order, rng, max_tiles, seed=BASE, log_every=None, check_cache=False, replay=None):
    """grow from one tile in the given order until max_tiles tiles or a dead end. Returns the patch and a record of the run.
    replay: a function (patch, tile index) -> the key a genuine pinwheel patch gives that tile; the run then follows it, and it is
    an error if that key is not among the legal moves (a control: a genuine continuation is never a dead end)."""
    P = Patch(complete_by_h, seed)
    C = MoveCache(P, check_cache=check_cache)
    rec = {"order": order, "moves": 0, "forced": 0, "choices": 0, "options": [], "outcome": None}
    while len(P.tiles) < max_tiles:
        inc = P.incomplete()
        if not inc:
            rec["outcome"] = "closed"
            break
        if order == "forced":
            pick = None
            for i in inc:
                lm = C.get(i)
                if len(lm) <= 1:
                    pick = (i, lm)
                    break
            if pick is None:
                pick = (inc[0], C.get(inc[0]))
            i, lm = pick
        else:
            if order == "bfs":
                i = inc[0]
            elif order == "finger":
                i = inc[-1]
            elif order == "random":
                i = rng.choice(inc)
            else:
                raise ValueError(order)
            lm = C.get(i)
        if not lm:
            rec["outcome"] = "dead end"
            rec["dead_tile"] = i
            break
        rec["moves"] += 1
        if len(lm) == 1:
            rec["forced"] += 1
        else:
            rec["choices"] += 1
            rec["options"].append(len(lm))
        if replay is not None:
            k = replay(P, i)
            if k not in lm:
                rec["outcome"] = "replay rejected"
                break
        else:
            k = lm[0] if len(lm) == 1 else rng.choice(lm)
        first = len(P.tiles)
        P.try_move(i, k, keep=True)
        C.moved(first)
        if log_every and rec["moves"] % log_every == 0:
            print(order, rec["moves"], len(P.tiles), rec["forced"], rec["choices"], flush=True)
    if rec["outcome"] is None:
        rec["outcome"] = "size reached"
    rec["tiles"] = len(P.tiles)
    d = tile_distance(P)
    inc = set(P.incomplete())
    rec["complete_radius"] = (min(d[i] for i in inc) - 1) if inc else max(d.values())
    rec["max_radius"] = max(d.values())
    return P, rec


# ---------------------------------------------------------------------- pinwheel patches in the seed's frame (controls)
def pinwheel_in_frame(k, pick):
    """the level-k patch T_k, written in the frame of one of its tiles chosen by pick(list of tiles) -> index"""
    tiles = A.pinwheel_patch(k)
    c = tiles[pick(tiles)]
    cf = tuple((Fr(p[0]), Fr(p[1])) for p in c)
    return [tuple(A.to_frame(cf, (Fr(p[0]), Fr(p[1]))) for p in t) for t in tiles], c


class Genuine:
    """a genuine pinwheel patch (T_k in the frame of one of its tiles), for the replay control and the legality tests"""

    def __init__(self, k, pick="centre"):
        tiles = A.pinwheel_patch(k)
        cx = sum(p[0] for t in tiles for p in t) / (3 * len(tiles))
        cy = sum(p[1] for t in tiles for p in t) / (3 * len(tiles))
        idx = min(range(len(tiles)), key=lambda i: (sum(p[0] for p in tiles[i]) / 3 - cx) ** 2 + (sum(p[1] for p in tiles[i]) / 3 - cy) ** 2)
        c = tuple((Fr(p[0]), Fr(p[1])) for p in tiles[idx])
        self.tiles = [tuple(A.to_frame(c, (Fr(p[0]), Fr(p[1]))) for p in t) for t in tiles]
        self.seed = self.tiles[idx]
        assert self.seed == BASE
        self.set = set(self.tiles)
        self.cell = Fr(1)
        self.cells = defaultdict(list)
        for t in self.tiles:
            for cl in Patch._cells_of(self, t):
                self.cells[cl].append(t)

    def touching(self, t):
        out = set()
        for cl in Patch._cells_of(self, t):
            for u in self.cells.get(cl, ()):
                if A.touch(t, u):
                    out.add(u)
        return out

    def key(self, t):
        return (A.orient(t), frozenset(tuple(A.to_frame(t, q) for q in X) for X in self.touching(t) | {t}))

    def replay(self, P, i):
        t = P.tiles[i]
        assert t in self.set, "the replayed patch left the genuine one"
        return self.key(t)
