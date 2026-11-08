"""Round spheres need one hidden bit per incidence, for SPHERE-GROWTH-20261107-001A.

Spaces are the knot spaces of COUNT-SURFACES-20261107-001A: a triangulation T of a closed surface with its triangles coloured in two
colours (points and lines), so that the incidences are T's sides and the co-lines are T's vertices. The two-kind law asks every
co-line to have two or three points (T-degree 4 or 6); a co-line of two points is a digon.

Constructions: the octahedral spheres K_m (with vertex coordinates), the capped tubes T(m, L, tau) (a lattice cylinder of
circumference 3m and L rows, closed by two triangles of side m, the top one turned by tau), and random closed spheres grown one
triangle at a time (test inputs only).

Laws: a law of radius r without hidden states is a set of allowed radius-r balls (rooted at a co-line, up to isomorphism, colours
kept); `ball_set` lists a sphere's balls. The seam law puts one hidden bit on every incidence: S1, every incidence of a digon is a
seam; S2, a co-line of three points has no seam or exactly two opposite ones. `seam_markings` finds the markings with a SAT solver
and `straight_rays` tests the same condition directly, by following the incidences of the digons straight on."""
import itertools
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/COUNT-SURFACES-20261107-001A/COUNT-SURFACES-20261107-001A-P001_the_count_reads_the_euler_characteristic"))
import surface_lib as SL  # noqa: E402


# ------------------------------------------------------------------------------------------------ spheres
def from_triangles(name, tris):
    """a closed surface from vertex triples, every edge in exactly two triangles; colours by alternation"""
    by_edge = defaultdict(list)
    for t, P in enumerate(tris):
        assert len(set(P)) == 3, "a triangle repeats a vertex"
        for k in range(3):
            by_edge[frozenset((P[(k + 1) % 3], P[(k + 2) % 3]))].append(t)
    if not all(len(v) == 2 for v in by_edge.values()):
        raise ValueError("an edge does not lie in exactly two triangles")
    col = [None] * len(tris)
    col[0], stack = 0, [0]
    while stack:
        t = stack.pop()
        P = tris[t]
        for k in range(3):
            a, b = by_edge[frozenset((P[(k + 1) % 3], P[(k + 2) % 3]))]
            u = b if a == t else a
            if col[u] is None:
                col[u] = 1 - col[t]
                stack.append(u)
            elif col[u] == col[t]:
                raise ValueError("the triangles are not 2-colourable")

    def nbr(t, k):
        P = tris[t]
        b, c = P[(k + 1) % 3], P[(k + 2) % 3]
        two = by_edge[frozenset((b, c))]
        return (two[0] if two[1] == t else two[1]), {b: b, c: c}
    S = SL.from_cover(name, [(col[t], tuple(P)) for t, P in enumerate(tris)], nbr)
    S.vtris = [tuple(P) for P in tris]
    S.vname = [None] * S.nv
    for t, P in enumerate(tris):
        for c in range(3):
            S.vname[S.vert[t][c]] = P[c]
    return S


def octahedral(m):
    """K_m with vertex coordinates (x, y, z), |x| + |y| + |z| = m: the same triangles as surface_lib.octahedral_sphere(m)"""
    tris = []
    for sx, sy, sz in itertools.product((1, -1), repeat=3):
        def P(i, j, l, sx=sx, sy=sy, sz=sz):
            return (sx * i, sy * j, sz * l)
        for i in range(m):
            for j in range(m - i):
                l = m - 1 - i - j
                tris.append((P(i + 1, j, l), P(i, j + 1, l), P(i, j, l + 1)))
        for i in range(m - 1):
            for j in range(m - 1 - i):
                l = m - 2 - i - j
                tris.append((P(i + 1, j + 1, l), P(i + 1, j, l + 1), P(i, j + 1, l + 1)))
    S = from_triangles(f"K_{m}", tris)
    S.kind, S.params = "octahedral", (m,)
    return S


def tube(m, L, tau=0):
    """a band of L rows on the lattice cylinder of circumference 3m, closed by two triangles of side m. Band vertex B(i, j) sits at
    x = i + j/2 on row j. The bottom cap's corners are B(0, 0), B(m, 0), B(2m, 0); the top cap's are B(tau, L), B(tau + m, L),
    B(tau + 2m, L). tube(m, m, 0) is K_m: its six side faces form the band."""
    W = 3 * m

    def B(i, j):
        return ("B", i % W, j)
    tris = []
    for j in range(L):
        for i in range(W):
            tris.append((B(i, j), B(i + 1, j), B(i, j + 1)))
            tris.append((B(i + 1, j), B(i + 1, j + 1), B(i, j + 1)))

    def cap(tag, row, off):
        def C(a, b):
            if b == 0:
                return B(off + a, row)
            if a + b == m:
                return B(off + m + b, row)
            if a == 0:
                return B(off + 3 * m - b, row)
            return (tag, a, b)
        out = [(C(a, b), C(a + 1, b), C(a, b + 1)) for a in range(m) for b in range(m - a)]
        out += [(C(a + 1, b), C(a + 1, b + 1), C(a, b + 1)) for a in range(m - 1) for b in range(m - 1 - a)]
        return out
    tris += cap("bottom", 0, 0) + cap("top", L, tau)
    S = from_triangles(f"T({m},{L},{tau})", tris)
    S.kind, S.params = "tube", (m, L, tau)
    return S


def degrees(S):
    c = Counter(v for t in range(S.nt) for v in S.vert[t])
    return [c[v] for v in range(S.nv)]


def random_sphere(rng, q=0.2, maxv=300):
    """test inputs: grow a disc one triangle at a time at the boundary vertex with the most triangles; a vertex closes with six
    triangles, or with four (probability q when it has three); the last three boundary vertices close together. Returns a closed
    sphere with all degrees 4 or 6, or None."""
    count = defaultdict(int)
    tris = [(0, 1, 2)]
    for v in range(3):
        count[v] = 1
    nv, B = 3, [0, 1, 2]
    while nv <= maxv:
        if len(B) == 3 and all(count[v] + 1 in (4, 6) for v in B):
            tris.append(tuple(B))
            try:
                S = from_triangles("grown", tris)
            except ValueError:
                return None
            return S if S.validate() and S.euler() == 2 and set(degrees(S)) <= {4, 6} else None
        c, _, i = max((count[v], rng.random(), i) for i, v in enumerate(B))
        v, u, w = B[i], B[i - 1], B[(i + 1) % len(B)]
        if c == 5 or (c == 3 and rng.random() < q):
            tris.append((u, v, w))
            count[u] += 1
            count[w] += 1
            count[v] += 1
            B.pop(i)
        elif c >= 6:
            return None
        else:
            x = nv
            nv += 1
            tris.append((v, w, x))
            count[v] += 1
            count[w] += 1
            count[x] = 1
            B.insert(i + 1, x)
    return None


# ------------------------------------------------------------------------------------------------ maps: codes and balls
def _code(S, t0, frame0, allowed=None):
    """breadth-first search over triangles from a rooted frame (a corner order); each triangle lists its colour and the labels of
    its neighbours across the sides opposite its frame's corners, frames passed on so that orientation is kept"""
    label, frame, order, out = {t0: 0}, {t0: frame0}, [t0], []
    i = 0
    while i < len(order):
        t = order[i]
        i += 1
        f = frame[t]
        row = [S.colour[t]]
        for k in range(3):
            s = f[k]
            t2, k2 = S.side[t][s]
            if allowed is not None and t2 not in allowed:
                row.append(-1)
                continue
            if t2 not in label:
                g1 = S.cmap[t][s][f[(k + 1) % 3]]
                g2 = S.cmap[t][s][f[(k + 2) % 3]]
                label[t2] = len(order)
                frame[t2] = (k2, g2, g1)
                order.append(t2)
            row.append(label[t2])
        out.append(tuple(row))
    return tuple(out)


def frames_at(t, c):
    return [(c, (c + 1) % 3, (c + 2) % 3), (c, (c + 2) % 3, (c + 1) % 3)]


def isomorphic(S1, S2):
    """colour-preserving isomorphism of the two triangulated surfaces, reflections allowed"""
    if S1.nt != S2.nt or S1.nv != S2.nv or sorted(degrees(S1)) != sorted(degrees(S2)):
        return False
    target = _code(S1, 0, (0, 1, 2))
    return any(_code(S2, t, f) == target for t in range(S2.nt) for c in range(3) for f in frames_at(t, c))


def vertex_graph(S):
    adj, tris_at = defaultdict(set), defaultdict(list)
    for t in range(S.nt):
        V = S.vert[t]
        for c in range(3):
            tris_at[V[c]].append((t, c))
            for c2 in range(3):
                if c2 != c:
                    adj[V[c]].add(V[c2])
    return adj, tris_at


def ball_code(S, v, r, adj, tris_at):
    """the radius-r ball at the co-line v (the triangles whose three corners lie within distance r of v), rooted at v, up to
    isomorphism with colours kept"""
    dist, dq = {v: 0}, deque([v])
    while dq:
        x = dq.popleft()
        if dist[x] == r:
            continue
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                dq.append(y)
    allowed = {t for t in range(S.nt) if all(u in dist for u in S.vert[t])}
    return min(_code(S, t, f, allowed) for t, c in tris_at[v] for f in frames_at(t, c))


def ball_set(S, r):
    adj, tris_at = vertex_graph(S)
    return {ball_code(S, v, r, adj, tris_at) for v in range(S.nv)}


# ------------------------------------------------------------------------------------------------ the seam law
def incidence_cycles(S, K):
    """for each co-line (vertex of T), the incidences around it (B-edges 3i + k: line i, side k) in cyclic order"""
    eid = {}
    for t in range(S.nt):
        for k in range(3):
            t2, k2 = S.side[t][k]
            eid[(t, k)] = 3 * K.lid[t] + k if S.colour[t] == 1 else 3 * K.lid[t2] + k2
    cyc, seen = {}, set()
    for t in range(S.nt):
        for c in range(3):
            if (t, c) in seen:
                continue
            v = S.vert[t][c]
            start = cur = (t, c)
            came, seq = None, []
            while True:
                seen.add(cur)
                tt, cc = cur
                ks = [k for k in range(3) if k != cc]
                k = ks[0] if came != ks[0] else ks[1]
                seq.append(eid[(tt, k)])
                t2, k2 = S.side[tt][k]
                cur, came = (t2, S.cmap[tt][k][cc]), k2
                if cur == start:
                    break
            cyc[v] = seq
    return cyc


def seam_clauses(cyc, straight=True):
    """S1 and S2 as clauses; variable e + 1 says incidence e is a seam. With straight=False (a control) S2 allows any two seams."""
    cl = []
    for v, seq in cyc.items():
        x = [e + 1 for e in seq]
        if len(x) == 4:
            cl += [[a] for a in x]
        elif len(x) == 6:
            if straight:
                for i in range(6):
                    cl.append([-x[i], x[(i + 3) % 6]])
                    for j in range(i + 1, 6):
                        if j - i != 3:
                            cl.append([-x[i], -x[j]])
            else:
                for a, b, c in itertools.combinations(x, 3):
                    cl.append([-a, -b, -c])
                for a in x:
                    cl.append([-a] + [b for b in x if b != a])
        else:
            raise ValueError("a co-line with other than two or three points")
    return cl


def seam_markings(S, K=None, limit=3, straight=True):
    """up to `limit` seam markings (sets of incidences)"""
    from pysat.solvers import Solver
    K = K or SL.KnotSpace(S)
    cyc = incidence_cycles(S, K)
    sols = []
    with Solver(name="cadical153", bootstrap_with=seam_clauses(cyc, straight)) as so:
        while len(sols) < limit and so.solve():
            mdl = so.get_model()
            sols.append(frozenset(e - 1 for e in mdl if e > 0))
            so.add_clause([-e for e in mdl if abs(e) <= 3 * K.n])
    return sols


def straight_rays(S, K=None):
    """from each digon follow each of its incidences straight on (the opposite incidence at each co-line of three points) until a
    digon is reached; returns the rays and whether they meet only at their ends (each inner co-line on exactly one segment, which
    is traced once from each end)"""
    K = K or SL.KnotSpace(S)
    cyc = incidence_cycles(S, K)
    ends = defaultdict(list)
    for v, seq in cyc.items():
        for e in seq:
            ends[e].append(v)
    pos = {(v, e): i for v, seq in cyc.items() for i, e in enumerate(seq)}
    rays = []
    for d in (v for v, s in cyc.items() if len(s) == 4):
        for e in cyc[d]:
            path, edges, cur_v, cur_e = [d], [e], d, e
            while True:
                a, b = ends[cur_e]
                w = b if a == cur_v else a
                path.append(w)
                if len(cyc[w]) == 4:
                    break
                cur_e = cyc[w][(pos[(w, cur_e)] + 3) % 6]
                edges.append(cur_e)
                cur_v = w
            rays.append((path, edges))
    inner = Counter(w for p, _ in rays for w in p[1:-1])
    return rays, all(c == 2 for c in inner.values())


def octahedron_edges(S, K=None):
    """on octahedral(m): the incidences (sides of T) whose two ends share a zero coordinate, i.e. lie on an edge of the octahedron"""
    K = K or SL.KnotSpace(S)
    out = set()
    for i, l in enumerate(K.lines):
        for k in range(3):
            a, b = S.vname[S.vert[l][(k + 1) % 3]], S.vname[S.vert[l][(k + 2) % 3]]
            if any(a[c] == 0 and b[c] == 0 for c in range(3)):
                out.add(3 * i + k)
    return frozenset(out)


def cubic_quadrangulations():
    """the 4 x 4 biadjacency matrices (row and column sums 3) of the cubic bipartite multigraphs on 4 + 4 vertices that have an
    embedding in the sphere with all six faces of length 4 (the region map of a seam marking is dual to one)"""
    rows = [r for r in itertools.product(range(4), repeat=4) if sum(r) == 3]
    found = set()
    for M in itertools.product(rows, repeat=4):
        if any(sum(M[i][j] for i in range(4)) != 3 for j in range(4)):
            continue
        edges = [(i, 4 + j) for i in range(4) for j in range(4) for _ in range(M[i][j])]
        darts = defaultdict(list)
        for e, (a, b) in enumerate(edges):
            darts[a].append((e, 0))
            darts[b].append((e, 1))
        for rot in itertools.product((0, 1), repeat=8):
            nxt = {}
            for v in range(8):
                h = darts[v] if rot[v] == 0 else [darts[v][0], darts[v][2], darts[v][1]]
                for k in range(3):
                    nxt[h[k]] = h[(k + 1) % 3]
            seen, lengths = set(), []
            for e in range(12):
                for end in (0, 1):
                    if (e, end) in seen:
                        continue
                    n, cur = 0, (e, end)
                    while cur not in seen:
                        seen.add(cur)
                        n += 1
                        e2, end2 = cur
                        cur = nxt[(e2, 1 - end2)]
                    lengths.append(n)
            if len(lengths) == 6 and all(x == 4 for x in lengths):
                found.add(M)
    return found


# ------------------------------------------------------------------------------------------------ the knot on these spheres
def kasteleyn(S):
    """the knot space with a Kasteleyn signing (no even co-line); on a sphere it exists and is unique up to gauge"""
    K = SL.KnotSpace(S)
    return K, K.signing(())


def elimination_width(S, K):
    """induced width of eliminating the points in breadth-first order from point 0 (the primal graph joins two points on a common
    line); Davis-Putnam elimination in this order refutes with clauses of at most width + 1 literals"""
    adj = defaultdict(set)
    for i in range(K.n):
        a, b, c = K.pt[i]
        adj[a] |= {b, c}
        adj[b] |= {a, c}
        adj[c] |= {a, b}
    dist, dq = {0: 0}, deque([0])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                dq.append(y)
    g = {p: set(adj[p]) for p in range(K.n)}
    width = 0
    for p in sorted(range(K.n), key=lambda p: (dist[p], p)):
        nb = g.pop(p)
        width = max(width, len(nb))
        for a in nb:
            g[a].discard(p)
            g[a] |= nb - {a}
    return width
