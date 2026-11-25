"""Core engine of TWO-COUNTINGS-20261125-001A-E001, written from the frozen texts alone.

  research/TWO-COUNTINGS-20261125-001/definitions.md      "TD" (cited by section)
  research/TWO-COUNTINGS-20261125-001A/preregistration.md "PR"
  deviations.md of this folder                            readings, cited "R n"

A knot is (rule, places), rule in {'even', 'odd', 'nae'}, places a tuple of distinction names.  A history (TD 1.3) is a
list of stages, each a list of knots; stage 0 is the start S_0 (it may be empty).  States are Python ints over a global
index of distinctions: the start's distinctions first (in a backtracking order), then each stage's fresh distinctions in
order of first appearance, so the restriction of a state to stage j - 1 is a prefix mask.  Everything is exact.
"""
from __future__ import annotations

import itertools
import json
import os
import resource
import subprocess
import sys
from collections import defaultdict
from fractions import Fraction as Fr
from math import gcd, lcm

import numpy as np

REPO = '/home/jscul/p-vs-np-contact-first'
EXP = REPO + '/experiments/TWO-COUNTINGS-20261125-001A/TWO-COUNTINGS-20261125-001A-E001_two_countings'
ART = REPO + '/artifacts/TWO-COUNTINGS-20261125-001A/TWO-COUNTINGS-20261125-001A-E001_two_countings'
PY = REPO + '/.venv/bin/python'
sys.path.insert(0, REPO + '/tools')
from knotlab.knots import check_knot  # noqa: E402  (canonical library, unchanged)
from knotlab.relations import Relation  # noqa: E402

MEM_CAP = 6 * 1024 ** 3


def cap_memory():
    """A hard 6 GB address-space cap on this process (the brief)."""
    resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP, MEM_CAP))


# ------------------------------------------------------------------------------------------------------- knots
def kstr(k):
    return '%s(%s)' % (k[0], ','.join(k[1]))


def parse_knot(s):
    rule, rest = s.split('(', 1)
    return (rule, tuple(rest.rstrip(')').split(',')))


def as_knot(k):
    if isinstance(k, str):
        return parse_knot(k)
    return (k[0], tuple(k[1]))


def sat_rule(rule, x, m):
    """Whether the bits x (= state & mask) satisfy the rule on the places of mask m."""
    if rule == 'even':
        return not (x.bit_count() & 1)
    if rule == 'odd':
        return bool(x.bit_count() & 1)
    if rule == 'nae':
        return x != 0 and x != m
    raise ValueError(rule)


def rule_pred(rule, bits):
    s = sum(bits)
    if rule == 'even':
        return s % 2 == 0
    if rule == 'odd':
        return s % 2 == 1
    return 0 < s < len(bits)


def variables_of(knots):
    out, seen = [], set()
    for _, P in knots:
        for p in P:
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def order_vars(knots):
    """A backtracking order: repeatedly take the knot with the fewest new distinctions among those meeting the ones
    placed (the first unplaced knot when none meets them)."""
    order, placed = [], set()
    left = [list(P) for _, P in knots]
    while left:
        best, bi = None, None
        for i, P in enumerate(left):
            new = [p for p in P if p not in placed]
            meet = len(P) - len(new)
            key = (0 if meet or not placed else 1, len(new), i)
            if best is None or key < best:
                best, bi = key, i
        P = left.pop(bi)
        for p in P:
            if p not in placed:
                placed.add(p)
                order.append(p)
    return order


def enum_backtrack(knots, order):
    """All allowed states of the knots, as ints over the bit positions given by `order`."""
    idx = {v: i for i, v in enumerate(order)}
    n = len(order)
    checks = [[] for _ in range(n)]
    for rule, P in knots:
        m = 0
        for p in P:
            m |= 1 << idx[p]
        checks[max(idx[p] for p in P)].append((rule, m))
    out = []
    if n == 0:
        return [0]
    stack = [(0, 0)]
    while stack:
        d, s = stack.pop()
        for bit in (1, 0):
            t = s | (bit << d)
            good = True
            for rule, m in checks[d]:
                if not sat_rule(rule, t & m, m):
                    good = False
                    break
            if good:
                if d + 1 == n:
                    out.append(t)
                else:
                    stack.append((d + 1, t))
    out.sort()
    return out


def enum_brute(knots, order):
    """Every assignment of every distinction (the gate's reference)."""
    idx = {v: i for i, v in enumerate(order)}
    ks = []
    for rule, P in knots:
        m = 0
        for p in P:
            m |= 1 << idx[p]
        ks.append((rule, m))
    return [s for s in range(1 << len(order)) if all(sat_rule(r, s & m, m) for r, m in ks)]


# ------------------------------------------------------------------------------------------------------ histories
def _filter(w, ks):
    ok = np.ones(len(w), dtype=bool)
    for rule, m in ks:
        x = w & np.int64(m)
        if rule == 'even':
            ok &= (np.bitwise_count(x) & 1) == 0
        elif rule == 'odd':
            ok &= (np.bitwise_count(x) & 1) == 1
        else:
            ok &= (x != 0) & (x != np.int64(m))
    return ok


class History:
    """TD 1.3-1.4: stages; fresh distinctions; completions c_j(o); A(S_j) for every j (numpy int64 states)."""

    def __init__(self, stages, start_order=None):
        self.stages = [[as_knot(k) for k in st] for st in stages]
        s0 = self.stages[0]
        order = list(start_order) if start_order is not None else order_vars(s0)
        assert set(order) == set(variables_of(s0)), 'start order must hold exactly the start distinctions'
        self.vars = list(order)
        seen = set(order)
        self.fresh = [list(order)]
        self.nvars_at = [len(order)]
        for st in self.stages[1:]:
            fr = []
            for _, P in st:
                for p in P:
                    if p not in seen:
                        seen.add(p)
                        fr.append(p)
                        self.vars.append(p)
            self.fresh.append(fr)
            self.nvars_at.append(len(self.vars))
        assert len(self.vars) <= 62, 'more than 62 distinctions'
        self.idx = {v: i for i, v in enumerate(self.vars)}
        self.A = [np.array(enum_numpy(s0, order), dtype=np.int64)]
        self.c = [None]
        for j in range(1, len(self.stages)):
            ks = []
            for rule, P in self.stages[j]:
                m = 0
                for p in P:
                    m |= 1 << self.idx[p]
                ks.append((rule, m))
            base = self.nvars_at[j - 1]
            f = len(self.fresh[j])
            prev = self.A[j - 1]
            cnt = np.zeros(len(prev), dtype=np.int64)
            parts = []
            for z in range(1 << f):
                w = prev | np.int64(z << base)
                ok = _filter(w, ks)
                parts.append(w[ok])
                cnt += ok
            Aj = np.sort(np.concatenate(parts)) if parts else prev.copy()
            self.A.append(Aj)
            self.c.append(cnt)
        self.t = len(self.stages) - 1
        self._cmat = None

    def mask_at(self, j):
        return (1 << self.nvars_at[j]) - 1

    def knots(self, upto=None):
        upto = self.t if upto is None else upto
        return [k for st in self.stages[:upto + 1] for k in st]

    def held(self, upto):
        return set(variables_of(self.knots(upto)))

    def c_at(self, j, states):
        """c_j(w|_(j-1)) for an array of states of any later stage."""
        pre = states & np.int64(self.mask_at(j - 1))
        pos = np.searchsorted(self.A[j - 1], pre)
        return self.c[j][pos]

    def cmat(self):
        """c_j of every final state, j = 1..t (rows)."""
        if self._cmat is None:
            F = self.A[self.t]
            self._cmat = np.array([self.c_at(j, F) for j in range(1, self.t + 1)], dtype=np.int64).reshape(self.t, len(F))
        return self._cmat

    def cdict(self, j):
        return {int(o): int(c) for o, c in zip(self.A[j - 1], self.c[j])}

    def extends(self, j):
        return bool((self.c[j] >= 1).all())

    def weights_from(self, s):
        """Counting from stage s (TD 3.3; s = 0 counting from the start, s = t counting from the finish), unconditioned:
        returns {'states', 'den' (weight = 1/den), 'kept'} or None when A(S_s) is empty."""
        if len(self.A[s]) == 0:
            return None
        F = self.A[self.t]
        cm = self.cmat()
        est = float(len(self.A[s]))
        for j in range(s + 1, self.t + 1):
            est *= float(cm[j - 1].max()) if len(F) else 1.0
        if est < 2.0 ** 60:
            den = np.full(len(F), len(self.A[s]), dtype=np.int64)
            for j in range(s + 1, self.t + 1):
                den = den * cm[j - 1]
        else:
            den = np.full(len(F), len(self.A[s]), dtype=object)
            for j in range(s + 1, self.t + 1):
                den = den * cm[j - 1].astype(object)
        dv, cnt = np.unique(den, return_counts=True)
        kept = sum((Fr(int(c), int(d)) for d, c in zip(dv, cnt)), Fr(0))
        return {'states': F, 'den': den, 'kept': kept}

    def value(self, w, rec):
        v = 0
        for i, name in enumerate(rec):
            v |= ((int(w) >> self.idx[name]) & 1) << i
        return v

    def values(self, states, rec):
        v = np.zeros(len(states), dtype=np.int64)
        for i, name in enumerate(rec):
            v |= ((states >> np.int64(self.idx[name])) & 1) << np.int64(i)
        return v


def _fits(den):
    return len(den) == 0 or max(den) < 2 ** 62


def enum_numpy(knots, order=None):
    """All allowed states of the knots over the positions of `order` (default order_vars), knot by knot."""
    knots = [as_knot(k) for k in knots]
    order = list(order) if order is not None else order_vars(knots)
    idx = {v: i for i, v in enumerate(order)}
    assert len(order) <= 62
    # add knots in the order their last distinction (in `order`) appears; extend by the distinctions between
    pending = sorted(knots, key=lambda k: max(idx[p] for p in k[1]) if k[1] else -1)
    states = np.zeros(1, dtype=np.int64)
    placed = 0
    ki = 0
    while placed < len(order) or ki < len(pending):
        # next knot's last position
        nxt = max(idx[p] for p in pending[ki][1]) if ki < len(pending) else len(order) - 1
        # extend by distinctions placed .. nxt
        f = nxt + 1 - placed
        if f > 0:
            base = placed
            parts = [states | np.int64(z << base) for z in range(1 << f)]
            states = np.concatenate(parts)
            placed = nxt + 1
        ks = []
        while ki < len(pending) and max(idx[p] for p in pending[ki][1]) < placed:
            rule, P = pending[ki]
            m = 0
            for p in P:
                m |= 1 << idx[p]
            ks.append((rule, m))
            ki += 1
        if ks:
            states = states[_filter(states, ks)]
        if ki >= len(pending) and placed >= len(order):
            break
    return np.sort(states)


def counting(H, s, renorm=True):
    """Weights from stage s, renormalised when weight is lost (TD 3.4); returns (W, kept)."""
    W = H.weights_from(s)
    if W is None:
        return None, Fr(0)
    W['scale'] = (1 / W['kept']) if (renorm and W['kept'] != 1) else Fr(1)
    return W, W['kept']


def _group(keys_list, den, scale):
    """Sum of 1/den over equal keys (tuples of arrays), times scale; exact."""
    cols = [np.asarray(c, dtype=np.int64) for c in keys_list]
    out = defaultdict(Fr)
    if _fits(den):
        d = np.asarray(den.astype(np.int64))
        bits = [max(1, int(c.max()).bit_length()) if len(c) else 1 for c in cols]
        dbits = max(1, int(d.max()).bit_length()) if len(d) else 1
        if sum(bits) + dbits <= 62 and all((c >= 0).all() for c in cols):
            key = np.zeros(len(d), dtype=np.int64)
            for c, b in zip(cols, bits):
                key = (key << np.int64(b)) | c
            key = (key << np.int64(dbits)) | d
            uq, cnt = np.unique(key, return_counts=True)
            dm = (1 << dbits) - 1
            for kk, c in zip(uq.tolist(), cnt.tolist()):
                dd = kk & dm
                kk >>= dbits
                parts = []
                for b in reversed(bits):
                    parts.append(kk & ((1 << b) - 1))
                    kk >>= b
                out[tuple(reversed(parts))] += Fr(c, dd)
        else:
            M = np.stack(cols + [d], axis=1)
            uq, cnt = np.unique(M, axis=0, return_counts=True)
            for row, c in zip(uq, cnt):
                out[tuple(int(x) for x in row[:-1])] += Fr(int(c), int(row[-1]))
    else:
        for i in range(len(den)):
            out[tuple(int(c[i]) for c in cols)] += Fr(1, int(den[i]))
    if scale != 1:
        out = {k: x * scale for k, x in out.items()}
    return dict(out)


def joint(H, W, recA, recB):
    F = W['states']
    u = H.values(F, recA)
    v = H.values(F, recB)
    return _group([u, v], W['den'], W['scale'])


def marginal(H, W, rec):
    F = W['states']
    u = H.values(F, rec)
    g = _group([u], W['den'], W['scale'])
    return {k[0]: x for k, x in g.items()}


def as_dict(H, W):
    """{final state: weight} (gates only)."""
    return {int(w): Fr(1, int(d)) * W['scale'] for w, d in zip(W['states'], W['den'])}


def tv(p, q):
    keys = set(p) | set(q)
    return sum((abs(p.get(k, Fr(0)) - q.get(k, Fr(0))) for k in keys), Fr(0)) / 2


# ----------------------------------------------------------------------------------------------------------- score
PLACEMENTS = [(0, 0), (0, 1), (1, 0), (1, 1)]   # where the minus sign sits


def _sign(p, a, b):
    return -1 if (a, b) == p else 1


def hidden_change(P):
    """TD 4.3 with R 6: the largest change of either record under the other's two settings."""
    best = Fr(0)
    for a in (0, 1):
        m0 = defaultdict(Fr)
        m1 = defaultdict(Fr)
        for (u, v), x in P[(a, 0)].items():
            m0[u] += x
        for (u, v), x in P[(a, 1)].items():
            m1[u] += x
        best = max(best, tv(m0, m1))
    for b in (0, 1):
        m0 = defaultdict(Fr)
        m1 = defaultdict(Fr)
        for (u, v), x in P[(0, b)].items():
            m0[v] += x
        for (u, v), x in P[(1, b)].items():
            m1[v] += x
        best = max(best, tv(m0, m1))
    return best


def record_changes(P):
    """(largest change of the first record, of the second record)."""
    ca = Fr(0)
    for a in (0, 1):
        m = [defaultdict(Fr), defaultdict(Fr)]
        for b in (0, 1):
            for (u, v), x in P[(a, b)].items():
                m[b][u] += x
        ca = max(ca, tv(m[0], m[1]))
    cb = Fr(0)
    for b in (0, 1):
        m = [defaultdict(Fr), defaultdict(Fr)]
        for a in (0, 1):
            for (u, v), x in P[(a, b)].items():
                m[a][v] += x
        cb = max(cb, tv(m[0], m[1]))
    return ca, cb


def _merge_rows(rows, merge=True):
    """rows: {value: tuple of Fractions}; returns list of merged rows (sums of proportional rows)."""
    groups = {}
    order = []
    for u in sorted(rows):
        r = rows[u]
        first = next((x for x in r if x != 0), None)
        if first is None:
            continue
        key = tuple(x / first for x in r) if merge else ('value', u)
        if key in groups:
            g = groups[key]
            groups[key] = tuple(p + q for p, q in zip(g, r))
        else:
            groups[key] = r
            order.append(key)
    return [groups[k] for k in order]


def _tables(P, swap=False, merge=True):
    """Integer matrices M[a][b] (rows: merged first-side values under a; cols: merged second-side values under b) and the
    common denominator.  swap: the roles of the two observers exchanged."""
    if swap:
        Q = {}
        for (a, b), t in P.items():
            Q[(b, a)] = {(v, u): x for (u, v), x in t.items()}
        P = Q
    Uv = {a: sorted({u for b in (0, 1) for (u, v), x in P[(a, b)].items() if x}) for a in (0, 1)}
    Vv = {b: sorted({v for a in (0, 1) for (u, v), x in P[(a, b)].items() if x}) for b in (0, 1)}
    # merge second-side columns per b: column of v under b is (P_0b(., v) over U_0, P_1b(., v) over U_1)
    colmerged = {}
    for b in (0, 1):
        cols = {v: tuple([P[(0, b)].get((u, v), Fr(0)) for u in Uv[0]] + [P[(1, b)].get((u, v), Fr(0)) for u in Uv[1]])
                for v in Vv[b]}
        colmerged[b] = _merge_rows(cols, merge)
    # now rows per a over the merged columns
    M = {}
    for a in (0, 1):
        rows = {}
        off = 0 if a == 0 else len(Uv[0])
        for i, u in enumerate(Uv[a]):
            rows[u] = tuple(colmerged[b][k][off + i] for b in (0, 1) for k in range(len(colmerged[b])))
        mr = _merge_rows(rows, merge)
        n0 = len(colmerged[0])
        M[a] = {0: [r[:n0] for r in mr], 1: [r[n0:] for r in mr]}
    den = 1
    for a in (0, 1):
        for b in (0, 1):
            for r in M[a][b]:
                for x in r:
                    den = lcm(den, x.denominator)
    Mi = {}
    for a in (0, 1):
        for b in (0, 1):
            Mi[(a, b)] = np.array([[int(x * den) for x in r] for r in M[a][b]], dtype=object)
    return Mi, den


def _signs(n, fix_first):
    if n == 0:
        return np.ones((1, 0), dtype=np.int64)
    rows = []
    rng = range(1 << (n - 1)) if fix_first else range(1 << n)
    for z in rng:
        if fix_first:
            bits = [0] + [(z >> i) & 1 for i in range(n - 1)]
        else:
            bits = [(z >> i) & 1 for i in range(n)]
        rows.append([1 - 2 * b for b in bits])
    return np.array(rows, dtype=np.int64)


def score_all(P, merged=True):
    """TD 4.4, all two-valued functions, exact (R 2-4).  P: {(a, b): {(u, v): weight}}."""
    best = None
    sizes = []
    for swap in (False, True):
        Mi, den = _tables(P, swap, merged)
        sizes.append((Mi[(0, 0)].shape[0] + Mi[(1, 0)].shape[0], swap, Mi, den))
    sizes.sort(key=lambda t: (t[0], t[1]))
    _, swap, Mi, den = sizes[0]
    big = max(int(abs(x)) for k in Mi for x in Mi[k].flat) if any(Mi[k].size for k in Mi) else 0
    n0 = Mi[(0, 0)].shape[0]
    n1 = Mi[(1, 0)].shape[0]
    vmax = max(Mi[(0, 0)].shape[1] if Mi[(0, 0)].ndim == 2 else 0, Mi[(0, 1)].shape[1] if Mi[(0, 1)].ndim == 2 else 0, 1)
    use64 = big * max(1, n0 + n1) * 4 * vmax < 2 ** 62
    F0 = _signs(n0, False)
    F1 = _signs(n1, True)
    L = {}
    for (a, b), M in Mi.items():
        F = F0 if a == 0 else F1
        if M.size == 0:
            L[(a, b)] = np.zeros((F.shape[0], 0), dtype=np.int64 if use64 else object)
            continue
        Mm = M.astype(np.int64) if use64 else M
        Ff = F if use64 else F.astype(object)
        L[(a, b)] = Ff @ Mm
    K0, K1 = F0.shape[0], F1.shape[0]
    chunk = max(1, int(4_000_000 // max(1, K1 * max(L[(0, 0)].shape[1], L[(0, 1)].shape[1], 1))))
    top = None
    for p in PLACEMENTS:
        for i in range(0, K0, chunk):
            tot = None
            for b in (0, 1):
                X = _sign(p, 0, b) * L[(0, b)][i:i + chunk, None, :] + _sign(p, 1, b) * L[(1, b)][None, :, :]
                s = np.abs(X).sum(axis=2)
                tot = s if tot is None else tot + s
            m = tot.max()
            if top is None or m > top:
                top = m
    return Fr(int(top), den)


def score_all_unmerged(P):
    """The same class by direct enumeration of both sides' functions on the first side and best response, no merging
    (gate only; small cases)."""
    Uv = {a: sorted({u for b in (0, 1) for (u, v), x in P[(a, b)].items() if x}) for a in (0, 1)}
    Vv = {b: sorted({v for a in (0, 1) for (u, v), x in P[(a, b)].items() if x}) for b in (0, 1)}
    best = None
    for f0 in itertools.product((1, -1), repeat=len(Uv[0])):
        for f1 in itertools.product((1, -1), repeat=len(Uv[1])):
            fa = {0: dict(zip(Uv[0], f0)), 1: dict(zip(Uv[1], f1))}
            for p in PLACEMENTS:
                tot = Fr(0)
                for b in (0, 1):
                    for v in Vv[b]:
                        s = Fr(0)
                        for a in (0, 1):
                            Lv = sum((fa[a][u] * P[(a, b)].get((u, v), Fr(0)) for u in Uv[a]), Fr(0))
                            s += _sign(p, a, b) * Lv
                        tot += abs(s)
                if best is None or tot > best:
                    best = tot
    return best


def score_parity(P, kA, kB, absval=False):
    """TD 4.4, parities of a nonempty set of record bits, exact (integers over the common denominator)."""
    den = 1
    for t in P.values():
        for x in t.values():
            den = lcm(den, x.denominator)
    TA = list(range(1, 1 << kA))
    TB = list(range(1, 1 << kB))
    E = {}
    for (a, b), t in P.items():
        us = sorted({u for (u, v) in t})
        vs = sorted({v for (u, v) in t})
        iu = {u: i for i, u in enumerate(us)}
        iv = {v: i for i, v in enumerate(vs)}
        M = np.zeros((len(us), len(vs)), dtype=object)
        for (u, v), x in t.items():
            M[iu[u], iv[v]] += int(x * den)
        CA = np.array([[1 - 2 * ((u & T).bit_count() & 1) for T in TA] for u in us], dtype=object).reshape(len(us), len(TA))
        CB = np.array([[1 - 2 * ((v & T).bit_count() & 1) for T in TB] for v in vs], dtype=object).reshape(len(vs), len(TB))
        E[(a, b)] = CA.T.dot(M).dot(CB)          # E[T, T2]
    best = None
    for p in PLACEMENTS:
        for g in ((1, -1) if absval else (1,)):
            for i0 in range(len(TA)):
                for i1 in range(len(TA)):
                    tot = 0
                    for b in (0, 1):
                        row = g * (_sign(p, 0, b) * E[(0, b)][i0, :] + _sign(p, 1, b) * E[(1, b)][i1, :])
                        tot += max(row)
                    if best is None or tot > best:
                        best = tot
    return Fr(int(best), den)


def fstr(x):
    if x is None:
        return None
    x = Fr(x)
    return str(x.numerator) if x.denominator == 1 else '%d/%d' % (x.numerator, x.denominator)


# --------------------------------------------------------------------------------------------------------- knot test
def full_states(knots):
    knots = [as_knot(k) for k in knots]
    order = order_vars(knots)
    return order, enum_numpy(knots, order)


def induced(knots, order=None, states=None):
    """{knot index: sorted list of induced rows as strings over its places}."""
    if states is None:
        order, states = full_states(knots)
    idx = {v: i for i, v in enumerate(order)}
    out = {}
    for i, (rule, P) in enumerate(knots):
        code = np.zeros(len(states), dtype=np.int64)
        for q, p in enumerate(P):
            code |= ((states >> np.int64(idx[p])) & 1) << np.int64(q)
        rows = []
        for c in np.unique(code):
            rows.append(''.join(str((int(c) >> q) & 1) for q in range(len(P))))
        out[i] = sorted(rows)
    return out


def verdict_of(places, rows):
    rel = Relation(tuple(places), frozenset(tuple(ch == '1' for ch in r) for r in rows))
    rep = check_knot(rel, places[:-1], places[-1])
    return {'K1': rep.binding, 'K2': rep.loss_on_erasure, 'K3': rep.coexistence, 'knot': rep.is_knot,
            'notes': list(rep.notes)}


def own_verdict(rule, places):
    rel = Relation.from_predicate(places, lambda val: rule_pred(rule, [int(val[p]) for p in places]))
    rep = check_knot(rel, places[:-1], places[-1])
    return {'K1': rep.binding, 'K2': rep.loss_on_erasure, 'K3': rep.coexistence, 'knot': rep.is_knot}


def project_test(knots):
    """The knot test in the whole structure by projection, and on its own, for every knot (TD 10, R 10)."""
    knots = [as_knot(k) for k in knots]
    order, states = full_states(knots)
    ind = induced(knots, order, states)
    out = []
    for i, (rule, P) in enumerate(knots):
        v = verdict_of(list(P), ind[i])
        o = own_verdict(rule, list(P))
        out.append({'knot': kstr((rule, P)), 'induced': ind[i], 'K1': v['K1'], 'K2': v['K2'], 'K3': v['K3'],
                    'whole': v['knot'], 'own': o['knot'], 'notes': v['notes']})
    return {'n_knots': len(knots), 'n_distinctions': len(order), 'n_states': len(states), 'knots': out}


def cnf_of(knots):
    clauses = []
    for rule, P in knots:
        m = len(P)
        if rule == 'nae':
            clauses.append(' '.join(P))
            clauses.append(' '.join('-' + p for p in P))
        else:
            want = 0 if rule == 'even' else 1
            for bits in itertools.product((0, 1), repeat=m):
                if sum(bits) % 2 != want:
                    # forbid this assignment: some place differs from it
                    clauses.append(' '.join((p if b == 0 else '-' + p) for p, b in zip(P, bits)))
    return '; '.join(clauses)


def canonical_cmd(knots, i):
    knots = [as_knot(k) for k in knots]
    rule, P = knots[i]
    allv = variables_of(knots)
    others = [v for v in allv if v not in P]
    cmd = [PY, '-B', '-m', 'knotlab', 'check', '--cnf', cnf_of(knots), '--loops', *P[:-1], '--contact', P[-1]]
    if others:
        cmd += ['--witnesses', *others]
    cmd.append('--json')
    return cmd


def _child_cap():
    resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP, MEM_CAP))


def canonical_check(knots, i, timeout=1800):
    cmd = canonical_cmd(knots, i)
    env = dict(os.environ)
    env['PYTHONPATH'] = 'tools'
    r = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True, timeout=timeout,
                       preexec_fn=_child_cap)
    if r.returncode != 0:
        return {'error': r.stderr.strip()[-500:], 'returncode': r.returncode}
    d = json.loads(r.stdout)
    return {'K1': d['binding'], 'K2': d['loss_on_erasure'], 'K3': d['coexistence'], 'knot': d['is_knot'],
            'allowed': sorted(d['allowed']), 'variables': d['variables']}


def cmd_text(knots, i):
    """The command line, as one would type it (for the outputs)."""
    c = canonical_cmd(knots, i)
    parts = ['PYTHONPATH=tools', 'python3', '-B'] + c[2:]
    out = []
    for p in parts:
        out.append('"%s"' % p if (' ' in p or ';' in p) else p)
    return ' '.join(out)


# ------------------------------------------------------------------------------------------------------------- io
def load_structures():
    d = json.load(open(REPO + '/research/TWO-COUNTINGS-20261125-001A/structures.json'))
    return {k: [as_knot(x) for x in v] for k, v in d.items()}


def dump(name, obj):
    path = os.path.join(ART, name)
    with open(path, 'w') as fh:
        json.dump(obj, fh, indent=1, sort_keys=False, default=_default)
        fh.write('\n')
    return path


def _default(o):
    if isinstance(o, Fr):
        return fstr(o)
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    if isinstance(o, np.integer):
        return int(o)
    raise TypeError(type(o))
