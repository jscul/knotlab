"""Shared-runner job for the referee's check of RING-IDENT-20261119-001A-P001 (own scope test, own girth, own growth, own cover and
cluster enumeration; the study's covermodel.in_scope and bare_sizes run read-only only as a labelled cross-check of the scope).

For every connected knot graph K on 3 to 7 knots (networkx's atlas) with no surplus or one surplus distinction at one knot, and for
a sample of connected graphs on 8 knots (one size past):
- round-1 groups with every knot live (the referee's engine, from a provisional start with ample places), demand d_k, bare sizes
  max(3, sh_k + d_k) + s_k; the scope (S1) to (S5) by the referee's own test;
- the candidate complex X and the girth of its incidence graph (shortest cycle by breadth-first search); Lemma 1 tested on every
  start satisfying (S3) and (S4), in scope or not;
- for in-scope starts: the growth by the referee's engine (complete rounds, fewest counts, GF(2) implication) to round 6, each
  junction's key (parents, fresh distinctions, and the sorted keys of its parents; a knot: (0, its loose distinctions)); and the
  clusters of the universal cover of X, enumerated lazily (cover points as non-backtracking walks from a base lift) by a frontier
  enumeration that meets each connected set containing the root once, each with key (|R*(C)|, |boundary(C)|, the sorted keys of
  C - v for v in R*(C)), summed over the base lift of every point of X with weight 1/|C|.  The multisets per round are compared.
- the two stars joined at their centres (Proposition 5): the growth's counts to round 10 against the cluster orbits per size.

  .venv/bin/python -B scripts/longrun.py launch research/RING-IDENT-20261119-001/referee-R1/job_ring.py \\
      --out runs/referee-ring --unit referee-ring --workers 6 --case-timeout 3600 --case-mem 2G --mem-max 16G
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
T = 6


def stars_of(n, edges, sizes):
    S = [[] for _ in range(n)]
    b = 0
    for i, j in edges:
        S[i].append(b)
        S[j].append(b)
        b += 1
    for k in range(n):
        while len(S[k]) < sizes[k]:
            S[k].append(b)
            b += 1
    return S


def round1(n, edges):
    import referee_first as RFK
    sh = Counter(x for e in edges for x in e)
    G = RFK.Start(stars_of(n, edges, [sh[k] + n + 3 for k in range(n)]))
    groups = G.groups(list(range(n)), None)
    d = Counter(x for g in groups for x in g)
    return [sh[k] for k in range(n)], [d[k] for k in range(n)], groups


def scope(n, edges, surplus):
    sh, d, groups = round1(n, edges)
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    s = [surplus.get(k, 0) for k in range(n)]
    S1 = all(sh[k] + d[k] >= 3 for k in range(n))
    S2 = all(s[k] == 0 or d[k] >= 2 for k in range(n))
    S3 = all(len(g) <= 2 for g in groups)
    S4 = all(len(nb[a] & nb[b]) <= 1 for a, b in itertools.combinations(range(n), 2))
    S5 = len(edges) >= n
    sizes = [max(3, sh[k] + d[k]) + s[k] for k in range(n)]
    return {"S1": S1, "S2": S2, "S3": S3, "S4": S4, "S5": S5}, sizes, nb


def complex_of(n, nb, surplus):
    """Points 0..n-1 (knots) and n.. (surplus points); blocks as tuples."""
    blocks = [tuple(sorted(nb[w])) for w in range(n) if len(nb[w]) >= 2]
    pts = n
    for k in range(n):
        for _ in range(surplus.get(k, 0)):
            blocks.append((k, pts))
            pts += 1
    return pts, blocks


def girth(npts, blocks):
    """Shortest cycle of the point-block incidence graph (bipartite), by breadth-first search from every node."""
    adj = defaultdict(list)
    for i, B in enumerate(blocks):
        for v in B:
            adj[("p", v)].append(("b", i))
            adj[("b", i)].append(("p", v))
    best = None
    for s in list(adj):
        dist, par = {s: 0}, {s: None}
        q = deque([s])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    par[y] = x
                    q.append(y)
                elif par[x] != y:
                    L = dist[x] + dist[y] + 1
                    best = L if best is None else min(best, L)
    return best


class Cover:
    """Lazy universal cover of the incidence graph from a base point: a cover point is a tuple (x0, (B1, x1), (B2, x2), ...)."""

    def __init__(self, npts, blocks):
        self.at = defaultdict(list)
        for i, B in enumerate(blocks):
            for v in B:
                self.at[v].append(i)
        self.blocks = blocks
        self.memo = {}

    def proj(self, p):
        return p[0] if len(p) == 1 else p[-1][1]

    def nbrs(self, p):
        if p in self.memo:
            return self.memo[p]
        out = []
        x = self.proj(p)
        came = None if len(p) == 1 else p[-1][0]
        if came is not None:
            par = p[:-1]
            out.append(par)
            px = self.proj(par)
            for y in self.blocks[came]:
                if y != px and y != x:
                    out.append(par + ((came, y),))
        for bi in self.at[x]:
            if bi == came:
                continue
            for y in self.blocks[bi]:
                if y != x:
                    out.append(p + ((bi, y),))
        self.memo[p] = out
        return out


def clusters(cov, root, m):
    """Every connected set of at most m cover points containing root, once each (frontier enumeration)."""
    out = []

    def rec(S, frontier, banned):
        out.append(S)
        if len(S) == m:
            return
        fr = list(frontier)
        for i, w in enumerate(fr):
            S2 = S | {w}
            ban2 = banned | set(fr[:i + 1])
            new = [x for x in cov.nbrs(w) if x not in S2 and x not in ban2 and x not in fr[i + 1:]]
            rec(S2, fr[i + 1:] + new, ban2)
    rec(frozenset([root]), list(cov.nbrs(root)), {root})
    return out


def model_keys(n, npts, blocks, m):
    cov = Cover(npts, blocks)
    inv = defaultdict(Counter)

    def connected(R):
        R = set(R)
        if not R:
            return False
        st = [next(iter(R))]
        seen = {st[0]}
        while st:
            a = st.pop()
            for b in cov.nbrs(a):
                if b in R and b not in seen:
                    seen.add(b)
                    st.append(b)
        return len(seen) == len(R)

    def rstar(S):
        return [v for v in S if any(cov.proj(x) < n for x in S - {v}) and connected(S - {v})]

    def bd(S):
        return len({y for v in S for y in cov.nbrs(v)} - S)
    for x in range(npts):
        for S in clusters(cov, (x,), m):
            if not any(cov.proj(v) < n for v in S):
                continue
            R = rstar(S)
            key = (len(R), bd(S), tuple(sorted((len(rstar(S - {v})), bd(S - {v})) for v in R)))
            inv[len(S) - 1][key] += Fraction(1, len(S))
    return inv


def growth_keys(n, edges, sizes, rounds):
    import referee_first as RFK
    G = RFK.Start(stars_of(n, edges, sizes))
    inv = defaultdict(Counter)
    base = {}
    for j in range(n):
        base[j] = (0, len(G.loose(j)))
        inv[0][(0, len(G.loose(j)), ())] += 1
    counts = [n]
    for t in range(1, rounds + 1):
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            counts.append(r)
            break
        new = [j for j in range(len(G.bits)) if G.round[j] == t]
        counts.append(len(new))
        for j in new:
            base[j] = (len(G.parents[j]), G.fresh[j])
        for j in new:
            inv[t][(base[j][0], base[j][1], tuple(sorted(base[q] for q in G.parents[j])))] += 1
    return inv, counts


def check(n, edges, surplus, rounds=T):
    sc, sizes, nb = scope(n, edges, surplus)
    npts, blocks = complex_of(n, nb, surplus)
    g = girth(npts, blocks)
    row = {"n": n, "edges": edges, "surplus": surplus, "scope": sc, "girth": g, "sizes": sizes}
    if all(sc[k] for k in ("S1", "S2", "S3", "S4")):
        a, counts = growth_keys(n, edges, sizes, rounds)
        b = model_keys(n, npts, blocks, rounds + 1)
        row["growth counts"] = counts
        row["orbits per size"] = [str(sum(b[t].values())) for t in range(rounds + 1)]
        bad = [t for t in range(rounds + 1) if {k: Fraction(v) for k, v in a.get(t, {}).items()} != {k: v for k, v in b.get(t, {}).items() if v}]
        row["keys agree"] = not bad
        row["rounds that differ"] = bad
    return row


def cases():
    import networkx as nx
    items = []
    for G in nx.graph_atlas_g():
        if 3 <= G.number_of_nodes() <= 7 and nx.is_connected(G):
            n = G.number_of_nodes()
            edges = sorted(tuple(sorted(e)) for e in G.edges())
            items.append([n, edges])
    for a in range(0, len(items), 40):
        yield f"A-{a // 40:03d}", {"part": "A", "graphs": items[a:a + 40]}
    rng = random.Random(20261119)
    seen, sample = [], []
    tries = 0
    while len(sample) < 80 and tries < 200000:
        tries += 1
        m = rng.randint(8, 11)
        G = nx.gnm_random_graph(8, m, seed=rng.randrange(10 ** 9))
        if not nx.is_connected(G) or nx.is_tree(G):
            continue
        if any(len(c) <= 4 for c in nx.minimum_cycle_basis(G)):
            continue
        if any(nx.is_isomorphic(G, H) for H in seen):
            continue
        seen.append(G)
        sample.append([8, sorted(tuple(sorted(e)) for e in G.edges())])
    for a in range(0, len(sample), 4):
        yield f"B-{a // 4:03d}", {"part": "B", "graphs": sample[a:a + 4]}
    yield "P5", {"part": "P5"}


def run(case_id, p):
    if p["part"] == "P5":
        n, edges = 6, [(0, 1), (0, 2), (0, 3), (3, 4), (3, 5)]
        sc, sizes, nb = scope(n, edges, {})
        npts, blocks = complex_of(n, nb, {})
        _, counts = growth_keys(n, edges, sizes, 10)
        b = model_keys(n, npts, blocks, 6)
        return {"scope": sc, "sizes": sizes, "blocks": blocks, "growth counts": counts,
                "cluster orbits per size 1..7": [str(sum(b[t].values())) for t in range(7)]}
    rows = []
    for n, edges in p["graphs"]:
        edges = [tuple(e) for e in edges]
        for surplus in [{}] + [{k: 1} for k in range(n)]:
            rows.append(check(n, edges, surplus))
    return {"rows": rows}
