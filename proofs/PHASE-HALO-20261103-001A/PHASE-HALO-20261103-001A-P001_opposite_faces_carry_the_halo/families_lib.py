"""Plane cubic bipartite graphs mixing frozen and liquid parts, for PHASE-HALO-20261103-001A: thick tubes (duals of subdivided bipyramids;
level 0 is the prism, a ladder), grids (duals of the subdivided octahedron), and a graph-level splice through a 3-edge cut."""
import collections
import itertools
import networkx as nx


def subdivided_dual(tris, level):
    """dual of a triangulation (list of vertex triples, oriented) after level rounds of 4-subdivision"""
    tris = [tuple(t) for t in tris]
    nv = 1 + max(max(t) for t in tris)
    for _ in range(level):
        mid = {}

        def m(u, v):
            nonlocal nv
            key = (min(u, v), max(u, v))
            if key not in mid:
                mid[key] = nv
                nv += 1
            return mid[key]
        new = []
        for (a, b, c) in tris:
            ab, bc, ca = m(a, b), m(b, c), m(c, a)
            new += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]
        tris = new
    edge_tris = collections.defaultdict(list)
    for i, t in enumerate(tris):
        for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edge_tris[(min(u, v), max(u, v))].append(i)
    g = nx.Graph()
    for e, ts in edge_tris.items():
        assert len(ts) == 2, e
        g.add_edge(*ts)
    return g


def bipyramid(m):
    """the bipyramid over an m-cycle (m even): equator 0..m-1, apexes m and m+1; Eulerian when m is even"""
    return [(m, i, (i + 1) % m) for i in range(m)] + [(m + 1, (i + 1) % m, i) for i in range(m)]


def tube(k, level):
    """thick ladders: the dual of the bipyramid over a 2k-cycle, subdivided level times (level 0 is the prism over a 2k-cycle)"""
    return subdivided_dual(bipyramid(2 * k), level)


def graph_splice(g1, v1, g2, v2):
    """join two plane cubic bipartite graphs through a 3-edge cut: delete vertex v1 of g1 and v2 of g2 (of opposite colours) and join
    their neighbours in a planar order"""
    c1 = nx.bipartite.color(g1)
    c2 = nx.bipartite.color(g2)
    n1 = list(g1.neighbors(v1))
    n2 = list(g2.neighbors(v2))
    for perm in itertools.permutations(range(3)):
        h = nx.Graph()
        h.add_edges_from(((0, a), (0, b)) for a, b in g1.edges() if v1 not in (a, b))
        h.add_edges_from(((1, a), (1, b)) for a, b in g2.edges() if v2 not in (a, b))
        for i in range(3):
            h.add_edge((0, n1[i]), (1, n2[perm[i]]))
        if nx.check_planarity(h)[0] and nx.is_bipartite(h):
            return nx.convert_node_labels_to_integers(h, label_attribute="origin")
    return None


def octahedral(level):
    """the dual of the octahedron subdivided level times"""
    tris = [(a, b, c) for a in (0, 1) for b in (2, 3) for c in (4, 5)]
    return subdivided_dual(tris, level)
