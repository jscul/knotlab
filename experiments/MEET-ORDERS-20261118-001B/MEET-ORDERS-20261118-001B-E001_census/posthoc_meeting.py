"""Post hoc (written after the read-out, after Q8 failed; not a prediction): group the labelled runs' signatures (labelled base
counts and mass by largest odd set at every level) by the meeting pattern read as an abstract hypergraph (which knots share which
distinctions, up to renaming, the line ignored) instead of by the pair-sharing tree.

  ../../../.venv/bin/python -B posthoc_meeting.py > ../../../artifacts/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/posthoc_meeting.txt
"""
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job
import melib as M

ROOT = HERE.parents[2]
res = json.loads((ROOT / "artifacts/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/results.json").read_text())


def hypergraph(knots):
    H = nx.Graph()
    for i, k in enumerate(knots):
        H.add_node(("k", i), t="k")
        for v in k:
            H.add_node(("d", v), t="d")
            H.add_edge(("k", i), ("d", v))
    return H


for n0 in (5, 6, 7):
    rows = {x["ordered"]: x for x in res["labelled_rows"] if x["n0"] == n0}
    classes = []
    for cid, p in job.cases():
        if not cid.startswith(f"X|{n0}|"):
            continue
        K = [tuple(k) for k in p["knots"]]
        x = rows[M.nesting(K, 0, n0 - 1, ordered=True)]
        H = hypergraph(K)
        for c in classes:
            if nx.is_isomorphic(c[0], H, node_match=lambda a, b: a["t"] == b["t"]):
                c[1].append((K, x))
                break
        else:
            classes.append((H, [(K, x)]))
    print(f"line of {n0}: {len(classes)} meeting patterns")
    sigs = []
    for H, xs in classes:
        sig = {json.dumps([[L["labelled"], L["mass"]] for L in x["levels"]], sort_keys=True) for _, x in xs}
        hub = max(sum(1 for k in xs[0][0] if v in k) for v in range(n0))
        sigs.append(sig)
        print(f"  pair-sharing tree {xs[0][1]['tree']}, most knots at one distinction {hub}, presentations up to mirror {len(xs)}, "
              f"signatures {len(sig)}; bare bracketings {sorted({M.nesting(K, 0, n0 - 1) for K, _ in xs})}")
        print("    labelled bases per level", json.loads(next(iter(sig)))[-1][0] if len(sig) == 1 else "several")
    flat = [s for v in sigs for s in v]
    print(f"  distinct signatures {len(set(flat))} for {len(classes)} meeting patterns")
