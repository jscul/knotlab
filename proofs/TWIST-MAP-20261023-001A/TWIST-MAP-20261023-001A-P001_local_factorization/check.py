#!/usr/bin/env python3
"""Check of TWIST-MAP-20261023-001A-P001 (standard library only).

- Theorem 1 (factorization) and Corollary 1 (reductions): every orientation of L(2,1,2,1) is enumerated in all 16 twists and grouped
  by skeleton; on sampled (twist, skeleton) pairs the count equals c * A, with c by brute force over the skeleton and over its
  series reduction, and A by brute force over the remaining edges and over the parallel-reduced shrunken graph.
- Matroid reading: on the same samples c = T(0, 2) of the frame matroid of the skeleton and A = T(2, 0) of the contraction.
- Lemma W: for random clusters (skeletons of random orientations) of L(2,2,2,2), L(3,1,2,2) and L(3,2,2,2), the boundary walks of the
  ribbon subgraph (face tracing with the tiling's rotation system) have classes spanning exactly the radical of the cluster's lattice,
  and the edges in each boundary walk's corners form a cocycle of class PD(its class) mod 2.
- Corollary 3 (walls): for random orientations with odd clusters, the twist plus the dual of a boundary class of an odd cluster keeps the
  label, leaves the shrunken graph and the clusters' twists unchanged up to switching, and the brute-force c * A agree.
- Proposition 4 and Corollary 3 on a whole surface: on L(2,1,2,1), N(q, E) = N(g q, g E) for every automorphism g of the tiling,
  and N(q, E) = N(q + chi, E) for every chi in the wall group of E.
- Remark 5: on every L-shaped surface of the roster the tiling has a vertex of degree 12 and only square faces, so its dual (all degrees
  4, one face of degree 12) is not isomorphic to it.
- Controls (each must be rejected): skipping the even clusters' gauge in the shrunken graph breaks the factorization; series-reducing
  the shrunken graph (instead of parallel-reducing it) changes A; parallel-reducing a cluster changes c; a twist that is not a wall
  changes some count.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
JM = ((0, 0, 1, 1), (0, 0, 1, 0), (-1, -1, 0, 0), (-1, 0, 0, 0))
TWISTS = [tuple((i >> (3 - k)) & 1 for k in range(4)) for i in range(16)]


# ------------------------------------------------------------------ surfaces with rotation systems

class Surface:
    def __init__(self, A, B, C, D):
        self.params = (A, B, C, D)
        W, H = A + B, C + D
        self.cells = [(x, y) for y in range(C) for x in range(W)] + [(x, y) for y in range(C, H) for x in range(A)]
        idx = {c: i for i, c in enumerate(self.cells)}
        N = len(self.cells)
        self.right = [idx[((x + 1) % (W if y < C else A), y)] for (x, y) in self.cells]
        self.up = [idx[(x, (y + 1) % (H if x < A else C))] for (x, y) in self.cells]
        parent = list(range(4 * N))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for s in range(N):
            for a, b in ((4 * s + 1, 4 * self.right[s]), (4 * s + 2, 4 * self.up[s]), (4 * s + 3, 4 * self.right[s] + 2),
                         (4 * s + 3, 4 * self.up[s] + 1)):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[rb] = ra
        roots = sorted({find(i) for i in range(4 * N)})
        vid = {r: i for i, r in enumerate(roots)}
        corner = lambda s, k: vid[find(4 * s + k)]
        self.V = len(roots)
        self.edges = []
        for s, (x, y) in enumerate(self.cells):
            self.edges.append((corner(s, 0), corner(s, 1), (0, 0, -int(x == 0), -int(x == A))))
            self.edges.append((corner(s, 0), corner(s, 2), (int(y == 0), int(y == H - 1), 0, 0)))
        assert self.V - len(self.edges) + N == -2
        # rotation: counterclockwise successor of each edge-end (edge, 0 = tail, 1 = head), one relation per cell corner
        self.succ = {}
        for s in range(N):
            b, l, t, r = 2 * s, 2 * s + 1, 2 * self.up[s], 2 * self.right[s] + 1
            self.succ[(b, 0)] = (l, 0)        # bottom-left corner: east -> north
            self.succ[(r, 0)] = (b, 1)        # bottom-right corner: north -> west
            self.succ[(t, 1)] = (r, 1)        # top-right corner: west -> south
            self.succ[(l, 1)] = (t, 0)        # top-left corner: south -> east
        assert len(self.succ) == 2 * len(self.edges)
        self.faces = [(2 * s, 2 * self.right[s] + 1, 2 * self.up[s], 2 * s + 1) for s in range(N)]   # b, r, t, l (boundary b + r - t - l)
        self.loops = [[2 * idx[(x, 0)] for x in range(W)], [2 * idx[(x, H - 1)] for x in range(A)],
                      [2 * idx[(0, y)] + 1 for y in range(H)], [2 * idx[(A, y)] + 1 for y in range(C)]]
        self.degree = {}
        for u, w, _o in self.edges:
            self.degree[u] = self.degree.get(u, 0) + 1
            self.degree[w] = self.degree.get(w, 0) + 1


def solve(v):
    M = [list(map(Fraction, JM[i])) + [Fraction(v[i])] for i in range(4)]
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


def twist_of(S, alpha):
    return [sum(a * o for a, o in zip(alpha, off)) & 1 for (_u, _w, off) in S.edges]


# ------------------------------------------------------------------ covers and skeletons

def arcs_of(u, w, b, t):
    return [((u, 0), (w, t)), ((w, 1 - t), (u, 1))] if b else [((w, t), (u, 0)), ((u, 1), (w, 1 - t))]


def scc(nodes, arcs):
    out = {n: [] for n in nodes}
    rev = {n: [] for n in nodes}
    for a, b in arcs:
        out[a].append(b)
        rev[b].append(a)
    seen, order = set(), []
    for s in nodes:
        if s in seen:
            continue
        seen.add(s)
        stack = [(s, 0)]
        while stack:
            v, i = stack.pop()
            if i < len(out[v]):
                stack.append((v, i + 1))
                w = out[v][i]
                if w not in seen:
                    seen.add(w)
                    stack.append((w, 0))
            else:
                order.append(v)
    comp = {}
    for s in reversed(order):
        if s in comp:
            continue
        comp[s] = s
        stack = [s]
        while stack:
            v = stack.pop()
            for w in rev[v]:
                if w not in comp:
                    comp[w] = s
                    stack.append(w)
    return comp


def skeleton(S, x, t):
    nodes = [(v, s) for v in range(S.V) for s in (0, 1)]
    arcs = []
    for (u, w, _o), b, te in zip(S.edges, x, t):
        arcs += arcs_of(u, w, b, te)
    comp = scc(nodes, arcs)
    return frozenset(e for e, (u, w, _o) in enumerate(S.edges) if comp[(u, 0)] == comp[(w, t[e])])


def clusters(S, lam, t):
    """vertex -> cluster id, gauge (sheet of the cluster's first lift) and per-cluster parity"""
    adj = {}
    for e in lam:
        u, w, _o = S.edges[e]
        adj.setdefault(u, []).append((w, t[e]))
        adj.setdefault(w, []).append((u, t[e]))
    cid, gauge, odd = {}, {}, {}
    for v in sorted(adj):
        if v in cid:
            continue
        cid[v], gauge[v], odd[v] = v, 0, False
        stack = [v]
        while stack:
            a = stack.pop()
            for b, f in adj[a]:
                if b not in cid:
                    cid[b], gauge[b] = v, gauge[a] ^ f
                    stack.append(b)
                elif gauge[b] != gauge[a] ^ f:
                    odd[v] = True
    return cid, gauge, odd


def hermite(rows):
    m = [list(r) for r in rows if any(r)]
    r = 0
    for c in range(4):
        live = [i for i in range(r, len(m)) if m[i][c] != 0]
        if not live:
            continue
        while len(live) > 1:
            p = min(live, key=lambda i: abs(m[i][c]))
            for i in live:
                if i != p:
                    f = m[i][c] // m[p][c]
                    m[i] = [a - f * b for a, b in zip(m[i], m[p])]
            live = [i for i in range(r, len(m)) if m[i][c] != 0]
        p = live[0]
        m[r], m[p] = m[p], m[r]
        if m[r][c] < 0:
            m[r] = [-a for a in m[r]]
        for i in range(r):
            f = m[i][c] // m[r][c]
            m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return tuple(tuple(row) for row in m[:r])


def lattice(S, es):
    """generators (I-coordinates) of the period lattice of a connected edge set"""
    adj, pot, gens = {}, {}, []
    for e in es:
        u, w, o = S.edges[e]
        adj.setdefault(u, []).append((w, o, 1))
        adj.setdefault(w, []).append((u, o, -1))
    for start in adj:
        if start in pot:
            continue
        pot[start] = (0, 0, 0, 0)
        stack = [start]
        while stack:
            u = stack.pop()
            for w, o, sg in adj[u]:
                p = tuple(a + sg * b for a, b in zip(pot[u], o))
                if w not in pot:
                    pot[w] = p
                    stack.append(w)
                elif p != pot[w]:
                    gens.append(tuple(a - b for a, b in zip(p, pot[w])))
    return gens


def label(S, lam, t, alpha):
    cid, _g, odd = clusters(S, lam, t)
    groups = {}
    for e in lam:
        groups.setdefault(cid[S.edges[e][0]], []).append(e)
    parts = []
    for k, es in groups.items():
        h = hermite(lattice(S, es))
        if h:
            parts.append(("o" if odd[k] else "e") + "".join("[" + ",".join(map(str, r)) + "]" for r in h))
    return "|".join(sorted(parts)) if parts else "-"


# ------------------------------------------------------------------ the two factors

def c_count(edges, lam_edges):
    """orientations of the skeleton edges (u, w, t) in which every edge is cyclic"""
    vs = sorted({v for u, w, _t in lam_edges for v in (u, w)})
    nodes = [(v, s) for v in vs for s in (0, 1)]
    n = 0
    for bits in range(1 << len(lam_edges)):
        arcs = []
        for i, (u, w, t) in enumerate(lam_edges):
            arcs += arcs_of(u, w, bits >> i & 1, t)
        comp = scc(nodes, arcs)
        if all(comp[(u, 0)] == comp[(w, t)] for u, w, t in lam_edges):
            n += 1
    return n


def series_reduce(es):
    es = [list(e) for e in es]
    while True:
        deg = {}
        for u, w, _t in es:
            deg[u] = deg.get(u, 0) + 1
            deg[w] = deg.get(w, 0) + 1
        cand = [v for v in sorted(deg) if deg[v] == 2 and not any(a == b == v for a, b, _t in es)]
        if not cand or len(es) <= 1:
            return [tuple(e) for e in es]
        v = cand[0]
        i, j = [k for k, (a, b, _t) in enumerate(es) if v in (a, b)]
        a = es[i][0] if es[i][1] == v else es[i][1]
        b = es[j][0] if es[j][1] == v else es[j][1]
        es = [e for k, e in enumerate(es) if k not in (i, j)] + [[a, b, es[i][2] ^ es[j][2]]]


def shrunk(S, lam, t, use_gauge=True):
    """Nodes (with types) and the remaining edges as (a, b, theta) between nodes."""
    cid, gauge, odd = clusters(S, lam, t)
    node = lambda v: ("K", cid[v]) if v in cid else ("v", v)
    types = {}
    for v in range(S.V):
        types[node(v)] = "ord" if v not in cid else ("odd" if odd[cid[v]] else "even")
    rest = []
    for e, (u, w, _o) in enumerate(S.edges):
        if e in lam:
            continue
        g = (gauge.get(u, 0) ^ gauge.get(w, 0)) if use_gauge else 0
        rest.append((node(u), node(w), t[e] ^ g))
    return types, rest


def a_count(types, rest):
    nodes = [(n, s) for n, ty in types.items() for s in ((0,) if ty == "odd" else (0, 1))]
    lift = lambda n, s: (n, 0) if types[n] == "odd" else (n, s)
    good = 0
    for bits in range(1 << len(rest)):
        arcs = []
        for i, (a, b, th) in enumerate(rest):
            for (p, ps), (q, qs) in arcs_of(a, b, bits >> i & 1, th):
                arcs.append((lift(p, ps), lift(q, qs)))
        comp = scc(nodes, arcs)
        if all(comp[n] == n for n in nodes) and not any(p == q for p, q in arcs):
            good += 1
    return good


def parallel_reduce(types, rest):
    keep = set()
    for a, b, th in rest:
        if types[a] == "odd" or types[b] == "odd":
            th = 0
        key = (a, b, th) if repr(a) <= repr(b) else (b, a, th)
        keep.add(key)
    return sorted(keep, key=repr)


# ------------------------------------------------------------------ matroid reading

def frame_rank(edges, S_idx, verts):
    par = {v: (v, 0) for v in verts}
    bal = {v: True for v in verts}

    def find(x):
        p = 0
        while par[x][0] != x:
            x, q = par[x][0], p ^ par[x][1]
            p = q
        return x, p

    for i in S_idx:
        u, w, th = edges[i]
        (ru, pu), (rw, pw) = find(u), find(w)
        if ru == rw:
            if pu ^ pw ^ th:
                bal[ru] = False
        else:
            par[rw] = (ru, pu ^ pw ^ th)
            bal[ru] = bal[ru] and bal[rw]
    roots = {find(v)[0] for v in verts}
    return len(verts) - sum(1 for r in roots if bal[r])


def tutte_eval(edges, verts, x, y, contract=()):
    """T(x, y) of the frame matroid on `edges` (after contracting the edge indices in `contract`), by the rank expansion."""
    rest = [i for i in range(len(edges)) if i not in set(contract)]
    rc = frame_rank(edges, contract, verts)
    rE = frame_rank(edges, list(range(len(edges))), verts) - rc
    total = Fraction(0)
    for bits in range(1 << len(rest)):
        sub = [rest[i] for i in range(len(rest)) if bits >> i & 1]
        r = frame_rank(edges, list(contract) + sub, verts) - rc
        total += Fraction(x - 1) ** (rE - r) * Fraction(y - 1) ** (len(sub) - r)
    return total


# ------------------------------------------------------------------ boundary walks (Lemma W)

def boundary_walks(S, es):
    """Boundary walks of the ribbon subgraph on edge set es: lists of darts (edge, direction +1 tail->head / -1)."""
    es = set(es)
    nxt = {}
    for end, s in S.succ.items():
        if end[0] not in es:
            continue
        s2 = s
        while s2[0] not in es:
            s2 = S.succ[s2]
        nxt[end] = s2
    darts = [(e, d) for e in es for d in (1, -1)]
    used, walks = set(), []
    for d0 in darts:
        if d0 in used:
            continue
        walk, d = [], d0
        while d not in used:
            used.add(d)
            walk.append(d)
            e, direction = d
            arrive = (e, 1) if direction == 1 else (e, 0)      # the end at the arrival vertex
            e2, which = nxt[arrive]                           # next end counterclockwise around the vertex
            d = (e2, 1 if which == 0 else -1)                 # leave along it
        walks.append(walk)
    return walks


def walk_class(S, walk):
    I = [0, 0, 0, 0]
    for e, d in walk:
        for k in range(4):
            I[k] += d * S.edges[e][2][k]
    return tuple(I)


def corner_edges(S, es, walk):
    """edges not in es lying in the corners traversed by a boundary walk (between consecutive darts at each vertex)"""
    es = set(es)
    out = []
    for i, (e, d) in enumerate(walk):
        arrive = (e, 1) if d == 1 else (e, 0)
        s2 = S.succ[arrive]
        while s2[0] not in es:
            out.append(s2[0])
            s2 = S.succ[s2]
    return out


def integer_kernel(G):
    n = len(G[0]) if G else 0
    M = [list(row) for row in G]
    U = [[int(i == j) for j in range(n)] for i in range(n)]
    col = 0
    for r in range(len(M)):
        while True:
            nz = [j for j in range(col, n) if M[r][j] != 0]
            if len(nz) <= 1:
                break
            p = min(nz, key=lambda j: abs(M[r][j]))
            for j in nz:
                if j != p:
                    f = M[r][j] // M[r][p]
                    for i in range(len(M)):
                        M[i][j] -= f * M[i][p]
                    for i in range(n):
                        U[i][j] -= f * U[i][p]
        nz = [j for j in range(col, n) if M[r][j] != 0]
        if nz:
            j = nz[0]
            for i in range(len(M)):
                M[i][col], M[i][j] = M[i][j], M[i][col]
            for i in range(n):
                U[i][col], U[i][j] = U[i][j], U[i][col]
            col += 1
    return [[U[i][j] for i in range(n)] for j in range(col, n)]


def radical(I_rows):
    B = [solve(I) for I in hermite(I_rows)]
    n = len(B)
    G = [[sum(B[i][a] * JM[a][b] * B[j][b] for a in range(4) for b in range(4)) for j in range(n)] for i in range(n)]
    rad = []
    for c in integer_kernel(G):
        x = [sum(c[i] * B[i][k] for i in range(n)) for k in range(4)]
        rad.append(tuple(sum(JM[j][k] * x[k] for k in range(4)) for j in range(4)))
    return hermite(rad)


# ------------------------------------------------------------------ automorphisms (Proposition 4)

def automorphisms(S):
    A, B, C, D = S.params
    W, H = A + B, C + D
    idx = {c: i for i, c in enumerate(S.cells)}
    left = {S.right[s]: s for s in range(len(S.cells))}
    down = {S.up[s]: s for s in range(len(S.cells))}
    step = {(1, 0): S.right, (0, 1): S.up, (-1, 0): left, (0, -1): down}
    mats = [((a, b), (c, d)) for a, b, c, d in product((-1, 0, 1), repeat=4)
            if abs(a) + abs(b) == 1 and abs(c) + abs(d) == 1 and abs(a * d - b * c) == 1]
    out = []
    for g1, g2 in mats:
        for t0 in range(len(S.cells)):
            sig, todo, ok = {0: t0}, [0], True
            while todo and ok:
                s = todo.pop()
                for d, img in (((1, 0), g1), ((-1, 0), (-g1[0], -g1[1])), ((0, 1), g2), ((0, -1), (-g2[0], -g2[1]))):
                    n, m = step[d][s], step[img][sig[s]]
                    if n in sig and sig[n] != m:
                        ok = False
                        break
                    if n not in sig:
                        sig[n] = m
                        todo.append(n)
            if not ok or len(set(sig.values())) != len(S.cells):
                continue

            def side(c, off):
                return {(0, -1): (2 * c, (1, 0)), (-1, 0): (2 * c + 1, (0, 1)), (0, 1): (2 * S.up[c], (1, 0)),
                        (1, 0): (2 * S.right[c] + 1, (0, 1))}[off]

            emap = {}
            for s in range(len(S.cells)):
                for src, along, off in ((2 * s, g1, (-g2[0], -g2[1])), (2 * s + 1, g2, (-g1[0], -g1[1]))):
                    e, direction = side(sig[s], off)
                    emap[src] = (e, 1 if along == direction else -1)
            out.append(emap)
    return out


def action(S, emap):
    cols = []
    for loop in S.loops:
        I = [0, 0, 0, 0]
        for e in loop:
            e2, sg = emap[e]
            for k in range(4):
                I[k] += sg * S.edges[e2][2][k]
        cols.append(solve(I))
    return [[cols[k][j] for k in range(4)] for j in range(4)]


def image_label(lab, M):
    if lab == "-":
        return "-"
    parts = []
    for part in lab.split("|"):
        rows = [tuple(int(v) for v in ch.split(",")) for ch in part[2:-1].split("][")]
        img = []
        for I in rows:
            x = solve(I)
            y = [sum(M[i][k] * x[k] for k in range(4)) for i in range(4)]
            img.append(tuple(sum(JM[j][k] * y[k] for k in range(4)) for j in range(4)))
        parts.append(part[0] + "".join("[" + ",".join(map(str, r)) + "]" for r in hermite(img)))
    return "|".join(sorted(parts))


def wall_group(lab):
    span = {(0, 0, 0, 0)}
    if lab == "-":
        return span
    for part in lab.split("|"):
        if part[0] != "o":
            continue
        rows = [tuple(int(v) for v in ch.split(",")) for ch in part[2:-1].split("][")]
        for I in radical(rows):
            g = tuple(v & 1 for v in solve(I))
            span |= {tuple(a ^ b for a, b in zip(s, g)) for s in span}
    return span


# ------------------------------------------------------------------ run

def run():
    rng = random.Random(20261023)
    checks, controls, failures = {}, {}, []

    # Theorem 1 and Corollary 1 on L(2,1,2,1), all orientations, all twists
    S = Surface(2, 1, 2, 1)
    E = len(S.edges)
    per = {}
    labels = {}
    tws = {q: twist_of(S, q) for q in TWISTS}
    for m in range(1 << E):
        x = [(m >> e) & 1 for e in range(E)]
        for q in TWISTS:
            lam = skeleton(S, x, tws[q])
            per[(q, lam)] = per.get((q, lam), 0) + 1
            if (q, lam) not in labels:
                labels[(q, lam)] = label(S, lam, tws[q], q)
    keys = sorted(per, key=lambda k: (k[0], sorted(k[1])))
    sample = [k for k in keys if 6 <= len(k[1]) <= 11]
    rng.shuffle(sample)
    sample = sample[:120]
    stats = {"pairs": 0, "count = c * A": 0, "c = c after series reduction": 0, "A = A after parallel reduction": 0,
             "c = T(0,2) of the frame matroid": 0, "A = T(2,0) of the contraction": 0}
    no_gauge_breaks = series_shrunk_differs = parallel_cluster_differs = 0
    for (q, lam) in sample:
        t = tws[q]
        lam_edges = [(S.edges[e][0], S.edges[e][1], t[e]) for e in sorted(lam)]
        c = c_count(S.edges, lam_edges)
        cs = c_count(S.edges, series_reduce(lam_edges))
        types, rest = shrunk(S, lam, t)
        A = a_count(types, rest)
        Ar = a_count(types, parallel_reduce(types, rest))
        stats["pairs"] += 1
        stats["count = c * A"] += c * A == per[(q, lam)]
        stats["c = c after series reduction"] += c == cs
        stats["A = A after parallel reduction"] += A == Ar
        allv = list(range(S.V))
        full = [(S.edges[e][0], S.edges[e][1], t[e]) for e in range(E)]
        lam_idx = sorted(lam)
        sub = [(S.edges[e][0], S.edges[e][1], t[e]) for e in lam_idx]
        lam_v = sorted({v for u, w, _t in sub for v in (u, w)})
        stats["c = T(0,2) of the frame matroid"] += tutte_eval(sub, lam_v, 0, 2) == c
        stats["A = T(2,0) of the contraction"] += tutte_eval(full, allv, 2, 0, contract=lam_idx) == A
        types0, rest0 = shrunk(S, lam, t, use_gauge=False)
        no_gauge_breaks += c * a_count(types0, rest0) != per[(q, lam)]
        # series-reducing the shrunken graph: suppress ordinary nodes of degree 2
        ser = series_reduce([(a, b, th) for a, b, th in rest if types[a] != "odd" and types[b] != "odd"]) + \
            [(a, b, th) for a, b, th in rest if types[a] == "odd" or types[b] == "odd"]
        used = {n for a, b, _ in ser for n in (a, b)}
        types_s = {n: ty for n, ty in types.items() if n in used or ty != "ord"}
        series_shrunk_differs += a_count(types_s, ser) != A
        par = sorted({(min(u, w), max(u, w), th) for u, w, th in lam_edges})
        parallel_cluster_differs += c_count(S.edges, par) != c
    checks["Theorem 1 and reductions on L(2,1,2,1), sampled (twist, skeleton) pairs"] = stats
    if any(v != stats["pairs"] for v in stats.values()):
        failures.append("factorization, reductions or matroid reading fail")
    controls["shrunken graph without the even clusters' gauge breaks the factorization"] = no_gauge_breaks
    controls["series-reducing the shrunken graph changes A"] = series_shrunk_differs
    controls["parallel-reducing a cluster changes c"] = parallel_cluster_differs

    # Proposition 4 and Corollary 3 on all of L(2,1,2,1)
    N = {}
    for (q, lam), n in per.items():
        key = (q, labels[(q, lam)])
        N[key] = N.get(key, 0) + n
    autos = [action(S, em) for em in automorphisms(S)]
    sym_ok = sym_tot = wall_ok = wall_tot = nonwall_diff = 0
    for (q, lab), n in N.items():
        for M in autos:
            q2 = tuple(sum(M[i][k] * q[k] for k in range(4)) & 1 for i in range(4))
            sym_tot += 1
            sym_ok += N.get((q2, image_label(lab, M)), 0) == n
        G = wall_group(lab)
        for chi in G:
            wall_tot += 1
            wall_ok += N.get((tuple(a ^ b for a, b in zip(q, chi)), lab), 0) == n
        for chi in TWISTS:
            if chi not in G and N.get((tuple(a ^ b for a, b in zip(q, chi)), lab), 0) not in (0, n):
                nonwall_diff += 1
    checks["L(2,1,2,1): symmetries and walls on all (twist, label) counts"] = {
        "automorphisms": len(autos), "symmetry relations": sym_tot, "hold": sym_ok, "wall relations": wall_tot, "wall relations hold": wall_ok}
    if sym_ok != sym_tot or wall_ok != wall_tot:
        failures.append("symmetries or walls fail on L(2,1,2,1)")
    controls["a twist outside the wall group changes some nonzero count"] = nonwall_diff

    # Lemma W and Corollary 3 on random clusters of larger surfaces
    lw = {"clusters": 0, "boundary classes span the radical": 0, "corner edges form a cocycle of class PD": 0}
    c3 = {"odd clusters": 0, "label kept": 0, "shrunken graph and clusters unchanged up to switching": 0, "c * A equal": 0}
    for shape, trials in (((2, 2, 2, 2), 120), ((3, 1, 2, 2), 120), ((3, 2, 2, 2), 80)):
        S = Surface(*shape)
        E = len(S.edges)
        for _ in range(trials):
            q = rng.choice(TWISTS)
            t = twist_of(S, q)
            x = [rng.randint(0, 1) for _ in range(E)]
            lam = skeleton(S, x, t)
            if not lam:
                continue
            cid, gauge, odd = clusters(S, lam, t)
            groups = {}
            for e in lam:
                groups.setdefault(cid[S.edges[e][0]], []).append(e)
            for k, es in groups.items():
                gens = lattice(S, es)
                if not hermite(gens):
                    continue
                lw["clusters"] += 1
                walks = boundary_walks(S, es)
                bclasses = [walk_class(S, wk) for wk in walks]
                lw["boundary classes span the radical"] += hermite(bclasses) == radical(gens)
                ok = True
                for wk, bc in zip(walks, bclasses):
                    ce = corner_edges(S, es, wk)
                    cnt = {}
                    for e in ce:
                        cnt[e] = cnt.get(e, 0) ^ 1
                    cocycle = {e for e, v in cnt.items() if v}
                    if any(sum(1 for e in f if e in cocycle) & 1 for f in S.faces):
                        ok = False
                    y = solve(bc)
                    for kk, loop in enumerate(S.loops):
                        inter = sum(y[j] * JM[j][kk] for j in range(4)) & 1
                        if sum(1 for e in loop if e in cocycle) & 1 != inter:
                            ok = False
                lw["corner edges form a cocycle of class PD"] += ok
                # Corollary 3 on odd clusters with small skeletons
                if odd[k] and E - len(lam) <= 12 and len(lam) <= 12:
                    for wk, bc in zip(walks, bclasses):
                        if not any(bc):
                            continue
                        y = solve(bc)
                        chi = tuple(v & 1 for v in y)
                        q2 = tuple(a ^ b for a, b in zip(q, chi))
                        t2 = twist_of(S, q2)
                        c3["odd clusters"] += 1
                        c3["label kept"] += label(S, lam, t2, q2) == label(S, lam, t, q)
                        types1, rest1 = shrunk(S, lam, t)
                        types2, rest2 = shrunk(S, lam, t2)
                        # unchanged up to switching: theta differences on non-odd edges form a coboundary on the nodes
                        par, good = {}, types1 == types2
                        def root(z):
                            s = 0
                            while z in par:
                                z, d = par[z]
                                s ^= d
                            return z, s
                        for (a, b, th1), (_a, _b, th2) in zip(rest1, rest2):
                            if types1[a] == "odd" or types1[b] == "odd":
                                continue
                            (ra, xa), (rb, xb) = root(a), root(b)
                            want = th1 ^ th2
                            if ra == rb:
                                good = good and (xa ^ xb == want)
                            else:
                                par[ra] = (rb, xa ^ xb ^ want)
                        l1 = [(S.edges[e][0], S.edges[e][1], t[e]) for e in sorted(lam)]
                        l2 = [(S.edges[e][0], S.edges[e][1], t2[e]) for e in sorted(lam)]
                        # the twists agree on the skeleton up to switching: t + t2 is a coboundary on the skeleton
                        par2, same_inside = {}, True
                        def root2(z):
                            s = 0
                            while z in par2:
                                z, d = par2[z]
                                s ^= d
                            return z, s
                        for (u, w, a1), (_u, _w, a2) in zip(l1, l2):
                            (ru, xu), (rw, xw) = root2(u), root2(w)
                            if ru == rw:
                                same_inside = same_inside and (xu ^ xw == a1 ^ a2)
                            else:
                                par2[ru] = (rw, xu ^ xw ^ a1 ^ a2)
                        c3["shrunken graph and clusters unchanged up to switching"] += good and same_inside
                        c3["c * A equal"] += c_count(S.edges, l1) * a_count(*parallel_reduce_pair(types1, rest1)) == \
                            c_count(S.edges, l2) * a_count(*parallel_reduce_pair(types2, rest2))
                        break
    checks["Lemma W on random clusters (L(2,2,2,2), L(3,1,2,2), L(3,2,2,2))"] = lw
    checks["Corollary 3 on odd clusters with small skeletons"] = c3
    if lw["clusters"] == 0 or any(v != lw["clusters"] for v in lw.values()):
        failures.append("Lemma W fails")
    if c3["odd clusters"] == 0 or any(v != c3["odd clusters"] for v in c3.values()):
        failures.append("Corollary 3 fails")

    # Remark 5: degrees of the tilings
    deg = {}
    for shape in ((2, 1, 2, 1), (2, 2, 2, 2), (3, 1, 2, 2), (2, 1, 2, 3), (2, 1, 3, 2), (2, 2, 3, 1), (2, 3, 2, 2), (2, 2, 2, 3), (3, 1, 3, 1)):
        S = Surface(*shape)
        deg[str(shape)] = sorted(set(S.degree.values()))
    checks["Remark 5: vertex degrees of the tilings (all faces are squares)"] = deg
    if any(v != [4, 12] for v in deg.values()):
        failures.append("Remark 5: unexpected degrees")
    if not all(v > 0 for v in controls.values()):
        failures.append("a control was not rejected")
    return {"checks": checks, "controls": controls, "failures": failures}


def parallel_reduce_pair(types, rest):
    return types, parallel_reduce(types, rest)


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
    print(f"{result['status']}: factorization, reductions, walls, symmetries and Lemma W checked")
    for f in outcome["failures"]:
        print("  failed:", f)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
