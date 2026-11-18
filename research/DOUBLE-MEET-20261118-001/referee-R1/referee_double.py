"""Referee R1 for DOUBLE-MEET-20261118-001 (own code; the study's weavelib.py, job.py and the pinned naelib/metriclib are not
imported).

  ../../../.venv/bin/python -B referee_double.py <part> > referee_double_<part>.json      (from this directory)

The weave: distinctions (i, j); knots u(i, j) = {(i, j), (i+1, j), (i, j+1)} and d(i, j) = {(i+1, j), (i, j+1), (i+1, j+1)}, all
not-all-equal.  A patch is a set of knots joined through shared pairs; a disc when V - E + F = 1 and the knots around every distinction
are joined through shared pairs (no pinch).  A distinction is lone when it lies in one knot of the patch.  Lone x (in knot K, whose
other distinctions are u, v) faces z when z - x = p (u - x) + q (v - x) with integers p, q >= 1 (solved in integers, not floats).
Bond distance b by testing every set (infinite when no bond holds the pair); steps apart from the knot-incidence graph.

Parts:
  discs      every disc of 1 to 10 knots (up to translation), and 2,500 random discs each of 12 and 13 knots (one size past the
             study's eleven): unbonded pairs (lone? opposite classes? facing both ways?); metric exactly when no pair is unbonded;
             bonded pairs against steps + 1 (below, equal, steps + 2 and beyond).
  pars       parallelograms of a x b sites, 2 <= a <= b, a * b <= 18: the unbonded pairs and the acute lone pair.
"""
import itertools
import json
import math
import random
import sys
from collections import Counter
from multiprocessing import Pool

import networkx as nx
import numpy as np

NAE3 = frozenset(range(1, 7))


def verts(t):
    o, i, j = t
    return ((i, j), (i + 1, j), (i, j + 1)) if o == "u" else ((i + 1, j), (i, j + 1), (i + 1, j + 1))


def adjacent(t):
    """The knots sharing a pair with t."""
    o, i, j = t
    return [("d", i, j), ("d", i - 1, j), ("d", i, j - 1)] if o == "u" else [("u", i, j), ("u", i + 1, j), ("u", i, j + 1)]


def canon(T):
    vs = [v for t in T for v in verts(t)]
    a, b = min(v[0] for v in vs), min(v[1] for v in vs)
    return frozenset((o, i - a, j - b) for o, i, j in T)


def disc(T):
    V = {v for t in T for v in verts(t)}
    E = {frozenset(e) for t in T for e in itertools.combinations(verts(t), 2)}
    if len(V) - len(E) + len(T) != 1:
        return False
    for v in V:
        star = [t for t in T if v in verts(t)]
        G = nx.Graph()
        G.add_nodes_from(range(len(star)))
        G.add_edges_from((a, b) for a, b in itertools.combinations(range(len(star)), 2)
                         if len(set(verts(star[a])) & set(verts(star[b]))) == 2)
        if not nx.is_connected(G):
            return False
    return True


def discs_upto(k):
    level = {canon({("u", 0, 0)}), canon({("d", 0, 0)})}
    allp = {1: level}
    for size in range(2, k + 1):
        nxt = set()
        for T in level:
            for t in T:
                for s in adjacent(t):
                    if s not in T:
                        nxt.add(canon(set(T) | {s}))
        level = nxt
        allp[size] = level
    return {s: [T for T in v if disc(T)] for s, v in allp.items()}


def random_disc(k, rng):
    while True:
        T = {rng.choice([("u", 0, 0), ("d", 0, 0)])}
        while len(T) < k:
            t = rng.choice(sorted(T))
            s = rng.choice(adjacent(t))
            T.add(s)
        if disc(T):
            return canon(T)


def facing(x, K, z):
    u, v = [w for w in verts(K) if w != x]
    a1, a2 = u[0] - x[0], u[1] - x[1]
    b1, b2 = v[0] - x[0], v[1] - x[1]
    c1, c2 = z[0] - x[0], z[1] - x[1]
    det = a1 * b2 - a2 * b1
    pn, qn = c1 * b2 - c2 * b1, a1 * c2 - a2 * c1
    if pn % det or qn % det:
        return False
    return pn // det >= 1 and qn // det >= 1


def states(n, ts):
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for a, b, c in ts:
        x, y, z = (s >> a) & 1, (s >> b) & 1, (s >> c) & 1
        ok &= ~((x == y) & (y == z))
    return s[ok]


def bonds_matrix(n, st):
    free = np.zeros(1 << n, dtype=bool)
    for m in range(1 << n):
        code = np.zeros(len(st), dtype=np.int64)
        k = 0
        for v in range(n):
            if (m >> v) & 1:
                code |= ((st >> v) & 1) << k
                k += 1
        free[m] = bool(np.all(np.bincount(code, minlength=1 << k)))
    D = [[math.inf] * n for _ in range(n)]
    for m in range(1, 1 << n):
        if free[m] or not all(free[m & ~(1 << i)] for i in range(n) if (m >> i) & 1):
            continue
        vs = [i for i in range(n) if (m >> i) & 1]
        for x, y in itertools.combinations(vs, 2):
            D[x][y] = D[y][x] = min(D[x][y], len(vs) - 1)
    return D


def judge(T):
    T = sorted(T)
    V = sorted({v for t in T for v in verts(t)})
    ix = {v: k for k, v in enumerate(V)}
    n = len(V)
    ts = [tuple(ix[v] for v in verts(t)) for t in T]
    D = bonds_matrix(n, states(n, ts))
    G = nx.Graph()
    for k, t in enumerate(ts):
        for v in t:
            G.add_edge(("k", k), ("d", v))
    sp = dict(nx.all_pairs_shortest_path_length(G))
    deg = Counter(v for t in T for v in verts(t))
    lone = {v: next(t for t in T if v in verts(t)) for v in V if deg[v] == 1}
    r = Counter()
    for x, z in itertools.combinations(V, 2):
        b = D[ix[x]][ix[z]]
        s = sp[("d", ix[x])][("d", ix[z])] // 2
        r["pairs"] += 1
        if b == math.inf:
            r["unbonded"] += 1
            ok = x in lone and z in lone and lone[x][0] != lone[z][0] and facing(x, lone[x], z) and facing(z, lone[z], x)
            r["unbonded_lone_opposite_facing"] += ok
        else:
            r["bonded"] += 1
            r[f"b_minus_steps_{b - s}"] += 1
    viol = sum(1 for x, z in itertools.combinations(range(n), 2) for y in range(n)
               if y not in (x, z) and D[x][z] > D[x][y] + D[y][z])
    finite_viol = sum(1 for x, z in itertools.combinations(range(n), 2) for y in range(n)
                      if y not in (x, z) and D[x][z] < math.inf and D[x][z] > D[x][y] + D[y][z])
    r["patches"] = 1
    r["metric"] = int(viol == 0)
    r["metric_iff_no_unbonded"] = int((viol == 0) == (r["unbonded"] == 0))
    r["finite_violations"] = finite_viol
    facing_pairs = [(x, z) for x, z in itertools.combinations(sorted(lone), 2) if lone[x][0] != lone[z][0]
                    and facing(x, lone[x], z) and facing(z, lone[z], x)]
    r["facing_pairs"] += len(facing_pairs)
    r["facing_bonded"] += sum(1 for x, z in facing_pairs if D[ix[x]][ix[z]] < math.inf)
    return dict(r)


def add(acc, r):
    for k, v in r.items():
        acc[k] = acc.get(k, 0) + v


def part_discs(workers=16):
    by = discs_upto(10)
    rng = random.Random("referee-double-meet")
    jobs = [T for s in range(1, 11) for T in by[s]]
    extra = {12: [random_disc(12, rng) for _ in range(2500)], 13: [random_disc(13, rng) for _ in range(2500)]}
    with Pool(workers) as P:
        res = P.map(judge, jobs, chunksize=32)
        res12 = P.map(judge, extra[12], chunksize=16)
        res13 = P.map(judge, extra[13], chunksize=16)
    out = {"discs_by_size": {s: len(by[s]) for s in range(1, 11)}}
    for name, R in (("every disc to 10 knots", res), ("random discs of 12 knots", res12), ("random discs of 13 knots", res13)):
        acc = {}
        for r in R:
            add(acc, r)
        out[name] = dict(sorted(acc.items()))
    return out


def parallelogram(a, b):
    sites = {(i, j) for i in range(a) for j in range(b)}
    return [t for i in range(a) for j in range(b) for t in (("u", i, j), ("d", i, j)) if all(v in sites for v in verts(t))]


def part_pars():
    out = {}
    for a in range(2, 5):
        for b in range(a, 10):
            if a * b > 18:
                continue
            T = parallelogram(a, b)
            V = sorted({v for t in T for v in verts(t)})
            ix = {v: k for k, v in enumerate(V)}
            n = len(V)
            ts = [tuple(ix[v] for v in verts(t)) for t in T]
            D = bonds_matrix(n, states(n, ts))
            unb = [(V[x], V[z]) for x, z in itertools.combinations(range(n), 2) if D[x][z] == math.inf]
            deg = Counter(v for t in T for v in verts(t))
            lone = sorted(v for v in V if deg[v] == 1)
            out[f"{a}x{b}"] = {"distinctions": n, "unbonded": unb, "lone": lone}
            print("pars", a, b, out[f"{a}x{b}"], file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"discs": part_discs, "pars": part_pars}[part]
    print(json.dumps(f(), indent=1, default=str))
