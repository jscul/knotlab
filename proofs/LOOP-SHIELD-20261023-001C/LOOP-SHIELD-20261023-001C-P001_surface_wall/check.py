#!/usr/bin/env python3
"""Check of LOOP-SHIELD-20261023-001C-P001: the wall on closed surfaces and the seam lemmas.

Standard library only. Genus-2 surfaces are L-shaped square-tiled tables L(A, B, C, D) (a bottom block (A + B) x C, a top block A x D
over columns 0..A-1, sides glued by translation). Edges carry their crossings with the core curves h1, h2, v1, v2, a basis of
H1 with unimodular intersection matrix J; the twist alpha in {0,1}^4 acts on an edge by alpha.o_e mod 2 and is the twist dual to
a = sum alpha_k b_k. For a class c = sum x_k b_k the dual twist PD(c) changes alpha by x mod 2.

- Theorem 1 (surface wall): random walks (with restarts) inside line events of core classes on two surfaces. For every visited
  orientation the wall is built in the cover dual to c (levels count crossings with the core curve of c); the check verifies the wall
  lemma (the moved digraph has the same arcs on directed cycles), that the image lies in the line event of alpha + x, that applying
  the construction from that twist returns the orientation, and that the wall's class PD(c) is among the seam classes. It also
  records whether every seam next to the loop carries only 0 or PD(c).
- Lemma E (seams on a surface): for random vertex sets P, every mod-2 cocycle supported on edges with exactly one end in P has a
  class dual to a class carried by the open star of P, modelled as G[P] plus a diagonal across every square with exactly two
  opposite corners in P.
- Lemma F (seams in three dimensions): on a 5 x 5 x 5 torus, loops along x confined to a 2 x 2 tube support only the zero seam class.
- Controls (each must be rejected at least once): flipping the bits on the wrong wall edges (those whose free end is the tail)
  changes the cyclic arcs; two disjoint loops of classes h2 and v2 support two independent seam classes; a full slice of the
  3 x 3 x 3 torus supports a nonzero seam class; ignoring the diagonal squares misses seam classes.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
J = ((0, 0, 1, 1), (0, 0, 1, 0), (-1, -1, 0, 0), (-1, 0, 0, 0))
WALKS = [  # (surface, twist, class in core coordinates x, restarts, steps per walk)
    ((2, 2, 2, 2), (0, 0, 1, 0), (0, -1, 0, 0), 6, 1500),
    ((2, 2, 2, 2), (1, 0, 0, 0), (0, 0, 0, 1), 6, 1500),
    ((3, 1, 2, 2), (0, 1, 0, 1), (0, 0, 1, 0), 3, 1500),
]


# ------------------------------------------------------------------ surfaces

class Surface:
    def __init__(self, A, B, C, D):
        cells = [(x, y) for y in range(C) for x in range(A + B)] + [(x, y) for y in range(C, C + D) for x in range(A)]
        pos = {c: i for i, c in enumerate(cells)}
        N = len(cells)
        self.right = [pos[((x + 1) % (A + B if y < C else A), y)] for (x, y) in cells]
        self.up = [pos[(x, (y + 1) % (C + D if x < A else C))] for (x, y) in cells]
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
        names = {}
        for i in range(4 * N):
            names.setdefault(find(i), len(names))
        corner = lambda s, k: names[find(4 * s + k)]
        self.V, self.N = len(names), N
        self.edges = []
        for s, (x, y) in enumerate(cells):
            self.edges.append((corner(s, 0), corner(s, 1), (0, 0, -int(x == 0), -int(x == A))))
            self.edges.append((corner(s, 0), corner(s, 2), (int(y == 0), int(y == C + D - 1), 0, 0)))
        assert self.V - len(self.edges) + N == -2
        self.faces = [(2 * s, 2 * self.right[s] + 1, 2 * self.up[s], 2 * s + 1) for s in range(N)]
        self.loops = [[2 * pos[(x, 0)] for x in range(A + B)], [2 * pos[(x, C + D - 1)] for x in range(A)],
                      [2 * pos[(0, y)] + 1 for y in range(C + D)], [2 * pos[(A, y)] + 1 for y in range(C)]]


def twist(S, alpha):
    return [sum(a * o for a, o in zip(alpha, off)) & 1 for (_u, _w, off) in S.edges]


def arcs(S, x, t):
    out = [[] for _ in range(2 * S.V)]
    for (u, w, _o), bit, te in zip(S.edges, x, t):
        if bit:
            out[2 * u].append(2 * w + te)
            out[2 * w + (1 ^ te)].append(2 * u + 1)
        else:
            out[2 * w + te].append(2 * u)
            out[2 * u + 1].append(2 * w + (1 ^ te))
    return out


def components(out):
    n = len(out)
    rev = [[] for _ in range(n)]
    for i in range(n):
        for j in out[i]:
            rev[j].append(i)
    seen, order = [False] * n, []
    for r in range(n):
        if seen[r]:
            continue
        seen[r] = True
        stack = [(r, 0)]
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
    for r in reversed(order):
        if comp[r] >= 0:
            continue
        comp[r], stack, members = r, [r], [r]
        while stack:
            v = stack.pop()
            for w in rev[v]:
                if comp[w] < 0:
                    comp[w] = r
                    stack.append(w)
                    members.append(w)
        low = min(members)
        for v in members:
            comp[v] = low
    return comp


def cyclic_arcs(out, comp):
    return {(i, j) for i in range(len(out)) for j in out[i] if comp[i] == comp[j]}


def solve_J(v):
    M = [list(map(Fraction, J[i])) + [Fraction(v[i])] for i in range(4)]
    for c in range(4):
        p = next(r for r in range(c, 4) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        for r in range(4):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return tuple(int(M[i][4] / M[i][i]) for i in range(4))


def line_class(S, t, comp):
    """None unless the cyclic periods all lie on one line; then that line's class in core coordinates."""
    parent, pos = list(range(S.V)), [(0, 0, 0, 0)] * S.V

    def find(v):
        acc = (0, 0, 0, 0)
        while parent[v] != v:
            acc = tuple(a + b for a, b in zip(acc, pos[v]))
            v = parent[v]
        return v, acc

    gens = []
    for (u, w, off), te in zip(S.edges, t):
        if comp[2 * u] != comp[2 * w + te]:
            continue
        (ru, pu), (rw, pw) = find(u), find(w)
        d = tuple(a + b - c for a, b, c in zip(pu, off, pw))
        if ru == rw:
            if any(d):
                gens.append(d)
        else:
            parent[rw], pos[rw] = ru, d
    if not gens:
        return None
    g0 = gens[0]
    if any(g0[i] * g[j] - g0[j] * g[i] for g in gens for i in range(4) for j in range(i + 1, 4)):
        return None
    k = 0
    for v in g0:
        k = gcd(k, abs(v))
    d = tuple(v // k for v in g0)
    if next(v for v in d if v) < 0:
        d = tuple(-v for v in d)
    return solve_J(d)


def same_line(x, c):
    return x is not None and (x == c or x == tuple(-v for v in c))


# ------------------------------------------------------------------ the surface wall

def wall(S, x, alpha, c):
    """For x in the line event of class c (a core class) in twist alpha: (gamma, flips, r, P, comp)."""
    t = twist(S, alpha)
    comp = components(arcs(S, x, t))
    inv = {comp[2 * v] for v in range(S.V) if comp[2 * v] == comp[2 * v + 1]}
    assert inv, "no swap-invariant strong component"
    star = min(inv, key=lambda r: min(v for v in range(S.V) if comp[2 * v] == r))
    P = {v for v in range(S.V) if comp[2 * v] == star}
    beta = [sum(a * o for a, o in zip(c, off)) for (_u, _w, off) in S.edges]   # crossings with the core curve of c
    adj = [[] for _ in range(S.V)]
    for e, (u, w, _o) in enumerate(S.edges):
        adj[u].append((w, beta[e]))
        adj[w].append((u, -beta[e]))
    flat, stack = {0}, [0]                       # each level of the cover is a copy of the edges not crossing the curve: connected
    while stack:
        u = stack.pop()
        for w, b in adj[u]:
            if b == 0 and w not in flat:
                flat.add(w)
                stack.append(w)
    assert len(flat) == S.V, "a level of the cover is disconnected"
    v0 = min(P)
    level, stack = {v0: 0}, [v0]
    while stack:
        u = stack.pop()
        for w, b in adj[u]:
            if w in P:
                if w not in level:
                    level[w] = level[u] + b
                    stack.append(w)
                else:
                    assert level[w] == level[u] + b, "the projection carries another class"
    K = {(v, level[v]) for v in P}
    lo, hi = min(level.values()), max(level.values())
    seeds = [(v, hi + 1) for v in range(S.V)]
    up, stack = set(seeds), list(seeds)
    while stack:
        u, j = stack.pop()
        for w, b in adj[u]:
            z = (w, j + b)
            if lo <= z[1] <= hi + 1 and z not in K and z not in up:
                up.add(z)
                stack.append(z)
    gamma, flips = set(), set()
    for e, (u, w, _o) in enumerate(S.edges):
        if u in P and w not in P and (w, level[u] + beta[e]) in up:
            gamma.add(e)
            flips.add(e)
        elif w in P and u not in P and (u, level[w] - beta[e]) in up:
            gamma.add(e)
    assert gamma, "empty wall"
    nb = [[] for _ in range(S.V)]
    for e, (u, w, _o) in enumerate(S.edges):
        f = (e in gamma) ^ (beta[e] & 1)
        nb[u].append((w, f))
        nb[w].append((u, f))
    r, stack = [None] * S.V, [0]
    r[0] = 0
    while stack:
        u = stack.pop()
        for w, f in nb[u]:
            if r[w] is None:
                r[w] = r[u] ^ f
                stack.append(w)
            else:
                assert r[w] == r[u] ^ f, "the wall is not in the class PD(c)"
    return gamma, flips, r, P, comp


def phi(S, x, alpha, c):
    gamma, flips, r, P, comp = wall(S, x, alpha, c)
    return [bit ^ (e in flips) ^ r[S.edges[e][0]] for e, bit in enumerate(x)], gamma, flips, P, comp


# ------------------------------------------------------------------ seam lemmas

def nullspace_gf2(rows, n):
    """Basis of {z in GF(2)^n : r.z = 0 for every row}, rows given as bit masks."""
    pivots = {}
    for row in rows:
        for p, pr in pivots.items():
            if (row >> p) & 1:
                row ^= pr
        if row:
            p = row.bit_length() - 1
            for q in list(pivots):
                if (pivots[q] >> p) & 1:
                    pivots[q] ^= row
            pivots[p] = row
    free = [i for i in range(n) if i not in pivots]
    basis = []
    for f in free:
        z = 1 << f
        for p, pr in pivots.items():
            if (pr >> f) & 1:
                z |= 1 << p
        basis.append(z)
    return basis


def seam_classes(edges, faces, loops, P):
    """Classes (values on the loops, mod 2) of a basis of the cocycles supported on edges with exactly one end in P."""
    boundary = [e for e, (u, w, *_r) in enumerate(edges) if (u in P) != (w in P)]
    index = {e: i for i, e in enumerate(boundary)}
    rows = []
    for f in faces:
        m = 0
        for e in f:
            if e in index:
                m ^= 1 << index[e]
        if m:
            rows.append(m)
    out = set()
    for z in nullspace_gf2(rows, len(boundary)):
        vec = tuple(sum((z >> index[e]) & 1 for e in loop if e in index) & 1 for loop in loops)
        out.add(vec)
    return out


def span_gf2(vectors):
    span = {tuple(0 for _ in range(len(next(iter(vectors))) if vectors else 0))} if vectors else set()
    for v in vectors:
        span |= {tuple(a ^ b for a, b in zip(s, v)) for s in span}
    return span


def open_star_edges(S, P):
    """Edges of a graph homotopy equivalent to the open star of P: G[P] plus a diagonal across every square with exactly two opposite
    corners in P (with its homology coordinates)."""
    out = [(u, w, off) for (u, w, off) in S.edges if u in P and w in P]
    for (b, r, t, l) in S.faces:
        (u0, u1, o_b), (v0, v1, o_r), (w0, w1, o_t), (z0, z1, o_l) = S.edges[b], S.edges[r], S.edges[t], S.edges[l]
        bl, br, tl, tr = u0, u1, z1, v1                 # corners: bottom-left, bottom-right, top-left, top-right
        for (a, c, off) in ((bl, tr, tuple(x + y for x, y in zip(o_b, o_r))), (br, tl, tuple(y - x for x, y in zip(o_b, o_l)))):
            others = {bl, br, tl, tr} - {a, c}
            if a in P and c in P and not (others & P):
                out.append((a, c, off))
    return out


def surface_cycle_classes(S, P, edges=None):
    """Mod-2 classes (core coordinates) carried by cycles of G[P] (or of the given edges on P)."""
    parent, pos = {v: v for v in P}, {v: (0, 0, 0, 0) for v in P}

    def find(v):
        acc = (0, 0, 0, 0)
        while parent[v] != v:
            acc = tuple(a + b for a, b in zip(acc, pos[v]))
            v = parent[v]
        return v, acc

    out = set()
    for (u, w, off) in (S.edges if edges is None else edges):
        if u in P and w in P:
            (ru, pu), (rw, pw) = find(u), find(w)
            d = tuple(a + b - c for a, b, c in zip(pu, off, pw))
            if ru == rw:
                if any(d):
                    out.add(tuple(v & 1 for v in solve_J(d)))
            else:
                parent[rw], pos[rw] = ru, d
    return out


def pd_surface(y):
    """Values on the core loops of the twist dual to the mod-2 class y (core coordinates): y . b_j."""
    return tuple(sum(y[k] * J[k][j] for k in range(4)) & 1 for j in range(4))


class Cubic:
    def __init__(self, L):
        n = L[0] * L[1] * L[2]
        coords = [(i % L[0], (i // L[0]) % L[1], i // (L[0] * L[1])) for i in range(n)]
        index = {c: i for i, c in enumerate(coords)}
        self.n, self.L = n, L
        self.edges, eid = [], {}
        for c in coords:
            for k in range(3):
                d = list(c)
                d[k] = (d[k] + 1) % L[k]
                eid[(c, k)] = len(self.edges)
                self.edges.append((index[c], index[tuple(d)], k))
        self.faces, self.face_axes = [], []
        for c in coords:
            for k in range(3):
                for m in range(k + 1, 3):
                    ck = list(c); ck[k] = (ck[k] + 1) % L[k]
                    cm = list(c); cm[m] = (cm[m] + 1) % L[m]
                    self.faces.append((eid[(c, k)], eid[(tuple(cm), k)], eid[(c, m)], eid[(tuple(ck), m)]))
                    self.face_axes.append((c, 3 - k - m))   # the axis normal to the plaquette
        self.loops = [[eid[((i, 0, 0), 0)] for i in range(L[0])], [eid[((0, i, 0), 1)] for i in range(L[1])],
                      [eid[((0, 0, i), 2)] for i in range(L[2])]]
        self.coords = coords


def cubic_two_cycle_classes(Q, P):
    """Classes (counts mod 2 of plaquettes crossed by the three axis lines through the origin) of 2-cycles of plaquettes in P."""
    inside = [f for f, quad in enumerate(Q.faces) if all(Q.edges[e][0] in P and Q.edges[e][1] in P for e in quad)]
    if not inside:
        return set()
    edge_index = {}
    cols = []
    for f in inside:
        m = 0
        for e in Q.faces[f]:
            edge_index.setdefault(e, len(edge_index))
            m ^= 1 << edge_index[e]
        cols.append(m)
    # 2-cycles: subsets of plaquettes with zero boundary = nullspace of the boundary map (columns are plaquettes)
    nrows = len(edge_index)
    rows = []
    for r in range(nrows):
        m = 0
        for i, col in enumerate(cols):
            if (col >> r) & 1:
                m |= 1 << i
        rows.append(m)
    out = set()
    for z in nullspace_gf2(rows, len(inside)):
        vec = [0, 0, 0]
        for i, f in enumerate(inside):
            if (z >> i) & 1:
                (cx, cy, cz), axis = Q.face_axes[f]
                # the axis-k line through the origin crosses the plaquettes normal to k at coordinates 0 in the other two axes
                if [cx, cy, cz][(axis + 1) % 3] == 0 and [cx, cy, cz][(axis + 2) % 3] == 0:
                    vec[axis] ^= 1
        out.add(tuple(vec))
    return out


# ------------------------------------------------------------------ run

def run() -> dict[str, object]:
    checks, failures = {}, []
    controls = {"bits flipped on the wrong wall edges change the cyclic arcs": 0,
                "two disjoint loops of classes h2 and v2 support two independent seam classes": 0,
                "full slice supports a nonzero seam class": 0, "diagonal squares matter": 0}
    rng = random.Random("loop-shield-surface-wall")
    for (shape, alpha, c, restarts, steps) in WALKS:
        S = Surface(*shape)
        t = twist(S, alpha)
        partner = tuple((a + x) & 1 for a, x in zip(alpha, c))
        tq = twist(S, partner)
        m = len(S.edges)

        def inside(x):
            return same_line(line_class(S, t, components(arcs(S, x, t))), c)

        stats = {"examined": 0, "lemma holds": 0, "image in the partner line event": 0, "involution returns": 0,
                 "seams carry only 0 and PD(c)": 0, "PD(c) realized": 0}
        pdc = pd_surface(tuple(v & 1 for v in c))
        seen = set()
        for _walk in range(restarts * steps):
            if _walk % steps == 0:
                tries = 0
                while True:
                    tries += 1
                    x = [rng.getrandbits(1) for _ in range(m)]
                    if inside(x):
                        break
                    assert tries < 2_000_000, "no start"
            e = rng.randrange(m)
            x[e] ^= 1
            if not inside(x):
                x[e] ^= 1
                continue
            if tuple(x) in seen:
                continue
            seen.add(tuple(x))
            x2, gamma, flips, P, comp = phi(S, x, alpha, c)
            out = arcs(S, x, t)
            t1 = [te ^ (i in gamma) for i, te in enumerate(t)]
            x1 = [b ^ (i in flips) for i, b in enumerate(x)]
            out1 = arcs(S, x1, t1)
            same = cyclic_arcs(out1, components(out1)) == cyclic_arcs(out, comp)
            out2 = arcs(S, x2, tq)
            comp2 = components(out2)
            image = same_line(line_class(S, tq, comp2), c)
            back = image and phi(S, x2, partner, c)[0] == x
            classes = seam_classes(S.edges, S.faces, S.loops, P)
            stats["examined"] += 1
            stats["lemma holds"] += same
            stats["image in the partner line event"] += image
            stats["involution returns"] += bool(back)
            stats["seams carry only 0 and PD(c)"] += classes <= {(0, 0, 0, 0), pdc}
            stats["PD(c) realized"] += pdc in span_gf2(classes)
            wrong = [b ^ (i in gamma and i not in flips) for i, b in enumerate(x)]
            out0 = arcs(S, wrong, t1)
            controls["bits flipped on the wrong wall edges change the cyclic arcs"] += cyclic_arcs(out0, components(out0)) != cyclic_arcs(out, comp)
        label = f"L{shape} twist {''.join(map(str, alpha))} class {c}"
        checks[label] = stats
        if stats["examined"] == 0 or any(stats[k] != stats["examined"] for k in ("lemma holds", "image in the partner line event",
                                                                            "involution returns", "PD(c) realized")):
            failures.append(f"{label}: the wall theorem fails")

    # Lemma E in general: random vertex sets of a surface; the seam classes lie among the duals of the open star's classes
    S = Surface(3, 2, 2, 2)
    inside_star, inside_graph, trials = 0, 0, 300
    for _ in range(trials):
        P = {v for v in range(S.V) if rng.random() < 0.5}
        seams = span_gf2(seam_classes(S.edges, S.faces, S.loops, P) or {(0, 0, 0, 0)})
        star = {pd_surface(y) for y in span_gf2(surface_cycle_classes(S, P, open_star_edges(S, P)) or {(0, 0, 0, 0)})}
        graph = {pd_surface(y) for y in span_gf2(surface_cycle_classes(S, P) or {(0, 0, 0, 0)})}
        inside_star += seams <= star
        inside_graph += seams <= graph
    checks["surface L(3,2,2,2), random vertex sets"] = {"sets": trials, "seam classes among duals of the open star's classes": inside_star,
                                                       "seam classes among duals of G[P]'s classes (diagonals ignored)": inside_graph}
    if inside_star != trials:
        failures.append("Lemma E in general fails")
    controls["diagonal squares matter"] = trials - inside_graph

    # Lemma F: on a 5 x 5 x 5 torus, loops whose open star is a tube (they stay within two consecutive values of y and of z) carry no
    # seam class; a full slice does
    Q = Cubic((5, 5, 5))
    index = {c: i for i, c in enumerate(Q.coords)}
    zero, trials = 0, 200
    for _ in range(trials):
        y0, z0, y, z = rng.randrange(5), rng.randrange(5), 0, 0
        P = set()
        for xx in range(5):
            P.add(index[(xx, (y0 + y) % 5, (z0 + z) % 5)])
            if rng.random() < 0.5:
                y ^= 1
                P.add(index[(xx, (y0 + y) % 5, (z0 + z) % 5)])
            if rng.random() < 0.5:
                z ^= 1
                P.add(index[(xx, (y0 + y) % 5, (z0 + z) % 5)])
        zero += seam_classes(Q.edges, Q.faces, Q.loops, P) <= {(0, 0, 0)}
    checks["cubic 5x5x5, loops along x within a 2 x 2 tube"] = {"loops": trials, "only the zero seam class": zero}
    if zero != trials:
        failures.append("Lemma F fails for tubes")
    Q = Cubic((3, 3, 3))
    slab = {v for v, (cx, cy, cz) in enumerate(Q.coords) if cz == 0}
    controls["full slice supports a nonzero seam class"] += bool(seam_classes(Q.edges, Q.faces, Q.loops, slab) - {(0, 0, 0)})
    # the control for surfaces: two disjoint loops on L(3,2,2,2), the top row of the top block (class h2) and column 4 of the right
    # block (class v2), whose vertex sets are not joined by any edge
    S = Surface(3, 2, 2, 2)
    two = set()
    for e in [2 * 13, 2 * 14, 2 * 15] + [2 * 4 + 1, 2 * 9 + 1]:   # bottom edges of cells (0..2, 3); left edges of cells (4, 0), (4, 1)
        two |= {S.edges[e][0], S.edges[e][1]}
    if len(span_gf2(seam_classes(S.edges, S.faces, S.loops, two) or {(0, 0, 0, 0)})) == 4:
        controls["two disjoint loops of classes h2 and v2 support two independent seam classes"] += 1
    if not all(v > 0 for v in controls.values()):
        failures.append("a control was not rejected")
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
    print(f"{result['status']}: the surface wall and the seam lemmas checked")
    for f in outcome["failures"]:
        print("  failed:", f)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
