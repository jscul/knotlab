#!/usr/bin/env python3
"""Checks for KNOT-SPACE-20261020-001B-P001. The statements are in proof.md.

A parity law's allowed states are a coset of a code C, and its knot matroid
is the column matroid of C. The graph reading of a code takes as vertices the
minimal supports whose deletion leaves the matroid connected. It succeeds
when every variable lies in two vertices and the resulting cut space is the
code.

Checks:
- Lemma. The circuits of a random coset of a binary code, computed by brute
  force over its states relative to each variable's range, are the minimal
  supports of the dual code with at least two elements.
- Proposition 2. Gauge laws over Z2, Z3, Z4 and S3 on random connected
  graphs have the cycles as circuits, and Tseitin laws with random charges
  have the bonds (brute force over allowed states).
- Theorem 3:
  - (a) the reading recovers the vertex stars of random 3-connected graphs;
    on a 2-connected graph with a 2-separation the reading is not the star
    family;
  - (b) Whitney twists of random 2-connected graphs give identical cut and
    cycle spaces.
- Theorem 4. On 3-connected planar graphs, the readings of the cut space
  and of the cycle space give a sphere: every edge lies in two faces, the
  faces at each vertex form one cycle, the read graph is connected, and
  V - E + F = 2. Also checked on the sphere-carrying local law of
  KNOT-SPACE-20261020-001C-E001, which is written on no graph.
- Theorem 5:
  - every random binary code is spanned by its minimal supports, so a code
    is determined by its matroid;
  - the reading fails on F7, F7*, M*(K5) and M*(K3,3), which are
    3-connected;
  - it succeeds on M(K5) and M(K3,3);
  - on 40 random 3-connected codes (half of them disguised graphs), the
    reading succeeds exactly when an exhaustive search over families of
    minimal supports finds a graph realization.
- Census agreement with KNOT-SPACE-20261020-001A-E001 and
  KNOT-SPACE-20261020-001C-E001. The realization search re-decides the
  graphic and cographic verdicts of C's 13 three-connected local laws.

Controls, each of which must be rejected:
- 'reading from all minimal supports';
- 'allowed states determine the graph exactly' (twists);
- 'the reading needs no 3-connectivity' (a 2-separated graph);
- 'a law written on no graph carries none' (the sphere-carrying local law).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS_A = ROOT / "artifacts" / "KNOT-SPACE-20261020-001A" / "KNOT-SPACE-20261020-001A-E001_space_census"
CENSUS_C = ROOT / "artifacts" / "KNOT-SPACE-20261020-001C" / "KNOT-SPACE-20261020-001C-E001_embeddings_and_local_laws"
SPHERE_LAW = (16, [2826, 82, 8467, 644, 9472, 18720, 4682, 49280])


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


# ------------------------------------------------------------------ gauge laws over a group

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


def group_ops(name):
    if name == "Z2":
        return 2, (lambda a, b: (a - b) % 2)
    if name == "Z3":
        return 3, (lambda a, b: (a - b) % 3)
    if name == "Z4":
        return 4, (lambda a, b: (a - b) % 4)
    return 6, (lambda a, b: s3mul(a, s3inv(b)))


def gauge_states_any(n, edges, name):
    q, sub = group_ops(name)
    out = set()
    for pot in product(range(q), repeat=n - 1):
        p = (0,) + pot
        out.add(tuple(sub(p[a], p[b]) for a, b in edges))
    return out


def random_connected(rng, n, p):
    while True:
        edges = [e for e in combinations(range(n), 2) if rng.random() < p]
        if is_connected_graph(n, edges):
            return edges


def fano():
    cols = [c for c in range(1, 8)]
    rows = [sum(1 << j for j, c in enumerate(cols) if c >> i & 1) for i in range(3)]
    return 7, rows


def links_are_cycles(verts, faces, m):
    """Each face meets each vertex star in 0 or 2 edges, and the faces at each vertex form one cycle."""
    for v in verts:
        at_v = [j for j in range(m) if v >> j & 1]
        adj = {j: [] for j in at_v}
        for f in faces:
            common = [j for j in at_v if f >> j & 1]
            if not common:
                continue
            if len(common) != 2:
                return False
            a, b = common
            adj[a].append(b)
            adj[b].append(a)
        if any(len(x) != 2 for x in adj.values()):
            return False
        seen, stack = {at_v[0]}, [at_v[0]]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        if len(seen) != len(at_v):
            return False
    return True


def sphere_cells(basis_cut, m):
    """(V, E, F, every edge in two faces, every vertex link one cycle, read graph connected), or None."""
    okv, verts = graph_reading(basis_cut, m)
    dual = kernel(basis_cut, m)
    okf, faces = graph_reading(dual, m)
    if not (okv and okf):
        return None
    per_edge = [sum(1 for f in faces if f >> j & 1) for j in range(m)]
    read_edges = [tuple(i for i, v in enumerate(verts) if v >> j & 1) for j in range(m)]
    return (len(verts), m, len(faces), all(c == 2 for c in per_edge), links_are_cycles(verts, faces, m),
            is_connected_graph(len(verts), read_edges))


def is_sphere(cells):
    return bool(cells) and cells[0] - cells[1] + cells[2] == 2 and all(cells[3:])


def realizable(basis, m):
    """Independent graphicness test for a 3-connected code: search all families of minimal supports that
    cover each coordinate exactly twice and span the code (a graph realization; its stars are cocircuits)."""
    target = canonical(basis)
    dim = len(rref(basis))
    by_coord = [[c for c in minimal_supports(basis) if c >> j & 1] for j in range(m)]

    def search(chosen, counts, saturated):
        if all(k == 2 for k in counts):
            return canonical(chosen) == target
        if len(chosen) >= dim + 1:
            return False
        best = None
        for j in range(m):
            if counts[j] < 2:
                opts = [c for c in by_coord[j] if c not in chosen and not c & saturated]
                if best is None or len(opts) < len(best[1]):
                    best = (j, opts)
                    if not opts:
                        return False
        for c in best[1]:
            new, sat = list(counts), saturated
            for i in range(m):
                if c >> i & 1:
                    new[i] += 1
                    if new[i] == 2:
                        sat |= 1 << i
            if search(chosen + [c], new, sat):
                return True
        return False

    return search([], [0] * m, 0)


def states_of(words, m):
    return {tuple(w >> j & 1 for j in range(m)) for w in words}


def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random(20261020)

    lemma = {"cosets": 0, "circuits_are_dual_supports": 0}
    for _ in range(40):
        mm = rng.randint(4, 9)
        C = [b for _, b in rref([rng.getrandbits(mm) for _ in range(rng.randint(1, mm - 1))])]
        if not C:
            continue
        a = rng.getrandbits(mm)
        S = states_of([a ^ w for w in codewords(C)], mm)
        predicted = sorted(tuple(j for j in range(mm) if y >> j & 1) for y in minimal_supports(kernel(C, mm))
                           if bin(y).count("1") >= 2)
        lemma["cosets"] += 1
        lemma["circuits_are_dual_supports"] += sorted(relative_circuits(S, mm)) == predicted
    checks["lemma_parity_circuits"] = lemma
    if lemma["circuits_are_dual_supports"] != lemma["cosets"]:
        failures.append("parity lemma")

    prop2 = {"laws": 0, "circuits_are_cycles": 0, "tseitin_laws": 0, "tseitin_circuits_are_bonds": 0}
    for _ in range(14):
        n = rng.randint(4, 5)
        edges = random_connected(rng, n, 0.55)
        if len(edges) > 9:
            edges = edges[:9]
            if not is_connected_graph(n, edges):
                continue
        m = len(edges)
        cycles = sorted(tuple(j for j in range(m) if c >> j & 1) for c in minimal_supports(cycle_space(n, edges))) \
            if cycle_space(n, edges) else []
        for name in ("Z2", "Z3", "Z4", "S3"):
            S = gauge_states_any(n, edges, name)
            prop2["laws"] += 1
            prop2["circuits_are_cycles"] += sorted(relative_circuits(S, m)) == cycles
        star = stars(n, edges)
        x0 = rng.getrandbits(m)
        charge = [bin(x0 & s).count("1") % 2 for s in star]
        S = states_of([x for x in range(1 << m) if all(bin(x & s).count("1") % 2 == charge[v] for v, s in enumerate(star))], m)
        bonds = sorted(tuple(j for j in range(m) if b >> j & 1) for b in minimal_supports(cut_space(n, edges))
                       if bin(b).count("1") >= 2)
        prop2["tseitin_laws"] += 1
        prop2["tseitin_circuits_are_bonds"] += sorted(relative_circuits(S, m)) == bonds
    checks["proposition_2_gauge_and_tseitin_circuits"] = prop2
    if prop2["circuits_are_cycles"] != prop2["laws"] or prop2["tseitin_circuits_are_bonds"] != prop2["tseitin_laws"]:
        failures.append("Proposition 2")

    thm3 = {"three_connected_graphs": 0, "recovered": 0, "twists": 0, "twists_identical": 0}
    for i in range(30):
        if i % 2 == 0:
            n, edges = random_cubic(rng, (8, 10, 12)[i % 3])
        else:
            while True:
                n = rng.randint(6, 9)
                edges = [e for e in combinations(range(n), 2) if rng.random() < 0.55]
                if three_connected_graph(n, edges) and len(edges) <= 22:
                    break
        m = len(edges)
        ok, verts = graph_reading(cut_space(n, edges), m)
        thm3["three_connected_graphs"] += 1
        thm3["recovered"] += ok and sorted(verts) == sorted(stars(n, edges))
    for _ in range(8):
        while True:
            a, b = rng.randint(4, 6), rng.randint(4, 6)
            e1 = [e for e in combinations(range(a), 2) if rng.random() < 0.6]
            e2 = [e for e in combinations(range(b), 2) if rng.random() < 0.6]
            relabel = {0: 0, 1: 1}
            for v in range(2, b):
                relabel[v] = a + v - 2
            n = a + b - 2
            g1 = [tuple(sorted(e)) for e in e1]
            g2 = [tuple(sorted((relabel[x], relabel[y]))) for x, y in e2 if (x, y) != (0, 1)]
            keep = [e for e in g2 if e not in g1]
            swap = {0: 1, 1: 0}
            edges = g1 + keep
            edges_t = g1 + [tuple(sorted((swap.get(x, x), swap.get(y, y)))) for x, y in keep]
            if len(set(edges)) != len(edges) or len(set(edges_t)) != len(edges_t):
                continue
            if not all(is_connected_graph(n, edges, removed={v}) for v in range(n)) or not is_connected_graph(n, edges):
                continue
            if sorted(stars(n, edges)) == sorted(stars(n, edges_t)):
                continue
            break
        thm3["twists"] += 1
        thm3["twists_identical"] += canonical(cut_space(n, edges)) == canonical(cut_space(n, edges_t)) and \
            canonical(cycle_space(n, edges)) == canonical(cycle_space(n, edges_t))
    checks["theorem_3_recovery_and_twists"] = thm3
    if thm3["recovered"] != thm3["three_connected_graphs"] or thm3["twists_identical"] != thm3["twists"]:
        failures.append("Theorem 3")

    thm4 = {}
    planar = {"K4": complete(4), "cube": cube(), "octahedron": octahedron(), "W6": wheel(6), "prism 5": prism(5),
              "antiprism 5": antiprism(5)}
    for i in range(6):
        planar[f"stacked {i}"] = stacked_triangulation(rng, rng.randint(6, 9))
    for name, (n, edges) in planar.items():
        cells = sphere_cells(cut_space(n, edges), len(edges))
        thm4[name] = {"cells": cells, "sphere": is_sphere(cells)}
    m, cons = SPHERE_LAW
    C = [b for _, b in rref(kernel(cons, m))]
    cells = sphere_cells(C, m)
    faces = graph_reading(kernel(C, m), m)[1]
    thm4["local law written on no graph"] = {"cells": cells, "three_connected": three_connected(C, m),
                                            "constraints_that_are_faces": sum(c in faces for c in cons),
                                            "constraints": len(cons), "sphere": is_sphere(cells)}
    checks["theorem_4_spheres"] = thm4
    if not all(v["sphere"] for v in thm4.values()):
        failures.append("Theorem 4")

    thm5 = {"codes": 0, "spanned_by_minimal_supports": 0}
    for _ in range(80):
        mm = rng.randint(6, 13)
        k = rng.randint(2, min(8, mm - 1))
        basis = [rng.getrandbits(mm) for _ in range(k)]
        basis = [b for _, b in rref(basis)]
        if not basis:
            continue
        thm5["codes"] += 1
        thm5["spanned_by_minimal_supports"] += canonical(minimal_supports(basis)) == canonical(basis)
    f7m, f7rows = fano()
    f7dual = kernel(f7rows, f7m)
    n5, e5 = complete(5)
    n33, e33 = bipartite(3, 3)
    thm5["F7 reading fails"] = not graph_reading(f7rows, f7m)[0] and three_connected(f7rows, f7m)
    thm5["F7* reading fails"] = not graph_reading(f7dual, f7m)[0] and three_connected(f7dual, f7m)
    thm5["M*(K5) reading fails"] = not graph_reading(cycle_space(n5, e5), len(e5))[0]
    thm5["M*(K33) reading fails"] = not graph_reading(cycle_space(n33, e33), len(e33))[0]
    thm5["M(K5) and M(K33) readings succeed"] = graph_reading(cut_space(n5, e5), len(e5))[0] and \
        graph_reading(cut_space(n33, e33), len(e33))[0]
    search = {"three_connected_codes": 0, "agree": 0, "graphic": 0}
    while search["three_connected_codes"] < 40:
        if search["three_connected_codes"] % 2 == 0:
            n = rng.randint(5, 7)
            edges = [e for e in combinations(range(n), 2) if rng.random() < 0.6]
            if not three_connected_graph(n, edges):
                continue
            mm = len(edges)
            perm = list(range(mm))
            rng.shuffle(perm)
            basis = [sum(1 << perm[j] for j in range(mm) if b >> j & 1) for b in cut_space(n, edges)]
        else:
            mm = rng.randint(9, 12)
            basis = [b for _, b in rref([rng.getrandbits(mm) for _ in range(rng.randint(mm // 3, 2 * mm // 3))])]
        if not three_connected(basis, mm):
            continue
        found = realizable(basis, mm)
        search["three_connected_codes"] += 1
        search["graphic"] += found
        search["agree"] += graph_reading(basis, mm)[0] == found
    thm5["reading_against_realization_search"] = search
    checks["theorem_5_recognition"] = thm5
    if thm5["spanned_by_minimal_supports"] != thm5["codes"] or search["agree"] != search["three_connected_codes"] or \
            not 0 < search["graphic"] < search["three_connected_codes"] or not all(
            v for k2, v in thm5.items() if k2 not in ("codes", "spanned_by_minimal_supports", "reading_against_realization_search")):
        failures.append("Theorem 5")

    census = {}
    if (CENSUS_A / "result.json").exists() and (CENSUS_C / "result.json").exists():
        a = json.loads((CENSUS_A / "result.json").read_text())
        c = json.loads((CENSUS_C / "result.json").read_text())
        local = [json.loads(line) for line in (CENSUS_C / "raw_rows.jsonl").read_text().splitlines()]
        local = [r for r in local if r["part"] == "local" and r.get("three_connected")]
        agree = 0
        for r in local:
            Cl = [b for _, b in rref(kernel(r["constraints"], r["m"]))]
            agree += (realizable(Cl, r["m"]), realizable(kernel(Cl, r["m"]), r["m"])) == (r["graphic"], r["cographic"])
        census = {"A_predictions": a["predictions"], "C_predictions": c["predictions"],
                  "A_three_connected_recovered": a["summary"]["recovery"]["gauge_all_recovered"],
                  "C_planarity_agreement": c["summary"]["planarity"]["dual_reading_agrees"],
                  "C_local": c["summary"]["local"],
                  "C_three_connected_local_laws": len(local), "C_local_verdicts_confirmed_by_search": agree}
        if not (a["predictions"]["S1"] and a["predictions"]["S2"] and a["predictions"]["S4"] and c["predictions"]["T1"]) \
                or agree != len(local):
            failures.append("census agreement")
    checks["census_agreement"] = census

    n, edges = cube()
    controls["reading_from_all_minimal_supports"] = {"cube": graph_reading(cut_space(n, edges), len(edges), use_all=True)[0],
                                                     "rejected": not graph_reading(cut_space(n, edges), len(edges), use_all=True)[0]}
    controls["allowed_states_determine_the_graph_exactly"] = {"twists_with_identical_states": thm3["twists_identical"],
                                                             "rejected": thm3["twists_identical"] > 0}
    # two copies of K4 glued along the edge 01: {0, 1} is a 2-separation
    two_sep_n, two_sep = 6, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 4), (0, 5), (1, 4), (1, 5), (4, 5)]
    ok, verts = graph_reading(cut_space(two_sep_n, two_sep), len(two_sep))
    two_connected_only = not three_connected_graph(two_sep_n, two_sep)
    controls["reading_needs_no_three_connectivity"] = {
        "graph_three_connected": not two_connected_only,
        "reading_gives_stars": ok and sorted(verts) == sorted(stars(two_sep_n, two_sep)),
        "rejected": two_connected_only and not (ok and sorted(verts) == sorted(stars(two_sep_n, two_sep)))}
    controls["a_law_written_on_no_graph_carries_none"] = {"sphere_law": thm4["local law written on no graph"]["sphere"],
                                                          "rejected": thm4["local law written on no graph"]["sphere"]}
    for name, control in controls.items():
        if not control["rejected"]:
            failures.append(f"control not rejected: {name}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
