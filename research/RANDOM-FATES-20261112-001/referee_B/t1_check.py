"""Independent referee check of T1 (Berge-acyclic 3-uniform hypergraphs under NAE / proper 2-colouring).

For each hypergraph H on n vertices:
  - allowed states = proper 2-colourings (no edge monochromatic), enumerated by bit tricks;
  - free[m] for every vertex subset m (projection of allowed states onto m is all of {0,1}^m);
  - bonds = non-free sets all of whose one-smaller subsets are free (and some state exists);
  - for each pair u, v: least bond size vs primal-graph distance d (expect d + 2; none across components);
  - no constrained pair; constrained triples with free pairs == edges;
  - Lemma C on every bond: in one component, every span-degree-1 vertex of T(S) lies in S, |S| >= t + 2;
  - alternating chain built from the incidence path is a bond of size d + 2.
Generators: (1) exhaustive over all Berge-acyclic edge sets on n <= 8 labelled vertices;
            (2) random union-find forests (uniform and hub-biased) on 9..13 vertices with isolated vertices and
                several components.
"""
import itertools
import random
import sys
from collections import deque

import numpy as np


def allowed_states(n, edges):
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for e in edges:
        m = sum(1 << v for v in e)
        x = s & m
        ok &= (x != 0) & (x != m)
    return s[ok]


def free_table(n, st):
    N = 1 << n
    free = np.zeros(N, dtype=bool)
    if len(st) == 0:
        return free
    pc = np.array([bin(m).count("1") for m in range(N)])
    for m in range(N):
        proj = np.unique(st & m)
        free[m] = (proj.size == (1 << pc[m]))
    return free, pc


def bonds_of(n, free, pc):
    out = []
    for m in range(1, 1 << n):
        if free[m]:
            continue
        good = True
        x = m
        while x:
            b = x & -x
            if not free[m ^ b]:
                good = False
                break
            x ^= b
        if good:
            out.append(m)
    return out


def primal_dist(n, edges):
    nbr = [set() for _ in range(n)]
    for e in edges:
        for a in e:
            for b in e:
                if a != b:
                    nbr[a].add(b)
    D = [[None] * n for _ in range(n)]
    for s in range(n):
        D[s][s] = 0
        q = deque([s])
        while q:
            x = q.popleft()
            for y in nbr[x]:
                if D[s][y] is None:
                    D[s][y] = D[s][x] + 1
                    q.append(y)
    return D


def incidence_path(n, edges, u, v):
    """Path u - K1 - c1 - ... - Kd - v in the incidence forest; returns list of edge indices or None."""
    # nodes: vertices 0..n-1, knots n..n+len(edges)-1
    adj = [[] for _ in range(n + len(edges))]
    for i, e in enumerate(edges):
        for x in e:
            adj[x].append(n + i)
            adj[n + i].append(x)
    prev = {u: None}
    q = deque([u])
    while q:
        x = q.popleft()
        for y in adj[x]:
            if y not in prev:
                prev[y] = x
                q.append(y)
    if v not in prev:
        return None
    path = []
    x = v
    while x is not None:
        path.append(x)
        x = prev[x]
    path.reverse()
    return path  # alternating vertex, knot, vertex, ...


def span(n, edges, S):
    """T(S): knot indices on the union of incidence paths between members of S (S in one component, |S| >= 2)."""
    S = list(S)
    ks = set()
    for a, b in itertools.combinations(S, 2):
        p = incidence_path(n, edges, a, b)
        if p is None:
            return None
        ks |= {x - n for x in p if x >= n}
    return ks


def is_berge_acyclic(n, edges):
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for e in edges:
        r = {f(x) for x in e}
        if len(r) < 3:
            return False
        r = list(r)
        for x in r[1:]:
            par[x] = r[0]
    return True


def check(n, edges, stats):
    st = allowed_states(n, edges)
    assert len(st) > 0, ("no state", n, edges)
    free, pc = free_table(n, st)
    bonds = bonds_of(n, free, pc)
    D = primal_dist(n, edges)
    eset = {sum(1 << v for v in e) for e in edges}
    viol = []
    # no constrained pair, no frozen vertex
    for v in range(n):
        if not free[1 << v]:
            viol.append(("frozen", v))
    for a, b in itertools.combinations(range(n), 2):
        if not free[(1 << a) | (1 << b)]:
            viol.append(("tie", a, b))
    # hollow triples == edges
    for t in itertools.combinations(range(n), 3):
        m = sum(1 << v for v in t)
        hollow = (not free[m]) and all(free[m ^ (1 << v)] for v in t)
        if hollow != (m in eset):
            viol.append(("triple", t))
    # least bond per pair
    least = {}
    for m in bonds:
        k = pc[m]
        verts = [v for v in range(n) if m >> v & 1]
        for a, b in itertools.combinations(verts, 2):
            if (a, b) not in least or least[(a, b)] > k:
                least[(a, b)] = k
    for a, b in itertools.combinations(range(n), 2):
        d = D[a][b]
        lb = least.get((a, b))
        stats["pairs"] += 1
        if d is not None:
            stats["by_d"][d] = stats["by_d"].get(d, 0) + 1
        if d is None:
            if lb is not None:
                viol.append(("crossbond", a, b, lb))
        elif lb != d + 2:
            viol.append(("least", a, b, d, lb))
    # Lemma C on every bond
    for m in bonds:
        S = [v for v in range(n) if m >> v & 1]
        stats["bonds"] += 1
        if len(S) < 2:
            viol.append(("small bond", S))
            continue
        T = span(n, edges, S)
        if T is None:
            viol.append(("bond across comps", S))
            continue
        deg = {}
        for i in T:
            for x in edges[i]:
                deg[x] = deg.get(x, 0) + 1
        t = len(T)
        if len(deg) != 2 * t + 1:
            viol.append(("span not hypertree?", S))
        leaves = {x for x, c in deg.items() if c == 1}
        if not leaves <= set(S):
            viol.append(("lemmaC", S))
        if len(S) < t + 2:
            viol.append(("count", S, t))
        if set(S) == leaves:
            stats["bond_eq_leafset"] += 1
        stats["max_hub"] = max(stats["max_hub"], max(sum(1 for e in edges if x in e) for x in range(n)))
    # alternating chain for every connected pair
    for u, v in itertools.combinations(range(n), 2):
        p = incidence_path(n, edges, u, v)
        if p is None:
            continue
        knots = [x - n for x in p if x >= n]
        cs = [x for x in p if x < n]  # u, c1, ..., c_{d-1}, v
        d = len(knots)
        S = {u, v}
        for i, ki in enumerate(knots):
            third = [x for x in edges[ki] if x != cs[i] and x != cs[i + 1]]
            assert len(third) == 1
            S.add(third[0])
        if d == 1:
            S = set(edges[knots[0]])
        m = sum(1 << x for x in S)
        isb = (not free[m]) and all(free[m ^ (1 << x)] for x in S)
        if not (isb and len(S) == d + 2):
            viol.append(("chain", u, v, sorted(S)))
        stats["chains"] += 1
    return viol


def random_forest(n, rng, kmax, hub):
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    edges = []
    deg = [0] * n
    tries = 0
    target = rng.randint(1, kmax)
    while len(edges) < target and tries < 2000:
        tries += 1
        if hub:
            wts = [(deg[x] + 1) ** 3 for x in range(n)]
            t = set()
            while len(t) < 3:
                t.add(rng.choices(range(n), weights=wts)[0] if len(t) == 0 else rng.randrange(n))
            t = tuple(sorted(t))
        else:
            t = tuple(sorted(rng.sample(range(n), 3)))
        r = {f(x) for x in t}
        if len(r) < 3:
            continue
        r = list(r)
        for x in r[1:]:
            par[x] = r[0]
        edges.append(t)
        for x in t:
            deg[x] += 1
    return edges


def main():
    mode = sys.argv[1]
    stats = {"graphs": 0, "pairs": 0, "bonds": 0, "chains": 0, "by_d": {}, "bond_eq_leafset": 0, "max_hub": 0,
             "multi_comp": 0}
    allviol = []
    if mode == "exhaustive":
        nmax = int(sys.argv[2])
        for n in range(3, nmax + 1):
            trip = list(itertools.combinations(range(n), 3))
            kmax = (n - 1) // 2
            cnt = 0
            for k in range(1, kmax + 1):
                for E in itertools.combinations(trip, k):
                    if not is_berge_acyclic(n, E):
                        continue
                    E = list(E)
                    v = check(n, E, stats)
                    stats["graphs"] += 1
                    cnt += 1
                    if v:
                        allviol.append((n, E, v[:3]))
            print("n", n, "Berge-acyclic edge sets", cnt, flush=True)
    else:
        seed = int(sys.argv[2])
        count = int(sys.argv[3])
        rng = random.Random(seed)
        for it in range(count):
            n = rng.randint(9, 13)
            hub = rng.random() < 0.5
            edges = random_forest(n, rng, (n - 1) // 2, hub)
            # count components with knots
            par = list(range(n))

            def f(x):
                while par[x] != x:
                    x = par[x]
                return x
            for e in edges:
                for x in e[1:]:
                    a, b = f(e[0]), f(x)
                    if a != b:
                        par[a] = b
            comps = len({f(e[0]) for e in edges})
            if comps >= 2:
                stats["multi_comp"] += 1
            v = check(n, edges, stats)
            stats["graphs"] += 1
            if v:
                allviol.append((n, edges, v[:3]))
    print(stats)
    print("violations", len(allviol))
    for x in allviol[:10]:
        print(x)


if __name__ == "__main__":
    main()
