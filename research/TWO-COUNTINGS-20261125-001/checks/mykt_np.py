"""Checker's knot test in the whole, vectorised (same semantics as mykt.py): states as int64 bitmasks."""
import itertools
import json
import resource
import sys

import numpy as np

resource.setrlimit(resource.RLIMIT_AS, (6 * 1024 ** 3, 6 * 1024 ** 3))


def popcount(x):
    c = np.zeros_like(x)
    y = x.copy()
    while y.any():
        c += y & 1
        y >>= 1
    return c


def allowed(rules):
    remaining = list(range(len(rules)))
    pos = {}
    states = np.zeros(1, dtype=np.int64)
    while remaining:
        best = max(remaining, key=lambda i: (sum(p in pos for p in rules[i][1]), -i))
        remaining.remove(best)
        law, P = rules[best]
        new = [p for p in P if p not in pos]
        for p in new:
            pos[p] = len(pos)
        if new:
            ext = np.zeros(2 ** len(new), dtype=np.int64)
            for e in range(2 ** len(new)):
                for q, p in enumerate(new):
                    if (e >> q) & 1:
                        ext[e] |= np.int64(1) << np.int64(pos[p])
            states = (states[:, None] | ext[None, :]).ravel()
        m = np.int64(0)
        for p in P:
            m |= np.int64(1) << np.int64(pos[p])
        s = popcount(states & m)
        if law == 'even':
            keep = (s % 2) == 0
        elif law == 'odd':
            keep = (s % 2) == 1
        else:
            keep = (s > 0) & (s < len(P))
        states = states[keep]
    return pos, states


def ktest(n, rel):
    rel = set(rel)
    K1 = len(rel) < 2 ** n
    K3 = len(rel) > 0
    K2 = all(len({r[:d] + r[d + 1:] for r in rel}) == 2 ** (n - 1) for d in range(n))
    return K1, K2, K3


def test_structure(rules):
    rules = [(l, tuple(p)) for l, p in rules]
    pos, states = allowed(rules)
    out = []
    for law, P in rules:
        code = np.zeros(len(states), dtype=np.int64)
        for q, p in enumerate(P):
            code |= ((states >> np.int64(pos[p])) & 1) << np.int64(q)
        rel = sorted(tuple((int(c) >> q) & 1 for q in range(len(P))) for c in np.unique(code))
        K1, K2, K3 = ktest(len(P), rel)
        own = [b for b in itertools.product((0, 1), repeat=len(P))
               if (law == 'even' and sum(b) % 2 == 0) or (law == 'odd' and sum(b) % 2 == 1)
               or (law == 'nae' and 0 < sum(b) < len(P))]
        o = ktest(len(P), own)
        out.append({'rule': '%s(%s)' % (law, ','.join(P)), 'induced': [''.join(map(str, r)) for r in rel],
                    'K1': K1, 'K2': K2, 'K3': K3, 'whole': K1 and K2 and K3, 'own': all(o)})
    return {'n_vars': len(pos), 'n_states': int(len(states)), 'rules': out}
