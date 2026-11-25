"""The census of COPYING-PARTS-20261123-001A (its cpcensus.py, imported unchanged), kept flags under parity, the two
weightings, and an exhaustive canonical form of small structures (deviations 15-17, 24)."""
from __future__ import annotations

import itertools
import math
import random
from functools import lru_cache

from dh_common import cpcensus, knots
import dh_engine as E


@lru_cache(maxsize=None)
def census(nmax=5, nmin=1):
    """[(n, atlas index, loose tuple, stars)] for n = nmin..nmax in cpcensus order."""
    out = []
    for n in range(nmin, nmax + 1):
        for gi, loose in cpcensus.starts(n):
            out.append((n, gi, tuple(loose), cpcensus.stars(gi, loose)))
    return out


def census_stars():
    return [c[3] for c in census()]


def kept_parity(stars):
    S = E.Struct(stars)
    pt = knots.parity_test(E.KS(S, 0))
    return not pt['fail'] and not pt['disagree']


def labelled_weight(n, gi, loose):
    auts = cpcensus.autos(gi)
    k = sum(1 for sg in auts if all(loose[sg[v]] == loose[v] for v in range(n)))
    return math.factorial(n) / k


def six_sample_order():
    """DH 9.3: the shuffle of 0 .. 82,655 by random.Random('DESCENT-HELD-20261125-001|six|v2')."""
    idx = list(range(82656))
    random.Random('DESCENT-HELD-20261125-001|six|v2').shuffle(idx)
    return idx


# ------------------------------------------------------------------------------------------------ canonical forms
def canon_graph(n, edges, loose):
    """Exhaustive canonical form of a simple graph on n <= 6 vertices with a loose count on each vertex."""
    best = None
    E_ = [tuple(e) for e in edges]
    for perm in itertools.permutations(range(n)):
        lo = [0] * n
        for v in range(n):
            lo[perm[v]] = loose[v]
        es = tuple(sorted(tuple(sorted((perm[a], perm[b]))) for a, b in E_))
        key = (tuple(lo), es)
        if best is None or key < best:
            best = key
    return (n,) + best


def census_canon(n, gi, loose):
    return canon_graph(n, cpcensus.edges(gi), list(loose))


def structure_canon(places, holders_in, barred):
    """places: list of knots' distinction lists (one part); holders_in: d -> holders inside the part; barred: set.
    Returns a canonical form when the structure is an allowed start of simple-graph shape with at most 5 knots,
    else (None, reason)."""
    n = len(places)
    if n > 5:
        return None, 'more than five knots'
    loose = [0] * n
    pairs = {}
    for u, P in enumerate(places):
        if len(P) < 3:
            return None, 'a knot of fewer than three places'
        for d in P:
            hs = holders_in[d]
            if d in barred:
                return None, 'a barred distinction'
            if len(hs) == 1:
                loose[u] += 1
            elif len(hs) == 2:
                a, b = sorted(hs)
                if u == a:
                    pairs[(a, b)] = pairs.get((a, b), 0) + 1
            else:
                return None, 'more than two holders'
    if any(v > 1 for v in pairs.values()):
        return None, 'two knots sharing two distinctions'
    # connected
    adj = {u: set() for u in range(n)}
    for a, b in pairs:
        adj[a].add(b); adj[b].add(a)
    seen = {0}
    st = [0]
    while st:
        v = st.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w); st.append(w)
    if len(seen) != n:
        return None, 'not connected'
    return canon_graph(n, list(pairs), loose), None
