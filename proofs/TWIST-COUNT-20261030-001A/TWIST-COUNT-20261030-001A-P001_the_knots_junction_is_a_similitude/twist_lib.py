"""Counting one twist off the bound (TWIST-COUNT-20261030-001A).

A signing of a cubic bipartite graph is a set of negated incidences (edges, as frozensets {line, point}); #col counts the point colourings
in which every line sees (colour xor sign) not all equal. In the Hadamard basis (H = [[1, 1], [1, -1]] on every edge) points become EVEN3,
lines [3, 0, -1, 0] and negations Z.

Trisum trees come from seymour_lib (SEYMOUR-COUNT-20261030-001B): leaves are planar braces with their squares (c0, c1, c2, c3), c0 and c2
points, c1 and c3 lines. A *branch tensor* F(z0, z1, z2, z3) at a square counts the colourings of the branch's own points: z0 and z2 are the
colours of c0 and c2, z1 and z3 those of the neighbours of c1 and c3 inside the branch. The signs of the square lines' incidences belong to
the *junction*, the tensor of the two closed branches at a square as seen by the third (the host)."""
import itertools
import numpy as np
import networkx as nx

H2 = np.array([[1, 1], [1, -1]], dtype=object)
EVEN = [y for y in itertools.product((0, 1), repeat=4) if sum(y) % 2 == 0]


def hada(F):
    """H applied on all four legs"""
    G = np.array(F, dtype=object)
    for ax in range(4):
        G = np.moveaxis(np.tensordot(H2, G, axes=([1], [ax])), 0, ax)
    return G


def mgi(f):
    """the 4-ary matchgate identity, legs in cyclic order (c0, c1, c2, c3)"""
    return f[0, 0, 0, 0] * f[1, 1, 1, 1] - f[1, 1, 0, 0] * f[0, 0, 1, 1] + f[1, 0, 1, 0] * f[0, 1, 0, 1] - f[1, 0, 0, 1] * f[0, 1, 1, 0]


def odd_entries(f):
    return [y for y in itertools.product((0, 1), repeat=4) if sum(y) % 2 and f[y] != 0]


def nae(a, b, c):
    return 0 if a == b == c else 1


def split_form(alpha, beta, tau, s1=0, s3=0):
    """the tensor of a closed untwisted branch with split (alpha, beta), odd square pattern tau = (t10, t12, t30, t32) and signs s1, s3 of the
    square lines' incidences into it (SEYMOUR-COUNT A, Lemma 2 and Proposition 4)"""
    t10, t12, t30, t32 = tau
    F = np.zeros((2, 2, 2, 2), dtype=object)
    for x0, z1, x2, z3 in itertools.product((0, 1), repeat=4):
        v1, v3 = z1 ^ s1, z3 ^ s3
        if (x0 ^ t10) == (x2 ^ t12):
            if v1 == x0 ^ t10:
                F[x0, z1, x2, z3] = alpha * int(v3 == x0 ^ t30) + beta * int(v3 == x2 ^ t32)
        elif v3 == x0 ^ t30:
            F[x0, z1, x2, z3] = beta * int(v1 == x0 ^ t10) + alpha * int(v1 == x2 ^ t12)
    return F


def junction(FQ, FR, s1, s3):
    """W(x0, z1, x2, z3) on the host's legs: s1 = signs of c1's incidences (host, Q, R), s3 likewise"""
    W = np.zeros((2, 2, 2, 2), dtype=object)
    for x0, x2 in itertools.product((0, 1), repeat=2):
        for zq1, zq3, zr1, zr3 in itertools.product((0, 1), repeat=4):
            w = FQ[x0, zq1, x2, zq3] * FR[x0, zr1, x2, zr3]
            if w == 0:
                continue
            for zh1, zh3 in itertools.product((0, 1), repeat=2):
                if nae(zh1 ^ s1[0], zq1 ^ s1[1], zr1 ^ s1[2]) and nae(zh3 ^ s3[0], zq3 ^ s3[1], zr3 ^ s3[2]):
                    W[x0, zh1, x2, zh3] += w
    return W


# ------------------------------------------------------------------------------------------------ signings and twists
def sgn(sign, u, v):
    return 1 if frozenset((u, v)) in sign else 0


def coboundary(edges, flips):
    """is the set `flips` (a subset of `edges`) a cut of the graph formed by `edges` (equivalently: even on every cycle)?"""
    g = nx.Graph()
    g.add_edges_from(tuple(e) for e in edges)
    side = {}
    for comp in nx.connected_components(g):
        r = next(iter(comp))
        side[r] = 0
        for u, v in nx.bfs_edges(g, r):
            side[v] = side[u] ^ (1 if frozenset((u, v)) in flips else 0)
    return all((side[a] ^ side[b]) == (1 if frozenset((a, b)) in flips else 0) for a, b in (tuple(e) for e in edges))


def kasteleyn_tree_signing(leaves):
    """a Pfaffian signing of the brace: a Kasteleyn signing of every leaf, switched so that every square carries one negation, on (c1, c0),
    then glued (SEYMOUR-COUNT-20261030-001B, Lemma 2)"""
    neg = set()
    for g, sqs in leaves:
        ok, emb = nx.check_planarity(g)
        seen, faces = set(), []
        for u, v in emb.edges():
            if (u, v) not in seen:
                faces.append(emb.traverse_face(u, v, mark_half_edges=seen))
        edges = [frozenset(e) for e in g.edges()]
        eid = {e: k for k, e in enumerate(edges)}
        piv = {}
        for f in faces[:-1]:
            vec, rhs = 0, (len(f) // 2 - 1) % 2
            for a, b in zip(f, f[1:] + f[:1]):
                vec ^= 1 << eid[frozenset((a, b))]
            for b_, (pv, pr) in piv.items():
                if vec >> b_ & 1:
                    vec, rhs = vec ^ pv, rhs ^ pr
            if vec == 0:
                assert rhs == 0
                continue
            top = vec.bit_length() - 1
            for b2 in list(piv):
                if piv[b2][0] >> top & 1:
                    piv[b2] = (piv[b2][0] ^ vec, piv[b2][1] ^ rhs)
            piv[top] = (vec, rhs)
        x = sum(1 << b_ for b_, (pv, pr) in piv.items() if pr)
        kneg = {edges[k] for k in range(len(edges)) if x >> k & 1}
        for S in sqs:
            cyc = [frozenset((S[j], S[(j + 1) % 4])) for j in range(4)]
            delta = {e for e in cyc if (e in kneg) != (e == cyc[0])}
            W = next(W for W in itertools.product((0, 1), repeat=4) if {cyc[j] for j in range(4) if W[j] != W[(j + 1) % 4]} == delta)
            for j in range(4):
                if W[j]:
                    kneg ^= {frozenset((S[j], w)) for w in g[S[j]]}
        sqe = {frozenset((S[j], S[(j + 1) % 4])) for S in sqs for j in range(4)}
        neg |= kneg - sqe
    return neg


def tree_structure(leaves, squares):
    at = {X: [i for i, (g, s) in enumerate(leaves) if X in s] for X in squares}
    tree = nx.Graph([(('leaf', i), ('sq', X)) for X in squares for i in at[X]])
    tree.add_nodes_from(('leaf', i) for i in range(len(leaves)))
    return at, tree


def branch_leaves(tree, S, i):
    """the leaves of the branch of square S that contains leaf i"""
    t = tree.copy()
    t.remove_node(('sq', S))
    return {k for kind, k in nx.node_connected_component(t, ('leaf', i)) if kind == 'leaf'}


def own_edges(g, sqs):
    sqe = {frozenset((S[j], S[(j + 1) % 4])) for S in sqs for j in range(4)}
    return {frozenset(e) for e in g.edges()} - sqe


def twisted_branches(leaves, squares, sign, kappa):
    """{(S, i): twisted?} for each square S and leaf i at S: the branch is twisted when sign and kappa differ by a non-cut on its edges"""
    at, tree = tree_structure(leaves, squares)
    out = {}
    for S in squares:
        for i in at[S]:
            E = set()
            for k in branch_leaves(tree, S, i):
                E |= own_edges(*leaves[k])
            out[(S, i)] = not coboundary(E, {e for e in E if (e in sign) != (e in kappa)})
    return out


def good_root(leaves, squares, tw):
    """a leaf from which every square has at most one twisted closed branch, or None"""
    at, tree = tree_structure(leaves, squares)
    for r in range(len(leaves)):
        ok = True
        for S in squares:
            closed = [i for i in at[S] if r not in branch_leaves(tree, S, i)]
            ok &= sum(tw[(S, i)] for i in closed) <= 1
        if ok:
            return r
    return None


# ------------------------------------------------------------------------------------------------ the junction tensor network
def evaluate(leaves, squares, lines, sign, root):
    """#col of the brace under `sign`, exactly, by the junction tensor network rooted at leaf `root` (brute force inside each leaf).
    Returns (count, junction records): for each junction, the square, the two closed leaves and the matchgate identity of its gadget."""
    at, tree = tree_structure(leaves, squares)
    records = []

    def leaf_sum(i, parent):
        g, sqs = leaves[i]
        sqv = {v for S in sqs for v in S}
        children = [S for S in sqs if S != parent]
        gadgets = {}
        for D in children:
            j, k = [l for l in at[D] if l != i]
            FQ, FR = branch(j, D), branch(k, D)
            legs = {}
            for side, l in (('h', i), ('q', j), ('r', k)):
                gl = leaves[l][0]
                legs[side] = [[w for w in gl[D[t]] if w not in D][0] for t in range(4)]
            s1 = tuple(sgn(sign, D[1], legs[x][1]) for x in 'hqr')
            s3 = tuple(sgn(sign, D[3], legs[x][3]) for x in 'hqr')
            W = junction(FQ, FR, s1, s3)
            records.append((D, j, k, mgi(hada(W))))
            gadgets[D] = (W, legs['h'])
        pts = sorted((v for v in g if v not in lines and (parent is None or v not in (parent[0], parent[2]))), key=str)
        own_lines = [v for v in g if v in lines and v not in sqv]
        return g, pts, own_lines, gadgets

    def weight(g, x, own_lines, gadgets):
        w = 1
        for l in own_lines:
            if not nae(*[x[p] ^ sgn(sign, l, p) for p in g[l]]):
                return 0
        for D, (W, legh) in gadgets.items():
            w *= W[x[D[0]], x[legh[1]], x[D[2]], x[legh[3]]]
            if w == 0:
                return 0
        return w

    memo = {}

    def branch(i, S):
        if (i, S) in memo:
            return memo[(i, S)]
        g, pts, own_lines, gadgets = leaf_sum(i, S)
        a1 = [w for w in g[S[1]] if w not in S][0]
        a3 = [w for w in g[S[3]] if w not in S][0]
        F = np.zeros((2, 2, 2, 2), dtype=object)
        for z0, z2 in itertools.product((0, 1), repeat=2):
            for bits in itertools.product((0, 1), repeat=len(pts)):
                x = dict(zip(pts, bits))
                x[S[0]], x[S[2]] = z0, z2
                w = weight(g, x, own_lines, gadgets)
                if w:
                    F[z0, x[a1], z2, x[a3]] += w
        memo[(i, S)] = F
        return F

    g, pts, own_lines, gadgets = leaf_sum(root, None)
    total = 0
    for bits in itertools.product((0, 1), repeat=len(pts)):
        total += weight(g, dict(zip(pts, bits)), own_lines, gadgets)
    return total, records


# ------------------------------------------------------------------------------------------------ pages: planar branches with a square face
def page(g, face=None):
    """a planar cubic bipartite brace g with a 4-face labelled as the square (colour class 0 of nx.bipartite.color as points). Returns
    (incidences of the page's own lines, its own points, {c1: neighbour, c3: neighbour}, the labelled square)."""
    col = nx.bipartite.color(g)
    if face is None:
        ok, emb = nx.check_planarity(g)
        seen, faces = set(), []
        for u, v in emb.edges():
            if (u, v) not in seen:
                faces.append(emb.traverse_face(u, v, mark_half_edges=seen))
        face = [f for f in faces if len(f) == 4][0]
    i0 = [k for k in range(4) if col[face[k]] == 0][0]
    sq = list(face[i0:]) + list(face[:i0])
    lab = dict(zip(sq, ('c0', 'c1', 'c2', 'c3')))
    lines = [v for v in g if col[v] == 1 and v not in lab]
    pts = [v for v in g if col[v] == 0 and v not in lab]
    inc = {l: [lab.get(w, w) for w in g[l]] for l in lines}
    att = {'c1': [w for w in g[sq[1]] if w not in lab][0], 'c3': [w for w in g[sq[3]] if w not in lab][0]}
    return inc, pts, att, sq


def page_tensor(inc, pts, att, sign):
    """F(z0, z1, z2, z3) of a page under `sign` (a set of (line, point) incidences, points 'c0'/'c2' allowed)"""
    pidx = {p: k for k, p in enumerate(pts)}
    allx = np.array(list(itertools.product((0, 1), repeat=len(pts))), dtype=np.int8)
    F = np.zeros((2, 2, 2, 2), dtype=object)
    for z0, z2 in itertools.product((0, 1), repeat=2):
        ok = np.ones(len(allx), dtype=bool)
        for l, ps in inc.items():
            vals = []
            for p in ps:
                s = 1 if (l, p) in sign else 0
                if p == 'c0':
                    vals.append(np.full(len(allx), z0 ^ s, dtype=np.int8))
                elif p == 'c2':
                    vals.append(np.full(len(allx), z2 ^ s, dtype=np.int8))
                else:
                    vals.append(allx[:, pidx[p]] ^ s)
            ok &= ~((vals[0] == vals[1]) & (vals[1] == vals[2]))
        sel = allx[ok]
        for a1, a3 in itertools.product((0, 1), repeat=2):
            F[z0, a1, z2, a3] += int(((sel[:, pidx[att['c1']]] == a1) & (sel[:, pidx[att['c3']]] == a3)).sum())
    return F


def page_sign_classes(inc):
    """one signing per class modulo switching at the page's own vertices: the page's own edges off a spanning forest, in all combinations
    (as sets of (line, point) incidences)"""
    interior = nx.Graph()
    for l, ps in inc.items():
        for p in ps:
            if p not in ('c0', 'c2'):
                interior.add_edge(('L', l), ('P', p))
    tree = {frozenset(e) for e in nx.minimum_spanning_edges(interior, data=False)}
    free = [(l, p) for l, ps in inc.items() for p in ps if frozenset((('L', l), ('P', p))) not in tree]
    for mask in range(1 << len(free)):
        yield {e for k, e in enumerate(free) if mask >> k & 1}


def split_of(F):
    """(alpha, beta, tau, s1, s3) if F has the split form of an untwisted closed branch, else None"""
    for tau in itertools.product((0, 1), repeat=4):
        if sum(tau) % 2 == 0:
            continue
        t10, t12, t30, t32 = tau
        for s1, s3 in itertools.product((0, 1), repeat=2):
            a = F[0, t10 ^ s1, t10 ^ t12, t30 ^ s3]
            b = F[0, t10 ^ s1, t10 ^ t12, t10 ^ t12 ^ t32 ^ s3]
            if (a or b) and (split_form(a, b, tau, s1, s3) == F).all():
                return int(a), int(b), tau, s1, s3
    return None
