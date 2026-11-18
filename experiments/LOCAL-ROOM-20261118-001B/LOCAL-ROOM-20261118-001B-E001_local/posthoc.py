"""Post hoc for LOCAL-ROOM-20261118-001B-E001 (written after the read-out of L1, labelled): what persists under the reach limit of
one split.  Recompute the frozen r = 1 runs (same seeds, so the same runs) and, for every run with two orders, split its splits
into two chains of nested splits (from a maximum matching of the semicube graph) and report the two chains' lengths and the
crossings at n = 6, 10, 14 and 20: do both orders keep growing, or does one stay fixed?
    .venv/bin/python -B posthoc.py      (writes artifacts/.../posthoc.json)
"""
import collections
import itertools
import json
import os
import random

import networkx as nx

import locallib as L

R = L.R
OUT = os.path.join(L.ROOT, "artifacts", "LOCAL-ROOM-20261118-001B", "LOCAL-ROOM-20261118-001B-E001_local")


def chains(states, n):
    full = (1 << n) - 1
    sp = R.splits(states, n)
    sides = [(i, x) for i, a in enumerate(sp) for x in (a, full ^ a)]
    G = nx.Graph()
    G.add_nodes_from(range(len(sides)))
    for p, q in itertools.combinations(range(len(sides)), 2):
        (i, x), (j, y) = sides[p], sides[q]
        if i != j and (x | y) == full:
            G.add_edge(p, q)
    M = nx.max_weight_matching(G, maxcardinality=True)
    link = collections.defaultdict(set)
    for p, q in M:
        link[sides[p][0]].add(sides[q][0])
        link[sides[q][0]].add(sides[p][0])
    seen, out = set(), []
    for i in range(len(sp)):
        if i in seen:
            continue
        comp, stack = 0, [i]
        while stack:
            j = stack.pop()
            if j in seen:
                continue
            seen.add(j)
            comp += 1
            stack.extend(link[j] - seen)
        out.append(comp)
    return sorted(out)


def trace_states(start, nmax, seed_value):
    rng = random.Random(seed_value)
    n, states = R.seed(start)
    out = {n: states}
    while n < nmax:
        perm = list(range(n))
        rng.shuffle(perm)
        blind = R.relabel(states, n, perm)
        opts = L.options(blind, n, 3, 1)
        if not opts:
            break
        _, states, _ = rng.choice(opts)
        n += 1
        out[n] = states
    return out


res = {}
for start in ("line", "2x2"):
    rows = collections.defaultdict(list)
    for i in range(100):
        tr = trace_states(start, 20, f"LR:L1:1:{start}:{i}")
        if R.measure(tr[20], 20)["kind"] != "two orders":       # k = lambda = 2 (two crossing orders), trees excluded
            continue
        for n in (6, 10, 14, 20):
            m = R.measure(tr[n], n)
            rows[n].append({"chains": chains(tr[n], n), "crossings": m["crossings"], "splits": m["splits"]})
    res[start] = {str(n): {"runs": len(v), "shorter_chain": dict(collections.Counter(x["chains"][0] for x in v)),
                           "longer_chain_median": sorted(x["chains"][-1] for x in v)[len(v) // 2] if v else None,
                           "crossings_median": sorted(x["crossings"] for x in v)[len(v) // 2] if v else None,
                           "crossings": dict(collections.Counter(x["crossings"] for x in v))} for n, v in rows.items()}
json.dump(res, open(os.path.join(OUT, "posthoc.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
