"""Kasteleyn faces and spin structures on minimal maps of three-fold spaces (THREEFOLD-SPIN-20261030-001A).

The incidence graph B(H) has a vertex ('P', p) per point, ('L', i) per line, and one edge per incidence (a line holding a point twice gives
two parallel edges).  Maps are rotation systems of surface_lib (THREEFOLD-SURFACES-20261030-001A).  A signing is a set of negated edge
indices; it is turned into an orientation (point -> line, reversed on negated edges).  For a bipartite face of length 2l the Kasteleyn
condition is: the number of negated edges on it is l - 1 mod 2.  Given a Kasteleyn orientation K and a perfect matching D, Cimasoni and
Reshetikhin (Comm. Math. Phys. 2007, Theorem 4.1) define a quadratic form on H_1(surface; Z_2) by q([C]) = n_K(C) + l_D(C) + 1 mod 2 for a
simple cycle C, where n_K counts the edges of C oriented against a traversal and l_D the vertices of C whose matching edge leaves C on one
fixed side; q is additive over disjoint cycles.  Homology classes are read off by pairing with 2g cocycles (GF(2) linear algebra on bit
masks)."""
import itertools
import networkx as nx
import surface_lib as SL


# ------------------------------------------------------------------------------------------------ graphs, faces, signings
def graph_of(H):
    return [(('L', i), ('P', p)) for i, l in enumerate(H) for p in l]


def negated(edges, neg):
    """edge indices of the negated incidences (line, point) in neg (every occurrence)"""
    s = set(neg)
    return frozenset(k for k, (l, p) in enumerate(edges) if (l[1], p[1]) in s)


def face_condition(edges, rot, neg=frozenset()):
    """per face: (length, Kasteleyn condition holds)"""
    out = []
    for f in SL.faces(edges, rot):
        l = len(f) // 2
        s = sum(1 for e, t in f if e in neg)
        out.append((len(f), (s - (l - 1)) % 2 == 0))
    return out


def three_distinct_faces(edges, rot):
    """every vertex has its three corners on three distinct faces"""
    at = {}
    for k, f in enumerate(SL.faces(edges, rot)):
        for e, t in f:
            at.setdefault(SL.head(edges, e, t), []).append(k)
    return all(len(ks) == len(set(ks)) for ks in at.values())


# ------------------------------------------------------------------------------------------------ GF(2) on bit masks
def add_to_basis(v, basis):
    for b in basis:
        if v ^ b < v:
            v ^= b
    if v:
        basis.append(v)
        basis.sort(reverse=True)
        return True
    return False


def nullspace(rows, ncols):
    """basis of {c : popcount(row & c) even for every row}"""
    piv = {}
    for r in rows:
        for col, pr in piv.items():
            if r >> col & 1:
                r ^= pr
        if r:
            col = r.bit_length() - 1
            for c2 in list(piv):
                if piv[c2] >> col & 1:
                    piv[c2] ^= r
            piv[col] = r
    out = []
    for f in (c for c in range(ncols) if c not in piv):
        v = 1 << f
        for col, pr in piv.items():
            if pr >> f & 1:
                v |= 1 << col
        out.append(v)
    return out


def h1_basis(edges, rot):
    """2g cocycles independent modulo coboundaries: pairing with them reads the class of a cycle in H_1(surface; Z_2)"""
    fmasks = []
    for f in SL.faces(edges, rot):
        m = 0
        for e, t in f:
            m ^= 1 << e
        fmasks.append(m)
    span = []
    for v, es in SL.incident(edges).items():
        m = 0
        for e in es:
            m ^= 1 << e
        add_to_basis(m, span)
    return [c for c in nullspace(fmasks, len(edges)) if add_to_basis(c, span)]


def hclass(Z, H1):
    return tuple(bin(Z & c).count('1') & 1 for c in H1)


def fundamental_cycles(edges):
    G = nx.MultiGraph()
    for i, (u, v) in enumerate(edges):
        G.add_edge(u, v, key=i)
    T = nx.minimum_spanning_tree(G)
    tree = {k for u, v, k in T.edges(keys=True)}
    out = []
    for i, (u, v) in enumerate(edges):
        if i in tree:
            continue
        path = nx.shortest_path(T, u, v)
        m = 1 << i
        for a, b in zip(path, path[1:]):
            m ^= 1 << next(iter(T[a][b]))
        out.append(m)
    return out


def class_representatives(edges, H1, fund=None):
    """one cycle-space element (bit mask) for every class of H_1"""
    reps = {(0,) * len(H1): 0}
    for m in fund or fundamental_cycles(edges):
        c = hclass(m, H1)
        new = {}
        for h, Z in reps.items():
            h2 = tuple(x ^ y for x, y in zip(h, c))
            if h2 not in reps and h2 not in new:
                new[h2] = Z ^ m
        reps.update(new)
    return reps


# ------------------------------------------------------------------------------------------------ matchings, cycles, the quadratic form
def perfect_matchings(edges):
    inc = SL.incident(edges)
    lines = sorted([v for v in inc if v[0] == 'L'], key=str)
    out = []

    def rec(k, used, chosen):
        if k == len(lines):
            out.append(chosen)
            return
        for e in inc[lines[k]]:
            p = SL.head(edges, e, lines[k])
            if p not in used:
                rec(k + 1, used | {p}, chosen | (1 << e))
    rec(0, frozenset(), 0)
    return out


def cycles_of(Z, edges):
    """the simple cycles of an even edge set of a cubic graph (every vertex of degree 0 or 2): lists of (vertex, edge leaving it)"""
    es = [e for e in range(len(edges)) if Z >> e & 1]
    at = {}
    for e in es:
        for v in edges[e]:
            at.setdefault(v, []).append(e)
    assert all(len(x) == 2 for x in at.values()), "not a disjoint union of cycles"
    seen, out = set(), []
    for e0 in es:
        if e0 in seen:
            continue
        cyc, v, e = [], edges[e0][0], e0
        while e not in seen:
            seen.add(e)
            cyc.append((v, e))
            w = SL.head(edges, e, v)
            a, b = at[w]
            e, v = (b if a == e else a), w
        out.append(cyc)
    return out


def q_cycle(cyc, edges, rot, neg, D, inc=None):
    """q([C]) = n_K(C) + l_D(C) + 1 mod 2 (Cimasoni-Reshetikhin) for one simple cycle"""
    inc = inc or SL.incident(edges)
    n = side = 0
    for j, (v, e) in enumerate(cyc):
        w = SL.head(edges, e, v)
        pt, ln = (v, w) if v[0] == 'P' else (w, v)
        if (pt if e not in neg else ln) != v:
            n += 1
        e_in = cyc[j - 1][1]
        third = [x for x in inc[v] if x != e_in and x != e]
        if len(third) == 1 and D >> third[0] & 1 and rot[v][e_in] == third[0]:
            side += 1
    return (n + side + 1) % 2


def q_of(Z, edges, rot, neg, D, inc=None):
    inc = inc or SL.incident(edges)
    return sum(q_cycle(c, edges, rot, neg, D, inc) for c in cycles_of(Z, edges)) % 2 if Z else 0


def gauss_arf(qvalues, g):
    """Arf invariant from the Gauss sum sum (-1)^q over H_1, which is +2^g (Arf 0) or -2^g (Arf 1) for a quadratic form"""
    s = sum((-1) ** v for v in qvalues)
    return 0 if s == 2 ** g else 1 if s == -(2 ** g) else ('not a quadratic form', s)


def form(edges, rot, neg, D, H1=None, reps=None):
    """the values of q_D on all classes, from one representative each"""
    H1 = H1 if H1 is not None else h1_basis(edges, rot)
    reps = reps if reps is not None else class_representatives(edges, H1)
    inc = SL.incident(edges)
    return {h: q_of(Z, edges, rot, neg, D, inc) for h, Z in reps.items()}


# ------------------------------------------------------------------------------------------------ tight cuts and crossing faces
def tight_cuts(edges):
    """the nontrivial tight 3-edge cuts of a cubic bipartite graph, as frozensets of edge indices"""
    V = SL.vertices(edges)
    out = []
    for cut in itertools.combinations(range(len(edges)), 3):
        G = nx.MultiGraph()
        G.add_nodes_from(V)
        G.add_edges_from(edges[i] for i in range(len(edges)) if i not in cut)
        comps = list(nx.connected_components(G))
        if len(comps) != 2 or min(len(c) for c in comps) < 3:
            continue
        Y = comps[0]
        if abs(sum(1 for v in Y if v[0] == 'P') - sum(1 for v in Y if v[0] == 'L')) == 1:
            out.append(frozenset(cut))
    return out


def crossing_faces(edges, rot, cut):
    """for each face using a cut edge: the number of its darts on cut edges"""
    return [sum(1 for e, t in f if e in cut) for f in SL.faces(edges, rot) if any(e in cut for e, t in f)]
