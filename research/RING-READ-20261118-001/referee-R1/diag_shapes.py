"""Referee R1 for RING-READ-20261118-001: the short bonds whose inner side has three or more junctions (the ones that break the
old reader's lemma "three or more junctions together leave at least seven distinctions"), by shape, at rounds 10 and 15.

  ../../../.venv/bin/python -B diag_shapes.py > referee_ringread_shapes.json      (from this directory)
"""
import json
from collections import Counter
from multiprocessing import Pool

import networkx as nx

import referee_ringread as RRD


def shapes(T, L):
    G = RRD.grow(T)
    stars = [frozenset(b) for b in G.bits]
    masks = [sum(1 << b for b in S) for S in stars]
    n, adj, own = RRD.graph(stars)
    adjd = {u: dict(v) for u, v in adj.items()}
    with Pool(20) as pool:
        res = pool.map(RRD.search_root, [(adjd, n, r, L, 3, L, masks) for r in range(n)])
    out = Counter()
    for found, _, _, _ in res:
        for J, c in found:
            H = nx.Graph()
            H.add_nodes_from(J)
            H.add_edges_from((u, v) for u in J for v in adjd[u] if v in J and v != n)
            kind = "path" if nx.is_tree(H) and max(dict(H.degree()).values()) <= 2 else ("cycle" if all(d == 2 for _, d in H.degree()) else "other")
            out[(c, len(J), kind, tuple(sorted(len(stars[j]) for j in J)))] += 1
    return {f"size {c}, {k} junctions, {kind}, junction sizes {list(sz)}": v for (c, k, kind, sz), v in sorted(out.items())}


if __name__ == "__main__":
    print(json.dumps({"round 10, bonds of at most 7 with three or more junctions inside": shapes(10, 7),
                      "round 15, bonds of at most 8 with three or more junctions inside": shapes(15, 8)}, indent=1))
