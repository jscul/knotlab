"""The transfer of a point split by heights, for HALO-FORCING-20261103-001B.

Q is a plane knot space H with Kasteleyn signs, split at a point z into three ports (one per line through z). Q is a plane matching
system: its solutions up to complement are the perfect matchings of lines to faces (the three faces at z merge into one odd face F0).
Heights: fix a reference matching mu0; crossing the edge of the line-face graph at the corner of face f at line K, between incidences p
(before K along f) and q (after), the height jumps from p's region to q's by mu(K, f) - mu0(K, f); every point has its own region.
The heights of matchings are exactly the integer solutions of -mu0(e) <= c(q) - c(p) <= 1 - mu0(e), and a point's value relative to
another, compared with mu0's solution, is the parity of their height difference.

R(L), the set of (port pattern, L pattern) pairs that occur, is decided by parity feasibility: fix L's matched face (one of three); the
projection of the height set onto the six regions of interest is cut out by the shortest-path distances between them; a parity vector is
feasible iff halving the constraints leaves no negative cycle."""
import collections
import heapq
import itertools

import networkx as nx


def faces_with_corners(H):
    g = nx.Graph()
    g.add_edges_from((("p", p), ("l", k)) for k, L in enumerate(H) for p in L)
    ok, emb = nx.check_planarity(g)
    assert ok
    seen, faces = set(), []
    for v, w in emb.edges():
        if (v, w) not in seen:
            faces.append(emb.traverse_face(v, w, mark_half_edges=seen))
    corners = []
    for fi, f in enumerate(faces):
        for i, v in enumerate(f):
            if v[0] == "l":
                corners.append((v[1], fi, f[i - 1][1], f[(i + 1) % len(f)][1]))
    return faces, corners


class Split:
    """H split at point z; ports are labelled n, n+1, n+2 in the order of the lines through z"""

    def __init__(self, H, s, n, z):
        self.H, self.s, self.n, self.z = H, s, n, z
        faces, corners = faces_with_corners(H)
        through = [k for k, L in enumerate(H) if z in L]
        self.port = {k: n + i for i, k in enumerate(through)}
        self.ports = [n + i for i in range(3)]
        at_z = {fi for fi, f in enumerate(faces) if ("p", z) in f}
        assert len(at_z) == 3
        fmap = {fi: ("F0" if fi in at_z else fi) for fi in range(len(faces))}
        self.lines = [tuple(self.port[k] if q == z else q for q in L) for k, L in enumerate(H)]
        self.edges = []                                    # (line, face, p, q) of the split
        for (k, fi, p, q) in corners:
            p2 = self.port[k] if p == z else p
            q2 = self.port[k] if q == z else q
            self.edges.append((k, fmap[fi], p2, q2))
        self.facelist = sorted({e[1] for e in self.edges}, key=str)
        assert len(self.facelist) == len(self.lines)
        # a reference perfect matching: each line chooses one corner, each face receives one (a line whose two corners lie in one face,
        # as a port's line does in F0, gives a double edge of the line-face graph; the matching chooses the corner)
        B = nx.Graph()
        B.add_nodes_from(("L", k) for k in range(len(self.lines)))
        B.add_nodes_from(("F", f) for f in self.facelist)
        for (k, f, p, q) in self.edges:
            B.add_edge(("L", k), ("F", f))
        M = nx.bipartite.maximum_matching(B, top_nodes=[("L", k) for k in range(len(self.lines))])
        self.mu0 = {}
        for k in range(len(self.lines)):
            f = M[("L", k)][1]
            self.mu0[k] = next(i for i, e in enumerate(self.edges) if e[0] == k and e[1] == f)
        assert len(self.mu0) == len(self.lines)
        self.points = sorted({q for L in self.lines for q in L})
        self.x0 = self.solution_of(self.mu0)

    def solution_of(self, mu):
        """the solution (values up to complement) of a matching mu: line -> index of its skipped corner in self.edges"""
        val = {self.points[0]: 0}
        adj = collections.defaultdict(list)
        for k, L in enumerate(self.lines):
            sg = dict(zip(L, self.s[k]))
            p, q = self.edges[mu[k]][2], self.edges[mu[k]][3]   # p and q agree (signed); the third point differs from both
            r = next(t for t in L if t not in (p, q))
            for a, b, d in ((p, q, 0), (p, r, 1), (q, r, 1)):
                rel = d ^ sg[a] ^ sg[b]
                adj[a].append((b, rel))
                adj[b].append((a, rel))
        todo = [self.points[0]]
        while todo:
            a = todo.pop()
            for b, rel in adj[a]:
                if b not in val:
                    val[b] = val[a] ^ rel
                    todo.append(b)
        return val

    def graph(self, fixed=None):
        """difference-constraint arcs (u, v, w): c(v) - c(u) <= w; fixed: {line: corner index} matched corners to impose"""
        arcs = []
        for i, (k, f, p, q) in enumerate(self.edges):
            m0 = int(self.mu0[k] == i)
            if fixed and k in fixed:
                d = int(fixed[k] == i) - m0
                arcs += [(p, q, d), (q, p, -d)]
            else:
                arcs += [(p, q, 1 - m0), (q, p, m0)]
        return arcs

    def transfer(self, L):
        """R(L): the set of (port pattern, L pattern) pairs (raw values) of the split's solutions"""
        X = list(self.lines[L])
        terms = self.ports + [q for q in X if q not in self.ports]
        out = set()
        Lcorners = [i for i, e in enumerate(self.edges) if e[0] == L]
        for phi in Lcorners:
            arcs = self.graph({L: phi})
            D = shortest(arcs, terms)
            if D is None:
                continue
            ref = terms[0]
            others = terms[1:]
            for v in itertools.product((0, 1), repeat=len(others)):
                par = dict(zip(others, v))
                par[ref] = 0
                if feasible(D, terms, par):
                    for flip in (0, 1):
                        val = {q: self.x0[q] ^ self.x0[ref] ^ par[q] ^ flip for q in terms}
                        out.add((tuple(val[y] for y in self.ports), tuple(val[q] for q in X)))
        return out


def shortest(arcs, terms):
    """distances D[a][b] = max c(b) - c(a) over the constraint system, between terminals; None if infeasible (Bellman-Ford)"""
    nodes = sorted({u for u, v, w in arcs} | {v for u, v, w in arcs})
    idx = {u: i for i, u in enumerate(nodes)}
    N = len(nodes)
    # Johnson: potentials from a virtual source
    h = [0] * N
    for _ in range(N):
        changed = False
        for u, v, w in arcs:
            if h[idx[u]] + w < h[idx[v]]:
                h[idx[v]] = h[idx[u]] + w
                changed = True
        if not changed:
            break
    else:
        return None
    adj = collections.defaultdict(list)
    for u, v, w in arcs:
        adj[idx[u]].append((idx[v], w + h[idx[u]] - h[idx[v]]))
    D = {}
    for a in terms:
        s = idx[a]
        dist = {s: 0}
        pq = [(0, s)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, 1 << 60):
                continue
            for v, w in adj[u]:
                nd = d + w
                if nd < dist.get(v, 1 << 60):
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        D[a] = {b: dist[idx[b]] - h[s] + h[idx[b]] for b in terms if idx[b] in dist}
    return D


def feasible(D, terms, par):
    """is there an integer vector x with x[b] - x[a] <= D[a][b] and x = par mod 2? (halve and look for a negative cycle)"""
    W = {a: {b: (D[a][b] - par[b] + par[a]) // 2 for b in terms if b in D[a]} for a in terms}
    dist = {a: dict(W[a]) for a in terms}
    for a in terms:
        dist[a][a] = min(dist[a].get(a, 0), 0)
    for k in terms:
        for i in terms:
            if k not in dist[i]:
                continue
            for j in terms:
                if j in dist[k] and dist[i][k] + dist[k][j] < dist[i].get(j, 1 << 60):
                    dist[i][j] = dist[i][k] + dist[k][j]
    return all(dist[a][a] >= 0 for a in terms)


def octahedral(level):
    """the dual of the octahedron subdivided level times (each triangle into four): a plane cubic bipartite graph (the triangulation is
    Eulerian: degrees 4 and 6)"""
    verts = {(1, 0, 0): 0, (-1, 0, 0): 1, (0, 1, 0): 2, (0, -1, 0): 3, (0, 0, 1): 4, (0, 0, -1): 5}
    tris = [(a, b, c) for a in (0, 1) for b in (2, 3) for c in (4, 5)]
    coords = {v: k for k, v in verts.items()}
    for _ in range(level):
        mid = {}

        def m(u, v):
            key = (min(u, v), max(u, v))
            if key not in mid:
                mid[key] = len(coords)
                coords[mid[key]] = tuple((a + b) for a, b in zip(coords[u], coords[v]))
            return mid[key]
        new = []
        for (a, b, c) in tris:
            ab, bc, ca = m(a, b), m(b, c), m(c, a)
            new += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]
        tris = new
    edge_tris = collections.defaultdict(list)
    for i, t in enumerate(tris):
        for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edge_tris[(min(u, v), max(u, v))].append(i)
    g = nx.Graph()
    for e, ts in edge_tris.items():
        assert len(ts) == 2
        g.add_edge(*ts)
    return g
