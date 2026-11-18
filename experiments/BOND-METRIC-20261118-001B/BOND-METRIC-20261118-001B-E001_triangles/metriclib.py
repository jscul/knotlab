"""Bond distance and the triangle inequality (BOND-METRIC-20261118-001B).

A set S of distinctions is free when the allowed states take all 2^|S| joint values on it. A bond is a set that is not free while
every set of |S| - 1 of its members is free (K1 to K3 on the projected states). Bond distance b(x, y) is the size of the least bond
holding x and y, minus one, and infinite when no bond holds them. The triangle inequality b(x, z) <= b(x, y) + b(y, z) is checked
on every triple, an infinite left side against a finite right side counting as a failure.

A law is a three-place relation, a set of allowed patterns p (bit i of p is the value at the law's place i). A knot places a law on
three distinctions in order."""
import itertools
import math

import numpy as np

P0 = frozenset([0b000, 0b011, 0b101, 0b110])          # parity, even
P1 = frozenset(range(8)) - P0                           # parity, odd
NAE = frozenset(range(1, 7))                            # not all equal
CLAUSE = frozenset(range(7))                            # not all ones
R5 = frozenset([0b000, 0b001, 0b010, 0b100, 0b111])     # not exactly two ones
R6 = frozenset(range(8)) - {0b101, 0b110}               # place 2 is 1 => places 0 and 1 agree


def switch(R, sw):
    return frozenset(p ^ sw for p in R)


def permute(R, perm):
    """The law with its places reordered: new place i reads old place perm[i]."""
    return frozenset(sum((((p >> perm[i]) & 1) << i) for i in range(3)) for p in R)


def orders(R):
    """The distinct relations got by reordering R's places (copies of one law placed in any order)."""
    return sorted({permute(R, perm) for perm in itertools.permutations(range(3))}, key=sorted)


BETWEEN = [switch(NAE, 1 << i) for i in range(3)]       # forbid a pattern with one place differing, and its complement
PNB = [P0, P1, NAE] + BETWEEN                           # the program's six laws


def k2_laws():
    """Every three-place relation passing K1 and K2 (some pattern missing, every pair of places free): 34 of them."""
    out = []
    for mask in range(1, 255):
        R = frozenset(p for p in range(8) if mask >> p & 1)
        if all(len({((p >> i) & 1, (p >> j) & 1) for p in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def language(R):
    """Canonical form of R under reordering places and switching every value at once: a base built from copies of R (placed in any
    order) has the bonds of the same base built from copies of R with every value switched. The 34 laws form 9 languages."""
    return min(tuple(sorted(r)) for perm in itertools.permutations(range(3)) for r in (permute(R, perm), switch(permute(R, perm), 7)))


# one representative of each language; a single-place switch is a different language (switching one distinction is a symmetry of
# a base, not of a law, since a distinction may sit in different places of different knots)
LANGUAGES = {"parity": P0, "NAE": NAE, "betweenness": switch(NAE, 4), "clause": CLAUSE, "clause-twisted": switch(CLAUSE, 1),
             "R5": R5, "R5-twisted": switch(R5, 1), "R6": R6, "R6-twisted": switch(R6, 1)}


def law_class(R):
    """Canonical form of R under reordering places and switching values."""
    return min(tuple(sorted(switch(permute(R, perm), sw))) for perm in itertools.permutations(range(3)) for sw in range(8))


def states(n, knots):
    """Allowed states (as integers, bit v = distinction v) of knots [(law, (a, b, c)), ...] on n distinctions."""
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for R, (a, b, c) in knots:
        pat = ((s >> a) & 1) | (((s >> b) & 1) << 1) | (((s >> c) & 1) << 2)
        allowed = np.zeros(8, dtype=bool)
        allowed[list(R)] = True
        ok &= allowed[pat]
    return s[ok]


def free_table(n, st):
    """free[m] for every set m of distinctions (a bit mask)."""
    free = np.zeros(1 << n, dtype=bool)
    for m in range(1 << n):
        free[m] = len(np.unique(st & m)) == (1 << bin(m).count("1"))
    return free


def bonds(n, free):
    return [m for m in range(1, 1 << n) if not free[m] and all(free[m & ~(1 << i)] for i in range(n) if m >> i & 1)]


def bond_matrix(n, st):
    """b[x][y] = least bond holding x and y, minus one (math.inf when none)."""
    free = free_table(n, st)
    D = [[math.inf] * n for _ in range(n)]
    for m in bonds(n, free):
        k = bin(m).count("1")
        vs = [i for i in range(n) if m >> i & 1]
        for x, y in itertools.combinations(vs, 2):
            if k - 1 < D[x][y]:
                D[x][y] = D[y][x] = k - 1
    return D


def violations(D, n, shift=0):
    """Triples (x, y, z), x < z, y the middle, with D[x][z] - shift > (D[x][y] - shift) + (D[y][z] - shift)."""
    out = []
    for x, z in itertools.combinations(range(n), 2):
        for y in range(n):
            if y in (x, z):
                continue
            left, right = D[x][z] - shift, (D[x][y] - shift) + (D[y][z] - shift)
            if left > right + 1e-9:
                out.append((x, y, z, D[x][y], D[y][z], D[x][z]))
    return out


def correlated(st, x, y):
    """Exact test of a nonzero correlation of the spins of x and y under the uniform weighting on the allowed states:
    N * sum(s_x s_y) != sum(s_x) * sum(s_y), in integers."""
    sx = 1 - 2 * ((st >> x) & 1)
    sy = 1 - 2 * ((st >> y) & 1)
    return int(len(st)) * int(np.sum(sx * sy)) != int(np.sum(sx)) * int(np.sum(sy))


def correlation(st, x, y):
    sx = 1 - 2 * ((st >> x) & 1)
    sy = 1 - 2 * ((st >> y) & 1)
    return float(np.mean(sx * sy) - np.mean(sx) * np.mean(sy))


def meet_at_most_once(triples):
    return all(len(set(a) & set(b)) <= 1 for a, b in itertools.combinations(triples, 2))


def covers(triples, n):
    return len({v for t in triples for v in t}) == n


def shortest_ring(triples):
    """Least number of knots in a ring of knots (consecutive knots share a distinction, a different one each time; the
    literature's hypergraph girth for linear systems), or None for a forest; two knots sharing two distinctions count as a ring of 2."""
    import networkx as nx
    G = nx.Graph()
    for i, t in enumerate(triples):
        for v in t:
            G.add_edge(("k", i), ("v", v))
    if nx.is_forest(G):
        return None
    return min(len(c) for c in nx.minimum_cycle_basis(G)) // 2
