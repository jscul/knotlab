"""Referee R1 for WEAVE-HEIGHTS-20261118-001 (own code; the study's job.py and the pinned weavelib/naelib/metriclib are not imported).

  ../../../.venv/bin/python -B referee_heights.py > referee_heights.json      (from this directory)

Discs from the referee's DOUBLE-MEET-R1 code (`referee_double`: its own weave, disc test and states).  D(s, t) is the least weight of a
walk along pairs of the patch, a forward step (e1 = (1, 0), e2 = (-1, 1), e3 = (0, -1)) weighing 1 and a backward step 2, by the
referee's own Dijkstra.  Checks:
  (a) every disc to 10 knots, and 1,500 random discs each of 13 and 14 knots: flagness (every three pairwise co-knotted distinctions
      a knot), no level knot from any distinction (Lemma 5's conclusion), D(x, y) + D(y, x) = 3 steps apart (Lemma 6), and the lone
      identities (Lemma 8);
  (b) Proposition 3 set by set on every disc to 10 knots (the study went to 8): a set is constrained (from the states) exactly when
      some m >= 3 of its members have a cyclic order with D-sum <= 3(m - 2), the least cyclic D-sum of every subset found by the
      referee's own Held-Karp;
  (c) Lemma 1's count on every disc to 8 knots: the number of states equals 2 x the number of ways to choose one falling pair per knot
      consistently.
Theorem 7 one size past (b >= steps + 1 on random discs of 12 and 13 knots) was computed in the referee's DOUBLE-MEET-R1 census.
"""
import heapq
import itertools
import json
import math
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/DOUBLE-MEET-20261118-001/referee-R1"))
import referee_double as RD  # noqa: E402

FWD = {(1, 0), (-1, 1), (0, -1)}


def walk_weights(V, E):
    adj = {v: [] for v in V}
    for a, b in E:
        d = (b[0] - a[0], b[1] - a[1])
        f, g = (a, b) if d in FWD else (b, a)
        adj[f].append((g, 1))
        adj[g].append((f, 2))
    D = {}
    for s in V:
        dist = {s: 0}
        pq = [(0, s)]
        while pq:
            d0, u = heapq.heappop(pq)
            if d0 > dist[u]:
                continue
            for w, c in adj[u]:
                if d0 + c < dist.get(w, math.inf):
                    dist[w] = d0 + c
                    heapq.heappush(pq, (d0 + c, w))
        D[s] = dist
    return D


def least_cycles(V, D):
    """For every subset R (bit mask over V) of at least three members, the least D-sum of a cyclic order of R (Held-Karp)."""
    n = len(V)
    W = np.array([[D[V[a]][V[b]] for b in range(n)] for a in range(n)], dtype=np.float64)
    # dp[mask, last]: least D-sum of a path from the lowest member of mask through all of mask, ending at last
    dp = np.full((1 << n, n), np.inf)
    for s in range(n):
        dp[1 << s, s] = 0
    best = np.full(1 << n, np.inf)
    for mask in range(1, 1 << n):
        row = dp[mask]
        if not np.isfinite(row).any():
            continue
        s = (mask & -mask).bit_length() - 1
        if bin(mask).count("1") >= 3:
            best[mask] = (row + W[:, s]).min()
        cand = (row[:, None] + W).min(axis=0)
        for nx_ in range(s + 1, n):
            if not (mask >> nx_) & 1:
                k = mask | (1 << nx_)
                if cand[nx_] < dp[k, nx_]:
                    dp[k, nx_] = cand[nx_]
    return best


def check(args):
    T, do_prop3, do_count = args
    T = sorted(T)
    V = sorted({v for t in T for v in RD.verts(t)})
    E = {tuple(sorted(e)) for t in T for e in itertools.combinations(RD.verts(t), 2)}
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)
    knots = {frozenset(RD.verts(t)) for t in T}
    r = Counter(discs=1)
    r["flag_fail"] = sum(1 for c in nx.enumerate_all_cliques(G) if len(c) == 3 and frozenset(c) not in knots)
    sp = dict(nx.all_pairs_shortest_path_length(G))
    for x in V:
        for t in T:
            if len({sp[x][v] for v in RD.verts(t)}) == 1:
                r["level_knots"] += 1
    # Lemma 5's cited ingredients, checked on the graphs themselves: every ball convex, and the triangle condition
    n0 = len(V)
    M = np.array([[sp[a][b] for b in V] for a in V])
    A = M == 1
    I = (M[:, None, :] + M.T[None, :, :]) == M[:, :, None]  # I[a, b, v]: v on a geodesic from a to b
    for xi in range(n0):
        for t in range(int(M[xi].max()) + 1):
            ball = M[xi] <= t
            r["balls"] += 1
            r["ball_not_convex"] += bool((I[np.ix_(ball, ball)] & ~ball[None, None, :]).any())
        for a in range(n0):
            for b in range(a + 1, n0):
                if A[a, b] and M[xi, a] == M[xi, b] >= 1:
                    r["triangle_cases"] += 1
                    r["triangle_fail"] += not (A[a] & A[b] & (M[xi] == M[xi, a] - 1)).any()
    D = walk_weights(V, E)
    for a, b in itertools.combinations(V, 2):
        r["round_trip_fail"] += D[a][b] + D[b][a] != 3 * sp[a][b]
    deg = Counter(v for t in T for v in RD.verts(t))
    for x in V:
        if deg[x] != 1:
            continue
        K = next(t for t in T if x in RD.verts(t))
        ks = RD.verts(K)
        # the forward 3-cycle through x: x -> u -> v -> x
        u = next(w for w in ks if w != x and (w[0] - x[0], w[1] - x[1]) in FWD)
        v = next(w for w in ks if w not in (x, u))
        for s in V:
            if s != x:
                r["lone_fail"] += D[s][x] != D[s][v] + 1
                r["lone_fail"] += D[x][s] != 1 + D[u][s]
    if do_prop3 or do_count:
        ix = {v: i for i, v in enumerate(V)}
        n = len(V)
        st = RD.states(n, [tuple(ix[w] for w in RD.verts(t)) for t in T])
    if do_count:
        pairs_of = [list(itertools.combinations(sorted(RD.verts(t)), 2)) for t in T]
        count = 0
        for choice in itertools.product(range(3), repeat=len(pairs_of)):
            fall = {}
            ok = True
            for kn, ch in zip(pairs_of, choice):
                for j, p in enumerate(kn):
                    want = j == ch
                    if fall.setdefault(p, want) != want:
                        ok = False
                        break
                if not ok:
                    break
            count += ok
        r["count_checked"] += 1
        r["count_fail"] += len(st) != 2 * count
    if do_prop3:
        best = least_cycles(V, D)
        size = np.array([bin(m).count("1") for m in range(1 << n)])
        tight = (size >= 3) & (best <= 3 * (size - 2))
        # a control: the bound one notch lower, 3(m - 3), must fail somewhere if the check can see anything
        loose = (size >= 3) & (best <= 3 * (size - 3))

        def up(f):  # constrained by the criterion: some tight subset (propagate up through supersets)
            f = f.copy()
            for i in range(n):
                bit = 1 << i
                for mask in range(1 << n):
                    if mask & bit and f[mask ^ bit]:
                        f[mask] = True
            return f
        crit, crit_lower = up(tight), up(loose)
        for mask in range(1 << n):
            code = np.zeros(len(st), dtype=np.int64)
            k = 0
            for i in range(n):
                if (mask >> i) & 1:
                    code |= ((st >> i) & 1) << k
                    k += 1
            constrained = not np.all(np.bincount(code, minlength=1 << k))
            r["sets"] += 1
            r["constrained"] += constrained
            r["criterion_fail"] += constrained != bool(crit[mask])
            r["control_fail (bound 3(m - 3))"] += constrained != bool(crit_lower[mask])
    return dict(r)


def part(workers=16):
    by = RD.discs_upto(10)
    rng = random.Random("referee-weave-heights")
    jobs = [(T, True, s <= 8) for s in range(1, 11) for T in by[s]]
    p12 = [(RD.random_disc(12, rng), True, False) for _ in range(300)]
    extra = [(RD.random_disc(13, rng), False, False) for _ in range(3000)] + [(RD.random_disc(14, rng), False, False) for _ in range(3000)]
    out = {"discs_by_size": {s: len(by[s]) for s in by}}
    with Pool(workers) as P:
        for name, J in (("every disc to 10 knots", jobs), ("300 random discs of 12 knots, Proposition 3 set by set", p12),
                        ("3,000 random discs each of 13 and 14 knots", extra)):
            acc = Counter()
            for r in P.map(check, J, chunksize=8):
                acc.update(r)
            out[name] = dict(sorted(acc.items()))
            print(name, out[name], file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    print(json.dumps(part(), indent=1, default=str))
