"""Bases, distances and order checks for DISTANCE-ORDER-20261117-001B-E001.

A base is a list of three-place knots on n distinctions, each knot a triple
(a, b, c) with a set of excluded joint states (plain not-all-equal excludes
000 and 111).  The disagreement count d(u, v) is the number of allowed states
in which u and v take different values; d/N is the disagreement rate.  Counts are exact (Python integers) by a
frontier dynamic programme along the distinction order, except on the weave
for L = 12, where a row transfer matrix in floating point is used.

Order checks for a distance D on the distinctions (unit = least positive value):
  P1  built from unit steps: D is a whole multiple of the unit, and every pair
      k > 1 units apart has a w one unit from u and k - 1 units from v;
  between(o, v, w): D(o, w) = D(o, v) + D(v, w) with D(o, v), D(v, w) > 0;
  gap: a pair with nothing strictly between (every finite D is the path
      distance of its gap graph); a line is a gap graph that is a path;
  chain: the longest sequence o, v1, ..., vk with each v_i strictly between o
      and v_(i+1), counted with o.
"""

import itertools
from fractions import Fraction

import numpy as np

NAE = frozenset({(0, 0, 0), (1, 1, 1)})


def thread(n):
    """Plain NAE on every three consecutive distinctions."""
    return n, [((i, i + 1, i + 2), NAE) for i in range(n - 2)]


def chain(k):
    """Plain NAE knots (w_i, m_i, w_{i+1}); w_i = 2i, m_i = 2i + 1."""
    return 2 * k + 1, [((2 * i, 2 * i + 1, 2 * i + 2), NAE) for i in range(k)]


def threshold_line(n):
    """j between i and k for every i < j < k: exclude x_i = x_k != x_j."""
    return n, [((i, j, k), frozenset({(0, 1, 0), (1, 0, 1)}))
               for i, j, k in itertools.combinations(range(n), 3)]


def weave_knots(L):
    """The six-regular weave W(L) of SPACE-ORDER-20261117-001: v(i, j) = i + L j."""
    v = lambda a, b: (a % L) + L * (b % L)
    out = []
    for j in range(L):
        for i in range(L):
            out.append(((v(i, j), v(i + 1, j), v(i, j + 1)), NAE))
            out.append(((v(i + 1, j), v(i, j + 1), v(i + 1, j + 1)), NAE))
    return L * L, out


def count(n, knots, pins=()):
    """Exact number of allowed states, with pinned values {(var, value)}.
    Frontier DP in the order 0..n-1: a variable leaves the frontier once every
    knot that holds it is complete."""
    pins = dict(pins)
    last = [-1] * n
    for t, _ in knots:
        m = max(t)
        for u in t:
            last[u] = max(last[u], m)
    by_max = {}
    for t, ex in knots:
        by_max.setdefault(max(t), []).append((t, ex))
    frontier = []
    table = {(): 1}
    for x in range(n):
        vals = (pins[x],) if x in pins else (0, 1)
        new_front = frontier + [x]
        pos = {u: i for i, u in enumerate(new_front)}
        checks = [(tuple(pos[u] for u in t), ex) for t, ex in by_max.get(x, [])]
        nt = {}
        for key, c in table.items():
            for b in vals:
                k2 = key + (b,)
                if all(tuple(k2[p] for p in ps) not in ex for ps, ex in checks):
                    nt[k2] = nt.get(k2, 0) + c
        keep = [i for i, u in enumerate(new_front) if last[u] > x]
        frontier = [new_front[i] for i in keep]
        table = {}
        for k2, c in nt.items():
            kk = tuple(k2[i] for i in keep)
            table[kk] = table.get(kk, 0) + c
    return sum(table.values())


def disagreement_table(n, knots, pairs=None):
    """N and {(u, v): number of allowed states with x_u != x_v}."""
    N = count(n, knots)
    pairs = pairs if pairs is not None else list(itertools.combinations(range(n), 2))
    d = {}
    for u, v in pairs:
        d[(u, v)] = count(n, knots, ((u, 0), (v, 1))) + count(n, knots, ((u, 1), (v, 0)))
    return N, d


def weave_transfer(L, exact):
    """Differ fractions from distinction 0 on W(L) by the row transfer matrix:
    N = Tr T^L, sum over states of s_0 s_v = Tr(S_0 T^r S_c T^(L-r)) for v = c + L r."""
    R = 1 << L
    bits = (np.arange(R)[:, None] >> np.arange(L)[None, :]) & 1
    ok = np.ones((R, R), dtype=bool)
    for i in range(L):
        a, a1 = bits[:, i][:, None], bits[:, (i + 1) % L][:, None]
        b, b1 = bits[:, i][None, :], bits[:, (i + 1) % L][None, :]
        ok &= ~((a == a1) & (a1 == b))          # up knot (i,j), (i+1,j), (i,j+1)
        ok &= ~((a1 == b) & (b == b1))          # down knot (i+1,j), (i,j+1), (i+1,j+1)
    dt = object if exact == "object" else (np.int64 if exact else np.float64)
    T = ok.astype(np.int64).astype(dt)
    P = [np.eye(R, dtype=np.int64).astype(dt)]
    for _ in range(L):
        P.append(P[-1] @ T)
    N = np.trace(P[L])
    spin = (1 - 2 * bits).astype(dt)            # +1 for value 0, -1 for value 1
    corr = {}
    for r in range(L):
        M = spin[:, 0][:, None] * P[r]          # S_0 T^r
        colsum = (M * P[L - r].T).sum(axis=0)   # sum_a M[a, b] P[b, a]
        for c in range(L):
            corr[c + L * r] = (colsum * spin[:, c]).sum()
    d = {v: (N - corr[v]) / 2 for v in corr}    # differ count from 0 to v
    return N, d


def weave_transfer_crt(L, primes=(1048573, 1048571, 1048559, 1048549, 1048517)):
    """Exact N and disagreement counts from distinction 0 on W(L): the transfer matrices of
    weave_transfer reduced modulo primes below 2^20 (float64 products stay exact), joined by the
    Chinese remainder theorem.  Counts are taken with 0/1 masks, so every quantity is nonnegative."""
    R = 1 << L
    bits = (np.arange(R)[:, None] >> np.arange(L)[None, :]) & 1
    ok = np.ones((R, R), dtype=bool)
    for i in range(L):
        a, a1 = bits[:, i][:, None], bits[:, (i + 1) % L][:, None]
        b, b1 = bits[:, i][None, :], bits[:, (i + 1) % L][None, :]
        ok &= ~((a == a1) & (a1 == b))
        ok &= ~((a1 == b) & (b == b1))
    T = ok.astype(np.float64)
    one = bits.astype(np.float64)               # 1 where the row's distinction c takes 1
    res_N, res_d = [], []
    for p in primes:
        P = [np.eye(R)]
        for _ in range(L):
            P.append(np.mod(P[-1] @ T, p))
        Np = int(np.mod(np.trace(P[L]), p))
        dp = {}
        for r in range(L):
            left1 = np.mod(one[:, 0][:, None] * P[r], p)          # value 1 at distinction 0
            left0 = np.mod((1 - one[:, 0])[:, None] * P[r], p)    # value 0 at distinction 0
            col1 = np.mod((left1 * P[L - r].T).sum(axis=0), p)
            col0 = np.mod((left0 * P[L - r].T).sum(axis=0), p)
            for c in range(L):
                dp[c + L * r] = int(np.mod((col1 * (1 - one[:, c])).sum() + (col0 * one[:, c]).sum(), p))
        res_N.append(Np)
        res_d.append(dp)
    M = 1
    for p in primes:
        M *= p
    def crt(rs):
        x = 0
        for r, p in zip(rs, primes):
            q = M // p
            x += r * q * pow(q, -1, p)
        return x % M
    N = crt(res_N)
    d = {v: crt([dp[v] for dp in res_d]) for v in res_d[0]}
    return N, d


def weave_steps(L, u, v):
    """Steps apart on W(L): neighbours differ by (+-1, 0), (0, +-1), (1, -1), (-1, 1)."""
    du, dv = (v % L) - (u % L), (v // L) - (u // L)
    best = None
    for a in (du - L, du, du + L):
        for b in (dv - L, dv, dv + L):
            s = abs(a) + abs(b) if a * b >= 0 else max(abs(a), abs(b))
            best = s if best is None else min(best, s)
    return best


def path_steps(n, knots):
    """Steps apart: graph distance between distinctions that share a knot."""
    adj = [set() for _ in range(n)]
    for t, _ in knots:
        for u, v in itertools.combinations(t, 2):
            adj[u].add(v)
            adj[v].add(u)
    dist = []
    for s in range(n):
        dd = [None] * n
        dd[s] = 0
        front = [s]
        while front:
            nxt = []
            for u in front:
                for w in adj[u]:
                    if dd[w] is None:
                        dd[w] = dd[u] + 1
                        nxt.append(w)
            front = nxt
        dist.append(dd)
    return dist


def as_matrix(n, d, diag=0):
    D = [[diag] * n for _ in range(n)]
    for (u, v), x in d.items():
        D[u][v] = D[v][u] = x
    return D


def unit_of(D, nodes):
    vals = [D[u][v] for u in nodes for v in nodes if u != v and D[u][v] > 0]
    return min(vals) if vals else None


def p1(D, nodes):
    """Built from unit steps (whole multiples of the unit, and a unit step toward v)."""
    unit = unit_of(D, nodes)
    if unit is None:
        return True, "no positive distance"
    for u in nodes:
        for v in nodes:
            if u == v or D[u][v] == 0:
                continue
            k = Fraction(D[u][v]) / Fraction(unit)
            if k.denominator != 1:
                return False, f"D({u},{v}) = {D[u][v]} is not a multiple of the unit {unit}"
            if k > 1 and not any(D[u][w] == unit and D[w][v] == D[u][v] - unit for w in nodes):
                return False, f"no unit step from {u} toward {v} (D = {D[u][v]}, unit {unit})"
    return True, f"unit {unit}"


def between_triples(D, nodes):
    """(o, v, w) with v strictly between o and w: D(o,w) = D(o,v) + D(v,w), all distinct, D(o,v), D(v,w) > 0."""
    out = []
    for o, v, w in itertools.permutations(nodes, 3):
        if o < w and D[o][v] > 0 and D[v][w] > 0 and D[o][w] == D[o][v] + D[v][w]:
            out.append((o, v, w))
    return out


def longest_chain(D, nodes, o, exclude=()):
    """Number of distinctions, o included, in the longest chain o, v1, ..., vk of the base-point order
    (v below w when v lies strictly between o and w); nodes in exclude are left out."""
    others = sorted((x for x in nodes if x != o and x not in exclude and D[o][x] > 0), key=lambda x: D[o][x])
    best = {}
    for w in others:
        b = 1
        for v in others:
            if D[o][v] < D[o][w] and D[v][w] > 0 and D[o][w] == D[o][v] + D[v][w]:
                b = max(b, best[v] + 1)
        best[w] = b
    return 1 + (max(best.values()) if best else 0)


def gap_graph(D, nodes):
    """Pairs with nothing strictly between them."""
    nodes = list(nodes)
    gaps = []
    for u, v in itertools.combinations(nodes, 2):
        if D[u][v] > 0 and not any(w not in (u, v) and D[u][w] > 0 and D[w][v] > 0 and D[u][v] == D[u][w] + D[w][v]
                                   for w in nodes):
            gaps.append((u, v))
    return gaps


def is_path(gaps, nodes):
    nodes = list(nodes)
    if len(gaps) != len(nodes) - 1:
        return False
    deg = {u: 0 for u in nodes}
    adj = {u: [] for u in nodes}
    for u, v in gaps:
        deg[u] += 1
        deg[v] += 1
        adj[u].append(v)
        adj[v].append(u)
    if max(deg.values()) > 2:
        return False
    seen, stack = {nodes[0]}, [nodes[0]]
    while stack:
        for w in adj[stack.pop()]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == len(nodes)


def log_rate(N, d):
    """tau = -log_3 |1 - 2 d / N| (infinite at rate one half)."""
    import math
    c = abs(1 - 2 * Fraction(d) / Fraction(N)) if not isinstance(d, float) else abs(1 - 2 * d / N)
    return float("inf") if c == 0 else -math.log(float(c), 3)


def with_flips(n, N, D):
    """Distinctions and their flips 0..2n-1 (u + n is the flip of u): d(u, v-bar) = N - d(u, v)."""
    E = [[0] * (2 * n) for _ in range(2 * n)]
    for u in range(n):
        for v in range(n):
            E[u][v] = E[u + n][v + n] = D[u][v]
            E[u][v + n] = E[u + n][v] = N - D[u][v]
    return E
