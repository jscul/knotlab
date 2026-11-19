"""Referee R1 for RING-READ-20261118-001: the bonds of at most 11 distinctions whose inner side has seven or more junctions, at a
given round: their sides (junctions by round), and the pairs whose least bond is missed by sides of at most seven.

  ../../../.venv/bin/python -B diag_large.py T > referee_ringread_diag_T.json      (from this directory)
"""
import itertools
import json
import sys
from collections import Counter
from multiprocessing import Pool

import referee_ringread as RRD

T = int(sys.argv[1])
G = RRD.grow(T)
stars = [frozenset(b) for b in G.bits]
masks = [sum(1 << b for b in S) for S in stars]
n, adj, own = RRD.graph(stars)
adjd = {u: dict(v) for u, v in adj.items()}
L = 11


def one(r):
    found, small, nodes, keep = RRD.search_root((adjd, n, r, L, 7, L, masks))
    out = []
    for J, c in found:
        w = 0
        for u in J:
            w ^= masks[u]
        out.append((J, c, w))
    return out, keep


with Pool(20) as pool:
    res = pool.map(one, range(n))
large = [x for o, _ in res for x in o]
keep = [k for _, ks in res for k in ks]
t7 = {}
for side, w in keep:
    if side > 7:
        continue
    bits = [b for b in range(w.bit_length()) if w >> b & 1]
    for p in itertools.combinations(bits, 2):
        t7[p] = min(t7.get(p, 99), len(bits))
missed = []
rows = []
for J, c, w in large:
    bits = [b for b in range(w.bit_length()) if w >> b & 1]
    miss = [p for p in itertools.combinations(bits, 2) if t7.get(p, 99) > c]
    missed.extend((p, c) for p in miss)
    rows.append({"size": c, "inner side (junctions)": len(J), "rounds of the inner side": dict(sorted(Counter(G.round[j] for j in J).items())),
                 "inner side sizes": dict(sorted(Counter(len(stars[j]) for j in J).items())),
                 "the bond's distinctions (holder rounds)": sorted(Counter(G.round[j] for b in bits for j in own[b] if j not in J).items()),
                 "pairs this bond gives a smaller K than sides <= 7": [list(p) for p in miss]})
print(json.dumps({"T": T, "bonds of at most 11 with an inner side of 7 or more": len(large),
                  "distinct missed pairs (with the bond size)": sorted({(p, c) for p, c in missed}), "bonds": rows}, indent=1, default=str))
