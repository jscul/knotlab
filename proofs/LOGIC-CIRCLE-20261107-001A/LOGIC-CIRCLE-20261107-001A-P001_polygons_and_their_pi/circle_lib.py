"""Circles of parity laws on plane graphs (ticket LOGIC-CIRCLE-20261107-001A).

A parity law on a plane graph G has one parity knot per vertex and one variable per edge; its knots are the bonds of G,
i.e. the cycles of the plane dual G*. Bond distance between two variables is the least such cycle through both dual edges,
minus one. This module builds the Archimedean tilings and their duals, the velocity polygons of periodic graphs, Golab's
self-perimeter pi, minimum cycles through two edges, and laws on line arrangements (de Bruijn grids)."""
from __future__ import annotations
import heapq, math, itertools
from fractions import Fraction
import numpy as np

S3 = math.sqrt(3.0)
S2 = math.sqrt(2.0)

# ---------------------------------------------------------------- periodic graphs

class PeriodicGraph:
    """A doubly periodic graph: vertices 0..n-1 in the unit cell, edges (u, v, d) joining u in cell 0 to v in cell d (lattice coords)."""
    def __init__(self, name, a1, a2, pos, edges):
        self.name, self.a1, self.a2 = name, np.array(a1, float), np.array(a2, float)
        self.pos = [np.array(p, float) for p in pos]
        self.edges = edges  # list of (u, v, (dx, dy)), each undirected edge once
        self.n = len(pos)

    def cart(self, v, d):
        return self.pos[v] + d[0] * self.a1 + d[1] * self.a2

    def darts(self):
        out = {u: [] for u in range(self.n)}
        for i, (u, v, d) in enumerate(self.edges):
            out[u].append((v, d, i, +1))
            out[v].append((u, (-d[0], -d[1]), i, -1))
        return out

def unit_distance_graph(name, a1, a2, pos, length=1.0, tol=1e-6, reach=3):
    a1, a2 = np.array(a1, float), np.array(a2, float)
    pos = [np.array(p, float) for p in pos]
    edges, seen = [], set()
    for u in range(len(pos)):
        for v in range(len(pos)):
            for dx in range(-reach, reach + 1):
                for dy in range(-reach, reach + 1):
                    if u == v and dx == 0 and dy == 0:
                        continue
                    q = pos[v] + dx * a1 + dy * a2
                    if abs(np.linalg.norm(q - pos[u]) - length) < tol:
                        key = (u, v, dx, dy)
                        rev = (v, u, -dx, -dy)
                        if rev in seen or key in seen:
                            continue
                        seen.add(key)
                        edges.append((u, v, (dx, dy)))
    return PeriodicGraph(name, a1, a2, pos, edges)

def degrees(g):
    deg = [0] * g.n
    for u, v, d in g.edges:
        deg[u] += 1; deg[v] += 1
    return deg

def faces(g):
    """Trace faces with the rotation system given by the drawing. Returns (face list, dart->(face, offset)).
    Each face: list of (u, cell offset) around it; dart key (u, v, d) with u in cell 0."""
    out = g.darts()
    rot = {}
    for u, lst in out.items():
        lst = sorted(lst, key=lambda t: math.atan2(*(g.cart(t[0], t[1]) - g.pos[u])[::-1]))
        rot[u] = lst
    def nxt(u, v, d):
        # arrived at v (cell d) along dart u->v; next dart = clockwise neighbour of the reverse dart v->u around v
        lst = rot[v]
        back = (-d[0], -d[1])
        k = next(i for i, t in enumerate(lst) if t[0] == u and t[1] == back)
        t = lst[(k - 1) % len(lst)]
        return v, t[0], t[1]
    owner, flist = {}, []
    for u in range(g.n):
        for (v, d, _, _) in rot[u]:
            if (u, v, d) in owner:
                continue
            fid = len(flist)
            walk, off = [], (0, 0)
            cu, cv, cd = u, v, d
            while True:
                key = (cu, cv, cd)
                owner[key] = (fid, (-off[0], -off[1]))
                walk.append((cu, off))
                off = (off[0] + cd[0], off[1] + cd[1])
                cu, cv, cd = nxt(cu, cv, cd)
                if (cu, cv, cd) == (u, v, d) and off == (0, 0):
                    break
                if len(walk) > 200:
                    raise RuntimeError("face did not close")
            flist.append(walk)
    return flist, owner

def face_sizes_at_vertices(g):
    flist, owner = faces(g)
    out = g.darts()
    conf = []
    for u in range(g.n):
        lst = sorted(out[u], key=lambda t: math.atan2(*(g.cart(t[0], t[1]) - g.pos[u])[::-1]))
        conf.append(tuple(len(flist[owner[(u, t[0], t[1])][0]]) for t in lst))
    return conf

def canonical_conf(c):
    rots = [c[i:] + c[:i] for i in range(len(c))]
    rots += [tuple(reversed(r)) for r in rots]
    return min(rots)

def dual(g):
    flist, owner = faces(g)
    # face positions: centroid of the canonical instance
    fpos = []
    for walk in flist:
        pts = [g.cart(u, off) for u, off in walk]
        fpos.append(np.mean(pts, axis=0))
    # for each dart key (u,v,d) with u in cell 0: owner gives (face, shift) such that the face instance containing
    # this dart is the canonical face translated by shift.
    edges = []
    for i, (u, v, d) in enumerate(g.edges):
        f1, s1 = owner[(u, v, d)]
        f2, s2 = owner[(v, u, (-d[0], -d[1]))]
        s2 = (s2[0] + d[0], s2[1] + d[1])  # reverse dart's tail v sits in cell d
        edges.append((f1, f2, (s2[0] - s1[0], s2[1] - s1[1])))
    h = PeriodicGraph("dual of " + g.name, g.a1, g.a2, fpos, edges)
    return h

# ---------------------------------------------------------------- velocity polygon

def simple_cycles(g, cap=2_000_000):
    """Yield (displacement, length) for every simple cycle of the quotient multigraph, both orientations."""
    out = g.darts()
    n = g.n
    count = 0
    for s in range(n):
        # DFS over darts through vertices > s, closing at s
        def rec(v, disp, length, visited, used_edges):
            nonlocal count
            for (w, d, ei, sgn) in out[v]:
                if ei in used_edges:
                    continue
                nd = (disp[0] + d[0], disp[1] + d[1])
                if w == s:
                    count += 1
                    if count > cap:
                        raise RuntimeError("too many cycles")
                    yield nd, length + 1
                elif w > s and w not in visited:
                    yield from rec(w, nd, length + 1, visited | {w}, used_edges | {ei})
        yield from rec(s, (0, 0), 0, frozenset([s]), frozenset())

def convex_hull(points):
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]

def velocity_polygon(g):
    vel = set()
    for disp, length in simple_cycles(g):
        if disp != (0, 0):
            vel.add((Fraction(disp[0], length), Fraction(disp[1], length)))
    return convex_hull(list(vel))

def facets(poly):
    """For a polygon containing 0 in its interior (vertices ccw), the normals n_i with <n_i, x> = 1 on edge i."""
    out = []
    m = len(poly)
    for i in range(m):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % m]
        det = x1 * y2 - x2 * y1
        # solve a x1 + b y1 = 1, a x2 + b y2 = 1
        a = (y2 - y1) / det
        b = (x1 - x2) / det
        out.append((a, b))
    return out

def gauge(poly_facets, x):
    return max(a * x[0] + b * x[1] for a, b in poly_facets)

def self_pi(poly):
    """Golab's pi of the normed plane whose unit ball is poly: half the perimeter of poly measured in its own norm."""
    fs = facets(poly)
    m = len(poly)
    per = sum(gauge(fs, (poly[(i + 1) % m][0] - poly[i][0], poly[(i + 1) % m][1] - poly[i][1])) for i in range(m))
    return per / 2

# ---------------------------------------------------------------- patches and minimum cycles

def patch(g, radius):
    """Finite piece of the periodic graph: cells with |dx|,|dy| <= radius. Returns (index, adjacency, positions, edge list)."""
    idx, pos = {}, []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            for v in range(g.n):
                idx[(v, dx, dy)] = len(pos)
                pos.append(g.cart(v, (dx, dy)))
    adj = [[] for _ in pos]
    elist = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            for (u, v, d) in g.edges:
                a = idx.get((u, dx, dy)); b = idx.get((v, dx + d[0], dy + d[1]))
                if a is None or b is None:
                    continue
                k = len(elist)
                elist.append((a, b))
                adj[a].append((b, k)); adj[b].append((a, k))
    return idx, adj, np.array(pos), elist

def min_cycle_through(adj, elist, e, f):
    """Length of a shortest cycle containing edges e and f (indices into elist): two vertex-disjoint paths joining the
    ends of e to the ends of f, avoiding e and f (min-cost flow, successive shortest paths with Dijkstra potentials)."""
    a, b = elist[e]; c, d = elist[f]
    if len({a, b, c, d}) < 4:
        raise ValueError("edges must not share a vertex")
    n = len(adj)
    N = 2 * n + 2
    S, T = 2 * n, 2 * n + 1
    head = [[] for _ in range(N)]  # arcs: [to, cap, cost, rev]
    def add(u, v, cap, cost):
        head[u].append([v, cap, cost, len(head[v])])
        head[v].append([u, 0, -cost, len(head[u]) - 1])
    for v in range(n):
        add(2 * v, 2 * v + 1, 1, 0)
    for k, (x, y) in enumerate(elist):
        if k == e or k == f:
            continue
        add(2 * x + 1, 2 * y, 1, 1)
        add(2 * y + 1, 2 * x, 1, 1)
    add(S, 2 * a, 1, 0); add(S, 2 * b, 1, 0)
    add(2 * c + 1, T, 1, 0); add(2 * d + 1, T, 1, 0)
    pot = [0] * N
    flow = cost = 0
    INF = float("inf")
    while flow < 2:
        dist = [INF] * N
        prev = [None] * N
        dist[S] = 0
        pq = [(0, S)]
        while pq:
            du, u = heapq.heappop(pq)
            if du > dist[u]:
                continue
            for i, (v, cap, c, _) in enumerate(head[u]):
                if cap > 0:
                    nd = du + c + pot[u] - pot[v]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev[v] = (u, i)
                        heapq.heappush(pq, (nd, v))
        if dist[T] == INF:
            return None
        for v in range(N):
            if dist[v] < INF:
                pot[v] += dist[v]
        v = T
        while v != S:
            u, i = prev[v]
            head[u][i][1] -= 1
            head[v][head[u][i][3]][1] += 1
            cost += head[u][i][2]
            v = u
        flow += 1
    return cost + 2

# ---------------------------------------------------------------- the Archimedean tilings

def _honeycomb_frame(L):
    a1 = np.array([S3 * L, 0.0]); a2 = np.array([S3 * L / 2, 1.5 * L])
    A = np.array([0.0, 0.0]); B = np.array([0.0, L])
    nbrs = [B, B - a2, B - a2 + a1]
    us = [(q - A) / np.linalg.norm(q - A) for q in nbrs]
    return a1, a2, A, B, us

def perp(u):
    return np.array([-u[1], u[0]])

def square():
    return unit_distance_graph("4.4.4.4 (square)", (1, 0), (0, 1), [(0, 0)])

def triangular():
    return unit_distance_graph("3.3.3.3.3.3 (triangular)", (1, 0), (0.5, S3 / 2), [(0, 0)])

def honeycomb():
    return unit_distance_graph("6.6.6 (honeycomb)", (S3, 0), (S3 / 2, 1.5), [(0, 0), (0, 1)])

def kagome():
    return unit_distance_graph("3.6.3.6 (kagome)", (2, 0), (1, S3), [(0, 0), (1, 0), (0.5, S3 / 2)])

def truncated_hexagonal():
    a1, a2, A, B, us = _honeycomb_frame(1 + 2 / S3)
    pts = [A + u / S3 for u in us] + [B - u / S3 for u in us]
    return unit_distance_graph("3.12.12 (truncated hexagonal)", a1, a2, pts)

def truncated_square():
    s = 1 + S2
    r = 1 / S2
    return unit_distance_graph("4.8.8 (truncated square)", (s, 0), (0, s), [(r, 0), (0, r), (-r, 0), (0, -r)])

def truncated_trihexagonal():
    a1, a2, A, B, us = _honeycomb_frame(1 + S3)
    pts = []
    for C, sgn in ((A, 1), (B, -1)):
        for u in us:
            u = sgn * u
            pts += [C + (S3 / 2) * u + 0.5 * perp(u), C + (S3 / 2) * u - 0.5 * perp(u)]
    return unit_distance_graph("4.6.12 (truncated trihexagonal)", a1, a2, pts)

def rhombitrihexagonal():
    a1, a2, A, B, us = _honeycomb_frame(1 + 1 / S3)
    pts = [A - u / S3 for u in us] + [B + u / S3 for u in us]
    return unit_distance_graph("3.4.6.4 (rhombitrihexagonal)", a1, a2, pts)

def snub_square():
    c = (1 + S3) / S2
    r = 1 / S2
    th = math.radians(15)
    pts = [(r * math.cos(math.pi / 4 + th + j * math.pi / 2), r * math.sin(math.pi / 4 + th + j * math.pi / 2)) for j in range(4)]
    return unit_distance_graph("3.3.4.3.4 (snub square)", (c, 0), (0, c), pts)

def elongated_triangular():
    return unit_distance_graph("3.3.3.4.4 (elongated triangular)", (1, 0), (0.5, 1 + S3 / 2), [(0, 0), (0, 1)])

def snub_hexagonal():
    a = np.array([1.0, 0.0]); b = np.array([0.5, S3 / 2])
    u = 2 * a + b; v = -a + 3 * b
    M = np.array([u, v]).T
    pts = []
    for i in range(-4, 5):
        for j in range(-4, 5):
            p = i * a + j * b
            s, t = np.linalg.solve(M, p)
            if -1e-9 <= s < 1 - 1e-9 and -1e-9 <= t < 1 - 1e-9 and not (abs(s) < 1e-9 and abs(t) < 1e-9):
                pts.append(p)
    assert len(pts) == 6, len(pts)
    return unit_distance_graph("3.3.3.3.6 (snub hexagonal)", u, v, pts)

ARCHIMEDEAN = [square, triangular, honeycomb, kagome, truncated_hexagonal, truncated_square, truncated_trihexagonal,
               rhombitrihexagonal, snub_square, elongated_triangular, snub_hexagonal]
EXPECTED = {"4.4.4.4": (4, 4, 4, 4), "3.3.3.3.3.3": (3,) * 6, "6.6.6": (6, 6, 6), "3.6.3.6": (3, 6, 3, 6),
            "3.12.12": (3, 12, 12), "4.8.8": (4, 8, 8), "4.6.12": (4, 6, 12), "3.4.6.4": (3, 4, 6, 4),
            "3.3.4.3.4": (3, 3, 4, 3, 4), "3.3.3.4.4": (3, 3, 3, 4, 4), "3.3.3.3.6": (3, 3, 3, 3, 6)}

# ---------------------------------------------------------------- laws on line arrangements

def grid_law(n, W, gammas, angles=None):
    """The law with a parity knot at each crossing of n families of unit-spaced parallel lines <z, N_j> + gamma_j in Z,
    restricted to crossings within distance W of the origin. Cells are named by de Bruijn's integer vectors."""
    if angles is None:
        angles = [math.pi * j / n for j in range(n)]
    N = [np.array([math.cos(a), math.sin(a)]) for a in angles]
    K = lambda z: tuple(math.ceil(float(N[m] @ z) + gammas[m]) for m in range(n))
    cells, adj, elist, epos, eline, seen = {}, [], [], [], [], {}
    def cid(key):
        if key not in cells:
            cells[key] = len(adj); adj.append([])
        return cells[key]
    for j in range(n):
        for l in range(j + 1, n):
            M = np.array([N[j], N[l]])
            for kj in range(-W - 2, W + 3):
                for kl in range(-W - 2, W + 3):
                    z = np.linalg.solve(M, np.array([kj - gammas[j], kl - gammas[l]]))
                    if np.linalg.norm(z) > W:
                        continue
                    base = list(K(z))
                    # cells around the crossing: coordinate j in {kj, kj+1}, l in {kl, kl+1}; others fixed (generic gammas)
                    four = {}
                    for dj in (0, 1):
                        for dl in (0, 1):
                            key = base[:]; key[j] = kj + dj; key[l] = kl + dl
                            four[(dj, dl)] = tuple(key)
                    for (p, q, fam, k) in (((0, 0), (1, 0), j, kj), ((0, 1), (1, 1), j, kj), ((0, 0), (0, 1), l, kl), ((1, 0), (1, 1), l, kl)):
                        a, b = cid(four[p]), cid(four[q])
                        e = (min(a, b), max(a, b))
                        if e in seen:
                            # the same segment seen from its other end: record the midpoint
                            i = seen[e]; epos[i] = (epos[i] + z) / 2
                            continue
                        seen[e] = len(elist)
                        elist.append(e); epos.append(z.copy()); eline.append((fam, k))
                        adj[a].append((b, seen[e])); adj[b].append((a, seen[e]))
    keys = [None] * len(adj)
    for key, i in cells.items():
        keys[i] = key
    return dict(n=n, N=N, gammas=gammas, adj=adj, elist=elist, epos=np.array(epos), eline=eline, keys=keys)

def separating(G, s, t):
    """Number of lines strictly separating segments s and t, other than the lines carrying them."""
    n = G["n"]
    (js, ks), (jt, kt) = G["eline"][s], G["eline"][t]
    ks_cells = G["keys"][G["elist"][s][0]]
    kt_cells = G["keys"][G["elist"][t][0]]
    sep = 0
    for m in range(n):
        if m != js and m != jt:
            sep += abs(ks_cells[m] - kt_cells[m])
        elif m == js and m == jt:
            sep += 0 if ks == kt else abs(ks - kt) - 1
        elif m == js:      # s lies on line (m, ks); t lies in the strip between lines K-1 and K
            Kt = kt_cells[m]
            sep += (Kt - 1 - ks) if Kt > ks else (ks - Kt)
        else:
            Ks = ks_cells[m]
            sep += (Ks - 1 - kt) if Ks > kt else (kt - Ks)
    return sep, (js, ks) == (jt, kt)


def max_mean_cycle(g, w):
    """Karp: the largest mean weight of a closed walk of the quotient multigraph, weight of a dart = w . displacement.
    Equals the support function of the velocity polygon in direction w (an independent check of the cycle enumeration)."""
    out = g.darts()
    n = g.n
    NEG = float("-inf")
    D = [[NEG] * n for _ in range(n + 1)]
    for v in range(n):
        D[0][v] = 0.0
    for k in range(1, n + 1):
        for u in range(n):
            if D[k - 1][u] == NEG:
                continue
            for (v, d, _, _) in out[u]:
                val = D[k - 1][u] + w[0] * d[0] + w[1] * d[1]
                if val > D[k][v]:
                    D[k][v] = val
    best = NEG
    for v in range(n):
        if D[n][v] == NEG:
            continue
        worst = min((D[n][v] - D[k][v]) / (n - k) for k in range(n) if D[k][v] != NEG)
        best = max(best, worst)
    return best

def bfs_from(adj, sources):
    from collections import deque
    dist = [-1] * len(adj)
    q = deque()
    for s in sources:
        dist[s] = 0; q.append(s)
    while q:
        u = q.popleft()
        for v, _ in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1; q.append(v)
    return dist
