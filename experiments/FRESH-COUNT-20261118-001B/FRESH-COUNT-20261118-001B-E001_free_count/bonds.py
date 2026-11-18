"""Exact bond distances on small parity presentations, and the threshold reader generalised to any star size.

A presentation is given by its stars (junction -> bits).  Its allowed states are the even assignments at every junction.  The
valid checks are the cuts: for a set U of junctions, the bits with exactly one endpoint in U (a loose bit counts at its one
junction).  A bond is an inclusion-minimal nonzero cut; on these presentations it is the cut of a connected U whose complement,
with the outside end of the loose bits, is connected.  Bond distance of two bits: the least size minus one of a bond of at least
three bits containing both (infinity when none).
"""
import itertools
from collections import defaultdict

INF = 10 ** 9


def graph(stars):
    owner = defaultdict(list)
    for j, S in enumerate(stars):
        for b in S:
            owner[b].append(j)
    n = len(stars)
    adj = [set() for _ in range(n)]
    loose = [False] * n
    for b, js in owner.items():
        if len(js) == 2:
            adj[js[0]].add(js[1])
            adj[js[1]].add(js[0])
        else:
            loose[js[0]] = True
    return owner, adj, loose


def connected_subsets(adj, n, limit=None):
    """All nonempty connected vertex sets, each exactly once, as bitmasks."""
    out = []
    nb = [0] * n
    for v in range(n):
        for u in adj[v]:
            nb[v] |= 1 << u

    def rec(S, ext, X):
        out.append(S)
        if limit is not None and len(out) > limit:
            raise RuntimeError('too many connected sets')
        while ext:
            v = (ext & -ext).bit_length() - 1
            ext &= ext - 1
            vb = 1 << v
            rec(S | vb, (ext | nb[v]) & ~(S | vb) & ~X, X)
            X |= vb

    for v in range(n):
        low = (1 << v) - 1
        rec(1 << v, nb[v] & ~low & ~(1 << v), low)
    return out


def bonds(stars, limit=2_000_000):
    owner, adj, loose = graph(stars)
    n = len(stars)
    has_out = any(loose)
    full = (1 << n) - 1
    nb = [0] * n
    for v in range(n):
        for u in adj[v]:
            nb[v] |= 1 << u
    out_mask = 0
    for v in range(n):
        if loose[v]:
            out_mask |= 1 << v

    def comp_connected(C):
        if C == 0:
            return False
        if has_out:
            # vertices of C must all reach the outside through C
            reach = C & out_mask
            frontier = reach
            while frontier:
                v = (frontier & -frontier).bit_length() - 1
                frontier &= frontier - 1
                new = nb[v] & C & ~reach
                reach |= new
                frontier |= new
            return reach == C
        v = (C & -C).bit_length() - 1
        reach = 1 << v
        frontier = reach
        while frontier:
            w = (frontier & -frontier).bit_length() - 1
            frontier &= frontier - 1
            new = nb[w] & C & ~reach
            reach |= new
            frontier |= new
        return reach == C

    result = set()
    for U in connected_subsets(adj, n, limit):
        C = full & ~U
        if C == 0 and not has_out:
            continue
        if C and not comp_connected(C):
            continue
        if C == 0 and has_out:
            pass  # complement is just the outside end: connected
        cut = []
        for b, js in owner.items():
            inside = sum(1 for j in js if (U >> j) & 1)
            if (len(js) == 1 and inside == 1) or (len(js) == 2 and inside == 1):
                cut.append(b)
        result.add(frozenset(cut))
    return result


def distances(stars, limit=2_000_000):
    allbits = sorted({b for S in stars for b in S})
    d = {}
    for B in bonds(stars, limit):
        if len(B) < 3:
            continue
        s = len(B) - 1
        for e, f in itertools.combinations(sorted(B), 2):
            if d.get((e, f), INF) > s:
                d[(e, f)] = s
    return allbits, d


def maximal_cliques(nodes, adj):
    out = []

    def bk(R, P, X):
        if not P and not X:
            out.append(R)
            return
        piv = max(P | X, key=lambda u: len(adj[u] & P))
        for v in list(P - adj[piv]):
            bk(R | {v}, P & adj[v], X & adj[v])
            P = P - {v}
            X = X | {v}

    bk(set(), set(nodes), set())
    return out


def read_stars(allbits, d, kmax):
    """The threshold reader of BOND-NEXT-JOIN-20261117-001, run with thresholds 3..kmax."""
    stars = []
    for k in range(3, kmax + 1):
        adj = {b: set() for b in allbits}
        for (e, f), s in d.items():
            if s <= k - 1:
                adj[e].add(f)
                adj[f].add(e)
        for S, T in itertools.combinations(stars, 2):
            if S & T and len(S) + len(T) - 2 <= k:
                for e in S - T:
                    for f in T - S:
                        adj[e].discard(f)
                        adj[f].discard(e)
        cl = [frozenset(c) for c in maximal_cliques(allbits, adj) if len(c) >= 3]
        stars = sorted(set(cl), key=sorted)
    return stars
