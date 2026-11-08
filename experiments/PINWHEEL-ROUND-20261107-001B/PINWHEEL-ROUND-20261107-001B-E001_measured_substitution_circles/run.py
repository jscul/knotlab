"""PINWHEEL-ROUND-20261107-001B-E001: measured circles of right-triangle substitution laws (exploratory; see contract.json).

Tilings: the pinwheel (Conway's cut of the 1:2 right triangle), the same five copies cut frame-consistently, and the 1:1 right
triangle halved by its altitude. Laws: parity knots at tile corners (bonds = cycles of the tile adjacency graph) or on tiles (bonds
= cycles of the vertex graph). Bond distance = least cycle through two edges, minus one (exact min-cost flow).
Writes artifacts/PINWHEEL-ROUND-20261107-001B/PINWHEEL-ROUND-20261107-001B-E001_measured_substitution_circles/run/result.json."""
from __future__ import annotations
import heapq, json, math, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts" / "PINWHEEL-ROUND-20261107-001B" / "PINWHEEL-ROUND-20261107-001B-E001_measured_substitution_circles" / "run"
K = 24
OFFSETS = [(0.0, 0.0), (3.1, 1.7), (-2.3, 2.9)]

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


# Exact least cycle through two edges (Suurballe on the vertex-split graph, scipy Dijkstra); validated equal to
# min_cycle_through above on 360 random pairs of the three tilings before this run.
EPS = 1e-9

class CycleSolver:
    def __init__(self, n, elist):
        self.n = n
        E = np.asarray(elist, dtype=np.int64)
        self.E = E
        m = len(E)
        # split graph: v_in = 2v, v_out = 2v + 1; S = 2n, T = 2n + 1
        self.N = 2 * n + 2
        split_src = 2 * np.arange(n); split_dst = 2 * np.arange(n) + 1
        x, y = E[:, 0], E[:, 1]
        # arcs: index 0..n-1 split arcs; then for edge k: x_out->y_in (n + 2k), y_out->x_in (n + 2k + 1)
        self.src = np.concatenate([split_src, np.stack([2 * x + 1, 2 * y + 1], axis=1).ravel()])
        self.dst = np.concatenate([split_dst, np.stack([2 * y, 2 * x], axis=1).ravel()])
        self.cost = np.concatenate([np.zeros(n), np.ones(2 * m)])

    def least_cycle(self, e, f):
        n, N = self.n, self.N
        a, b = self.E[e]; c, d = self.E[f]
        if len({int(a), int(b), int(c), int(d)}) < 4:
            return None
        S, T = 2 * n, 2 * n + 1
        keep = np.ones(len(self.src), dtype=bool)
        keep[[n + 2 * e, n + 2 * e + 1, n + 2 * f, n + 2 * f + 1]] = False
        src = np.concatenate([self.src[keep], [S, S, 2 * c + 1, 2 * d + 1]])
        dst = np.concatenate([self.dst[keep], [2 * a, 2 * b, T, T]])
        cost = np.concatenate([self.cost[keep], [0, 0, 0, 0]])
        # first shortest path
        G1 = csr_matrix((cost + EPS, (src, dst)), shape=(N, N))
        dist, pred = dijkstra(G1, directed=True, indices=S, return_predecessors=True)
        if not np.isfinite(dist[T]):
            return None
        path = set()
        v = T
        while v != S:
            u = pred[v]; path.add((u, v)); v = u
        # residual graph with reduced costs: forward arcs not on the path keep c + d(u) - d(v); path arcs reversed with cost 0
        du = dist[src]; dv = dist[dst]
        finite = np.isfinite(du) & np.isfinite(dv)
        key = src.astype(np.int64) * N + dst
        pkey = np.array([int(u) * N + int(w) for u, w in path], dtype=np.int64)
        on_path = np.isin(key, pkey)
        red = cost + EPS + np.where(finite, du - dv, 0.0)
        red = np.maximum(red, 0.0)
        use = finite & ~on_path
        rsrc = np.concatenate([src[use], dst[on_path]])
        rdst = np.concatenate([dst[use], src[on_path]])
        rcost = np.concatenate([red[use], np.zeros(on_path.sum())])
        G2 = csr_matrix((rcost + EPS, (rsrc, rdst)), shape=(N, N))
        d2 = dijkstra(G2, directed=True, indices=S, return_predecessors=False)
        if not np.isfinite(d2[T]):
            return None
        total = 2 * dist[T] + d2[T]
        # remove the epsilon contributions: round to the nearest integer path cost
        return int(round(total)) + 2


TOPS = {"pinwheel": ((0, 0), (2, 0), (0, 1)), "consistent": ((0, 0), (2, 0), (0, 1)), "isosceles": ((0, 0), (1, 0), (0, 1))}
DEPTH = {"pinwheel": (7, 8), "consistent": (7, 8), "isosceles": (16, 18)}

def incenter(top):
    (ax, ay), (bx, by), (cx, cy) = top
    a = math.dist((bx, by), (cx, cy)); b = math.dist((ax, ay), (cx, cy)); c = math.dist((ax, ay), (bx, by))
    s = a + b + c
    return ((a * ax + b * bx + c * cx) / s, (a * ay + b * by + c * cy) / s)

def setup(rule, k):
    tiles, scale = tiling_rule(rule, k)
    G = build_graph(tiles)
    L = laws(G)
    Dk = (10 if rule != "isosceles" else 2) ** k
    c = np.array(incenter([(x * Dk, y * Dk) for x, y in TOPS[rule]])) / scale
    coords = np.array(G["coords"], dtype=float) / scale
    segs = G["segs"]
    mid = (coords[[a for a, b in segs]] + coords[[b for a, b in segs]]) / 2
    angles = []
    for O, P, Q in tiles:
        angles.append(round(math.atan2(P[1] - O[1], P[0] - O[0]) % (2 * math.pi), 9))
    centroids = np.array([((O[0] + P[0] + Q[0]) / 3, (O[1] + P[1] + Q[1]) / 3) for O, P, Q in tiles], dtype=float) / scale
    solvers = {law: CycleSolver(len(L[law][0]), L[law][1]) for law in L}
    return {"tiles": len(tiles), "L": L, "solvers": solvers, "c": c, "mid": mid, "angles": np.array(angles), "centroids": centroids}

def harmonics(N):
    F = np.fft.rfft(N) / len(N)
    c0 = abs(F[0])
    return {str(j): round(float(2 * abs(F[j]) / c0), 5) for j in (2, 4, 6, 8)}

def measure(S, law, R, nsrc):
    adj, elist, seg_of = S["L"][law]
    emid = S["mid"][seg_of]
    prof = []
    for off in OFFSETS[:nsrc]:
        e0 = int(np.argmin(np.linalg.norm(emid - (S["c"] + np.array(off)), axis=1)))
        Ns = []
        for j in range(K):
            th = 2 * math.pi * j / K
            f = int(np.argmin(np.linalg.norm(emid - (emid[e0] + R * np.array([math.cos(th), math.sin(th)])), axis=1)))
            cyc = S["solvers"][law].least_cycle(e0, f)
            Ns.append((cyc - 1) / float(np.linalg.norm(emid[f] - emid[e0])))
        prof.append(Ns)
    mean = np.array(prof).mean(axis=0)
    return {"R": R, "sources": nsrc, "mean_profile": [round(float(v), 4) for v in mean],
            "anisotropy": round(float(mean.max() / mean.min()), 4), "mean_N": round(float(mean.mean()), 4), "harmonics": harmonics(mean)}

def orientations_within(S, R):
    d = np.linalg.norm(S["centroids"] - S["c"], axis=1)
    return int(len(set(S["angles"][d <= R].tolist())))

def main():
    t0 = time.time()
    res = {"laws": {}, "orientations_within_R": {}}
    for rule in ("isosceles", "pinwheel", "consistent"):
        k1, k2 = DEPTH[rule]
        for k, radii, nsrc in ((k1, (8, 16, 32, 64), 3), (k2, (128,), 1)):
            t = time.time()
            S = setup(rule, k)
            print(rule, "k", k, "tiles", S["tiles"], f"setup {time.time()-t:.0f}s", flush=True)
            res["orientations_within_R"].setdefault(rule, {})
            for R in radii:
                res["orientations_within_R"][rule][str(R)] = orientations_within(S, R)
            for law in ("corner", "tile"):
                for R in radii:
                    t = time.time()
                    row = measure(S, law, R, nsrc)
                    row["k"] = k; row["seconds"] = round(time.time() - t, 1)
                    res["laws"].setdefault(f"{rule}/{law}", []).append(row)
                    print(rule, law, {x: row[x] for x in ("R", "anisotropy", "mean_N", "harmonics", "seconds")}, flush=True)
                    OUT.mkdir(parents=True, exist_ok=True)
                    (OUT / "result.partial.json").write_text(json.dumps(res, indent=1) + "\n")
            del S
    res["runtime_seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    p = OUT / "result.partial.json"
    if p.exists():
        p.unlink()
    print("runtime", res["runtime_seconds"])

if __name__ == "__main__":
    main()
