"""The complete radius-2 atlas of the pinwheel law (ticket PINWHEEL-ATLAS-20261107-001A).

Tiles are (O, P, Q): the right angle, the end of the long leg and the end of the short leg (legs 1 : 2). Conway's cut is affine in
(O, P, Q), so it can be applied in any affine frame:
    H = (4 Q + P) / 5,  M = (O + P) / 2,  F1 = (O + H) / 2,  F2 = (H + P) / 2,
    children (H, O, Q), (F1, M, O), (F1, M, H), (F2, H, M), (F2, P, M).
A collar is a tile with every tile that touches it (shares a point). Its key is the tile's handedness and the set of collar tiles in
the tile's own frame (O at 0, Q at (1, 0), P at (0, 1)). Children that touch have parents that touch, so a child's collar lies in the
cut of its parent's collar, and Phi (the collars of the five children) is a map on keys.

The planar map, rooted codes and oriented labels are those of PINWHEEL-NATIVE-20261107-001B: a dart u -> v gets the code of a
breadth-first traversal from u starting at v in counterclockwise order (vertex numbers and degrees, out to graph distance r), and the
label (left tile's side and interval, right tile's side and interval, whether the two sides run the same way)."""
from __future__ import annotations
import math
from collections import defaultdict, deque
from fractions import Fraction as Fr
from functools import reduce

Z, ONE, HALF, F45, F15 = Fr(0), Fr(1), Fr(1, 2), Fr(4, 5), Fr(1, 5)
BASE = ((Z, Z), (Z, ONE), (ONE, Z))          # O, P, Q in a tile's own frame


# ---- the cut, in any affine frame -------------------------------------------------------------------------------------------------
def comb(A, B, wa, wb):
    return (A[0] * wa + B[0] * wb, A[1] * wa + B[1] * wb)

def cut(t):
    O, P, Q = t
    H = comb(Q, P, F45, F15)
    M = comb(O, P, HALF, HALF)
    F1 = comb(O, H, HALF, HALF)
    F2 = comb(H, P, HALF, HALF)
    return [(H, O, Q), (F1, M, O), (F1, M, H), (F2, H, M), (F2, P, M)]

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def on_seg(p, a, b):
    if cross(a, b, p) != 0:
        return False
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])

def sides(t):
    O, P, Q = t
    return ((O, Q), (O, P), (Q, P))

def touch(A, B):
    return (any(on_seg(p, a, b) for p in A for a, b in sides(B))
            or any(on_seg(p, a, b) for p in B for a, b in sides(A)))

def to_frame(c, X):
    O, P, Q = c
    e1 = (Q[0] - O[0], Q[1] - O[1]); e2 = (P[0] - O[0], P[1] - O[1])
    det = e1[0] * e2[1] - e1[1] * e2[0]
    dx, dy = X[0] - O[0], X[1] - O[1]
    return ((dx * e2[1] - dy * e2[0]) / det, (e1[0] * dy - e1[1] * dx) / det)

def orient(t):
    """+1 when the tile has the frame's orientation (Q - O, P - O positively oriented), else -1."""
    O, P, Q = t
    return 1 if cross(O, Q, P) > 0 else -1


# ---- collars and their closure ------------------------------------------------------------------------------------------------------
def key_of(h, c, tiles):
    return (h, frozenset(tuple(to_frame(c, X) for X in t) for t in tiles))

def phi(key):
    h, tiles = key
    tiles = list(tiles)
    kids = {t: cut(t) for t in tiles}
    allkids = [k for t in tiles for k in kids[t]]
    return [key_of(h * orient(c), c, [k for k in allkids if k == c or touch(c, k)]) for c in kids[BASE]]

def closure(seed=None, max_level=None):
    """All collar keys reachable from the one-tile seed (the level-0 patch), with the level at which each first occurs. The search
    ends when every key's five images are already present, i.e. the set is closed under Phi."""
    seed = seed or (1, frozenset([BASE]))
    first = {seed: 0}
    q = deque([seed])
    while q:
        k = q.popleft()
        if max_level is not None and first[k] >= max_level:
            continue
        for k2 in phi(k):
            if k2 not in first:
                first[k2] = first[k] + 1
                q.append(k2)
    return first

def ray(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    s = abs(dx) if dx != 0 else abs(dy)
    return (dx / s, dy / s)

def fan_rays(p, t):
    if p in t:
        a, b = [x for x in t if x != p]
        return [ray(p, a), ray(p, b)]
    for a, b in sides(t):
        if on_seg(p, a, b):
            return [ray(p, a), ray(p, b)]
    return None

def complete(key):
    """The collar covers a neighbourhood of its central tile: at each corner of the central tile and each tile corner on its sides,
    the sectors of the tiles containing that point close up (each bounding ray is shared by exactly two sectors)."""
    _, tiles = key
    tiles = list(tiles)
    pts = set(BASE) | {p for t in tiles for p in t if any(on_seg(p, a, b) for a, b in sides(BASE))}
    for p in pts:
        cnt = defaultdict(int)
        for t in tiles:
            r = fan_rays(p, t)
            if r is not None:
                for x in r:
                    cnt[x] += 1
        if any(v != 2 for v in cnt.values()):
            return False
    return True


# ---- planar maps, codes and labels ---------------------------------------------------------------------------------------------------
def descend(tiles, central, j):
    cur = [(t, t == central) for t in tiles]
    for _ in range(j):
        cur = [(k, f) for t, f in cur for k in cut(t)]
    return [t for t, _ in cur], [t for t, f in cur if f]

def integerize(tiles):
    den = reduce(lambda a, b: a * b // math.gcd(a, b), {x.denominator for t in tiles for p in t for x in p}, 1)
    return [tuple((int(p[0] * den), int(p[1] * den)) for p in t) for t in tiles]

def build_map(tiles, h=1):
    """Planar map of integer tiles: rotation counterclockwise in the orientation h (+1: the coordinates' own orientation)."""
    vid = {}
    for t in tiles:
        for p in t:
            vid.setdefault(p, len(vid))
    pts = list(vid)
    cell = max(1, max(abs(t[1][0] - t[0][0]) + abs(t[1][1] - t[0][1]) for t in tiles))
    buckets = defaultdict(list)
    for p in pts:
        buckets[(p[0] // cell, p[1] // cell)].append(p)
    seg = defaultdict(list)
    for ti, (O, P, Q) in enumerate(tiles):
        for s, (A, B) in (("S", (O, Q)), ("L", (O, P)), ("H", (Q, P))):
            dx, dy = B[0] - A[0], B[1] - A[1]
            L2 = dx * dx + dy * dy
            on = {A: Fr(0), B: Fr(1)}
            for cx in range(min(A[0], B[0]) // cell, max(A[0], B[0]) // cell + 1):
                for cy in range(min(A[1], B[1]) // cell, max(A[1], B[1]) // cell + 1):
                    for p in buckets.get((cx, cy), ()):
                        if p in on or (p[0] - A[0]) * dy - (p[1] - A[1]) * dx != 0:
                            continue
                        sc = (p[0] - A[0]) * dx + (p[1] - A[1]) * dy
                        if 0 < sc < L2:
                            on[p] = Fr(sc, L2)
            sq = sorted(on.items(), key=lambda kv: kv[1])
            for (p1, l1), (p2, l2) in zip(sq, sq[1:]):
                seg[frozenset((p1, p2))].append((ti, s, l1, l2, p1))
    adj = defaultdict(set)
    for k in seg:
        a, b = tuple(k)
        adj[vid[a]].add(vid[b]); adj[vid[b]].add(vid[a])
    rot = {}
    for v, nb in adj.items():
        x, y = pts[v]
        order = sorted(nb, key=lambda w: math.atan2(pts[w][1] - y, pts[w][0] - x))
        rot[v] = order if h > 0 else order[::-1]
    cent = [(O[0] + P[0] + Q[0], O[1] + P[1] + Q[1]) for O, P, Q in tiles]      # 3 * centroid
    dlab = {}
    for k, inc in seg.items():
        a, b = tuple(k)
        for u, v in ((a, b), (b, a)):
            left = right = None
            for ti, s, lo, hi, st in inc:
                c = cent[ti]
                cr = (v[0] - u[0]) * (c[1] - 3 * u[1]) - (v[1] - u[1]) * (c[0] - 3 * u[0])
                if (cr > 0) == (h > 0):
                    left = (s, lo, hi)
                else:
                    right = (s, lo, hi)
            aligned = (inc[0][4] == inc[1][4]) if len(inc) == 2 else None
            dlab[(vid[u], vid[v])] = (left, right, aligned)
    boundary = {vid[p] for k, inc in seg.items() if len(inc) == 1 for p in k}
    return {"pts": pts, "vid": vid, "rot": rot, "dlab": dlab, "boundary": boundary}

def bfs_dist(rot, sources):
    d = {s: 0 for s in sources}; q = deque(sources)
    while q:
        u = q.popleft()
        for w in rot[u]:
            if w not in d:
                d[w] = d[u] + 1; q.append(w)
    return d

def code(rot, u, v, r):
    num = {u: 0}; order = [u]; entry = {u: v}; dist = {u: 0}
    out = []
    i = 0
    while i < len(order):
        x = order[i]; i += 1
        nb = rot[x]
        k = nb.index(entry[x])
        row = []
        for y in nb[k:] + nb[:k]:
            if dist[x] < r:
                if y not in num:
                    num[y] = len(order); order.append(y); entry[y] = x; dist[y] = dist[x] + 1
                row.append(num[y])
            else:
                row.append(num.get(y, -1))
        out.append((len(nb), tuple(row)))
    return tuple(out)

def collar_codes(key, j, r=2):
    """Codes and labels of the darts whose tail is a vertex of the central tile's j-fold descendants, computed in the j-fold cut of
    the collar; also the number of such darts closer than r + 2 to the edge of the cut collar (they would need more context)."""
    h, tiles = key
    alltiles, desc = descend(list(tiles), BASE, j)
    pts = {p for t in alltiles for p in t}
    den = reduce(lambda a, b: a * b // math.gcd(a, b), {x.denominator for p in pts for x in p}, 1)
    conv = {p: (int(p[0] * den), int(p[1] * den)) for p in pts}
    itiles = [tuple(conv[p] for p in t) for t in alltiles]
    M = build_map(itiles, h)
    db = bfs_dist(M["rot"], list(M["boundary"]))
    tails = {M["vid"][conv[p]] for t in desc for p in t}
    got, short = defaultdict(set), 0
    for (u, v), lab in M["dlab"].items():
        if u not in tails:
            continue
        if db.get(u, 0) <= r + 1 or db.get(v, 0) <= r + 1:
            short += 1
            continue
        got[code(M["rot"], u, v, r)].add(lab)
    return got, short


# ---- the geometric reference (PINWHEEL-NATIVE-20261107-001B's construction) ---------------------------------------------------------
def split_pinwheel(tile):
    O, P, Q = tile
    H = (Q[0] + (P[0] - Q[0]) // 5, Q[1] + (P[1] - Q[1]) // 5)
    M = ((O[0] + P[0]) // 2, (O[1] + P[1]) // 2)
    F1 = ((O[0] + H[0]) // 2, (O[1] + H[1]) // 2)
    F2 = ((H[0] + P[0]) // 2, (H[1] + P[1]) // 2)
    return [(H, O, Q), (F1, M, O), (F1, M, H), (F2, H, M), (F2, P, M)]

def pinwheel_patch(k):
    tiles = [((0, 0), (2, 0), (0, 1))]
    for _ in range(k):
        tiles = [tuple((x * 10, y * 10) for x, y in t) for t in tiles]
        tiles = [s for t in tiles for s in split_pinwheel(t)]
    return tiles

def patch_codes(tiles, r, h=1):
    M = build_map(tiles, h)
    db = bfs_dist(M["rot"], list(M["boundary"]))
    g = defaultdict(set)
    for (u, v), lab in M["dlab"].items():
        if db.get(u, 0) <= r + 1 or db.get(v, 0) <= r + 1:
            continue
        g[code(M["rot"], u, v, r)].add(lab)
    return g
