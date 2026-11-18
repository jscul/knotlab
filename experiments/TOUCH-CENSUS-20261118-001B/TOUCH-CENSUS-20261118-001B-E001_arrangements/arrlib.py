"""Arrangements of touching parity knots and their growth under the fewest counts (TOUCH-CENSUS-20261118-001B).

An arrangement is a connected multigraph on n knots with a size (3 to 5 places) at each knot: the multiplicity of a pair is the
number of distinctions the two knots share, a knot's degree is at most its size, and its other distinctions are open. Two
arrangements are the same when a renaming of the knots carries one to the other (counted once). Growth uses FIRST-KNOT's start
library (the joining rule, the fewest counts, implied parity by GF(2))."""
import itertools
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT / 'experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots'))
import startlib as S  # noqa: E402

F = S.F


def canon(sizes, M):
    n = len(sizes)
    best = None
    for perm in itertools.permutations(range(n)):
        key = (tuple(sizes[perm[i]] for i in range(n)),
               tuple(M[perm[i]][perm[j]] for i in range(n) for j in range(i + 1, n)))
        if best is None or key < best:
            best = key
    return best


def connected(n, M):
    seen, st = {0}, [0]
    while st:
        x = st.pop()
        for y in range(n):
            if M[x][y] and y not in seen:
                seen.add(y)
                st.append(y)
    return len(seen) == n


def automorphisms(key):
    """Renamings of the knots that keep sizes and shared counts."""
    sizes, flat = key
    n = len(sizes)
    pairs = list(itertools.combinations(range(n), 2))
    M = [[0] * n for _ in range(n)]
    for (i, j), m in zip(pairs, flat):
        M[i][j] = M[j][i] = m
    return sum(1 for p in itertools.permutations(range(n))
               if all(sizes[p[i]] == sizes[i] for i in range(n)) and all(M[p[i]][p[j]] == M[i][j] for i, j in pairs))


def arrangements(nmax, smin=3, smax=5, labelled=False):
    """Distinct connected arrangements of 1..nmax knots.  With labelled=True, a dict from each to its number of labelled
    descriptions (knots labelled, places not): n! / |automorphisms|."""
    from math import factorial
    out = set()
    for n in range(1, nmax + 1):
        pairs = list(itertools.combinations(range(n), 2))
        for sizes in itertools.combinations_with_replacement(range(smin, smax + 1), n):
            M = [[0] * n for _ in range(n)]
            deg = [0] * n

            def rec(k):
                if k == len(pairs):
                    if connected(n, M):
                        out.add(canon(sizes, M))
                    return
                i, j = pairs[k]
                for m in range(0, min(sizes[i] - deg[i], sizes[j] - deg[j]) + 1):
                    M[i][j] = M[j][i] = m
                    deg[i] += m
                    deg[j] += m
                    rec(k + 1)
                    deg[i] -= m
                    deg[j] -= m
                M[i][j] = M[j][i] = 0

            rec(0)
    if not labelled:
        return {k: None for k in out}
    return {k: factorial(len(k[0])) // automorphisms(k) for k in out}


def stars_of(key):
    sizes, flat = key
    n = len(sizes)
    stars = [[] for _ in range(n)]
    b = 0
    for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
        for _ in range(m):
            stars[i].append(b)
            stars[j].append(b)
            b += 1
    for i in range(n):
        while len(stars[i]) < sizes[i]:
            stars[i].append(b)
            b += 1
    return stars


def grow_tracked(stars, rounds=30, maxj=6000):
    """Grow under the fewest counts, recording each round's chain-birth classes: offshoots of demand 1 whose parent is not itself
    a chain offshoot, grouped by their demand-1 partner (a sibling pair of births is one class)."""
    births = []

    def rule(P, info, rng):
        ks = F.fewest(P, info, rng)
        byid = {i['j']: i for i in info}
        cls = defaultdict(set)
        for i in info:
            if i['p'] != 1 or i['d'] != 1:
                continue
            j = i['j']
            parent = [x for x in P.owner[P.bits_of[j][0]] if x != j][0]
            if P.parents[parent] == 1 and P.demand_at_birth[parent] == 1:
                continue
            sib = [x for bb in P.bits_of[parent] for x in P.owner[bb] if x not in (parent, j) and x in byid]
            partner = sib[0] if sib else None
            twin = partner in byid and byid[partner]['p'] == 1 and byid[partner]['d'] == 1
            cls[frozenset((j, partner)) if twin else partner].add(j)
        births.append(sorted(len(v) for v in cls.values()))
        return ks

    P = S.from_junctions(stars)
    out = 'alive'
    for _ in range(rounds):
        r = P.step(S.gf2(rule), None)
        if r is None:
            out = 'stall'
            break
        if r['new'] == 0:
            out = 'closed'
            break
        if len(P.bits_of) > maxj:
            out = 'big'
            break
    return P, out, births


def measured_dimension(P, outcome, window=7):
    """0 if closed; k + 1 for the least k whose k-th differences of junctions per round are constant and nonzero over the last
    `window` rounds (k = 0: constant per round); None if a stall or unsettled."""
    if outcome == 'closed':
        return 0
    if outcome == 'stall':
        return None
    w = P.counts_by_round()[1:][-window:]
    if len(w) < window:
        return None
    d = w
    for k in range(0, window - 1):
        if len(set(d)) == 1 and d[0] != 0:
            return k + 1
        d = [d[i + 1] - d[i] for i in range(len(d) - 1)]
    return None
