"""Cheapest joins: each knot's size = shared + round-1 demand in the joined start + its part's own spare (size - shared - demand
in the part alone), floor 3."""
from pilot import *
from collections import defaultdict, Counter

def demand_of(nk, edges):
    sh = Counter()
    for i, j in edges: sh[i] += 1; sh[j] += 1
    st = stars_from([sh[k] + 1 for k in range(nk)], edges)
    P = S.from_junctions(st)
    gs = P.groups_among(list(range(nk)))
    d = Counter()
    for g in gs:
        for j in g: d[j] += 1
    return [sh[k] for k in range(nk)], [d[k] for k in range(nk)]

def spares(sizes, edges):
    sh, d = demand_of(len(sizes), edges)
    return [s - a - b for s, a, b in zip(sizes, sh, d)]

def joined_sizes(nk, edges, spare):
    sh, d = demand_of(nk, edges)
    return [max(3, sh[k] + d[k] + spare[k]) for k in range(nk)]

def series(sizes, edges, rounds=34, tmax=90, maxj=40000):
    P, out = grow(stars_from(sizes, edges), rounds=rounds, tmax=tmax, maxj=maxj)
    return P.counts_by_round(), out

def describe(c, start=6):
    s = c[start:]
    if len(s) < 12: return None
    L, C = berlekamp_massey(s)
    ok = 2 * L + 2 <= len(s)
    import cmath
    # dominant root by power iteration on companion: use numpy-free root finding via ratio
    ratio = s[-1] / s[-2] if s[-2] else None
    return dict(order=L, coeffs=[str(x) for x in C], settled=ok, ratio=round(ratio, 4) if ratio else None)
