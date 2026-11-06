"""Polynomial counting on Seymour's cubic bound (SEYMOUR-COUNT-20261030-001B).

A three-fold space H is a connected cubic triple system that is not 2-colourable. Its incidence graph is cubic bipartite, with the points and
the lines as colour classes, and A(H, L) = #col(H - L) / 2 is the product of the amplitudes of the braces of that graph
(THREEFOLD-AMPLITUDE-20261030-001C, Corollary 5). This library computes every factor in polynomial time, without any signing:
  - the two-vertex and the four-vertex brace give 1, the Heawood graph 5;
  - a planar brace gives |det| of its line-face matrix (rows: the lines other than one line L; columns: the faces not at L; Berman 1980);
  - any other brace (non-planar, Pfaffian) is split along trisectors, sets of four vertices whose removal leaves three components
    (Robertson-Seymour-Thomas 1999, 8.4), until every piece is planar. Each planar piece is then one weighted determinant, in which the two
    branches beyond each of its squares weight the rows of the square's lines (ticket A, Proposition 5), and the first square closes by
    the trisum law (ticket A, Theorem 3).

Graphs are networkx graphs. A square is a tuple (c0, c1, c2, c3) of four vertices: c0, c2 points and c1, c3 lines. Its split (alpha, beta),
for a branch glued there, counts half the colourings of the branch minus c1 in which the third point of c3 agrees, as seen by c3, with c0,
respectively with c2."""
import itertools
import networkx as nx
import grammar_lib as M


# ------------------------------------------------------------------------------------------------ determinants of planar pieces
def det(rows):
    """exact determinant of an integer matrix (Bareiss elimination, fraction-free)"""
    a = [list(r) for r in rows]
    n = len(a)
    if n == 0:
        return 1
    sign, prev = 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if a[i][k] != 0), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) // prev
        prev = a[k][k]
    return sign * a[n - 1][n - 1]


def plane_faces(g):
    """the faces of the planar embedding of g, as vertex sets (unique for a 3-connected graph)"""
    ok, emb = nx.check_planarity(g)
    assert ok
    seen, out = set(), []
    for u, v in emb.edges():
        if (u, v) not in seen:
            out.append(set(emb.traverse_face(u, v, mark_half_edges=seen)))
    return out


def side_faces(faces, sq):
    """the face of the square and the side faces of its lines: c3F0 is the face holding c3 and c0 but not c2, and so on"""
    c0, c1, c2, c3 = sq

    def one(inside, outside):
        ks = [k for k, f in enumerate(faces) if all(v in f for v in inside) and outside not in f]
        assert len(ks) == 1, (sq, inside, outside, ks)
        return ks[0]
    own = [k for k, f in enumerate(faces) if all(v in f for v in sq)]
    assert len(own) == 1
    return {"sq": own[0], "c3F0": one((c3, c0), c2), "c3F2": one((c3, c2), c0), "c1F0": one((c1, c0), c2), "c1F2": one((c1, c2), c0)}


def line_face_matrix(g, lines, L, restrict=None, children=()):
    """rows: the lines other than L; columns: the faces not at L; entry 1 where the line lies on the face. A child square (sq, wA, wB) puts
    wA, wB on the side faces of c3 at c0, c2 and wB, wA on those of c1 (the view from c1 is swapped, ticket A, Proposition 4); restrict =
    (line, face) keeps only that entry of the line's row."""
    fs = plane_faces(g)
    rows = sorted((w for w in g if w in lines and w != L), key=str)
    cols = [k for k in range(len(fs)) if L not in fs[k]]
    W = {(w, k): 1 for w in rows for k in cols if w in fs[k]}
    for sq, wA, wB in children:
        sf = side_faces(fs, sq)
        W[(sq[3], sf["c3F0"])], W[(sq[3], sf["c3F2"])] = wA, wB
        W[(sq[1], sf["c1F0"])], W[(sq[1], sf["c1F2"])] = wB, wA
    if restrict is not None:
        w, f = restrict
        for k in cols:
            if k != f:
                W.pop((w, k), None)
    assert len(rows) == len(cols)
    return rows, cols, W


def berman(g, lines, L, restrict=None, children=()):
    """|det| of the (weighted, restricted) line-face matrix: the weighted number of Tutte matchings with outer triangle L"""
    rows, cols, W = line_face_matrix(g, lines, L, restrict, children)
    return abs(det([[W.get((w, k), 0) for k in cols] for w in rows]))


def piece_split(g, lines, S, children=()):
    """the split (alpha, beta) at the square S of the planar piece g with the given child squares: L = c1, the row of c3 restricted to its
    side face at c0, respectively at c2"""
    sf = side_faces(plane_faces(g), S)
    return tuple(berman(g, lines, S[1], (S[3], sf[k]), children) for k in ("c3F0", "c3F2"))


# ------------------------------------------------------------------------------------------------ trisectors and the trisum tree
def _cut_vertices(adj, removed, n):
    """articulation points of the graph on range(n) minus `removed` (iterative depth-first search)"""
    disc, low, out, t = [-1] * n, [0] * n, set(), 0
    for root in range(n):
        if root in removed or disc[root] >= 0:
            continue
        disc[root] = low[root] = t
        t += 1
        kids = 0
        stack = [(root, -1, iter(adj[root]))]
        while stack:
            v, parent, it = stack[-1]
            w = next(it, None)
            if w is None:
                stack.pop()
                if stack:
                    u = stack[-1][0]
                    low[u] = min(low[u], low[v])
                    if stack[-1][1] != -1 and low[v] >= disc[u]:
                        out.add(u)
                continue
            if w in removed or w == parent:
                continue
            if disc[w] >= 0:
                low[v] = min(low[v], disc[w])
            else:
                disc[w] = low[w] = t
                t += 1
                if v == root:
                    kids += 1
                stack.append((w, v, iter(adj[w])))
        if kids >= 2:
            out.add(root)
    return out


def _components(adj, removed, n):
    seen, k = set(removed), 0
    for s in range(n):
        if s in seen:
            continue
        k += 1
        seen.add(s)
        todo = [s]
        while todo:
            v = todo.pop()
            for w in adj[v]:
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
    return k


def four_cycle_vertices(g):
    """the vertices of g that lie on a 4-cycle"""
    out = set()
    for v in g:
        for a, b in itertools.combinations(g[v], 2):
            common = (set(g[a]) & set(g[b])) - {v}
            if common:
                out |= {v, a, b} | common
    return out


def find_trisector(g, lines, prune=True):
    """a trisector of the cubic graph g as a labelled square (c0, c1, c2, c3), or None: two points and two lines, pairwise non-adjacent,
    whose removal leaves at least three components. For each pair of points c0, c2 and line c1 the fourth vertex is a cut vertex of
    g - {c0, c1, c2}, so the search takes O(n^3) depth-first searches. prune=True skips vertices on 4-cycles, which no trisector of a
    Pfaffian cubic brace contains (a trisector vertex on a 4-cycle puts K2,3 in a piece; Robertson-Seymour-Thomas 8.3, 8.7)."""
    nodes = sorted(g, key=str)
    idx = {v: i for i, v in enumerate(nodes)}
    adj = [[idx[w] for w in g[v]] for v in nodes]
    n = len(nodes)
    skip = {idx[v] for v in four_cycle_vertices(g)} if prune else set()
    P = [idx[v] for v in nodes if v not in lines and idx[v] not in skip]
    Lset = {idx[v] for v in nodes if v in lines and idx[v] not in skip}
    for c0, c2 in itertools.combinations(P, 2):
        near = set(adj[c0]) | set(adj[c2])
        for c1 in sorted(Lset - near):
            for c3 in sorted(_cut_vertices(adj, {c0, c1, c2}, n)):
                if c3 in Lset and c3 not in near and _components(adj, {c0, c1, c2, c3}, n) >= 3:
                    return tuple(nodes[i] for i in (c0, c1, c2, c3))
    return None


def all_trisectors(g, lines):
    """every trisector of g (unpruned search; for checks on small graphs), as frozensets"""
    nodes = sorted(g, key=str)
    idx = {v: i for i, v in enumerate(nodes)}
    adj = [[idx[w] for w in g[v]] for v in nodes]
    n = len(nodes)
    P = [idx[v] for v in nodes if v not in lines]
    Lset = {idx[v] for v in nodes if v in lines}
    out = set()
    for c0, c2 in itertools.combinations(P, 2):
        for c1 in sorted(Lset):
            for c3 in _cut_vertices(adj, {c0, c1, c2}, n):
                if c3 in Lset and _components(adj, {c0, c1, c2, c3}, n) >= 3:
                    out.add(frozenset(nodes[i] for i in (c0, c1, c2, c3)))
    return out


def split_at(g, X):
    """the pieces of the trisum along the trisector X: each component of g - X with X and the square's four edges"""
    rest = g.copy()
    rest.remove_nodes_from(X)
    pieces = []
    for K in nx.connected_components(rest):
        h = g.subgraph(set(K) | set(X)).copy()
        h.add_edges_from([(X[j], X[(j + 1) % 4]) for j in range(4)])
        pieces.append(h)
    return pieces


def trisum_tree(T, lines):
    """split the cubic brace T along trisectors until every piece is planar. Returns (leaves, squares): a leaf is (graph, its squares), and
    squares are listed in the order found, the first being a trisector of T."""
    work, leaves, squares = [(T, [])], [], []
    while work:
        g, sqs = work.pop()
        if nx.check_planarity(g)[0]:
            leaves.append((g, sqs))
            continue
        X = find_trisector(g, lines)
        if X is None:
            raise ValueError("a non-planar piece with no trisector: the brace is not Pfaffian, or is the Heawood graph")
        squares.append(X)
        pieces = split_at(g, X)
        for s in sqs:
            assert sum(set(s) <= set(h) for h in pieces) == 1
        for h in pieces:
            assert all(d == 3 for _, d in h.degree())
            work.append((h, [s for s in sqs if set(s) <= set(h)] + [X]))
    return leaves, squares


def law(splits):
    """the trisum law (ticket A, Theorem 3): weighted choices of leanings that are not all equal"""
    (a1, b1), (a2, b2), (a3, b3) = splits
    return (a1 + b1) * (a2 + b2) * (a3 + b3) - a1 * a2 * a3 - b1 * b2 * b3


def tree_amplitude(leaves, squares, lines, swapped=True, root=0):
    """the amplitude of a brace from its trisum tree: the trisum law at the square squares[root], whose three branches each have their split
    from their leaf at that square as one weighted determinant, the two branches beyond each other square of the leaf giving the weights.
    swapped=False uses the unswapped weights on c1's row (a control)."""
    at = {X: [i for i, (g, sqs) in enumerate(leaves) if X in sqs] for X in squares}
    assert all(len(v) == 3 for v in at.values())

    def branch(i, S):
        g, sqs = leaves[i]
        children = []
        for D in sqs:
            if D == S:
                continue
            j, k = [l for l in at[D] if l != i]
            (aQ, bQ), (aR, bR) = branch(j, D), branch(k, D)
            rr = (aQ + bQ) * (aR + bR)
            wA, wB = rr - aQ * aR, rr - bQ * bR
            children.append((D, wA, wB) if swapped else (D, wA, wB, 'unswapped'))
        if not swapped:
            return _unswapped_split(g, lines, S, children)
        return piece_split(g, lines, S, children)
    X0 = squares[root]
    return law([branch(i, X0) for i in at[X0]])


def _unswapped_split(g, lines, S, children):
    fs = plane_faces(g)
    sf = side_faces(fs, S)
    out = []
    for key in ("c3F0", "c3F2"):
        rows, cols, W = line_face_matrix(g, lines, S[1], (S[3], sf[key]), [(D, wA, wB) for D, wA, wB, _ in children])
        for D, wA, wB, _ in children:
            sd = side_faces(fs, D)
            W[(D[1], sd["c1F0"])], W[(D[1], sd["c1F2"])] = wA, wB
        out.append(abs(det([[W.get((w, k), 0) for k in cols] for w in rows])))
    return tuple(out)


# ------------------------------------------------------------------------------------------------ braces and spaces
def brace_amplitude(b):
    """(amplitude, kind) of a brace of the tight-cut decomposition (grammar_lib adjacency multigraph)"""
    if len(b) == 2:
        return 1, 'theta'
    t = M.brace_type(b)[0]
    if t == 'heawood':
        return 5, t
    if t == 'doubled square':
        return 1, t
    g = nx.Graph([(u, w) for u in b for w in b[u]])
    lines = {v for v in g if M.kind(v) == 'L'}
    if t == 'planar':
        return berman(g, lines, min(lines, key=str)), t
    leaves, squares = trisum_tree(g, lines)
    return tree_amplitude(leaves, squares, lines), f"trisum tree ({len(leaves)} planar pieces)"


def space_amplitude(H):
    """A(H, L) for a three-fold space H (any line L): the product over the braces of its incidence graph, and the brace kinds"""
    prod, kinds = 1, []
    for b in M.decompose(M.multigraph(H)):
        a, t = brace_amplitude(b)
        prod *= a
        kinds.append(t)
    return prod, kinds
