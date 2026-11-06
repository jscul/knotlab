"""The knot's atom on an edge (KNOT-COUPLING-20261031-001A).

A system is a list of lines, each a tuple of three distinct hashable points; every point lies on three lines. A signing is a set of negated
incidences (line index, point). The monochromatic enumerator of a signed system is

    M(H, sigma; lam) = sum over 2-colourings c of the points of lam ** (number of lines whose three colours, flipped on negated
                       incidences, agree),

so M(H, sigma; 0) is the number of proper 2-colourings (#col) and a line weighs lam when monochromatic and 1 otherwise.
In the even-subgraph (Hadamard) form a line is [1, 0, u, 0] with u = (lam - 1) / (lam + 3).

The atom H<e0>, for an incidence e0 = (l0, p0) of H, replaces an incidence e = (l, p) of a system G: p takes p0's place in l0 and p0 takes
p's place in l."""
import itertools
from fractions import Fraction

import networkx as nx

FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def points(lines):
    return sorted({p for l in lines for p in l}, key=repr)


def is_cubic(lines):
    deg = {}
    for l in lines:
        assert len(set(l)) == 3
        for p in l:
            deg[p] = deg.get(p, 0) + 1
    return all(d == 3 for d in deg.values()) and len(deg) == len(lines)


def point_splice(H1, t, H2, M):
    """the point splice of H2 (at its line M) into H1 (at its point t), THREEFOLD-SPACES-20261030-001A: remove t and M; the three lines of H1
    through t take the three points of M, in order"""
    out, k = [], 0
    for l in H1:
        if t in l:
            out.append(tuple(('s', M[k]) if q == t else ('a', q) for q in l))
            k += 1
        else:
            out.append(tuple(('a', q) for q in l))
    return out + [tuple(('s', q) for q in l) for l in H2 if tuple(l) != tuple(M)]


SPLICE = point_splice(FANO, 0, FANO, FANO[0])          # the 13-point Fano splice


def incidences(lines):
    return [(i, p) for i, l in enumerate(lines) for p in l]


def incidence_graph(lines):
    g = nx.Graph()
    for i, l in enumerate(lines):
        for p in l:
            g.add_edge(('l', i), ('p', p))
    return g


# ------------------------------------------------------------------------------------------------ exact counting by elimination
def evaluate(lines, lam, neg=frozenset(), fixed=None):
    """M(H, sigma; lam) at an exact value lam (int or Fraction, or a pair (re, im) of Fractions for complex values) by variable elimination
    over the points (min-degree order). fixed: {point: colour} pins some points."""
    cplx = isinstance(lam, tuple)
    one = (Fraction(1), Fraction(0)) if cplx else 1
    zero = (Fraction(0), Fraction(0)) if cplx else 0

    def add(a, b):
        return (a[0] + b[0], a[1] + b[1]) if cplx else a + b

    def mul(a, b):
        return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]) if cplx else a * b

    fixed = fixed or {}
    factors = []
    for i, l in enumerate(lines):
        scope = tuple(p for p in dict.fromkeys(l) if p not in fixed)
        table = {}
        for a in itertools.product((0, 1), repeat=len(scope)):
            col = dict(zip(scope, a))
            col.update(fixed)
            seen = {col[p] ^ ((i, p) in neg) for p in l}
            table[a] = lam if len(seen) == 1 else one
        factors.append((scope, table))
    free = [p for p in points(lines) if p not in fixed]
    remaining = set(free)
    const = one
    while remaining:
        nb = {p: set() for p in remaining}
        for scope, _ in factors:
            for p in scope:
                nb[p] |= set(scope) - {p}
        v = min(remaining, key=lambda p: (len(nb[p]), repr(p)))
        mine = [f for f in factors if v in f[0]]
        factors = [f for f in factors if v not in f[0]]
        scope = tuple(sorted({q for s, _ in mine for q in s} - {v}, key=repr))
        table = {}
        for a in itertools.product((0, 1), repeat=len(scope)):
            asg = dict(zip(scope, a))
            tot = zero
            for cv in (0, 1):
                asg[v] = cv
                prod = one
                for s, t in mine:
                    prod = mul(prod, t[tuple(asg[q] for q in s)])
                tot = add(tot, prod)
            table[a] = tot
        if scope:
            factors.append((scope, table))
        else:
            const = mul(const, table[()])
        remaining.discard(v)
    for s, t in factors:
        assert not s
        const = mul(const, t[()])
    return const


def mono_poly(lines, neg=frozenset()):
    """integer coefficients of M(H, sigma; lam), degree <= number of lines, by exact interpolation at lam = 0..|L|"""
    n = len(lines)
    xs = list(range(n + 1))
    ys = [evaluate(lines, Fraction(t), neg) for t in xs]
    # Newton divided differences, then expand
    coef = list(ys)
    for j in range(1, n + 1):
        for i in range(n, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - j])
    poly = [Fraction(0)] * (n + 1)
    basis = [Fraction(1)]
    for j in range(n + 1):
        for k, c in enumerate(basis):
            poly[k] += coef[j] * c
        nxt = [Fraction(0)] * (len(basis) + 1)
        for k, c in enumerate(basis):
            nxt[k + 1] += c
            nxt[k] -= xs[j] * c
        basis = nxt
    assert all(c.denominator == 1 for c in poly)
    return [int(c) for c in poly]


def brute_mono(lines, neg=frozenset()):
    """the distribution of monochromatic lines by direct enumeration (small systems only)"""
    pts = points(lines)
    dist = [0] * (len(lines) + 1)
    for c in itertools.product((0, 1), repeat=len(pts)):
        col = dict(zip(pts, c))
        k = sum(1 for i, l in enumerate(lines) if len({col[p] ^ ((i, p) in neg) for p in l}) == 1)
        dist[k] += 1
    return dist


def even_form(lines, lam, neg=frozenset()):
    """M via the even-subgraph form: 2^|P| ((2 lam + 6) / 8)^|L| sum over even subgraphs chi of the incidence graph of
    u^(|chi|/2) (-1)^|sigma & chi|, u = (lam - 1)/(lam + 3) (small systems only)"""
    g = incidence_graph(lines)
    edges = [frozenset(e) for e in g.edges()]
    idx = {e: k for k, e in enumerate(edges)}
    span = [0]
    for cyc in nx.cycle_basis(g):
        m = 0
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            m ^= 1 << idx[frozenset((a, b))]
        span += [s ^ m for s in span]
    negmask = sum(1 << idx[frozenset((('l', i), ('p', p)))] for i, p in neg)
    lam = Fraction(lam)
    u = (lam - 1) / (lam + 3)
    tot = Fraction(0)
    for chi in span:
        tot += u ** (bin(chi).count("1") // 2) * (-1) ** bin(chi & negmask).count("1")
    return 2 ** len(points(lines)) * ((2 * lam + 6) / 8) ** len(lines) * tot


# ------------------------------------------------------------------------------------------------ atoms and decorations
def negate(neg, inc):
    return frozenset(set(neg) ^ {inc})


def edge_function(H, e0, lam):
    """g(a, b) of the atom H<e0> at lam: the line l0 sees colour a in p0's place, and p0 has colour b"""
    l0, p0 = e0
    out = {}
    for a, b in itertools.product((0, 1), repeat=2):
        ext = ('ext',)
        lines = [tuple(ext if (i == l0 and q == p0) else q for q in l) for i, l in enumerate(H)]
        # the external colour a is a pinned extra point; p0 pinned to b
        out[(a, b)] = evaluate(lines, lam, fixed={ext: a, p0: b})
    return out


def decorate(G, e, H, e0, tag):
    """G with the atom H<e0> on the incidence e = (l, p) of G: p moves into H's line l0 (in p0's place), p0 moves into l (in p's place)"""
    l, p = e
    l0, p0 = e0
    out = [tuple(((tag, p0) if (i == l and q == p) else q) for q in L) for i, L in enumerate(G)]
    for j, L in enumerate(H):
        out.append(tuple(p if (j == l0 and q == p0) else (tag, q) for q in L))
    return out


def chain(G, e, H, e0, k, tag="c"):
    """k atoms in series on the incidence e: returns the new system and the incidence that now carries e's role at the far end"""
    cur, inc = G, e
    for j in range(k):
        cur = decorate(cur, inc, H, e0, (tag, j))
        l, p = inc
        inc = (l, ((tag, j), e0[1]))        # the line l now holds the atom's point p0, renamed
    return cur


def rho_parts(H, e0, lam):
    """(alpha, beta) with alpha = M(H)/2, beta = M(H with e0 negated)/2, at lam"""
    return evaluate(H, lam) / 2, evaluate(H, lam, negate(frozenset(), e0)) / 2


def pm_count(g):
    """number of perfect matchings of a bipartite graph (small graphs): permanent by recursion"""
    left = sorted([v for v in g if v[0] == 'l'], key=repr)
    right_index = {v: k for k, v in enumerate(sorted([v for v in g if v[0] == 'p'], key=repr))}
    nbrs = [[right_index[w] for w in g[v]] for v in left]
    memo = {}

    def rec(i, used):
        if i == len(left):
            return 1
        key = (i, used)
        if key not in memo:
            memo[key] = sum(rec(i + 1, used | (1 << j)) for j in nbrs[i] if not used >> j & 1)
        return memo[key]
    return rec(0, 0)


def signed_det(lines, neg=frozenset()):
    """det of the incidence matrix with -1 on negated incidences (rows lines, columns points), exact"""
    import sympy as sp
    pts = points(lines)
    m = sp.zeros(len(lines), len(pts))
    for i, l in enumerate(lines):
        for p in l:
            m[i, pts.index(p)] = -1 if (i, p) in neg else 1
    return m.det()
