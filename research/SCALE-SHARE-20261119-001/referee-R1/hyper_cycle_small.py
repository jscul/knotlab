"""The cycle-of-blocks-through-a-hyperedge shape at five and six knots: every five-knot census arrangement flagged (the rule was
exact on all in-scope five-knot arrangements in CLUSTER-ALL's T1), and the two six-knot misses of hyper_cycle_search.py with the
study's own grower (joinlib's grow via scale.J, read-only) as a cross-check of the referee's growth.

  ../../../.venv/bin/python -B hyper_cycle_small.py > referee_scale_hyper_cycle_small.json
"""
import json
import sys

import hyper_cycle_search as H
import referee_scale as R
import scan_cycles as SC

sys.path.insert(0, str(R.ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
import referee_cluster as RC  # noqa: E402

S = R.S
five = 0
five_flag = []
for sizes, flat in R.census5():
    sz, e = RC.edges_of((sizes, flat))
    A = S.Cl.analyse(sz, e)
    five += 1
    if A.get("scope") and not A.get("stall") and SC.hyper_cycle(A):
        five_flag.append(RC.compare(("x", sz, e))["verdict"])
six = []
for seed in (6028024, 6029462):
    sz, e = H.sample(6, seed)
    A = S.Cl.analyse(sz, e)
    G, o = RC.my_growth(sz, e, rounds=20)
    g = S.J.grow(sz, e, rounds=20, maxj=20000, tmax=120)
    six.append({"seed": seed, "sizes": sz, "touches": e, "blocks": A["blocks"],
                "hyperedges": [list(B) for B, be in zip(A["blocks"], A["bedges"]) if be is None],
                "referee's growth": [o, G.counts()[:12]], "study's grower": [g["outcome"], g["counts"][:12]],
                "rule": S.Cl.series(sz, e, 12), "rule's class": R.base(S.classify(sz, [[sum(1 for t in e if set(t) == {i, j}) for j in range(6)] for i in range(6)]))})
print(json.dumps({"five-knot census arrangements": five, "five-knot in scope with the shape": len(five_flag),
                  "their verdicts": {v: five_flag.count(v) for v in set(five_flag)}, "six-knot misses": six}, indent=1, default=str))
