"""LOGIC-CIRCLE-20261107-001C-E001: measured circles of random planar parity laws (exploratory; see contract.json).

Bond distance between two variables of a planar parity law = least cycle of its plane dual H through the two dual edges, minus
one (exact two-unit minimum-cost flow). Writes artifacts/LOGIC-CIRCLE-20261107-001C/LOGIC-CIRCLE-20261107-001C-E001_measured_circles/run/result.json."""
from __future__ import annotations
import heapq, json, math, random, sys, time
from collections import deque
from pathlib import Path
import numpy as np
from scipy.spatial import Delaunay

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts" / "LOGIC-CIRCLE-20261107-001C" / "LOGIC-CIRCLE-20261107-001C-E001_measured_circles" / "run"
K = 24
SOURCES = 4

def min_cycle_through(adj, elist, e, f):
    """Least cycle through edges e and f: two vertex-disjoint paths joining their ends (min-cost flow with potentials)."""
    a, b = elist[e]; c, d = elist[f]
    if len({a, b, c, d}) < 4:
        return None
    n = len(adj); N = 2 * n + 2; S, T = 2 * n, 2 * n + 1
    head = [[] for _ in range(N)]
    def add(u, v, cap, cost):
        head[u].append([v, cap, cost, len(head[v])]); head[v].append([u, 0, -cost, len(head[u]) - 1])
    for v in range(n):
        add(2 * v, 2 * v + 1, 1, 0)
    for k, (x, y) in enumerate(elist):
        if k != e and k != f:
            add(2 * x + 1, 2 * y, 1, 1); add(2 * y + 1, 2 * x, 1, 1)
    add(S, 2 * a, 1, 0); add(S, 2 * b, 1, 0); add(2 * c + 1, T, 1, 0); add(2 * d + 1, T, 1, 0)
    pot = [0] * N; cost = 0; INF = float("inf")
    for _ in range(2):
        dist = [INF] * N; prev = [None] * N; dist[S] = 0; pq = [(0, S)]
        while pq:
            du, u = heapq.heappop(pq)
            if du > dist[u]:
                continue
            for i, (v, cap, c_, _) in enumerate(head[u]):
                if cap > 0:
                    nd = du + c_ + pot[u] - pot[v]
                    if nd < dist[v]:
                        dist[v] = nd; prev[v] = (u, i); heapq.heappush(pq, (nd, v))
        if dist[T] == INF:
            return None
        for v in range(N):
            if dist[v] < INF:
                pot[v] += dist[v]
        v = T
        while v != S:
            u, i = prev[v]; head[u][i][1] -= 1; head[v][head[u][i][3]][1] += 1; cost += head[u][i][2]; v = u
    return cost + 2

def from_edges(pos, edges):
    adj = [[] for _ in range(len(pos))]
    for k, (a, b) in enumerate(edges):
        adj[a].append((b, k)); adj[b].append((a, k))
    mid = np.array([(pos[a] + pos[b]) / 2 for a, b in edges])
    return adj, list(edges), mid

def square_H(R):
    m = 2 * R + 24
    pos = np.array([(x, y) for x in range(m) for y in range(m)], float)
    idx = lambda x, y: x * m + y
    edges = [(idx(x, y), idx(x + 1, y)) for x in range(m - 1) for y in range(m)] + [(idx(x, y), idx(x, y + 1)) for x in range(m) for y in range(m - 1)]
    return (*from_edges(pos, edges), np.array([m / 2, m / 2]))

def triangular_H(R):
    m = 2 * R + 30
    pos = np.array([(i + 0.5 * j, j * math.sqrt(3) / 2) for i in range(-m // 2, m) for j in range(m)], float)
    key = {(round(p[0] * 2), round(p[1] * 2 / math.sqrt(3))): k for k, p in enumerate(pos)}
    edges = []
    for k, p in enumerate(pos):
        for dx, dy in ((1, 0), (0.5, math.sqrt(3) / 2), (-0.5, math.sqrt(3) / 2)):
            q = (round((p[0] + dx) * 2), round((p[1] + dy) * 2 / math.sqrt(3)))
            if q in key:
                edges.append((k, key[q]))
    centre = np.array([m / 4 + m / 4, m * math.sqrt(3) / 4])
    return (*from_edges(pos, edges), centre)

def split_H(R, p, rng):
    L = 2 * R + 30
    Dg = rng.random((L, L)) < p
    pos = np.array([(x, y) for x in range(L + 1) for y in range(L + 1)], float)
    idx = lambda x, y: x * (L + 1) + y
    edges = [(idx(x, y), idx(x + 1, y)) for x in range(L) for y in range(L + 1)] + [(idx(x, y), idx(x, y + 1)) for x in range(L + 1) for y in range(L)]
    for i in range(L):
        for j in range(L):
            edges.append((idx(i, j), idx(i + 1, j + 1)) if Dg[i, j] else (idx(i + 1, j), idx(i, j + 1)))
    return (*from_edges(pos, edges), np.array([L / 2, L / 2]))

def voronoi_H(R, rng):
    W = 2 * R + 30
    m = rng.poisson(W * W)
    pts = rng.random((m, 2)) * W
    tri = Delaunay(pts)
    es = set()
    for s in tri.simplices:
        for a, b in ((s[0], s[1]), (s[1], s[2]), (s[0], s[2])):
            es.add((min(a, b), max(a, b)))
    return (*from_edges(pts, sorted(es)), np.array([W / 2, W / 2]))

def g_strict(s, t, q):
    if q <= 0: return 0.0
    if q >= 1: return min(s, t)
    if q * s <= t <= s / q:
        return (2 * math.sqrt(q * s * t) - q * (s + t)) / (1 - q)
    return min(s, t)

PRED = {
    "square": lambda u: 2 * (abs(u[0]) + abs(u[1])),
    "honeycomb": lambda u: 2 * max(math.cos(math.atan2(u[1], u[0]) - math.radians(30 + 60 * j)) for j in range(6)) / math.cos(math.radians(30)),
    "split-1/2": lambda u: 2 * (abs(u[0]) + abs(u[1]) - g_strict(abs(u[0]), abs(u[1]), 0.5)),
    "split-1/4": lambda u: 2 * (abs(u[0]) + abs(u[1]) - g_strict(abs(u[0]), abs(u[1]), 0.25 if u[0] * u[1] >= 0 else 0.75)),
    "voronoi": None,
}

def profile(build, R, rng, label):
    """Mean radial profile over SOURCES sources: N_k = delta / |x| in K directions."""
    Ns = np.zeros((SOURCES, K)); dev = []
    for s in range(SOURCES):
        adj, elist, mid, centre = build()
        off = np.array([[0, 0], [1.3, 0.4], [-0.7, 1.1], [0.4, -1.2]][s]) if label in ("square", "honeycomb") else np.zeros(2)
        e0 = int(np.argmin(np.linalg.norm(mid - (centre + off), axis=1)))
        for k in range(K):
            th = 2 * math.pi * k / K
            f = int(np.argmin(np.linalg.norm(mid - (mid[e0] + R * np.array([math.cos(th), math.sin(th)])), axis=1)))
            L = min_cycle_through(adj, elist, e0, f)
            x = mid[f] - mid[e0]
            Ns[s, k] = (L - 1) / np.linalg.norm(x)
            if PRED.get(label):
                pr = PRED[label](x / np.linalg.norm(x))
                dev.append(abs(Ns[s, k] - pr) / pr)
    mean = Ns.mean(axis=0)
    out = {"R": R, "mean_profile": [round(v, 4) for v in mean], "anisotropy": round(float(mean.max() / mean.min()), 4),
           "mean_N": round(float(mean.mean()), 4)}
    if dev:
        out["max_relative_deviation_from_prediction"] = round(float(max(dev)), 4)
        out["mean_relative_deviation_from_prediction"] = round(float(np.mean(dev)), 4)
    return out

def bfs(adj, s):
    dist = [-1] * len(adj); dist[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for v, _ in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1; q.append(v)
    return dist

def uniform_quadrangulation(n, rng):
    steps = np.array([1] * n + [-1] * (n + 1)); rng.shuffle(steps)
    k = int(np.argmin(np.cumsum(steps)))
    steps = np.concatenate([steps[k + 1:], steps[:k + 1]])[:-1]
    parent, label, contour, cur = [-1], [0], [0], 0
    for s in steps:
        if s == 1:
            v = len(parent); parent.append(cur); label.append(label[cur] + int(rng.integers(-1, 2))); cur = v
        else:
            cur = parent[cur]
        contour.append(cur)
    corners = contour[:-1]; m = len(corners); lab = [label[c] for c in corners]
    vstar = len(parent); last = {}; succ = [None] * m
    for kk in range(2 * m - 1, -1, -1):
        l = lab[kk % m]
        if kk < m:
            succ[kk] = last.get(l - 1)
        last[l] = kk
    edges = [(corners[i], vstar if succ[i] is None else corners[succ[i] % m]) for i in range(m)]
    adj = [[] for _ in range(vstar + 1)]
    for k, (a, b) in enumerate(edges):
        adj[a].append((b, k)); adj[b].append((a, k))
    return adj, edges

def main():
    t0 = time.time()
    rng = np.random.default_rng(20261107); random.seed(20261107)
    res = {"laws": {}, "quadrangulation": {}}
    sizes = {"square": [10, 20, 40], "honeycomb": [10, 20, 40], "split-1/2": [20, 40, 80], "split-1/4": [20, 40, 80], "voronoi": [10, 20, 40, 60]}
    for label, radii in sizes.items():
        res["laws"][label] = []
        for R in radii:
            t = time.time()
            if label == "square": build = lambda: square_H(R)
            elif label == "honeycomb": build = lambda: triangular_H(R)
            elif label == "split-1/2": build = lambda: split_H(R, 0.5, rng)
            elif label == "split-1/4": build = lambda: split_H(R, 0.25, rng)
            else: build = lambda: voronoi_H(R, rng)
            row = profile(build, R, rng, label)
            row["seconds"] = round(time.time() - t, 1)
            res["laws"][label].append(row)
            print(label, {k: v for k, v in row.items() if k != "mean_profile"}, flush=True)
    for n in (1000, 4000, 16000, 64000):
        t = time.time(); ds, gd, none = [], [], 0
        for rep in range(8):
            adj, edges = uniform_quadrangulation(n, rng)
            got = 0
            while got < 8:
                e, f = random.randrange(len(edges)), random.randrange(len(edges))
                if len(set(edges[e]) | set(edges[f])) < 4:
                    continue
                L = min_cycle_through(adj, edges, e, f)
                if L is None:
                    none += 1; continue
                ds.append(L - 1); got += 1
                gd.append(bfs(adj, edges[e][0])[edges[f][0]])
        res["quadrangulation"][str(n)] = {"mean_bond_distance": round(float(np.mean(ds)), 3), "sd": round(float(np.std(ds)), 3),
                                          "mean_graph_distance": round(float(np.mean(gd)), 3), "pairs": len(ds),
                                          "pairs_without_common_bond": none, "seconds": round(time.time() - t, 1)}
        print("quadrangulation", n, res["quadrangulation"][str(n)], flush=True)
    ns = [1000, 4000, 16000, 64000]
    y = [math.log(res["quadrangulation"][str(n)]["mean_bond_distance"]) for n in ns]
    x = [math.log(n) for n in ns]
    slope = float(np.polyfit(x, y, 1)[0])
    res["quadrangulation_loglog_slope"] = round(slope, 4)
    res["quadrangulation_loglog_slope_last_two"] = round((y[-1] - y[-2]) / (x[-1] - x[-2]), 4)
    res["runtime_seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("slope", slope, "runtime", res["runtime_seconds"])

if __name__ == "__main__":
    main()
