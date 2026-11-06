"""Cubic triple systems, sign-nonsingular matrices, splices (THREEFOLD-SPACES-20261030-001A).

A cubic triple system H is a list of lines (triples of distinct points 0..n-1, lines may repeat) with every point on exactly three lines;
here the number of lines equals the number of points.  A colouring is proper when no line is monochromatic; a twist complements the colour
of one point inside one line.  The incidence matrix A has rows = lines, columns = points; a signing multiplies chosen entries by -1."""
import itertools, math
import numpy as np
import sympy as sp

FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def npoints(H):
    return 1 + max(p for l in H for p in l)


def is_cubic(H):
    n = npoints(H)
    deg = [0] * n
    for l in H:
        if len(set(l)) != 3:
            return False
        for p in l:
            deg[p] += 1
    return len(H) == n and all(d == 3 for d in deg)


def connected(H):
    n = npoints(H)
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b, c in H:
        par[f(b)] = f(a)
        par[f(c)] = f(a)
    return len({f(x) for x in range(n)}) == 1


def colourable(H, twist=None):
    """brute force (n <= 20): a proper 2-colouring, optionally with the incidence twist = (line index, point) complemented"""
    n = npoints(H)
    lines = [list(l) for l in H]
    masks = []
    for i, l in enumerate(lines):
        masks.append([(p, twist is not None and twist == (i, p)) for p in l])
    for c in range(1 << (n - 1)):
        col = [0] + [(c >> j) & 1 for j in range(n - 1)]
        ok = True
        for m in masks:
            vals = {col[p] ^ int(t) for p, t in m}
            if len(vals) == 1:
                ok = False
                break
        if ok:
            return True
    return False


def colourable_sat(H, twist=None):
    """the same by SAT (any size)"""
    from pysat.solvers import Solver
    with Solver(name='cadical153') as s:
        for i, l in enumerate(H):
            lits = [(p + 1) * (-1 if (twist == (i, p)) else 1) for p in l]
            s.add_clause(lits)
            s.add_clause([-x for x in lits])
        return s.solve()


def matrix(H, signs=()):
    """integer incidence matrix; signs = incidences (line index, point) to negate"""
    n = npoints(H)
    A = np.zeros((len(H), n), dtype=object)
    for i, l in enumerate(H):
        for p in l:
            A[i, p] += 1
    for i, p in signs:
        A[i, p] = -A[i, p]
    return A


def det(A):
    return int(sp.Matrix(A.tolist()).det(method='bareiss'))


def permanent(A):
    """Ryser with Gray code (exact integers); n <= ~22"""
    A = [[int(x) for x in row] for row in A]
    n = len(A)
    rowsum = [0] * n
    total = 0
    sign = -1
    prev = 0
    for k in range(1, 1 << n):
        gray = k ^ (k >> 1)
        diff = gray ^ prev
        j = diff.bit_length() - 1
        add = 1 if gray & diff else -1
        for i in range(n):
            rowsum[i] += add * A[i][j]
        prev = gray
        prod = 1
        for r in rowsum:
            prod *= r
            if prod == 0:
                break
        total += (-1) ** bin(gray).count('1') * prod
    return (-1) ** n * total


def sns(H, signs=()):
    """sign-nonsingular: |det| = per > 0 of the (signed) incidence matrix (per of the absolute values)"""
    A = matrix(H, signs)
    d = det(A)
    P = permanent(np.abs(A))
    return P > 0 and abs(d) == P, d, P


def perfect_matchings(H):
    """all bijections lines -> points with each line matched to one of its points"""
    n = npoints(H)
    out = []

    def rec(i, used, cur):
        if i == len(H):
            out.append(tuple(cur))
            return
        for p in sorted(set(H[i])):
            if p not in used:
                used.add(p)
                cur.append(p)
                rec(i + 1, used, cur)
                cur.pop()
                used.discard(p)
    rec(0, set(), [])
    return out


def perm_sign(pi):
    n = len(pi)
    seen = [False] * n
    s = 1
    for i in range(n):
        if not seen[i]:
            j, L = i, 0
            while not seen[j]:
                seen[j] = True
                j = pi[j]
                L += 1
            if L % 2 == 0:
                s = -s
    return s


def digraph(H, M):
    """D(H, M): vertices = points; point M[l] -> every other point of line l (M a perfect matching line -> point)"""
    n = npoints(H)
    out = {p: [] for p in range(n)}
    for l, line in enumerate(H):
        p = M[l]
        for q in line:
            if q != p:
                out[p].append(q)
    return out


def has_even_dicycle(D):
    """search for a directed cycle of even length (small digraphs)"""
    n = len(D)
    # parity-reachability: an even cycle through v exists iff some simple even cycle exists; do an explicit DFS over simple paths
    for s in range(n):
        stack = [(s, [s], {s})]
        while stack:
            u, path, seen = stack.pop()
            for w in D[u]:
                if w == s and len(path) % 2 == 0:
                    return True
                if w > s and w not in seen:
                    stack.append((w, path + [w], seen | {w}))
    return False


def point_splice(H1, t, H2, M):
    """replace point t of H1 by H2 minus its line M; the three lines through t receive the three points of M"""
    through = [l for l in H1 if t in l]
    off = npoints(H1)
    H2s = [tuple(p + off for p in l) for l in H2]
    Ms = tuple(p + off for p in M)
    out = [l for l in H1 if t not in l]
    out += [tuple(sorted((Ms[i],) + tuple(p for p in through[i] if p != t))) for i in range(3)]
    removed = False
    for l in H2s:
        if l == Ms and not removed:
            removed = True
            continue
        out.append(l)
    return relabel(out)


def line_splice(H1, L, H2, m):
    """replace line L = (a, b, c) of H1 by H2 minus its point m; the three pairs left by m are completed by a, b, c"""
    off = npoints(H1)
    H2s = [tuple(p + off for p in l) for l in H2]
    ms = m + off
    pairs = [tuple(p for p in l if p != ms) for l in H2s if ms in l]
    out = []
    removed = False
    for l in H1:
        if tuple(l) == tuple(L) and not removed:
            removed = True
            continue
        out.append(l)
    out += [tuple(sorted(pairs[i] + (L[i],))) for i in range(3)]
    out += [l for l in H2s if ms not in l]
    return relabel(out)


def relabel(H):
    pts = sorted({p for l in H for p in l})
    re = {p: i for i, p in enumerate(pts)}
    return [tuple(sorted(re[p] for p in l)) for l in H]


def tight_cuts(H, max_shore=None):
    """nontrivial point-type 3-edge tight cuts: sets X of lines and P of points with |P| = |X| + 1 >= 2, every line of X inside P, and
    exactly three incidences between P and lines outside X; returned as (lines X, points P) (small n: exhaustive over line sets)"""
    n = npoints(H)
    out = []
    idx = range(len(H))
    sizes = range(1, (max_shore or len(H)) )
    for k in sizes:
        for X in itertools.combinations(idx, k):
            P = sorted({p for i in X for p in H[i]})
            if len(P) != k + 1:
                continue
            cut = sum(1 for i in idx if i not in X for p in H[i] if p in P)
            if cut == 3 and len(P) < n:
                out.append((X, tuple(P)))
    return out


def gadget_from(H, L0, order=(0, 1, 2)):
    """the three-fold gadget dual to (H, L0): triangles = points of H, contacts = lines other than L0, corner triangles = the points of L0
    (A, B, C at L0[order[0]], L0[order[1]], L0[order[2]]), one base incidence per contact (a perfect matching contacts -> triangles other
    than T_A).  Returns a complex (vertex count, triangles in role order (a, b, c), corners (0, 1, 2)) for SPACE-SELECTION's gadget_lib."""
    import networkx as nx
    n = npoints(H)
    i0 = H.index(tuple(L0)) if tuple(L0) in H else [tuple(l) for l in H].index(tuple(L0))
    contacts = [i for i in range(len(H)) if i != i0]
    tA, tB, tC = (L0[order[0]], L0[order[1]], L0[order[2]])
    g = nx.Graph()
    for i in contacts:
        for p in H[i]:
            if p != tA:
                g.add_edge(('c', i), ('t', p))
    match = nx.bipartite.maximum_matching(g, top_nodes=[('c', i) for i in contacts])
    base_of = {match[('c', i)][1]: i for i in contacts}          # triangle -> contact holding its base slot
    assert len(base_of) == n - 1
    vid = {i: 3 + k for k, i in enumerate(contacts)}
    tris = []
    for p in range(n):
        lines = [i for i in contacts if p in H[i]]
        slot = [None, None, None]
        if p == tA:
            slot[0] = 0
        else:
            slot[0] = vid[base_of[p]]
            lines.remove(base_of[p])
        if p == tB:
            slot[1] = 1
        if p == tC:
            slot[2] = 2
        for i in lines:
            j = slot.index(None)
            slot[j] = vid[i]
        tris.append(tuple(slot))
    # put T_A first
    tris = [tris[tA]] + [t for q, t in enumerate(tris) if q != tA]
    return (3 + len(contacts), tuple(tris), (0, 1, 2))
