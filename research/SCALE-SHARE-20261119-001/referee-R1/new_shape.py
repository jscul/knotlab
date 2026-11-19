"""The two starts of the referee's chains on which the rule fails through a cycle of blocks through a first-round group of three
(n = 16 from the spot check, chain 100; n = 12 from the scan, chains 200-203): the start, the referee's counts, the study's own
grower's counts (joinlib's grow via scale.J, run read-only as a cross-check), the rule's counts and class.

  ../../../.venv/bin/python -B new_shape.py > referee_scale_new_shape.json
"""
import json
import sys

import referee_scale as R
import scan_cycles as SC

sys.path.insert(0, str(R.ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
import referee_cluster as RC  # noqa: E402

S = R.S
out = []
for n, ks in ((16, [100]), (12, [200, 201, 202, 203])):
    for k in ks:
        _, _, states = R.my_chain((n, k, 300), keep_states=True)
        for sizes, M in states:
            sz, e = S.edges_of(sizes, M)
            A = S.Cl.analyse(sz, e)
            if not A.get("scope") or A.get("stall") or not SC.hyper_cycle(A):
                continue
            G, o = RC.my_growth(sz, e, rounds=25, maxj=60000)
            g = S.J.grow(sz, e, rounds=25, maxj=60000, tmax=300)
            out.append({"n": n, "chain": k, "sizes": sz, "touches": e, "blocks": A["blocks"],
                        "hyperedges": [list(B) for B, be in zip(A["blocks"], A["bedges"]) if be is None],
                        "referee's growth": [o, G.counts()], "study's grower": [g["outcome"], g["counts"]],
                        "rule": S.Cl.series(sz, e, 25), "rule's class": R.base(S.classify(sizes, M))})
print(json.dumps(out, indent=1, default=str))
