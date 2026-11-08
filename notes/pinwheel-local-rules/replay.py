#!/usr/bin/env python3
"""Independent replay for the note "The pinwheel tilings have no undecorated local rules".

    python3 replay.py

Self-contained (standard library only, exact rational arithmetic). It rebuilds the collars of the pinwheel from one triangle by
Conway's cut, decides which are complete by an angle count (not by the sector test of the original computation), and checks:
  1. the collars close up: 193 in all, 108 complete, and the cut sends every complete collar to five complete ones;
  2. the rhombus lattice cut once has every collar complete and pinwheel (20 tiles per period), and cut twice (100 tiles);
  3. the rhombus lattice itself, and the rectangle lattice cut once, do not (controls).
Prints one line per check and exits with 1 on a failure."""
from fractions import Fraction as F
from collections import deque
import sys

O0 = (F(0), F(0))
BASE = (O0, (F(0), F(1)), (F(1), F(0)))        # a tile is (O, P, Q): right angle, end of the long leg, end of the short leg


def lin(a, b, wa, wb):
    return (a[0] * wa + b[0] * wb, a[1] * wa + b[1] * wb)


def cut(t):
    O, P, Q = t
    H = lin(Q, P, F(4, 5), F(1, 5))
    M = lin(O, P, F(1, 2), F(1, 2))
    F1 = lin(O, H, F(1, 2), F(1, 2))
    F2 = lin(H, P, F(1, 2), F(1, 2))
    return [(H, O, Q), (F1, M, O), (F1, M, H), (F2, H, M), (F2, P, M)]


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def on_segment(p, a, b):
    return cross(a, b, p) == 0 and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])


def sides(t):
    O, P, Q = t
    return ((O, Q), (O, P), (Q, P))


def touch(s, t):
    return any(on_segment(p, a, b) for p in s for a, b in sides(t)) or any(on_segment(p, a, b) for p in t for a, b in sides(s))


def frame(c, x):
    O, P, Q = c
    e1 = (Q[0] - O[0], Q[1] - O[1])
    e2 = (P[0] - O[0], P[1] - O[1])
    det = e1[0] * e2[1] - e1[1] * e2[0]
    dx, dy = x[0] - O[0], x[1] - O[1]
    return ((dx * e2[1] - dy * e2[0]) / det, (e1[0] * dy - e1[1] * dx) / det)


def hand(t):
    O, P, Q = t
    return 1 if cross(O, Q, P) > 0 else -1


def key(h, c, tiles):
    return (h, frozenset(tuple(frame(c, x) for x in t) for t in tiles))


def images(k):
    h, tiles = k
    kids = [c for t in tiles for c in cut(t)]
    return [key(h * hand(c), c, [d for d in kids if d == c or touch(c, d)]) for c in cut(BASE)]


def complete(k):
    """angle count: at each corner of the central tile and each collar vertex on its sides, the corners and straight angles of the
    collar's tiles must add up to a full turn. With a = arctan(1/2) (irrational in turns), corner O is a right angle, corner P is a,
    corner Q is a right angle minus a, and a point inside a side is a straight angle; a full turn needs as many P corners as Q
    corners and nO + nQ + 2 nE = 4."""
    _, tiles = k
    pts = set(BASE) | {p for t in tiles for p in t if any(on_segment(p, a, b) for a, b in sides(BASE))}
    for p in pts:
        nO = nP = nQ = nE = 0
        for t in tiles:
            O, P, Q = t
            if p == O:
                nO += 1
            elif p == P:
                nP += 1
            elif p == Q:
                nQ += 1
            elif any(on_segment(p, a, b) for a, b in sides(t)):
                nE += 1
        if nP != nQ or nO + nQ + 2 * nE != 4:
            return False
    return True


def closure():
    seed = (1, frozenset([BASE]))
    seen, q = {seed}, deque([seed])
    while q:
        for k2 in images(q.popleft()):
            if k2 not in seen:
                seen.add(k2)
                q.append(k2)
    return seen


def lattice(cell, basis, r):
    (a, b), (c, d) = basis
    return [tuple((F(p[0] + i * a + j * c), F(p[1] + i * b + j * d)) for p in t)
            for i in range(-r, r + 1) for j in range(-r, r + 1) for t in cell]


def cuts(tiles, k):
    for _ in range(k):
        tiles = [c for t in tiles for c in cut(t)]
    return tiles


def collar_ok(plane, reps, keys):
    bad = 0
    for t in reps:
        k = key(hand(t), t, [u for u in plane if u == t or touch(t, u)])
        bad += k not in keys
    return bad


def main():
    fails = 0

    def report(name, ok):
        nonlocal fails
        print(("PASS " if ok else "FAIL ") + name)
        fails += not ok
    keys = closure()
    comp = {k for k in keys if complete(k)}
    report(f"collars close up: {len(keys)} keys, {len(comp)} complete (expect 193, 108)", len(keys) == 193 and len(comp) == 108)
    report("the cut sends every complete collar to five complete ones", all(all(c in comp for c in images(k)) for k in comp))
    rh = [((0, 0), (0, 2), (1, 0)), ((0, 0), (0, 2), (-1, 0)), ((0, 0), (0, -2), (1, 0)), ((0, 0), (0, -2), (-1, 0))]
    basis = ((1, 2), (1, -2))
    centre = [tuple((F(x), F(y)) for x, y in t) for t in rh]
    plane = lattice(rh, basis, 2)
    for k, n in ((1, 20), (2, 100)):
        reps = cuts(centre, k)
        report(f"rhombus lattice cut {k} time(s): all {len(reps)} tiles of a period have pinwheel collars (expect {n})",
               len(reps) == n and collar_ok(cuts(plane, k), reps, comp) == 0)
    report("control: the rhombus lattice uncut has a collar that is not a pinwheel collar", collar_ok(plane, centre, comp) > 0)
    rect = [((0, 0), (0, 2), (1, 0)), ((1, 2), (1, 0), (0, 2))]
    rplane = lattice(rect, ((1, 0), (0, 2)), 2)
    rc = [tuple((F(x), F(y)) for x, y in t) for t in rect]
    report("control: the rectangle lattice cut once has a collar that is not a pinwheel collar",
           collar_ok(cuts(rplane, 1), cuts(rc, 1), comp) > 0)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
