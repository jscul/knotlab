"""Flip certificates for odd-period words (research/EVEN-PERIOD-20261112-001/preregistration.md, ticket A).

A word u of minimal period p is a repeating state x_i = u[i mod p]. A knot kind (0, a, b), 0 < a < b, is satisfied by u exactly when
u is never constant on (r, r + a, r + b) mod p, so it depends only on the residue pair (a mod p, b mod p); G(u) is the set of residue
pairs u satisfies (lemma 2). A p-periodic word c is compatible with u when it satisfies every pair in G(u). A residue r0 of c is
flippable when no pair (al, be) in G(u), in no role (first, middle, last), puts the two other values of a knot through r0 equal and
different from c[r0]. A flip certificate for u is a compatible c with a flippable residue (lemma 3): every base allowing u then
allows c with one value flipped, a state that does not repeat, so no harmony allows u."""
import itertools

import numpy as np


def lyndon(p):
    """the Lyndon words of length p over {0, 1} (aperiodic necklaces), by the FKM algorithm"""
    a = [0] * (p + 1)
    t = 1
    out = []

    def gen(t, q):
        if t > p:
            if p % q == 0 and q == p:
                out.append(a[1:p + 1].copy())
            return
        a[t] = a[t - q]
        gen(t + 1, q)
        for j in range(a[t - q] + 1, 2):
            a[t] = j
            gen(t + 1, t)

    gen(1, 1)
    return out


def words(p):
    """every Lyndon word of length p (one word per orbit of minimal period p; an orbit and its complement are both listed)"""
    for w in lyndon_iter(p):
        yield np.array(w, dtype=np.int8)


def lyndon_iter(p):
    """the Lyndon words of length p, generated without storing them (Duval's iteration)"""
    w = [0]
    while w:
        if len(w) == p:
            yield list(w)
        m = len(w)
        while len(w) < p:
            w.append(w[len(w) - m])
        while w and w[-1] == 1:
            w.pop()
        if w:
            w[-1] = 1


IDX = {}


def _idx(p):
    if p not in IDX:
        r = np.arange(p)
        al = np.arange(p)[:, None, None]
        be = np.arange(p)[None, :, None]
        IDX[p] = (np.broadcast_to(r, (p, p, p)), (r + al) % p, (r + be) % p)
    return IDX[p]


def good_pairs(u):
    """G(u): residue pairs (al, be) with u never constant on (r, r + al, r + be)"""
    p = len(u)
    R, A, B = _idx(p)
    mono = (u[R] == u[A]) & (u[A] == u[B])
    ok = ~mono.any(axis=2)
    return [(int(x), int(y)) for x, y in zip(*np.nonzero(ok))]


def roles(r0, al, be, p):
    """the two other residues of a knot of residue pair (al, be) through r0, in each role"""
    return (((r0 + al) % p, (r0 + be) % p), ((r0 - al) % p, (r0 - al + be) % p), ((r0 - be) % p, (r0 - be + al) % p))


def flippable(c, G):
    p = len(c)
    out = []
    for r0 in range(p):
        if not any(c[x] == c[y] != c[r0] for (al, be) in G for (x, y) in roles(r0, al, be, p)):
            out.append(r0)
    return out


def compatible(c, G):
    p = len(c)
    return all(len({c[r], c[(r + al) % p], c[(r + be) % p]}) > 1 for r in range(p) for (al, be) in G)


def certificate_by_sat(u, G):
    """a compatible word with a flippable residue, by SAT (pysat), or None"""
    from pysat.solvers import Solver
    p = len(u)
    v = lambda i: i + 1
    base = set()
    for (al, be) in G:
        for r in range(p):
            t = sorted({r, (r + al) % p, (r + be) % p})
            base.add(tuple(v(i) for i in t))
            base.add(tuple(-v(i) for i in t))
    for r0 in range(p):
        cl = set(base)
        for (al, be) in G:
            for (x, y) in roles(r0, al, be, p):
                # forbid c[x] = c[y] != c[r0]
                cl.add(tuple(sorted({-v(x), -v(y), v(r0)})))
                cl.add(tuple(sorted({v(x), v(y), -v(r0)})))
        with Solver(name="cadical153", bootstrap_with=[list(c) for c in cl]) as s:
            if s.solve():
                m = s.get_model()
                c = [int(m[i] > 0) for i in range(p)]
                return c, r0
    return None


def certify(u):
    """('no kind', None) if G(u) is empty; ('self', r0) if u itself has a flippable residue; ('other', (c, r0)); ('none', None)"""
    G = good_pairs(u)
    if not G:
        return "no kind", None, 0
    f = flippable(u, G)
    if f:
        return "self", f[0], len(G)
    cert = certificate_by_sat(u, G)
    if cert is None:
        return "none", None, len(G)
    return "other", cert, len(G)
