#!/usr/bin/env python3
"""Producer for TWIST-MAP-20261023-001B-E001: the map of exact twist relations on genus-2 square-tiled surfaces.

Each surface is an L-shaped table L(A, B, C, D): a bottom block of (A + B) x C unit cells and a top block of A x D cells over
columns 0..A-1, with opposite sides glued by translation. Its graph has a bottom and a left edge per cell; edges carry homology
coordinates, their signed crossings with the core curves h1 (row 0), h2 (top row of the top block), v1 (column 0) and v2
(column A). The twist alpha in {0,1}^4 is the class sum alpha_i b_i mod 2; its value on an edge is alpha.o_e mod 2.

Phase 1 (labels.c): every orientation is labelled in each of the 16 twists by its cyclic structure. A cluster is a connected
component of the cyclic edges (edges on a directed cycle of the twisted double cover); the label lists, for every cluster with a
nonzero period lattice, its parity under the twist and its lattice in Hermite normal form.
Phase 2: the closure of (twist, label) pairs under walls (for each odd cluster, the twists dual to the radical of its lattice under
the intersection form) and under the automorphisms of the tiling. P1: every class carries one count. An unexplained equality is a
pair of twists with the same label, equal counts of at least THRESHOLD, in different classes.
Phase 3 (skel.c): per-skeleton counts (the skeleton is the set of cyclic edges) for the twists of the unexplained equalities and of
the control pairs (wall pairs, and pairs with unequal counts).
Phase 4: for every skeleton, the contracted graph: each cluster becomes a point (odd or even), parallel edges are reduced to the set
of their twists, and each even point carries its own gauge. Two twists are related on a skeleton when an isomorphism of these typed
graphs and a gauge carry one twist class onto the other (the identity is tried first).
Phase 5 (factorization control): on sampled skeletons with few edges, the per-skeleton count equals c * A, with c the number of
orientations of the skeleton in which every skeleton edge is cyclic and A the number of acyclic orientations of the contracted graph,
both by brute force; related twists have equal A.

Every orientation and its reversal have the same label and skeleton (a global sheet swap), so enumerations other than the checks
run over masks whose top bit is 0 and are doubled; L(2,2,2,2) is also enumerated in full as the control of the halving.

    python3 -B run.py    writes raw_rows.jsonl (surface by surface) and result.json under artifacts/
"""

from __future__ import annotations

import json
import os
import resource
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "TWIST-MAP-20261023-001B" / HERE.name
WORKERS = min(20, os.cpu_count() or 1)
THRESHOLD = 1000
CONTROL_PAIRS = 20
FACTOR_SAMPLES = 30
FACTOR_MAX_EDGES = 14
ISO_CAP = 100000
CONTROL_SKELETONS = 300
J = ((0, 0, 1, 1), (0, 0, 1, 0), (-1, -1, 0, 0), (-1, 0, 0, 0))     # J[j][k] = b_j . b_k for (h1, h2, v1, v2)
TW = [tuple(t) for t in product((0, 1), repeat=4)]
ROSTER = [  # (family, label, parameters, half)
    ("F_check", "L(2,1,2,1)", (2, 1, 2, 1), False),
    ("F_check", "L(2,2,2,2) full", (2, 2, 2, 2), False),
    ("F_seen", "L(2,2,2,2)", (2, 2, 2, 2), True),
    ("F_seen", "L(3,1,2,2)", (3, 1, 2, 2), True),
    ("F_fresh", "L(2,1,2,3)", (2, 1, 2, 3), True),
    ("F_fresh", "L(2,1,3,2)", (2, 1, 3, 2), True),
    ("F_fresh", "L(2,2,3,1)", (2, 2, 3, 1), True),
    ("F_fresh", "L(2,3,2,2)", (2, 3, 2, 2), True),
    ("F_fresh", "L(2,2,2,3)", (2, 2, 2, 3), True),
    ("F_fresh", "L(3,1,3,1)", (3, 1, 3, 1), True),
]
STEPS = {(1, 0): "r", (-1, 0): "ri", (0, 1): "u", (0, -1): "ui"}
D4 = [((1, 0), (0, 1)), ((0, 1), (-1, 0)), ((-1, 0), (0, -1)), ((0, -1), (1, 0)),
      ((-1, 0), (0, 1)), ((1, 0), (0, -1)), ((0, 1), (1, 0)), ((0, -1), (-1, 0))]


# ------------------------------------------------------------------ surfaces

def l_surface(A, B, C, D):
    cells = [(x, y) for y in range(C) for x in range(A + B)] + [(x, y) for y in range(C, C + D) for x in range(A)]
    pos = {c: i for i, c in enumerate(cells)}
    N = len(cells)
    right = [pos[((x + 1) % (A + B if y < C else A), y)] for (x, y) in cells]
    up = [pos[(x, (y + 1) % (C + D if x < A else C))] for (x, y) in cells]
    left, down = [0] * N, [0] * N
    for s in range(N):
        left[right[s]] = s
        down[up[s]] = s
    parent = list(range(4 * N))                      # corner k of cell s: 0 bottom-left, 1 bottom-right, 2 top-left, 3 top-right

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for s in range(N):
        for a, b in ((4 * s + 1, 4 * right[s]), (4 * s + 2, 4 * up[s]), (4 * s + 3, 4 * right[s] + 2), (4 * s + 3, 4 * up[s] + 1)):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra
    roots = sorted({find(i) for i in range(4 * N)})
    vid = {r: i for i, r in enumerate(roots)}
    corner = lambda s, k: vid[find(4 * s + k)]
    edges = []
    for s, (x, y) in enumerate(cells):
        edges.append((corner(s, 0), corner(s, 1), (0, 0, -int(x == 0), -int(x == A))))
        edges.append((corner(s, 0), corner(s, 2), (int(y == 0), int(y == C + D - 1), 0, 0)))
    V = len(roots)
    assert V - len(edges) + N == -2, "not genus 2"
    for s in range(N):
        b, l, r, t = edges[2 * s][2], edges[2 * s + 1][2], edges[2 * right[s] + 1][2], edges[2 * up[s]][2]
        assert all(b[i] + r[i] - t[i] - l[i] == 0 for i in range(4))
    loops = [[(2 * pos[(x, 0)], 1) for x in range(A + B)], [(2 * pos[(x, C + D - 1)], 1) for x in range(A)],
             [(2 * pos[(0, y)] + 1, 1) for y in range(C + D)], [(2 * pos[(A, y)] + 1, 1) for y in range(C)]]
    for k, loop in enumerate(loops):
        assert [sum(edges[e][2][i] for e, _ in loop) for i in range(4)] == [J[i][k] for i in range(4)]
    return {"cells": cells, "N": N, "V": V, "edges": edges, "loops": loops,
            "move": {"r": right, "u": up, "ri": left, "ui": down}}


def spec_text(surf, twists):
    E = surf["edges"]
    return "\n".join([f"{surf['V']} {len(E)} 4"] + [f"{u} {w} " + " ".join(map(str, o)) for u, w, o in E]
                     + [str(len(twists))] + [" ".join(map(str, a)) for a in twists]) + "\n"


def solve(v):
    """x with J x = v (J is unimodular)."""
    M = [list(map(Fraction, J[i])) + [Fraction(v[i])] for i in range(4)]
    for c in range(4):
        p = next(r for r in range(c, 4) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        for r in range(4):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    x = [M[i][4] / M[i][i] for i in range(4)]
    assert all(q.denominator == 1 for q in x)
    return tuple(int(q) for q in x)


def side_edge(surf, s, side):
    mv = surf["move"]
    return {"b": 2 * s, "l": 2 * s + 1, "t": 2 * mv["u"][s], "r": 2 * mv["r"][s] + 1}[side]


def automorphisms(surf):
    """Cell maps with a constant derivative in D4 that preserve the tiling, with their action on oriented edges."""
    mv, N = surf["move"], surf["N"]
    out = []
    for (d1, d2) in D4:
        for target in range(N):
            sigma, stack, ok = {0: target}, [0], True
            while stack and ok:
                s = stack.pop()
                for step, img in (("r", d1), ("u", d2), ("ri", (-d1[0], -d1[1])), ("ui", (-d2[0], -d2[1]))):
                    t, ts = mv[step][s], mv[STEPS[img]][sigma[s]]
                    if t in sigma:
                        if sigma[t] != ts:
                            ok = False
                            break
                    else:
                        sigma[t] = ts
                        stack.append(t)
            if not ok or len(set(sigma.values())) != N:
                continue
            emap = {}
            for s in range(N):
                for (src, along, offset) in ((2 * s, d1, (-d2[0], -d2[1])), (2 * s + 1, d2, (-d1[0], -d1[1]))):
                    side = {(0, -1): "b", (-1, 0): "l", (0, 1): "t", (1, 0): "r"}[offset]
                    lattice_dir = (1, 0) if side in "bt" else (0, 1)
                    emap[src] = (side_edge(surf, sigma[s], side), 1 if along == lattice_dir else -1)
            out.append(emap)
    return out


def homology_action(surf, emap):
    """A with class(g(gamma)) = A class(gamma), in core coordinates."""
    cols = []
    for loop in surf["loops"]:
        I = [0, 0, 0, 0]
        for (e, sgn) in loop:
            e2, s2 = emap[e]
            for k in range(4):
                I[k] += sgn * s2 * surf["edges"][e2][2][k]
        cols.append(solve(I))
    return [[cols[k][j] for k in range(4)] for j in range(4)]


# ------------------------------------------------------------------ labels, lattices, walls

def hnf_rows(rows):
    m = [list(r) for r in rows if any(r)]
    r = 0
    for c in range(4):
        if r >= len(m):
            break
        while True:
            piv = None
            for i in range(r, len(m)):
                if m[i][c] != 0 and (piv is None or abs(m[i][c]) < abs(m[piv][c])):
                    piv = i
            if piv is None:
                break
            m[r], m[piv] = m[piv], m[r]
            done = True
            for i in range(r + 1, len(m)):
                if m[i][c] != 0:
                    f = int(m[i][c] / m[r][c])
                    m[i] = [a - f * b for a, b in zip(m[i], m[r])]
                    if m[i][c] != 0:
                        done = False
            if done:
                break
        if r >= len(m) or m[r][c] == 0:
            continue
        if m[r][c] < 0:
            m[r] = [-a for a in m[r]]
        for i in range(r):
            f = m[i][c] // m[r][c]
            m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return [tuple(row) for row in m[:r]]


def parse_label(label):
    if label == "-":
        return []
    out = []
    for part in label.split("|"):
        rows = [tuple(int(v) for v in chunk.split(",")) for chunk in part[2:-1].split("][")] if len(part) > 1 else []
        out.append((part[0] == "o", rows))
    return out


def format_label(clusters):
    parts = sorted(("o" if odd else "e") + "".join("[" + ",".join(map(str, r)) + "]" for r in rows) for odd, rows in clusters)
    return "|".join(parts) if parts else "-"


def map_label(label, A):
    out = []
    for odd, rows in parse_label(label):
        img = []
        for I in rows:
            y = [sum(A[i][k] * v for k, v in enumerate(solve(I))) for i in range(4)]
            img.append(tuple(sum(J[j][k] * y[k] for k in range(4)) for j in range(4)))
        out.append((odd, hnf_rows(img)))
    return format_label(out)


def int_kernel(M):
    n = len(M[0])
    m = len(M)
    rows = [[M[i][j] for i in range(m)] + [int(i == j) for i in range(n)] for j in range(n)]
    r = 0
    for c in range(m):
        while True:
            piv = None
            for i in range(r, n):
                if rows[i][c] != 0 and (piv is None or abs(rows[i][c]) < abs(rows[piv][c])):
                    piv = i
            if piv is None:
                break
            rows[r], rows[piv] = rows[piv], rows[r]
            done = True
            for i in range(r + 1, n):
                if rows[i][c] != 0:
                    f = int(rows[i][c] / rows[r][c])
                    rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
                    if rows[i][c] != 0:
                        done = False
            if done:
                break
        if all(rows[i][c] == 0 for i in range(r, n)) and (r >= n or rows[r][c] == 0):
            continue
        r += 1
    return [row[m:] for row in rows[r:] if all(v == 0 for v in row[:m])]


def wall_group(label):
    """Span (mod 2, as twist vectors) of the duals of the radicals of the odd clusters' lattices."""
    gens = []
    for odd, rows in parse_label(label):
        if not odd:
            continue
        B = [solve(I) for I in rows]
        gram = [[sum(B[i][a] * J[a][b] * B[j][b] for a in range(4) for b in range(4)) for j in range(len(B))] for i in range(len(B))]
        for c in int_kernel(gram):
            gens.append(tuple(sum(c[i] * B[i][k] for i in range(len(B))) & 1 for k in range(4)))
    span = {(0, 0, 0, 0)}
    for g in gens:
        span |= {tuple(a ^ b for a, b in zip(s, g)) for s in span}
    return span


class DSU:
    def __init__(self):
        self.p = {}

    def find(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def closure(surf, counts):
    actions = [homology_action(surf, g) for g in automorphisms(surf)]
    dsu = DSU()
    for k in counts:
        dsu.find(k)
    for L in {L for (_q, L) in counts}:
        G = wall_group(L)
        for q in TW:
            for chi in G:
                q2 = tuple(a ^ b for a, b in zip(q, chi))
                if (q, L) in counts or (q2, L) in counts:
                    dsu.union((q, L), (q2, L))
    for A in actions:
        for (q, L) in list(counts):
            q2 = tuple(sum(A[i][k] * q[k] for k in range(4)) & 1 for i in range(4))
            dsu.union((q, L), (q2, map_label(L, A)))
    return dsu, len(actions)


# ------------------------------------------------------------------ enumeration

def run_chunks(binary, text, E, half, extra=()):
    total = 1 << (E - 1 if half else E)
    pieces = WORKERS * 8
    step = -(-total // pieces)
    ranges = [(i * step, min(total, (i + 1) * step)) for i in range(pieces) if i * step < total]

    def one(r):
        return subprocess.run([binary, "exh", str(r[0]), str(r[1]), *extra], input=text, capture_output=True, text=True,
                              check=True).stdout

    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(one, ranges))


def label_counts(binary, surf, half):
    text = spec_text(surf, TW)
    counts, n, mis = {}, {}, {}
    f = 2 if half else 1
    for out in run_chunks(binary, text, len(surf["edges"]), half):
        for line in out.splitlines():
            if line.startswith("sector"):
                p = line.split()
                s = int(p[1])
                n[s] = n.get(s, 0) + f * int(p[2].split("=")[1])
                mis[s] = mis.get(s, 0) + f * int(p[3].split("=")[1])
                continue
            _l, s, rest = line.split(maxsplit=2)
            lab, c = rest.rsplit("=", 1)
            key = (TW[int(s)], lab)
            counts[key] = counts.get(key, 0) + f * int(c)
    return counts, n, mis


def skeleton_counts(binary, surf, targets, half):
    text = spec_text(surf, TW) + f"{len(targets)}\n" + "".join(f"{TW.index(q)} {L}\n" for (q, L) in targets)
    res = {t: {} for t in range(len(targets))}
    f = 2 if half else 1
    for out in run_chunks(binary, text, len(surf["edges"]), half):
        for line in out.splitlines():
            _k, t, rest = line.split()
            mask, c = rest.split("=")
            d = res[int(t)]
            d[int(mask)] = d.get(int(mask), 0) + f * int(c)
    return res


# ------------------------------------------------------------------ contracted graphs

def edge_twists(surf, alpha):
    return [sum(a * o for a, o in zip(alpha, off)) & 1 for (_u, _w, off) in surf["edges"]]


def clusters_of(surf, mask, t):
    """Clusters of the skeleton: vertex -> cluster id, per-cluster gauge (vertex -> sheet) and parity."""
    E = surf["edges"]
    adj = {}
    for e in range(len(E)):
        if mask >> e & 1:
            u, w, _o = E[e]
            adj.setdefault(u, []).append((w, t[e]))
            adj.setdefault(w, []).append((u, t[e]))
    cid, gauge, odd = {}, {}, []
    for v in sorted(adj):
        if v in cid:
            continue
        k = len(odd)
        odd.append(False)
        cid[v], gauge[v] = k, 0
        stack = [v]
        while stack:
            u = stack.pop()
            for w, f in adj[u]:
                if w not in cid:
                    cid[w], gauge[w] = k, gauge[u] ^ f
                    stack.append(w)
                elif gauge[w] != gauge[u] ^ f:
                    odd[k] = True
    return cid, gauge, odd


def contracted(surf, mask, alpha):
    """Typed contracted graph of a skeleton under a twist: node attributes (type, self-loop twist set), simple adjacency, and the
    twist set of every edge whose ends are not odd points (in the even points' own gauges)."""
    E = surf["edges"]
    t = edge_twists(surf, alpha)
    cid, gauge, odd = clusters_of(surf, mask, t)
    node = lambda v: ("c", cid[v]) if v in cid else ("v", v)
    attrs = {}
    for v in range(surf["V"]):
        n = node(v)
        attrs[n] = ["ord" if n[0] == "v" else ("odd" if odd[n[1]] else "even"), set()]
    adj = {n: set() for n in attrs}
    tw = {}
    for e in range(len(E)):
        if mask >> e & 1:
            continue
        u, w, _o = E[e]
        a, b = node(u), node(w)
        th = t[e] ^ gauge.get(u, 0) ^ gauge.get(w, 0)
        if a == b:
            attrs[a][1].add(th)
            continue
        adj[a].add(b)
        adj[b].add(a)
        if attrs[a][0] != "odd" and attrs[b][0] != "odd":
            tw.setdefault(frozenset((a, b)), set()).add(th)
    return {n: (a[0], tuple(sorted(a[1]))) for n, a in attrs.items()}, adj, {k: frozenset(v) for k, v in tw.items()}


def isomorphisms(g1, g2, cap):
    """Isomorphisms of typed simple graphs (attributes and adjacency), by backtracking; yields dicts, stops after cap."""
    at1, adj1 = g1[0], g1[1]
    at2, adj2 = g2[0], g2[1]

    def inv(at, adj, n):
        return (at[n], len(adj[n]), tuple(sorted((at[m], len(adj[m])) for m in adj[n])))

    i1 = {n: inv(at1, adj1, n) for n in at1}
    i2 = {n: inv(at2, adj2, n) for n in at2}
    if sorted(i1.values()) != sorted(i2.values()):
        return
    order = sorted(at1, key=lambda n: (-len(adj1[n]), repr(n)))
    cand = {n: [m for m in at2 if i2[m] == i1[n]] for n in order}
    phi, used, count = {}, set(), [0]

    def extend(k):
        if count[0] >= cap:
            return
        if k == len(order):
            count[0] += 1
            yield dict(phi)
            return
        n = order[k]
        for m in cand[n]:
            if m in used:
                continue
            if any((p in adj1[n]) != (phi[p] in adj2[m]) for p in phi):
                continue
            phi[n] = m
            used.add(m)
            yield from extend(k + 1)
            del phi[n]
            used.discard(m)

    yield from extend(0)


def gauge_compatible(b1, b2, phi):
    """Twists on bundles (pair -> sorted tuple or set of twists): is there a gauge g with b1 = b2 o phi + delta g?"""
    par = {}

    def find(x):
        p = 0
        while x in par:
            x, q = par[x]
            p ^= q
        return x, p

    if len(b1) != len(b2):
        return False
    for key, s1 in b1.items():
        a, b = tuple(key)
        s2 = b2.get(frozenset((phi[a], phi[b])))
        if s2 is None:
            return False
        flip = type(s2)(sorted(1 - x for x in s2)) if isinstance(s2, tuple) else frozenset(1 - x for x in s2)
        allowed = set()
        if s1 == s2:
            allowed.add(0)
        if s1 == flip:
            allowed.add(1)
        if not allowed:
            return False
        if allowed == {0, 1}:
            continue
        want = allowed.pop()
        ra, xa = find(a)
        rb, xb = find(b)
        if ra == rb:
            if xa ^ xb != want:
                return False
        else:
            par[ra] = (rb, xa ^ xb ^ want)
    return True


def series_reduce(edges):
    """Suppress vertices of degree 2 (edges in series): the two edges become one with the sum of their twists. This keeps the
    number of orientations in which every edge is cyclic (series edges must be co-oriented)."""
    edges = [list(e) for e in edges]
    while True:
        deg = {}
        for u, w, _t in edges:
            deg[u] = deg.get(u, 0) + 1
            deg[w] = deg.get(w, 0) + 1
        v = next((v for v, d in sorted(deg.items()) if d == 2 and not any(a == b == v for a, b, _t in edges)), None)
        if v is None or len(edges) <= 1:
            return [tuple(e) for e in edges]
        i, j = [k for k, (a, b, _t) in enumerate(edges) if v in (a, b)]
        a = edges[i][0] if edges[i][1] == v else edges[i][1]
        b = edges[j][0] if edges[j][1] == v else edges[j][1]
        merged = [a, b, edges[i][2] ^ edges[j][2]]
        edges = [e for k, e in enumerate(edges) if k not in (i, j)] + [merged]


def twisted_clusters(surf, mask, alpha):
    """Each cluster, series-reduced, as a twisted multigraph: node attributes (multiset of self-loop twists, degree with
    multiplicity), simple adjacency, and the multiset of twists on each bundle of parallel edges."""
    E = surf["edges"]
    t = edge_twists(surf, alpha)
    cid, _gauge, odd = clusters_of(surf, mask, t)
    raw = {}
    for e in range(len(E)):
        if mask >> e & 1:
            u, w, _o = E[e]
            raw.setdefault(cid[u], []).append((u, w, t[e]))
    res = {}
    for k, edges in raw.items():
        at, adj, bun = {}, {}, {}
        for u, w, th in series_reduce(edges):
            for v in (u, w):
                at.setdefault(v, [[], 0])
                adj.setdefault(v, set())
            at[u][1] += 1
            at[w][1] += 1
            if u == w:
                at[u][0].append(th)
                continue
            adj[u].add(w)
            adj[w].add(u)
            bun.setdefault(frozenset((u, w)), []).append(th)
        res[("c", k)] = ("odd" if odd[k] else "even",
                         ({v: (tuple(sorted(a[0])), a[1]) for v, a in at.items()}, adj, {key: tuple(sorted(v)) for key, v in bun.items()}))
    return res


def cluster_iso(c1, c2):
    if len(c1[0]) != len(c2[0]):
        return False
    for phi in isomorphisms(c1, c2, ISO_CAP):
        if gauge_compatible(c1[2], c2[2], phi):
            return True
    return False


def clusters_match(k1, k2):
    """Is there a type-preserving bijection of clusters under which each twisted cluster is isomorphic to its image?"""
    a, b = list(k1.values()), list(k2.values())
    if sorted(x[0] for x in a) != sorted(x[0] for x in b):
        return False
    ok = [[a[i][0] == b[j][0] and cluster_iso(a[i][1], b[j][1]) for j in range(len(b))] for i in range(len(a))]
    used = set()

    def match(i):
        if i == len(a):
            return True
        for j in range(len(b)):
            if j not in used and ok[i][j]:
                used.add(j)
                if match(i + 1):
                    return True
                used.discard(j)
        return False

    return match(0)


def relation(surf, mask, q1, q2):
    """How the two twists are related on a skeleton: the outside part (contracted graph) by the identity, an isomorphism or not at
    all; the clusters' own part by equal twist classes, isomorphic twisted clusters or not at all."""
    g1, g2 = contracted(surf, mask, q1), contracted(surf, mask, q2)
    k1, k2 = twisted_clusters(surf, mask, q1), twisted_clusters(surf, mask, q2)
    ident = {n: n for n in g1[0]}
    if g1[0] == g2[0] and gauge_compatible(g1[2], g2[2], ident):
        outside = "identity"
    else:
        outside, n = "none", 0
        for phi in isomorphisms(g1, g2, ISO_CAP):
            n += 1
            if gauge_compatible(g1[2], g2[2], phi):
                outside = "isomorphism"
                break
        if outside == "none" and n >= ISO_CAP:
            outside = "undecided"
    same = set(k1) == set(k2) and all(k1[p][0] == k2[p][0] and k1[p][1][0] == k2[p][1][0]
                                      and gauge_compatible(k1[p][1][2], k2[p][1][2], {v: v for v in k1[p][1][0]}) for p in k1)
    inside = "identity" if same else ("isomorphic" if clusters_match(k1, k2) else "unmatched")
    return outside, inside


def explained(rel):
    return rel[0] in ("identity", "isomorphism") and rel[1] in ("identity", "isomorphic")


# ------------------------------------------------------------------ factorization control (brute force)

def acyclic(nodes, arcs):
    indeg = {n: 0 for n in nodes}
    out = {n: [] for n in nodes}
    for a, b in arcs:
        out[a].append(b)
        indeg[b] += 1
    stack = [n for n in nodes if indeg[n] == 0]
    seen = 0
    while stack:
        a = stack.pop()
        seen += 1
        for b in out[a]:
            indeg[b] -= 1
            if indeg[b] == 0:
                stack.append(b)
    return seen == len(nodes)


def lift_arcs(a, b, th, x, ta, tb):
    """Arcs of one edge between contracted nodes a (tail) and b (head) with twist th and orientation x; odd points have one lift."""
    def L(n, s, typ):
        return (n, 0) if typ == "odd" else (n, s)
    if x:
        return [(L(a, 0, ta), L(b, th, tb)), (L(b, 1 - th, tb), L(a, 1, ta))]
    return [(L(b, th, tb), L(a, 0, ta)), (L(a, 1, ta), L(b, 1 - th, tb))]


def factor_check(surf, mask, alpha, measured):
    """Brute-force c (skeleton orientations with every skeleton edge cyclic) and A (acyclic orientations of the reduced contracted
    graph); returns (c, A, c * A == measured)."""
    E = surf["edges"]
    t = edge_twists(surf, alpha)
    sk = [e for e in range(len(E)) if mask >> e & 1]
    # c: every skeleton edge on a directed cycle of the cover restricted to the skeleton (both ends of an arc in one component)
    c = 0
    for bits in range(1 << len(sk)):
        out = {}
        for i, e in enumerate(sk):
            u, w, _o = E[e]
            for (p, q) in lift_arcs(("v", u), ("v", w), t[e], bits >> i & 1, "ord", "ord"):
                out.setdefault(p, []).append(q)
        comp = scc(out)
        if all(comp[(("v", E[e][0]), 0)] == comp[(("v", E[e][1]), t[e])] for e in sk):
            c += 1
    at, adj, tw = contracted(surf, mask, alpha)
    redges = []                                       # reduced edges: (a, b, twist); odd-incident edges carry twist 0
    for a in at:
        for b in adj[a]:
            if repr(a) < repr(b):
                if at[a][0] == "odd" or at[b][0] == "odd":
                    redges.append((a, b, 0))
                else:
                    for th in sorted(tw[frozenset((a, b))]):
                        redges.append((a, b, th))
    for a in at:
        for th in sorted(at[a][1]):
            redges.append((a, a, th))
    nodes = [(n, s) for n in at for s in ((0,) if at[n][0] == "odd" else (0, 1))]
    A = 0
    if len(redges) > FACTOR_MAX_EDGES:
        return c, None, None
    for bits in range(1 << len(redges)):
        arcs = []
        for i, (a, b, th) in enumerate(redges):
            arcs += lift_arcs(a, b, th, bits >> i & 1, at[a][0], at[b][0])
        if acyclic(nodes, arcs):
            A += 1
    return c, A, c * A == measured


def scc(out):
    """Strong components (Tarjan, iterative) of a dict digraph; returns node -> component id."""
    nodes = set(out)
    for vs in out.values():
        nodes.update(vs)
    index, low, comp, onst, st = {}, {}, {}, set(), []
    cnt = [0]
    for r in nodes:
        if r in index:
            continue
        work = [(r, iter(out.get(r, ())))]
        index[r] = low[r] = cnt[0]
        cnt[0] += 1
        st.append(r)
        onst.add(r)
        while work:
            v, it = work[-1]
            nxt = next(it, None)
            if nxt is not None:
                if nxt not in index:
                    index[nxt] = low[nxt] = cnt[0]
                    cnt[0] += 1
                    st.append(nxt)
                    onst.add(nxt)
                    work.append((nxt, iter(out.get(nxt, ()))))
                elif nxt in onst:
                    low[v] = min(low[v], index[nxt])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == index[v]:
                    while True:
                        w = st.pop()
                        onst.discard(w)
                        comp[w] = v
                        if w == v:
                            break
    return comp


# ------------------------------------------------------------------ analysis per surface

def tstr(q):
    return "".join(map(str, q))


def analyse_surface(skel_bin, row, surf, half):
    counts = {(tuple(q), L): n for q, L, n in row["counts"]}
    dsu, nauto = closure(surf, counts)
    groups = {}
    for k in list(dsu.p):
        groups.setdefault(dsu.find(k), []).append(k)
    p1_fail = []
    for members in groups.values():
        if len({counts.get(k, 0) for k in members}) > 1:
            p1_fail.append(sorted([[tstr(q), L, counts.get((q, L), 0)] for (q, L) in members])[:6])
    labels = sorted({L for (_q, L) in counts})
    unexpl, walls, unequal = [], [], []
    for L in labels:
        nz = [(q, counts[(q, L)]) for q in TW if counts.get((q, L), 0) >= THRESHOLD]
        G = wall_group(L)
        for i in range(len(nz)):
            for j in range(i + 1, len(nz)):
                (q1, n1), (q2, n2) = nz[i], nz[j]
                same = dsu.find((q1, L)) == dsu.find((q2, L))
                if n1 == n2 and not same:
                    unexpl.append((L, q1, q2, n1))
                if tuple(a ^ b for a, b in zip(q1, q2)) in G:
                    walls.append((L, q1, q2, n1))
                if n1 != n2:
                    unequal.append((L, q1, q2, min(n1, n2)))
    walls = sorted(walls, key=lambda r: (-r[3], r[0], r[1], r[2]))[:CONTROL_PAIRS]
    unequal = sorted(unequal, key=lambda r: (-r[3], r[0], r[1], r[2]))[:CONTROL_PAIRS]
    pairs = [("unexplained", r) for r in unexpl] + [("wall", r) for r in walls] + [("unequal", r) for r in unequal]
    targets = sorted({(q, L) for _kind, (L, q1, q2, _n) in pairs for q in (q1, q2)})
    tix = {t: i for i, t in enumerate(targets)}
    sk = skeleton_counts(skel_bin, surf, targets, half) if targets else {}
    sums_ok = all(sum(sk[tix[(q, L)]].values()) == counts[(q, L)] for (q, L) in targets)
    records, soundness, unsound = [], [], []
    for kind, (L, q1, q2, n) in pairs:
        a, b = sk[tix[(q1, L)]], sk[tix[(q2, L)]]
        masks = sorted(set(a) | set(b))
        per = []
        for m in masks:
            rel = relation(surf, m, q1, q2) if kind == "unexplained" or len(per) < CONTROL_SKELETONS else None
            per.append((m, a.get(m, 0), b.get(m, 0), rel))
        checked = [p for p in per if p[3] is not None]
        tally = {}
        for _m, _x, _y, r in checked:
            tally["/".join(r)] = tally.get("/".join(r), 0) + 1
        rec = {"kind": kind, "label": L, "twists": [tstr(q1), tstr(q2)], "counts": [counts[(q1, L)], counts[(q2, L)]],
               "skeletons": len(masks), "checked": len(checked), "skeleton_wise_equal": all(x == y for _m, x, y, _r in per),
               "relations": tally, "all_explained": len(checked) == len(per) and all(explained(r) for _m, _x, _y, r in checked),
               "outside_related_all": all(r[0] in ("identity", "isomorphism") for _m, _x, _y, r in checked)}
        if kind != "unequal":
            rec["per_skeleton"] = [[m, x, y, list(r) if r else None] for m, x, y, r in per][:400]
        records.append(rec)
        for m, x, y, r in checked:
            if explained(r):
                soundness.append((L, q1, q2, m, x, y, r))
                if x != y:
                    unsound.append([L, tstr(q1), tstr(q2), m, x, y, list(r)])
    # factorization control on sampled skeletons with few edges
    samples = []
    seen = set()
    for (L, q1, q2, m, x, y, r) in soundness:
        if bin(m).count("1") > FACTOR_MAX_EDGES or (m, q1, q2) in seen:
            continue
        seen.add((m, q1, q2))
        samples.append((L, q1, q2, m, x, y, r))
    samples = samples[:FACTOR_SAMPLES * 3]
    factor = []
    for (L, q1, q2, m, x, y, r) in samples:
        c1, A1, ok1 = factor_check(surf, m, q1, x)
        c2, A2, ok2 = factor_check(surf, m, q2, y)
        if A1 is None or A2 is None:
            continue
        factor.append({"label": L, "twists": [tstr(q1), tstr(q2)], "mask": m, "measured": [x, y], "c": [c1, c2], "A": [A1, A2],
                       "factorizes": ok1 and ok2, "related_A_equal": A1 == A2, "relation": list(r)})
        if len(factor) >= FACTOR_SAMPLES:
            break
    return {"automorphisms": nauto, "labels": len(labels), "classes": len(groups), "P1_failures": p1_fail[:20],
            "unsound_skeletons": unsound[:50], "unsound_count": len(unsound),
            "P1_failure_count": len(p1_fail), "unexplained": len([r for r in records if r["kind"] == "unexplained"]),
            "skeleton_sums_match": sums_ok, "pairs": records, "factorization": factor}


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / "raw_rows.jsonl"
    if raw.exists():
        raw.unlink()
    started = time.time()
    build = Path(tempfile.mkdtemp(prefix="twistmap-"))
    lab_bin, skel_bin = str(build / "labels"), str(build / "skel")
    subprocess.run(["gcc", "-O2", "-o", lab_bin, str(HERE / "labels.c")], check=True)
    subprocess.run(["gcc", "-O2", "-o", skel_bin, str(HERE / "skel.c")], check=True)
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    rows = []
    try:
        for fam, label, params, half in ROSTER:
            surf = l_surface(*params)
            counts, n, mis = label_counts(lab_bin, surf, half)
            row = {"family": fam, "label": label, "params": list(params), "vertices": surf["V"], "edges": len(surf["edges"]),
                   "half_enumeration": half, "n": {tstr(TW[s]): n[s] for s in sorted(n)}, "mis": {tstr(TW[s]): mis[s] for s in sorted(mis)},
                   "counts": sorted([[list(q), L, c] for (q, L), c in counts.items()])}
            if fam != "F_check":
                row["analysis"] = analyse_surface(skel_bin, row, surf, half)
            rows.append(row)
            with open(raw, "a") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")
            print(fam, label, len(surf["edges"]), round(time.time() - started), flush=True)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    fails = []
    for r in rows:
        for q, v in r["n"].items():
            if v != 1 << r["edges"]:
                fails.append(f"orientations {r['label']} {q}")
        if any(r["mis"].values()):
            fails.append(f"swap-invariance test {r['label']}")
        tot = {}
        for q, L, c in r["counts"]:
            tot[tstr(q)] = tot.get(tstr(q), 0) + c
        if any(v != 1 << r["edges"] for v in tot.values()) or len(tot) != 16:
            fails.append(f"label totals {r['label']}")
        a = r.get("analysis")
        if a:
            if not a["skeleton_sums_match"]:
                fails.append(f"skeleton sums {r['label']}")
            for p in a["pairs"]:
                if p["kind"] == "wall" and not (p["skeleton_wise_equal"] and p["relations"].get("identity/identity", 0) == p["checked"]):
                    fails.append(f"wall pair not absorbed skeleton by skeleton {r['label']} {p['label']} {p['twists']}")
            if a["unsound_count"]:
                fails.append(f"explained skeletons with unequal counts {r['label']} ({a['unsound_count']})")
            for fct in a["factorization"]:
                if not (fct["factorizes"] and fct["related_A_equal"]):
                    fails.append(f"factorization {r['label']} {fct['label']} {fct['twists']} {fct['mask']}")
    full = next(r for r in rows if r["label"] == "L(2,2,2,2) full")
    half = next(r for r in rows if r["label"] == "L(2,2,2,2)")
    if full["counts"] != half["counts"]:
        fails.append("half enumeration differs from the full one on L(2,2,2,2)")
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not fails, "control_failures": fails[:50],
              "rows": len(rows), "compiler": gcc, "workers": WORKERS, "threshold": THRESHOLD}
    if fails:
        result["verdict"] = "invalid"
    else:
        fresh = [r for r in rows if r["family"] == "F_fresh"]
        p1 = all(r["analysis"]["P1_failure_count"] == 0 for r in rows if r.get("analysis"))
        un = [(r["label"], p) for r in fresh for p in r["analysis"]["pairs"] if p["kind"] == "unexplained"]
        p2_incomplete = any(p["skeleton_wise_equal"] and p["skeletons"] >= 2 for _l, p in un)
        p3_fail = [[l, p["label"], p["twists"], p["counts"][0], p["skeletons"], p["skeleton_wise_equal"], p["relations"]]
                   for l, p in un if not (p["skeleton_wise_equal"] and p["all_explained"])]
        seen_un = [(r["label"], p) for r in rows if r["family"] == "F_seen" for p in r["analysis"]["pairs"] if p["kind"] == "unexplained"]
        result["summary"] = {
            "P1_predicted_equalities_hold": p1,
            "P2_walls_and_symmetries_incomplete": p2_incomplete,
            "P3_local_mechanism_explains_all": not p3_fail,
            "P3_failures": p3_fail,
            "unexplained_fresh": len(un),
            "unexplained_fresh_by_surface": {r["label"]: r["analysis"]["unexplained"] for r in fresh},
            "unexplained_seen": len(seen_un),
            "unexplained_seen_local": sum(1 for _l, p in seen_un if p["skeleton_wise_equal"] and p["all_explained"]),
            "relations_fresh": {k: sum(p["relations"].get(k, 0) for _l, p in un)
                                for k in sorted({k for _l, p in un for k in p["relations"]})},
        }
        if not p1:
            result["verdict"] = "refuted"
        elif p2_incomplete and not p3_fail:
            result["verdict"] = "supported"
        else:
            result["verdict"] = "partially supported"
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds") if k in result}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
