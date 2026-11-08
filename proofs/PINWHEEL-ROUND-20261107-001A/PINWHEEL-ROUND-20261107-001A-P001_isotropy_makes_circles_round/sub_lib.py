"""Right-triangle substitution tilings and their parity laws (ticket PINWHEEL-ROUND-20261107-001A).

The pinwheel (Conway's cut of the triangle with legs 1:2), the same five copies cut frame-consistently, and the 1:1 triangle
halved by its altitude. Tiles are (O, P, Q): right-angle vertex, end of the long leg, end of the short leg; exact integer
coordinates. A parity law has knots at tile corners (bonds: cycles of the tile adjacency graph) or on tiles (bonds: cycles of
the vertex graph); bond distance is the least such cycle through two variables, minus one."""
from __future__ import annotations
import heapq, math
from collections import defaultdict

def split(tile, m):
    O, P, Q = tile
    d = 1 + m * m
    H = (Q[0] + (P[0] - Q[0]) // d, Q[1] + (P[1] - Q[1]) // d)
    out = [(H, O, Q)]                       # small copy: right angle at H, long leg to O, short leg to Q
    ex = ((P[0] - H[0]) // m, (P[1] - H[1]) // m)
    ey = ((O[0] - H[0]) // m, (O[1] - H[1]) // m)
    V = lambda i, j: (H[0] + i * ex[0] + j * ey[0], H[1] + i * ex[1] + j * ey[1])
    for i in range(m):
        for j in range(m - i):
            out.append((V(i, j), V(i + 1, j), V(i, j + 1)))
            if i + j <= m - 2:
                out.append((V(i + 1, j + 1), V(i, j + 1), V(i + 1, j)))
    return out

def tiling(m, k):
    """k substitution levels from one triangle; coordinates scaled by (m (1 + m^2))^k so that all points are integers."""
    D = m * (1 + m * m)
    tiles = [((0, 0), (m, 0), (0, 1))]
    for _ in range(k):
        tiles = [tuple((x * D, y * D) for x, y in t) for t in tiles]
        tiles = [s for t in tiles for s in split(t, m)]
    scale = D ** k / math.sqrt(1 + m * m) ** k          # one short leg of a final tile has length `scale` in these coordinates
    return tiles, scale

def build_graph(tiles):
    """Plane graph of the tiling: vertices = tile corners, edges = boundary segments between consecutive vertices.
    Returns dict with vertex coords, segment list (vertex pairs), segment -> tiles, tile adjacency via segments."""
    vid = {}
    for t in tiles:
        for p in t:
            if p not in vid:
                vid[p] = len(vid)
    coords = [None] * len(vid)
    for p, i in vid.items():
        coords[i] = p
    # bucket vertices
    side_len = max(abs(t[1][0] - t[0][0]) + abs(t[1][1] - t[0][1]) for t in tiles[:50])
    cell = max(1, side_len)
    buckets = defaultdict(list)
    for p, i in vid.items():
        buckets[(p[0] // cell, p[1] // cell)].append(i)
    seg_tiles = defaultdict(list)
    for ti, t in enumerate(tiles):
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            ax, ay = a; bx, by = b
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            on = [(0, vid[a]), (L2, vid[b])]
            for cx in range(min(ax, bx) // cell, max(ax, bx) // cell + 1):
                for cy in range(min(ay, by) // cell, max(ay, by) // cell + 1):
                    for i in buckets.get((cx, cy), ()):
                        px, py = coords[i]
                        if (px - ax) * dy - (py - ay) * dx != 0:
                            continue
                        s = (px - ax) * dx + (py - ay) * dy
                        if 0 < s < L2:
                            on.append((s, i))
            on.sort()
            for (s1, i1), (s2, i2) in zip(on, on[1:]):
                seg_tiles[(min(i1, i2), max(i1, i2))].append(ti)
    segs = list(seg_tiles.keys())
    return {"coords": coords, "segs": segs, "seg_tiles": [seg_tiles[s] for s in segs], "ntiles": len(tiles)}

def laws(G):
    """Adjacency lists for the two laws' bond graphs.
    corner law (knots at vertices): bonds = cycles of the tile adjacency graph; variables = interior segments.
    tile law (knots on tiles): bonds = cycles of the vertex graph; variables = all segments."""
    nt = G["ntiles"]
    tadj = [[] for _ in range(nt)]
    telist = []
    seg_of_tedge = []
    for k, ts in enumerate(G["seg_tiles"]):
        if len(ts) == 2:
            a, b = ts
            j = len(telist); telist.append((a, b)); seg_of_tedge.append(k)
            tadj[a].append((b, j)); tadj[b].append((a, j))
    nv = len(G["coords"])
    vadj = [[] for _ in range(nv)]
    for k, (a, b) in enumerate(G["segs"]):
        vadj[a].append((b, k)); vadj[b].append((a, k))
    return {"corner": (tadj, telist, seg_of_tedge), "tile": (vadj, list(G["segs"]), list(range(len(G["segs"]))))}

def orientation_count(tiles, tol=1e-9):
    """Distinct directions of the long leg, modulo 2 pi."""
    angs = set()
    for O, P, Q in tiles:
        a = math.atan2(P[1] - O[1], P[0] - O[0]) % (2 * math.pi)
        angs.add(round(a, 9))
    return len(angs)

def split_pinwheel(tile):
    """Conway's pinwheel decomposition (legs 1:2): drop the altitude from the right angle; cut the larger piece along its median
    to the midpoint M of the long leg, and each of the two isosceles halves along its axis. Four copies meet at M; the two
    halves give mirror-image pairs. Needs coordinates divisible by 10."""
    O, P, Q = tile
    H = (Q[0] + (P[0] - Q[0]) // 5, Q[1] + (P[1] - Q[1]) // 5)
    M = ((O[0] + P[0]) // 2, (O[1] + P[1]) // 2)
    F1 = ((O[0] + H[0]) // 2, (O[1] + H[1]) // 2)
    F2 = ((H[0] + P[0]) // 2, (H[1] + P[1]) // 2)
    return [(H, O, Q), (F1, M, O), (F1, M, H), (F2, H, M), (F2, P, M)]

def tiling_rule(rule, k):
    """rule in {'pinwheel', 'consistent', 'isosceles'}: the pinwheel (Conway's cut), the same five copies cut frame-consistently
    (altitude, then midpoints), or the isosceles right triangle halved by its altitude."""
    if rule == "pinwheel":
        D, top, f = 10, ((0, 0), (2, 0), (0, 1)), split_pinwheel
    elif rule == "consistent":
        D, top, f = 10, ((0, 0), (2, 0), (0, 1)), lambda t: split(t, 2)
    elif rule == "isosceles":
        D, top, f = 2, ((0, 0), (1, 0), (0, 1)), lambda t: split(t, 1)
    else:
        raise ValueError(rule)
    tiles = [top]
    for _ in range(k):
        tiles = [tuple((x * D, y * D) for x, y in t) for t in tiles]
        tiles = [s for t in tiles for s in f(t)]
    ratio = math.sqrt(5) if rule != "isosceles" else math.sqrt(2)
    scale = D ** k / ratio ** k
    return tiles, scale

def handedness(t):
    (ox, oy), (px, py), (qx, qy) = t
    return 1 if (px - ox) * (qy - oy) - (py - oy) * (qx - ox) > 0 else -1

def check_congruent(tiles, scale, m):
    """Every tile has legs scale*m and scale*1 at a right angle (exactness up to float rounding)."""
    worst = 0.0
    for O, P, Q in tiles:
        a = math.dist(O, P) / scale; b = math.dist(O, Q) / scale
        dot = (P[0] - O[0]) * (Q[0] - O[0]) + (P[1] - O[1]) * (Q[1] - O[1])
        worst = max(worst, abs(a - m), abs(b - 1))
        if dot != 0:
            return False, worst
    return worst < 1e-6, worst


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
