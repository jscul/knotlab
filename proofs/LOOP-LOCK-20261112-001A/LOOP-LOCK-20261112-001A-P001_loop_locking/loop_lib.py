"""Which loops lock (research/LOOP-LOCK-20261112-001/preregistration.md, ticket A).

Endless blocks stitched in one order (ENDLESS-BLOCK-20261112-001): each distinction of a pattern is a copy of a harmony H on Z_P, and each
knot (x, y, z) binds NAE((x, i), (y, i + a), (z, i + b)) for every kind (0, a, b) of H and every i. R is the one-knot relation on H's
states, and the step relation T(u, w) holds when some state v has R(u, v, w)."""
import itertools
import sys
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/ENDLESS-BLOCK-20261112-001A/ENDLESS-BLOCK-20261112-001A-P001_endless_blocks"))
import endless_lib as E  # noqa: E402


def as_int(w):
    return sum(b << i for i, b in enumerate(w))


def rot(x, s, P):
    """the word read from place s: bit i of the result is bit (i + s) of x"""
    s %= P
    mask = (1 << P) - 1
    return ((x >> s) | (x << (P - s))) & mask


def relation(h):
    """R as a set of index triples over H's states, and T as a set of index pairs"""
    P = h["P"]
    W = [as_int(w) for w in E.N.states(h)]
    mask = (1 << P) - 1
    kinds = [(a, b) for (_, a, b) in h["kinds"]]
    R = set()
    for iu, u in enumerate(W):
        for iv, v in enumerate(W):
            shifted_v = [rot(v, a, P) for (a, b) in kinds]
            for iw, w in enumerate(W):
                ok = True
                for (a, b), va in zip(kinds, shifted_v):
                    wb = rot(w, b, P)
                    if (u & va & wb) | (~u & ~va & ~wb & mask):
                        ok = False
                        break
                if ok:
                    R.add((iu, iv, iw))
    T = {(u, w) for (u, v, w) in R}
    return W, R, T


def loopless_girth(T, n):
    """the length of the shortest directed cycle of T without its loops (None if there is none)"""
    adj = {u: [w for (x, w) in T if x == u and w != u] for u in range(n)}
    best = None
    for s in range(n):
        dist = {s: 0}
        frontier = [s]
        while frontier:
            nxt = []
            for u in frontier:
                for w in adj[u]:
                    if w == s:
                        c = dist[u] + 1
                        best = c if best is None else min(best, c)
                    elif w not in dist:
                        dist[w] = dist[u] + 1
                        nxt.append(w)
            frontier = nxt
    return best


def locked(Ppat, h, groups):
    """for each group of copies, whether every copy in it equals the group's first copy, place by place, in every state"""
    cl, nv, var = E.build(Ppat, h, "one order")
    P = h["P"]
    out = []
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        if not s.solve():
            return None
        for g in groups:
            aux = []
            extra = []
            nxt = nv + 1
            for c in g[1:]:
                for i in range(P):
                    y = nxt
                    nxt += 1
                    a, b = var(g[0], i), var(c, i)
                    extra += [[-y, a, b], [-y, -a, -b]]
                    aux.append(y)
            if not aux:
                out.append(True)
                continue
            with Solver(name="cadical153", bootstrap_with=cl + extra + [aux]) as s2:
                out.append(not s2.solve())
    return out


def tied_to_root(Ppat, h, root=0):
    """the copies equal to the root copy, place by place, in every state"""
    n = Ppat[0]
    res = locked(Ppat, h, [[root, c] for c in range(n) if c != root])
    if res is None:
        return None
    return [c for c, r in zip([c for c in range(n) if c != root], res) if r]


def figure_eight(k1, k2):
    """two closed chains through one shared distinction 0: loop A has shared 0, 2, ..., loop B shares 0"""
    knots, n = [], 1
    A = [0]
    for j in range(k1 - 1):
        A.append(n + 1); n += 2
    knots_A = []
    shared_A = A
    for j in range(k1):
        p = n; n += 1
        knots_A.append((shared_A[j], p, shared_A[(j + 1) % k1]))
    B = [0]
    for j in range(k2 - 1):
        B.append(n); n += 1
    knots_B = []
    for j in range(k2):
        p = n; n += 1
        knots_B.append((B[j], p, B[(j + 1) % k2]))
    # renumber densely
    used = sorted({x for k in knots_A + knots_B for x in k})
    mp = {x: i for i, x in enumerate(used)}
    return (len(used), [tuple(mp[x] for x in k) for k in knots_A + knots_B]), [mp[x] for x in shared_A], [mp[x] for x in B]


def theta(k, m):
    """two loops sharing one knot: loop A has k knots on shared s_0 .. s_(k-1); loop B shares A's first knot (s_0, p_0, s_1) and returns
    from s_1 to s_0 by m - 1 knots of its own (oriented the same way round)"""
    labels = {}
    nxt = [0]

    def new():
        nxt[0] += 1
        return nxt[0] - 1
    sA = [new() for _ in range(k)]
    knots = []
    for j in range(k):
        knots.append((sA[j], new(), sA[(j + 1) % k]))
    sB = [sA[1]] + [new() for _ in range(m - 2)] + [sA[0]]
    for j in range(m - 1):
        knots.append((sB[j], new(), sB[j + 1]))
    return (nxt[0], knots), sA, sB


def path_knots(seq, new):
    """knots (seq[j], hanging, seq[j+1]) along a sequence of shared distinctions, each with a fresh hanging copy"""
    return [(seq[j], new(), seq[j + 1]) for j in range(len(seq) - 1)]


def crossed():
    """two loops sharing two copies x, y and no knot (the advisor's): loop 1 goes x -> y in 1 knot and back in 3; loop 2 goes x -> y in 3
    knots and back in 1. Returns the pattern and the shared copies of each loop."""
    c = [0]

    def new():
        c[0] += 1
        return c[0] - 1
    x, y = new(), new()
    a1, a2 = new(), new()
    b1, b2 = new(), new()
    k = []
    k += path_knots([x, y], new) + path_knots([y, a1, a2, x], new)
    k += path_knots([x, b1, b2, y], new) + path_knots([y, x], new)
    return (c[0], k), [x, y, a1, a2], [x, y, b1, b2]


def circulant(n):
    """n shared copies; loop A steps i -> i + 1, loop B steps i -> i + 2, each knot with a fresh hanging copy"""
    c = [n]

    def new():
        c[0] += 1
        return c[0] - 1
    A = [(i, new(), (i + 1) % n) for i in range(n)]
    B = [(i, new(), (i + 2) % n) for i in range(n)]
    return (c[0], A + B), list(range(n)), A, B


def tie_classes(Ppat, h, copies):
    """classes of the given copies equal to one another, place by place, in every state (None if no state)"""
    classes = []
    for c in copies:
        placed = False
        for cl in classes:
            r = locked(Ppat, h, [[cl[0], c]])
            if r is None:
                return None
            if r[0]:
                cl.append(c)
                placed = True
                break
        if not placed:
            classes.append([c])
    return classes
