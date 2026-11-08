"""Periodic parent tilings from a labelled collar law (CRYSTAL-UP-20261108-001A-E001).

Reuses LAST-BIT-20261108-001B's forcing_lib (its LabelledPatch, a labelled version of GROWTH-LAW-20261107-001B's growth engine).
Everything is written in the seed tile's affine frame (O at 0, Q at (1, 0), P at (0, 1)), where every tile congruent to the seed has
frame area 1/2, so a lattice of frame determinant d carries 2|d| tiles per period.

- grow_patch: exhaustive extension of a labelled collar to a tile distance, returning the patch (as forcing_lib.extends, which only
  says whether one exists).
- vectors: translation vectors between two complete tiles of a patch with the same shape, label and labelled collar. A period of a
  tiling containing the patch maps such tiles to each other, so periods are looked for among them.
- TorusPatch: growth on the torus of a lattice. Every tile is an orbit, stored by one canonical image (centroid in the fundamental
  parallelogram) and its translates by small lattice vectors (a window wide enough that every canonical image's collar, and every
  tile a move adds around it, sits inside). Collars, consistency and moves are those of LabelledPatch, read at canonical images.
- torus_grow: depth-first completion of every orbit's collar from a seed collar, with backtracking and a step budget. A completed
  torus is a periodic tiling all of whose labelled collars lie in the law."""
from __future__ import annotations

import importlib.util
import itertools
import math
import sys
from collections import defaultdict
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


F = _load("last_bit_b_forcing_lib", ROOT / "proofs/LAST-BIT-20261108-001B/LAST-BIT-20261108-001B-P001_geometry_alone/forcing_lib.py")
GE, A, D = F.GE, F.A, F.D
BASE = F.BASE
SIG = ((1, 0, 1, 0, 1), (0, 0, 1, 1, 0))


def light_setup():
    """the skeleton and the core, without the pair tables (not needed here)"""
    F.G["sk"] = D.Skeleton()
    core = F.RB.load_core()
    F.G["core"] = core
    F.G["sets"] = [Y for Y, _ in core]
    F.G["kids"] = {yi: [(F.G["sk"].index.get(t), src) for t, src in D.images(1, list(Y))] for yi, Y in enumerate(F.G["sets"])}


def survivor_law(survivors):
    """S1*: the labelled level-one collars surviving LAST-BIT-20261108-001B (its survivors.json plus the labelled keys of L(s) that
    are core collars), as {(core index, labels)}; and the split (in L(s), keys outside, non-keys)"""
    L = F.law_as_sets(SIG)
    sk, core = F.G["sk"], F.G["core"]
    inL = [(yi, p) for yi, (Y, iskey) in enumerate(core) if iskey for p in sorted(L.get(sk.index[(1, Y)], ()))]
    ko = [(yi, tuple(p)) for yi, p in survivors["keys outside L(s)"]]
    nk = [(yi, tuple(p)) for yi, p in survivors["non-keys"]]
    return L, inL, ko, nk


def keys_by_h(items):
    out = {1: [], -1: []}
    for yi, p in items:
        it = frozenset(zip(F.G["sets"][yi], p))
        out[1].append((1, it))
        out[-1].append((-1, it))
    return out


def start_patch(kbh, start_key, cls=None, **kw):
    h, items = start_key
    lab = dict(items)[BASE]
    cls = cls or F.LabelledPatch
    P = cls(kbh, BASE, lab, **kw)
    for x, l in items:
        if x != BASE:
            if P.overlaps(x):
                return None
            P.add_l(x, l)
    return P


def grow_patch(kbh, start_key, depth, budget, rng=None):
    """as forcing_lib.extends, but returns the patch (or None); rng shuffles the order in which moves are tried"""
    P = start_patch(kbh, start_key)
    if P is None or not all(P.consistent(i) for i in range(len(P.tiles))):
        return None
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
        lm = list(lm)
        if rng is not None:
            rng.shuffle(lm)
        for k in lm:
            n0 = len(P.tiles)
            if P.try_move(i, k, keep=True) == 0:
                continue
            r = dfs()
            if r is True:
                return True
            while len(P.tiles) > n0:
                P.pop()
            if r is None:
                return None
        return False
    return P if dfs() is True else None


def shape(t):
    O, P, Q = t
    return ((P[0] - O[0], P[1] - O[1]), (Q[0] - O[0], Q[1] - O[1]))


def vectors(P, same_collar=True, max_len2=None):
    """translation vectors (frame coordinates) between tiles with equal shape and label; with same_collar, only between complete
    tiles with equal labelled collars as well"""
    groups = defaultdict(list)
    for i, t in enumerate(P.tiles):
        if same_collar:
            if P.is_complete(i):
                groups[(shape(t), P.labels[t], P.collar(i))].append(t[0])
        else:
            groups[(shape(t), P.labels[t])].append(t[0])
    out = set()
    for pts in groups.values():
        for a, b in itertools.combinations(pts, 2):
            v = (b[0] - a[0], b[1] - a[1])
            if v < (0, 0):
                v = (-v[0], -v[1])
            if max_len2 is None or norm2(v) <= max_len2:
                out.add(v)
    return out


def euclid(v):
    """frame -> Euclidean coordinates (seed tile: short leg (1, 0), long leg (0, 2))"""
    return (v[0], 2 * v[1])


def norm2(v):
    x, y = euclid(v)
    return x * x + y * y


def det(u, v):
    return u[0] * v[1] - u[1] * v[0]


def reduce_basis(u, v):
    """Lagrange-Gauss reduction in the Euclidean metric; a canonical sign"""
    def dot(a, b):
        ea, eb = euclid(a), euclid(b)
        return ea[0] * eb[0] + ea[1] * eb[1]
    while True:
        if norm2(u) > norm2(v):
            u, v = v, u
        q = dot(u, v) / norm2(u)
        m = math.floor(q + Fr(1, 2))
        if m == 0:
            break
        v = (v[0] - m * u[0], v[1] - m * u[1])
        if norm2(v) >= norm2(u):
            break
    if norm2(u) > norm2(v):
        u, v = v, u
    if det(u, v) < 0:
        v = (-v[0], -v[1])
    return u, v


def lattice_key(u, v):
    """a canonical key for the lattice spanned by u, v: its Hermite normal form over the rationals"""
    # write as integer matrix after clearing denominators
    den = math.lcm(*[x.denominator for x in (*u, *v)])
    a = [[int(u[0] * den), int(u[1] * den)], [int(v[0] * den), int(v[1] * den)]]
    # row HNF of the 2x2 integer matrix (rows generate the lattice)
    g, x, y = _egcd(a[0][0], a[1][0])
    if g == 0:
        r1 = a[0] if a[0][1] != 0 else a[1]
        h = (0, abs(r1[1]), 0)
        return (den,) + h
    r1 = [x * a[0][0] + y * a[1][0], x * a[0][1] + y * a[1][1]]
    r2 = [(a[1][0] // g) * a[0][0] - (a[0][0] // g) * a[1][0], (a[1][0] // g) * a[0][1] - (a[0][0] // g) * a[1][1]]
    if r1[0] < 0:
        r1 = [-r1[0], -r1[1]]
    d = abs(r2[1])
    c = r1[1] % d if d else r1[1]
    return (den, r1[0], c, d)


def _egcd(a, b):
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    g, x, y = _egcd(b, a % b)
    return (g, y, x - (a // b) * y)


def lattices(vecs, nmax):
    """distinct lattices spanned by two of the vectors with at most nmax tiles per period, smallest first"""
    vecs = sorted(vecs, key=norm2)
    seen = {}
    for u, v in itertools.combinations(vecs, 2):
        d = det(u, v)
        if d == 0:
            continue
        n = 2 * abs(d)
        if n.denominator != 1 or n > nmax:
            continue
        b = reduce_basis(u, v)
        k = lattice_key(*b)
        if k not in seen:
            seen[k] = (int(n), b)
    return sorted(seen.values(), key=lambda x: (x[0], norm2(x[1][0]) + norm2(x[1][1])))


class TorusPatch(F.LabelledPatch):
    """LabelledPatch on the torus of the lattice (e1, e2): tiles are added and removed by orbit"""

    def __init__(self, kbh, seed, seed_label, lattice, margin=7.5):
        self.e1, self.e2 = lattice
        self.det = det(self.e1, self.e2)
        # window: enough translates to cover every point within `margin` (Euclidean units; a tile's diameter is sqrt 5) of the
        # fundamental parallelogram; three diameters cover a canonical image's collar, the tiles a move adds and what they overlap
        area = 2 * abs(float(self.det))
        h1 = area / math.sqrt(norm2(self.e2))
        h2 = area / math.sqrt(norm2(self.e1))
        self.R = max(1, math.ceil(margin / min(h1, h2)))
        self.offsets = sorted(itertools.product(range(-self.R, self.R + 1), repeat=2), key=lambda ij: abs(ij[0]) + abs(ij[1]))
        self.orbit_imgs = []      # per orbit: list of image indices (first = canonical)
        self.orbit_of = {}        # image tile -> orbit id
        super().__init__(kbh, seed, seed_label)

    def coords(self, p):
        a = det(p, self.e2) / self.det
        b = det(self.e1, p) / self.det
        return a, b

    def canonical(self, t):
        cx = (t[0][0] + t[1][0] + t[2][0]) / 3
        cy = (t[0][1] + t[1][1] + t[2][1]) / 3
        a, b = self.coords((cx, cy))
        i, j = math.floor(a), math.floor(b)
        return self.shift(t, -i, -j)

    def shift(self, t, i, j):
        vx = i * self.e1[0] + j * self.e2[0]
        vy = i * self.e1[1] + j * self.e2[1]
        return tuple((p[0] + vx, p[1] + vy) for p in t)

    def add_l(self, t, label):
        """add the whole orbit of t; returns the index of the canonical image"""
        g0 = self.canonical(t)
        oid = len(self.orbit_imgs)
        idx = []
        for i, j in self.offsets:
            g = self.shift(g0, i, j)
            self.labels[g] = label
            idx.append(GE.Patch.add(self, g))
            self.orbit_of[g] = oid
        self.orbit_imgs.append(idx)
        return idx[0]

    def pop(self):
        """remove the last orbit"""
        idx = self.orbit_imgs.pop()
        for _ in idx:
            t = self.tiles[-1]
            GE.Patch.pop(self)
            del self.labels[t]
            del self.orbit_of[t]

    def n_orbits(self):
        return len(self.orbit_imgs)

    def canon_of(self, i):
        return self.orbit_imgs[self.orbit_of[self.tiles[i]]][0]

    def try_move(self, i, key, keep=False):
        new = self.realizable(i, key)
        if new is None:
            return 0
        n0 = self.n_orbits()
        ok = True
        for g, lab in new:
            if g in self.index:
                if self.labels[g] != lab:
                    ok = False
                    break
                continue
            if self.overlaps(g):
                ok = False
                break
            self.add_l(g, lab)
        added = self.n_orbits() - n0
        if ok:
            affected = set()
            for o in range(n0, self.n_orbits()):
                for k in self.orbit_imgs[o]:
                    affected.add(self.orbit_of[self.tiles[k]])
                    for j in self.touch[k]:
                        affected.add(self.orbit_of[self.tiles[j]])
            ok = all(self.consistent(self.orbit_imgs[o][0]) for o in affected)
        if not ok or not keep:
            for _ in range(added):
                self.pop()
            return 0 if not ok else max(added, 1)
        return max(added, 1)

    def incomplete_orbits(self):
        return [o for o in range(self.n_orbits()) if not self.is_complete(self.orbit_imgs[o][0])]

    def cell_tiles(self):
        return [(self.tiles[idx[0]], self.labels[self.tiles[idx[0]]]) for idx in self.orbit_imgs]


def torus_grow(kbh, start_key, lattice, budget, nmax_orbits):
    """complete every orbit's collar on the torus of `lattice` from the seed collar. Returns ('torus', cell) / ('none', steps) /
    ('budget', steps) / ('invalid', reason)"""
    h, items = start_key
    lab = dict(items)[BASE]
    P = TorusPatch(kbh, BASE, lab, lattice)
    for x, l in items:
        if x == BASE:
            continue
        if x in P.index:
            if P.labels[x] != l:
                return ("invalid", "seed collar meets its own translate with another label"), P
            continue
        if P.overlaps(x):
            return ("invalid", "seed collar overlaps its own translate"), P
        P.add_l(x, l)
    if not all(P.consistent(P.orbit_imgs[o][0]) for o in range(P.n_orbits())):
        return ("invalid", "seed collar inconsistent on this torus"), P
    steps = [0]

    def dfs():
        steps[0] += 1
        if steps[0] > budget:
            return None
        if P.n_orbits() > nmax_orbits:
            return False
        inc = P.incomplete_orbits()
        if not inc:
            return True
        best = None
        for o in inc:
            lm = P.legal_moves(P.orbit_imgs[o][0])
            if best is None or len(lm) < len(best[1]):
                best = (o, lm)
                if len(lm) <= 1:
                    break
        o, lm = best
        i = P.orbit_imgs[o][0]
        for k in lm:
            n0 = P.n_orbits()
            if P.try_move(i, k, keep=True) == 0:
                continue
            r = dfs()
            if r is True:
                return True
            while P.n_orbits() > n0:
                P.pop()
            if r is None:
                return None
        return False
    r = dfs()
    if r is True:
        return ("torus", P.cell_tiles()), P
    return (("budget" if r is None else "none"), steps[0]), P
