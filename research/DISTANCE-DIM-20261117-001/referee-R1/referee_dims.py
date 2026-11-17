"""Referee R1 for DISTANCE-DIM-20261117-001 (own code; nothing imported from the study).

  .venv/bin/python -B referee_dims.py > referee_dims.json

A. The implication half. For each test order (chain 12; grids 4x4, 6x6, 3x7; 5x5 less a 2x2 corner; 3x3x3; S_3 with bottom and
   top; bare S_3): its up-sets, the disagreement counts, strict betweenness against the order's intervals (D1), pairs with a
   missing joint pattern against comparability (D2), comparability from betweenness, the order rebuilt from betweenness by
   D3's propagation (checked to be P or its reverse), and the order dimension: a 2-realizer searched among linear extensions
   (coordinate orders for grids), and for dimension 3 a check that no 2-realizer exists (exhaustive on S_3 with bottom and top).
B. The chain grid (square torus, a knot (u, p, v) with a private p on each edge): grid correlations by the referee's own float
   row transfer, made exactly symmetric by reading them as a function of the canonical displacement (the torus's eight
   symmetries); private correlations from the conditional mean -(s_u + s_v)/2. Gap graph (relative neighbourhood, strict, on
   tau) from a grid start and from a private start: degrees and levels, against K3's frozen values. Transfer gaps (K7).
C. The weave W(L): tau from v(0,0) by float transfer; the relative-neighbourhood levels at L = 12 (K4); two other order-only
   readings: the nearest-neighbour graph (the k nearest by tau, k = 6) and the unit ball (tau <= 1), with their degrees and
   components; transfer gaps and gap x width (K8).
"""
from __future__ import annotations

import itertools
import json
import math
from collections import deque

import numpy as np
import scipy.sparse.linalg as sla


# ------------------------------------------------------------------ A. implications

def grid(*sides):
    els = list(itertools.product(*[range(s) for s in sides]))
    return els, lambda u, v: all(a <= b for a, b in zip(u, v))


def standard_example(bt):
    els = [("a", i) for i in range(3)] + [("b", i) for i in range(3)]
    leq0 = lambda u, v: u == v or (u[0] == "a" and v[0] == "b" and u[1] != v[1])
    if not bt:
        return els, leq0
    els = [("bot",)] + els + [("top",)]
    return els, lambda u, v: u == v or u == ("bot",) or v == ("top",) or (len(u) > 1 and len(v) > 1 and leq0(u, v))


def upsets(els, leq):
    n = len(els)
    up = [sum(1 << j for j in range(n) if leq(els[i], els[j])) for i in range(n)]
    out = set()
    stack = [0]
    seen = {0}
    while stack:
        s = stack.pop()
        out.add(s)
        for i in range(n):
            if not (s >> i) & 1:
                t = s | up[i]
                # adding the up-closure of i keeps an up-set
                if t not in seen:
                    seen.add(t)
                    stack.append(t)
    return sorted(out)


def implication_half():
    cases = {"chain 12": grid(12), "4x4": grid(4, 4), "6x6": grid(6, 6), "3x7": grid(3, 7)}
    e, l = grid(5, 5)
    keep = [x for x in e if not (x[0] >= 3 and x[1] >= 3)]
    cases["5x5 less 2x2"] = (keep, l)
    cases["3x3x3"] = grid(3, 3, 3)
    cases["S3 with bottom and top"] = standard_example(True)
    cases["bare S3"] = standard_example(False)
    out = {}
    for name, (els, leq) in cases.items():
        n = len(els)
        U = upsets(els, leq)
        d = [[sum(((s >> u) & 1) != ((s >> v) & 1) for s in U) for v in range(n)] for u in range(n)]
        lt = lambda u, v: u != v and leq(els[u], els[v])
        comp = {(u, v) for u in range(n) for v in range(n) if u < v and (lt(u, v) or lt(v, u))}
        between = {(u, w, v) for u in range(n) for v in range(u + 1, n) for w in range(n) if w not in (u, v)
                   and d[u][w] > 0 and d[w][v] > 0 and d[u][v] == d[u][w] + d[w][v]}
        interval = {(u, w, v) for u in range(n) for v in range(u + 1, n) for w in range(n) if w not in (u, v)
                    and ((lt(u, w) and lt(w, v)) or (lt(v, w) and lt(w, u)))}
        missing = {(u, v) for u in range(n) for v in range(u + 1, n)
                   if len({(((s >> u) & 1), ((s >> v) & 1)) for s in U}) < 4}
        comp_b = {(min(a, b), max(a, b)) for t in between for a, b in itertools.combinations(t, 2)}
        # D3's propagation: fix one comparable pair's direction, push it through shared elements
        mid = {frozenset(t): t[1] for t in between}
        below = {}                                  # below[(a, b)] = True when a < b in the rebuilt order
        if comp_b:
            x0, w0 = min(comp_b)
            below[(x0, w0)], below[(w0, x0)] = True, False
            q = deque([(x0, w0)])
            nbr = {u: set() for u in range(n)}
            for a, b in comp_b:
                nbr[a].add(b)
                nbr[b].add(a)
            while q:
                p_, q_ = q.popleft()
                for (pp, qq) in ((p_, q_), (q_, p_)):
                    for r in nbr[qq]:
                        if r == pp or (qq, r) in below:
                            continue
                        q_above_p = below[(pp, qq)]
                        m = mid.get(frozenset((pp, qq, r)))
                        q_above_r = (not q_above_p) if m == qq else q_above_p
                        below[(r, qq)], below[(qq, r)] = q_above_r, not q_above_r
                        q.append((qq, r))
        orient = {k: v for k, v in below.items() if v}
        rebuilt = set(orient)
        truth = {(u, v) for u in range(n) for v in range(n) if lt(u, v)}
        rev = {(v, u) for u, v in truth}
        row = {"elements": n, "states": len(U), "betweenness_equals_intervals": between == interval,
               "missing_pattern_equals_comparable": missing == comp, "comparability_from_betweenness_exact": comp_b == comp,
               "betweenness_triples": len(between),
               "order_rebuilt_up_to_reversal": bool(orient) and rebuilt in (truth, rev)}
        row["dimension"] = dimension(els, leq, lt, n, name)
        out[name] = row
    return out


def linear_extensions(n, lt, limit=200000):
    preds = [[u for u in range(n) if lt(u, v)] for v in range(n)]
    res = []

    def rec(order, placed):
        if len(res) >= limit:
            return
        if len(order) == n:
            res.append(list(order))
            return
        for v in range(n):
            if not (placed >> v) & 1 and all((placed >> u) & 1 for u in preds[v]):
                order.append(v)
                rec(order, placed | (1 << v))
                order.pop()
    rec([], 0)
    return res


def realizes(exts, n, lt):
    pos = [{v: i for i, v in enumerate(e)} for e in exts]
    for u in range(n):
        for v in range(n):
            if u != v:
                inter = all(p[u] < p[v] for p in pos)
                if inter != lt(u, v):
                    return False
    return True


def dimension(els, leq, lt, n, name):
    if name.startswith("chain"):
        return {"dimension": 1, "how": "a linear order"}
    k = len(els[0]) if isinstance(els[0], tuple) and all(isinstance(c, int) for c in els[0]) else None
    if k:
        # coordinate realizer: lex orders with each coordinate first
        exts = []
        for first in range(k):
            keyorder = [first] + [c for c in range(k) if c != first]
            exts.append(sorted(range(n), key=lambda i: tuple(els[i][c] for c in keyorder)))
        ok = realizes(exts, n, lt)
        two_ok = None
        if k == 3:
            # contains the Boolean lattice 2^3 (Komm), so no 2-realizer
            two_ok = False
        return {"dimension": k, "coordinate_realizer_verified": ok, "two_realizer": two_ok}
    exts = linear_extensions(n, lt)
    two = any(realizes([a, b], n, lt) for a, b in itertools.combinations(exts, 2))
    three = None if two else any(realizes([a, b, c], n, lt) for a, b, c in itertools.combinations(exts, 3))
    return {"linear_extensions": len(exts), "two_realizer_exists": two, "three_realizer_exists": three,
            "dimension": 2 if two else (3 if three else ">3")}


# ------------------------------------------------------------------ B. chain grid

def chain_grid_corr(L):
    R = 1 << L
    bits = (np.arange(R)[:, None] >> np.arange(L)[None, :]) & 1
    horiz = np.prod(np.where(bits != np.roll(bits, -1, axis=1), 2.0, 1.0), axis=1)
    vert = np.prod(np.where(bits[:, None, :] != bits[None, :, :], 2.0, 1.0), axis=2)
    T = horiz[:, None] * vert
    T = T / np.abs(np.linalg.eigvals(T) if L <= 8 else sla.eigs(T, k=1, which="LM", return_eigenvectors=False)).max()
    P = [np.eye(R)]
    for _ in range(L):
        P.append(P[-1] @ T)
    Z = np.trace(P[L])
    s = 1.0 - 2.0 * bits
    raw = {}
    for r in range(L):
        col = ((s[:, 0][:, None] * P[r]) * P[L - r].T).sum(axis=0)
        for c in range(L):
            raw[(c, r)] = float((col * s[:, c]).sum() / Z)
    # exact symmetry: one value per canonical displacement under the torus's eight symmetries
    def canon(dx, dy):
        a, b = min(dx % L, (-dx) % L), min(dy % L, (-dy) % L)
        return (min(a, b), max(a, b))
    groups = {}
    for (c, r), v in raw.items():
        groups.setdefault(canon(c, r), []).append(v)
    val = {k: sum(v) / len(v) for k, v in groups.items()}
    spread = max(max(v) - min(v) for v in groups.values())
    return (lambda dx, dy: 1.0 if canon(dx, dy) == (0, 0) else val[canon(dx, dy)]), spread


def chain_grid_gap(L):
    g, spread = chain_grid_corr(L)
    # distinctions: grid (x, y), horizontal private ('h', x, y) on edge (x,y)-(x+1,y), vertical ('v', x, y) on (x,y)-(x,y+1)
    nodes = [("g", x, y) for x in range(L) for y in range(L)] + [("h", x, y) for x in range(L) for y in range(L)] + \
            [("v", x, y) for x in range(L) for y in range(L)]

    def ends(a):
        if a[0] == "g":
            return [(a[1], a[2])]
        if a[0] == "h":
            return [(a[1], a[2]), ((a[1] + 1) % L, a[2])]
        return [(a[1], a[2]), (a[1], (a[2] + 1) % L)]

    def corr(a, b):
        if a == b:
            return 1.0
        ea, eb = ends(a), ends(b)
        fa = 1.0 if a[0] == "g" else -0.5
        fb = 1.0 if b[0] == "g" else -0.5
        if a[0] != "g" and b[0] != "g" or a[0] != b[0]:
            # privates are conditionally independent given the grid, with mean -(s_u + s_v)/2
            tot = sum(g(q[0] - p[0], q[1] - p[1]) for p in ea for q in eb)
            return fa * fb * tot
        return g(eb[0][0] - ea[0][0], eb[0][1] - ea[0][1])

    idx = {a: i for i, a in enumerate(nodes)}
    M = len(nodes)
    TAU = np.zeros((M, M))
    for i, a in enumerate(nodes):
        for j in range(i + 1, M):
            TAU[i, j] = TAU[j, i] = -math.log(abs(corr(a, nodes[j])), 3)

    def gap_neighbours(o):
        io = idx[o]
        t = TAU[io]
        out = []
        for jv, v in enumerate(nodes):
            if jv == io:
                continue
            block = (t < t[jv]) & (TAU[:, jv] < t[jv])
            block[io] = block[jv] = False
            if not block.any():
                out.append(v)
        return out
    # the gap graph is translation-invariant: build it from the neighbours of the three kinds of start
    nb = {k: gap_neighbours(s) for k, s in (("g", ("g", 0, 0)), ("h", ("h", 0, 0)), ("v", ("v", 0, 0)))}

    def shift(a, dx, dy):
        return (a[0], (a[1] + dx) % L, (a[2] + dy) % L)

    def neighbours(a):
        return [shift(v, a[1], a[2]) for v in nb[a[0]]]
    levels = []
    seen = {("g", 0, 0)}
    fr = [("g", 0, 0)]
    while fr:
        levels.append(len(fr))
        nf = []
        for a in fr:
            for b in neighbours(a):
                if b not in seen:
                    seen.add(b)
                    nf.append(b)
        fr = nf
    return {"symmetry_spread_of_raw_floats": spread, "degree_grid": len(nb["g"]), "degree_h": len(nb["h"]),
            "degree_v": len(nb["v"]), "levels_from_grid_start": levels}


def chain_grid_transfer_gap(L):
    R = 1 << L
    bits = (np.arange(R)[:, None] >> np.arange(L)[None, :]) & 1
    horiz = np.prod(np.where(bits != np.roll(bits, -1, axis=1), 2.0, 1.0), axis=1)
    vert = np.prod(np.where(bits[:, None, :] != bits[None, :, :], 2.0, 1.0), axis=2)
    # symmetric form: sqrt(h) V sqrt(h)
    sh = np.sqrt(horiz)
    S = sh[:, None] * vert * sh[None, :]
    ev = np.sort(np.abs(np.linalg.eigvalsh(S)))[::-1]
    return float(math.log(ev[0] / ev[1], 3))


# ------------------------------------------------------------------ C. weave

def weave_T(L):
    R = 1 << L
    a = np.arange(R)
    bit = lambda x, i: (x >> (i % L)) & 1
    T = np.ones((R, R), dtype=bool)
    for i in range(L):
        ai, ai1 = bit(a, i)[:, None], bit(a, i + 1)[:, None]
        bi, bi1 = bit(a, i)[None, :], bit(a, i + 1)[None, :]
        T &= ~((ai == ai1) & (ai1 == bi))
        T &= ~((ai1 == bi) & (bi == bi1))
    return T.astype(np.float64)


def weave_tau(L):
    T = weave_T(L)
    R = len(T)
    a = np.arange(R)
    P = [np.eye(R)]
    for _ in range(L):
        P.append(P[-1] @ T)
    Z = np.trace(P[L])
    s = 1.0 - 2.0 * ((a[:, None] >> np.arange(L)[None, :]) & 1)
    tau = {}
    for r in range(L):
        col = ((s[:, 0][:, None] * P[r]) * P[L - r].T).sum(axis=0)
        for c in range(L):
            v = float((col * s[:, c]).sum() / Z)
            tau[(c, r)] = 0.0 if (c, r) == (0, 0) else -math.log(abs(v), 3)
    return tau


def bfs_levels(L, nbrs):
    seen = {(0, 0)}
    fr = [(0, 0)]
    levels = []
    while fr:
        levels.append(len(fr))
        nf = []
        for p in fr:
            for d in nbrs:
                q = ((p[0] + d[0]) % L, (p[1] + d[1]) % L)
                if q not in seen:
                    seen.add(q)
                    nf.append(q)
        fr = nf
    return levels, len(seen)


def weave_readings(L):
    tau = weave_tau(L)
    keys = [k for k in tau if k != (0, 0)]
    t = lambda p, q: tau[((q[0] - p[0]) % L, (q[1] - p[1]) % L)]
    rng = [k for k in keys if not any(w != k and tau[w] < tau[k] - 1e-9 and t(w, k) < tau[k] - 1e-9 for w in keys)]
    srt = sorted(keys, key=lambda k: tau[k])
    k6 = srt[:6]
    ball = [k for k in keys if tau[k] <= 1 + 1e-9]
    out = {"rng_degree": len(rng), "rng_levels": bfs_levels(L, rng)[0],
           "nearest6": sorted(k6), "nearest6_levels_and_reach": bfs_levels(L, k6),
           "unit_ball_degree": len(ball), "unit_ball_levels": bfs_levels(L, ball)[0]}
    return out


def weave_gap(L):
    T = weave_T(L)
    if L <= 9:
        ev = np.linalg.eigvals(T)
    else:
        ev = sla.eigs(T, k=12, which="LM", return_eigenvectors=False)
    m = np.sort(np.abs(ev))[::-1]
    top = m[0]
    second = next(x for x in m[1:] if x < top * (1 - 1e-9))
    g = math.log(top / second, 3)
    return {"gap": g, "gap_x_width": g * L, "top_multiplicity": int(sum(abs(x - top) < top * 1e-9 for x in m))}


def main():
    out = {"implications": implication_half()}
    out["chain_grid"] = {L: {**chain_grid_gap(L), "transfer_gap": chain_grid_transfer_gap(L)} for L in (8, 10, 12)}
    out["weave"] = {L: {**weave_readings(L), **weave_gap(L)} for L in (6, 9, 12)}
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
