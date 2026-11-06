"""Glue and decoration for cubic triple systems (THREEFOLD-GRAMMAR-20261030-001A); uses threefold_lib of THREEFOLD-SPACES-20261030-001A.

A multi-system is a list of lines, each a triple of points with repetition allowed, every point occurring three times in total.  A
signing is a set of negated incidences (line index, point) of multiplicity one.  Decoration replaces a point by a piece attached through
the three points of the piece's root line: a Fano block (Fano plane minus a line, untwisted) or the twisted 14-point system T14 (twisted
at the incidence (root line, port 0))."""
import itertools
import networkx as nx
import threefold_lib as T

FANO = T.FANO
T14 = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 7, 8), (1, 9, 10), (2, 7, 9), (2, 8, 10), (3, 5, 11), (3, 6, 12), (4, 5, 12),
       (4, 6, 11), (7, 10, 13), (8, 9, 13), (11, 12, 13)]          # twisted at (line 0, point 0); line 0 is its root line
K4 = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]                  # incidence graph = the cube


def incidences(H):
    inc = {}
    for i, l in enumerate(H):
        for k, p in enumerate(l):
            inc.setdefault(p, []).append((i, k))
    return inc


def decorate(H, neg):
    """replace every point that carries a negated incidence or a repeated incidence by a piece: an odd number of negations at the point
    (after switching at the point, one) calls for T14 with its twisted port on the odd incidence, an even number for a Fano block"""
    inc = incidences(H)
    neg = set(neg)
    port = {}                              # (line index, position) -> new label
    pieces = []
    for p, lst in inc.items():
        lines_here = [i for i, k in lst]
        negs = [(i, k) for i, k in lst if (i, p) in neg]
        repeated = len(set(lines_here)) < 3
        if not negs and not repeated:
            for i, k in lst:
                port[(i, k)] = ('o', p)
            continue
        if len(negs) in (1, 2):
            odd = negs[0] if len(negs) == 1 else next(x for x in lst if x not in negs)
            piece, twisted = T14, True
            order = [odd] + [x for x in lst if x != odd]
        else:
            piece, twisted = FANO, False
            order = list(lst)
        root = piece[0]
        for (i, k), q in zip(order, root):
            port[(i, k)] = ('c', p, q)
        pieces.append((p, piece))
    lines = [tuple(port[(i, k)] for k in range(3)) for i, l in enumerate(H)]
    for p, piece in pieces:
        for j, l in enumerate(piece):
            if j != 0:
                lines.append(tuple(('c', p, q) for q in l))
    pts = sorted({x for l in lines for x in l}, key=str)
    pid = {x: k for k, x in enumerate(pts)}
    return [tuple(sorted(pid[x] for x in l)) for l in lines]


def bipartite(H):
    g = nx.Graph()
    for i, l in enumerate(H):
        g.add_node(('L', i))
        for p in l:
            g.add_node(('P', p))
            g.add_edge(('L', i), ('P', p))
    return g


def faces(H):
    """faces of a planar embedding of the incidence graph of a simple system, as lists of directed edges (u, v)"""
    g = bipartite(H)
    ok, emb = nx.check_planarity(g)
    if not ok:
        return None
    seen, out = set(), []
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        f = emb.traverse_face(u, v, mark_half_edges=seen)
        out.append(f)
    return out


def kasteleyn_signing(H):
    """a set of negated incidences such that every face but one of a planar embedding of B(H) of length 2l carries l - 1 negations mod 2
    (Kasteleyn); returns None when B(H) is not planar"""
    fs = faces(H)
    if fs is None:
        return None
    edges = [(i, p) for i, l in enumerate(H) for p in sorted(set(l))]
    eid = {e: k for k, e in enumerate(edges)}
    rows = []
    for f in fs[:-1]:
        vec = 0
        for a, b in zip(f, f[1:] + f[:1]):
            line, point = (a, b) if a[0] == 'L' else (b, a)
            vec ^= 1 << eid[(line[1], point[1])]
        rhs = (len(f) // 2 - 1) % 2
        rows.append((vec, rhs))
    # Gaussian elimination over GF(2)
    piv = {}
    for vec, rhs in rows:
        for b, (pv, pr) in piv.items():
            if vec >> b & 1:
                vec ^= pv
                rhs ^= pr
        if vec == 0:
            if rhs:
                return None
            continue
        b = vec.bit_length() - 1
        for b2 in list(piv):
            pv, pr = piv[b2]
            if pv >> b & 1:
                piv[b2] = (pv ^ vec, pr ^ rhs)
        piv[b] = (vec, rhs)
    x = 0
    for b, (pv, pr) in piv.items():
        if pr:
            x |= 1 << b
    return [edges[k] for k in range(len(edges)) if x >> k & 1]


def hexagonal_prism():
    colr = {('u', i): i % 2 for i in range(6)}
    colr.update({('v', i): (i + 1) % 2 for i in range(6)})
    adj = {}
    for i in range(6):
        for a, b in ((('u', i), ('u', (i + 1) % 6)), (('v', i), ('v', (i + 1) % 6)), (('u', i), ('v', i))):
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
    pts = [v for v in colr if colr[v] == 0]
    pid = {v: k for k, v in enumerate(pts)}
    return [tuple(sorted(pid[w] for w in adj[v])) for v in colr if colr[v] == 1]


def cubic_planar_bipartite(name):
    """a few planar cubic bipartite graphs as triple systems (points = one colour class)"""
    if name == 'cube':
        return K4
    if name == 'hexagonal prism':
        return hexagonal_prism()
    if name == 'truncated octahedron':
        g = nx.Graph()
        # vertices: permutations of (0, 1, 2, 3) with adjacency by an adjacent transposition (Cayley graph of S4) = truncated octahedron
        perms = list(itertools.permutations(range(4)))
        for p in perms:
            for i in range(3):
                q = list(p)
                q[i], q[i + 1] = q[i + 1], q[i]
                g.add_edge(p, tuple(q))
        sign = {p: sum(1 for a, b in itertools.combinations(range(4), 2) if p[a] > p[b]) % 2 for p in perms}
        pts = [p for p in perms if sign[p] == 0]
        pid = {p: k for k, p in enumerate(pts)}
        return [tuple(sorted(pid[w] for w in g[v])) for v in perms if sign[v] == 1]
    raise ValueError(name)


# ------------------------------------------------------------------------------------------------ tight-cut decomposition
def multigraph(H):
    """bipartite incidence multigraph: dict vertex -> Counter of neighbours (points ('P', p), lines ('L', i))"""
    from collections import Counter
    adj = {}
    for i, l in enumerate(H):
        adj.setdefault(('L', i), Counter())
        for p in l:
            adj[('L', i)][('P', p)] += 1
            adj.setdefault(('P', p), Counter())[('L', i)] += 1
    return adj


def kind(v):
    """'P' for points and contracted point-type vertices, 'L' otherwise"""
    return 'P' if v[0] == 'P' or (v[0] == 'X' and v[1] == 'P') else 'L'


def _has_pm(adj, removed):
    g = nx.Graph()
    side_a = [v for v in adj if kind(v) == 'P' and v not in removed]
    side_b = [v for v in adj if kind(v) == 'L' and v not in removed]
    g.add_nodes_from(side_a, bipartite=0)
    g.add_nodes_from(side_b, bipartite=1)
    for u in side_a:
        for w in adj[u]:
            if w not in removed:
                g.add_edge(u, w)
    if len(side_a) != len(side_b):
        return False, None, None
    m = nx.bipartite.hopcroft_karp_matching(g, top_nodes=side_a)
    if sum(1 for u in side_a if u in m) == len(side_a):
        return True, None, None
    return False, g, m


def find_tight_cut(adj):
    """a nontrivial tight cut shore (set of vertices), or None if the graph is a brace; via a pair of disjoint edges that does not extend
    to a perfect matching and the Hall violator it leaves (assumes a connected matching-covered bipartite multigraph)"""
    edges = [(u, w) for u in adj if kind(u) == 'P' for w in adj[u]]
    n = len(adj)
    for e, f in itertools.combinations(edges, 2):
        if len({e[0], e[1], f[0], f[1]}) < 4:
            continue
        removed = {e[0], e[1], f[0], f[1]}
        ok, g, m = _has_pm(adj, removed)
        if ok:
            continue
        # Hall violator on the point side: points reachable by alternating paths from an unmatched point
        side_a = [v for v in g if kind(v) == 'P']
        free = [u for u in side_a if u not in m]
        reach_a, reach_b = set(free), set()
        stack = list(free)
        while stack:
            u = stack.pop()
            for w in g[u]:
                if w not in reach_b:
                    reach_b.add(w)
                    v = m.get(w)
                    if v is not None and v not in reach_a:
                        reach_a.add(v)
                        stack.append(v)
        S = reach_a                                 # points; N_G(S) in the full graph
        NS = {w for u in S for w in adj[u]}
        for cand in (S, ):
            if len(NS) == len(S) + 1:
                X = set(S) | NS
                if 3 <= len(X) <= n - 3:
                    return X
        # try the line side symmetric violator
        side_b = [v for v in g if kind(v) == 'L']
        freeb = [w for w in side_b if w not in m]
        reach_b2, reach_a2 = set(freeb), set()
        stack = list(freeb)
        while stack:
            w = stack.pop()
            for u in g[w]:
                if u not in reach_a2:
                    reach_a2.add(u)
                    v = m.get(u)
                    if v is not None and v not in reach_b2:
                        reach_b2.add(v)
                        stack.append(v)
        S2 = reach_b2
        NS2 = {u for w in S2 for u in adj[w]}
        if len(NS2) == len(S2) + 1:
            X = set(S2) | NS2
            if 3 <= len(X) <= n - 3:
                return X
    return None


def contract(adj, X, name):
    """contract the shore X to a single vertex called name (kind of the majority side of X)"""
    from collections import Counter
    out = {}
    for u, nb in adj.items():
        if u in X:
            continue
        c = Counter()
        for w, k in nb.items():
            c[name if w in X else w] += k
        out[u] = c
    cnt = Counter()
    for u in X:
        for w, k in adj[u].items():
            if w not in X:
                cnt[w] += k
    out[name] = cnt
    return out


def decompose(adj, counter=None):
    """tight-cut decomposition: list of braces (as adjacency multigraphs) with their contracted vertices marked ('X', k)"""
    if counter is None:
        counter = [0]
    X = find_tight_cut(adj)
    if X is None:
        return [adj]
    pts = sum(1 for v in X if kind(v) == 'P')
    lines = len(X) - pts
    k = counter[0]
    counter[0] += 1
    # the vertex replacing X takes the kind of X's majority side; the vertex replacing the complement the other kind
    maj = 'P' if pts > lines else 'L'
    rest = set(adj) - set(X)
    a1 = contract(adj, X, ('X', maj, k))
    a2 = contract(adj, rest, ('X', 'L' if maj == 'P' else 'P', k))
    return decompose(a1, counter) + decompose(a2, counter)


HEAWOOD = None


def brace_type(adj):
    """'heawood', 'doubled square', 'planar' or 'other' (underlying simple graph), with the number of contracted vertices"""
    global HEAWOOD
    if HEAWOOD is None:
        HEAWOOD = nx.Graph([(('P', p), ('L', i)) for i, l in enumerate(FANO) for p in l])
    g = nx.Graph([(u, w) for u in adj for w in adj[u]])
    mult = any(k > 1 for u in adj for k in adj[u].values())
    ncon = sum(1 for v in adj if v[0] == 'X')
    if len(adj) == 4 and mult:
        return 'doubled square', ncon
    if len(adj) == 14 and not mult and nx.is_isomorphic(g, HEAWOOD):
        return 'heawood', ncon
    if nx.check_planarity(g)[0]:
        return 'planar', ncon
    return 'other', ncon


def leaf_kinds(H):
    """(brace type, kind of the contracted vertex) for every leaf of the decomposition: a Heawood leaf contracted at a line is a Fano
    block (Fano minus a line, attached at its points), one contracted at a point a dual block (Fano minus a point, attached at its lines)"""
    from collections import Counter
    out = Counter()
    for b in decompose(multigraph(H)):
        t, n = brace_type(b)
        if n == 1:
            x = next(v for v in b if v[0] == 'X')
            out[(t, 'block' if kind(x) == 'L' else 'dual block')] += 1
    return out


# ------------------------------------------------------------------------------------------------ Pfaffian braces and their 4-cycles
def system_of(g):
    """triple system of a bipartite networkx graph with equal colour classes (points = colour class 0)"""
    col = nx.bipartite.color(g)
    pts = sorted((v for v in g if col[v] == 0), key=str)
    pid = {v: k for k, v in enumerate(pts)}
    return [tuple(sorted(pid[w] for w in g[v])) for v in sorted(g, key=str) if col[v] == 1]


def cube_on(C, tag):
    """a cube through the 4-cycle C = (c0, c1, c2, c3); the opposite face is new, with vertices (tag, j)"""
    g = nx.Graph()
    for j in range(4):
        g.add_edge(C[j], C[(j + 1) % 4])
        g.add_edge((tag, j), (tag, (j + 1) % 4))
        g.add_edge(C[j], (tag, j))
    return g


def trisum(graphs, C, deleted):
    """the trisum (Robertson-Seymour-Thomas) of three graphs whose pairwise intersections are the 4-cycle C, minus the edges deleted"""
    assert len(graphs) == 3
    Cset = set(C)
    for a, b in itertools.combinations(graphs, 2):
        assert set(a) & set(b) == Cset
    g = nx.Graph()
    for h in graphs:
        g.add_edges_from(h.edges())
    g.remove_edges_from(deleted)
    return g


def four_cycles(H):
    """4-cycles of the incidence graph, each as a frozenset of edges"""
    g = bipartite(H)
    out = set()
    for u, w in itertools.combinations(sorted(g, key=str), 2):
        common = sorted(set(g[u]) & set(g[w]), key=str)
        for a, b in itertools.combinations(common, 2):
            out.add(frozenset(frozenset(e) for e in ((u, a), (a, w), (w, b), (b, u))))
    return list(out)


def every_4cycle_has_a_disjoint_partner(H):
    cs = four_cycles(H)
    return bool(cs) and all(any(not (c & d) for d in cs) for c in cs)


def max_disjoint_4cycles(H, cap=3):
    """size (capped) of a largest set of pairwise edge-disjoint 4-cycles"""
    cs = four_cycles(H)
    best = 0

    def grow(chosen, start):
        nonlocal best
        best = max(best, len(chosen))
        if best >= cap:
            return
        for k in range(start, len(cs)):
            if all(not (cs[k] & c) for c in chosen):
                grow(chosen + [cs[k]], k + 1)
    grow([], 0)
    return best


def pfaffian_signings(H, limit=None):
    """all sign-nonsingular signings with every edge of a fixed spanning tree positive (one per switching class), by floating
    determinants against the exact permanent; each is confirmed exactly with threefold_lib.sns"""
    import numpy as np
    g = bipartite(H)
    tree = set(frozenset(e) for e in nx.minimum_spanning_edges(g, data=False))
    co = [e for e in g.edges() if frozenset(e) not in tree]
    co = [(a[1], b[1]) if a[0] == 'L' else (b[1], a[1]) for a, b in co]
    A0 = T.matrix(H).astype(float)
    per = T.permanent(T.matrix(H))
    out = []
    for mask in range(1 << len(co)):
        A = A0.copy()
        neg = [co[k] for k in range(len(co)) if mask >> k & 1]
        for i, p in neg:
            A[i, p] = -A[i, p]
        if abs(abs(np.linalg.det(A)) - per) < 0.5:
            assert T.sns(H, neg)[0]
            out.append(neg)
            if limit and len(out) >= limit:
                break
    return out
