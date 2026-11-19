"""The referee's spot-check misses (referee_scale.py spot, n = 12 and 16): for each, the referee's counts against the rule's, the
first differing round, the start-knot sets carrying two or more junctions of that round in the referee's growth (with each
junction's parent count), the rule's blocks with a missing pair, and whether scale.break_shape (read-only) flags the start.

  ../../../.venv/bin/python -B spot_misses.py > referee_scale_spot_misses.json
"""
import json
import sys
from collections import defaultdict
from multiprocessing import Pool

import referee_scale as R

sys.path.insert(0, str(R.ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
import referee_cluster as RC  # noqa: E402


def find(args):
    n, k = args
    _, _, states = R.my_chain((n, k, 300), keep_states=True)
    out = []
    for sizes, M in states:
        sz, e = R.S.edges_of(sizes, M)
        r = RC.compare(("x", sz, e))
        if r["verdict"] != "miss":
            continue
        G, o = RC.my_growth(sz, e, rounds=r["first difference"] + 1)
        anc = {}
        for j in range(len(G.bits)):
            anc[j] = {j} if G.round[j] == 0 else set().union(*(anc[p] for p in G.parents[j]))
        t = r["first difference"]
        by = defaultdict(list)
        for j in range(len(G.bits)):
            if G.round[j] == t:
                by[frozenset(x for x in anc[j] if G.round[x] == 0)].append(j)
        A = R.S.Cl.analyse(sz, e)
        import itertools
        gaps = [[list(B), sorted(set(itertools.combinations(B, 2)) - {tuple(sorted(p)) for p in be})]
                for B, be in zip(A["blocks"], A["bedges"]) if be is not None and len(B) >= 3
                and {tuple(sorted(p)) for p in be} != set(itertools.combinations(B, 2))]
        out.append({"n": n, "chain": k, "sizes": sz, "touches": e, "first difference": t,
                    "mine": G.counts(), "rule": R.S.Cl.series(sz, e, t + 1),
                    "start-knot sets with two or more junctions at that round (parents)": [
                        [sorted(s), [len(G.parents[j]) for j in js]] for s, js in by.items() if len(js) > 1 and len(s) >= 3],
                    "rule's blocks with a missing pair": gaps, "break_shape flags it": R.S.break_shape(sz, e)})
    return out


if __name__ == "__main__":
    with Pool(8) as pool:
        res = pool.map(find, [(n, 100 + k) for n in (12, 16) for k in range(4)])
    print(json.dumps([x for r in res for x in r], indent=1, default=str))
