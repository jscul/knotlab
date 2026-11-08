#!/usr/bin/env python3
"""Check for COLLAR-PLANE-20261108-001A-P001: a periodic plane obeys every undecorated local law of the pinwheel.

    python3 -B check.py        (about two minutes; writes result.json)

Exact rational arithmetic throughout, with PINWHEEL-ATLAS-20261107-001A's atlas_lib (Conway's cut, collars, keys, planar maps and
rooted codes) and its atlas.json (the 1,168 radius-2 codes).
- The law: the closure of collar keys (193) and its complete keys (108).
- Lemma 1: the cut maps every complete key to five complete keys, so the cut of a collar-legal plane is collar-legal.
- The witness: the rhombus lattice R (the four tiles around a common right angle form a rhombus with diagonals 2 and 4; its
  translates by the lattice Z(1, 2) + Z(1, -2) tile the plane). R_k is its k-fold cut. One fundamental domain of R_k is the k-fold
  cut of the central rhombus, so testing those 4 * 5^k tiles tests every tile of the periodic plane.
  - R_1 and R_2: every collar is a complete key (computed twice: with a spatial hash and by brute force).
  - R_2: every interior dart's radius-2 code is in the atlas.
- The width w: the least distance from a complete key's central tile to the outside of the collar's union, and k(r), the number of
  cuts after which every patch of tile radius r of the cut of a collar-legal plane lies inside the cut of one collar.
- Controls, each of which must fail: R uncut; the rectangle lattice cut once and twice; R_1 against the radius-2 atlas; R_1 with one
  rectangle flipped to its other diagonal."""
from __future__ import annotations

import json
import math
import sys
import time
from collections import defaultdict
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ATLAS_DIR = ROOT / "proofs/PINWHEEL-ATLAS-20261107-001A/PINWHEEL-ATLAS-20261107-001A-P001_the_complete_radius_2_atlas"
sys.path.insert(0, str(ATLAS_DIR))
import atlas_lib as A  # noqa: E402

BASE = A.BASE


def law():
    keys = A.closure()
    complete = {k for k in keys if A.complete(k)}
    return keys, complete


def fr(t):
    return tuple((Fr(p[0]), Fr(p[1])) for p in t)


def cut_k(tiles, k):
    for _ in range(k):
        tiles = [c for t in tiles for c in A.cut(t)]
    return tiles


def key_of(t, touching):
    return (A.orient(t), frozenset(tuple(A.to_frame(t, X) for X in u) for u in touching | {t}))


class Hash:
    def __init__(self, tiles):
        self.size = max(max(abs(t[i][j] - t[(i + 1) % 3][j]) for i in range(3) for j in range(2)) for t in tiles)
        self.cells = defaultdict(list)
        for t in tiles:
            for c in self.cells_of(t):
                self.cells[c].append(t)

    def cells_of(self, t):
        s = self.size
        xs = [p[0] for p in t]
        ys = [p[1] for p in t]
        for i in range(math.floor(min(xs) / s), math.floor(max(xs) / s) + 1):
            for j in range(math.floor(min(ys) / s), math.floor(max(ys) / s) + 1):
                yield (i, j)

    def touching(self, t):
        out = set()
        for c in self.cells_of(t):
            for u in self.cells.get(c, ()):
                if u != t and A.touch(t, u):
                    out.add(u)
        return out


def collar_test(plane, reps, complete, brute=False):
    """(tested, not a complete key, distinct keys used) over the representative tiles"""
    H = None if brute else Hash(plane)
    bad = 0
    used = set()
    for t in reps:
        tt = {u for u in plane if u != t and A.touch(t, u)} if brute else H.touching(t)
        K = key_of(t, tt)
        used.add(K)
        if K not in complete:
            bad += 1
    return len(reps), bad, len(used)


# ---- the planes -------------------------------------------------------------------------------------------------------------------
RHOMBUS = [((0, 0), (0, 2), (1, 0)), ((0, 0), (0, 2), (-1, 0)), ((0, 0), (0, -2), (1, 0)), ((0, 0), (0, -2), (-1, 0))]
LATTICE_R = ((1, 2), (1, -2))
RECTANGLE = [((0, 0), (0, 2), (1, 0)), ((1, 2), (1, 0), (0, 2))]     # a tile and its half-turn across the hypotenuse
LATTICE_Q = ((1, 0), (0, 2))


def lattice_plane(cell, basis, radius):
    (a, b), (c, d) = basis
    out = []
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            vx, vy = i * a + j * c, i * b + j * d
            out += [tuple((Fr(p[0] + vx), Fr(p[1] + vy)) for p in t) for t in cell]
    return out


def flip_rectangle(plane, near):
    """replace the first half-turn rectangle (two tiles sharing their hypotenuse) that meets `near` by its other diagonal"""
    byhyp = defaultdict(list)
    for t in plane:
        byhyp[frozenset((t[1], t[2]))].append(t)
    near = set(near)
    for h in sorted(byhyp, key=lambda h: sorted(h)):
        ts = byhyp[h]
        if len(ts) != 2 or not (ts[0] in near or ts[1] in near):
            continue
        a, b = sorted(ts)
        if (a[0][0] + b[0][0], a[0][1] + b[0][1]) != (a[1][0] + a[2][0], a[1][1] + a[2][1]):
            continue                                   # a kite, not a rectangle
        Oa, Pa, Qa = a
        Ob = b[0]
        new = [(Qa, Ob, Oa), (Pa, Oa, Ob)]             # right angles at the other two corners
        assert all(A.orient(t) != 0 for t in new)
        return [t for t in plane if t not in (a, b)] + new, new
    raise AssertionError("no rectangle found")


# ---- the radius-2 atlas -------------------------------------------------------------------------------------------------------------
def atlas_codes():
    data = json.loads((ATLAS_DIR / "atlas.json").read_text())
    return {tuple((d, tuple(r)) for d, r in code) for code, _ in data["atlas"]}


def dart_test(tiles, codes, r=2):
    M = A.build_map(A.integerize(tiles), 1)
    db = A.bfs_dist(M["rot"], list(M["boundary"]))
    tested = bad = 0
    for (u, v) in M["dlab"]:
        if db.get(u, 0) <= r + 1 or db.get(v, 0) <= r + 1:
            continue
        tested += 1
        if A.code(M["rot"], u, v, r) not in codes:
            bad += 1
    return tested, bad


# ---- the width of a collar ----------------------------------------------------------------------------------------------------------
def euclid(X):
    return (float(X[0]), 2.0 * float(X[1]))          # a tile's frame: short leg 1 along x, long leg 2 along y


def seg_dist(p, q, a, b):
    def pt_seg(x, a, b):
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        s = max(0.0, min(1.0, ((x[0] - ax) * dx + (x[1] - ay) * dy) / L2))
        return math.hypot(x[0] - ax - s * dx, x[1] - ay - s * dy)
    return min(pt_seg(p, a, b), pt_seg(q, a, b), pt_seg(a, p, q), pt_seg(b, p, q))


def collar_width(key):
    """least Euclidean distance from the central tile to the boundary of the union of the collar's tiles (assumed to be a
    neighbourhood of it); pieces of tile sides between consecutive collar vertices on one side of exactly one tile are boundary"""
    tiles = list(key[1])
    verts = {p for t in tiles for p in t}
    count = defaultdict(int)
    for t in tiles:
        for a, b in A.sides(t):
            on = sorted([p for p in verts if A.on_seg(p, a, b)], key=lambda p: (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2)
            for p, q in zip(on, on[1:]):
                count[frozenset((p, q))] += 1
    boundary = [tuple(s) for s, c in count.items() if c == 1]
    best = float("inf")
    for a, b in A.sides(BASE):
        for p, q in boundary:
            best = min(best, seg_dist(euclid(p), euclid(q), euclid(a), euclid(b)))
    return best


def main():
    t0 = time.time()
    res = {"checks": {}, "controls": {}, "census": {}}
    keys, complete = law()
    res["census"]["collar keys"] = len(keys)
    res["census"]["complete keys"] = len(complete)
    res["checks"]["law has 193 keys, 108 complete"] = len(keys) == 193 and len(complete) == 108

    # Lemma 1: the cut maps complete keys to complete keys
    images_ok = all(all(c in complete for c in A.phi(K)) for K in complete)
    res["checks"]["the cut maps every complete key to five complete keys"] = images_ok

    # the witness
    plane = lattice_plane(RHOMBUS, LATTICE_R, 3)
    centre = [fr(t) for t in RHOMBUS]
    for k in (1, 2):
        Pk = cut_k(plane, k)
        reps = cut_k(centre, k)
        n, bad, used = collar_test(Pk, reps, complete)
        res["census"][f"R_{k}: fundamental-domain tiles, non-key collars, distinct keys"] = [n, bad, used]
        res["checks"][f"R_{k}: every collar is a complete pinwheel collar (hash)"] = n == 4 * 5 ** k and bad == 0
        if k == 1:
            n2, bad2, _ = collar_test(Pk, reps, complete, brute=True)
            res["checks"]["R_1: every collar is a complete pinwheel collar (brute force)"] = n2 == 20 and bad2 == 0
    # periodicity of R_k: translating the patch by the lattice maps tiles to tiles (on the central part)
    P1 = cut_k(plane, 1)
    S1 = set(P1)
    reps1 = cut_k(centre, 1)
    per = all(tuple((p[0] + v[0], p[1] + v[1]) for p in t) in S1 for t in reps1 for v in LATTICE_R)
    res["checks"]["R_1 is invariant under the lattice Z(1, 2) + Z(1, -2)"] = per

    # R_2 against the radius-2 atlas
    codes = atlas_codes()
    res["census"]["atlas codes"] = len(codes)
    tested, bad = dart_test(cut_k(lattice_plane(RHOMBUS, LATTICE_R, 2), 2), codes)
    res["census"]["R_2: interior darts tested, outside the radius-2 atlas"] = [tested, bad]
    res["checks"]["R_2: every interior dart's radius-2 code is in the atlas"] = tested > 0 and bad == 0

    # the width and k(r)
    widths = [collar_width(K) for K in complete]
    w = min(widths)
    res["census"]["least collar width w (tile legs 1 and 2)"] = round(w, 6)
    res["checks"]["every complete collar has positive width"] = w > 0
    diam = math.sqrt(5)
    res["census"]["k(r): cuts after which every tile-radius-r patch lies in the cut of one collar"] = {
        r: next(k for k in range(60) if (r + 1) * diam * 5 ** (-k / 2) < w) for r in (1, 2, 3, 5, 10, 100)}

    # controls
    n, bad, _ = collar_test(plane, [fr(t) for t in RHOMBUS], complete)
    res["controls"]["R uncut has a non-key collar"] = bad > 0
    qplane = lattice_plane(RECTANGLE, LATTICE_Q, 3)
    for k in (1, 2):
        n, bad, _ = collar_test(cut_k(qplane, k), cut_k([fr(t) for t in RECTANGLE], k), complete)
        res["controls"][f"rectangle lattice cut {k} time(s) has a non-key collar"] = bad > 0
    tested, bad = dart_test(cut_k(lattice_plane(RHOMBUS, LATTICE_R, 2), 1), codes)
    res["census"]["R_1: interior darts tested, outside the radius-2 atlas"] = [tested, bad]
    res["controls"]["R_1 breaks the radius-2 atlas"] = bad > 0
    # one half-turn rectangle of R_1 flipped to its other diagonal (still a tiling), everything else unchanged
    flipped, new = flip_rectangle(P1, reps1)
    near = set(new) | {u for u in flipped if any(A.touch(u, x) for x in new)}
    n, bad, _ = collar_test(flipped, sorted(near), complete)
    res["census"]["R_1 with one rectangle flipped: tiles tested, non-key collars"] = [n, bad]
    res["controls"]["R_1 with one rectangle flipped has a non-key collar"] = bad > 0

    res["status"] = "passed" if all(res["checks"].values()) and all(res["controls"].values()) else "failed"
    res["failures"] = [k for k, v in {**res["checks"], **res["controls"]}.items() if not v]
    res["runtime_seconds"] = round(time.time() - t0, 1)
    (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
