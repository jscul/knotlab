import sys, json, random, time
import numpy as np
from pysat.solvers import Minisat22

def lyndon(p):
    """Duval: all binary Lyndon words of length exactly p."""
    w = [-1]
    out = []
    while w:
        w[-1] += 1
        m = len(w)
        if m == p:
            out.append(tuple(w))
        while len(w) < p:
            w.append(w[len(w) - m])
        while w and w[-1] == 1:
            w.pop()
    return out

def min_period(u):
    p = len(u)
    for d in range(1, p + 1):
        if p % d == 0 and all(u[i] == u[i % d] for i in range(p)):
            return d

def pairs(p):
    return [(a, b) for a in range(1, p) for b in range(a + 1, p)]

def good_pairs_batch(W):
    """W: (N,p) 0/1. returns list of pairs and bool (N, npairs): u satisfies kind (0,a,b)."""
    N, p = W.shape
    P = pairs(p)
    G = np.zeros((N, len(P)), bool)
    for k, (a, b) in enumerate(P):
        Wa = np.roll(W, -a, axis=1); Wb = np.roll(W, -b, axis=1)
        const = ((W == Wa) & (W == Wb)).any(axis=1)
        G[:, k] = ~const
    return P, G

def triples(p, gp):
    return [(r, (r + a) % p, (r + b) % p) for (a, b) in gp for r in range(p)]

def compatible(c, T):
    return all(not (c[i] == c[j] == c[k]) for (i, j, k) in T)

def flippable(c, T, r0):
    for t in T:
        if r0 in t:
            o = [c[x] for x in t if x != r0]
            assert len(o) == 2
            if o[0] == o[1] != c[r0]:
                return False
    return True

def nae_clauses(vs):
    # vs: literals; NAE = not all true, not all false
    return [list(vs), [-v for v in vs]]

def sat_certificate(p, T):
    """search c compatible with c and c^e_0 compatible (r0=0 WLOG by translation invariance of T)."""
    s = Minisat22()
    var = lambda i: i + 1
    for (i, j, k) in T:
        s.add_clause([var(i), var(j), var(k)]); s.add_clause([-var(i), -var(j), -var(k)])
        lits = [(-var(x) if x == 0 else var(x)) for x in (i, j, k)]
        s.add_clause(lits); s.add_clause([-l for l in lits])
    ok = s.solve()
    c = None
    if ok:
        m = s.get_model(); c = tuple(1 if m[i] > 0 else 0 for i in range(p))
    s.delete()
    return c

def certify(u, gp):
    """returns ('none-kind'|'self'|'other'|'NOCERT', c, r0)"""
    p = len(u)
    if not gp:
        return 'no kind', u, 0
    T = triples(p, gp)
    for r0 in range(p):
        if flippable(u, T, r0):
            return 'self', u, r0
    c = sat_certificate(p, T)
    if c is None:
        return 'NOCERT', None, None
    assert compatible(c, T) and flippable(c, T, 0)
    return 'other', c, 0

def gp_of(u):
    p = len(u)
    P, G = good_pairs_batch(np.array([u]))
    return [P[k] for k in range(len(P)) if G[0, k]]
