"""Covers and tori for PLAIN-TIME-20261108-001B, on ticket A's plain_lib.

The universal cover of a regular map of type (m, f) (m contacts per ring, f per face) is the tessellation {f, m}; its rotation group is the
triangle group <x, y | x^m = y^2 = (xy)^f = 1>, x turning a ring, y a contact. A ball of the cover's contact graph is read inside PSL(2, p)
for a large prime p with p = 1 mod 4mf/gcd(m, f): x = diag(l, 1/l) with l of order 2m, y of trace 0, and tr(xy) = u + 1/u with u of order
2f, so that x, y and xy have orders m, 2 and f. The ball is the cover's when the quotient identifies no two contacts within it; two
primes are read and must agree. Contacts are cosets g<y> (g up to sign); the arcs into the contact h<y> come from (h x^-1)<y> and
(h y x^-1)<y>, the arcs out of d<y> go to (d x)<y> and (d y x)<y>, as in plain_lib.group_map."""
from __future__ import annotations

import collections
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census"))
import plain_lib as P  # noqa: E402


# ---------- covers in PSL(2, p)
def is_prime(n):
    return n > 1 and all(n % q for q in range(2, int(n ** 0.5) + 1))


def factor(n):
    out, d = [], 2
    while d * d <= n:
        while n % d == 0:
            out.append(d)
            n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def root_of_unity(order, p):
    """an element of exact order `order` in F_p^*"""
    qs = set(factor(p - 1))
    g = next(g for g in range(2, p) if all(pow(g, (p - 1) // q, p) != 1 for q in qs))
    return pow(g, (p - 1) // order, p)


def prime_for(m, f, start):
    L = 4 * m * f // math.gcd(m, f)
    q = start - start % L + 1
    while not (q > start and is_prime(q)):
        q += L
    return q


def psl(p):
    h = (p - 1) // 2

    def norm(M):
        for v in M:
            if v:
                return M if v <= h else tuple((-u) % p for u in M)
        return M

    def mul(A, B):
        return norm(((A[0] * B[0] + A[1] * B[2]) % p, (A[0] * B[1] + A[1] * B[3]) % p,
                     (A[2] * B[0] + A[3] * B[2]) % p, (A[2] * B[1] + A[3] * B[3]) % p))
    return norm, mul


def cover_ball(m, f, p, R):
    """the backward ball of radius R about a target contact of the cover {f, m}, read in PSL(2, p): layer sizes, rings by their
    distance (rings whose least distance is below R), and late rings by distance"""
    norm, mul = psl(p)
    inv = lambda a: pow(a, p - 2, p)
    lam, mu = root_of_unity(2 * m, p), root_of_unity(2 * f, p)
    a = (mu + inv(mu)) * inv((lam - inv(lam)) % p) % p
    x = norm((lam, 0, 0, inv(lam)))
    y = norm((a, 1, (-1 - a * a) % p, (-a) % p))
    xi = x
    for _ in range(m - 2):
        xi = mul(xi, x)
    contact = lambda g: min(g, mul(g, y))
    target = contact(norm((1, 0, 0, 1)))
    dist, layers = {target: 0}, [[target]]
    for r in range(R):
        nxt = []
        for h in layers[-1]:
            for g in (mul(h, xi), mul(mul(h, y), xi)):
                c = contact(g)
                if c not in dist:
                    dist[c] = r + 1
                    nxt.append(c)
        layers.append(nxt)
    cnt = {target: 1}
    for r in range(1, R + 1):
        for d in layers[r]:
            cnt[d] = sum(cnt[e] for e in (contact(mul(d, x)), contact(mul(mul(d, y), x))) if dist.get(e) == r - 1)
    seen_rings, by, late = set(), collections.Counter(), collections.Counter()
    for d in dist:
        for g in (d, mul(d, y)):
            ring, h = [], g
            for _ in range(m):
                ring.append(h)
                h = mul(h, x)
            key = min(ring)
            if key in seen_rings:
                continue
            seen_rings.add(key)
            cs = [contact(h) for h in ring]
            ds = [dist.get(c, R + 1) for c in cs]
            D = min(ds)
            if D >= R:
                continue
            by[D] += 1
            if not any(ds[i] == D and cnt[cs[i]] % 2 for i in range(m)):
                late[D] += 1
    return [len(L) for L in layers], dict(sorted(by.items())), dict(sorted(late.items()))


# ---------- every torus of a lattice kind, as lattices up to rotation
def hnf(v1, v2):
    """the canonical basis ((p, 0), (q, r)), r > 0, 0 <= q < p, of the lattice spanned by v1 and v2"""
    (a, b), (c, d) = v1, v2

    def egcd(u, w):
        if w == 0:
            return (abs(u), (1 if u >= 0 else -1), 0)
        g, s, t = egcd(w, u % w)
        return g, t, s - (u // w) * t
    g, s, t = egcd(b, d)
    det = abs(a * d - b * c)
    pp = det // g
    q = (s * a + t * c) % pp
    return (pp, q, g)


def lattices(kind, nmax):
    """{canonical form: (b, c)} for every rotation-invariant sublattice of index at most nmax, both chiralities"""
    rot = {"square": lambda v: (-v[1], v[0]), "triangular": lambda v: (v[0] - v[1], v[0]),
           "honeycomb": lambda v: (-v[0] - v[1], v[0])}[kind]
    out = {}
    K = int(nmax ** 0.5) + 2
    for b in range(-K, K + 1):
        for c in range(-K, K + 1):
            if (b, c) == (0, 0):
                continue
            w = rot((b, c))
            N = abs(b * w[1] - c * w[0])
            if 1 <= N <= nmax:
                out.setdefault(hnf((b, c), w), (b, c, N))
    return out


def first_tie(m, f, p, R):
    """the least directed distance at which some contact of the cover has two or more shortest routes to the target, with those
    counts (the contact-level horizon), or None within radius R"""
    norm, mul = psl(p)
    inv = lambda a: pow(a, p - 2, p)
    lam, mu = root_of_unity(2 * m, p), root_of_unity(2 * f, p)
    a = (mu + inv(mu)) * inv((lam - inv(lam)) % p) % p
    x = norm((lam, 0, 0, inv(lam)))
    y = norm((a, 1, (-1 - a * a) % p, (-a) % p))
    xi = x
    for _ in range(m - 2):
        xi = mul(xi, x)
    contact = lambda g: min(g, mul(g, y))
    target = contact(norm((1, 0, 0, 1)))
    dist, layer, cnt = {target: 0}, [target], {target: 1}
    for r in range(1, R + 1):
        nxt = []
        for h in layer:
            for g in (mul(h, xi), mul(mul(h, y), xi)):
                c = contact(g)
                if c not in dist:
                    dist[c] = r
                    nxt.append(c)
        for d in nxt:
            cnt[d] = sum(cnt[e] for e in (contact(mul(d, x)), contact(mul(mul(d, y), x))) if dist.get(e) == r - 1)
        ties = sorted(cnt[d] for d in nxt if cnt[d] >= 2)
        if ties:
            return r, ties
        layer = nxt
    return None
