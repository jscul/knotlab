"""Diagnosis after the frozen run (not a prediction): what makes the old reader's invented junctions?

For each invented clique of R1 at each failing stage, every pair inside it is short through some bond.  Record one smallest
bond per pair (the side U of at most six junctions found by the enumeration) and classify the junctions those bonds use: the
largest witness side, and whether the union of the witness sides holds a cycle of junctions (a closed walk through shared
distinctions), as in VARIABLE-OUTPUT-READER-20261118-001H's cycle of four-place junctions, or only paths.

Run: .venv/bin/python -B witness_shapes.py 10 15
"""
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ringread as R  # noqa: E402
B = R.B


def witnessed_table(stars, m, K):
    """As ringread.bond_table, also keeping one smallest side for each pair."""
    n = len(stars)
    adj = R.junction_graph(stars)
    OUT = n
    mask = [sum(1 << b for b in s) for s in stars]
    best, wit = {}, {}

    def complement_connected(U):
        seen, stack = {OUT}, [OUT]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in U and y not in seen:
                    seen.add(y)
                    stack.append(y)
        return len(seen) + len(U) == n + 1

    def extend(U, sup, ext, v):
        size = sup.bit_count()
        if size <= K + 1:
            bits = [i for i in range(sup.bit_length()) if sup >> i & 1]
            better = [p for p in combinations(bits, 2) if best.get(p, K + 1) > size - 1]
            if better and complement_connected(U):
                for p in better:
                    best[p] = size - 1
                    wit[p] = U
        if len(U) == m:
            return
        ext = set(ext)
        while ext:
            w = ext.pop()
            nb = {x for x in adj[w] if x != OUT and x > v and x not in U and all(x not in adj[u] for u in U)}
            extend(U | {w}, sup ^ mask[w], ext | nb, v)

    for v in range(n):
        extend(frozenset([v]), mask[v], {x for x in adj[v] if x != OUT and x > v}, v)
    labels = sorted(R.owners(stars))
    return {p: best.get(p, K + 1) for p in combinations(labels, 2)}, wit, adj


for T in map(int, sys.argv[1:]):
    P = R.grow(T)
    st = R.stars_of(P)
    K = max(map(len, st))
    tab, wit, adj = witnessed_table(st, 6, K)
    truth = set(st)
    labels = B.table_labels(tab)
    stars = set()
    for s in range(3, K + 1):
        raw = {p for p, d in tab.items() if d < s}
        new = B.clique_stars(labels, B.prune(raw, stars, s))
        spur = new - truth
        if spur:
            print(f'round {T}, stage {s}: {len(spur)} invented, {len(truth - new)} lost')
            shapes = Counter()
            for c in spur:
                sides = [wit[tuple(sorted(p))] for p in combinations(sorted(c), 2)]
                union = set().union(*sides)
                g = nx.Graph()
                g.add_nodes_from(union)
                for u in union:
                    for w in adj[u]:
                        if w in union:
                            g.add_edge(u, w)
                cyc = nx.cycle_basis(g)
                shapes[(len(c), max(map(len, sides)), 'cycle ' + ','.join(str(len(x)) for x in sorted(cyc, key=len)) if cyc else 'no cycle',
                        tuple(sorted(Counter(len(st[u]) for u in union).items())))] += 1
            for k, v in sorted(shapes.items(), key=lambda kv: -kv[1])[:8]:
                print(f'   {v} x invented size {k[0]}: largest witness side {k[1]} junctions; {k[2]}; witness junction sizes {k[3]}')
            pass
        stars = new
