"""Trisums of non-colourable cubic pieces along a square (SEYMOUR-COUNT-20261030-001A).

Graphs are networkx graphs on points and lines (bipartite, cubic).  A square is a list (c0, c1, c2, c3) of four vertices: c0, c2 points,
c1, c3 lines.  A piece contains its square's four edges; a trisum glues three pieces along the same labelled square and deletes those
edges.  Pfaffian signings are found from a minimal map: a solution of Kasteleyn's face conditions over GF(2), twisted by the cohomology
class that makes the system non-colourable (a non-colourable cubic system is exactly a Pfaffian one, THREEFOLD-AMPLITUDE-20261030-001C)."""
import itertools
import networkx as nx
from pysat.solvers import Solver
import surface_lib as SL
import amplitude_lib as AM
import spin_lib as S

C4 = [('c', j) for j in range(4)]
D4 = [('d', j) for j in range(4)]


def as_system(g, anchor=None):
    """(system, point index, line index, lines in order): points are the colour class of `anchor` (a point), default C4[0]"""
    anchor = anchor or C4[0]
    col = nx.bipartite.color(g)
    if anchor in col and col[anchor] != 0:
        col = {v: 1 - c for v, c in col.items()}
    pts = sorted((v for v in g if col[v] == 0), key=str)
    lns = sorted((v for v in g if col[v] == 1), key=str)
    pid = {v: k for k, v in enumerate(pts)}
    lid = {v: k for k, v in enumerate(lns)}
    return [tuple(sorted(pid[w] for w in g[v])) for v in lns], pid, lid, lns


def one_minimal_map(edges):
    g = SL.genus(edges)
    V, E = len(SL.vertices(edges)), len(edges)
    cnf, r = SL._model(edges, E - V + 2 - 2 * g, fix_first=False)
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as s:
        assert s.solve()
        m = set(l for l in s.get_model() if l > 0)
        return g, SL.rotation(edges, {v: int(r(v) in m) for v in SL.vertices(edges)})


def pfaffian_signing(H):
    """negated incidences (line, point) of a Pfaffian signing of the cubic system H, and the genus of the map used"""
    E = S.graph_of(H)
    g, rot = one_minimal_map(E)
    piv = {}
    for f in SL.faces(E, rot):
        m = 0
        for e, t in f:
            m ^= 1 << e
        b = (len(f) // 2 - 1) % 2
        for col, (pm, pb) in piv.items():
            if m >> col & 1:
                m, b = m ^ pm, b ^ pb
        if m:
            col = m.bit_length() - 1
            for c2 in list(piv):
                pm, pb = piv[c2]
                if pm >> col & 1:
                    piv[c2] = (pm ^ m, pb ^ b)
            piv[col] = (m, b)
        else:
            assert b == 0
    sol = sum(1 << col for col, (m, b) in piv.items() if b)
    H1 = S.h1_basis(E, rot)
    for beta in itertools.product((0, 1), repeat=len(H1)):
        c = sol
        for bb, cc in zip(beta, H1):
            if bb:
                c ^= cc
        neg = [(E[k][0][1], E[k][1][1]) for k in range(len(E)) if c >> k & 1]
        if not AM.colourable(H, neg):
            return neg, g
    raise ValueError("no non-colourable Kasteleyn twist")


def leaning(g, sq=C4, side='c1'):
    """the leaning split at the square sq: side 'c1' removes c1 and reads the third point of c3 (agreeing with c0: alpha, with c2: beta);
    side 'c3' removes c3 and reads the third point of c1"""
    H, pid, lid, lns = as_system(g, sq[0])
    neg, _ = pfaffian_signing(H)
    negs = set(neg)
    c0, c1, c2, c3 = sq
    drop, read = (c1, c3) if side == 'c1' else (c3, c1)
    u = [w for w in g[read] if w not in (c0, c2)][0]
    s = lambda ln, p: 1 if (lid[ln], pid[p]) in negs else 0
    al = be = 0
    for x0, x2 in itertools.product((0, 1), repeat=2):
        if (x0 ^ s(read, c0)) == (x2 ^ s(read, c2)):
            continue
        al += AM.count(H, neg, drop=lid[drop], fix={pid[c0]: x0, pid[c2]: x2, pid[u]: x0 ^ s(read, c0) ^ s(read, u)})
        be += AM.count(H, neg, drop=lid[drop], fix={pid[c0]: x0, pid[c2]: x2, pid[u]: x2 ^ s(read, c2) ^ s(read, u)})
    assert al + be == AM.count(H, neg, drop=lid[drop])
    return al // 2, be // 2


# ------------------------------------------------------------------------------------------------ pieces and trisums
def prism_piece(k, flip=False, sq=C4, tag='p'):
    """the 2k-prism with its square u0 u1 v1 v0 labelled sq (flip exchanges c0 and c2)"""
    m = 2 * k
    g = nx.Graph()
    for i in range(m):
        g.add_edges_from([(('u', i), ('u', (i + 1) % m)), (('v', i), ('v', (i + 1) % m)), (('u', i), ('v', i))])
    face = [('u', 0), ('u', 1), ('v', 1), ('v', 0)]
    target = sq if not flip else [sq[2], sq[1], sq[0], sq[3]]
    mp = dict(zip(face, target))
    return nx.relabel_nodes(g, lambda v: mp.get(v, (tag, v)))


def two_square_prism(k, flipC=False, flipD=False, tag='h'):
    """the 2k-prism with two disjoint squares labelled C4 and D4, each starting at a point"""
    m = 2 * k
    g = nx.Graph()
    for i in range(m):
        g.add_edges_from([(('u', i), ('u', (i + 1) % m)), (('v', i), ('v', (i + 1) % m)), (('u', i), ('v', i))])
    j = 2 if k == 2 else (k if k % 2 == 0 else k + 1)
    faceC = [('u', 0), ('u', 1), ('v', 1), ('v', 0)]
    faceD = [('u', j), ('u', j + 1), ('v', j + 1), ('v', j)]
    mp = dict(zip(faceC, C4 if not flipC else [C4[2], C4[1], C4[0], C4[3]]))
    mp.update(dict(zip(faceD, D4 if not flipD else [D4[2], D4[1], D4[0], D4[3]])))
    return nx.relabel_nodes(g, lambda v: mp.get(v, (tag, v)))


def truncated_octahedron_piece(flip=False):
    import computation_lib as CL
    G = CL.omnitruncation(nx.complete_graph(4))
    col = nx.bipartite.color(G)
    for a in sorted(G, key=str):
        if col[a]:
            continue
        for b, d in itertools.combinations(sorted(G[a], key=str), 2):
            for c in sorted(set(G[b]) & set(G[d]), key=str):
                if c != a and not G.has_edge(a, c):
                    face = [a, b, c, d] if not flip else [c, b, a, d]
                    mp = dict(zip(face, C4))
                    return nx.relabel_nodes(G, lambda v: mp.get(v, ('t', v)))


def trisum_of(pieces, sq=C4):
    G = nx.Graph()
    for t, g in enumerate(pieces):
        G.add_edges_from(nx.relabel_nodes(g, lambda v: v if (v in C4 or v in D4) else ('xyz'[t], v)).edges())
    G.remove_edges_from([(sq[j], sq[(j + 1) % 4]) for j in range(4)])
    assert all(d == 3 for _, d in G.degree())
    return G


def amplitude(G, anchor=None):
    H, pid, lid, lns = as_system(G, anchor)
    neg, g = pfaffian_signing(H)
    vals = {AM.amplitude(H, L, neg) for L in (0, len(H) // 2, len(H) - 1)}
    assert len(vals) == 1
    return vals.pop()


def law(splits):
    (a1, b1), (a2, b2), (a3, b3) = splits
    return (a1 + b1) * (a2 + b2) * (a3 + b3) - a1 * a2 * a3 - b1 * b2 * b3


# ------------------------------------------------------------------------------------------------ boundary tensors and the weights lemma
def boundary_tensors(G, sq=C4):
    """inside the trisum G with its own Pfaffian signing: for each piece tag, the counts of its own points' colourings making its own
    lines proper, by (colour of c0, colour of c2, value seen by c1 at the piece's incidence, value seen by c3 at it)"""
    H, pid, lid, lns = as_system(G, sq[0])
    negs = set(pfaffian_signing(H)[0])
    c0, c1, c2, c3 = sq
    tag = lambda v: 'C' if (v in sq) else v[0]
    out = {}
    for t in sorted({tag(v) for v in G if tag(v) != 'C'}):
        pts = [v for v in pid if tag(v) == t]
        lines = [v for v in lid if tag(v) == t]
        u1 = [w for w in G[c1] if tag(w) == t][0]
        u3 = [w for w in G[c3] if tag(w) == t][0]
        sg = lambda ln, p: 1 if (lid[ln], pid[p]) in negs else 0
        tab = {}
        for x0, x2 in itertools.product((0, 1), repeat=2):
            for bits in itertools.product((0, 1), repeat=len(pts)):
                col = dict(zip(pts, bits))
                col[c0], col[c2] = x0, x2
                if all(len({col[p] ^ sg(ln, p) for p in G[ln]}) == 2 for ln in lines):
                    key = (x0, x2, col[u1] ^ sg(c1, u1), col[u3] ^ sg(c3, u3))
                    tab[key] = tab.get(key, 0) + 1
        out[t] = tab
    return out


def weighted_host_count(host, sq_parent, sq_child, child_splits, lean_parent):
    """the weights lemma, by exact colouring counts: sum over colourings of host - c1 (parent square) with the given leaning at the parent
    square of the child weight of the host's state at the child square (both of its lines proper), halved"""
    H, pid, lid, lns = as_system(host, sq_parent[0])
    neg, _ = pfaffian_signing(H)
    negs = set(neg)
    s = lambda ln, p: 1 if (lid[ln], pid[p]) in negs else 0
    (aQ, bQ), (aR, bR) = child_splits
    rQR = (aQ + bQ) * (aR + bR)
    wA, wB = rQR - aQ * aR, rQR - bQ * bR
    p0, p1, p2, p3 = sq_parent
    d0, d1, d2, d3 = sq_child
    up = [w for w in host[p3] if w not in (p0, p2)][0]
    u1 = [w for w in host[d1] if w not in (d0, d2)][0]
    u3 = [w for w in host[d3] if w not in (d0, d2)][0]
    total = 0
    for x0, x2 in itertools.product((0, 1), repeat=2):          # parent square: c3 must see c0 and c2 differently
        if (x0 ^ s(p3, p0)) == (x2 ^ s(p3, p2)):
            continue
        xu = (x0 ^ s(p3, p0) ^ s(p3, up)) if lean_parent == 'alpha' else (x2 ^ s(p3, p2) ^ s(p3, up))
        for y0, y2 in itertools.product((0, 1), repeat=2):
            for which in (d1, d3):                                  # the child-square line that sees d0, d2 equal
                other = d3 if which == d1 else d1
                if (y0 ^ s(which, d0)) != (y2 ^ s(which, d2)):
                    continue
                uw = u1 if which == d1 else u3
                uo = u3 if which == d1 else u1
                xw = 1 ^ y0 ^ s(which, d0) ^ s(which, uw)          # the line that sees d0 = d2 is proper: its third point differs
                for lean_child in ('alpha', 'beta'):
                    xo = (y0 ^ s(other, d0) ^ s(other, uo)) if lean_child == 'alpha' else (y2 ^ s(other, d2) ^ s(other, uo))
                    fix, clash = {}, False
                    for v, val in ((p0, x0), (p2, x2), (up, xu), (d0, y0), (d2, y2), (uw, xw), (uo, xo)):
                        if pid[v] in fix and fix[pid[v]] != val:
                            clash = True
                        fix[pid[v]] = val
                    if clash:
                        continue
                    n = AM.count(H, neg, drop=lid[p1], fix=fix)
                    if which == d1:                                  # c1-case: weights read on c3's leaning
                        total += n * (wA if lean_child == 'alpha' else wB)
                    else:                                            # c3-case: roles exchanged
                        total += n * (wB if lean_child == 'alpha' else wA)
    return total // 2
