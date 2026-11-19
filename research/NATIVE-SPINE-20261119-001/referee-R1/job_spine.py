"""Shared-runner job for the referee's check of NATIVE-SPINE-20261119-001 (own growth, own relation, networkx's matcher and strongly
connected components, its own shuffle; the starts read from BREAK-EDDIES' population.json as data; no study code imported or run).

For each of the ten plastic-number starts, grown by the referee's engine (complete rounds, fewest counts, GF(2) implication) to 24
rounds or MAXJ junctions, at every round t with c(t) = c(t - 2) + c(t - 3):
- the spine relation: round t's junctions to their ancestors at exact depths 2 and 3, with chain counts m;
- rules N (depth 2 only), M (the largest m) and F (the smallest m): whether what each keeps is a perfect matching; M's share of
  kept ancestors at depth 2; for every j, whether the largest m at depth 3 is at least the largest at depth 2 (it must be: every
  chain to a depth-2 ancestor continues to each of its parents);
- the forced share: a perfect matching by networkx's Hopcroft-Karp, the alternating digraph (unmatched pairs left to right,
  matched ones right to left), its strongly connected components by networkx; a matched pair is forced when its ends lie in
  different components.  On rounds with at most 400 junctions, each matched pair also tested directly: remove it, and ask for
  another perfect matching;
- at rounds 10, 15 and 20, three degree-preserving shuffles (double swaps, the referee's own, 20 per pair, seeds 1 to 3) tested
  for a perfect matching.
One small round of T-028 (t = 7) is also written out junction by junction for the depth split.

  .venv/bin/python -B scripts/longrun.py launch research/NATIVE-SPINE-20261119-001/referee-R1/job_spine.py \\
      --out runs/referee-spine --unit referee-spine --workers 3 --case-timeout 3600 --case-mem 4G --mem-max 16G
"""
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
TEN = [28, 44, 52, 55, 56, 58, 61, 65, 66, 68]
MAXJ = 45000


def cases():
    pop = json.loads((ROOT / "experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json").read_text())
    for i in TEN:
        yield f"T-{i:03d}", {"start": {"sizes": pop[i]["sizes"], "edges": pop[i]["edges"]}, "rounds": 24}


def perfect(left, adj):
    import networkx as nx
    B = nx.Graph()
    L = [("L", u) for u in left]
    B.add_nodes_from(L)
    for u in left:
        for v in adj[u]:
            B.add_edge(("L", u), ("R",) + v)
    mt = nx.algorithms.bipartite.hopcroft_karp_matching(B, top_nodes=L)
    return mt, all(x in mt for x in L)


def run(case_id, p):
    import networkx as nx
    import referee_first as RFK
    import referee_touch as RT
    st = p["start"]
    n0 = len(st["sizes"])
    M0 = [[0] * n0 for _ in range(n0)]
    for a, b in st["edges"]:
        M0[a][b] += 1
        M0[b][a] += 1
    G = RFK.Start(RT.stars(st["sizes"], M0))
    for _ in range(p["rounds"]):
        if G.step(RFK.fewest, None, None) != "ok" or len(G.bits) > MAXJ:
            break
    T = G.rounds
    c = G.counts()
    n = len(G.bits)
    par = [sorted(G.parents[j]) if G.round[j] > 0 else [] for j in range(n)]
    br = defaultdict(list)
    for j in range(n):
        br[G.round[j]].append(j)

    def anc(j, k):
        cur = Counter({j: 1})
        for _ in range(k):
            nxt = Counter()
            for x, m in cur.items():
                for q in par[x]:
                    nxt[q] += m
            cur = nxt
        return cur
    rows, example = [], None
    for t in range(4, T + 1):
        if c[t] != c[t - 2] + c[t - 3]:
            continue
        rel = {j: {(k, a): m for k in (2, 3) for a, m in anc(j, k).items()} for j in br[t]}
        rset = {(2, a) for a in br[t - 2]} | {(3, a) for a in br[t - 3]}
        row = {"t": t, "count": c[t]}
        for rule in "NMF":
            kept = {}
            for j, cand in rel.items():
                if rule == "N":
                    kept[j] = [x for x in cand if x[0] == 2]
                else:
                    best = (max if rule == "M" else min)(cand.values())
                    kept[j] = [x for x, m in cand.items() if m == best]
            hits = Counter(x for v in kept.values() for x in v)
            row[rule + " perfect"] = all(len(v) == 1 for v in kept.values()) and all(hits.get(x, 0) == 1 for x in rset)
            row[rule + " ties"] = sum(1 for v in kept.values() if len(v) > 1)
            if rule == "M":
                tot = sum(len(v) for v in kept.values())
                row["M kept at depth 2"] = sum(1 for v in kept.values() for x in v if x[0] == 2) / max(1, tot)
        row["max m at depth 3 >= max at depth 2 (every j)"] = all(
            max((m for (k, a), m in cand.items() if k == 3), default=0) >= max((m for (k, a), m in cand.items() if k == 2), default=0)
            for cand in rel.values())
        left = list(rel)
        adj = {j: list(rel[j]) for j in left}
        mt, ok = perfect(left, adj)
        row["perfect matching"] = ok
        if ok:
            mu = {u: mt[("L", u)][1:] for u in left}
            D = nx.DiGraph()
            for u in left:
                for v in adj[u]:
                    if v != mu[u]:
                        D.add_edge(("L", u), ("R",) + v)
                D.add_edge(("R",) + mu[u], ("L", u))
            comp = {}
            for i, C in enumerate(nx.strongly_connected_components(D)):
                for x in C:
                    comp[x] = i
            row["forced share (components)"] = sum(1 for u in left if comp[("L", u)] != comp[("R",) + mu[u]]) / len(left)
            if len(left) <= 400:
                forced = 0
                for u in left:
                    adj2 = dict(adj)
                    adj2[u] = [v for v in adj[u] if v != mu[u]]
                    _, ok2 = perfect(left, adj2)
                    forced += not ok2
                row["forced share (each pair removed)"] = forced / len(left)
        if t in (10, 15, 20):
            res = []
            for seed in (1, 2, 3):
                rng = random.Random(1000 * seed + t)
                edges = [(j, x) for j in left for x in adj[j]]
                have = set(edges)
                for _ in range(20 * len(edges)):
                    i, k = rng.randrange(len(edges)), rng.randrange(len(edges))
                    (u1, v1), (u2, v2) = edges[i], edges[k]
                    if u1 == u2 or v1 == v2 or (u1, v2) in have or (u2, v1) in have:
                        continue
                    have -= {(u1, v1), (u2, v2)}
                    have |= {(u1, v2), (u2, v1)}
                    edges[i], edges[k] = (u1, v2), (u2, v1)
                sadj = defaultdict(list)
                for u, v in edges:
                    sadj[u].append(v)
                degl = Counter(u for u, _ in edges) == Counter(u for u in left for _ in adj[u])
                res.append([perfect(left, sadj)[1], degl])
            row["shuffles: perfect, left degrees kept"] = res
        rows.append(row)
        if case_id == "T-028" and t == 7:
            example = {str(j): {f"depth {k} ancestor {a}": m for (k, a), m in sorted(rel[j].items())} for j in br[t][:4]}
    return {"counts": c, "rows": rows, "example (T-028, round 7, first four junctions)": example}
