"""Knot spaces on closed surfaces, for COUNT-SURFACES-20261107-001A.

A knot space is read off a triangulation T of a closed surface S whose triangles are coloured in two colours, neighbours differing:
the points are the triangles of colour 0, the lines those of colour 1, and a point lies on a line once for every side they share.
The incidence graph B (points, lines, one edge per side of T) is then cellularly embedded in S, dual to T, so B's faces are T's
vertices. A signing puts a bit on every side; a line's not-all-equal constraint reads the literals x_p xor s over its three sides.
A line's corner at a vertex v of T is the pair of its two sides at v; under an assignment the corner agrees when those two literals
are equal. A satisfied line has one agreeing corner, a violated (monochromatic) one three.

What proof.md proves, and this module checks:
- agree_v = d_v + flip_v (mod 2) under every assignment, where d_v is the number of line corners at v and flip_v the sum of the
  signs on those corners' sides; the set D of vertices where this is even has |D| = chi (mod 2), and every such D occurs;
- violated lines - E = (chi - |D|) / 2 under every assignment, where E = sum over v of floor(agree_v / 2);
- with chi = |D| the satisfying assignments come in complementary pairs, one pair for each perfect matching of the lines with the
  vertices outside D (along corners) whose homology class matches the signing's.

A triangulation is stored as glued triangles: colour[t], side[t][k] = (t2, k2) (side k of t, opposite its corner k, is glued to side
k2 of t2) and cmap[t][k] = {c: c2} (corner c of t, for the two corners c != k, sits at the same vertex as corner c2 of t2). Vertices
are classes of corners. Constructions: lattice tori and Klein bottles (quotients of the triangular lattice by translations and
glides that keep the two colours), projective planes (a hexagon of the lattice with antipodal boundary gluing), the octahedral
spheres (the knot spheres K_k), and branched double covers of any of these."""
import itertools
import random
from collections import defaultdict

import numpy as np

# ------------------------------------------------------------------------------------------------ triangulations


class Surface:
    def __init__(self, name, colour, side, cmap, corners_at=None):
        self.name, self.colour, self.side, self.cmap = name, list(colour), [list(s) for s in side], [list(c) for c in cmap]
        self.nt = len(self.colour)
        self._vertices()
        self.corners_at = corners_at

    def _vertices(self):
        par = {(t, c): (t, c) for t in range(self.nt) for c in range(3)}

        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a
        for t in range(self.nt):
            for k in range(3):
                t2, _ = self.side[t][k]
                for c, c2 in self.cmap[t][k].items():
                    ra, rb = find((t, c)), find((t2, c2))
                    if ra != rb:
                        par[ra] = rb
        roots = sorted({find(a) for a in par})
        rid = {r: i for i, r in enumerate(roots)}
        self.vert = [[rid[find((t, c))] for c in range(3)] for t in range(self.nt)]
        self.nv = len(roots)

    def euler(self):
        return self.nv - 3 * self.nt // 2 + self.nt

    def validate(self):
        """gluings symmetric, colours alternate, every vertex link one cycle"""
        ok = self.nt % 2 == 0
        for t in range(self.nt):
            for k in range(3):
                t2, k2 = self.side[t][k]
                ok &= self.side[t2][k2] == (t, k) and self.colour[t] != self.colour[t2]
                cm = self.cmap[t][k]
                ok &= sorted(cm) == sorted({0, 1, 2} - {k}) and sorted(cm.values()) == sorted({0, 1, 2} - {k2})
                ok &= all(self.cmap[t2][k2][c2] == c for c, c2 in cm.items())
        # links: walk around each vertex
        seen = set()
        for t in range(self.nt):
            for c in range(3):
                if (t, c) in seen:
                    continue
                v = self.vert[t][c]
                start, cur, came, n = (t, c), (t, c), None, 0
                while True:
                    seen.add(cur)
                    n += 1
                    tt, cc = cur
                    ks = [k for k in range(3) if k != cc]
                    k = ks[0] if came != ks[0] else ks[1]
                    t2, k2 = self.side[tt][k]
                    nxt = (t2, self.cmap[tt][k][cc])
                    came, cur = k2, nxt
                    if cur == start:
                        break
                    if n > 6 * self.nt:
                        return False
                ok &= sum(1 for a in range(self.nt) for b in range(3) if self.vert[a][b] == v) == n
        return bool(ok)

    def orientable(self):
        """local corner orders (0, 1, 2) taken as orientations; a gluing is orientation-reversing when it pairs corner k+1 of t with
        corner k2+1 of t2"""
        o = [None] * self.nt
        for s in range(self.nt):
            if o[s] is not None:
                continue
            o[s], stack = 0, [s]
            while stack:
                t = stack.pop()
                for k in range(3):
                    t2, k2 = self.side[t][k]
                    rev = int(self.cmap[t][k][(k + 1) % 3] == (k2 + 1) % 3)
                    want = o[t] ^ rev
                    if o[t2] is None:
                        o[t2] = want
                        stack.append(t2)
                    elif o[t2] != want:
                        return False
        return True

    def connected(self):
        seen, stack = {0}, [0]
        while stack:
            t = stack.pop()
            for k in range(3):
                t2 = self.side[t][k][0]
                if t2 not in seen:
                    seen.add(t2)
                    stack.append(t2)
        return len(seen) == self.nt


def from_cover(name, tris, nbr):
    """tris: list of (colour, (P0, P1, P2)) for one representative per triangle (positions in a cover, any hashable points);
    nbr(t, k) -> (t2, {P: Q}) gives the triangle across side k of tris[t] and where its side's two endpoints sit in tris[t2]"""
    side, cmap = [], []
    for t, (col, P) in enumerate(tris):
        srow, crow = [], []
        for k in range(3):
            t2, where = nbr(t, k)
            Q = tris[t2][1]
            c1 = Q.index(where[P[(k + 1) % 3]])
            c2 = Q.index(where[P[(k + 2) % 3]])
            srow.append((t2, 3 - c1 - c2))
            crow.append({(k + 1) % 3: c1, (k + 2) % 3: c2})
        side.append(srow)
        cmap.append(crow)
    return Surface(name, [c for c, _ in tris], side, cmap)


# lattice coordinates (i, j) stand for the point i*a + j*b with a = (1, 0), b = (1/2, sqrt(3)/2); positions are scaled by 6 so that
# vertices, side midpoints and centroids are integral. up(i, j) has corners (i, j), (i+1, j), (i, j+1); down(i, j) has corners
# (i+1, j), (i+1, j+1), (i, j+1); both lists are counterclockwise.
def up(i, j):
    return ((6 * i, 6 * j), (6 * i + 6, 6 * j), (6 * i, 6 * j + 6))


def down(i, j):
    return ((6 * i + 6, 6 * j), (6 * i + 6, 6 * j + 6), (6 * i, 6 * j + 6))


def centroid(P):
    return (sum(p[0] for p in P) // 3, sum(p[1] for p in P) // 3)


def across(P, k):
    """the triangle across side k in the plane, with the same two shared corners"""
    a, b, c = P[k], P[(k + 1) % 3], P[(k + 2) % 3]
    return (b[0] + c[0] - a[0], b[1] + c[1] - a[1])


def lattice_quotient(name, fundamental, canon):
    """fundamental: list of (i, j) whose up and down triangles represent every orbit once; canon(point) -> (point', affine map)"""
    tris = []
    for (i, j) in fundamental:
        tris.append((0, up(i, j)))
        tris.append((1, down(i, j)))
    key = {}
    for t, (_, P) in enumerate(tris):
        cc, _ = canon(centroid(P))
        assert cc not in key, "fundamental domain repeats a triangle"
        key[cc] = t
    assert all(canon(centroid(P))[0] == centroid(P) for _, P in tris), "fundamental triangles must be canonical"

    def nbr(t, k):
        P = tris[t][1]
        b, c = P[(k + 1) % 3], P[(k + 2) % 3]
        a2 = across(P, k)
        cen = ((a2[0] + b[0] + c[0]) // 3, (a2[1] + b[1] + c[1]) // 3)
        cc, g = canon(cen)
        return key[cc], {b: g(b), c: g(c)}
    S = from_cover(name, tris, nbr)
    S.tris, S.canon = tris, canon
    return S


def torus(p, q, r):
    """the triangular lattice modulo L = <(p, 0), (q, r)> (Hermite normal form, 0 <= q < p), index p*r"""
    def canon(pt):
        X, Y = pt
        t = Y // (6 * r)
        dX, dY = -6 * q * t, -6 * r * t
        X2 = X + dX
        u = X2 // (6 * p)
        dX -= 6 * p * u
        return (X + dX, Y + dY), (lambda z, dX=dX, dY=dY: (z[0] + dX, z[1] + dY))
    S = lattice_quotient(f"torus({p},{q},{r})", [(i, j) for j in range(r) for i in range(p)], canon)
    S.kind, S.params = "torus", (p, q, r)
    return S


def klein(m, h, c=0):
    """the triangular lattice modulo <t: (i, j) -> (i + m, j), g: (i, j) -> (-i - j + c, j + h)>; g reflects in a line perpendicular
    to a lattice direction (keeping the two colours) and glides h rows; c = 0 puts the axis through vertices of every other row, c = 1
    halfway between (conjugating by a lattice translation changes c by an even number); the quotient is a Klein bottle with m*h
    vertices"""
    def g(z):
        return (-z[0] - z[1] + 6 * c, z[1] + 6 * h)

    def ginv(z):
        return (-z[0] - z[1] + 6 * h + 6 * c, z[1] - 6 * h)

    def canon(pt):
        maps = []
        z = pt
        while z[1] >= 6 * h:
            z = ginv(z)
            maps.append(ginv)
        while z[1] < 0:
            z = g(z)
            maps.append(g)
        u = z[0] // (6 * m)
        z = (z[0] - 6 * m * u, z[1])

        def f(w, maps=tuple(maps), u=u):
            for mp in maps:
                w = mp(w)
            return (w[0] - 6 * m * u, w[1])
        return z, f
    # the fundamental strip X in [0, 6m), Y in [0, 6h) must hold one centroid per orbit: take triangles by canonical centroid
    S = lattice_quotient(f"klein({m},{h},{c})", [(i, j) for j in range(h) for i in range(m)], canon)
    S.kind, S.params = "klein", (m, h, c)
    return S


def projective_plane(m):
    """the hexagon max(|i|, |j|, |i + j|) <= m of the lattice, centred at a vertex, with antipodal boundary points identified; the
    point reflection swaps up and down triangles, so the colours agree across the gluing"""
    def inside(z):
        i, j = z[0] / 6, z[1] / 6
        return max(abs(i), abs(j), abs(i + j)) <= m + 1e-9
    tris = []
    for i in range(-m - 1, m + 1):
        for j in range(-m - 1, m + 1):
            for col, P in ((0, up(i, j)), (1, down(i, j))):
                if all(inside(z) for z in P):
                    tris.append((col, P))
    key = {centroid(P): t for t, (_, P) in enumerate(tris)}

    def nbr(t, k):
        P = tris[t][1]
        b, c = P[(k + 1) % 3], P[(k + 2) % 3]
        a2 = across(P, k)
        cen = ((a2[0] + b[0] + c[0]) // 3, (a2[1] + b[1] + c[1]) // 3)
        if cen in key:
            return key[cen], {b: b, c: c}
        neg = (-centroid(P)[0], -centroid(P)[1])
        return key[neg], {b: (-b[0], -b[1]), c: (-c[0], -c[1])}
    S = from_cover(f"projective_plane({m})", tris, nbr)
    S.kind, S.params = "projective plane", (m,)
    return S


def octahedral_sphere(k):
    """the k-frequency octahedron; a triangle's colour is its orientation class (up/down within its octant) xor its octant's sign"""
    tris = []
    for sx, sy, sz in itertools.product((1, -1), repeat=3):
        P = lambda i, j, l: (sx * i, sy * j, sz * l)  # noqa: E731
        neg = int(sx * sy * sz < 0)
        for i in range(k):
            for j in range(k - i):
                l = k - 1 - i - j
                tris.append((neg, (P(i + 1, j, l), P(i, j + 1, l), P(i, j, l + 1))))
        for i in range(k - 1):
            for j in range(k - 1 - i):
                l = k - 2 - i - j
                tris.append((1 - neg, (P(i + 1, j + 1, l), P(i + 1, j, l + 1), P(i, j + 1, l + 1))))
    by_pair = defaultdict(list)
    for t, (_, P) in enumerate(tris):
        for kk in range(3):
            by_pair[frozenset((P[(kk + 1) % 3], P[(kk + 2) % 3]))].append(t)

    def nbr(t, kk):
        P = tris[t][1]
        b, c = P[(kk + 1) % 3], P[(kk + 2) % 3]
        two = by_pair[frozenset((b, c))]
        assert len(two) == 2
        return (two[0] if two[1] == t else two[1]), {b: b, c: c}
    S = from_cover(f"octahedral_sphere({k})", tris, nbr)
    S.kind, S.params = "sphere", (k,)
    return S


def double_cover(S, branch):
    """the double cover of S branched exactly at the vertex set `branch` (even size): sheets switch across a set of sides whose
    vertex degrees are odd exactly at `branch` (a join of shortest paths)"""
    branch = sorted(branch)
    assert len(branch) % 2 == 0
    # the 1-skeleton: edges = glued side pairs
    eid, ends = {}, []
    for t in range(S.nt):
        for k in range(3):
            if (t, k) in eid:
                continue
            t2, k2 = S.side[t][k]
            e = len(ends)
            eid[(t, k)] = eid[(t2, k2)] = e
            ends.append((S.vert[t][(k + 1) % 3], S.vert[t][(k + 2) % 3]))
    adj = defaultdict(list)
    for e, (a, b) in enumerate(ends):
        adj[a].append((b, e))
        adj[b].append((a, e))
    cut = [0] * len(ends)
    for a, b in zip(branch[0::2], branch[1::2]):
        prev, frontier = {a: None}, [a]
        while b not in prev:
            nxt = []
            for v in frontier:
                for w, e in adj[v]:
                    if w not in prev:
                        prev[w] = (v, e)
                        nxt.append(w)
            frontier = nxt
        v = b
        while prev[v] is not None:
            v, e = prev[v]
            cut[e] ^= 1
    deg = defaultdict(int)
    for e, (a, b) in enumerate(ends):
        if cut[e]:
            deg[a] += 1
            deg[b] += 1
    assert {v for v in deg if deg[v] % 2} == set(branch)
    colour, side, cmap = [], [], []
    for sh in (0, 1):
        for t in range(S.nt):
            colour.append(S.colour[t])
            side.append([(S.side[t][k][0] + S.nt * (sh ^ cut[eid[(t, k)]]), S.side[t][k][1]) for k in range(3)])
            cmap.append([dict(S.cmap[t][k]) for k in range(3)])
    C = Surface(f"double_cover({S.name}, {branch})", colour, side, cmap)
    C.kind, C.params, C.base = "double cover", (S.name, tuple(branch)), S
    return C


# ------------------------------------------------------------------------------------------------ the knot space and its signings


class KnotSpace:
    def __init__(self, S):
        self.S = S
        self.points = [t for t in range(S.nt) if S.colour[t] == 0]
        self.lines = [t for t in range(S.nt) if S.colour[t] == 1]
        self.n = len(self.points)
        assert len(self.lines) == self.n
        pid = {t: i for i, t in enumerate(self.points)}
        self.lid = {t: i for i, t in enumerate(self.lines)}
        # line i, side k: the point across it; B-edge index 3i + k
        self.pt = [[pid[S.side[l][k][0]] for k in range(3)] for l in self.lines]
        # corners: (line i, corner c) at vertex v, made of sides (c+1)%3 and (c+2)%3
        self.corners_at = defaultdict(list)
        for i, l in enumerate(self.lines):
            for c in range(3):
                self.corners_at[S.vert[l][c]].append((i, c))
        self.V = S.nv
        self.d = [len(self.corners_at[v]) for v in range(self.V)]
        self.chi = S.euler()
        # the point's three sides as B-edges (for gauge)
        self.point_sides = defaultdict(list)
        for i in range(self.n):
            for k in range(3):
                self.point_sides[self.pt[i][k]].append(3 * i + k)

    def simple(self):
        """every line has three distinct points"""
        return all(len(set(p)) == 3 for p in self.pt)

    def flip(self, s):
        return [sum(s[3 * i + (c + 1) % 3] + s[3 * i + (c + 2) % 3] for i, c in self.corners_at[v]) % 2 for v in range(self.V)]

    def even_faces(self, s):
        f = self.flip(s)
        return sorted(v for v in range(self.V) if (self.d[v] + f[v]) % 2 == 0)

    # -------------------------------------------------------------------------------------- linear algebra over F2 (ints as bit rows)
    def _face_rows(self):
        rows = []
        for v in range(self.V):
            r = 0
            for i, c in self.corners_at[v]:
                r ^= 1 << (3 * i + (c + 1) % 3)
                r ^= 1 << (3 * i + (c + 2) % 3)
            rows.append(r)
        return rows

    def gauge_vectors(self):
        g = []
        for p in range(self.n):
            r = 0
            for e in self.point_sides[p]:
                r ^= 1 << e
            g.append(r)
        for i in range(self.n):
            g.append(0b111 << (3 * i))
        return g

    def signing(self, D=()):
        """a signing whose even faces are exactly D, or None"""
        D = set(D)
        rows = self._face_rows()
        target = [(self.d[v] + 1 + (v in D)) % 2 for v in range(self.V)]
        sol = solve_f2(rows, target, 3 * self.n)
        if sol is None:
            return None
        return [(sol >> e) & 1 for e in range(3 * self.n)]

    def classes(self):
        """a basis of the flat signings (all flips zero) modulo gauge: its size is the F2-dimension of H_1(S)"""
        rows = self._face_rows()
        ker = kernel_f2(rows, 3 * self.n)
        gauge = self.gauge_vectors()
        span = Basis()
        for g in gauge:
            span.add(g)
        assert all(span.reduce(g) == 0 for g in gauge)
        assert all(all(bin(r & g).count("1") % 2 == 0 for r in rows) for g in gauge), "gauge must be flat"
        out = []
        for z in ker:
            if span.add(z):
                out.append(z)
        return [[(z >> e) & 1 for e in range(3 * self.n)] for z in out]

    # -------------------------------------------------------------------------------------- clauses and counts
    def clauses(self, s):
        cl = []
        for i in range(self.n):
            lits = [(self.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1) for k in range(3)]
            cl.append(lits)
            cl.append([-x for x in lits])
        return cl

    def tallies(self, s, x):
        """(violated lines, agree per vertex) under assignment x (list of bits)"""
        lit = [[x[self.pt[i][k]] ^ s[3 * i + k] for k in range(3)] for i in range(self.n)]
        viol = sum(1 for L in lit if L[0] == L[1] == L[2])
        agree = [0] * self.V
        for v in range(self.V):
            for i, c in self.corners_at[v]:
                agree[v] += lit[i][(c + 1) % 3] == lit[i][(c + 2) % 3]
        return viol, agree

    def count_identity(self, s, x):
        D = set(self.even_faces(s))
        viol, agree = self.tallies(s, x)
        par = all(agree[v] % 2 == (self.d[v] + self.flip(s)[v]) % 2 for v in range(self.V))
        E = sum(a // 2 for a in agree)
        return par and 2 * (viol - E) == self.chi - len(D), viol, E

    def sat(self, s, solver="cadical153"):
        from pysat.solvers import Solver
        with Solver(name=solver, bootstrap_with=self.clauses(s)) as so:
            r = so.solve()
            return bool(r), (so.get_model() if r else None)

    def brute_count(self, s):
        """number of satisfying assignments, by enumeration (n <= 24)"""
        n = self.n
        assert n <= 24
        X = np.arange(1 << n, dtype=np.int64)
        ok = np.ones(1 << n, dtype=bool)
        for i in range(n):
            ys = [((X >> self.pt[i][k]) & 1) ^ s[3 * i + k] for k in range(3)]
            ok &= ~((ys[0] == ys[1]) & (ys[1] == ys[2]))
        return int(ok.sum())

    # -------------------------------------------------------------------------------------- the matching side
    def matchings(self, D=(), limit=None):
        """every map A: line -> corner whose vertex degrees are odd off D and even on D (perfect matchings of the lines with the
        vertices off D when chi = |D|), by backtracking with parity pruning"""
        D = set(D)
        need = [0 if v in D else 1 for v in range(self.V)]
        lines_at = defaultdict(set)
        for v in range(self.V):
            for i, c in self.corners_at[v]:
                lines_at[v].add(i)
        last = {}
        for v in range(self.V):
            last[v] = max(lines_at[v])
        closes = defaultdict(list)
        for v in range(self.V):
            closes[last[v]].append(v)
        vert_of = [[self.S.vert[self.lines[i]][c] for c in range(3)] for i in range(self.n)]
        deg = [0] * self.V
        A, out = [None] * self.n, []

        def rec(i):
            if limit is not None and len(out) >= limit:
                return
            if i == self.n:
                out.append(tuple(A))
                return
            for c in range(3):
                v = vert_of[i][c]
                deg[v] += 1
                A[i] = c
                if all(deg[w] % 2 == need[w] for w in closes[i]):
                    rec(i + 1)
                deg[v] -= 1
            A[i] = None
        rec(0)
        return out

    def assignment_from(self, A, s):
        """the assignments whose agreeing corners are exactly A's (one per line): solve x_a + x_b = s_a + s_b + [corner not in A]"""
        par, rel = list(range(self.n)), [0] * self.n

        def find(a):
            if par[a] == a:
                return a, 0
            r, d = find(par[a])
            par[a], rel[a] = r, rel[a] ^ d
            return r, rel[a]
        for i in range(self.n):
            for c in range(3):
                k1, k2 = (c + 1) % 3, (c + 2) % 3
                a, b = self.pt[i][k1], self.pt[i][k2]
                want = s[3 * i + k1] ^ s[3 * i + k2] ^ (A[i] != c)
                ra, da = find(a)
                rb, db = find(b)
                if ra == rb:
                    if da ^ db != want:
                        return None
                else:
                    par[ra], rel[ra] = rb, da ^ db ^ want
        x = [find(a)[1] for a in range(self.n)]
        return x


# ------------------------------------------------------------------------------------------------ holonomy on lattice quotients
def edge_index(K):
    """canonical side midpoint -> B-edge index (line i, side k -> 3i + k), for lattice quotients"""
    S = K.S
    out = {}
    for i, l in enumerate(K.lines):
        P = S.tris[l][1]
        for k in range(3):
            b, c = P[(k + 1) % 3], P[(k + 2) % 3]
            mid = ((b[0] + c[0]) // 2, (b[1] + c[1]) // 2)
            out[S.canon(mid)[0]] = 3 * i + k
    assert len(out) == 3 * K.n
    return out


def staircase(i0, j0, di, dj):
    """the B-edges (as cover sides: (down triangle corners, side k)) crossed walking from up(i0, j0) to up(i0 + di, j0 + dj): a +i step
    crosses sides 1 and 2 of down(i, j) (turning at its corner (i+1, j)), a +j step sides 1 and 0 (turning at (i, j+1))"""
    out, i, j = [], i0, j0
    for _ in range(abs(di)):
        if di > 0:
            out += [(down(i, j), 1), (down(i, j), 2)]
            i += 1
        else:
            out += [(down(i - 1, j), 1), (down(i - 1, j), 2)]
            i -= 1
    for _ in range(abs(dj)):
        if dj > 0:
            out += [(down(i, j), 1), (down(i, j), 0)]
            j += 1
        else:
            out += [(down(i, j - 1), 1), (down(i, j - 1), 0)]
            j -= 1
    return out


def holonomy(K, s, di, dj, idx=None):
    """the sum of the signs crossed walking from up(0, 0) to up(di, dj) in the cover (a closed loop when the two are identified)"""
    idx = idx or edge_index(K)
    tot = 0
    for P, k in staircase(0, 0, di, dj):
        b, c = P[(k + 1) % 3], P[(k + 2) % 3]
        mid = ((b[0] + c[0]) // 2, (b[1] + c[1]) // 2)
        tot ^= s[idx[K.S.canon(mid)[0]]]
    return tot


def loops(S):
    """the cover displacements of up(0, 0) along two loops generating H_1: (p, 0) and (q, r) on torus(p, q, r); the translation
    (m, 0) and the glide's image up(c - 1, h) of up(0, 0) on klein(m, h, c)"""
    if S.kind == "torus":
        p, q, r = S.params
        return [(p, 0), (q, r)]
    m, h, c = S.params
    return [(m, 0), (c - 1, h)]


def labelled_classes(K):
    """the signings 0 + z over the classes z, each labelled by its holonomy along loops(S); the trivial signing is Kasteleyn when
    every vertex has degree 6"""
    assert all(d == 3 for d in K.d)
    idx = edge_index(K)
    Z = K.classes()
    out = {}
    for a in itertools.product((0, 1), repeat=len(Z)):
        s = [0] * (3 * K.n)
        for ai, z in zip(a, Z):
            if ai:
                s = [u ^ w for u, w in zip(s, z)]
        lab = tuple(holonomy(K, s, di, dj, idx) for di, dj in loops(K.S))
        assert lab not in out
        out[lab] = s
    return out


# ------------------------------------------------------------------------------------------------ F2 helpers


class Basis:
    """an incremental F2 basis of bit rows, by leading bit"""
    def __init__(self):
        self.rows = {}

    def reduce(self, v):
        while v:
            h = v.bit_length() - 1
            if h in self.rows:
                v ^= self.rows[h]
            else:
                return v
        return 0

    def add(self, v):
        v = self.reduce(v)
        if v:
            self.rows[v.bit_length() - 1] = v
            return True
        return False


def solve_f2(rows, target, ncols):
    """a solution of rows . s = target over F2 (rows as bit masks over ncols unknowns), or None"""
    piv = {}
    for r, t in zip(rows, target):
        a = r | (t << ncols)
        while a & ((1 << ncols) - 1):
            h = (a & ((1 << ncols) - 1)).bit_length() - 1
            if h in piv:
                a ^= piv[h]
            else:
                piv[h] = a
                break
        else:
            if a >> ncols:
                return None
    # back substitution: process pivots from low to high
    sol = 0
    for h in sorted(piv):
        a = piv[h]
        rest = a & ((1 << h) - 1)
        val = (a >> ncols) & 1
        val ^= bin(rest & sol).count("1") & 1
        if val:
            sol |= 1 << h
    return sol


def kernel_f2(rows, ncols):
    """a basis of {s : rows . s = 0}"""
    piv = {}
    for r in rows:
        a = r
        while a:
            h = a.bit_length() - 1
            if h in piv:
                a ^= piv[h]
            else:
                piv[h] = a
                break
    # reduce fully (each pivot row's lower pivots eliminated)
    for h in sorted(piv):
        for h2 in sorted(piv):
            if h2 > h and (piv[h2] >> h) & 1:
                piv[h2] ^= piv[h]
    free = [c for c in range(ncols) if c not in piv]
    out = []
    for f in free:
        v = 1 << f
        for h, a in piv.items():
            if (a >> f) & 1:
                v |= 1 << h
        out.append(v)
    return out


def random_assignment(n, rng):
    return [rng.randrange(2) for _ in range(n)]


def hnf_sublattices(N):
    """every sublattice of Z^2 of index N, as Hermite normal forms (p, q, r) with p*r = N, 0 <= q < p"""
    out = []
    for p in range(1, N + 1):
        if N % p == 0:
            r = N // p
            for q in range(p):
                out.append((p, q, r))
    return out


# ------------------------------------------------------------------------------------------------ lattice tori: the criterion
def hex_norm(a, b):
    """graph distance from 0 to a*e1 + b*e2 in the triangular lattice; also the width of the slope triangle in direction (a, b)"""
    return max(abs(a), abs(b), abs(a + b))


def short_vectors(p, q, r, bound=4):
    """nonzero vectors x*(p, 0) + y*(q, r) with |x|, |y| <= bound, as (norm^2, (a, b)) with norm^2 = a^2 + ab + b^2"""
    out = []
    for x in range(-bound, bound + 1):
        for y in range(-bound, bound + 1):
            if (x, y) != (0, 0):
                a, b = x * p + y * q, y * r
                out.append((a * a + a * b + b * b, (a, b)))
    return sorted(out)


def torus_kind(p, q, r):
    """degenerate (a unit vector in L: some line repeats a point), thin (a vector of norm^2 3: circumference sqrt 3), or other"""
    vs = short_vectors(p, q, r)
    if vs[0][0] == 1:
        return "degenerate"
    if any(nn == 3 for nn, _ in vs):
        return "thin"
    return "other"


def satisfiable_classes(p, q, r):
    """the holonomy labels (omega(p, 0), omega(q, r)) of the classes the criterion makes satisfiable: one for every integer point (s, t)
    of the triangle conv{(0, 0), (p, q), (0, -r)}, namely ((p + s) mod 2, (q + r + t) mod 2). The triangle is the slope triangle
    {G : G(1, 0) >= 0, G(0, -1) >= 0, G(1, 0) + G(0, -1) <= 1} in the coordinates G(1, 0) = s/p, G(q, r) = t of Hom(L, Z)."""
    from fractions import Fraction
    import math
    out = set()
    for s in range(0, p + 1):
        lo = Fraction(-r) + Fraction(s * (q + r), p)
        hi = Fraction(s * q, p)
        for t in range(math.ceil(lo), math.floor(hi) + 1):
            out.add(((p + s) % 2, (q + r + t) % 2))
    return out


FANO_TORI = [(7, 2, 1), (7, 4, 1)]


# ------------------------------------------------------------------------------------------------ thin tori are cyclic chains
def chain(K):
    """for a thin torus: order the points by a slice functional phi (vanishing on a norm^2 3 vector of L): phi(i, j) = i - j, i + 2j or
    2i + j for w = (1, 1), (2, -1), (-1, 2). Returns (slice of each point, for each line its middle slice c and its sides' offsets)."""
    p, q, r = K.S.params
    N = p * r
    w = next(v for nn, v in short_vectors(p, q, r) if nn == 3)
    phis = {(1, 1): (1, -1), (-1, -1): (1, -1), (2, -1): (1, 2), (-2, 1): (1, 2), (-1, 2): (2, 1), (1, -2): (2, 1)}
    fa, fb = phis[w]
    slice_of = []
    for t in K.points:
        X, Y = K.S.tris[t][1][0]
        slice_of.append((fa * X // 6 + fb * Y // 6) % N)
    lines = []
    for i in range(K.n):
        sl = [slice_of[K.pt[i][k]] for k in range(3)]
        for c in sl:
            offs = [((x - c + 1) % N) - 1 for x in sl]
            if sorted(offs) == [-1, 0, 1]:
                lines.append((c, [(offs[k], k) for k in range(3)]))
                break
        else:
            return None
    return slice_of, lines


def find_violated_line(K, s, x, ch=None):
    """the binary search on a thin torus: with O(log n) queries of x, return (a violated line, the queried points). Invariant: an arc
    [a, b] of slices whose lines (middle slices a+1..b-1) cannot all hold given x on slices a, a+1, b-1, b."""
    slice_of, lines = ch or chain(K)
    N = len(slice_of)
    at = {sl: i for i, sl in enumerate(slice_of)}
    by_c = {}
    for i, (c, offs) in enumerate(lines):
        by_c[c] = (i, offs)
    queried = {}

    def ask(idx):
        pnt = at[idx % N]
        queried[pnt] = x[pnt]
        return x[pnt]

    def holds(c, val):
        i, offs = by_c[c % N]
        lit = [val(c + o) ^ s[3 * i + k] for o, k in offs]
        return not (lit[0] == lit[1] == lit[2])

    def arc_ok(a, b, bv):
        """is there y on slices a..b with the boundary values bv (dict index -> value) satisfying lines a+1..b-1"""
        states = {(bv[a], bv[a + 1])}
        for i in range(a + 1, b):
            nxt = set()
            for (u, v) in states:
                for w in ((bv[i + 1],) if i + 1 in bv else (0, 1)):
                    vals = {i - 1: u, i: v, i + 1: w}
                    if holds(i, lambda j: vals[j]):
                        nxt.add((v, w))
            states = nxt
        return (bv[b - 1], bv[b]) in states

    a, b = 0, N + 1
    bv = {0: ask(0), 1: ask(1), N: x[at[0]], N + 1: x[at[1 % N]]}
    assert not arc_ok(a, b, bv)
    while b - a > 6:
        m = (a + b) // 2
        bv[m], bv[m + 1] = ask(m), ask(m + 1)
        if not arc_ok(a, m + 1, bv):
            b = m + 1
        else:
            assert not arc_ok(m, b, bv)
            a = m
    for idx in range(a, b + 1):
        bv[idx] = ask(idx)
    for c in range(a + 1, b):
        if not holds(c, lambda j: bv[j]):
            return by_c[c % N][0], queried
    return None, queried
