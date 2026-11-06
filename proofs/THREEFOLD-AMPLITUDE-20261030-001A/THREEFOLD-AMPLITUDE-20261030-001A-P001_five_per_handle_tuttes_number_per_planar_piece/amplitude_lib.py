"""The knot's amplitude on three-fold spaces (THREEFOLD-AMPLITUDE-20261030-001A).

A system is a list of lines (triples of points, repetition allowed).  A signing `neg` is a set of incidences (line index, point) whose colour
is complemented on that line.  A colouring is proper on a line when the line's seen values (colour xor sign) are not all equal.  The
amplitude A(H, L) is half the number of colourings proper on every line except L; when H is not 2-colourable every such colouring makes L
constant as seen, so A(H, L) counts them with L's seen value fixed.  Counting is exact, by variable elimination."""
import itertools
import numpy as np
import networkx as nx


# ------------------------------------------------------------------------------------------------ exact counting
def _eliminate(factors):
    g = nx.Graph()
    for vs, t in factors:
        g.add_nodes_from(vs)
        for a in vs:
            for b in vs:
                if a != b:
                    g.add_edge(a, b)
    scalar = 1
    while g.number_of_nodes():
        v = min(g.nodes(), key=lambda u: (g.degree(u), str(u)))
        nb = list(g[v])
        for a in nb:
            for b in nb:
                if a != b:
                    g.add_edge(a, b)
        g.remove_node(v)
        inv = [f for f in factors if v in f[0]]
        rest = [f for f in factors if v not in f[0]]
        if not inv:
            scalar *= 2
            factors = rest
            continue
        allv = sorted({u for vs, t in inv for u in vs}, key=str)
        prod = np.ones((2,) * len(allv), dtype=object)
        for vs, t in inv:
            shape = [2 if u in vs else 1 for u in allv]
            tt = np.transpose(t, [vs.index(u) for u in allv if u in vs]).reshape(shape)
            prod = prod * tt
        summed = prod.sum(axis=allv.index(v))
        newv = [u for u in allv if u != v]
        factors = rest + ([(newv, summed)] if newv else [])
        if not newv:
            scalar *= summed.item() if hasattr(summed, 'item') else summed
    for vs, t in factors:
        scalar *= t.item() if hasattr(t, 'item') else t
    return int(scalar)


def count(H, neg=(), drop=None, fix=None, seen=None):
    """number of colourings proper (as seen) on every line except `drop`; fix: point -> colour; seen: dict line index -> {position in the
    line: value} replacing the value the line sees at that incidence (used for the point lemma; a line may contain a point twice)"""
    neg = set(neg)
    pts = sorted({p for l in H for p in l}, key=str)
    real, const = [], 1
    for i, l in enumerate(H):
        if i == drop:
            continue
        over = (seen or {}).get(i, {})
        vs = sorted({p for k, p in enumerate(l) if k not in over}, key=str)
        t = np.zeros((2,) * len(vs), dtype=object)
        for idx in np.ndindex(*(2,) * len(vs)):
            val = dict(zip(vs, idx))
            vals = [over[k] if k in over else val[p] ^ (1 if (i, p) in neg else 0) for k, p in enumerate(l)]
            t[idx] = 0 if len(set(vals)) == 1 else 1
        if vs:
            real.append((vs, t))
        else:
            const *= int(t)
    for p in pts:
        if fix and p in fix:
            real.append(([p], np.array([1 - fix[p], fix[p]], dtype=object)))
    used = {p for vs, t in real for p in vs}
    free = [p for p in pts if p not in used]
    return const * _eliminate(real) * 2 ** len(free)


def amplitude(H, L, neg=()):
    return count(H, neg, drop=L) // 2


def colourable(H, neg=()):
    return count(H, neg) > 0


# ------------------------------------------------------------------------------------------------ the point lemma
def point_counts(H, p, neg=()):
    """for a point p with three incidences (line index, position; a line may hold p twice): the incidences, and for each pattern y of values
    seen at them the number of colourings of the other points proper on every line (as a dict pattern -> count)"""
    inc = [(i, k) for i, l in enumerate(H) for k, q in enumerate(l) if q == p]
    assert len(inc) == 3
    out = {}
    for y in itertools.product((0, 1), repeat=3):
        seen = {}
        for (i, k), v in zip(inc, y):
            seen.setdefault(i, {})[k] = v
        out[y] = count(H, neg, seen=seen) // 2           # p itself no longer constrains anything: it is free (factor 2)
    return inc, out


# ------------------------------------------------------------------------------------------------ the law's corner relation
def knot_table():
    K = np.zeros((2, 2, 2), dtype=object)
    for a, b, c in itertools.product((0, 1), repeat=3):
        K[a, b, c] = (-1) ** a * (0, 1, -1, 0)[a + b + c]
    return K


def corner_relation(cx, W):
    """R(x_A, x_B, x_C) = sum over inner bits of the product of W over triangles (gadget format of SPACE-SELECTION's gadget_lib)"""
    nv, tris, corners = cx
    W = np.asarray(W, dtype=object)
    out = {}
    for c in itertools.product((0, 1), repeat=3):
        fixed = dict(zip(corners, c))
        factors = []
        const = 1
        for t in tris:
            vs = sorted(set(v for v in t if v not in fixed))
            tab = np.zeros((2,) * len(vs), dtype=object)
            for idx in np.ndindex(*(2,) * len(vs)):
                val = dict(fixed)
                val.update(zip(vs, idx))
                tab[idx] = W[val[t[0]], val[t[1]], val[t[2]]]
            if vs:
                factors.append((vs, tab))
            else:
                const *= tab.item() if hasattr(tab, 'item') else tab
        out[c] = const * _eliminate(factors)
    return out


def lambda0(cx):
    """the exactness factor of the knot on a gadget: (exact?, set of ratios R/K over corner patterns where K != 0)"""
    K = knot_table()
    R = corner_relation(cx, K)
    exact = all(R[c] == 0 for c in R if K[c] == 0)
    ratios = {R[c] // K[c] if R[c] % K[c] == 0 else R[c] / K[c] for c in R if K[c] != 0}
    return exact, ratios


# ------------------------------------------------------------------------------------------------ planar glue: faces, Tutte matchings, arborescences
def bipartite(H):
    g = nx.Graph()
    for i, l in enumerate(H):
        for p in l:
            g.add_edge(('L', i), ('P', p))
    return g


def faces(H):
    ok, emb = nx.check_planarity(bipartite(H))
    assert ok
    seen, out = set(), []
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        out.append(emb.traverse_face(u, v, mark_half_edges=seen))
    return out


def tutte_matchings(H, L):
    """perfect matchings between the lines other than L and the faces not incident to line-vertex L, each line matched to a face around it
    (a permanent, by Ryser's formula)"""
    fs = [set(f) for f in faces(H)]
    rows = [i for i in range(len(H)) if i != L]
    cols = [k for k, f in enumerate(fs) if ('L', L) not in f]
    assert len(rows) == len(cols)
    A = [[1 if ('L', i) in fs[k] else 0 for k in cols] for i in rows]
    n = len(A)
    total = 0
    for S in range(1, 1 << n):
        prod = 1
        for r in range(n):
            s = sum(A[r][c] for c in range(n) if S >> c & 1)
            if s == 0:
                prod = 0
                break
            prod *= s
        total += (-1) ** bin(S).count('1') * prod
    return (-1) ** n * total


def face_colours(H):
    """the proper 3-colouring of the faces of a planar cubic bipartite graph: the three faces at a vertex get three colours; it is unique up
    to permuting colours and is found by propagation from one vertex"""
    fs = faces(H)
    at = {}
    for k, f in enumerate(fs):
        for v in f:
            at.setdefault(v, []).append(k)
    v0 = next(iter(at))
    col = {k: c for c, k in enumerate(at[v0])}
    changed = True
    while changed:
        changed = False
        for v, ks in at.items():
            known = [k for k in ks if k in col]
            if len(known) == 2 and len(ks) == 3:
                (u,) = [k for k in ks if k not in col]
                col[u] = ({0, 1, 2} - {col[k] for k in known}).pop()
                changed = True
    assert len(col) == len(fs)
    assert all(len({col[k] for k in ks}) == 3 for ks in at.values())
    return fs, col


def arborescence_number(H, colour=2):
    """Tutte's tree-trinity number: spanning arborescences of the digraph on the faces of one colour class, with an arc for every edge of
    the other two classes' boundary type, from the colour-class face at its point end to the one at its line end (directed matrix-tree
    theorem; the digraph is balanced, so the root does not matter)"""
    import sympy
    fs, col = face_colours(H)
    cls = [k for k in range(len(fs)) if col[k] == colour]
    idx = {k: i for i, k in enumerate(cls)}
    at = {}
    for k in cls:
        for v in fs[k]:
            at[v] = k
    n = len(cls)
    Lm = [[0] * n for _ in range(n)]
    g = bipartite(H)
    for u, v in g.edges():
        pnt, lin = (u, v) if u[0] == 'P' else (v, u)
        # the edge lies between two faces of the other colours iff neither of its two faces has `colour`
        a, b = at[pnt], at[lin]
        if a == b:
            continue
        # arc a -> b counts toward b's in-degree
        Lm[idx[b]][idx[b]] += 1
        Lm[idx[a]][idx[b]] -= 1
    M = sympy.Matrix(Lm)
    return int(M[1:, 1:].det())
