#!/usr/bin/env python3
"""Checks for BOARD-READ-20261110-001A: on every periodic board the route reading is a polygon norm up to a constant.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
On BOARD-READ-20261110-001B-E001's board_lib: for four boards at g = 2 and 3, the cycle polygon contains 0 in its interior, and route
distances by breadth-first search on a 40 x 40-domain torus stay within a constant of the polygon's gauge (least over the torus's
images), with no growth from the nearer half of the distances read to the farther half."""
import hashlib
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/BOARD-READ-20261110-001B/BOARD-READ-20261110-001B-E001_route_and_graph_polygons"))
import board_lib as BL  # noqa: E402

T0 = time.time()
OUT = {}
DEPS = {"experiments/BOARD-READ-20261110-001B/BOARD-READ-20261110-001B-E001_route_and_graph_polygons/board_lib.py": "1cc208f412014c3738a478b9cb376fc4308c1055f781e1e72b6470f1ecbe8155"}
L, KMAX = 40, 16
DIRS = [(a, b) for a in range(-3, 4) for b in range(-3, 4) if (a, b) != (0, 0) and math.gcd(abs(a), abs(b)) == 1]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def interior(points):
    # 0 interior: every direction among 72 has a positive finite gauge
    for i in range(72):
        th = 2 * math.pi * i / 72
        v = (math.cos(th), math.sin(th))
        best = None
        P = [(float(x), float(y)) for x, y in points]
        for a in range(len(P)):
            for b in range(a + 1, len(P)):
                (px, py), (qx, qy) = P[a], P[b]
                det = px * qy - py * qx
                if abs(det) < 1e-15:
                    continue
                s = (v[0] * qy - v[1] * qx) / det
                t = (px * v[1] - py * v[0]) / det
                if s >= -1e-12 and t >= -1e-12:
                    best = s + t if best is None else min(best, s + t)
        if best is None:
            return False
    return True


def one(board, g):
    route, graph = BL.polygons(board, g)
    tor = BL.torus(board, g, L)
    t0 = tor["types"][0]
    dist = BL.bfs(tor["succ"], BL.ring_cells(tor, t0, 0, 0))
    near, far = [], []
    for v in DIRS:
        K = KMAX // max(abs(v[0]), abs(v[1]))
        for k in range(1, K + 1):
            T = min(dist[c] for c in BL.ring_cells(tor, t0, k * v[0], k * v[1]))
            N = min(BL.gauge(route, (k * v[0] + L * a, k * v[1] + L * b), board) for a in (-1, 0, 1) for b in (-1, 0, 1))
            (near if k <= K // 2 else far).append(abs(float(T - N)))
    return {"board": board, "g": g, "0 interior": interior(route) and interior(graph), "nearer half max |T - N|": max(near),
            "farther half max |T - N|": max(far)}


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    rows = [one(b, g) for b in ("square", "triangular", "honeycomb", "kagome") for g in (2, 3)]
    ok = all(r["0 interior"] and r["farther half max |T - N|"] <= r["nearer half max |T - N|"] for r in rows)
    check("1 The polygon has 0 inside and the route reading stays within a constant of its gauge, without growth, on four boards", ok, rows)
    result = {"ticket": "BOARD-READ-20261110-001A", "artifact_id": "BOARD-READ-20261110-001A-P001", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        return 0
    old = json.loads(path.read_text())
    same = json.dumps(old["checks"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True)
    print("result.json matches" if same else "result.json differs")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
