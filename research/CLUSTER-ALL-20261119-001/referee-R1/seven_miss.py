"""The referee's one seven-knot miss (seed 91758): the round-2 and round-3 junctions of its own growth grouped by the start knots
they descend from, and the rule's blocks (clusters.analyse, read-only).

  ../../../.venv/bin/python -B seven_miss.py > referee_cluster_seven_miss.json
"""
import json
from collections import defaultdict

import referee_cluster as RC

s, e = RC.seven(91758)
G, o = RC.my_growth(s, e, rounds=4)
anc = {}
for j in range(len(G.bits)):
    anc[j] = {j} if G.round[j] == 0 else set().union(*(anc[p] for p in G.parents[j]))
out = {"sizes": s, "touches": e, "my counts": G.counts(), "rule's counts": RC.Cl.series(s, e, 5)}
for r in (2, 3):
    by = defaultdict(list)
    for j in range(len(G.bits)):
        if G.round[j] == r:
            by[frozenset(k for k in anc[j] if G.round[k] == 0)].append(j)
    out[f"round {r}: start-knot sets with two or more junctions (parents of each)"] = [
        [sorted(S), [len(G.parents[j]) for j in js]] for S, js in by.items() if len(js) > 1]
A = RC.Cl.analyse(s, e)
out["rule's blocks"] = A["blocks"]
print(json.dumps(out, indent=1, default=str))
