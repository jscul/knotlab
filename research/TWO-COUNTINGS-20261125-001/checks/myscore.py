"""Checker's own four-correlation score, hiding and countings (exact), on setting tests.

A setting test: stages (list of rule lists, the first the start), then the setting knots
KA[a] = nae(x1, x2|x3, za), KB[b] = nae(y1, y2|y3, zb) as one last stage.
Counting from the finish: uniform on the allowed states of each finished structure.
Counting from stage s: (1/|A(S_s)|) * prod_{j>s} 1/c_j(w restricted), renormalised per history if weight is lost.
Score: max over the four minus placements and all two-valued functions of own record and own setting.
"""
import itertools
import sys
from fractions import Fraction as Fr
from math import lcm

import numpy as np

sys.path.insert(0, 'CHECK_SCRATCH')
from mykt import allowed_states

REC_A = ('x1', 'x2', 'x3', 'za')
REC_B = ('y1', 'y2', 'y3', 'zb')


def setting_knots(optA=('x2', 'x3'), optB=('y2', 'y3')):
    KA = {a: ('nae', ('x1', optA[a], 'za')) for a in (0, 1)}
    KB = {b: ('nae', ('y1', optB[b], 'zb')) for b in (0, 1)}
    return KA, KB


def states_dicts(rules):
    order, st = allowed_states(rules)
    return order, st


def weights(stages, s):
    """stages: list of rule lists (stage j adds stages[j]). Return (order, states of the finish, weights, kept)."""
    cum = []
    acc = []
    for st in stages:
        acc = acc + list(st)
        cum.append(list(acc))
    enums = [allowed_states(c) for c in cum]
    counts = {}
    for j in range(1, len(stages)):
        ord_prev = enums[j - 1][0]
        ord_j, st_j = enums[j]
        pj = {v: i for i, v in enumerate(ord_j)}
        idx = [pj[v] for v in ord_prev]
        d = {}
        for t in st_j:
            kk = tuple(t[i] for i in idx)
            d[kk] = d.get(kk, 0) + 1
        counts[j] = d
    order_f, states_f = enums[-1]
    pos_f = {v: i for i, v in enumerate(order_f)}
    W = []
    for w in states_f:
        wt = Fr(1, len(enums[s][1]))
        for j in range(s + 1, len(stages)):
            key = tuple(w[pos_f[v]] for v in enums[j - 1][0])
            wt /= counts[j][key]
        W.append(wt)
    tot = sum(W)
    if tot != 1:
        W = [x / tot for x in W]
    return order_f, states_f, W, tot


def joint(order, states, W, recA=REC_A, recB=REC_B):
    pos = {v: i for i, v in enumerate(order)}
    ia = [pos[v] for v in recA]
    ib = [pos[v] for v in recB]
    P = {}
    for w, x in zip(states, W):
        u = tuple(w[i] for i in ia)
        v = tuple(w[i] for i in ib)
        P[(u, v)] = P.get((u, v), 0) + x
    return P


def tv(p, q):
    keys = set(p) | set(q)
    return sum(abs(p.get(k, 0) - q.get(k, 0)) for k in keys) / 2


def marg(P, side):
    m = {}
    for (u, v), x in P.items():
        k = u if side == 0 else v
        m[k] = m.get(k, 0) + x
    return m


def change(Ps):
    """Ps[(a,b)] joint. Largest TV of a record's distribution under the other's two settings."""
    c = Fr(0)
    for a in (0, 1):
        c = max(c, tv(marg(Ps[(a, 0)], 0), marg(Ps[(a, 1)], 0)))
    for b in (0, 1):
        c = max(c, tv(marg(Ps[(0, b)], 1), marg(Ps[(1, b)], 1)))
    return c


def _merged(Ps, UB):
    """Per own setting a, merge record values whose rows (over b and v) are positive multiples; drop zero rows.
    Returns {a: list of row vectors {(b, v): weight}} (exact; an optimal f_a takes one value on a merged class)."""
    out = {}
    for a in (0, 1):
        rows = {}
        for b in (0, 1):
            for (u, v), x in Ps[(a, b)].items():
                if x:
                    rows.setdefault(u, {})[(b, v)] = rows.setdefault(u, {}).get((b, v), 0) + x
        groups = {}
        for u, r in rows.items():
            ks = sorted(r)
            first = r[ks[0]]
            key = tuple((k, r[k] / first) for k in ks)
            g = groups.setdefault(key, {})
            for k in ks:
                g[k] = g.get(k, 0) + r[k]
        out[a] = list(groups.values())
    return out


def score(Ps):
    """Max over sign placements and all two-valued functions of own record and own setting (exact)."""
    UA = sorted({u for P in Ps.values() for (u, v) in P})
    UB = sorted({v for P in Ps.values() for (u, v) in P})
    swapped = {(b, a): {(v, u): x for (u, v), x in P.items()} for (a, b), P in Ps.items()}
    mA = _merged(Ps, UB)
    mB = _merged(swapped, UA)
    if len(mA[0]) + len(mA[1]) > len(mB[0]) + len(mB[1]):
        Ps, mA = swapped, mB
        UA, UB = UB, UA
    D = 1
    for P in Ps.values():
        for x in P.values():
            D = lcm(D, x.denominator)
    n = len(UB)
    ib = {v: i for i, v in enumerate(UB)}
    M = {}
    for a in (0, 1):
        for b in (0, 1):
            A = np.zeros((len(mA[a]), n), dtype=np.int64)
            for i, row in enumerate(mA[a]):
                for (bb, v), x in row.items():
                    if bb == b:
                        A[i, ib[v]] = int(x * D)
            M[(a, b)] = A
    F = {a: np.array(list(itertools.product((1, -1), repeat=len(mA[a]))), dtype=np.int64) for a in (0, 1)}
    L = {(a, b): F[a] @ M[(a, b)] for a in (0, 1) for b in (0, 1)}
    best = None
    for minus in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        sg = {ab: (-1 if ab == minus else 1) for ab in M}
        n0, n1 = len(F[0]), len(F[1])
        tot = np.zeros((n0, n1), dtype=np.int64)
        for b in (0, 1):
            X = sg[(0, b)] * L[(0, b)]
            Y = sg[(1, b)] * L[(1, b)]
            tot += np.abs(X[:, None, :] + Y[None, :, :]).sum(axis=2)
        v = int(tot.max())
        best = v if best is None else max(best, v)
    return Fr(best, D)


def setting_test(pre_stages, optA=('x2', 'x3'), optB=('y2', 'y3'), counting='finish', s=0):
    KA, KB = setting_knots(optA, optB)
    Ps = {}
    tots = {}
    for a in (0, 1):
        for b in (0, 1):
            stages = [list(x) for x in pre_stages] + [[KA[a], KB[b]]]
            if counting == 'finish':
                rules = [r for st in stages for r in st]
                order, states = allowed_states(rules)
                W = [Fr(1, len(states))] * len(states)
                tots[(a, b)] = len(states)
            else:
                order, states, W, tot = weights(stages, s)
                tots[(a, b)] = tot
            Ps[(a, b)] = joint(order, states, W)
    return score(Ps), change(Ps), tots
