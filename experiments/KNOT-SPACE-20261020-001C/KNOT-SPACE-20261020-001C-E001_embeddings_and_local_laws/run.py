#!/usr/bin/env python3
"""Producer for KNOT-SPACE-20261020-001C-E001 (exploratory; see contract.json).

This is the bounded continuation of KNOT-SPACE-20261020-001A-E001:
- planarity is decided by searching rotation systems, independent of any
  matroid, and compared with the dual reading of the gauge law's allowed
  states;
- local parity laws written on no graph, designed so that their knot
  matroids can be 3-connected, are tested for graphic and cographic knot
  matroids;
- Ledrappier's allowed states are measured on tori up to 8x8.

Writes artifacts/KNOT-SPACE-20261020-001C/<this folder>/:
result.json, raw_rows.jsonl and run_output.txt.

    python3 -B run.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "KNOT-SPACE-20261020-001C" / HERE.name
LOG = []
START = time.time()


def log(msg):
    line = f"[{time.time() - START:.0f}s] {msg}"
    LOG.append(line)
    print(line, flush=True)


# ------------------------------------------------------------------ GF(2) linear algebra on bitmasks

def rref(rows):
    basis = []
    for r in rows:
        for p, b in basis:
            if r >> p & 1:
                r ^= b
        if r:
            p = r.bit_length() - 1
            basis = [(q, b ^ r if b >> p & 1 else b) for q, b in basis] + [(p, r)]
    return basis


def canonical(rows):
    return tuple(sorted(b for _, b in rref(rows)))


def kernel(rows, m):
    basis = rref(rows)
    pivots = {p for p, _ in basis}
    out = []
    for f in range(m):
        if f in pivots:
            continue
        x = 1 << f
        for p, r in basis:
            if r >> f & 1:
                x |= 1 << p
        out.append(x)
    return out


def codewords(basis):
    words = [0]
    for b in basis:
        words += [w ^ b for w in words]
    return words


def minimal_supports(basis):
    words = sorted((w for w in codewords(basis) if w), key=lambda w: (bin(w).count("1"), w))
    minimal = []
    for w in words:
        if not any(m & w == m for m in minimal):
            minimal.append(w)
    return minimal


def rank_on(basis, mask):
    return len(rref([b & mask for b in basis]))


def connected(basis, mask):
    """Is the column matroid of the code restricted to the coordinates in mask connected?"""
    elems = [j for j in range(mask.bit_length()) if mask >> j & 1]
    if not elems:
        return False
    rows = rref([b & mask for b in basis])
    parent = {j: j for j in elems}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for p, r in rows:
        for j in elems:
            if j != p and r >> j & 1:
                parent[find(j)] = find(p)
    return len({find(j) for j in elems}) == 1


def three_connected(basis, m):
    full = (1 << m) - 1
    if not connected(basis, full):
        return False
    rE = rank_on(basis, full)
    for mask in range(1 << (m - 1)):
        X = (mask << 1) | 1
        Y = full ^ X
        if bin(X).count("1") < 2 or bin(Y).count("1") < 2:
            continue
        if rank_on(basis, X) + rank_on(basis, Y) - rE <= 1:
            return False
    return True


def graph_reading(basis, m, use_all=False):
    """Returns (success, vertex supports)."""
    full = (1 << m) - 1
    minimal = minimal_supports(basis)
    if use_all:
        vertices = minimal
    else:
        vertices = [c for c in minimal if connected(basis, full ^ c)]
    counts = [sum(1 for c in vertices if c >> j & 1) for j in range(m)]
    if any(k != 2 for k in counts):
        return False, vertices
    return canonical(vertices) == canonical(basis), vertices


# ------------------------------------------------------------------ graphs

def stars(n, edges):
    out = [0] * n
    for i, (a, b) in enumerate(edges):
        out[a] |= 1 << i
        out[b] |= 1 << i
    return out


def cut_space(n, edges):
    return [b for _, b in rref(stars(n, edges))]


def cycle_space(n, edges):
    return kernel(stars(n, edges), len(edges))


def is_connected_graph(n, edges, removed=()):
    alive = [v for v in range(n) if v not in removed]
    if not alive:
        return True
    adj = {v: set() for v in alive}
    for a, b in edges:
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
    seen, stack = {alive[0]}, [alive[0]]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == len(alive)


def three_connected_graph(n, edges):
    if n < 4 or len(set(map(lambda e: tuple(sorted(e)), edges))) != len(edges):
        return False
    return is_connected_graph(n, edges) and all(is_connected_graph(n, edges, removed={a, b}) for a, b in combinations(range(n), 2))


def complete(n):
    return n, [(a, b) for a, b in combinations(range(n), 2)]


def wheel(k):
    return k + 1, [(0, i) for i in range(1, k + 1)] + [(i, i % k + 1) for i in range(1, k + 1)]


def prism(k):
    return 2 * k, [(i, (i + 1) % k) for i in range(k)] + [(k + i, k + (i + 1) % k) for i in range(k)] + [(i, k + i) for i in range(k)]


def antiprism(k):
    return 2 * k, [(i, (i + 1) % k) for i in range(k)] + [(k + i, k + (i + 1) % k) for i in range(k)] + \
        [(i, k + i) for i in range(k)] + [(i, k + (i + 1) % k) for i in range(k)]


def cube():
    return 8, [(a, b) for a, b in combinations(range(8), 2) if bin(a ^ b).count("1") == 1]


def octahedron():
    return 6, [(a, b) for a, b in combinations(range(6), 2) if b != a + 3 or a >= 3]


def bipartite(p, q):
    return p + q, [(a, p + b) for a in range(p) for b in range(q)]


def petersen():
    return 10, [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + [(5 + i, 5 + (i + 2) % 5) for i in range(5)]


def torus_grid(k):
    idx = lambda i, j: (i % k) * k + (j % k)
    edges = set()
    for i in range(k):
        for j in range(k):
            edges.add(tuple(sorted((idx(i, j), idx(i + 1, j)))))
            edges.add(tuple(sorted((idx(i, j), idx(i, j + 1)))))
    return k * k, sorted(edges)


def random_cubic(rng, n):
    while True:
        stubs = [v for v in range(n) for _ in range(3)]
        rng.shuffle(stubs)
        edges = [tuple(sorted((stubs[2 * i], stubs[2 * i + 1]))) for i in range(len(stubs) // 2)]
        if any(a == b for a, b in edges) or len(set(edges)) != len(edges):
            continue
        if three_connected_graph(n, edges):
            return n, edges


def stacked_triangulation(rng, n):
    edges = {tuple(sorted(e)) for e in combinations(range(4), 2)}
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    v = 4
    while v < n:
        f = faces.pop(rng.randrange(len(faces)))
        a, b, c = f
        edges |= {tuple(sorted((v, a))), tuple(sorted((v, b))), tuple(sorted((v, c)))}
        faces += [(a, b, v), (a, c, v), (b, c, v)]
        v += 1
    return n, sorted(edges)


def random_incidence(rng, m, deg, w):
    """Random constraints of size w with every variable in exactly deg constraints."""
    while True:
        stubs = [v for v in range(m) for _ in range(deg)]
        rng.shuffle(stubs)
        rows = [stubs[i:i + w] for i in range(0, len(stubs), w)]
        if all(len(set(r)) == len(r) for r in rows):
            return [sum(1 << v for v in r) for r in rows]


def ledrappier(L):
    idx = lambda i, j: (i % L) * L + (j % L)
    return [(1 << idx(i, j)) | (1 << idx(i + 1, j)) | (1 << idx(i, j + 1)) for i in range(L) for j in range(L)]




def planar_by_embeddings(n, edges, cap=2_000_000):
    """True/False when some/no rotation system gives V - E + F = 2; None if the search exceeds cap systems."""
    nbrs = {v: [] for v in range(n)}
    for a, b in edges:
        nbrs[a].append(b)
        nbrs[b].append(a)
    options = []
    total = 1
    for v in range(n):
        ns = nbrs[v]
        orders = [tuple(ns)] if len(ns) <= 2 else [(ns[0],) + p for p in permutations(ns[1:])]
        options.append(orders)
        total *= len(orders)
    if total > cap:
        return None
    m = len(edges)
    for choice in product(*options):
        succ = {}
        for v in range(n):
            order = choice[v]
            for i, w in enumerate(order):
                succ[(v, w)] = order[(i + 1) % len(order)]
        seen = set()
        faces = 0
        for a, b in edges:
            for dart in ((a, b), (b, a)):
                if dart in seen:
                    continue
                faces += 1
                d = dart
                while d not in seen:
                    seen.add(d)
                    u, w = d
                    d = (w, succ[(w, u)])
        if n - m + faces == 2:
            return True
    return False


def random_sparse(rng, m):
    rows = []
    for _ in range(m // 2):
        size = rng.randint(3, 5)
        rows.append(sum(1 << v for v in rng.sample(range(m), size)))
    return rows


def analyse_law(rows, m):
    C = [b for _, b in rref(kernel(rows, m))]
    dual = kernel(C, m)
    row = {"m": m, "constraints": rows, "dim": len(C), "dual_dim": len(dual)}
    if not C or not dual or len(C) > 15 or len(dual) > 15:
        row["three_connected"] = None
        return row
    row["three_connected"] = three_connected(C, m)
    row["graphic"] = graph_reading(C, m)[0]
    row["cographic"] = graph_reading(dual, m)[0]
    return row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261021)
    rows = []
    graphs = {"K4": complete(4), "K5": complete(5), "K6": complete(6), "cube": cube(), "octahedron": octahedron(),
              "K33": bipartite(3, 3), "K34": bipartite(3, 4), "Petersen": petersen()}
    for k in range(4, 10):
        graphs[f"W{k}"] = wheel(k)
    for k in range(3, 7):
        graphs[f"prism {k}"] = prism(k)
    for i in range(24):
        graphs[f"random cubic {i}"] = random_cubic(rng, (8, 10, 12)[i % 3])
    for name, (n, edges) in graphs.items():
        m = len(edges)
        planar = planar_by_embeddings(n, edges)
        dual_ok, faces = graph_reading(cycle_space(n, edges), m)
        rows.append({"part": "planarity", "name": name, "n": n, "m": m, "edges": [list(e) for e in edges],
                     "three_connected_graph": three_connected_graph(n, edges), "planar_by_embeddings": planar,
                     "dual_reading": dual_ok, "faces": len(faces) if dual_ok else None})
    log("planarity done")
    disguised = 0
    for i in range(10):
        n, edges = random_cubic(rng, (8, 10, 12)[i % 3])
        perm = list(range(len(edges)))
        rng.shuffle(perm)
        relabelled = [edges[perm[j]] for j in range(len(edges))]
        C = [b for _, b in rref(kernel(stars(n, relabelled), len(edges)))]
        ok, verts = graph_reading(kernel(C, len(edges)), len(edges))
        disguised += ok and canonical(verts) == canonical(stars(n, relabelled))
    log("disguised graphs done")
    local = []
    for m in (12, 14, 16):
        for _ in range(40):
            local.append({"part": "local", "kind": "three of size six", **analyse_law(random_incidence(rng, m, 3, 6), m)})
            local.append({"part": "local", "kind": "sparse", **analyse_law(random_sparse(rng, m), m)})
    rows += local
    log("local laws done")
    ledr = []
    for L in range(3, 9):
        C = kernel(ledrappier(L), L * L)
        ledr.append({"part": "ledrappier", "L": L, "variables": L * L, "dim": len(C)})
    rows += ledr
    plan = [r for r in rows if r["part"] == "planarity" and r["three_connected_graph"] and r["planar_by_embeddings"] is not None]
    t1 = all(r["dual_reading"] == r["planar_by_embeddings"] for r in plan)
    tc = [r for r in local if r.get("three_connected")]
    frac = sum(bool(r["graphic"] or r["cographic"]) for r in tc) / max(1, len(tc))
    t2 = len(tc) >= 20 and frac <= 0.05
    known_planar = [r for r in rows if r["part"] == "planarity" and (r["name"].startswith("W") or r["name"].startswith("prism")
                                                                     or r["name"] in ("cube", "octahedron", "K4"))]
    known_nonplanar = [r for r in rows if r["part"] == "planarity" and r["name"] in ("K5", "K33", "Petersen")]
    controls = {
        "C1_search_accepts_known_planar": all(r["planar_by_embeddings"] in (True, None) for r in known_planar)
        and any(r["planar_by_embeddings"] for r in known_planar),
        "C1_search_rejects_known_nonplanar": all(r["planar_by_embeddings"] is False for r in known_nonplanar),
        "C2_disguised_graphs_recovered": disguised == 10,
    }
    summary = {
        "planarity": {"graphs": len(plan), "planar": sum(r["planar_by_embeddings"] for r in plan),
                      "dual_reading_agrees": sum(r["dual_reading"] == r["planar_by_embeddings"] for r in plan),
                      "search_capped": [r["name"] for r in rows if r["part"] == "planarity" and r["planar_by_embeddings"] is None]},
        "local": {kind: {"laws": sum(1 for r in local if r["kind"] == kind),
                         "three_connected": sum(1 for r in local if r["kind"] == kind and r.get("three_connected")),
                         "graphic_or_cographic": sum(1 for r in local if r["kind"] == kind and r.get("three_connected")
                                                     and (r["graphic"] or r["cographic"]))}
                  for kind in ("three of size six", "sparse")},
        "fraction": round(frac, 4),
        "ledrappier": ledr,
        "disguised_graphs_recovered": disguised,
    }
    result = {"experiment_id": "KNOT-SPACE-20261020-001C-E001", "evidence_stage": "exploratory", "summary": summary,
              "predictions": {"T1": t1, "T2": t2}, "controls": controls, "signal": t1 and t2,
              "wall_seconds": round(time.time() - START, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (OUT / "raw_rows.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    log(f"summary {json.dumps(summary)}")
    log(f"predictions {result['predictions']} controls {controls} signal {result['signal']}")
    (OUT / "run_output.txt").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    sys.exit(main())
