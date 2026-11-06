"""Circuits as bitmasks and the elimination closure up to ties, for SPLICE-TREE-20261102-001C.

A circuit is a minimal constrained set of a solution set (glue_lib.circuits); here every set of points is a bitmask. Two points form a
tie when they make a two-element circuit; a knot (a circuit of three or more points) never holds two tied points, since the tie
would be a smaller constrained subset, so replacing every point by its tie class keeps a knot's size.

The closure of a base set of knots (as tie classes) adds (A | B) minus one class shared by A and B whenever that is again a knot. To
produce T this way, A and B must lie inside T plus the eliminated class and so are no larger than T; by induction a derivation of T
never uses a knot larger than T. Hence a closure computed with circuits up to a size bound is exact for every knot within the bound."""
import itertools

import numpy as np


def circuits(sol, n, maxsize=None, batch=4096):
    """the minimal constrained sets of a list of 0/1 assignments, as bitmasks (same sets as glue_lib.circuits)"""
    arr = np.array(sol, dtype=np.int64)
    codes = (arr * (np.int64(1) << np.arange(n, dtype=np.int64))).sum(axis=1)
    free = sum(1 << v for v in range(n) if len(np.unique(arr[:, v])) == 2)
    allm = np.arange(1 << n, dtype=np.int64)
    size = np.zeros(1 << n, dtype=np.int16)
    free_size = np.zeros(1 << n, dtype=np.int16)
    for b in range(n):
        bit = ((allm >> b) & 1).astype(np.int16)
        size += bit
        if free >> b & 1:
            free_size += bit
    constrained = np.zeros(1 << n, dtype=bool)
    found = []
    for r in range(1, (maxsize or n) + 1):
        masks = allm[size == r]
        inherited = np.zeros(len(masks), dtype=bool)
        for b in range(n):
            has = ((masks >> b) & 1) == 1
            inherited[has] |= constrained[masks[has] ^ (1 << b)]
        constrained[masks[inherited]] = True
        cand = masks[~inherited]
        for i in range(0, len(cand), batch):
            bm = cand[i:i + batch]
            proj = codes[:, None] & bm[None, :]
            proj.sort(axis=0)
            distinct = 1 + (np.diff(proj, axis=0) != 0).sum(axis=0)
            hit = bm[distinct < (np.int64(1) << free_size[bm].astype(np.int64))]
            constrained[hit] = True
            found.extend(int(m) for m in hit)
    return found


def bits(m):
    out = []
    while m:
        low = m & -m
        out.append(low.bit_length() - 1)
        m ^= low
    return out


def tie_classes(n, ties):
    """each point's class representative (the least point tied to it)"""
    rep = list(range(n))

    def find(v):
        while rep[v] != v:
            rep[v] = rep[rep[v]]
            v = rep[v]
        return v
    for t in ties:
        a, b = (find(v) for v in bits(t))
        if a != b:
            rep[max(a, b)] = min(a, b)
    return [find(v) for v in range(n)]


def canon(m, rep):
    out = 0
    for v in bits(m):
        out |= 1 << rep[v]
    return out


def closure(knots, base, n):
    """the least set containing base and closed under eliminations that land in knots (all as class bitmasks), computed per target:
    T joins when some class h outside T has two members A, B of the set inside T | h, both through h, with A | B = T | h"""
    gen = set(base)
    targets = sorted(set(knots) - gen)
    while targets:
        arr = np.array(sorted(gen), dtype=np.int64)
        through = [arr[((arr >> h) & 1) == 1] for h in range(n)]
        added, kept = [], []
        for T in targets:
            ok = False
            for h in range(n):
                if T >> h & 1 or len(through[h]) < 2:
                    continue
                goal = T | (1 << h)
                inside = through[h][(through[h] & ~goal) == 0].tolist()
                if any(A | B == goal for A, B in itertools.combinations(inside, 2)):
                    ok = True
                    break
            (added if ok else kept).append(T)
        if not added:
            break
        gen.update(added)
        targets = kept
    return gen


def closure_forward(knots, base):
    """the same closure by forward elimination of every pair through every shared class (for cross-checking)"""
    gen = set(base)
    frontier = list(gen)
    while frontier:
        new = []
        for A in frontier:
            for B in list(gen):
                shared = A & B
                while shared:
                    h = shared & -shared
                    shared ^= h
                    c = (A | B) & ~h
                    if c in knots and c not in gen:
                        gen.add(c)
                        new.append(c)
        frontier = new
    return gen
