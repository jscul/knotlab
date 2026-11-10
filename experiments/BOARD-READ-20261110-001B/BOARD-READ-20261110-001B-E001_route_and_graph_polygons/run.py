#!/usr/bin/env python3
"""Run BOARD-READ-20261110-001B-E001 (frozen contract beside this file): route and graph polygons of four boards.

    .venv/bin/python3 -B run.py
Writes artifacts/BOARD-READ-20261110-001B/BOARD-READ-20261110-001B-E001_route_and_graph_polygons/run/result.json."""
import json
import math
import sys
import time
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import board_lib as BL  # noqa: E402

OUT = ROOT / "artifacts/BOARD-READ-20261110-001B/BOARD-READ-20261110-001B-E001_route_and_graph_polygons/run"
BOARDS = ("square", "triangular", "honeycomb", "kagome")
GS = (2, 3, 4, 5, 6)
DIRS = [(a, b) for a in range(-3, 4) for b in range(-3, 4) if (a, b) != (0, 0) and math.gcd(abs(a), abs(b)) == 1]
L, KMAX = 48, 20


def hull(points):
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


def homothetic(P, Q):
    """is P = s Q for some s > 0 (both hulls about the origin)?"""
    if len(P) != len(Q):
        return None
    sq = [(x * x + y * y) for x, y in Q]
    k = max(range(len(Q)), key=lambda i: sq[i])
    for p in P:
        s2 = (p[0] ** 2 + p[1] ** 2) / sq[k]
        # try s = sqrt(s2) rational
        num, den = s2.numerator, s2.denominator
        rn, rd = math.isqrt(num), math.isqrt(den)
        if rn * rn == num and rd * rd == den:
            s = Fraction(rn, rd)
            if sorted((x * s, y * s) for x, y in Q) == sorted(P):
                return str(s)
    return None


def anisotropy(points, board, steps=3600):
    (a1, a2) = BL.BOARDS[board]["basis"]
    det = a1[0] * a2[1] - a1[1] * a2[0]
    vals = []
    for i in range(steps):
        th = 2 * math.pi * i / steps
        ex, ey = math.cos(th), math.sin(th)
        # Euclidean unit vector to lattice coordinates
        lx = (ex * a2[1] - ey * a2[0]) / det
        ly = (a1[0] * ey - a1[1] * ex) / det
        n = BL.gauge([(float(x), float(y)) for x, y in points], (lx, ly), board) if False else None
        vals.append(float_gauge(points, (lx, ly)))
    return max(vals) / min(vals)


def float_gauge(points, v):
    best = None
    P = [(float(x), float(y)) for x, y in points]
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            (px, py), (qx, qy) = P[i], P[j]
            det = px * qy - py * qx
            if abs(det) < 1e-15:
                continue
            a = (v[0] * qy - v[1] * qx) / det
            b = (px * v[1] - py * v[0]) / det
            if a >= -1e-12 and b >= -1e-12:
                best = a + b if best is None else min(best, a + b)
    return best


def one(job):
    board, g = job
    t0 = time.time()
    route_pts, graph_pts = BL.polygons(board, g)
    H, HG = hull(route_pts), hull(graph_pts)
    tor = BL.torus(board, g, L)
    t0type = tor["types"][0]
    src = BL.ring_cells(tor, t0type, 0, 0)
    dist = BL.bfs(tor["succ"], src)
    gd = BL.graph_bfs(board, L, (t0type, 0, 0))
    dev_route, dev_graph, readings = [], [], 0
    for v in DIRS:
        for k in range(1, KMAX // max(abs(v[0]), abs(v[1])) + 1):
            tgt = BL.ring_cells(tor, t0type, k * v[0], k * v[1])
            T = min(dist[c] for c in tgt)
            N = BL.gauge(route_pts, (k * v[0], k * v[1]), board)
            dev_route.append(float(T - N))
            NG = BL.gauge(graph_pts, (k * v[0], k * v[1]), board)
            dev_graph.append(float(gd[(t0type, (k * v[0]) % L, (k * v[1]) % L)] - NG))
            readings += 1
    return {"board": board, "g": g, "route hull": [[str(x), str(y)] for x, y in H], "graph hull": [[str(x), str(y)] for x, y in HG],
            "route vertices": len(H), "graph vertices": len(HG), "homothetic (route = s graph)": homothetic(H, HG),
            "route anisotropy": anisotropy(H, board), "graph anisotropy": anisotropy(HG, board),
            "readings": readings, "route T - N range": [min(dev_route), max(dev_route)],
            "graph d - N_G range": [min(dev_graph), max(dev_graph)], "seconds": round(time.time() - t0, 1)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    jobs = [(b, g) for b in BOARDS for g in GS]
    with Pool(6) as pool:
        rows = pool.map(one, jobs, chunksize=1)
    (OUT / "result.json").write_text(json.dumps({"experiment_id": "BOARD-READ-20261110-001B-E001", "rows": rows,
                                                  "seconds": round(time.time() - t0)}, indent=1) + "\n")
    for r in rows:
        print(r["board"], r["g"], r["route vertices"], r["graph vertices"], r["homothetic (route = s graph)"],
              round(r["route anisotropy"], 4), round(r["graph anisotropy"], 4), r["route T - N range"], r["graph d - N_G range"], flush=True)


if __name__ == "__main__":
    main()
