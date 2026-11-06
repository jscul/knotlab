#!/usr/bin/env python3
"""Check the strong-component reduction of fair not-all-equal worlds.

Standard library only. A torus is Z^2 modulo the lattice spanned by w1 = (Lh, 0) and w2 = (s, Lv); the parity of a
period vector a*w1 + b*w2 is p(a, b) = a*Lh + b*(s + Lv) mod 2, and the torus is twisted when p is not zero.

- Theorem 1: consistency of the world (an independent propagation solver, and exhaustive assignment marking on 3 x 3)
  equals the absence of a strongly connected component of the literal graph containing both literals of a variable.
- Theorem 2: that test equals "the projected cyclic edges have a cluster with an odd cycle" (two-colouring), equals
  "a cross cluster or an odd winding" (homology lattices), and every cross cluster has the whole period lattice.
- Theorem 3: on plane grids every orientation makes each edge cyclic in exactly one of the primal and dual orientations.
- Theorem 4: on twisted tori the primal and dual cyclic edges of the twisted orientation are complementary for every
  pattern; for the untwisted orientation of a torus there are orientations where they are not.
- Theorem 5: on twisted tori the counts of all-contractible and cross configurations are equal, consistency is
  contractible plus even windings, and the emergence lies between -log2(1 - P0) and -log2 P0.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- tori

class Torus:
    def __init__(self, Lh: int, Lv: int, s: int) -> None:
        self.Lh, self.Lv, self.s = Lh, Lv, s
        self.V = Lh * Lv
        self.p1, self.p2 = Lh % 2, (s + Lv) % 2
        self.twisted = bool(self.p1 or self.p2)
        # edges: index 2v (step (1,0)) and 2v+1 (step (0,1)); target, lattice offset (a, b), parity of the offset
        self.edges = []
        for v in range(self.V):
            x, y = v % Lh, v // Lh
            for step in ((1, 0), (0, 1)):
                w, off, par = self.reduce(x + step[0], y + step[1])
                self.edges.append((v, w, step, off, par))
        # faces are indexed by their lower-left corner; dual edge of edge (v, step) joins (below, above) or (left, right)
        self.dual = []
        for (v, w, step, off, par) in self.edges:
            x, y = v % Lh, v // Lh
            if step == (1, 0):
                f0, off0, par0 = self.reduce(x, y - 1)       # below
            else:
                f0, off0, par0 = self.reduce(x - 1, y)       # left
            self.dual.append((f0, off0, par0, v))            # (other face, its offset, its parity, own face = v)

    def reduce(self, X: int, Y: int):
        q = Y // self.Lv
        X1, Y1 = X - q * self.s, Y - q * self.Lv
        r = X1 // self.Lh
        X2 = X1 - r * self.Lh
        return Y1 * self.Lh + X2, (r, q), (r * self.p1 + q * self.p2) % 2

    def parity(self, a: int, b: int) -> int:
        return (a * self.p1 + b * self.p2) % 2


# ---------------------------------------------------------------- digraphs

def closure(adj: list[int]) -> list[int]:
    """Reachability bitmasks (reflexive) by Warshall's algorithm on bitsets."""
    n = len(adj)
    reach = [adj[i] | (1 << i) for i in range(n)]
    for k in range(n):
        bk, rk = 1 << k, reach[k]
        for i in range(n):
            if reach[i] & bk:
                reach[i] |= rk
    return reach


def twisted_arcs(T: Torus, spokes: list[int]):
    """Literal graph of the world: node 2v+h means h_v = h. Spoke 1 on {u,w}: (u,1)->(w,0), (w,1)->(u,0); spoke 0:
    (u,0)->(w,1), (w,0)->(u,1). Returns adjacency and, per edge, its arc from the lift whose tail literal is the spoke."""
    adj = [0] * (2 * T.V)
    lift = []
    for e, (v, w, step, off, par) in enumerate(T.edges):
        x = spokes[e]
        a, b = 2 * v + x, 2 * w + (1 - x)
        c, d = 2 * w + x, 2 * v + (1 - x)
        adj[a] |= 1 << b
        adj[c] |= 1 << d
        lift.append((a, b))
    return adj, lift


def twisted_dual_arcs(T: Torus, spokes: list[int]):
    """Rotate every lifted arc by +90 degrees. Lifted vertex (v, k) has h-value (x + y + k) mod 2; along an edge the
    sheet changes by the parity of the lattice offset. The arc of a lift points along +step iff its tail's h-value
    equals the spoke. East arcs rotate to arcs from the face below to the face above; north arcs rotate to arcs from
    the right face to the left face. Dual nodes are 2f + sheet."""
    adj = [0] * (2 * T.V)
    arcs = []
    for e, (v, w, step, off, par) in enumerate(T.edges):
        x, y = v % T.Lh, v // T.Lh
        f0, off0, par0 = T.dual[e][0], T.dual[e][1], T.dual[e][2]
        per_lift = []
        for k in (0, 1):
            h_tail = (x + y + k) % 2
            forward = h_tail == spokes[e]
            own, other = 2 * v + k, 2 * f0 + (k ^ par0)      # face "above"/"right" is v's own face, sheet k
            if step == (1, 0):
                src, dst = (other, own) if forward else (own, other)     # +x: below -> above
            else:
                src, dst = (own, other) if forward else (other, own)     # +y: right -> left
            adj[src] |= 1 << dst
            per_lift.append((src, dst))
        arcs.append(per_lift[0])
    return adj, arcs


def untwisted_arcs(T: Torus, bits: list[int]):
    adj, adjd, arcs, arcsd = [0] * T.V, [0] * T.V, [], []
    for e, (v, w, step, off, par) in enumerate(T.edges):
        f0 = T.dual[e][0]
        fwd = bits[e] == 1
        a, b = (v, w) if fwd else (w, v)
        adj[a] |= 1 << b
        arcs.append((a, b))
        if step == (1, 0):
            src, dst = (f0, v) if fwd else (v, f0)
        else:
            src, dst = (v, f0) if fwd else (f0, v)
        adjd[src] |= 1 << dst
        arcsd.append((src, dst))
    return adj, arcs, adjd, arcsd


def cyclic(reach: list[int], arcs) -> list[bool]:
    return [bool((reach[b] >> a) & 1) for a, b in arcs]


# ---------------------------------------------------------------- topology of an edge set on the torus

def hnf_add(lat, vec):
    rows = [list(r) for r in lat] + [list(vec)]
    rows = [r for r in rows if r[0] or r[1]]
    if not rows:
        return []
    # eliminate the first column
    while sum(1 for r in rows if r[0]) > 1:
        rows.sort(key=lambda r: (abs(r[0]) if r[0] else 10 ** 9))
        piv = rows[0]
        for r in rows[1:]:
            if r[0]:
                q = r[0] // piv[0]
                r[0] -= q * piv[0]
                r[1] -= q * piv[1]
    first = [r for r in rows if r[0]]
    g2 = 0
    for r in rows:
        if not r[0]:
            g2 = math.gcd(g2, r[1])
    if not first:
        return [(0, g2)] if g2 else []
    a, b = first[0]
    if a < 0:
        a, b = -a, -b
    if g2 == 0:
        return [(a, b)]
    return [(a, b % g2), (0, g2)]


def topology(T: Torus, chosen: list[bool], dual: bool = False):
    """Clusters of the chosen edges (primal edges of T, or dual edges of T* when dual=True).
    Returns per cluster: (vertices, lattice basis) and the two-colouring verdict (has an odd cycle)."""
    n = T.V
    parent, pot = list(range(n)), [(0, 0)] * n

    def find(u):
        path = []
        while parent[u] != u:
            path.append(u)
            u = parent[u]
        root = u
        # recompute potentials along the path (from root outward)
        acc = (0, 0)
        for node in reversed(path):
            p = pot[node]
            acc = (acc[0] + p[0], acc[1] + p[1])
            pot[node] = acc
            parent[node] = root
        return root

    lat = {u: [] for u in range(n)}
    adj = [[] for _ in range(n)]
    for e, use in enumerate(chosen):
        if not use:
            continue
        if not dual:
            v, w, step, off, par = T.edges[e]
            a, b, offv = v, w, off
        else:
            f0, off0, par0, own = T.dual[e]
            # dual edge from face f0 to face own; own = f0 shifted back by the inverse of off0
            a, b, offv = f0, own, (-off0[0], -off0[1])
        adj[a].append((b, offv))
        adj[b].append((a, (-offv[0], -offv[1])))
        ra, rb = find(a), find(b)
        pa, pb = pot[a], pot[b]
        if ra == rb:
            d = (pa[0] + offv[0] - pb[0], pa[1] + offv[1] - pb[1])
            if d != (0, 0):
                L = lat[ra]
                for vec in [d]:
                    L = hnf_add(L, vec)
                lat[ra] = L
        else:
            parent[rb] = ra
            pot[rb] = (pa[0] + offv[0] - pb[0], pa[1] + offv[1] - pb[1])
            L = lat[ra]
            for vec in lat[rb]:
                L = hnf_add(L, vec)
            lat[ra] = L
    clusters = {}
    for u in range(n):
        clusters.setdefault(find(u), []).append(u)
    # independent odd-cycle test by two-colouring (parity of lengths); the walk length parity is the steps' parity
    colour = [-1] * n
    odd_by_root = {}
    for u in range(n):
        if colour[u] >= 0:
            continue
        colour[u] = 0
        stack, odd = [u], False
        while stack:
            z = stack.pop()
            for (t, _) in adj[z]:
                if colour[t] < 0:
                    colour[t] = 1 - colour[z]
                    stack.append(t)
                elif colour[t] == colour[z]:
                    odd = True
        odd_by_root[find(u)] = odd_by_root.get(find(u), False) or odd
    out = []
    for r, verts in clusters.items():
        out.append((verts, lat[r], odd_by_root.get(r, False)))
    return out


def classify(T: Torus, clusters):
    """Global topology: ('contractible',), ('cross',), or ('winding', primitive class); plus odd-cluster flags."""
    kind, cls, odd_hom, odd_col, cross_full = "contractible", None, False, False, True
    for verts, L, odd in clusters:
        odd_col = odd_col or odd
        if len(L) == 2:
            kind = "cross"
            cross_full = cross_full and (L[0][0] == 1 and L[1][1] == 1)
            if T.parity(*L[0]) or T.parity(*L[1]):
                odd_hom = True
        elif len(L) == 1:
            a, b = L[0]
            g = math.gcd(a, b)
            c = (a // g, b // g)
            if c[0] < 0 or (c[0] == 0 and c[1] < 0):
                c = (-c[0], -c[1])
            if kind != "cross":
                kind, cls = "winding", c
            if T.parity(a, b):
                odd_hom = True
    return kind, cls, odd_hom, odd_col, cross_full


# ---------------------------------------------------------------- an independent solver for the world

def solve_world(T: Torus, spokes: list[int]) -> bool:
    """Two-literal propagation (Even-Itai-Shamir): fix a free variable, propagate forced values; on a contradiction
    undo and try the other value; if both fail the world is inconsistent. Constraint on {u,w}: not h_u = h_w = spoke."""
    nbrs = [[] for _ in range(T.V)]
    for e, (v, w, step, off, par) in enumerate(T.edges):
        nbrs[v].append((w, spokes[e]))
        nbrs[w].append((v, spokes[e]))
    val = [-1] * T.V

    def propagate(start, value):
        trial = {start: value}
        stack = [start]
        while stack:
            u = stack.pop()
            for w, x in nbrs[u]:
                if trial[u] == x:                    # u equals the spoke, so w must differ from it
                    need = 1 - x
                    have = trial.get(w, val[w] if val[w] >= 0 else None)
                    if have is None:
                        trial[w] = need
                        stack.append(w)
                    elif have != need:
                        return None
        return trial

    for v in range(T.V):
        if val[v] >= 0:
            continue
        for value in (0, 1):
            t = propagate(v, value)
            if t is not None:
                for u, b in t.items():
                    val[u] = b
                break
        else:
            return False
    return all(not (val[v] == val[w] == spokes[e]) for e, (v, w, *_r) in enumerate(T.edges))


def consistent_set_exhaustive(T: Torus) -> bytearray:
    """All consistent spoke patterns: each assignment h allows exactly the patterns whose spoke differs from the common
    value on every monochromatic edge; mark the union of these subcubes."""
    E = len(T.edges)
    ok = bytearray(1 << E)
    for h in range(1 << T.V):
        fixed_mask = fixed_val = 0
        for e, (v, w, *_r) in enumerate(T.edges):
            hv, hw = (h >> v) & 1, (h >> w) & 1
            if hv == hw:
                fixed_mask |= 1 << e
                if hv == 0:
                    fixed_val |= 1 << e
        free = ((1 << E) - 1) & ~fixed_mask
        sub = free
        while True:
            ok[fixed_val | sub] = 1
            if sub == 0:
                break
            sub = (sub - 1) & free
    return ok


# ---------------------------------------------------------------- one twisted pattern

def analyse_twisted(T: Torus, spokes: list[int]):
    adj, lift = twisted_arcs(T, spokes)
    reach = closure(adj)
    inc_scc = any((reach[2 * v] >> (2 * v + 1)) & 1 and (reach[2 * v + 1] >> (2 * v)) & 1 for v in range(T.V))
    cyc = cyclic(reach, lift)
    clusters = topology(T, cyc)
    kind, cls, odd_hom, odd_col, cross_full = classify(T, clusters)
    adjd, arcsd = twisted_dual_arcs(T, spokes)
    reachd = closure(adjd)
    cycd = cyclic(reachd, arcsd)
    complementary = all(a != b for a, b in zip(cyc, cycd))
    dkind, dcls, *_ = classify(T, topology(T, cycd, dual=True))
    return {"inc_scc": inc_scc, "odd_col": odd_col, "odd_hom": odd_hom, "cross_full": cross_full, "kind": kind,
            "cls": cls, "complementary": complementary, "dual_kind": dkind, "dual_cls": dcls}


def twisted_family(T: Torus, patterns, solver_check, exhaustive_ok=None):
    tally = {"n": 0, "cons": 0, "contr": 0, "cross": 0, "odd_wind": 0, "even_wind": 0}
    bad = {"solver": 0, "scc_vs_colour": 0, "scc_vs_homology": 0, "cross_not_full": 0, "not_complementary": 0,
           "trichotomy": 0, "cons_identity": 0}
    E = len(T.edges)
    for t in patterns:
        spokes = [(t >> e) & 1 for e in range(E)]
        r = analyse_twisted(T, spokes)
        cons = not r["inc_scc"]
        if exhaustive_ok is not None:
            if bool(exhaustive_ok[t]) != cons:
                bad["solver"] += 1
        elif solver_check and solve_world(T, spokes) != cons:
            bad["solver"] += 1
        bad["scc_vs_colour"] += r["inc_scc"] != r["odd_col"]
        bad["scc_vs_homology"] += r["inc_scc"] != r["odd_hom"]
        bad["cross_not_full"] += r["kind"] == "cross" and not r["cross_full"]
        bad["not_complementary"] += not r["complementary"]
        expect = {"contractible": "cross", "cross": "contractible", "winding": "winding"}[r["kind"]]
        if r["dual_kind"] != expect or (r["kind"] == "winding" and r["dual_cls"] != r["cls"]):
            bad["trichotomy"] += 1
        tally["n"] += 1
        tally["cons"] += cons
        if r["kind"] == "contractible":
            tally["contr"] += 1
        elif r["kind"] == "cross":
            tally["cross"] += 1
        elif T.parity(*r["cls"]):
            tally["odd_wind"] += 1
        else:
            tally["even_wind"] += 1
        even_or_contr = r["kind"] == "contractible" or (r["kind"] == "winding" and not T.parity(*r["cls"]))
        bad["cons_identity"] += cons != even_or_contr
    return tally, bad


# ---------------------------------------------------------------- plane grids (Theorem 3)

def plane_grid(nx: int, ny: int):
    """Grid of nx x ny vertices; faces: inner squares (i, j) and the outer face. Returns edges with dual face pairs."""
    V = nx * ny
    inner = (nx - 1) * (ny - 1)
    outer = inner
    def face(i, j):
        return j * (nx - 1) + i if 0 <= i < nx - 1 and 0 <= j < ny - 1 else outer
    edges = []
    for y in range(ny):
        for x in range(nx):
            v = y * nx + x
            if x + 1 < nx:
                edges.append((v, v + 1, (1, 0), face(x, y - 1), face(x, y)))      # below, above
            if y + 1 < ny:
                edges.append((v, v + nx, (0, 1), face(x - 1, y), face(x, y)))     # left, right
    return V, inner + 1, edges


def plane_check(nx: int, ny: int) -> dict:
    V, F, edges = plane_grid(nx, ny)
    E = len(edges)
    bad = 0
    count_cyc = [0] * E
    for t in range(1 << E):
        adj, adjd, arcs, arcsd = [0] * V, [0] * F, [], []
        for e, (v, w, step, f_lo, f_hi) in enumerate(edges):
            fwd = (t >> e) & 1
            a, b = (v, w) if fwd else (w, v)
            adj[a] |= 1 << b
            arcs.append((a, b))
            if step == (1, 0):
                src, dst = (f_lo, f_hi) if fwd else (f_hi, f_lo)       # +x rotates to below -> above
            else:
                src, dst = (f_hi, f_lo) if fwd else (f_lo, f_hi)       # +y rotates to right -> left
            adjd[src] |= 1 << dst
            arcsd.append((src, dst))
        cyc = cyclic(closure(adj), arcs)
        cycd = cyclic(closure(adjd), arcsd)
        bad += sum(1 for a, b in zip(cyc, cycd) if a == b)
        for e in range(E):
            count_cyc[e] += cyc[e]
    return {"grid": f"{nx}x{ny}", "orientations": 1 << E, "edges_cyclic_in_both_or_neither": bad,
            "mean_cyclic_fraction": round(sum(count_cyc) / (E * (1 << E)), 6)}


# ---------------------------------------------------------------- main

def run() -> dict:
    checks, controls = {}, {}
    # Theorems 1, 2, 4, 5 exhaustively on twisted 3 x 3 tori
    exhaustive = {}
    for (Lh, Lv, s) in ((3, 3, 0), (3, 3, 1)):
        T = Torus(Lh, Lv, s)
        ok = consistent_set_exhaustive(T)
        tally, bad = twisted_family(T, range(1 << len(T.edges)), False, exhaustive_ok=ok)
        exhaustive[f"{Lh}x{Lv} s={s} parity=({T.p1},{T.p2})"] = {"tally": tally, "violations": bad}
    checks["exhaustive_twisted_3x3"] = exhaustive
    # sampled on larger twisted tori, with the independent propagation solver
    rng = random.Random(20261022)
    sampled = {}
    for (Lh, Lv, s, n) in ((5, 5, 0, 1500), (5, 4, 0, 1500), (5, 5, 2, 1500), (7, 5, 3, 800), (5, 3, 0, 1500)):
        T = Torus(Lh, Lv, s)
        if not T.twisted:
            continue
        E = len(T.edges)
        pats = [rng.getrandbits(E) for _ in range(n)]
        tally, bad = twisted_family(T, pats, True)
        sampled[f"{Lh}x{Lv} s={s} parity=({T.p1},{T.p2})"] = {"tally": tally, "violations": bad}
    checks["sampled_twisted"] = sampled
    # Theorem 3 on plane grids, all orientations
    checks["plane_complementarity"] = [plane_check(3, 3), plane_check(2, 4)]
    # Theorem 4, the untwisted side: complementarity fails for some orientations
    T = Torus(3, 3, 0)
    fails, both_cyclic_edges, n = 0, 0, 20000
    rng = random.Random(7)
    for _ in range(n):
        bits = [rng.getrandbits(1) for _ in T.edges]
        adj, arcs, adjd, arcsd = untwisted_arcs(T, bits)
        cyc, cycd = cyclic(closure(adj), arcs), cyclic(closure(adjd), arcsd)
        both = sum(1 for a, b in zip(cyc, cycd) if a and b)
        neither = sum(1 for a, b in zip(cyc, cycd) if not a and not b)
        assert neither == 0                     # Minty: an edge not cyclic is on a dicut, whose dual is cyclic
        if both:
            fails += 1
            both_cyclic_edges += both
    checks["untwisted_3x3_sampled"] = {"orientations": n, "with_doubly_cyclic_edges": fails, "doubly_cyclic_edges": both_cyclic_edges}
    # Theorem 5 sandwich on the exhaustive tori
    sandwich = {}
    for key, v in exhaustive.items():
        t = v["tally"]
        P0 = t["contr"] / t["n"]
        E = -math.log2(t["cons"] / t["n"])
        sandwich[key] = {"P0": round(P0, 6), "E": round(E, 6), "lower": round(-math.log2(1 - P0), 6),
                         "upper": round(-math.log2(P0), 6), "inside": -math.log2(1 - P0) <= E <= -math.log2(P0)}
    checks["emergence_sandwich"] = sandwich

    # controls
    T = Torus(3, 3, 0)
    rng = random.Random(11)
    # (a) a single sheet: test only one literal of each variable for self-reachability -> must disagree with the solver
    disagree = 0
    for _ in range(3000):
        spokes = [rng.getrandbits(1) for _ in T.edges]
        adj, _l = twisted_arcs(T, spokes)
        reach = closure(adj)
        wrong = any((reach[2 * v + 1] >> (2 * v)) & 1 for v in range(T.V))  # one forced variable is not a contradiction
        disagree += wrong != (not solve_world(T, spokes))
    controls["single_sheet_test_rejected"] = disagree > 0
    # (b) rotating north arcs the wrong way breaks plane complementarity
    V, F, edges = plane_grid(3, 3)
    broke = False
    for t in range(1 << len(edges)):
        adj, adjd, arcs, arcsd = [0] * V, [0] * F, [], []
        for e, (v, w, step, f_lo, f_hi) in enumerate(edges):
            fwd = (t >> e) & 1
            a, b = (v, w) if fwd else (w, v)
            adj[a] |= 1 << b
            arcs.append((a, b))
            src, dst = (f_lo, f_hi) if fwd else (f_hi, f_lo)               # wrong for north edges
            adjd[src] |= 1 << dst
            arcsd.append((src, dst))
        if any(a == b for a, b in zip(cyclic(closure(adj), arcs), cyclic(closure(adjd), arcsd))):
            broke = True
            break
    controls["wrong_rotation_rejected"] = broke
    # (c) the untwisted orientation does not satisfy the twisted identity P0 = P(cross)
    contr = cross = 0
    rng = random.Random(13)
    for _ in range(4000):
        bits = [rng.getrandbits(1) for _ in T.edges]
        adj, arcs, _a, _b = untwisted_arcs(T, bits)
        kind = classify(T, topology(T, cyclic(closure(adj), arcs)))[0]
        contr += kind == "contractible"
        cross += kind == "cross"
    controls["untwisted_duality_rejected"] = abs(contr - cross) > 6 * math.sqrt(contr + cross)
    checks["untwisted_3x3_topology"] = {"orientations": 4000, "contractible": contr, "cross": cross}

    failures = []
    for key, v in list(exhaustive.items()) + list(sampled.items()):
        for name, count in v["violations"].items():
            if count:
                failures.append(f"{key}: {name} {count}")
    for key, v in exhaustive.items():
        if v["tally"]["contr"] != v["tally"]["cross"]:
            failures.append(f"{key}: contractible {v['tally']['contr']} != cross {v['tally']['cross']}")
    for g in checks["plane_complementarity"]:
        if g["edges_cyclic_in_both_or_neither"]:
            failures.append(f"plane {g['grid']}: complementarity fails")
    if checks["untwisted_3x3_sampled"]["with_doubly_cyclic_edges"] == 0:
        failures.append("untwisted: no doubly cyclic edge found")
    for key, v in sandwich.items():
        if not v["inside"]:
            failures.append(f"{key}: emergence outside the sandwich")
    failures += [f"control {k}" for k, ok in controls.items() if not ok]
    return {"checks": checks, "controls": controls, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
        "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
        "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
        "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"],
        "checks": outcome["checks"], "controls": outcome["controls"], "failures": outcome["failures"],
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv[1:]:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != result:
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: strong-component reduction checked")
    for f in outcome["failures"]:
        print("  failed:", f)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
