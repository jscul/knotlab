"""Decorated substitutions of the pinwheel and periodic planes, through the skeleton of Conway's cut on collars
(ROUND-PRICE-20261108-001A-P001).

A decorated substitution on labels {0, 1} is a pair s = (s(0), s(1)) of 5-tuples: a tile with label a gives its child i the label
s(a)_i (children numbered as in PINWHEEL-ATLAS-20261107-001A's atlas_lib.cut). Its law is the set of complete labelled collars
reachable from one labelled tile of either handedness under the labelled cut. A periodic plane is given by the tiles of one cell and
a lattice; its descendants are (cell tile, lattice translation, path of child indices), and the collar of each descendant is found
from the collars of the cell's tiles through the cut, so no coordinates are needed beyond the first level."""
from __future__ import annotations

import itertools
import sys
from collections import deque
from fractions import Fraction as Fr
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/PINWHEEL-ATLAS-20261107-001A/PINWHEEL-ATLAS-20261107-001A-P001_the_complete_radius_2_atlas"))
import atlas_lib as A  # noqa: E402

BASE = A.BASE


def canon(tiles):
    return sorted(tiles)


def images(h, tiles):
    """the five children of the central tile of the collar (h, tiles): their collars (h', canonical tiles) with, for each tile of a
    child's collar, the (collar tile, child index) it comes from"""
    kids = [(c, j, m) for j, t in enumerate(tiles) for m, c in enumerate(A.cut(t))]
    out = []
    for c in A.cut(BASE):
        col = [(tuple(A.to_frame(c, X) for X in k), j, m) for k, j, m in kids if k == c or A.touch(c, k)]
        img = canon([x for x, _, _ in col])
        pos = {x: n for n, x in enumerate(img)}
        src = [None] * len(img)
        for x, j, m in col:
            src[pos[x]] = (j, m)
        out.append(((h * A.orient(c), tuple(img)), tuple(src)))
    return out


class Skeleton:
    """collar types (keys and any other collar met in a plane's cuts), indexed, with their images under the cut"""

    def __init__(self):
        keys = set(A.closure((1, frozenset([BASE])))) | set(A.closure((-1, frozenset([BASE]))))
        self.types = []
        self.index = {}
        for k in sorted(keys, key=lambda k: (k[0], sorted(k[1]))):
            self.add((k[0], tuple(canon(k[1]))))
        self.n_keys = len(self.types)
        self.complete = [A.complete((h, frozenset(t))) for h, t in self.types]
        self.seeds = [self.index[(1, (BASE,))], self.index[(-1, (BASE,))]]
        self._phi = {}

    def add(self, typ):
        if typ not in self.index:
            self.index[typ] = len(self.types)
            self.types.append(typ)
        return self.index[typ]

    def phi(self, n):
        if n not in self._phi:
            h, tiles = self.types[n]
            self._phi[n] = [(self.add(t), src) for t, src in images(h, list(tiles))]
            while len(self.complete) < len(self.types):
                h2, t2 = self.types[len(self.complete)]
                self.complete.append(A.complete((h2, frozenset(t2))))
        return self._phi[n]


def law(sk, sig):
    """complete labelled keys (type index, labels in canonical tile order) of the decorated substitution sig"""
    seen, q = set(), deque()
    for s0 in sk.seeds:
        for a in range(len(sig)):
            seen.add((s0, (a,)))
            q.append((s0, (a,)))
    while q:
        n, lab = q.popleft()
        for n2, src in sk.phi(n):
            s2 = (n2, tuple(sig[lab[j]][m] for j, m in src))
            if s2 not in seen:
                seen.add(s2)
                q.append(s2)
    out = {}
    for n, lab in seen:
        if n < sk.n_keys and sk.complete[n]:
            out.setdefault(n, []).append(lab)
    return {n: sorted(v) for n, v in out.items()}


class Plane:
    """a periodic tiling: cell tiles (exact) and a lattice basis; collars of cell tiles as (cell tile, i, j) positions"""

    def __init__(self, sk, cell, lattice, radius=3):
        self.sk = sk
        self.cell = [tuple((Fr(p[0]), Fr(p[1])) for p in t) for t in cell]
        (a, b), (c, d) = lattice
        self.lattice = lattice
        det = a * d - b * c
        tiles = [tuple((p[0] + i * a + j * c, p[1] + i * b + j * d) for p in t)
                 for i in range(-radius, radius + 1) for j in range(-radius, radius + 1) for t in self.cell]

        def decompose(u):
            for s, t in enumerate(self.cell):
                vx, vy = u[0][0] - t[0][0], u[0][1] - t[0][1]
                if all((u[k][0] - t[k][0], u[k][1] - t[k][1]) == (vx, vy) for k in range(3)):
                    i = (vx * d - vy * c) / det
                    j = (vy * a - vx * b) / det
                    if i.denominator == 1 and j.denominator == 1:
                        return s, int(i), int(j)
            raise ValueError("not a lattice translate of a cell tile")
        self.root = []
        for t in self.cell:
            col = [u for u in tiles if u == t or A.touch(t, u)]
            framed = {tuple(A.to_frame(t, p) for p in u): u for u in col}
            typ = (A.orient(t), tuple(canon(list(framed))))
            n = sk.add(typ)
            self.root.append((n, tuple(decompose(framed[x]) for x in typ[1])))

    @lru_cache(maxsize=None)
    def tile(self, s, path):
        """type index of the descendant (cell tile s, translation 0, path) and its collar as (cell tile, di, dj, path)"""
        if not path:
            n, coll = self.root[s]
            return n, tuple((s2, di, dj, ()) for s2, di, dj in coll)
        n0, coll0 = self.tile(s, path[:-1])
        n, src = self.sk.phi(n0)[path[-1]]
        return n, tuple(coll0[j][:3] + (coll0[j][3] + (m,),) for j, m in src)

    def descendants(self, k):
        return [(s, p) for s in range(len(self.cell)) for p in itertools.product(range(5), repeat=k)]


def sublattices(m):
    """Hermite normal forms (a, c, d), a d = m, 0 <= c < a: the sublattice spanned by (a, 0) and (c, d) in lattice coordinates"""
    return [(a, c, m // a) for a in range(1, m + 1) if m % a == 0 for c in range(a)]


def reduce(i, j, L):
    a, c, d = L
    q = j // d
    return (i - q * c) % a, j - q * d


def constraints(plane, allowed, k, cells):
    """(literal tuple, allowed label tuples) for the descendants at depth k of the listed (s, i, j) cells; positions are keyed by
    (s, i, j, path)"""
    out = []
    for (s, path) in plane.descendants(k):
        n, coll = plane.tile(s, path)
        for (s0, i, j) in cells:
            if s0 != s:
                continue
            out.append(([(s2, i + di, j + dj, p) for s2, di, dj, p in coll], allowed.get(n, [])))
    return out


def solve(cons, keyfun, want_model=False):
    from pysat.solvers import Cadical153
    var = {}
    S = Cadical153()
    rows = []
    for lits, allowed in cons:
        if not allowed:
            S.delete()
            return (False, None) if want_model else False
        rows.append(([var.setdefault(keyfun(x), len(var) + 1) for x in lits], allowed))
    top = len(var)
    for vs, allowed in rows:
        ys = []
        for tup in allowed:
            top += 1
            ys.append(top)
            for v, b in zip(vs, tup):
                S.add_clause([-top, v if b else -v])
        S.add_clause(ys)
    ok = S.solve()
    model = None
    if ok and want_model:
        m = set(x for x in S.get_model() if x > 0)
        model = {key: (v in m) for key, v in var.items()}
    S.delete()
    return (ok, model) if want_model else ok


def periodic(plane, allowed, k, L, want_model=False):
    a, c, d = L
    cells = [(s, i, j) for s in range(len(plane.cell)) for i in range(a) for j in range(d)]
    cons = constraints(plane, allowed, k, cells)
    return solve(cons, lambda x: (x[0],) + reduce(x[1], x[2], L) + (x[3],), want_model)


def boxed(plane, allowed, k, B):
    cells = [(s, i, j) for s in range(len(plane.cell)) for i in range(-B + 1, B) for j in range(-B + 1, B)]
    return solve(constraints(plane, allowed, k, cells), lambda x: x)


RHOMBUS = [((0, 0), (0, 2), (1, 0)), ((0, 0), (0, 2), (-1, 0)), ((0, 0), (0, -2), (1, 0)), ((0, 0), (0, -2), (-1, 0))]
RHOMBUS_LATTICE = ((1, 2), (1, -2))
