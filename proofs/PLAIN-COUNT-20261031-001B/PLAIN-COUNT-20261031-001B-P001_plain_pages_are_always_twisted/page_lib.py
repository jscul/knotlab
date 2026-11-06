"""Plain pages are always twisted (PLAIN-COUNT-20261031-001B).

A *page* is a 2-connected planar cubic bipartite graph with a square face S (the junction). It is *plain* when no edge is negated. Its
own edges are all edges except S's four; it is *twisted* when the plain signing differs from the glued Pfaffian (Kasteleyn) signing by
a non-cut on its own edges (TWIST-COUNT-20261030-001A). A *trisum tree* glues pages along squares, three pages per square, and deletes
the square edges."""
import itertools
import networkx as nx
import scipy.spatial


def faces(g):
    ok, emb = nx.check_planarity(g)
    assert ok
    seen, out = set(), []
    for u, v in emb.edges():
        if (u, v) not in seen:
            out.append(emb.traverse_face(u, v, mark_half_edges=seen))
    return out


def delaunay(n, seed):
    """the Delaunay triangulation of n points in general position (a planar map)"""
    import numpy as np
    rng = np.random.default_rng(seed)
    tri = scipy.spatial.Delaunay(rng.random((n, 2)))
    g = nx.Graph()
    for s in tri.simplices:
        g.add_edges_from(itertools.combinations(map(int, s), 2))
    return g


def family(omnitruncation):
    """named planar cubic bipartite graphs: prisms and flag graphs (omnitruncations) of planar maps"""
    fam = {f"{2 * n}-prism": nx.circular_ladder_graph(2 * n) for n in range(2, 9)}
    maps = {"K4": nx.complete_graph(4), "triangular prism": nx.circular_ladder_graph(3), "cube": nx.hypercube_graph(3),
            "octahedron": nx.octahedral_graph(), "pentagonal prism": nx.circular_ladder_graph(5), "dodecahedron": nx.dodecahedral_graph(),
            "icosahedron": nx.icosahedral_graph(), "K2,3": nx.complete_bipartite_graph(2, 3),
            "theta": nx.Graph([(0, 1), (1, 2), (0, 3), (3, 2), (0, 4), (4, 5), (5, 2)])}
    maps.update({f"wheel W{n}": nx.wheel_graph(n + 1) for n in range(3, 10)})
    maps.update({f"cycle C{n}": nx.cycle_graph(n) for n in range(3, 9)})
    maps.update({f"Delaunay {n} (seed {s})": delaunay(n, s) for n, s in ((8, 1), (10, 2), (12, 3), (14, 4))})
    for name, m in maps.items():
        fam[f"flags of {name}"] = omnitruncation(m)
    return {k: nx.convert_node_labels_to_integers(g, ordering="sorted") for k, g in fam.items()}


def squares(g):
    """the square faces, each as a 4-tuple starting at a vertex of colour class 0"""
    col = nx.bipartite.color(g)
    out = []
    for f in faces(g):
        if len(f) == 4:
            i0 = [k for k in range(4) if col[f[k]] == 0][0]
            out.append(tuple(f[i0:] + f[:i0]))
    return out


def glue(pieces):
    """a trisum tree: pieces = [(graph, {square name: square 4-tuple in that graph})], every square name in three pieces. Returns the glued
    graph (square edges deleted), the leaves [(piece graph renamed, [squares])] and the squares as 4-tuples of glued names."""
    names = {}
    for i, (g, sq) in enumerate(pieces):
        col = nx.bipartite.color(g)
        for s, S in sq.items():
            assert col[S[0]] == col[S[2]] != col[S[1]] == col[S[3]]
    def nm(i, v):
        for s, S in pieces[i][1].items():
            if v in S:
                return ('sq', s, S.index(v))
        return (i, v)
    G = nx.Graph()
    leaves = []
    allsq = sorted({s for g, sq in pieces for s in sq}, key=str)
    SQ = {s: tuple(('sq', s, k) for k in range(4)) for s in allsq}
    for i, (g, sq) in enumerate(pieces):
        h = nx.relabel_nodes(g, {v: nm(i, v) for v in g})
        leaves.append((h, [SQ[s] for s in sorted(sq, key=str)]))
        sqe = {frozenset((SQ[s][k], SQ[s][(k + 1) % 4])) for s in sq for k in range(4)}
        G.add_edges_from(e for e in h.edges() if frozenset(e) not in sqe)
    return G, leaves, [SQ[s] for s in allsq]


def is_brace(g):
    """2-extendable: every matching of two edges extends to a perfect matching"""
    col = nx.bipartite.color(g)
    top = [v for v in g if col[v] == 0]
    for e, f in itertools.combinations(g.edges(), 2):
        if len(set(e) | set(f)) < 4:
            continue
        h = g.copy()
        h.remove_nodes_from(set(e) | set(f))
        m = nx.bipartite.hopcroft_karp_matching(h, top_nodes=[v for v in top if v in h])
        if len(m) != h.number_of_nodes():
            return False
    return True


def four_cycles(g):
    out = set()
    for u in g:
        for a, b in itertools.combinations(g[u], 2):
            for w in set(g[a]) & set(g[b]):
                if w != u:
                    out.add(frozenset((u, a, w, b)))
    return out


def cycles(g, L):
    """all simple cycles of length L, as frozensets of edges"""
    out = set()
    order = {v: i for i, v in enumerate(sorted(g, key=str))}
    for s in g:
        stack = [(s, [s])]
        while stack:
            v, path = stack.pop()
            if len(path) == L:
                if s in g[v]:
                    out.add(frozenset(frozenset((path[i], path[(i + 1) % L])) for i in range(L)))
                continue
            for w in g[v]:
                if order[w] > order[s] and w not in path:
                    stack.append((w, path + [w]))
    return out


def vertices(C):
    return {v for e in C for v in e}


def nice(g, Q):
    """g minus the vertices of Q has a perfect matching"""
    h = g.copy()
    h.remove_nodes_from(Q)
    col = nx.bipartite.color(h)
    m = nx.bipartite.hopcroft_karp_matching(h, top_nodes=[v for v in h if col[v] == 0])
    return len(m) == h.number_of_nodes()


def incidence(H):
    g = nx.Graph()
    for i, l in enumerate(H):
        for p in l:
            g.add_edge(('L', i), ('P', p))
    return g
