"""Is a grown patch a pinwheel patch? (GROWTH-LAW-20261107-001B-E001)

Two tests, both against PINWHEEL-ATLAS-20261107-001A's results:
- atlas_check: every dart of the patch's planar map farther than r + 1 from its boundary has its radius-2 rooted code among the
  1,168 codes of the atlas (the pinwheel's radius-2 law).
- embed: the patch occurs in some pinwheel tiling. Climb the hierarchy from the seed: a level-i ancestor of the seed is a tile a_i
  with collar key K_i, and the seed's level-(i+1) ancestor is any tile a_{i+1} with some child c equal to a_i whose key K_{i+1} has
  Phi(K_{i+1})[c] = K_i (Lemma 1 of the atlas proof). Every patch tile that overlaps the region of a_i's collar must be one of the
  i-fold descendants of that collar's tiles; a chain fails as soon as one does not. The patch occurs in a pinwheel tiling when some
  chain reaches a level whose collar region holds the whole patch with every tile among its descendants (the collar is legal, and
  so are its descendants: they occur in some T_k)."""
from __future__ import annotations

import json
from collections import defaultdict
from fractions import Fraction as Fr

import growth_engine as E

A = E.A

ATLAS_CODES = None


def atlas_codes():
    global ATLAS_CODES
    if ATLAS_CODES is None:
        data = json.loads((E.ATLAS / "atlas.json").read_text())
        ATLAS_CODES = {tuple((d, tuple(r)) for d, r in code) for code, _ in data["atlas"]}
    return ATLAS_CODES


def atlas_check(tiles, r=2):
    """(darts tested, darts whose radius-r code is not in the atlas)"""
    codes = atlas_codes()
    M = A.build_map(A.integerize(tiles), 1)
    db = A.bfs_dist(M["rot"], list(M["boundary"]))
    total = bad = 0
    for (u, v) in M["dlab"]:
        if db.get(u, 0) <= r + 1 or db.get(v, 0) <= r + 1:
            continue
        total += 1
        if A.code(M["rot"], u, v, r) not in codes:
            bad += 1
    return total, bad


# ---------------------------------------------------------------------- climbing the hierarchy
_W = [  # child vertices (O', P', Q') as weights on the parent's (O, P, Q), from atlas_lib.cut
    ((Fr(0), Fr(1, 5), Fr(4, 5)), (Fr(1), Fr(0), Fr(0)), (Fr(0), Fr(0), Fr(1))),              # (H, O, Q)
    ((Fr(1, 2), Fr(1, 10), Fr(2, 5)), (Fr(1, 2), Fr(1, 2), Fr(0)), (Fr(1), Fr(0), Fr(0))),    # (F1, M, O)
    ((Fr(1, 2), Fr(1, 10), Fr(2, 5)), (Fr(1, 2), Fr(1, 2), Fr(0)), (Fr(0), Fr(1, 5), Fr(4, 5))),  # (F1, M, H)
    ((Fr(0), Fr(3, 5), Fr(2, 5)), (Fr(0), Fr(1, 5), Fr(4, 5)), (Fr(1, 2), Fr(1, 2), Fr(0))),  # (F2, H, M)
    ((Fr(0), Fr(3, 5), Fr(2, 5)), (Fr(0), Fr(1), Fr(0)), (Fr(1, 2), Fr(1, 2), Fr(0))),        # (F2, P, M)
]


def _inv3(M):
    a, b, c = M[0]
    d, e, f = M[1]
    g, h, i = M[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return ((( e * i - f * h) / det, -(b * i - c * h) / det, (b * f - c * e) / det),
            (-(d * i - f * g) / det, (a * i - c * g) / det, -(a * f - c * d) / det),
            (( d * h - e * g) / det, -(a * h - b * g) / det, (a * e - b * d) / det))


_WINV = [_inv3(W) for W in _W]


def _combine(weights, pts):
    return tuple(sum(w * p[k] for w, p in zip(weights, pts)) for k in range(2))


def parent_of(child, c):
    """the tile whose child number c is `child`"""
    Winv = _WINV[c]
    return tuple(_combine(Winv[r], child) for r in range(3))


def _check_cut():
    t = ((Fr(0), Fr(0)), (Fr(0), Fr(1)), (Fr(1), Fr(0)))
    for c, ch in enumerate(A.cut(t)):
        assert tuple(_combine(_W[c][r], t) for r in range(3)) == ch
        assert parent_of(ch, c) == t


_check_cut()


def bbox(t):
    xs = [p[0] for p in t]
    ys = [p[1] for p in t]
    return min(xs), min(ys), max(xs), max(ys)


def boxes_meet(b1, b2):
    return b1[0] <= b2[2] and b2[0] <= b1[2] and b1[1] <= b2[3] and b2[1] <= b1[3]


def descendants_in_box(tiles, depth, box):
    cur = [t for t in tiles if boxes_meet(bbox(t), box)]
    for _ in range(depth):
        cur = [c for t in cur for c in A.cut(t) if boxes_meet(bbox(c), box)]
    return set(cur)


class Climber:
    def __init__(self, keys):
        self.keys = list(keys)
        self.phi = {k: A.phi(k) for k in self.keys}
        self.inv = defaultdict(list)
        for k, kids in self.phi.items():
            for c, ck in enumerate(kids):
                self.inv[ck].append((k, c))

    def embed(self, tiles, seed_key, max_level=8):
        """(found, level, chains tried). tiles: the patch in the seed's frame (the seed is BASE)."""
        tiles = list(tiles)
        tset = set(tiles)
        box = (min(bbox(t)[0] for t in tiles), min(bbox(t)[1] for t in tiles),
               max(bbox(t)[2] for t in tiles), max(bbox(t)[3] for t in tiles))
        tried = 0
        frontier = [(E.BASE, seed_key)]
        for level in range(1, max_level + 1):
            nxt = []
            for a, k in frontier:
                for K1, c in self.inv.get(k, ()):
                    tried += 1
                    a1 = parent_of(a, c)
                    if A.orient(a1) != K1[0]:
                        continue
                    collar = [E.tile_in(a1, x) for x in K1[1]]
                    desc = descendants_in_box(collar, level, box)
                    inside = [t for t in tiles if any(E.interiors_meet(t, q) for q in collar
                                                      if boxes_meet(bbox(t), bbox(q)))]
                    if any(t not in desc for t in inside):
                        continue
                    if len(inside) == len(tiles):
                        return True, level, tried
                    nxt.append((a1, K1))
            frontier = list({(a, k) for a, k in nxt})
            if not frontier:
                return False, level, tried
        return False, max_level, tried
