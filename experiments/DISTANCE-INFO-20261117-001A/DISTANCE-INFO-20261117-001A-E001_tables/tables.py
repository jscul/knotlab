"""Bond-distance tables of not-all-equal bases (DISTANCE-INFO-20261117-001).

A base is a set of not-all-equal knots (three distinct distinctions each) on
n labelled distinctions that allows at least one state; its relation is the
set of allowed states, kept as an integer bit mask over the 2^n states.  A
bond is a set B of at least two distinctions on which the allowed states,
with every other distinction forgotten, form a knot: not every joint state of
B occurs, and forgetting any one member of B leaves the rest free.  The bond
distance of two distinctions is the size of the smallest bond containing both,
minus one (glossary), or infinity (0 here, written None) when no bond holds
them.  The table is the matrix of bond distances over all pairs.
"""

import itertools


def knot_mask(n, t):
    m = 0
    a, b, c = t
    for s in range(1 << n):
        x, y, z = s >> a & 1, s >> b & 1, s >> c & 1
        if not (x == y == z):
            m |= 1 << s
    return m


def all_knots(n):
    return list(itertools.combinations(range(n), 3))


def distinct_relations(n, max_count=None):
    """Every relation an NAE knot set on n distinctions allows (nonempty), by
    closure: start from the full relation and intersect with knots."""
    full = (1 << (1 << n)) - 1
    masks = [knot_mask(n, t) for t in all_knots(n)]
    seen = {full}
    frontier = [full]
    while frontier:
        nxt = []
        for r in frontier:
            for km in masks:
                q = r & km
                if q and q not in seen:
                    seen.add(q)
                    nxt.append(q)
                    if max_count and len(seen) > max_count:
                        raise RuntimeError("too many relations")
        frontier = nxt
    return seen


def states_of(n, rel):
    return [s for s in range(1 << n) if rel >> s & 1]


def projection(n, sts, B):
    return {tuple(s >> i & 1 for i in B) for s in sts}


def is_bond(n, sts, B):
    k = len(B)
    proj = projection(n, sts, B)
    if len(proj) == 1 << k:
        return False
    for drop in range(k):
        sub = B[:drop] + B[drop + 1:]
        if len({tuple(x[j] for j in range(k) if j != drop) for x in proj}) != 1 << (k - 1):
            return False
    return True


def bond_table(n, rel, signed=False):
    """Bond distance of every pair (u < v); with signed=True a bond of size two
    also records whether the pair is equal (+) or unequal (-)."""
    sts = states_of(n, rel)
    table = []
    for u, v in itertools.combinations(range(n), 2):
        rest = [i for i in range(n) if i not in (u, v)]
        d = None
        for size in range(0, n - 1):
            found = False
            for extra in itertools.combinations(rest, size):
                B = tuple(sorted((u, v) + extra))
                if is_bond(n, sts, B):
                    found = True
                    break
            if found:
                d = size + 1
                break
        if signed and d == 1:
            pr = projection(n, sts, (u, v))
            d = "1=" if (0, 0) in pr else "1≠"
        table.append(d)
    return tuple(table)


def bond_set(n, rel):
    """Every bond of the relation, each as a sorted tuple of distinctions."""
    sts = states_of(n, rel)
    out = []
    for k in range(2, n + 1):
        for B in itertools.combinations(range(n), k):
            if is_bond(n, sts, B):
                out.append(B)
    return tuple(out)


def bond_signatures(n, rel):
    """Three readings of the bonds: the bond set alone (c), with the sign of
    every size-two bond (c-s), and with every bond's missing joint states (c')."""
    sts = states_of(n, rel)
    plain, tied, full = [], [], []
    for k in range(2, n + 1):
        for B in itertools.combinations(range(n), k):
            if is_bond(n, sts, B):
                plain.append(B)
                proj = projection(n, sts, B)
                if k == 2:
                    tied.append((B, "=" if (0, 0) in proj else "≠"))
                else:
                    tied.append((B, None))
                missing = tuple(sorted(set(itertools.product((0, 1), repeat=k)) - proj))
                full.append((B, missing))
    return tuple(plain), tuple(tied), tuple(full)


def prime_implicates(n, rel):
    """Minimal forbidden partial states (control: these determine the relation)."""
    sts = states_of(n, rel)
    out = []
    for k in range(1, n + 1):
        for S in itertools.combinations(range(n), k):
            proj = projection(n, sts, S)
            for pat in itertools.product((0, 1), repeat=k):
                if pat in proj:
                    continue
                minimal = True
                for drop in range(k):
                    sub = S[:drop] + S[drop + 1:]
                    subpat = pat[:drop] + pat[drop + 1:]
                    if sub and subpat not in projection(n, sts, sub):
                        minimal = False
                        break
                if minimal:
                    out.append((S, pat))
    return tuple(out)


def permute(n, rel, perm):
    out = 0
    for s in range(1 << n):
        if rel >> s & 1:
            t = 0
            for i in range(n):
                if s >> i & 1:
                    t |= 1 << perm[i]
            out |= 1 << t
    return out


def isomorphic(n, r1, r2):
    if bin(r1).count("1") != bin(r2).count("1"):
        return False
    return any(permute(n, r1, p) == r2 for p in itertools.permutations(range(n)))
