"""How common is the referee's 16-knot miss's shape, and does the rule misclassify it elsewhere?  On the referee's own chains
(non-stalled states, 4 chains x NSAMP per n): the share of in-scope starts with a piece of the map whose blocks form a cycle
through a first-round group of three (a hyperedge), and, for every such start and every start the rule calls a ring, the
referee's own growth (FIRST-KNOT-R1 engine, 25 rounds) against the rule (clusters.series and dimension.growth_class, read-only).

  NS=8,10,12,16,20 NSAMP=300 ../../../.venv/bin/python -B scan_cycles.py > referee_scale_cycles.json
"""
import json
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

import referee_scale as R

sys.path.insert(0, str(R.ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
import referee_cluster as RC  # noqa: E402

S = R.S


def hyper_cycle(A):
    """Does some piece of blocks (knots and blocks, joined by incidence) hold a cycle and a hyperedge?"""
    blocks = A["blocks"]
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, B in enumerate(blocks):
        for k in B:
            parent[find(("b", i))] = find(("k", k))
    comp = defaultdict(lambda: [0, 0, False])     # nodes, incidences, has a hyperedge
    for i, B in enumerate(blocks):
        c = comp[find(("b", i))]
        c[1] += len(B)
        c[2] |= A["bedges"][i] is None
    for x in list(parent):
        comp[find(x)][0] += 1
    return any(inc > nodes - 1 and hy for nodes, inc, hy in comp.values())


def scan(args):
    n, k, N = args
    _, _, states = R.my_chain((n, k, N), keep_states=True)
    rows = []
    for sizes, M in states:
        sz, e = S.edges_of(sizes, M)
        A = S.Cl.analyse(sz, e)
        if not A.get("scope") or A.get("stall"):
            rows.append({"scope": bool(A.get("scope"))})
            continue
        flag = hyper_cycle(A)
        cls = R.base(S.classify(sizes, M))
        row = {"scope": True, "hyper cycle": flag, "class": cls}
        if flag or cls.startswith("ring"):
            G, o = RC.my_growth(sz, e, rounds=25, maxj=60000)
            c = G.counts()
            pred = S.Cl.series(sz, e, len(c))
            row.update({"equal": pred[:len(c)] == c, "mine": c[:12], "rule": pred[:12], "mine outcome": o})
        rows.append(row)
    return n, rows


if __name__ == "__main__":
    ns = [int(x) for x in os.environ.get("NS", "8,10,12,16,20").split(",")]
    N = int(os.environ.get("NSAMP", "300"))
    with Pool(int(os.environ.get("WORKERS", "12"))) as pool:
        res = pool.map(scan, [(n, 200 + k, N) for n in ns for k in range(4)], chunksize=1)
    out = {}
    for n in ns:
        rows = [r for nn, rs in res if nn == n for r in rs]
        sc = [r for r in rows if r["scope"]]
        hc = [r for r in sc if r["hyper cycle"]]
        rg = [r for r in sc if r["class"].startswith("ring")]
        out[n] = {"non-stalled samples": len(rows), "in scope": len(sc),
                  "with a cycle of blocks through a hyperedge": len(hc),
                  "... the rule's class": dict(Counter(r["class"] for r in hc)),
                  "... equal to the referee's growth for 25 rounds": sum(r["equal"] for r in hc),
                  "the rule says ring": len(rg), "... equal to the referee's growth": sum(r["equal"] for r in rg),
                  "examples of misses": [r for r in hc + rg if not r["equal"]][:3]}
    print(json.dumps(out, indent=1, default=str))
