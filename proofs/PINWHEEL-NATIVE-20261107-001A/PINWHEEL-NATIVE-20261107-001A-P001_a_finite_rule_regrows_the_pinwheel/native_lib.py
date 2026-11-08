"""The pinwheel law grown by a finite symbolic rule (ticket PINWHEEL-NATIVE-20261107-001A).

Geometric reference: Conway's pinwheel cut in exact integer coordinates (tiles (O, P, Q): right angle, end of the long leg, end of
the short leg). Symbolic rule: knots (tiles) with a handedness and three ordered sides of distinction ids (S: O->Q, L: O->P,
H: Q->P); distinctions with one or two incidences (tile, side, lo, hi), [lo, hi] their interval along that side as a fraction of
the side, and whether the two sides run the same way along them. No coordinates are used by the rule."""
from __future__ import annotations
import math
from collections import defaultdict
from fractions import Fraction as Fr

def split(tile, m):
    O, P, Q = tile
    d = 1 + m * m
    H = (Q[0] + (P[0] - Q[0]) // d, Q[1] + (P[1] - Q[1]) // d)
    out = [(H, O, Q)]                       # small copy: right angle at H, long leg to O, short leg to Q
    ex = ((P[0] - H[0]) // m, (P[1] - H[1]) // m)
    ey = ((O[0] - H[0]) // m, (O[1] - H[1]) // m)
    V = lambda i, j: (H[0] + i * ex[0] + j * ey[0], H[1] + i * ex[1] + j * ey[1])
    for i in range(m):
        for j in range(m - i):
            out.append((V(i, j), V(i + 1, j), V(i, j + 1)))
            if i + j <= m - 2:
                out.append((V(i + 1, j + 1), V(i, j + 1), V(i + 1, j)))
    return out

def split_pinwheel(tile):
    """Conway's pinwheel decomposition (legs 1:2): drop the altitude from the right angle; cut the larger piece along its median
    to the midpoint M of the long leg, and each of the two isosceles halves along its axis. Four copies meet at M; the two
    halves give mirror-image pairs. Needs coordinates divisible by 10."""
    O, P, Q = tile
    H = (Q[0] + (P[0] - Q[0]) // 5, Q[1] + (P[1] - Q[1]) // 5)
    M = ((O[0] + P[0]) // 2, (O[1] + P[1]) // 2)
    F1 = ((O[0] + H[0]) // 2, (O[1] + H[1]) // 2)
    F2 = ((H[0] + P[0]) // 2, (H[1] + P[1]) // 2)
    return [(H, O, Q), (F1, M, O), (F1, M, H), (F2, H, M), (F2, P, M)]

def tiling_rule(rule, k):
    """rule in {'pinwheel', 'consistent', 'isosceles'}: the pinwheel (Conway's cut), the same five copies cut frame-consistently
    (altitude, then midpoints), or the isosceles right triangle halved by its altitude."""
    if rule == "pinwheel":
        D, top, f = 10, ((0, 0), (2, 0), (0, 1)), split_pinwheel
    elif rule == "consistent":
        D, top, f = 10, ((0, 0), (2, 0), (0, 1)), lambda t: split(t, 2)
    elif rule == "isosceles":
        D, top, f = 2, ((0, 0), (1, 0), (0, 1)), lambda t: split(t, 1)
    else:
        raise ValueError(rule)
    tiles = [top]
    for _ in range(k):
        tiles = [tuple((x * D, y * D) for x, y in t) for t in tiles]
        tiles = [s for t in tiles for s in f(t)]
    ratio = math.sqrt(5) if rule != "isosceles" else math.sqrt(2)
    scale = D ** k / ratio ** k
    return tiles, scale

def handedness(t):
    (ox, oy), (px, py), (qx, qy) = t
    return 1 if (px - ox) * (qy - oy) - (py - oy) * (qx - ox) > 0 else -1


CUTS = {"S": (), "L": (Fr(1, 2),), "H": (Fr(1, 5), Fr(3, 5))}
# how each parent side is covered by child sides: (lo, hi, child index, child side, same direction?)
COVER = {"S": ((Fr(0), Fr(1), 0, "H", False),),
         "L": ((Fr(0), Fr(1, 2), 1, "H", True), (Fr(1, 2), Fr(1), 4, "H", True)),
         "H": ((Fr(0), Fr(1, 5), 0, "S", False), (Fr(1, 5), Fr(3, 5), 3, "L", False), (Fr(3, 5), Fr(1), 4, "L", True))}
HANDS = (-1, -1, 1, 1, -1)                       # child handedness relative to the parent's
INTERNAL = (((0, "L", Fr(0), Fr(1, 2)), (2, "S", Fr(0), Fr(1)), False),     # H-F1
            ((0, "L", Fr(1, 2), Fr(1)), (1, "S", Fr(0), Fr(1)), True),      # F1-O
            ((1, "L", Fr(0), Fr(1)), (2, "L", Fr(0), Fr(1)), True),         # F1-M
            ((2, "H", Fr(0), Fr(1)), (3, "H", Fr(0), Fr(1)), False),        # H-M
            ((3, "S", Fr(0), Fr(1)), (4, "S", Fr(0), Fr(1)), True))         # F2-M

def start():
    hands = [1]
    segs = [{"inc": [(0, s, Fr(0), Fr(1))], "aligned": None} for s in "SLH"]
    return hands, segs

def label(seg):
    """The distinction's label: its incidences without tile ids, and whether the sides run the same way."""
    d = tuple(sorted((s, lo, hi) for _, s, lo, hi in seg["inc"]))
    return (d, seg["aligned"])

def split_seg(seg):
    """Pieces of a distinction at the next level: list of (incidences, aligned), each incidence (child index, side, lo, hi) of the
    parent tile listed in the same position. Depends only on the label."""
    inc = seg["inc"]
    us = set()
    for i, (_, s, a, b) in enumerate(inc):
        for f in CUTS[s]:
            if a < f < b:
                u = (f - a) / (b - a)
                us.add(u if (i == 0 or seg["aligned"]) else 1 - u)
    pts = [Fr(0)] + sorted(us) + [Fr(1)]
    out = []
    for u0, u1 in zip(pts, pts[1:]):
        new, signs = [], []
        for i, (t, s, a, b) in enumerate(inc):
            up = i == 0 or seg["aligned"]
            l0 = a + u0 * (b - a) if up else b - u0 * (b - a)
            l1 = a + u1 * (b - a) if up else b - u1 * (b - a)
            lo, hi = min(l0, l1), max(l0, l1)
            for c0, c1, ci, cs, fwd in COVER[s]:
                if c0 <= lo and hi <= c1:
                    break
            else:
                raise ValueError("piece crosses a child boundary")
            m0 = (l0 - c0) / (c1 - c0) if fwd else (c1 - l0) / (c1 - c0)
            m1 = (l1 - c0) / (c1 - c0) if fwd else (c1 - l1) / (c1 - c0)
            new.append((ci, cs, min(m0, m1), max(m0, m1)))
            signs.append(1 if m1 > m0 else -1)
        out.append((new, (signs[0] == signs[1]) if len(new) == 2 else None, signs[0]))
    return out

def step(hands, segs):
    """One level: every knot splits into five, every distinction into its pieces, five new distinctions inside every knot."""
    nh = []
    for h in hands:
        nh.extend(h * c for c in HANDS)
    ns = []
    for seg in segs:
        for new, aligned, s0 in split_seg(seg):
            inc = [(5 * seg["inc"][i][0] + ci, cs, lo, hi) for i, (ci, cs, lo, hi) in enumerate(new)]
            ns.append({"inc": inc, "aligned": aligned})
    for t in range(len(hands)):
        for (c1, s1, a1, b1), (c2, s2, a2, b2), al in INTERNAL:
            ns.append({"inc": [(5 * t + c1, s1, a1, b1), (5 * t + c2, s2, a2, b2)], "aligned": al})
    return nh, ns

def sides(nt, segs):
    """Each knot's three sides as ordered lists of distinction ids (by position along the side)."""
    out = [{"S": [], "L": [], "H": []} for _ in range(nt)]
    for k, seg in enumerate(segs):
        for t, s, lo, hi in seg["inc"]:
            out[t][s].append((lo, k))
    for o in out:
        for s in o:
            o[s] = [k for _, k in sorted(o[s])]
    return out

def grow(k):
    hands, segs = start()
    for _ in range(k):
        hands, segs = step(hands, segs)
    return hands, segs

def geometric_incidences(tiles):
    vid = {}
    for t in tiles:
        for p in t:
            vid.setdefault(p, len(vid))
    pts = list(vid)
    side_len = max(abs(t[1][0] - t[0][0]) + abs(t[1][1] - t[0][1]) for t in tiles[:50])
    cell = max(1, side_len)
    buckets = defaultdict(list)
    for p in pts:
        buckets[(p[0] // cell, p[1] // cell)].append(p)
    segs = defaultdict(list)
    for ti, (O, P, Q) in enumerate(tiles):
        for s, (A, B) in (("S", (O, Q)), ("L", (O, P)), ("H", (Q, P))):
            dx, dy = B[0] - A[0], B[1] - A[1]
            L2 = dx * dx + dy * dy
            on = {A: Fr(0), B: Fr(1)}
            for cx in range(min(A[0], B[0]) // cell, max(A[0], B[0]) // cell + 1):
                for cy in range(min(A[1], B[1]) // cell, max(A[1], B[1]) // cell + 1):
                    for p in buckets.get((cx, cy), ()):
                        if (p[0] - A[0]) * dy - (p[1] - A[1]) * dx != 0:
                            continue
                        sc = (p[0] - A[0]) * dx + (p[1] - A[1]) * dy
                        if 0 < sc < L2:
                            on[p] = Fr(sc, L2)
            seq = sorted(on.items(), key=lambda kv: kv[1])
            for (p1, l1), (p2, l2) in zip(seq, seq[1:]):
                segs[frozenset((p1, p2))].append((ti, s, l1, l2, p1))
    # canonical: frozenset of incidences plus alignment (same start point along both sides)
    out = set()
    for key, inc in segs.items():
        if len(inc) == 2:
            aligned = inc[0][4] == inc[1][4]
        else:
            aligned = None
        out.add((frozenset((t, s, a, b) for t, s, a, b, _ in inc), aligned))
    return out


def symbolic_incidences(segs):
    return {(frozenset(seg["inc"]), seg["aligned"]) for seg in segs}

def closed_alphabet():
    """Close the set of distinction labels under the rule, from the starting triangle and the five inside distinctions."""
    def rep(lab):
        d, aligned = lab
        return {"inc": [(i, s, lo, hi) for i, (s, lo, hi) in enumerate(d)], "aligned": aligned}
    def children(lab):
        return [label({"inc": [(0, cs, lo, hi) for ci, cs, lo, hi in new], "aligned": aligned}) for new, aligned, _ in split_seg(rep(lab))]
    hands, segs = start()
    alphabet = {label(s) for s in segs}
    alphabet |= {label({"inc": [(0, s1, a1, b1), (1, s2, a2, b2)], "aligned": al}) for (c1, s1, a1, b1), (c2, s2, a2, b2), al in INTERNAL}
    rounds = 0
    while True:
        new = {c for lab in alphabet for c in children(lab)} - alphabet
        rounds += 1
        if not new:
            return alphabet, children, rounds
        alphabet |= new
