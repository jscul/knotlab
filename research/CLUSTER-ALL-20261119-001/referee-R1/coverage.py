"""Which clauses of the rule (clusters.analyse, read-only) the referee's sampled cases exercise: the 600 five-knot census
arrangements and 300 six-knot samples of referee_cluster.py's `sample` part.

  ../../../.venv/bin/python -B coverage.py > referee_cluster_coverage.json
"""
import json
import random
import sys
from collections import Counter

import referee_cluster as RC

Cl = RC.Cl
five = [k for k in RC.census_keys() if len(k[0]) == 5]
pick = random.Random(19).sample(five, 600)
cases = [("five", RC.edges_of((k[0], k[1]))) for k in pick] + [("six", RC.six(70000 + 7 * k)) for k in range(300)]
cov = Counter()
for grp, (sizes, e) in cases:
    A = Cl.analyse(sizes, e)
    if not A.get("scope", False):
        cov[f"{grp}: out of scope"] += 1
        continue
    if A.get("stall"):
        cov[f"{grp}: stall"] += 1
        continue
    cov[f"{grp}: grows or closes"] += 1
    for k in sorted({k for v in A["pend"].values() for k in v}):
        cov[f"{grp}: a pendant of kind {['leaf', 'one chain', 'two chains'][k]}"] += 1
    if A.get("hyper"):
        cov[f"{grp}: a hyperedge"] += 1
    if any(be is not None and len(b) >= 4 for b, be in zip(A["blocks"], A["bedges"])):
        cov[f"{grp}: a block of four or more knots"] += 1
print(json.dumps(dict(sorted(cov.items())), indent=1))
