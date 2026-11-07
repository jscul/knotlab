"""Ledrappier's law x(i,j) + x(i+1,j) + x(i,j+1) = 0 on Z^2: knots as vanishing sums of X^a (1+X)^b.

A finite set S of sites is an implied parity check of the law exactly when the sum over S of
X^a (1+X)^b is 0 in F2(X) (Y = 1 + X kills the ideal (1 + X + Y)). A knot is a minimal such set with at
least three points. Monomials X^a (1+X)^b are encoded as Python ints after shifting a, b >= 0, which
multiplies the whole sum by one monomial and does not change which sums vanish.
"""

from __future__ import annotations

from typing import Iterable, Sequence


def vec(a: int, b: int) -> int:
    """Coefficients of x^a (1+x)^b over F2 (a, b >= 0) as a bitmask."""
    if a < 0 or b < 0:
        raise ValueError("shift to non-negative exponents first")
    p = 1
    for _ in range(b):
        p ^= p << 1
    return p << a


def rank(vectors: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    r = 0
    for v in vectors:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                r += 1
                break
    return r


def shifted(points: Sequence[tuple[int, int]]):
    a0 = min(a for a, _ in points)
    b0 = min(b for _, b in points)
    return [(a - a0, b - b0) for a, b in points]


def vanishes(points: Sequence[tuple[int, int]]) -> bool:
    total = 0
    for a, b in shifted(points):
        total ^= vec(a, b)
    return total == 0


def is_knot(points: Sequence[tuple[int, int]]) -> bool:
    points = list(points)
    if len(points) < 3 or len(set(points)) != len(points):
        return False
    vs = [vec(a, b) for a, b in shifted(points)]
    total = 0
    for v in vs:
        total ^= v
    return total == 0 and rank(vs) == len(vs) - 1


def naf(n: int) -> list[tuple[int, int]]:
    """Non-adjacent form of n >= 1 as (sign, exponent) pairs, lowest exponent first."""
    digits, e = [], 0
    while n:
        if n & 1:
            d = 2 - (n & 3)
            digits.append((d, e))
            n -= d
        n >>= 1
        e += 1
    return digits


def naf_weight(n: int) -> int:
    return len(naf(n))


def hop_knot(n: int, digits: Sequence[tuple[int, int]] | None = None) -> list[tuple[int, int]]:
    """The knot through (0,0) and (n,0) built from signed powers of two: one Frobenius triangle per hop,
    with apex (min(z, z'), 2^e) for the hop z -> z' = z + s 2^e; the inner path points cancel."""
    if digits is None:
        digits = naf(n)
    z, apexes = 0, []
    for s, e in digits:
        z2 = z + s * 2 ** e
        apexes.append((min(z, z2), 2 ** e))
        z = z2
    if z != n:
        raise ValueError("digits do not sum to n")
    return [(0, 0), (n, 0)] + apexes


def is_frobenius_triangle(points) -> bool:
    pts = set(points)
    if len(pts) != 3:
        return False
    for c in pts:
        others = pts - {c}
        for e in range(0, 40):
            if others == {(c[0] + 2 ** e, c[1]), (c[0], c[1] + 2 ** e)}:
                return True
    return False


# symmetries of the law: the swap (i,j) -> (j,i) and the rotation (i,j) -> (-i-j, i) map up-triangles
# to translated up-triangles, so they map knots to knots
def swap(p):
    return (p[1], p[0])


def rotate(p):
    return (-p[0] - p[1], p[0])


def d_norm_table(radius: int, max_terms: int) -> dict[tuple[int, int], int]:
    """Least number of terms +-2^e v (v in e1, e2, e1-e2) summing to each vector with |coords| <= radius,
    by breadth-first search over sums that stay within a margin (exact for the table's range when the
    margin covers every partial sum of a shortest word; the check records the margin used)."""
    gens = []
    e = 0
    while 2 ** e <= 4 * radius:
        for v in ((1, 0), (0, 1), (1, -1)):
            for s in (1, -1):
                gens.append((s * v[0] * 2 ** e, s * v[1] * 2 ** e))
        e += 1
    bound = 4 * radius
    dist = {(0, 0): 0}
    frontier = [(0, 0)]
    for k in range(1, max_terms + 1):
        nxt = []
        for p in frontier:
            for g in gens:
                q = (p[0] + g[0], p[1] + g[1])
                if max(abs(q[0]), abs(q[1])) <= bound and q not in dist:
                    dist[q] = k
                    nxt.append(q)
        frontier = nxt
    return {p: d for p, d in dist.items() if max(abs(p[0]), abs(p[1])) <= radius}


def smallest_vanishing_through(p, q, window: Sequence[tuple[int, int]], max_size: int):
    """Smallest vanishing set through p and q with at most max_size <= 5 points, extra points from the
    window. For at most five points, vanishing implies knot: the law has no one- or two-point checks."""
    if max_size > 5:
        raise ValueError("search is exact as a knot search only up to five points")
    pts = [w for w in window if w != p and w != q]
    allp = pts + [p, q]
    a0 = min(a for a, _ in allp)
    b0 = min(b for _, b in allp)
    v = {w: vec(w[0] - a0, w[1] - b0) for w in allp}
    target = v[p] ^ v[q]
    lookup: dict[int, tuple[int, int]] = {}
    for w in pts:
        lookup.setdefault(v[w], w)
    if max_size >= 3 and target in lookup:
        return [p, q, lookup[target]]
    if max_size >= 4:
        for s in pts:
            t = lookup.get(target ^ v[s])
            if t is not None and t != s:
                return [p, q, s, t]
    if max_size >= 5:
        for i, s in enumerate(pts):
            x = target ^ v[s]
            for t in pts[i + 1:]:
                u = lookup.get(x ^ v[t])
                if u is not None and u != s and u != t:
                    return [p, q, s, t, u]
    return None
