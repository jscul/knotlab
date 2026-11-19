"""Shared-runner job for the referee's check of CHAIN-IDENT-20261119-001A-P001 (own extended complex, own class test, own growth,
own lazy cover and cluster enumeration from RING-IDENT-R1's job_ring.py; no study code imported or run).

For every connected knot graph K on 2 to 7 knots (networkx's atlas) with no surplus or one surplus distinction at one knot, and one
size past (all 23 trees on 8 knots, and a sample of 8-knot graphs with a cycle, the same surplus variants):
- bare sizes from the referee's round-1 groups (every knot live), open_k, live knots, s_k = open_k - d_k;
- X+: live knots, blocks N(w) restricted to live knots (w with two or more live neighbours), s_k pendant points per live knot,
  R(open_k) rays at each (0, 1, 2 for open >= 3, 2, 1), truncated at T + 3 points;
- the class by the referee's own test: (S3) no round-1 group of three or more, (S4) no two knots with two common neighbours, (S5+)
  every component of X+ holding a live knot has a cycle in its core or a ray;
- in the class and in the relay class (S5+ failing), per round to T = 6: each junction's key (parents, fresh, its parents' keys)
  from the referee's engine (complete rounds, fewest counts, GF(2) implication) against each cluster orbit's key (|R*|, |boundary|,
  the keys of C - v), with the non-live knots added at round 0;
- for trees in the class, Theorem 2: the counts c(0..20) from the growth against the cluster count by Theorem 2's composition
  formula (cores F_Y, their clusters Q holding a knot, the rays based in Q), the degree R - 1, and the (R - 1)-th difference against
  (sum of N_Y over components with R rays) for t >= max |F_Y|;
- the four named starts (a pair, the paths of three, four and five knots): the growth's counts to round 12 against the cluster
  orbits per size.

  .venv/bin/python -B scripts/longrun.py launch research/CHAIN-IDENT-20261119-001/referee-R1/job_chain.py \\
      --out runs/referee-chain --unit referee-chain --workers 6 --case-timeout 3600 --case-mem 2G --mem-max 16G
"""
import itertools
import json
import math
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/RING-IDENT-20261119-001/referee-R1"))
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
T = 6
T2 = 20


def plus(n, edges, surplus, ray_len=T + 3):
    import job_ring as JR
    sh, d, groups = JR.round1(n, edges)
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    sizes = [max(3, sh[k] + d[k]) + surplus.get(k, 0) for k in range(n)]
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    ls = set(live)
    blocks = [tuple(sorted(nb[w] & ls)) for w in range(n) if len(nb[w] & ls) >= 2]
    nxt = n
    pend = []                                           # (knot, pendant point, number of rays, [ray point lists])
    for k in live:
        R = 0 if opn[k] >= 3 else (1 if opn[k] == 2 else 2)
        for _ in range(opn[k] - d[k]):
            o = nxt
            nxt += 1
            blocks.append((k, o))
            rays = []
            for _ in range(R):
                prev, pts = o, []
                for _ in range(ray_len):
                    blocks.append((prev, nxt))
                    pts.append(nxt)
                    prev = nxt
                    nxt += 1
                rays.append(pts)
            pend.append((k, o, R, rays))
    S3 = all(len(g) <= 2 for g in groups)
    S4 = all(len(nb[a] & nb[b]) <= 1 for a, b in itertools.combinations(range(n), 2))
    # S5+: components of the core (live knots, pendant points, core blocks)
    core_blocks = [B for B in blocks if all(x < n or any(x == p[1] for p in pend) for x in B)]
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x
    for B in core_blocks:
        for x in B[1:]:
            parent[find(x)] = find(B[0])
    comps = defaultdict(lambda: {"knots": set(), "points": set(), "blocks": 0, "inc": 0, "rays": 0})
    for k in live:
        comps[find(k)]["knots"].add(k)
    for B in core_blocks:
        c = comps[find(B[0])]
        c["blocks"] += 1
        c["inc"] += len(B)
        c["points"] |= set(B)
    for k, o, R, _ in pend:
        comps[find(k)]["rays"] += R
    S5 = True
    for c in comps.values():
        if not c["knots"]:
            continue
        pts = c["points"] | c["knots"]
        cycle = c["inc"] > len(pts) + c["blocks"] - 1        # incidence graph has more lines than a tree on its nodes
        if not cycle and c["rays"] == 0:
            S5 = False
    return {"sizes": sizes, "open": opn, "live": live, "d": d, "blocks": blocks, "npts": nxt, "pend": pend, "S3": S3, "S4": S4,
            "S5+": S5, "comps": comps, "find": find, "nb": nb}


def model_keys(n, X, m):
    import job_ring as JR
    cov = JR.Cover(X["npts"], X["blocks"])
    live = set(X["live"])
    inv = defaultdict(Counter)

    def knot(v):
        return cov.proj(v) < n

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
        return [v for v in S if any(knot(x) for x in S - {v}) and connected(S - {v})]

    def bd(S):
        return len({y for v in S for y in cov.nbrs(v)} - S)
    roots = [x for x in range(X["npts"]) if x >= n or x in live]
    for x in roots:
        for S in JR.clusters(cov, (x,), m):
            if not any(knot(v) for v in S):
                continue
            R = rstar(S)
            inv[len(S) - 1][(len(R), bd(S), tuple(sorted((len(rstar(S - {v})), bd(S - {v})) for v in R)))] += Fraction(1, len(S))
    for k in range(n):
        if k not in live:
            inv[0][(0, 0, ())] += 1
    return inv


def growth(n, edges, sizes, rounds):
    import job_ring as JR
    return JR.growth_keys(n, edges, sizes, rounds)


def theorem2(n, X, mmax):
    """Cluster counts by Theorem 2's formula, per size m = 1..mmax, and the claimed degree and coefficient."""
    comps = X["comps"]
    find = X["find"]
    out = [0] * (mmax + 1)
    claim = []
    adj = defaultdict(set)
    for B in X["blocks"]:
        if all(x < n or any(x == p[1] for p in X["pend"]) for x in B):
            for a, b in itertools.combinations(B, 2):
                adj[a].add(b)
                adj[b].add(a)
    rays_at = defaultdict(int)
    for k, o, R, _ in X["pend"]:
        rays_at[o] += R
    for root, c in comps.items():
        if not c["knots"]:
            continue
        F = sorted(c["points"] | c["knots"])
        Fs = set(F)
        Qs = []
        for r in range(1, len(F) + 1):
            for Q in itertools.combinations(F, r):
                Qset = set(Q)
                if not any(q < n for q in Q):
                    continue
                st, seen = [Q[0]], {Q[0]}
                while st:
                    a = st.pop()
                    for b in adj[a] & Qset:
                        if b not in seen:
                            seen.add(b)
                            st.append(b)
                if len(seen) == len(Q):
                    Qs.append(Q)
        for m in range(1, mmax + 1):
            tot = 0
            for Q in Qs:
                if len(Q) == m:
                    tot += 1
                rs = sum(rays_at[q] for q in Q)
                for s in range(1, rs + 1):
                    if m - len(Q) - 1 >= s - 1:
                        tot += math.comb(rs, s) * math.comb(m - len(Q) - 1, s - 1)
            out[m] += tot
        RY = c["rays"]
        bases = {o for k, o, R, _ in X["pend"] if R > 0 and find(k) == root}
        NY = sum(1 for Q in Qs if bases <= set(Q))
        claim.append({"core": len(F), "rays": RY, "N": NY})
    return out, claim


def check(n, edges, surplus, tree_extra=False):
    X = plus(n, edges, surplus)
    row = {"n": n, "edges": edges, "surplus": {str(k): v for k, v in surplus.items()}, "S3": X["S3"], "S4": X["S4"], "S5+": X["S5+"]}
    if not (X["S3"] and X["S4"]):
        return row
    a, counts = growth(n, edges, X["sizes"], T)
    b = model_keys(n, X, T + 1)
    bad = [t for t in range(T + 1) if {k: Fraction(v) for k, v in a.get(t, {}).items()} != {k: v for k, v in b.get(t, {}).items() if v}]
    row["keys agree"] = not bad
    row["growth counts"] = counts
    if X["S5+"] and len(edges) == n - 1:
        _, c20 = growth(n, edges, X["sizes"], T2)
        pred, claim = theorem2(n, X, T2 + 1)
        dead = sum(1 for k in range(n) if k not in set(X["live"]))
        pred_c = [pred[t + 1] + (dead if t == 0 else 0) for t in range(T2 + 1)]
        row["theorem 2: counts equal the formula"] = [x for x in c20 if isinstance(x, int)] == pred_c[:len([x for x in c20 if isinstance(x, int)])]
        R = max(c["rays"] for c in claim)
        lead = sum(c["N"] for c in claim if c["rays"] == R)
        t0 = max(c["core"] for c in claim)
        seq = [x for x in c20 if isinstance(x, int)][t0:]
        diffs = seq
        for _ in range(R - 1):
            diffs = [diffs[i + 1] - diffs[i] for i in range(len(diffs) - 1)]
        nxt = [diffs[i + 1] - diffs[i] for i in range(len(diffs) - 1)]
        row["theorem 2: R, sum N, (R-1)th differences constant and equal to sum N"] = [R, lead, all(x == lead for x in diffs) and all(x == 0 for x in nxt)]
        row["counts to 20"] = c20
    return row


def cases():
    import networkx as nx
    items = []
    for G in nx.graph_atlas_g():
        if 2 <= G.number_of_nodes() <= 7 and nx.is_connected(G):
            items.append([G.number_of_nodes(), sorted(tuple(sorted(e)) for e in G.edges())])
    for a in range(0, len(items), 40):
        yield f"A-{a // 40:03d}", {"graphs": items[a:a + 40]}
    past = [[8, sorted(tuple(sorted(e)) for e in t.edges())] for t in nx.nonisomorphic_trees(8)]
    rng = random.Random(20261119)
    seen = []
    tries = 0
    while len(seen) < 40 and tries < 100000:
        tries += 1
        G = nx.gnm_random_graph(8, rng.randint(8, 10), seed=rng.randrange(10 ** 9))
        if not nx.is_connected(G) or nx.is_tree(G) or any(nx.is_isomorphic(G, H) for H in seen):
            continue
        seen.append(G)
        past.append([8, sorted(tuple(sorted(e)) for e in G.edges())])
    for a in range(0, len(past), 4):
        yield f"B-{a // 4:03d}", {"graphs": past[a:a + 4]}
    yield "N", {"named": True}


def run(case_id, p):
    if p.get("named"):
        out = {}
        for name, n, edges in (("pair", 2, [(0, 1)]), ("path of three", 3, [(0, 1), (1, 2)]),
                               ("path of four", 4, [(0, 1), (1, 2), (2, 3)]), ("path of five", 5, [(0, 1), (1, 2), (2, 3), (3, 4)])):
            X = plus(n, edges, {})
            _, counts = growth(n, edges, X["sizes"], 12)
            pred, claim = theorem2(n, X, 13)
            dead = sum(1 for k in range(n) if k not in set(X["live"]))
            out[name] = {"class": {"S3": X["S3"], "S4": X["S4"], "S5+": X["S5+"]}, "sizes": X["sizes"], "open": X["open"],
                         "pendants (knot, rays)": [[k, R] for k, o, R, _ in X["pend"]], "growth": counts,
                         "cluster count": [pred[t + 1] + (dead if t == 0 else 0) for t in range(13)], "components": claim}
        return out
    rows = []
    for n, edges in p["graphs"]:
        edges = [tuple(e) for e in edges]
        for surplus in [{}] + [{k: 1} for k in range(n)]:
            rows.append(check(n, edges, surplus))
    return {"rows": rows}
