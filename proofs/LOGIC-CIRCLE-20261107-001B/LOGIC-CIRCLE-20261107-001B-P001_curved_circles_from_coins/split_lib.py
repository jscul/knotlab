"""Curved circles from coins (ticket LOGIC-CIRCLE-20261107-001B).

The random split law: Z^2 with one diagonal in each unit square, NE with probability p independently, NW otherwise. Its plane
dual is three-regular: the square parity law with each four-place knot split into two three-place knots joined by a new
variable, the split's orientation set by the coin. The law's knots are the cycles of this graph, so bond distance is the least
cycle through two edges, minus one. Also: the Poisson-Voronoi law (dual: the Delaunay graph)."""
import heapq, math
import numpy as np
from collections import deque

def environment(L, p, rng):
    return (rng.random((L, L)) < p).astype(np.int8)   # face (i, j) = [i, i+1] x [j, j+1]; 1 = NE diagonal

def graph(D):
    """Vertices (x, y), 0 <= x, y <= L; edges: axis edges and one diagonal per face. Returns adj, elist, index."""
    L = D.shape[0]
    idx = lambda x, y: x * (L + 1) + y
    n = (L + 1) ** 2
    adj = [[] for _ in range(n)]
    elist = []
    def add(a, b):
        k = len(elist); elist.append((a, b)); adj[a].append((b, k)); adj[b].append((a, k))
    for x in range(L + 1):
        for y in range(L + 1):
            if x < L: add(idx(x, y), idx(x + 1, y))
            if y < L: add(idx(x, y), idx(x, y + 1))
    for i in range(L):
        for j in range(L):
            if D[i, j]: add(idx(i, j), idx(i + 1, j + 1))
            else:       add(idx(i + 1, j), idx(i, j + 1))
    return adj, elist, idx

def bfs(adj, s):
    dist = [-1] * len(adj); dist[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for v, _ in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1; q.append(v)
    return dist

def chain_table(F):
    """F: 0/1 array over faces (rows = first coordinate). T[a, b] = longest strictly increasing chain of 1-faces in [0, a) x [0, b)."""
    A, B = F.shape
    T = np.zeros((A + 1, B + 1), dtype=np.int32)
    for a in range(1, A + 1):
        row = F[a - 1]
        prev, cur = T[a - 1], T[a]
        for b in range(1, B + 1):
            cur[b] = max(prev[b], cur[b - 1], prev[b - 1] + row[b - 1])
    return T

def formula_distances(D, u):
    """Predicted distance from vertex u = (ux, uy) to every vertex, by quadrant: |dx| + |dy| - longest strict chain of
    correctly oriented faces in the box [u, w]."""
    L = D.shape[0]
    ux, uy = u
    out = np.zeros((L + 1, L + 1), dtype=np.int64)
    # NE quadrant (w >= u): NE faces (i, j) with ux <= i < wx, uy <= j < wy, chain increasing in both
    T = chain_table(D[ux:, uy:])
    for wx in range(ux, L + 1):
        for wy in range(uy, L + 1):
            out[wx, wy] = (wx - ux) + (wy - uy) - T[wx - ux, wy - uy]
    # SW quadrant (w <= u): NE faces in [w, u), chain read backwards
    F = D[:ux, :uy][::-1, ::-1]
    T = chain_table(F)
    for wx in range(0, ux + 1):
        for wy in range(0, uy + 1):
            out[wx, wy] = (ux - wx) + (uy - wy) - T[ux - wx, uy - wy]
    # NW quadrant (wx <= ux, wy >= uy): NW faces, chain increasing in (-x, +y)
    NW = 1 - D
    F = NW[:ux, uy:][::-1, :]
    T = chain_table(F)
    for wx in range(0, ux + 1):
        for wy in range(uy, L + 1):
            out[wx, wy] = (ux - wx) + (wy - uy) - T[ux - wx, wy - uy]
    # SE quadrant (wx >= ux, wy <= uy): NW faces, chain increasing in (+x, -y)
    F = NW[ux:, :uy][:, ::-1]
    T = chain_table(F)
    for wx in range(ux, L + 1):
        for wy in range(0, uy + 1):
            out[wx, wy] = (wx - ux) + (uy - wy) - T[wx - ux, uy - wy]
    return out

def g_strict(s, t, q):
    """Seppalainen's limit for the longest strictly increasing chain in [0, s n] x [0, t n] with density q, divided by n."""
    if q <= 0: return 0.0
    if q >= 1: return min(s, t)
    if q * s <= t <= s / q:
        return (2 * math.sqrt(q * s * t) - q * (s + t)) / (1 - q)
    return min(s, t)

def c_shape(x, y, p):
    q = p if x * y >= 0 else 1 - p
    s, t = abs(x), abs(y)
    return s + t - g_strict(s, t, q)


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


def voronoi_dual(W, rng):
    """Delaunay graph of a Poisson process of intensity 1 in [0, W]^2: the plane dual of the Voronoi law (three-place knots)."""
    from scipy.spatial import Delaunay
    m = rng.poisson(W * W)
    pts = rng.random((m, 2)) * W
    tri = Delaunay(pts)
    es = set()
    for s in tri.simplices:
        for a, b in ((s[0], s[1]), (s[1], s[2]), (s[0], s[2])):
            es.add((min(a, b), max(a, b)))
    elist = sorted(es)
    adj = [[] for _ in range(m)]
    for k, (a, b) in enumerate(elist):
        adj[a].append((b, k)); adj[b].append((a, k))
    return adj, elist, pts, tri

def circle_pi(p, m=40000):
    """Golab's pi of the law's circle {c_p <= 1}: half its perimeter measured in its own norm c_p (fine polygonal approximation)."""
    pts = []
    for k in range(m):
        t = 2 * math.pi * k / m
        u = (math.cos(t), math.sin(t))
        r = 1 / c_shape(u[0], u[1], p)
        pts.append((r * u[0], r * u[1]))
    per = 0.0
    for k in range(m):
        a, b = pts[k], pts[(k + 1) % m]
        per += c_shape(b[0] - a[0], b[1] - a[1], p)
    return per / 2
