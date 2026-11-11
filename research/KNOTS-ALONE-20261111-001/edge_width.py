"""Exploratory, after the frozen census: NAE's readings on flat worlds against the edge-width (the length of a shortest
non-contractible cycle). Not part of the frozen contract.

For a lattice torus Z^2 / L (neighbours +-(1,0), +-(0,1), +-(1,1)) the edge-width is the least hexagonal norm of a nonzero vector
of L, |(x, y)| = max(|x|, |y|) when x y >= 0 and |x| + |y| otherwise. For a general surface world it is computed from Z/2
homology: the least length of a cycle of the 1-skeleton that is not a sum of knot boundaries (shortest such cycles are among the
fundamental cycles of breadth-first trees).
"""

from __future__ import annotations

import itertools
import json
import os
import sys
from collections import Counter, defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "KNOTS-ALONE-20261111-001A",
                                "KNOTS-ALONE-20261111-001A-E001_knots_alone_census"))
import knots_alone as ka  # noqa: E402


def edge_width(V, T):
    edges = sorted({e for t in T for e in itertools.combinations(sorted(t), 2)})
    eidx = {e: i for i, e in enumerate(edges)}
    # boundary space over GF(2), as a reduced basis keyed by leading bit
    basis = {}

    def reduce(x):
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                return x
        return 0
    for t in T:
        x = 0
        for e in itertools.combinations(sorted(t), 2):
            x ^= 1 << eidx[e]
        r = reduce(x)
        if r:
            basis[r.bit_length() - 1] = r
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    best = None
    for s in range(V):
        parent, depth = {s: None}, {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for w in sorted(adj[u]):
                if w not in parent:
                    parent[w], depth[w] = u, depth[u] + 1
                    q.append(w)

        def path(u):
            out = []
            while parent[u] is not None:
                out.append(tuple(sorted((u, parent[u]))))
                u = parent[u]
            return out
        for a, b in edges:
            if parent.get(a) == b or parent.get(b) == a:
                continue
            length = depth[a] + depth[b] + 1
            if best is not None and length >= best:
                continue
            x = 1 << eidx[(a, b)]
            for e in path(a) + path(b):
                x ^= 1 << eidx[e]
            if reduce(x):
                best = length
    return best


def main():
    census = json.load(open(os.path.join(ROOT, "artifacts", "KNOTS-ALONE-20261111-001A",
                                         "KNOTS-ALONE-20261111-001A-E001_knots_alone_census", "census.json")))
    worlds = census["worlds"]
    flat = [(i, w) for i, w in enumerate(worlds) if w["surface"] and w.get("d") == 6]
    rows = Counter()
    for i, w in flat:
        ew = edge_width(w["V"], [tuple(t) for t in w["T"]])
        w["edge_width"] = ew
        r = w["NAE"]
        state = "faithful" if r.get("faithful") else "native" if r.get("native") else "allowed" if r["allowed"] else "no state"
        rows[(ew, w["orientable"], state)] += 1
    print("flat worlds by edge-width, orientability and NAE reading:")
    for k in sorted(rows):
        print("  ", k, rows[k])
    by = Counter()
    for rec in census["bonds"]:
        ew = worlds[rec["world"]]["edge_width"]
        if rec["NAE"] is None or not worlds[rec["world"]]["NAE"].get("faithful"):
            continue
        d3 = [b for dl, b, n in rec["NAE"] if dl == 3]
        by[(ew, tuple(sorted(set(map(str, d3)))))] += 1
    print("bond-distance tori (faithful) by edge-width: beta values at delta 3")
    for k in sorted(by):
        print("  ", k, by[k])
    stress = os.path.join(HERE, "stress_test.json")
    if os.path.exists(stress):
        st = json.load(open(stress))
        print("stress test tori: (edge-width, beta values at delta 3) -> count")
        tori = {}
        for V in range(25, 31):
            for T in ka.lattice_tori(V):
                tori.setdefault(V, []).append(T)
        c = Counter()
        for V in range(25, 31):
            recs = [r for r in st["P5"] if r["V"] == V]
            for T, r in zip(tori[V], recs):
                if "table" not in r:
                    c[(edge_width(V, T), "not faithful")] += 1
                    continue
                d3 = sorted({str(b) for dl, b, n in r["table"] if dl == 3})
                c[(edge_width(V, T), tuple(d3))] += 1
        for k in sorted(c, key=str):
            print("  ", k, c[k])


if __name__ == "__main__":
    main()
