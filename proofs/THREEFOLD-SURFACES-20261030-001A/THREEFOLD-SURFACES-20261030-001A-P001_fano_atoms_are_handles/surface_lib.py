"""Orientable embeddings of cubic graphs by rotation systems (THREEFOLD-SURFACES-20261030-001A).

A graph is a list of edges (u, v), so parallel edges are allowed.  A dart is (edge index, tail).  A rotation system gives every vertex a
cyclic successor map on the indices of its incident edges; the faces are the orbits of the face-tracing map, which sends a dart along edge
e into vertex h to the dart along rot[h][e] out of h.  For a connected graph the genus of a rotation system is 1 - (V - E + F)/2, and the
genus of the graph is the least genus over rotation systems.  At a vertex of degree three there are exactly two rotations, one the mirror
of the other."""
import itertools, random
import networkx as nx
from pysat.formula import IDPool, CNF
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def from_nx(g):
    return [(u, v) for u, v in g.edges()]


def vertices(edges):
    return sorted({x for e in edges for x in e}, key=str)


def incident(edges):
    inc = {}
    for i, (u, v) in enumerate(edges):
        inc.setdefault(u, []).append(i)
        inc.setdefault(v, []).append(i)
    return inc


def head(edges, e, t):
    u, v = edges[e]
    return v if t == u else u


def rotation(edges, bits):
    """bits[v] = 0: incident edges in listed order, 1: the reverse cyclic order"""
    inc = incident(edges)
    rot = {}
    for v, o in inc.items():
        k = len(o)
        rot[v] = {o[i]: o[(i + 1) % k] for i in range(k)} if bits.get(v, 0) == 0 else {o[i]: o[(i - 1) % k] for i in range(k)}
    return rot


def mirror(rot):
    return {v: {b: a for a, b in s.items()} for v, s in rot.items()}


def faces(edges, rot):
    darts = [(i, u) for i, (u, v) in enumerate(edges)] + [(i, v) for i, (u, v) in enumerate(edges)]
    seen, out = set(), []
    for d in darts:
        if d in seen:
            continue
        f = []
        e, t = d
        while (e, t) not in seen:
            seen.add((e, t))
            f.append((e, t))
            h = head(edges, e, t)
            e, t = rot[h][e], h
        out.append(f)
    return out


def genus_of(edges, rot):
    V, E = len(vertices(edges)), len(edges)
    return 1 - (V - E + len(faces(edges, rot))) // 2


def _model(edges, F, fix_first=True):
    """SAT model: rotation bits r(v) and face labels x(d, k); satisfiable iff some rotation system has at least F faces"""
    inc = incident(edges)
    V = vertices(edges)
    assert all(len(inc[v]) == 3 for v in V), "cubic graphs only"
    darts = [(i, u) for i, (u, v) in enumerate(edges)] + [(i, v) for i, (u, v) in enumerate(edges)]
    did = {d: j for j, d in enumerate(darts)}
    pool = IDPool()
    r = lambda v: pool.id(('r', v))  # noqa: E731
    x = lambda d, k: pool.id(('x', d, k))  # noqa: E731
    cnf = CNF()
    if fix_first:
        cnf.append([-r(V[0])])
    for j in range(len(darts)):
        cnf.extend(CardEnc.equals([x(j, k) for k in range(F)], 1, vpool=pool, encoding=EncType.seqcounter).clauses)
    for (e, t), j in did.items():
        h = head(edges, e, t)
        o = inc[h]
        i = o.index(e)
        n0, n1 = did[(o[(i + 1) % 3], h)], did[(o[(i - 1) % 3], h)]
        for k in range(F):
            cnf.append([r(h), -x(j, k), x(n0, k)])
            cnf.append([-r(h), -x(j, k), x(n1, k)])
    for k in range(F):
        cnf.append([x(j, k) for j in range(len(darts))])
    for j in range(len(darts)):
        for k in range(1, F):
            cnf.append([-x(j, k)] + [x(i, k - 1) for i in range(j)])
    return cnf, r


def faces_at_least(edges, F, solver='cadical153'):
    if F <= 0:
        return True
    cnf, r = _model(edges, F)
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        return s.solve()


def genus(edges, lo=0, solver='cadical153'):
    """exact orientable genus of a connected cubic (multi)graph: the least g with a rotation system of at least E - V + 2 - 2g faces"""
    V, E = len(vertices(edges)), len(edges)
    g = lo
    while not faces_at_least(edges, E - V + 2 - 2 * g, solver):
        g += 1
    return g


def min_genus_rotations(edges, g):
    """all rotation systems (as bit maps) of genus at most g, by SAT with blocking clauses on the rotation bits"""
    V, E = len(vertices(edges)), len(edges)
    cnf, r = _model(edges, E - V + 2 - 2 * g, fix_first=False)
    out = []
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as s:
        while s.solve():
            m = set(l for l in s.get_model() if l > 0)
            bits = {v: int(r(v) in m) for v in vertices(edges)}
            out.append(bits)
            s.add_clause([-r(v) if bits[v] else r(v) for v in vertices(edges)])
    return out


def genus_reduced(edges):
    """genus of a graph of maximum degree three: loops and vertices of degree at most one are dropped and vertices of degree two
    suppressed (none of this changes the genus); components add (Battle-Harary-Kodama-Youngs); each is planar or measured by SAT"""
    g = nx.MultiGraph()
    g.add_edges_from(edges)
    changed = True
    while changed:
        changed = False
        for v in list(g):
            if g.number_of_edges(v, v):
                g.remove_edges_from([(v, v)] * g.number_of_edges(v, v))
                changed = True
            if g.degree(v) <= 1:
                g.remove_node(v)
                changed = True
            elif g.degree(v) == 2:
                a, b = [w for w in g[v] for _ in range(g.number_of_edges(v, w))]
                g.remove_node(v)
                g.add_edge(a, b)
                changed = True
    total = 0
    for comp in nx.connected_components(g):
        c = g.subgraph(comp)
        if not nx.check_planarity(nx.Graph(c))[0]:
            total += genus([(u, v) for u, v, k in c.edges(keys=True)])
    return total


# ------------------------------------------------------------------------------------------------ splices and cut permutations
def splice(A, x, R, y, perm=(0, 1, 2)):
    """delete x from A and y from R and join the edge-ends: the i-th edge at x (in A's edge order) meets the perm[i]-th edge at y"""
    ia = [i for i, e in enumerate(A) if x in e]
    ir = [i for i, e in enumerate(R) if y in e]
    assert len(ia) == 3 and len(ir) == 3
    out = [(('a', u), ('a', v)) for i, (u, v) in enumerate(A) if i not in ia]
    out += [(('b', u), ('b', v)) for i, (u, v) in enumerate(R) if i not in ir]
    ends_a = [A[i][0] if A[i][1] == x else A[i][1] for i in ia]
    ends_r = [R[i][0] if R[i][1] == y else R[i][1] for i in ir]
    out += [(('a', ends_a[k]), ('b', ends_r[perm[k]])) for k in range(3)]
    return out


def cut_data(edges, rot, Y):
    """for a 3-edge cut with shore Y: the cut edge indices c[0..2] (ordered by index), and the transitions tau (entering Y via c[i], the face
    first leaves via c[tau[i]]) and pi (the same for the other side)"""
    Y = set(Y)
    c = [i for i, (u, v) in enumerate(edges) if (u in Y) != (v in Y)]
    assert len(c) == 3
    pos = {e: k for k, e in enumerate(c)}

    def transitions(side_in):
        out = {}
        for k, e in enumerate(c):
            u, v = edges[e]
            t = u if u not in side_in else v                       # tail outside the side, so the dart enters it
            ee, tt = e, t
            while True:
                h = head(edges, ee, tt)
                ee, tt = rot[h][ee], h
                if ee in pos and head(edges, ee, tt) not in side_in:
                    out[k] = pos[ee]
                    break
        return tuple(out[k] for k in range(3))
    V = set(vertices(edges))
    return c, transitions(Y), transitions(V - Y)


def contract_side(edges, rot, Y, c, r, name):
    """G/(complement of Y): the outside becomes one vertex `name` with rotation r (a successor map on positions 0..2 of the cut edges)"""
    Y = set(Y)
    keep = [i for i, (u, v) in enumerate(edges) if u in Y or v in Y]
    new_edges, newid = [], {}
    for i in keep:
        u, v = edges[i]
        newid[i] = len(new_edges)
        new_edges.append((u if u in Y else name, v if v in Y else name))
    new_rot = {}
    for v in Y:
        new_rot[v] = {newid[a]: newid[b] for a, b in rot[v].items()}
    new_rot[name] = {newid[c[k]]: newid[c[r[k]]] for k in range(3)}
    return new_edges, new_rot


# ------------------------------------------------------------------------------------------------ permutations of three cut edges
S3 = [p for p in itertools.permutations(range(3))]
CYCLES3 = [(1, 2, 0), (2, 0, 1)]


def compose(p, q):
    """(p o q)(i) = p[q[i]]"""
    return tuple(p[q[i]] for i in range(3))


def inverse(p):
    out = [0] * 3
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


def cycles(p):
    seen, n = set(), 0
    for i in range(3):
        if i not in seen:
            n += 1
            j = i
            while j not in seen:
                seen.add(j)
                j = p[j]
    return n


def D(tau, pi, r, rt):
    """twice the genus defect at the cut: cyc(r tau) + cyc(rt pi) - cyc(pi tau) - 3 (even)"""
    return cycles(compose(r, tau)) + cycles(compose(rt, pi)) - cycles(compose(pi, tau)) - 3


# ------------------------------------------------------------------------------------------------ orbits of rotation systems
def automorphisms(edges):
    g = nx.Graph()
    g.add_edges_from(edges)
    from networkx.algorithms.isomorphism import GraphMatcher
    return list(GraphMatcher(g, g).isomorphisms_iter())


def canonical(edges, rot, autos):
    """least image of a rotation system of a simple graph under automorphisms and mirroring (as neighbour successor maps)"""
    nbr = {}
    for v, s in rot.items():
        nbr[v] = {head(edges, a, v): head(edges, b, v) for a, b in s.items()}
    best = None
    for a in autos:
        for m in (False, True):
            key = []
            for v, s in nbr.items():
                pairs = s.items() if not m else [(w, u) for u, w in s.items()]
                key.append((str(a[v]), tuple(sorted((str(a[u]), str(a[w])) for u, w in pairs))))
            key = tuple(sorted(key))
            if best is None or key < best:
                best = key
    return best


def random_rotation(edges, rnd):
    return rotation(edges, {v: rnd.randrange(2) for v in vertices(edges)})
