"""Referee R1 for THREE-WAY-20261119-001: the referee's own three-way readings, forcing with triples, and exact search for a
renaming that keeps both readings.  Built on the referee's earlier code (bonds: UNIQUE-TABLE-R1's closed-aware enumeration; pair
tables: CENSUS-READ-R1's shore table; growth: FRESH-COUNT-R1 / FIRST-KNOT-R1); no study code imported.

Readings.  A bond is a cut of the junction graph with both sides connected (closed-aware), and its word is the set of distinctions
it crosses; bonds are the circuits of the equation space.  The pair reading of x, y is the least bond holding both (the table, K);
the three-way reading of x, y, z is the least bond holding all three, or None.  (Sizes, not sizes less one: one shift throughout.)
"""
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1", "research/UNIQUE-TABLE-20261119-001/referee-R1",
          "research/GROWN-PAIR-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
INF_SIZE = 10 ** 6


def relabel(stars):
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    return [sorted(idx[b] for b in s) for s in stars], len(labels)


def stage(key, rnd):
    import referee_first as RFK
    import referee_census as RC
    G = RFK.Start(RC.stars_of(tuple(map(tuple, key))))
    for _ in range(rnd):
        if G.step(RFK.fewest, None, None) != "ok":
            return None
    return [sorted(s) for s in G.bits]


def readings(stars, nb):
    """stars on 0..nb-1.  Returns (bonds sorted by size, K as nested lists of sizes, T: triple -> size or None)."""
    from samecode import minimal_words
    bonds = sorted(minimal_words(stars), key=lambda w: (w.bit_count(), w))
    K = [[INF_SIZE] * nb for _ in range(nb)]
    for x in range(nb):
        K[x][x] = 0
    T = {}
    for t in combinations(range(nb), 3):
        T[t] = None
    left_pairs = {(x, y) for x, y in combinations(range(nb), 2)}
    left_triples = set(T)
    for w in bonds:
        if not left_pairs and not left_triples:
            break
        s = w.bit_count()
        bits = [x for x in range(nb) if w >> x & 1]
        for p in combinations(bits, 2):
            if p in left_pairs:
                K[p[0]][p[1]] = K[p[1]][p[0]] = s
                left_pairs.discard(p)
        if left_triples:
            for t in combinations(bits, 3):
                if t in left_triples:
                    T[t] = s
                    left_triples.discard(t)
    return bonds, K, T


def span(words):
    basis = {}
    for r in words:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return basis


def in_span(basis, r):
    while r:
        p = r.bit_length() - 1
        if p not in basis:
            return False
        r ^= basis[p]
    return True


def iso_both(KA, KB, TA, TB, nb, cap=5000000):
    """Exact: is there a bijection of distinctions carrying K_A onto K_B and T_A onto T_B?  True / False / None (cap)."""
    rowA = [sorted(r) for r in KA]
    rowB = [sorted(r) for r in KB]
    tcA = [sorted((v if v is not None else -1) for t, v in TA.items() if x in t) for x in range(nb)]
    tcB = [sorted((v if v is not None else -1) for t, v in TB.items() if y in t) for y in range(nb)]
    cand = {x: [y for y in range(nb) if rowA[x] == rowB[y] and tcA[x] == tcB[y]] for x in range(nb)}
    if any(not c for c in cand.values()):
        return False
    order = sorted(range(nb), key=lambda x: len(cand[x]))
    img, used, steps = {}, set(), [0]

    def tri(T, a, b, c):
        return T[tuple(sorted((a, b, c)))]

    def go(k):
        steps[0] += 1
        if steps[0] > cap:
            return None
        if k == nb:
            return True
        x = order[k]
        done = order[:k]
        for y in cand[x]:
            if y in used or any(KA[x][z] != KB[y][img[z]] for z in done):
                continue
            if any(tri(TA, x, z1, z2) != tri(TB, y, img[z1], img[z2]) for z1, z2 in combinations(done, 2)):
                continue
            img[x] = y
            used.add(y)
            r = go(k + 1)
            if r:
                return True
            del img[x]
            used.discard(y)
            if r is None:
                return None
        return False
    return go(0)


def forcing(stars, nb, K, T, smax=None):
    """The referee's forcing with pairs and triples.  Every code with these readings has, for each pair (triple) read s, a least
    circuit of size s holding it; that circuit is an s-set all of whose pairs and triples read at most s.  A candidate is dropped
    when it is strictly comparable with a forced word, or when some nonzero word of its span with the forced words is lighter than
    the least circuit through any of its distinctions (every nonzero word of a binary code contains a circuit).  A key with one candidate left forces it.  Sizes up to smax (default: the largest junction).  Returns the forced
    words and whether they span the stage's equation space."""
    smax = smax or max(map(len, stars))
    m = [min(K[x][y] for y in range(nb) if y != x) for x in range(nb)]
    cands = {}

    def sets_of(s):
        if s in cands:
            return cands[s]
        adj = [{y for y in range(nb) if y != x and K[x][y] <= s} for x in range(nb)]
        out = []

        def ext(cur, pool):
            if len(cur) == s:
                if all(T[t] is not None and T[t] <= s for t in combinations(cur, 3)):
                    out.append(sum(1 << x for x in cur))
                return
            for y in sorted(pool):
                if y > cur[-1]:
                    ext(cur + [y], pool & adj[y])
        for x in range(nb):
            ext([x], adj[x])
        cands[s] = out
        return out
    keys = [(sum(1 << x for x in p), K[p[0]][p[1]]) for p in combinations(range(nb), 2) if 3 <= K[p[0]][p[1]] <= smax]
    keys += [(sum(1 << x for x in t), v) for t, v in T.items() if v is not None and 3 <= v <= smax]
    forced, dead = [], set()
    while True:
        Fb = span(forced)
        Fspan = [0]
        for b in Fb.values():
            Fspan = Fspan + [v ^ b for v in Fspan]
        new = []
        for need, s in keys:
            alive = []
            for w in sets_of(s):
                if w & need != need or w in dead:
                    continue
                if w not in forced:
                    if any(f != w and (f & w in (f, w)) for f in forced):
                        dead.add(w)
                        continue
                    light = False
                    for f in Fspan:
                        v = w ^ f
                        if v and v.bit_count() < min(m[x] for x in range(nb) if v >> x & 1):
                            light = True
                            break
                    if light:
                        dead.add(w)
                        continue
                alive.append(w)
            if len(alive) == 1 and alive[0] not in forced and alive[0] not in new:
                new.append(alive[0])
        if not new:
            break
        forced += new
    C = span(sum(1 << x for x in s) for s in stars)
    spans = len(span(forced)) == len(C) and all(in_span(C, f) for f in forced)
    return forced, spans
