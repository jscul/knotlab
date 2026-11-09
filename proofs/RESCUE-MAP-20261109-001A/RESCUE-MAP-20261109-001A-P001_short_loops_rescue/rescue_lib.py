"""Tubes and tori of the square, triangular and honeycomb lattices of rings (RESCUE-MAP-20261109-001A).

Contacts of the plane lattices are (type, p): on the square and triangular lattices the edge from ring p in direction D[t] (t < half);
on the honeycomb, e_t(p) of honey_lib (A(p) joined to B(p), B(p - e1), B(p - e2)). A ring lists its contacts counterclockwise and an arc
goes from each contact to the next on each of its rings (loopnet_lib's reading). A tube is the quotient by one lattice vector v; a torus
by a lattice of rank 2. Distances and shortest-route counts are read backwards from a target contact, counts mod 2 unless a modulus is given."""
from __future__ import annotations

import collections
import math


DIRS = {"square": ((1, 0), (0, 1), (-1, 0), (0, -1)),
        "triangular": ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))}
TYPES = {"square": 2, "triangular": 3, "honeycomb": 3}
RING_SIZE = {"square": 4, "triangular": 6, "honeycomb": 3}
ELL = {"square": 4, "triangular": 6, "honeycomb": 5}   # the planes' first late distances (PLAIN-TIME-20261108-001B, Theorem 2)


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def rings_of(kind):
    """ring kinds: one per point on the square and triangular lattices, A and B on the honeycomb"""
    return ("A", "B") if kind == "honeycomb" else ("R",)


def slots(kind, rk, p):
    """the contacts of the ring of kind rk at p, counterclockwise"""
    if kind == "honeycomb":
        if rk == "A":
            return [(0, p), (1, p), (2, p)]
        return [(0, p), (1, add(p, (1, 0))), (2, add(p, (0, 1)))]
    D = DIRS[kind]
    h = len(D) // 2
    out = []
    for i, d in enumerate(D):
        out.append((i, p) if i < h else (i - h, add(p, d)))
    return out


def contact_rings(kind, c):
    """the two rings (kind, point) holding contact c, with c's slot on each"""
    t, p = c
    if kind == "honeycomb":
        q = (p, add(p, (-1, 0)), add(p, (0, -1)))[t]
        return [("A", p, t), ("B", q, t)]
    D = DIRS[kind]
    h = len(D) // 2
    return [("R", p, t), ("R", add(p, D[t]), t + h)]


def out_arcs(kind, c):
    """the arcs out of contact c: to the next contact counterclockwise on each of its rings"""
    res = []
    for rk, p, s in contact_rings(kind, c):
        sl = slots(kind, rk, p)
        res.append(sl[(s + 1) % len(sl)])
    return res


def in_arcs(kind, c):
    res = []
    for rk, p, s in contact_rings(kind, c):
        sl = slots(kind, rk, p)
        res.append(sl[(s - 1) % len(sl)])
    return res


# ---------- quotients: canonical representatives modulo a rank-1 or rank-2 lattice
class Quotient:
    def __init__(self, gens):
        self.gens = [tuple(g) for g in gens]

    def red(self, p):
        if len(self.gens) == 1:
            a, b = self.gens[0]
            g = math.gcd(a, b)
            a0, b0 = a // g, b // g
            # coordinates along v0 = (a0, b0) and a complement u with det(v0, u) = 1
            s, t = egcd(a0, b0)[1:]
            u = (-t, s)
            det = a0 * u[1] - b0 * u[0]
            assert det == 1
            x, y = p
            j = a0 * y - b0 * x            # det(v0, p): the coordinate across v0
            k = x * u[1] - y * u[0]        # coordinate along v0
            k %= g                          # modulo v = g v0
            return (k * a0 + j * u[0], k * b0 + j * u[1])
        (a, b), (c, d) = self.gens
        det = a * d - b * c
        if det < 0:
            (a, b), (c, d) = (c, d), (a, b)
            det = -det
        x, y = p
        s = x * d - y * c
        t = y * a - x * b
        fs, ft = s // det, t // det
        return (x - fs * a - ft * c, y - fs * b - ft * d)


def egcd(m, n):
    if n == 0:
        return (abs(m), 1 if m >= 0 else -1, 0)
    g, s, t = egcd(n, m % n)
    return g, t, s - (m // n) * t


def bfs_counts(kind, Q, target, radius, modulus=2):
    """backward breadth-first search in the quotient from the target contact: {contact: (distance, count mod 2)} to the given radius.
    Exact: a contact at distance r is reached only through contacts at distance r - 1, all inside the radius."""
    red = lambda c: (c[0], Q.red(c[1]))
    tgt = red(target)
    dist, cnt = {tgt: 0}, {tgt: 1}
    layer = [tgt]
    for r in range(1, radius + 1):
        nxt = set()
        for c in layer:
            for b in in_arcs(kind, c):
                b = red(b)
                if b not in dist:
                    nxt.add(b)
        # a contact at distance r sums the counts of its out-neighbours at distance r - 1, each arc once
        for b in nxt:
            dist[b] = r
        for b in nxt:
            cnt[b] = sum(cnt[e] for e in map(red, out_arcs(kind, b)) if dist.get(e) == r - 1) % modulus
        layer = list(nxt)
        if not layer:
            break
    return dist, cnt


def ring_verdict(kind, Q, dist, cnt, rk, p, radius):
    """(least distance, closest slots, on time) for the ring of kind rk at p, if all its contacts are within the radius"""
    sl = [(c[0], Q.red(c[1])) for c in slots(kind, rk, p)]
    ds = [dist.get(c) for c in sl]
    if any(x is None for x in ds):
        return None
    d = min(ds)
    close = [i for i, c in enumerate(sl) if ds[i] == d]
    return d, close, any(cnt[sl[i]] for i in close)
