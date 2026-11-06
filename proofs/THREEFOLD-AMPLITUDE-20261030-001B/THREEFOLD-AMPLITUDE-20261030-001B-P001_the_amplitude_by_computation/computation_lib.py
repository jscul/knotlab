"""Builders for THREEFOLD-AMPLITUDE-20261030-001B: systems from bipartite graphs, omnitruncations of planar maps, the glue of a hypermap,
hypertree counts (Kalman), spanning-tree counts, trisums of prisms along a square face, and the product of brace amplitudes."""
import itertools
import networkx as nx
import sympy
from networkx.algorithms.tree.mst import SpanningTreeIterator


def system_of(g, point=None):
    """the system of a cubic bipartite graph: lines are the vertices of the colour class not containing `point` (default: class 1)"""
    col = nx.bipartite.color(g)
    if point is not None and col[point] != 0:
        col = {v: 1 - c for v, c in col.items()}
    pts = sorted((v for v in g if col[v] == 0), key=str)
    pid = {v: k for k, v in enumerate(pts)}
    return [tuple(sorted(pid[w] for w in g[v])) for v in sorted(g, key=str) if col[v] == 1]


def faces_of(g):
    ok, emb = nx.check_planarity(g)
    assert ok
    seen, out = set(), []
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        out.append(emb.traverse_face(u, v, mark_half_edges=seen))
    return out


def omnitruncation(g):
    """the flag graph of a planar map: a vertex per flag (dart, side), joined along the three reflections"""
    ok, emb = nx.check_planarity(g)
    assert ok
    G = nx.Graph()
    for u, v in emb.edges():
        for s in (0, 1):
            w = emb[u][v]['cw'] if s == 0 else emb[u][v]['ccw']
            G.add_edge((u, v, s), (u, w, 1 - s))      # the other edge at u in the same face
            G.add_edge((u, v, s), (u, v, 1 - s))      # the other face at the same vertex and edge
            G.add_edge((u, v, s), (v, u, 1 - s))      # the other end of the edge, same face
    return G


def hypermap_glue(G):
    """the planar cubic bipartite graph of a hypermap: cone every face of the plane bipartite graph G (a trinity with colours U, W, faces)
    and take the planar dual"""
    tris = []
    for k, f in enumerate(faces_of(G)):
        for i in range(len(f)):
            tris.append((('f', k), f[i], f[(i + 1) % len(f)]))
    side = {}
    for i, t in enumerate(tris):
        for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            side.setdefault(frozenset(e), []).append(i)
    P = nx.Graph()
    for e, fs in side.items():
        assert len(fs) == 2
        P.add_edge(fs[0], fs[1])
    return P


def hypertrees(G, W):
    """Kalman's hypertrees of the hypergraph whose hyperedges are the vertices of W (with their neighbours): the distinct vectors
    (deg_T(w) - 1 for w in W) over spanning trees T of G"""
    W = sorted(W, key=str)
    return len({tuple(T.degree(w) - 1 for w in W) for T in SpanningTreeIterator(G)})


def spanning_trees(g):
    """Kirchhoff: number of spanning trees of a connected (multi)graph, exactly"""
    nodes = sorted(g, key=str)
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    Lm = [[0] * n for _ in range(n)]
    for u, v in g.edges():
        if u == v:
            continue
        a, b = idx[u], idx[v]
        Lm[a][a] += 1
        Lm[b][b] += 1
        Lm[a][b] -= 1
        Lm[b][a] -= 1
    return int(sympy.Matrix(Lm)[1:, 1:].det())


C4 = [('c', j) for j in range(4)]


def prism_on(k, tag, flip=False):
    """the 2k-prism with its square face u0 u1 v1 v0 identified with C4 (c0 = u0, c1 = u1, c2 = v1, c3 = v0); flip reflects the face
    (c0 and c2 exchanged)"""
    m = 2 * k
    g = nx.Graph()
    for i in range(m):
        g.add_edges_from([(('u', i), ('u', (i + 1) % m)), (('v', i), ('v', (i + 1) % m)), (('u', i), ('v', i))])
    face = [('u', 0), ('u', 1), ('v', 1), ('v', 0)]
    target = C4 if not flip else [C4[2], C4[1], C4[0], C4[3]]
    mp = dict(zip(face, target))
    return nx.relabel_nodes(g, lambda v: mp.get(v, (tag, v)))


def trisum_of_prisms(ks, flips=(False, False, False)):
    """the cubic trisum of three prisms (2k-prisms for k in ks) along a common square face, all four face edges deleted"""
    g = nx.Graph()
    for t, (k, f) in enumerate(zip(ks, flips)):
        g.add_edges_from(prism_on(k, 'abc'[t], f).edges())
    g.remove_edges_from([(C4[j], C4[(j + 1) % 4]) for j in range(4)])
    assert all(d == 3 for _, d in g.degree())
    return g


def brace_factor(b, M, AM):
    """the amplitude of a brace of a tight-cut decomposition (grammar_lib M, amplitude_lib AM): the two-vertex brace (one point thrice on
    one line, the system with one point) 1, Heawood 5, doubled square 1, planar: Tutte's tree-trinity number (an arborescence number),
    otherwise the amplitude at one line with a Pfaffian signing found by search"""
    if len(b) == 2:
        return 1, 'theta'
    t = M.brace_type(b)[0]
    if t == 'heawood':
        return 5, t
    if t == 'doubled square':
        return 1, t
    pts = sorted([v for v in b if M.kind(v) == 'P'], key=str)
    pid = {v: k for k, v in enumerate(pts)}
    Hb = [tuple(sorted(pid[w] for w in b[v])) for v in sorted(b, key=str) if M.kind(v) == 'L']
    if t == 'planar':
        return AM.arborescence_number(Hb, 0), t
    return AM.amplitude(Hb, 0, M.pfaffian_signings(Hb, limit=1)[0]), t


def brace_product(H, M, AM):
    """the product of the brace amplitudes of H and the brace kinds"""
    prod, kinds = 1, []
    for b in M.decompose(M.multigraph(H)):
        f, t = brace_factor(b, M, AM)
        prod *= f
        kinds.append(t)
    return prod, kinds
