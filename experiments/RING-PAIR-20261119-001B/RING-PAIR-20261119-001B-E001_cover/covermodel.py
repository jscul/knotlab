"""The cover model of the cheapest parity growth (RING-PAIR-20261119-001B).

Model H.  Take a bare start (each knot max(3, shared + round-1 demand) places, plus listed surplus distinctions; joinlib of
JOIN-GROWTH-20261118-001B).  Its candidate complex X has the knots as vertices; for every knot w, the knots sharing a distinction
with w (its neighbours N(w)) are pairwise candidates through w, and X holds the full simplex on N(w) (a block); each listed surplus
distinction at a knot r adds a new vertex joined to r alone (a block of two).  The universal cover of X is a tree of these blocks.
H says: the junctions made in round t are the deck orbits of the finite connected vertex sets of size t + 1 of the cover that
contain a knot.

Scope (where H is claimed): every knot has shared + round-1 demand >= 3 (no distinction from the floor of three places); every
listed surplus distinction sits on a knot of round-1 demand >= 2; round 1 has no group of three or more; no two knots have two
common neighbours.  Outside it the floor's distinctions renew and nest (JOIN-GROWTH-20261118-001's laws), and H is not claimed.

Counting.  For a block B entered at its vertex z, U(B, z) = y prod_{B' at z, B' != B} Phi(B', z), with
Phi(B, z) = prod_{w in B, w != z} (1 + U(B, w)); the orbit series is, by the dissymmetry of block trees,
C(y) = sum_x y prod_{B at x} Phi(B, x) - sum_B sum_{S subset B, |S| >= 2} (|S| - 1) prod_{v in S} U(B, v) = sum_t c(t) y^(t+1).
The system is polynomial with positive coefficients, so C is algebraic (rational when X has at most one independent cycle)."""
import itertools
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins'))
import joinlib as J  # noqa: E402


def in_scope(n, edges, surplus=None):
    surplus = surplus or {}
    sh, d = J.shared_and_demand(n, edges)
    if any(sh[k] + d[k] < 3 for k in range(n)):
        return False, 'a distinction from the floor'
    if any(d[int(k)] < 2 for k, v in surplus.items() if v):
        return False, 'surplus at a knot of demand below 2'
    P = J.S.from_junctions(J.stars_from(J.bare_sizes(n, edges, surplus), edges))
    if any(len(g) > 2 for g in P.groups_among(list(range(n)))):
        return False, 'a group of three in round 1'
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    if any(len(nb[a] & nb[b]) >= 2 for a, b in itertools.combinations(range(n), 2)):
        return False, 'two common neighbours'
    return True, ''


def blocks_of(n, edges, surplus=None):
    """Vertex count and blocks of the candidate complex (one full simplex per knot's neighbours; a pendant block per surplus)."""
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    B = [tuple(sorted(nb[w])) for w in range(n) if len(nb[w]) >= 2]
    k = n
    for r, v in sorted((int(a), b) for a, b in (surplus or {}).items()):
        for _ in range(v):
            B.append((r, k))
            k += 1
    return k, B


# -- exact series (integers) --------------------------------------------------------------------------------------------------------
def _mul(a, b, N):
    out = [0] * (N + 1)
    for i, x in enumerate(a):
        if x:
            for j in range(N + 1 - i):
                if b[j]:
                    out[i + j] += x * b[j]
    return out


def series(nv, blocks, N, knots):
    """c(0..N-1) of H; `knots` is the number of knot vertices (the rest are surplus vertices, whose singletons are not junctions)."""
    one = [1] + [0] * N
    at = defaultdict(list)
    for i, B in enumerate(blocks):
        for z in B:
            at[z].append(i)
    U = {(i, z): [0] * (N + 1) for i, B in enumerate(blocks) for z in B}

    def phi(i, z):
        r = one
        for w in blocks[i]:
            if w != z:
                r = _mul(r, [a + b for a, b in zip(one, U[(i, w)])], N)
        return r
    for _ in range(N + 1):
        new = {}
        for (i, z) in U:
            r = one
            for j in at[z]:
                if j != i:
                    r = _mul(r, phi(j, z), N)
            new[(i, z)] = [0] + r[:N]
        if new == U:
            break
        U = new
    C = [0] * (N + 1)
    for x in range(nv):
        r = one
        for i in at[x]:
            r = _mul(r, phi(i, x), N)
        C = [a + b for a, b in zip(C, [0] + r[:N])]
    for i, B in enumerate(blocks):
        for m in range(2, len(B) + 1):
            for S in itertools.combinations(B, m):
                pr = one
                for v in S:
                    pr = _mul(pr, U[(i, v)], N)
                C = [a - (m - 1) * b for a, b in zip(C, pr)]
    c = C[1:]
    c[0] -= nv - knots
    return c


def model_counts(n, edges, surplus, N):
    nv, B = blocks_of(n, edges, surplus)
    return series(nv, B, N, n)


# -- the radius of convergence --------------------------------------------------------------------------------------------------------
def rho(blocks, iters=20000, steps=50):
    """The largest y at which the fixed-point iteration of the system from 0 stays bounded (the series' radius); rate = 1/rho."""
    at = defaultdict(list)
    for i, B in enumerate(blocks):
        for z in B:
            at[z].append(i)
    keys = [(i, z) for i, B in enumerate(blocks) for z in B]

    def bounded(y):
        u = {k: 0.0 for k in keys}
        for _ in range(iters):
            v = {}
            for (i, z) in keys:
                r = 1.0
                for j in at[z]:
                    if j != i:
                        for w in blocks[j]:
                            if w != z:
                                r *= 1.0 + u[(j, w)]
                v[(i, z)] = y * r
            m = max(v.values())
            if m != m or m > 1e8:
                return False
            if max(abs(v[k] - u[k]) for k in keys) < 1e-13:
                return True
            u = v
        return True
    lo, hi = 0.0, 1.0
    for _ in range(steps):
        mid = (lo + hi) / 2
        if bounded(mid):
            lo = mid
        else:
            hi = mid
    return lo
