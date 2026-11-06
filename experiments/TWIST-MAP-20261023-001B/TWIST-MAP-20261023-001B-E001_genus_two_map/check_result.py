#!/usr/bin/env python3
"""Independent check of the genus-2 twist map; imports no producer code.

Parses raw_rows.jsonl, the frozen contract and result.json, and:
- checks the roster, the totals per twist, the swap-invariance flag and that the halved enumeration of L(2,2,2,2) equals the full one;
- builds L(2,1,2,1) by its own construction (lattice points of the L-shaped region glued along its sides) and labels all 2^16
  orientations in all 16 twists with its own classification, comparing every tally;
- recomputes, with its own code, the automorphisms of each surface (as cell permutations), their action on twists and labels, the
  wall groups, the closure classes, P1 and the list of unexplained equalities, and compares them with the producer's;
- checks that per-skeleton counts sum to the label counts and that skeleton-wise equality is as reported;
- recomputes the relation on every skeleton of every unexplained equality of the two smallest fresh surfaces and on up to 200 per
  other surface, with its own shrunken graphs, series reduction and isomorphism search;
- recomputes c and A by brute force for the producer's factorization samples and compares them with the measured skeleton counts;
- recomputes the verdict from the frozen decision rule.

    python3 -B check_result.py
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / "artifacts/TWIST-MAP-20261023-001B" / HERE.name
LABELS = ["L(2,1,2,1)", "L(2,2,2,2) full", "L(2,2,2,2)", "L(3,1,2,2)", "L(2,1,2,3)", "L(2,1,3,2)", "L(2,2,3,1)", "L(2,3,2,2)",
          "L(2,2,2,3)", "L(3,1,3,1)"]
JM = ((0, 0, 1, 1), (0, 0, 1, 0), (-1, -1, 0, 0), (-1, 0, 0, 0))
TWISTS = [tuple((i >> (3 - k)) & 1 for k in range(4)) for i in range(16)]
THRESHOLD = 1000


# ------------------------------------------------------------------ own surface construction

def surface(A, B, C, D):
    """Lattice points of the L-region glued along its sides; edges are the bottom and left sides of each cell, in cell order
    (rows of the bottom block, then rows of the top block)."""
    W, H = A + B, C + D
    inside = lambda x, y: (0 <= x <= W and 0 <= y <= C) or (0 <= x <= A and C <= y <= H)
    pts = [(x, y) for x in range(W + 1) for y in range(H + 1) if inside(x, y)]
    parent = {p: p for p in pts}

    def root(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def glue(p, q):
        a, b = root(p), root(q)
        if a != b:
            parent[a] = b

    for (x, y) in pts:
        if x == W and y <= C:
            glue((x, y), (0, y))
        if x == A and C <= y <= H:
            glue((x, y), (0, y))
        if y == H and x <= A:
            glue((x, y), (x, 0))
        if y == C and A <= x <= W:
            glue((x, y), (x, 0))
    reps = sorted({root(p) for p in pts})
    vid = {r: i for i, r in enumerate(reps)}
    cells = [(x, y) for y in range(C) for x in range(W)] + [(x, y) for y in range(C, H) for x in range(A)]
    edges = []
    for (x, y) in cells:
        edges.append((vid[root((x, y))], vid[root((x + 1, y))], (0, 0, -int(x == 0), -int(x == A))))
        edges.append((vid[root((x, y))], vid[root((x, y + 1))], (int(y == 0), int(y == H - 1), 0, 0)))
    return len(reps), edges, cells


# ------------------------------------------------------------------ own classification

def components(n, out):
    """Strong components by Kosaraju (iterative)."""
    rev = [[] for _ in range(n)]
    for a in range(n):
        for b in out[a]:
            rev[b].append(a)
    seen, order = [False] * n, []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, 0)]
        while stack:
            v, i = stack.pop()
            if i < len(out[v]):
                stack.append((v, i + 1))
                w = out[v][i]
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, 0))
            else:
                order.append(v)
    comp = [-1] * n
    c = 0
    for s in reversed(order):
        if comp[s] >= 0:
            continue
        comp[s] = c
        stack = [s]
        while stack:
            v = stack.pop()
            for w in rev[v]:
                if comp[w] < 0:
                    comp[w] = c
                    stack.append(w)
        c += 1
    return comp


def hermite(rows):
    m = [list(r) for r in rows if any(r)]
    out, r = [], 0
    for c in range(4):
        live = [row for row in m[r:] if row[c] != 0]
        if not live:
            continue
        while True:
            live = [i for i in range(r, len(m)) if m[i][c] != 0]
            if len(live) <= 1:
                break
            p = min(live, key=lambda i: abs(m[i][c]))
            for i in live:
                if i != p:
                    f = m[i][c] // m[p][c]
                    m[i] = [a - f * b for a, b in zip(m[i], m[p])]
        if not live:
            continue
        p = live[0]
        m[r], m[p] = m[p], m[r]
        if m[r][c] < 0:
            m[r] = [-a for a in m[r]]
        for i in range(r):
            f = m[i][c] // m[r][c]
            m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return [tuple(row) for row in m[:r]]


def classify(V, edges, x, alpha):
    t = [sum(a * o for a, o in zip(alpha, off)) & 1 for (_u, _w, off) in edges]
    out = [[] for _ in range(2 * V)]
    for (u, w, _o), b, te in zip(edges, x, t):
        if b:
            out[2 * u].append(2 * w + te)
            out[2 * w + 1 - te].append(2 * u + 1)
        else:
            out[2 * w + te].append(2 * u)
            out[2 * u + 1].append(2 * w + 1 - te)
    comp = components(2 * V, out)
    cyc = [e for e, (u, w, _o) in enumerate(edges) if comp[2 * u] == comp[2 * w + t[e]]]
    parent = {}

    def find(v):
        while parent.setdefault(v, v) != v:
            v = parent[v]
        return v

    for e in cyc:
        a, b = find(edges[e][0]), find(edges[e][1])
        if a != b:
            parent[b] = a
    groups = {}
    for e in cyc:
        groups.setdefault(find(edges[e][0]), []).append(e)
    parts = []
    for es in groups.values():
        pot, gens, adj = {}, [], {}
        for e in es:
            u, w, o = edges[e]
            adj.setdefault(u, []).append((w, o, 1))
            adj.setdefault(w, []).append((u, o, -1))
        start = edges[es[0]][0]
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
        h = hermite(gens)
        if not h:
            continue
        odd = any(sum(a * g for a, g in zip(alpha, gen)) & 1 for gen in gens)
        parts.append(("o" if odd else "e") + "".join("[" + ",".join(map(str, row)) + "]" for row in h))
    return "|".join(sorted(parts)) if parts else "-", sum(1 << e for e in cyc)


# ------------------------------------------------------------------ own closure

def solve(v):
    M = [list(map(Fraction, JM[i])) + [Fraction(v[i])] for i in range(4)]
    for c in range(4):
        p = next(r for r in range(c, 4) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        for r in range(4):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return tuple(int(M[i][4] / M[i][i]) for i in range(4))


def cell_symmetries(A, B, C, D):
    """Permutations of cells with a constant derivative g in the dihedral group mapping neighbours to neighbours; for each, the
    image of every edge (as edge index and sign)."""
    W, H = A + B, C + D
    cells = [(x, y) for y in range(C) for x in range(W)] + [(x, y) for y in range(C, H) for x in range(A)]
    idx = {c: i for i, c in enumerate(cells)}

    def step(c, d):
        x, y = c
        if d == (1, 0):
            return idx[((x + 1) % (W if y < C else A), y)]
        if d == (-1, 0):
            return idx[((x - 1) % (W if y < C else A), y)]
        if d == (0, 1):
            return idx[(x, (y + 1) % (H if x < A else C))]
        return idx[(x, (y - 1) % (H if x < A else C))]

    mats = [((a, b), (c, d)) for a, b, c, d in product((-1, 0, 1), repeat=4) if abs(a * d - b * c) == 1 and abs(a) + abs(b) == 1 and abs(c) + abs(d) == 1]
    out = []
    for (g1, g2) in mats:                  # images of e1 and e2
        for t0 in range(len(cells)):
            sig = {0: t0}
            todo = [0]
            ok = True
            while todo and ok:
                s = todo.pop()
                for d, img in (((1, 0), g1), ((-1, 0), (-g1[0], -g1[1])), ((0, 1), g2), ((0, -1), (-g2[0], -g2[1]))):
                    n, m = step(cells[s], d), step(cells[sig[s]], img)
                    if n in sig and sig[n] != m:
                        ok = False
                        break
                    if n not in sig:
                        sig[n] = m
                        todo.append(n)
            if not ok or len(set(sig.values())) != len(cells):
                continue
            # the bottom edge of s is the side at -e2 running along e1; its image is the side of sig(s) at -g2 running along g1
            def side(c, offset):
                if offset == (0, -1):
                    return 2 * c, (1, 0)
                if offset == (-1, 0):
                    return 2 * c + 1, (0, 1)
                if offset == (0, 1):
                    return 2 * step(cells[c], (0, 1)), (1, 0)
                return 2 * step(cells[c], (1, 0)) + 1, (0, 1)
            emap = {}
            for s in range(len(cells)):
                for src, along, off in ((2 * s, g1, (-g2[0], -g2[1])), (2 * s + 1, g2, (-g1[0], -g1[1]))):
                    e, direction = side(sig[s], off)
                    emap[src] = (e, 1 if along == direction else -1)
            out.append(emap)
    return out


def action(A, B, C, D, edges, emap):
    W, H = A + B, C + D
    cells = [(x, y) for y in range(C) for x in range(W)] + [(x, y) for y in range(C, H) for x in range(A)]
    idx = {c: i for i, c in enumerate(cells)}
    loops = [[2 * idx[(x, 0)] for x in range(W)], [2 * idx[(x, H - 1)] for x in range(A)],
             [2 * idx[(0, y)] + 1 for y in range(H)], [2 * idx[(A, y)] + 1 for y in range(C)]]
    cols = []
    for loop in loops:
        I = [0, 0, 0, 0]
        for e in loop:
            e2, sg = emap[e]
            for k in range(4):
                I[k] += sg * edges[e2][2][k]
        cols.append(solve(I))
    return [[cols[k][j] for k in range(4)] for j in range(4)]


def integer_kernel(G):
    """Basis of {c in Z^n : G c = 0} by unimodular column operations (Euclid on each row), tracking the transformation."""
    n = len(G[0]) if G else 0
    M = [list(row) for row in G]
    U = [[int(i == j) for j in range(n)] for i in range(n)]       # columns of U track the column operations
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


def kernel_mod_lattice(B):
    """Mod-2 span of the images sum c_i B_i of the integer kernel of the Gram matrix B J B^T (the radical of the lattice)."""
    n = len(B)
    G = [[sum(B[i][a] * JM[a][b] * B[j][b] for a in range(4) for b in range(4)) for j in range(n)] for i in range(n)]
    span = {(0, 0, 0, 0)}
    for c in integer_kernel(G):
        g = tuple(sum(c[i] * B[i][k] for i in range(n)) & 1 for k in range(4))
        span |= {tuple(a ^ b for a, b in zip(s, g)) for s in span}
    return span


def parse(label):
    if label == "-":
        return []
    res = []
    for part in label.split("|"):
        rows = [tuple(int(v) for v in ch.split(",")) for ch in part[2:-1].split("][")] if len(part) > 1 else []
        res.append((part[0] == "o", rows))
    return res


def walls(label):
    span = {(0, 0, 0, 0)}
    for odd, rows in parse(label):
        if odd:
            g = kernel_mod_lattice([solve(I) for I in rows])
            span = {tuple(a ^ b for a, b in zip(s, h)) for s in span for h in g}
    return span


def image_label(label, M):
    parts = []
    for odd, rows in parse(label):
        img = []
        for I in rows:
            x = solve(I)
            y = [sum(M[i][k] * x[k] for k in range(4)) for i in range(4)]
            img.append(tuple(sum(JM[j][k] * y[k] for k in range(4)) for j in range(4)))
        parts.append(("o" if odd else "e") + "".join("[" + ",".join(map(str, r)) + "]" for r in hermite(img)))
    return "|".join(sorted(parts)) if parts else "-"


def own_closure(params, edges, counts):
    A, B, C, D = params
    mats = [action(A, B, C, D, edges, em) for em in cell_symmetries(A, B, C, D)]
    parent = {}

    def find(k):
        while parent.setdefault(k, k) != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def join(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    keys = list(counts)
    for (q, L) in keys:
        find((q, L))
    for L in {L for _q, L in keys}:
        for q in TWISTS:
            for chi in walls(L):
                q2 = tuple(a ^ b for a, b in zip(q, chi))
                if (q, L) in counts or (q2, L) in counts:
                    join((q, L), (q2, L))
    for M in mats:
        for (q, L) in keys:
            join((q, L), (tuple(sum(M[i][k] * q[k] for k in range(4)) & 1 for i in range(4)), image_label(L, M)))
    return find, parent, len(mats)


# ------------------------------------------------------------------ own relation on a skeleton

def own_relation(edges, V, mask, q1, q2):
    def build(alpha):
        t = [sum(a * o for a, o in zip(alpha, off)) & 1 for (_u, _w, off) in edges]
        sk = [e for e in range(len(edges)) if mask >> e & 1]
        lab, sheet, odd = {}, {}, {}
        adj = {}
        for e in sk:
            u, w, _o = edges[e]
            adj.setdefault(u, []).append((w, t[e]))
            adj.setdefault(w, []).append((u, t[e]))
        for v in sorted(adj):
            if v in lab:
                continue
            lab[v], sheet[v] = v, 0
            odd[v] = False
            todo = [v]
            while todo:
                a = todo.pop()
                for b, f in adj[a]:
                    if b not in lab:
                        lab[b], sheet[b] = v, sheet[a] ^ f
                        todo.append(b)
                    elif sheet[b] != sheet[a] ^ f:
                        odd[v] = True
        pt = lambda v: ("K", lab[v]) if v in lab else ("v", v)
        kind = {}
        for v in range(V):
            kind[pt(v)] = "ord" if v not in lab else ("odd" if odd[lab[v]] else "even")
        nb, loops, tw = {n: set() for n in kind}, {n: set() for n in kind}, {}
        for e in range(len(edges)):
            if mask >> e & 1:
                continue
            u, w, _o = edges[e]
            a, b = pt(u), pt(w)
            th = t[e] ^ sheet.get(u, 0) ^ sheet.get(w, 0)
            if a == b:
                loops[a].add(th)
                continue
            nb[a].add(b)
            nb[b].add(a)
            if kind[a] != "odd" and kind[b] != "odd":
                tw.setdefault(frozenset((a, b)), set()).add(th)
        # clusters, series-reduced
        clus = {}
        for e in sk:
            u, w, _o = edges[e]
            clus.setdefault(lab[u], []).append([u, w, t[e]])
        red = {}
        for k, es in clus.items():
            while True:
                deg = {}
                for u, w, _th in es:
                    deg[u] = deg.get(u, 0) + 1
                    deg[w] = deg.get(w, 0) + 1
                cand = [v for v in sorted(deg) if deg[v] == 2 and not any(a == b == v for a, b, _ in es)]
                if not cand or len(es) <= 1:
                    break
                v = cand[0]
                i, j = [n for n, (a, b, _th) in enumerate(es) if v in (a, b)]
                a = es[i][0] if es[i][1] == v else es[i][1]
                b = es[j][0] if es[j][1] == v else es[j][1]
                es = [x for n, x in enumerate(es) if n not in (i, j)] + [[a, b, es[i][2] ^ es[j][2]]]
            red[("K", k)] = ("odd" if odd[k] else "even", es)
        return kind, nb, {n: tuple(sorted(s)) for n, s in loops.items()}, tw, red

    def isos(n1, n2, k1, k2, l1, l2, cap=100000):
        nodes1 = sorted(n1, key=lambda n: (-len(n1[n]), str(n)))
        sig = lambda nb, kd, lp, n: (kd[n], lp[n], len(nb[n]), tuple(sorted((kd[m], lp[m], len(nb[m])) for m in nb[n])))
        s1 = {n: sig(n1, k1, l1, n) for n in n1}
        s2 = {n: sig(n2, k2, l2, n) for n in n2}
        if sorted(s1.values()) != sorted(s2.values()):
            return
        phi, used, count = {}, set(), [0]

        def go(i):
            if count[0] >= cap:
                return
            if i == len(nodes1):
                count[0] += 1
                yield dict(phi)
                return
            n = nodes1[i]
            for m in n2:
                if m in used or s2[m] != s1[n]:
                    continue
                if all((p in n1[n]) == (phi[p] in n2[m]) for p in phi):
                    phi[n] = m
                    used.add(m)
                    yield from go(i + 1)
                    used.discard(m)
                    del phi[n]

        yield from go(0)

    def switching_ok(b1, b2, phi):
        if len(b1) != len(b2):
            return False
        par = {}

        def root(x):
            s = 0
            while x in par:
                x, d = par[x]
                s ^= d
            return x, s

        for key, s1 in b1.items():
            a, b = tuple(key)
            s2 = b2.get(frozenset((phi[a], phi[b])))
            if s2 is None:
                return False
            ok = set()
            if sorted(s1) == sorted(s2):
                ok.add(0)
            if sorted(s1) == sorted(1 - x for x in s2):
                ok.add(1)
            if not ok:
                return False
            if len(ok) == 2:
                continue
            want = ok.pop()
            (ra, xa), (rb, xb) = root(a), root(b)
            if ra == rb:
                if xa ^ xb != want:
                    return False
            else:
                par[ra] = (rb, xa ^ xb ^ want)
        return True

    def cluster_graph(es):
        nb, lp, bund, deg = {}, {}, {}, {}
        for u, w, th in es:
            for v in (u, w):
                nb.setdefault(v, set())
                lp.setdefault(v, [])
                deg[v] = deg.get(v, 0) + 1
            if u == w:
                deg[u] += 0
                lp[u].append(th)
                continue
            nb[u].add(w)
            nb[w].add(u)
            bund.setdefault(frozenset((u, w)), []).append(th)
        kd = {v: deg[v] for v in nb}
        return nb, kd, {v: tuple(sorted(x)) for v, x in lp.items()}, {k: tuple(sorted(v)) for k, v in bund.items()}

    def cluster_iso(es1, es2):
        g1, g2 = cluster_graph(es1), cluster_graph(es2)
        if len(g1[0]) != len(g2[0]):
            return False
        for phi in isos(g1[0], g2[0], g1[1], g2[1], g1[2], g2[2]):
            if switching_ok(g1[3], g2[3], phi):
                return True
        return False

    k1, n1, l1, t1, r1 = build(q1)
    k2, n2, l2, t2, r2 = build(q2)
    if k1 == k2 and l1 == l2 and switching_ok(t1, t2, {n: n for n in n1}):
        outside = "identity"
    else:
        outside = "none"
        for phi in isos(n1, n2, k1, k2, l1, l2):
            if switching_ok(t1, t2, phi):
                outside = "isomorphism"
                break
    same = set(r1) == set(r2) and all(r1[k][0] == r2[k][0] and cluster_graph(r1[k][1])[2] == cluster_graph(r2[k][1])[2]
                                      and switching_ok(cluster_graph(r1[k][1])[3], cluster_graph(r2[k][1])[3],
                                                       {v: v for v in cluster_graph(r1[k][1])[0]}) for k in r1)
    if same:
        inside = "identity"
    else:
        a, b = list(r1.values()), list(r2.values())
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

        inside = "isomorphic" if len(a) == len(b) and match(0) else "unmatched"
    return outside, inside


def brute_cA(edges, V, mask, alpha):
    t = [sum(a * o for a, o in zip(alpha, off)) & 1 for (_u, _w, off) in edges]
    sk = [e for e in range(len(edges)) if mask >> e & 1]
    rest = [e for e in range(len(edges)) if not mask >> e & 1]
    c = 0
    for bits in range(1 << len(sk)):
        x = [0] * len(edges)
        for i, e in enumerate(sk):
            x[e] = bits >> i & 1
        out = [[] for _ in range(2 * V)]
        for i, e in enumerate(sk):
            u, w, _o = edges[e]
            if x[e]:
                out[2 * u].append(2 * w + t[e])
                out[2 * w + 1 - t[e]].append(2 * u + 1)
            else:
                out[2 * w + t[e]].append(2 * u)
                out[2 * u + 1].append(2 * w + 1 - t[e])
        comp = components(2 * V, out)
        if all(comp[2 * edges[e][0]] == comp[2 * edges[e][1] + t[e]] for e in sk):
            c += 1
    return c, len(rest)


# ------------------------------------------------------------------ main

def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(l) for l in (ART / "raw_rows.jsonl").read_text().splitlines() if l.strip()]
    problems = []
    if [r["label"] for r in rows] != LABELS:
        problems.append("roster differs")
    for r in rows:
        tot = {}
        for q, L, c in r["counts"]:
            tot["".join(map(str, q))] = tot.get("".join(map(str, q)), 0) + c
        if len(tot) != 16 or any(v != 1 << r["edges"] for v in tot.values()):
            problems.append(f"totals {r['label']}")
        if any(r["mis"].values()):
            problems.append(f"swap-invariance {r['label']}")
    full = next(r for r in rows if r["label"] == "L(2,2,2,2) full")
    half = next(r for r in rows if r["label"] == "L(2,2,2,2)")
    if full["counts"] != half["counts"]:
        problems.append("halving")
    # own enumeration of L(2,1,2,1)
    V, edges, _cells = surface(2, 1, 2, 1)
    tally = {}
    for m in range(1 << len(edges)):
        x = [(m >> e) & 1 for e in range(len(edges))]
        for q in TWISTS:
            lab, _mask = classify(V, edges, x, q)
            tally[(q, lab)] = tally.get((q, lab), 0) + 1
    row = next(r for r in rows if r["label"] == "L(2,1,2,1)")
    theirs = {(tuple(q), L): c for q, L, c in row["counts"]}
    if tally != theirs:
        problems.append("L(2,1,2,1) own enumeration differs")
    own_rel_checked = own_rel_disagree = 0
    unexpl_all = []
    factor_checked = factor_bad = 0
    for r in rows:
        a = r.get("analysis")
        if not a:
            continue
        params = tuple(r["params"])
        V, edges, _cells = surface(*params)
        counts = {(tuple(q), L): c for q, L, c in r["counts"]}
        find, parent, nauto = own_closure(params, edges, counts)
        if nauto != a["automorphisms"]:
            problems.append(f"automorphism count {r['label']}: {nauto} vs {a['automorphisms']}")
        classes = {}
        for k in list(parent):
            classes.setdefault(find(k), set()).add(counts.get(k, 0))
        p1 = sum(1 for v in classes.values() if len(v) > 1)
        if p1 != a["P1_failure_count"]:
            problems.append(f"P1 disagreement {r['label']}: own {p1}, producer {a['P1_failure_count']}")
        own_un = []
        for L in sorted({L for _q, L in counts}):
            nz = [(q, counts[(q, L)]) for q in TWISTS if counts.get((q, L), 0) >= THRESHOLD]
            for i in range(len(nz)):
                for j in range(i + 1, len(nz)):
                    (q1, n1), (q2, n2) = nz[i], nz[j]
                    if n1 == n2 and find((q1, L)) != find((q2, L)):
                        own_un.append((L, "".join(map(str, q1)), "".join(map(str, q2))))
        prod_un = [(p["label"], p["twists"][0], p["twists"][1]) for p in a["pairs"] if p["kind"] == "unexplained"]
        if sorted(own_un) != sorted(prod_un):
            problems.append(f"unexplained list differs on {r['label']}: own {len(own_un)}, producer {len(prod_un)}")
        budget = 10 ** 9 if r["label"] in ("L(2,1,2,3)", "L(2,1,3,2)") else 200
        for p in a["pairs"]:
            if p["kind"] == "unexplained":
                unexpl_all.append((r["family"], r["label"], p))
            per = p.get("per_skeleton")
            if per is None:
                continue
            if len(per) == p["skeletons"]:
                if sum(x for _m, x, _y, _r in per) != p["counts"][0] or sum(y for _m, _x, y, _r in per) != p["counts"][1]:
                    problems.append(f"skeleton sums {r['label']} {p['label']} {p['twists']}")
                if p["skeleton_wise_equal"] != all(x == y for _m, x, y, _r in per):
                    problems.append(f"skeleton-wise flag {r['label']} {p['label']} {p['twists']}")
            if p["kind"] != "unexplained":
                continue
            q1, q2 = (tuple(int(c) for c in s) for s in p["twists"])
            for m, x, y, rel in per:
                if budget <= 0:
                    break
                budget -= 1
                mine = own_relation(edges, V, m, q1, q2)
                own_rel_checked += 1
                if list(mine) != list(rel):
                    own_rel_disagree += 1
        for f in a["factorization"]:
            q1, q2 = (tuple(int(c) for c in s) for s in f["twists"])
            for q, meas, cprod in ((q1, f["measured"][0], f["c"][0]), (q2, f["measured"][1], f["c"][1])):
                c, _rest = brute_cA(edges, V, f["mask"], q)
                factor_checked += 1
                if c != cprod or meas % c or meas // c != f["A"][[q1, q2].index(q)]:
                    factor_bad += 1
    if own_rel_disagree:
        problems.append(f"relations disagree on {own_rel_disagree} of {own_rel_checked} skeletons")
    if factor_bad:
        problems.append(f"factorization disagrees on {factor_bad} of {factor_checked}")
    # verdict
    fresh = [(lab, p) for fam, lab, p in unexpl_all if fam == "F_fresh"]
    p1_ok = all(r["analysis"]["P1_failure_count"] == 0 for r in rows if r.get("analysis"))
    p2 = any(p["skeleton_wise_equal"] and p["skeletons"] >= 2 for _l, p in fresh)
    p3 = all(p["skeleton_wise_equal"] and p["all_explained"] for _l, p in fresh)
    verdict = "invalid" if not result["controls_ok"] else ("refuted" if not p1_ok else ("supported" if p2 and p3 else "partially supported"))
    if verdict != result["verdict"]:
        problems.append(f"verdict {verdict} vs producer {result['verdict']}")
    print(json.dumps({"problems": problems, "own_relations_checked": own_rel_checked, "own_relation_disagreements": own_rel_disagree,
                      "factorization_checked": factor_checked, "verdict": verdict, "unexplained_fresh": len(fresh),
                      "contract_status": contract["status"]}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
