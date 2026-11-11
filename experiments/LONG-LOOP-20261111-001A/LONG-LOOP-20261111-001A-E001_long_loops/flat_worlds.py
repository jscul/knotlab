"""Flat worlds of knots alone as quotients of the triangular lattice (LONG-LOOP-20261111-001A-E001).

The triangular lattice is Z^2 with neighbours +-(1,0), +-(0,1), +-(1,1) and knots {x, x+(1,0), x+(1,1)}, {x, x+(0,1), x+(1,1)}.
Every 6-regular triangulated torus is Z^2/L for a sublattice L (Altshuler), and every 6-regular triangulated Klein bottle is
Z^2/G for a group G = L u gL, g(x) = Mx + s a glide reflection of the lattice with M a reflection of its point group, L an
M-invariant sublattice and Ms + s in L (the deck group of a flat triangulation: its orientation-preserving part is translations,
since rotations fix points). Edge-width is min over g' != 1 in G and vertices x of the lattice distance from x to g'x.
"""

from __future__ import annotations

import itertools

NBR = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]


def hexn(x, y):
    return max(abs(x), abs(y)) if x * y >= 0 else abs(x) + abs(y)


def point_group():
    out = []
    nb = set(NBR)
    for a, b, c, d in itertools.product((-1, 0, 1), repeat=4):
        if a * d - b * c not in (1, -1):
            continue
        if {(a * x + b * y, c * x + d * y) for x, y in NBR} == nb:
            out.append(((a, b), (c, d)))
    return out


REFLECTIONS = [M for M in point_group() if M[0][0] * M[1][1] - M[0][1] * M[1][0] == -1]


def apply(M, v):
    return (M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1])


class Lattice:
    """L spanned by (a, b) and (0, c); cosets reduced to x in [0, a), y in [0, c)."""

    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

    def red(self, x, y):
        q, x0 = divmod(x, self.a)
        return x0, (y - q * self.b) % self.c

    def contains(self, v):
        return self.red(*v) == (0, 0)

    def vectors(self, r=8):
        return [(i * self.a, i * self.b + j * self.c) for i in range(-r, r + 1) for j in range(-r, r + 1) if (i, j) != (0, 0)]


def sublattices(index):
    for a in range(1, index + 1):
        if index % a:
            continue
        c = index // a
        for b in range(c):
            yield Lattice(a, b, c)


def lattice_knots():
    return [((0, 0), (1, 0), (1, 1)), ((0, 0), (0, 1), (1, 1))]


def torus(L):
    """Z^2/L as (V, knots, edge-width), or None if not a simplicial surface."""
    idx = {}
    for x in range(L.a):
        for y in range(L.c):
            idx[(x, y)] = len(idx)
    V = len(idx)
    T = set()
    for x in range(L.a):
        for y in range(L.c):
            for tri in lattice_knots():
                vs = tuple(sorted(idx[L.red(x + p, y + q)] for p, q in tri))
                if len(set(vs)) < 3:
                    return None
                T.add(vs)
    if len(T) != 2 * V:
        return None
    ew = min(hexn(*v) for v in L.vectors())
    return V, sorted(T), ew


def klein(L, M, s):
    """Z^2/<L, g>, g(x) = Mx + s, as (V, knots, edge-width), or None if the action is not free or the quotient not simplicial."""
    reps = [(x, y) for x in range(L.a) for y in range(L.c)]

    def sigma(p):
        q = apply(M, p)
        return L.red(q[0] + s[0], q[1] + s[1])
    orbit = {}
    for p in reps:
        if p in orbit:
            continue
        q = sigma(p)
        if q == p:
            return None
        k = len(orbit) // 2 if False else None
        orbit[p] = orbit[q] = min(p, q)
    names = {r: i for i, r in enumerate(sorted(set(orbit.values())))}
    V = len(names)
    T = set()
    for x, y in reps:
        for tri in lattice_knots():
            vs = tuple(sorted(names[orbit[L.red(x + p, y + q)]] for p, q in tri))
            if len(set(vs)) < 3:
                return None
            T.add(vs)
    if len(T) != 2 * V:
        return None
    # edge-width: translations, and glides g' = (M, s + l)
    ew = min(hexn(*v) for v in L.vectors())
    for l in L.vectors(r=4) + [(0, 0)]:
        for x, y in reps:
            q = apply(M, (x, y))
            d = (q[0] + s[0] + l[0] - x, q[1] + s[1] + l[1] - y)
            ew = min(ew, hexn(*d))
    return V, sorted(T), ew


def klein_bottles(V):
    """Every Z^2/G with |Z^2/L| = 2V, as raw (V, knots, edge-width) triples (isomorphic copies included)."""
    out = []
    for L in sublattices(2 * V):
        for M in REFLECTIONS:
            if not (L.contains(apply(M, (L.a, L.b))) and L.contains(apply(M, (0, L.c)))):
                continue
            for s in ((x, y) for x in range(L.a) for y in range(L.c)):
                g2 = apply(M, s)
                if not L.contains((g2[0] + s[0], g2[1] + s[1])):
                    continue
                r = klein(L, M, s)
                if r is not None:
                    out.append(r)
    return out
