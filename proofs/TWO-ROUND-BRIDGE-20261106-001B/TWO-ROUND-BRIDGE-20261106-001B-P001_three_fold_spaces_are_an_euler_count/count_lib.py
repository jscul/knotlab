"""Three-fold spaces as an Euler count, for TWO-ROUND-BRIDGE-20261106-001B.

A signed knot space is a cubic triple system (n points, n lines) with a signed not-all-equal constraint on every line. When its
incidence graph B (points and lines) is plane, a line's corner on a face is the pair of its two points that are consecutive along that
face; the corner agrees under an assignment when the two literals are equal. A satisfied line has exactly one agreeing corner, a
violated (monochromatic) one three. Kasteleyn signs make every face carry an agreeing corner under every assignment (the face cycle
cannot alternate). Corners are partitioned both by lines and by faces, and Euler's formula for the plane cubic bipartite B gives
|faces| = |lines| + 2. Summing: the lines give n agreeing corners while the faces need n + 2. This is the count behind
HANDLE-EMERGENCE-20261102-001C's skip model, used here as a refutation.

Families: the k-frequency octahedron (its dual is the Goldberg-Coxeter graph GC(k,0) of the cube, a plane cubic bipartite graph with six
squares and hexagons, treewidth growing like k), planar_lib's ladder growth from the cube, prisms and the truncated octahedron; their
decorations (grammar_lib.decorate) are unsigned three-fold spaces (non-2-colourable cubic triple systems)."""
import itertools
import sys
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"))
sys.path.insert(0, str(ROOT / "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"))
import planar_lib as PL  # noqa: E402
import grammar_lib as GR  # noqa: E402


# ------------------------------------------------------------------------------------------------ families
def octa_dual(k):
    """the dual of the k-frequency octahedron: vertices = triangles, edges = shared sides (cubic, plane, bipartite)"""
    tris = set()
    for sx, sy, sz in itertools.product((1, -1), repeat=3):
        P = lambda i, j, l: (sx * i, sy * j, sz * l)  # noqa: E731
        for i in range(k):
            for j in range(k - i):
                l = k - 1 - i - j
                tris.add(frozenset([P(i + 1, j, l), P(i, j + 1, l), P(i, j, l + 1)]))
        for i in range(k - 1):
            for j in range(k - 1 - i):
                l = k - 2 - i - j
                tris.add(frozenset([P(i + 1, j + 1, l), P(i + 1, j, l + 1), P(i, j + 1, l + 1)]))
    tris = sorted(tris, key=lambda t: sorted(t))
    by_edge = {}
    for ti, t in enumerate(tris):
        for e in itertools.combinations(sorted(t), 2):
            by_edge.setdefault(e, []).append(ti)
    g = nx.Graph()
    for e, ts in by_edge.items():
        assert len(ts) == 2
        g.add_edge(*ts)
    return g


def separating_triangles(k):
    """3-cycles of the k-frequency octahedron that are not faces; none means the dual cubic graph has no nontrivial 3-edge cut, so
    (being cubic and bipartite) it is a brace: its tight-cut decomposition is trivial"""
    faces = set()
    for sx, sy, sz in itertools.product((1, -1), repeat=3):
        P = lambda i, j, l: (sx * i, sy * j, sz * l)  # noqa: E731
        for i in range(k):
            for j in range(k - i):
                l = k - 1 - i - j
                faces.add(frozenset([P(i + 1, j, l), P(i, j + 1, l), P(i, j, l + 1)]))
        for i in range(k - 1):
            for j in range(k - 1 - i):
                l = k - 2 - i - j
                faces.add(frozenset([P(i + 1, j + 1, l), P(i + 1, j, l + 1), P(i, j + 1, l + 1)]))
    t = nx.Graph()
    for f in faces:
        t.add_edges_from(itertools.combinations(sorted(f), 2))
    tri = {frozenset((a, b, c)) for a in t for b in t[a] for c in t[b] if c in t[a] and len({a, b, c}) == 3}
    return len(tri - faces)


def signed_space(g):
    """(lines, signs, n) with Kasteleyn signs (planar_lib)"""
    return PL.to_space(g)


def unsigned_system(g):
    col = nx.bipartite.color(g)
    pts = sorted(v for v in g if col[v] == 0)
    lns = sorted(v for v in g if col[v] == 1)
    pid = {v: i for i, v in enumerate(pts)}
    return [tuple(sorted(pid[w] for w in g[L])) for L in lns]


def three_fold_space(g):
    """the unsigned three-fold space decorating the Kasteleyn-signed plane system of g (grammar_lib)"""
    H = unsigned_system(g)
    neg = GR.kasteleyn_signing(H)
    return GR.decorate(H, neg), len(neg)


# ------------------------------------------------------------------------------------------------ the count
def plane_faces(lines, n):
    g = nx.Graph()
    for i, L in enumerate(lines):
        for p in L:
            g.add_edge(("p", p), ("l", i))
    ok, emb = nx.check_planarity(g)
    assert ok
    seen, out = set(), []
    for v, w in emb.edges():
        if (v, w) not in seen:
            out.append(emb.traverse_face(v, w, mark_half_edges=seen))
    return out


def corners(lines, n):
    """[(line, a, b, face index)] and the faces' point sets"""
    fs = plane_faces(lines, n)
    out, fpts = [], []
    for fi, f in enumerate(fs):
        m = len(f)
        for t, v in enumerate(f):
            if v[0] == "l":
                out.append((v[1], f[(t - 1) % m][1], f[(t + 1) % m][1], fi))
        fpts.append(sorted({v[1] for v in f if v[0] == "p"}))
    return out, fpts


def agree(signs_of, l, a, b, x):
    return (x[a] ^ signs_of[(l, a)]) == (x[b] ^ signs_of[(l, b)])


def certificate(lines, signs, n):
    cs, fpts = corners(lines, n)
    sg = {(i, p): signs[i][j] for i, L in enumerate(lines) for j, p in enumerate(L)}
    by_face = {}
    for l, a, b, fi in cs:
        by_face.setdefault(fi, []).append((l, a, b))
    faces_always = 0
    for fi, U in enumerate(fpts):
        ok = True
        for vals in itertools.product((0, 1), repeat=len(U)):
            x = dict(zip(U, vals))
            if not any(agree(sg, l, a, b, x) for l, a, b in by_face[fi]):
                ok = False
                break
        faces_always += ok
    per_line = {}
    for l, a, b, fi in cs:
        per_line.setdefault(l, []).append(frozenset((a, b)))
    partition = len(per_line) == len(lines) and all(len(v) == 3 and len(set(v)) == 3 for v in per_line.values())
    # a satisfied line has exactly one agreeing corner, a violated one three
    line_ok = True
    for i, L in enumerate(lines):
        for v in itertools.product((0, 1), repeat=3):
            x = dict(zip(L, v))
            lit = [v[j] ^ signs[i][j] for j in range(3)]
            nag = sum(agree(sg, i, a, b, x) for a, b in itertools.combinations(L, 2))
            line_ok &= nag == (3 if lit[0] == lit[1] == lit[2] else 1)
    return {"points": n, "lines": len(lines), "faces": len(fpts), "faces minus lines": len(fpts) - len(lines),
            "faces with an agreeing corner under every assignment": faces_always, "corners partition by lines and faces": partition,
            "a line has one agreeing corner if satisfied, three if not": line_ok, "most points on a face": max(map(len, fpts))}


def tseitin_bijection(lines, signs, n):
    """assignments modulo complement versus odd-degree corner sets of the line-face graph: counts and an exhaustive check (small n)"""
    cs, fpts = corners(lines, n)
    sg = {(i, p): signs[i][j] for i, L in enumerate(lines) for j, p in enumerate(L)}
    E, V = len(cs), len(lines) + len(fpts)
    G = nx.Graph()
    for idx, (l, a, b, fi) in enumerate(cs):
        G.add_edge(("l", l), ("f", fi), key=idx)
    out = {"corner graph edges": E, "corner graph vertices": V, "connected": nx.is_connected(G),
           "dimension of odd-degree corner sets": E - V + 1, "dimension of assignments modulo complement": n - 1}
    if n <= 20:
        images = set()
        odd = True
        for vals in itertools.product((0, 1), repeat=n):
            if vals[0]:
                continue
            A = tuple(int(agree(sg, l, a, b, vals)) for l, a, b, fi in cs)
            deg = {}
            for (l, a, b, fi), z in zip(cs, A):
                deg[("l", l)] = deg.get(("l", l), 0) + z
                deg[("f", fi)] = deg.get(("f", fi), 0) + z
            odd &= all(d % 2 == 1 for d in deg.values())
            images.add(A)
        out["exhaustive: every image has odd degree everywhere"] = odd
        out["exhaustive: distinct images"] = len(images)
        out["exhaustive: odd-degree corner sets"] = 2 ** (E - V + 1)
    return out


def sa_restricted(lines, signs, n, use_faces=True):
    """status of the level-3 Sherali-Adams LP restricted to local distributions on the lines and (if use_faces) on the faces' point
    sets, with consistent pair marginals and the lines' constraints: 0 feasible, 2 infeasible"""
    from scipy.optimize import linprog
    sets = {tuple(sorted(L)) for L in lines}
    if use_faces:
        cs, fpts = corners(lines, n)
        sets |= {tuple(U) for U in fpts if len(U) >= 2}
    sets = sorted(sets)
    idx = {}
    for S in sets:
        for v in itertools.product((0, 1), repeat=len(S)):
            idx[(S, v)] = len(idx)
    nv = len(idx)
    rows, rhs = [], []
    for S in sets:
        r = np.zeros(nv)
        for v in itertools.product((0, 1), repeat=len(S)):
            r[idx[(S, v)]] = 1
        rows.append(r)
        rhs.append(1)
    pair_sets = {}
    for S in sets:
        for a, b in itertools.combinations(S, 2):
            pair_sets.setdefault((a, b), []).append(S)
    for (a, b), Ss in pair_sets.items():
        for S1, S2 in zip(Ss, Ss[1:]):
            for va, vb in itertools.product((0, 1), repeat=2):
                r = np.zeros(nv)
                for S, sgn in ((S1, 1), (S2, -1)):
                    ia, ib = S.index(a), S.index(b)
                    for v in itertools.product((0, 1), repeat=len(S)):
                        if v[ia] == va and v[ib] == vb:
                            r[idx[(S, v)]] += sgn
                rows.append(r)
                rhs.append(0)
    bounds = [(0, 1)] * nv
    for i, L in enumerate(lines):
        S = tuple(sorted(L))
        s = dict(zip(L, signs[i]))
        for v in itertools.product((0, 1), repeat=3):
            lit = [v[S.index(p)] ^ s[p] for p in S]
            if lit[0] == lit[1] == lit[2]:
                bounds[idx[(S, v)]] = (0, 0)
    res = linprog(np.zeros(nv), A_eq=np.array(rows), b_eq=np.array(rhs), bounds=bounds, method="highs")
    return int(res.status)


def nae_clauses(lines, signs=None):
    cls = []
    for i, L in enumerate(lines):
        s = signs[i] if signs is not None else (0, 0, 0)
        lit = [(p + 1) * (-1 if sg else 1) for p, sg in zip(L, s)]
        cls.append(lit)
        cls.append([-x for x in lit])
    return cls


def primal_width_bound(lines, n):
    """an upper bound on the treewidth of the primal graph (points sharing a line), by the min-fill-in heuristic"""
    from networkx.algorithms.approximation import treewidth_min_fill_in
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for L in lines:
        g.add_edges_from(itertools.combinations(L, 2))
    return treewidth_min_fill_in(g)[0]


# ------------------------------------------------------------------------------------------------ Davis-Putnam elimination
def dp_eliminate(clauses, order):
    """Davis-Putnam: eliminate the variables in order (all non-tautological resolvents, subsumed clauses dropped). Clauses are
    frozensets of nonzero ints (DIMACS literals). Returns the remaining clauses, the number of clauses produced (the size of the
    regular resolution derivation it describes) and the largest clause width that occurred"""
    S = {frozenset(c) for c in clauses}
    produced, wmax = 0, max((len(c) for c in S), default=0)
    for v in order:
        pos = [c for c in S if v in c]
        neg = [c for c in S if -v in c]
        rest = {c for c in S if v not in c and -v not in c}
        new = set()
        for a in pos:
            for b in neg:
                r = (a - {v}) | (b - {-v})
                if any(-l in r for l in r):
                    continue
                new.add(frozenset(r))
        produced += len(new)
        if new:
            wmax = max(wmax, max(len(c) for c in new))
        cand = rest | new
        # drop subsumed clauses
        by_len = sorted(cand, key=len)
        kept = []
        for c in by_len:
            if not any(k <= c for k in kept):
                kept.append(c)
        S = set(kept)
        if frozenset() in S:
            break
    return S, produced, wmax


def min_degree_order(clauses, variables):
    """a greedy elimination order on the primal graph (minimum degree, ties by index)"""
    g = nx.Graph()
    g.add_nodes_from(variables)
    for c in clauses:
        vs = sorted({abs(l) for l in c})
        g.add_edges_from(itertools.combinations(vs, 2))
    order = []
    while g.number_of_nodes():
        v = min(g.nodes, key=lambda u: (g.degree(u), u))
        nb = list(g.neighbors(v))
        g.add_edges_from(itertools.combinations(nb, 2))
        g.remove_node(v)
        order.append(v)
    return order
