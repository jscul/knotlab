"""States-only readings (STATES-GROWTH-20261119-001B).

`nae_core(n, states)`: the minimal not-all-equal constraints the allowed states satisfy: the sets S of distinctions on which no
allowed state is constant, minimal under inclusion (validity is closed upward, so S is minimal when every set one smaller fails).
Searched up to `kmax` places.  `canonical(n, states)`: that set as a presentation (junction -> distinctions), with its distinctions'
multiplicities (how many minimal constraints hold each)."""
import itertools

import numpy as np


def nae_core(n, st, kmax=7):
    bits = [((st >> b) & 1).astype(np.int8) for b in range(n)]
    valid = {}
    core = []
    for k in range(2, kmax + 1):
        for S in itertools.combinations(range(n), k):
            subs = [tuple(x for x in S if x != y) for y in S]
            if k > 2 and any(valid.get(t, False) for t in subs):
                valid[S] = True                  # a superset of a valid set: valid, not minimal
                continue
            tot = np.zeros(len(st), dtype=np.int16)
            for b in S:
                tot += bits[b]
            v = not bool(np.any((tot == 0) | (tot == k)))
            valid[S] = v
            if v:
                core.append(S)
    return core


def multiplicity(n, core):
    m = [0] * n
    for S in core:
        for b in S:
            m[b] += 1
    return m


def verdict(stars, core):
    """'saturated' (the minimal constraints are the presentation), 'sharpened' (they differ but are an admissible presentation:
    every member of three places or more, every distinction in at most two), or 'undefined'."""
    P = sorted(tuple(sorted(x)) for x in stars)        # with repeats: a duplicated junction is not saturated
    if P == sorted(core):
        return 'saturated'
    held = {}
    for S in core:
        for b in S:
            held[b] = held.get(b, 0) + 1
    if all(len(S) >= 3 for S in core) and all(v <= 2 for v in held.values()):
        return 'sharpened'
    return 'undefined'
