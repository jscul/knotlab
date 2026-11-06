#!/usr/bin/env python3
"""Producer for KNOT-SPACE-20261020-001A-E001 (exploratory; see contract.json).

A parity law's allowed states are a coset of a binary code C. Its knot matroid
is the column matroid of C:
- cocircuits are the minimal supports of C;
- circuits are the minimal supports of the dual code.

The graph reading of a code D takes as vertices the minimal supports of D
whose deletion leaves the matroid of D connected, and joins vertices by the
variables they share. The reading succeeds when every variable lies in
exactly two vertices and the cut space of the resulting graph is D.

Writes artifacts/KNOT-SPACE-20261020-001A/<this folder>/:
result.json, raw_rows.jsonl and run_output.txt.

    python3 -B run.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "KNOT-SPACE-20261020-001A" / HERE.name
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


# ------------------------------------------------------------------ presentations

def scramble(rng, rows, m):
    rows = list(rows)
    k = len(rows)
    for _ in range(3 * k):
        i, j = rng.randrange(k), rng.randrange(k)
        if i != j:
            rows[i] ^= rows[j]
    extra = []
    for _ in range(rng.randint(1, 3)):
        s = 0
        for r in rows:
            if rng.random() < 0.5:
                s ^= r
        extra.append(s)
    out = rows + extra
    rng.shuffle(out)
    return out


def gauge_presentation(rng, n, edges):
    return scramble(rng, cycle_space(n, edges), len(edges))


def tseitin_presentation(rng, n, edges):
    return scramble(rng, stars(n, edges), len(edges))


# ------------------------------------------------------------------ non-binary gauge

S3 = [(0, 1, 2), (1, 0, 2), (2, 1, 0), (0, 2, 1), (1, 2, 0), (2, 0, 1)]
S3I = {p: i for i, p in enumerate(S3)}


def s3mul(a, b):
    pa, pb = S3[a], S3[b]
    return S3I[tuple(pa[pb[i]] for i in range(3))]


def s3inv(a):
    pa = S3[a]
    r = [0] * 3
    for i in range(3):
        r[pa[i]] = i
    return S3I[tuple(r)]


def gauge_states(n, edges, group):
    if group == "Z3":
        q, sub = 3, (lambda a, b: (a - b) % 3)
    else:
        q, sub = 6, (lambda a, b: s3mul(a, s3inv(b)))
    out = set()
    for pot in product(range(q), repeat=n - 1):
        p = (0,) + pot
        out.add(tuple(sub(p[a], p[b]) for a, b in edges))
    return out


def relative_circuits(S, m):
    sizes = [len({t[i] for t in S}) for i in range(m)]
    found = []
    for size in range(1, m + 1):
        for Y in combinations(range(m), size):
            if any(set(C) <= set(Y) for C in found):
                continue
            full = 1
            for i in Y:
                full *= sizes[i]
            if len({tuple(t[i] for i in Y) for t in S}) < full:
                found.append(Y)
    return found


# ------------------------------------------------------------------ local laws

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


# ------------------------------------------------------------------ main

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261020)
    rows = []

    named = {"K4": complete(4), "K5": complete(5), "K6": complete(6), "cube": cube(), "octahedron": octahedron(),
             "K33": bipartite(3, 3), "K34": bipartite(3, 4), "Petersen": petersen(), "torus 3x3": torus_grid(3)}
    for k in range(4, 10):
        named[f"W{k}"] = wheel(k)
    for k in range(3, 7):
        named[f"prism {k}"] = prism(k)
    for i in range(12):
        named[f"random cubic {i}"] = random_cubic(rng, rng.choice([8, 10, 12]))
    planar = {"K4", "cube", "octahedron"} | {f"W{k}" for k in range(4, 10)} | {f"prism {k}" for k in range(3, 7)}
    extra_planar = {f"antiprism {k}": antiprism(k) for k in (4, 5)}
    for i in range(6):
        extra_planar[f"stacked {i}"] = stacked_triangulation(rng, rng.randint(6, 9))

    # S1 and S3: recovery and spheres
    for name, (n, edges) in list(named.items()) + list(extra_planar.items()):
        m = len(edges)
        truth = canonical(stars(n, edges))
        row = {"part": "recovery", "name": name, "n": n, "m": m, "edges": [list(e) for e in edges],
               "three_connected_graph": three_connected_graph(n, edges), "planar": name in planar or name in extra_planar}
        gauge_ok, tseitin_ok = 0, 0
        for _ in range(3):
            pres = gauge_presentation(rng, n, edges)
            C = [b for _, b in rref(kernel(pres, m))]
            ok, verts = graph_reading(C, m)
            gauge_ok += ok and canonical(verts) == truth and len(verts) == n
            pres = tseitin_presentation(rng, n, edges)
            C = [b for _, b in rref(kernel(pres, m))]
            dual = kernel(C, m)
            ok, verts = graph_reading(dual, m)
            tseitin_ok += ok and canonical(verts) == truth and len(verts) == n
            # control C3: read vertices off the presentation's own rows
            row.setdefault("rows_as_vertices_match", 0)
            row["rows_as_vertices_match"] += canonical([r for r in pres if r]) == truth and len([r for r in pres if r]) == n
        row["gauge_recovered"] = gauge_ok
        row["tseitin_recovered"] = tseitin_ok
        cyc = cycle_space(n, edges)
        ok, faces = graph_reading(cyc, m)
        row["dual_reading"] = ok
        if ok:
            F = len(faces)
            per_edge = [sum(1 for f in faces if f >> j & 1) for j in range(m)]
            row["faces"] = F
            row["sphere"] = all(c == 2 for c in per_edge) and n - m + F == 2
        all_ok, _ = graph_reading(cut_space(n, edges), m, use_all=True)
        row["all_cocircuits_reading"] = all_ok
        rows.append(row)
    log("recovery and spheres done")

    # S2: Whitney twists
    twists = []
    for t in range(4):
        while True:
            a = rng.randint(4, 6)
            b = rng.randint(4, 6)
            e1 = [e for e in combinations(range(a), 2) if rng.random() < 0.6]
            e2 = [e for e in combinations(range(b), 2) if rng.random() < 0.6]
            # pieces share vertices 0 (u) and 1 (v); piece 2's vertices 2.. are fresh
            relabel2 = {0: 0, 1: 1}
            for v in range(2, b):
                relabel2[v] = a + v - 2
            n = a + b - 2
            g1 = [tuple(sorted(e)) for e in e1]
            g2 = [tuple(sorted((relabel2[x], relabel2[y]))) for x, y in e2 if (x, y) != (0, 1)]
            edges = g1 + [e for e in g2 if e not in g1]
            swap = {0: 1, 1: 0}
            twisted2 = [tuple(sorted((swap.get(x, x), swap.get(y, y)))) for x, y in g2]
            edges_t = g1 + [e for e, orig in zip(twisted2, g2) if orig not in g1]
            if len(set(edges)) != len(edges) or len(set(edges_t)) != len(edges_t):
                continue
            if not (is_connected_graph(n, edges) and all(is_connected_graph(n, edges, removed={v}) for v in range(n))):
                continue
            if sorted(stars(n, edges)) == sorted(stars(n, edges_t)):
                continue
            break
        same_states = canonical(cut_space(n, edges)) == canonical(cut_space(n, edges_t)) and \
            canonical(cycle_space(n, edges)) == canonical(cycle_space(n, edges_t))
        twists.append({"part": "twist", "n": n, "m": len(edges), "edges": [list(e) for e in edges],
                       "edges_twisted": [list(e) for e in edges_t], "same_allowed_states": same_states,
                       "stars_differ": sorted(stars(n, edges)) != sorted(stars(n, edges_t))})
    rows += twists
    log("twists done")

    # S4: non-binary gauge
    nonbinary = []
    for name, (n, edges) in (("K4", complete(4)), ("prism 3", prism(3)), ("W5", wheel(5)), ("K5", complete(5))):
        m = len(edges)
        cycles = sorted(tuple(j for j in range(m) if c >> j & 1) for c in minimal_supports(cycle_space(n, edges)))
        for group in ("Z3", "S3"):
            S = gauge_states(n, edges, group)
            circ = sorted(relative_circuits(S, m))
            nonbinary.append({"part": "nonbinary", "name": name, "group": group, "states": len(S),
                              "circuits_are_cycles": circ == cycles})
    rows += nonbinary
    log("non-binary gauge done")

    # S5: local laws
    local = []
    for (m, w) in ((10, 3), (12, 3), (12, 4), (14, 3), (16, 4)):
        for _ in range(24):
            r = analyse_law(random_incidence(rng, m, 3, w), m)
            local.append({"part": "local", "kind": f"three per variable, size {w}", **r})
    for L in (3, 4):
        r = analyse_law(ledrappier(L), L * L)
        local.append({"part": "local", "kind": f"Ledrappier {L}x{L}", **r})
    for _ in range(60):
        m = rng.choice([10, 12, 14])
        w = rng.choice([3, 4])
        if (2 * m) % w:
            w = 2 if (2 * m) % 3 else 3
        r = analyse_law(random_incidence(rng, m, 2, w), m)
        local.append({"part": "local", "kind": "two per variable", **r})
    rows += local
    log("local laws done")

    rec = [r for r in rows if r["part"] == "recovery"]
    tc = [r for r in rec if r["three_connected_graph"]]
    s1 = all(r["gauge_recovered"] == 3 and r["tseitin_recovered"] == 3 for r in tc)
    s2 = all(t["same_allowed_states"] and t["stars_differ"] for t in twists)
    s3 = all((r.get("dual_reading") and r.get("sphere")) if r["planar"] else not r.get("dual_reading") for r in tc)
    s4 = all(r["circuits_are_cycles"] for r in nonbinary)
    three = [r for r in local if r["kind"].startswith("three per") and r.get("three_connected")]
    frac = sum(r["graphic"] or r["cographic"] for r in three) / max(1, len(three))
    ledr = [r for r in local if r["kind"].startswith("Ledrappier")]
    two = [r for r in local if r["kind"] == "two per variable" and r.get("three_connected")]
    s5 = frac <= 0.05 and all(not (r.get("graphic") or r.get("cographic")) for r in ledr) and all(r["cographic"] for r in two)
    controls = {
        "C1_all_cocircuits_reading_fails_somewhere": any(not r["all_cocircuits_reading"] for r in tc),
        "C2_twists_have_identical_allowed_states": all(t["same_allowed_states"] for t in twists),
        "C3_rows_as_vertices_fails_under_scrambling": any(r["rows_as_vertices_match"] < 3 for r in tc),
    }
    summary = {
        "recovery": {"graphs": len(rec), "three_connected": len(tc),
                     "gauge_all_recovered": sum(r["gauge_recovered"] == 3 for r in tc),
                     "tseitin_all_recovered": sum(r["tseitin_recovered"] == 3 for r in tc),
                     "planar_spheres": sum(bool(r.get("sphere")) for r in tc if r["planar"]),
                     "planar": sum(r["planar"] for r in tc),
                     "nonplanar_dual_reading_fails": sum(not r.get("dual_reading") for r in tc if not r["planar"]),
                     "nonplanar": sum(not r["planar"] for r in tc)},
        "twists": {"count": len(twists), "identical_states": sum(t["same_allowed_states"] for t in twists)},
        "nonbinary": {"laws": len(nonbinary), "circuits_are_cycles": sum(r["circuits_are_cycles"] for r in nonbinary)},
        "local": {"three_per_variable_laws": sum(1 for r in local if r["kind"].startswith("three per")),
                  "three_connected": len(three),
                  "graphic_or_cographic": sum(bool(r["graphic"] or r["cographic"]) for r in three),
                  "fraction": round(frac, 4),
                  "ledrappier": [{k: r.get(k) for k in ("kind", "dim", "dual_dim", "three_connected", "graphic", "cographic")}
                                 for r in ledr],
                  "two_per_variable_three_connected": len(two),
                  "two_per_variable_cographic": sum(bool(r["cographic"]) for r in two)},
    }
    result = {"experiment_id": "KNOT-SPACE-20261020-001A-E001", "evidence_stage": "exploratory", "summary": summary,
              "predictions": {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5}, "controls": controls,
              "signal": s1 and s2 and s3 and s4 and s5, "wall_seconds": round(time.time() - START, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (OUT / "raw_rows.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    log(f"summary {json.dumps(summary)}")
    log(f"predictions {result['predictions']} controls {controls} signal {result['signal']}")
    (OUT / "run_output.txt").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    sys.exit(main())
