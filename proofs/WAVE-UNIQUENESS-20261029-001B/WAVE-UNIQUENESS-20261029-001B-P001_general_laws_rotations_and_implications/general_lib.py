"""General three-bit laws on the level-k Sierpinski gaskets (WAVE-UNIQUENESS-20261029-001B).

A law is a 2x2x2 table w[a, b, c] (roles a, b, c of the up triangle T(i, j) = ((i, j), (i+1, j), (i, j+1))).  The six symmetries of the
gasket permute the roles and the corners together (SIGNED-GASKETS-20261029-001B, Lemma 1), so a law is exact iff each of its role
permutations is; complementing every bit also preserves exactness.  Generic laws are two-sector: w = u1 v1 y1 + u2 v2 y2."""
import itertools
import sympy as sp

TU = list(itertools.product((0, 1), repeat=3))
G = {t: sp.Symbol("g%d%d%d" % t) for t in TU}


def gasket(k):
    V = [(i, j) for i in range(k + 1) for j in range(k + 1 - i)]
    tris = [((i, j), (i + 1, j), (i, j + 1)) for i in range(k) for j in range(k - i)]
    return V, tris, [(0, 0), (k, 0), (0, k)]


def relation(k, weights=None):
    """the corner relation of a general law at level k, as a dict tuple -> polynomial in the eight weights (brute force)"""
    weights = weights or G
    V, tris, corners = gasket(k)
    internal = [v for v in V if v not in corners]
    out = {}
    for cv in TU:
        tot = 0
        for bits in itertools.product((0, 1), repeat=len(internal)):
            val = dict(zip(internal, bits))
            val.update(zip(corners, cv))
            term = 1
            for a, b, c in tris:
                term *= weights[(val[a], val[b], val[c])]
            tot += term
        out[cv] = sp.expand(tot)
    return out


def J(v):
    return (-v[1], v[0])


def dot(x, y):
    return x[0] * y[0] + x[1] * y[1]


def two_sector(u1, v1, y1, u2, v2, y2, c=1):
    return {t: u1[t[0]] * v1[t[1]] * y1[t[2]] + c * u2[t[0]] * v2[t[1]] * y2[t[2]] for t in TU}


def cyclic(u1, v1, y1, c=1):
    """the cyclic branch: u2 = J v1, v2 = J y1, y2 = J u1"""
    return two_sector(u1, v1, y1, J(v1), J(y1), J(u1), c)


def implication(s, t):
    """the basic implication law e0 v y + Jv Jy e1 with v = (1, s), y = (1, t): support a = 1 implies c = 1"""
    return cyclic((1, 0), (1, s), (1, t), 1)


def permute(w, perm):
    """(perm w)(x0, x1, x2) = w(x_perm[0], x_perm[1], x_perm[2])"""
    return {t: w[tuple(t[perm[i]] for i in range(3))] for t in TU}


def complement(w):
    return {t: w[tuple(1 - x for x in t)] for t in TU}


def slot_rank_one(u, M):
    """w = u(a) M[b][c]"""
    return {t: u[t[0]] * M[t[1]][t[2]] for t in TU}


def is_knot(w):
    allowed = [t for t in TU if w[t] != 0]
    if not allowed or len(allowed) == 8:
        return False
    return all(len({t[:i] + t[i + 1:] for t in allowed}) == 4 for i in range(3))


def support(w):
    return sorted("".join(map(str, t)) for t in TU if w[t] != 0)
