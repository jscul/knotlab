"""Bond distance by brute force on small presentations, under either law (NAE-GROWTH-20261119-001B, part B).

A presentation is its stars (junction -> bits).  Its allowed states are the assignments that pass every junction: even parity, or
not all equal.  A set of bits is free when the allowed states take every pattern on it; a bond is a set that is not free while
every proper subset is (BOND-METRIC's definition, read from the allowed states alone).  Bond distance of two bits: the least size
of a bond holding both, minus one.  Only bonds of at most `kmax` bits are searched; a pair in none gets `kmax` (pooled).
"""
import itertools

import numpy as np


def states(n, stars, law):
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for S in stars:
        c = np.zeros(1 << n, dtype=np.int64)
        for b in S:
            c += (s >> b) & 1
        ok &= (c % 2 == 0) if law == 'parity' else ((c != 0) & (c != len(S)))
    return s[ok]


def table(n, st, kmax=7):
    """{(x, y): least bond size - 1} for x < y, bonds of at most kmax bits; pairs in none get kmax."""
    bits = [(st >> b) & 1 for b in range(n)]
    free = {0: True}
    D = {}
    for k in range(1, kmax + 1):
        for comb in itertools.combinations(range(n), k):
            m = 0
            for b in comb:
                m |= 1 << b
            subs = [m & ~(1 << b) for b in comb]
            if not all(free.get(x, False) for x in subs):
                free[m] = False          # holds a smaller bond: not free, not minimal
                continue
            idx = np.zeros(len(st), dtype=np.int64)
            for i, b in enumerate(comb):
                idx |= bits[b] << i
            f = np.unique(idx).size == (1 << k)
            free[m] = f
            if not f:
                for x, y in itertools.combinations(comb, 2):
                    D.setdefault((x, y), k - 1)
    return {(x, y): D.get((x, y), kmax) for x, y in itertools.combinations(range(n), 2)}
