"""Explicit bases for the proofs of ROW-ARRANGE-20261118-001A: partial cubes as bases.

A partial cube (a connected bipartite graph whose metric embeds isometrically in a hypercube) gives a base: its states are the
empty set, everything, and the halfspaces W_ab = {x : d(x, a) < d(x, b)} of its pairs ab, and these are exactly the solution set of
the betweenness constraints B(x, y, z) for y on a shortest path from x to z (proof in the proof file).  Families:
- F(a, b): two rings of 2a and 2b points sharing one point;
- kappa(G): the simplex graph of a graph G without triangles (points: the empty set, the vertices and the pairs of G; joined when
  one is the other plus one vertex); its splits are the vertices of G, two crossing exactly when adjacent in G."""
import itertools

import networkx as nx
import numpy as np


def halfspace_base(G):
    nodes = sorted(G.nodes(), key=repr)
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    full = (1 << n) - 1
    st = {0, full}
    for a, b in G.edges():
        m = sum(1 << idx[x] for x in nodes if dist[x][a] < dist[x][b])
        st |= {m, full ^ m}
    return sorted(st), n, nodes, dist


def betweenness_solutions(G):
    """Every 0/1 assignment satisfying B(x, y, z) for each y on a shortest path from x to z (brute force, numpy)."""
    nodes = sorted(G.nodes(), key=repr)
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    triples = [(idx[x], idx[y], idx[z]) for x, z in itertools.combinations(nodes, 2) for y in nodes
               if y not in (x, z) and dist[x][y] + dist[y][z] == dist[x][z]]
    out = []
    for start in range(0, 1 << n, 1 << 22):
        s = np.arange(start, min(start + (1 << 22), 1 << n), dtype=np.uint64)
        ok = np.ones(len(s), dtype=bool)
        for a, b, c in triples:
            x, y, z = [(s >> np.uint64(v)) & np.uint64(1) for v in (a, b, c)]
            ok &= ~((x == z) & (x != y))
        out.extend(int(v) for v in s[ok])
    return sorted(out)


def F(a, b):
    G = nx.cycle_graph(2 * a)
    H = nx.relabel_nodes(nx.cycle_graph(2 * b), {i: ("b", i) for i in range(2 * b)})
    G = nx.union(G, H)
    return nx.contracted_nodes(G, 0, ("b", 0), self_loops=False)


def kappa(H):
    G = nx.Graph()
    G.add_node(())
    for v in H.nodes():
        G.add_edge((), (v,))
    for u, v in H.edges():
        e = tuple(sorted((u, v), key=repr))
        G.add_edge((u,), e)
        G.add_edge((v,), e)
    return G
