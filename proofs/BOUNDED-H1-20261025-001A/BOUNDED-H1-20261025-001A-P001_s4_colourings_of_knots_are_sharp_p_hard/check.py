"""Check for BOUNDED-H1-20261025-001A-P001: S4 colourings of knots are #P-hard.

Standard library only. Parts:
  1. the bicycle law: on the alternating diagram D(G^(3)), the colourings by S3 transpositions are the vertex potentials, and the
     number of S4 transposition lifts over a potential is 2^(nullity of the F2 Laplacian of the monochromatic subgraph);
     left-right cycles of a plane graph number c + dim B (Rosenstiehl-Read), checked directly;
  2. counts: the parity form, the 12-state model, and 2^-n 4^m Z_Potts(G; 12, 1/2) for subdivided graphs (links);
  3. the local lemma: a 3-twist fixes S3 colours and, on S4 lifts, swaps bits iff the two colours are equal;
  4. gadgets: effective interactions in span{J, I, N}, spanning-tree and 2-forest parities, knots preserved;
  5. end-to-end knot counts against 2^-N alpha^m P_G(b, g);
  6. the interpolation that recovers P(H, 12) from knot counts, after doubling the edges outside a spanning tree;
  7. controls.
Writes result.json next to this file."""
import itertools
import json
import math
import random
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ------------------------------------------------------------------------------------------------------------- plane graphs
def cycle(n):
    return (n, [(i, (i + 1) % n) for i in range(n)], {i: [i, (i - 1) % n] for i in range(n)})


def theta(k):
    return (2, [(0, 1)] * k, {0: list(range(k)), 1: list(reversed(range(k)))})


GRAPHS = {
    "single edge": (2, [(0, 1)], {0: [0], 1: [0]}),
    "path": (3, [(0, 1), (1, 2)], {0: [0], 1: [0, 1], 2: [1]}),
    "C3": cycle(3), "C4": cycle(4), "C5": cycle(5), "theta2": theta(2), "theta3": theta(3),
    "diamond": (4, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 2)], {0: [2, 0], 1: [0, 1, 3], 2: [1, 2, 4], 3: [3, 4]}),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], {0: [0, 1, 2], 1: [3, 0, 4], 2: [5, 1, 3], 3: [4, 2, 5]}),
    "triangle with pendant": (4, [(0, 1), (1, 2), (2, 0), (2, 3)], {0: [0, 2], 1: [1, 0], 2: [2, 1, 3], 3: [3]}),
    # a 4-cycle with two pendant edges: the smallest graph where the law without the bicycle term fails
    "C4 with two pendants": (6, [(0, 2), (0, 3), (1, 3), (2, 4), (2, 5), (3, 5)],
                             {0: [1, 0], 1: [2], 2: [0, 4, 3], 3: [1, 2, 5], 4: [3], 5: [4, 5]}),
}


def grid_subgraph(W, H, keep, rng):
    pts = [(x, y) for y in range(H) for x in range(W)]
    idx = {p: i for i, p in enumerate(pts)}
    E = []
    for (x, y) in pts:
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            q = (x + dx, y + dy)
            if q in idx and rng.random() < keep:
                E.append((idx[(x, y)], idx[q]))
    n = len(pts)
    if components(n, E) != 1:
        return None
    rot = {}
    for u in range(n):
        x0, y0 = pts[u]
        inc = [e for e, (a, b) in enumerate(E) if u in (a, b)]
        rot[u] = sorted(inc, key=lambda e: math.atan2(pts[E[e][0] + E[e][1] - u][1] - y0, pts[E[e][0] + E[e][1] - u][0] - x0))
    return n, E, rot


def square_grid(W, H):
    pts = [(x, y) for y in range(H) for x in range(W)]
    idx = {p: i for i, p in enumerate(pts)}
    E = [(idx[(x, y)], idx[(x + dx, y + dy)]) for (x, y) in pts for dx, dy in ((1, 0), (0, 1)) if (x + dx, y + dy) in idx]
    rot = {}
    for u in range(len(pts)):
        x0, y0 = pts[u]
        inc = [e for e, (a, b) in enumerate(E) if u in (a, b)]
        rot[u] = sorted(inc, key=lambda e: math.atan2(pts[E[e][0] + E[e][1] - u][1] - y0, pts[E[e][0] + E[e][1] - u][0] - x0))
    return len(pts), E, rot


def thicken(n, edges, rot, k):
    ne, idx = [], {}
    for e, (u, v) in enumerate(edges):
        idx[e] = list(range(len(ne), len(ne) + k))
        ne += [(u, v)] * k
    nrot = {u: [] for u in range(n)}
    for u in range(n):
        for e in rot[u]:
            nrot[u].extend(idx[e] if edges[e][0] == u else list(reversed(idx[e])))
    return ne, nrot


def subdivide(n, edges, rot):
    ne, nrot = [], {}
    for e, (u, v) in enumerate(edges):
        ne.append((u, n + e))
        ne.append((n + e, v))
    for u in range(n):
        nrot[u] = [2 * e if edges[e][0] == u else 2 * e + 1 for e in rot[u]]
    for e in range(len(edges)):
        nrot[n + e] = [2 * e, 2 * e + 1]
    return n + len(edges), ne, nrot


def components(n, E):
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    c = n
    for u, v in E:
        a, b = f(u), f(v)
        if a != b:
            par[a] = b
            c -= 1
    return c


# --------------------------------------------------------------------------- the alternating diagram D(G) of a plane graph
def diagram(n, edges, rot):
    """crossing per edge of G; slots (e, end, side); over strand = (0,F1)-(1,F2). Returns arcs, crossings (over, in, out), links."""
    m = len(edges)
    link = {}
    for w in range(n):
        r = rot[w]
        for i in range(len(r)):
            a, b = r[i], r[(i + 1) % len(r)]
            ea = 0 if edges[a][0] == w else 1
            eb = 0 if edges[b][0] == w else 1
            sa = (a, ea, "F2" if ea == 0 else "F1")
            sb = (b, eb, "F1" if eb == 0 else "F2")
            link[sa] = sb
            link[sb] = sa
    opp = {}
    for e in range(m):
        opp[(e, 0, "F1")] = (e, 1, "F2")
        opp[(e, 1, "F2")] = (e, 0, "F1")
        opp[(e, 0, "F2")] = (e, 1, "F1")
        opp[(e, 1, "F1")] = (e, 0, "F2")
    is_over = lambda s: (s[1], s[2]) in ((0, "F1"), (1, "F2"))
    seen, comps = set(), []
    for e in range(m):
        for start in ((e, 0, "F1"), (e, 0, "F2")):
            if start in seen:
                continue
            comp, s = [], start
            while s not in seen:
                seen.add(s)
                t = opp[s]
                seen.add(t)
                comp.append((s[0], is_over(s)))
                s = link[t]
            comps.append(comp)
    arc_id, over_arc, unders = 0, {}, {e: [] for e in range(m)}
    for comp in comps:
        k = next(i for i, (e, ov) in enumerate(comp) if not ov)
        comp = comp[k + 1:] + comp[:k + 1]
        first = cur = arc_id
        arc_id += 1
        for i, (e, ov) in enumerate(comp):
            if ov:
                over_arc[e] = cur
            else:
                nxt = arc_id if i < len(comp) - 1 else first
                if i < len(comp) - 1:
                    arc_id += 1
                unders[e].append((cur, nxt))
                cur = nxt
    crossings = []
    for e in range(m):
        assert len(unders[e]) == 1
        (a, b), = unders[e]
        crossings.append((over_arc[e], a, b))
    return arc_id, crossings, len(comps)


def link_components(n, edges, rot):
    if not edges:
        return n
    return diagram(n, edges, rot)[2]


# ------------------------------------------------------------------------------------------------------------ S3 and S4 data
def pmul(p, q):
    return tuple(p[q[i]] for i in range(4))


def transposition(i, j):
    p = list(range(4))
    p[i], p[j] = p[j], p[i]
    return tuple(p)


T = [transposition(0, 1), transposition(2, 3), transposition(0, 2), transposition(1, 3), transposition(0, 3), transposition(1, 2)]
CONJ = [[T.index(pmul(pmul(T[b], T[a]), T[b])) for a in range(6)] for b in range(6)]
# class k // 2 = the pairing fixed (= the image transposition in S4/V4 = S3); with labels 0, 1, 2 the S3 rule is c' = 2 b - a
assert all(CONJ[b][a] // 2 == (2 * (b // 2) - a // 2) % 3 for a in range(6) for b in range(6))


def nullspace_mod3(rows, nv):
    A = [r[:] for r in rows]
    piv, r = [], 0
    for c in range(nv):
        pr = next((i for i in range(r, len(A)) if A[i][c] % 3), None)
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        inv = 1 if A[r][c] % 3 == 1 else 2
        A[r] = [(x * inv) % 3 for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] % 3:
                f = A[i][c]
                A[i] = [(x - f * y) % 3 for x, y in zip(A[i], A[r])]
        piv.append(c)
        r += 1
    basis = []
    for fc in (c for c in range(nv) if c not in piv):
        v = [0] * nv
        v[fc] = 1
        for i, pc in enumerate(piv):
            v[pc] = (-A[i][fc]) % 3
        basis.append(v)
    return basis


def s3_colourings(na, crossings):
    rows = []
    for o, u, w in crossings:
        r = [0] * na
        r[w] += 1
        r[o] -= 2
        r[u] += 1
        rows.append([x % 3 for x in r])
    basis = nullspace_mod3(rows, na)
    for coeffs in itertools.product(range(3), repeat=len(basis)):
        yield [sum(c * b[a] for c, b in zip(coeffs, basis)) % 3 for a in range(na)]


def f2_affine_dimension(rows, nv):
    """rows over F2 with a constant last entry; returns dimension of the solution set, or None if empty"""
    A = [r[:] for r in rows]
    rank = 0
    for c in range(nv):
        pr = next((i for i in range(rank, len(A)) if A[i][c]), None)
        if pr is None:
            continue
        A[rank], A[pr] = A[pr], A[rank]
        for i in range(len(A)):
            if i != rank and A[i][c]:
                A[i] = [x ^ y for x, y in zip(A[i], A[rank])]
        rank += 1
    if any(row[nv] and not any(row[:nv]) for row in A):
        return None
    return nv - rank


def lift_dimension(na, crossings, labels):
    rows = []
    for o, u, w in crossings:
        val = {}
        for xo in (0, 1):
            for xu in (0, 1):
                res = CONJ[2 * labels[o] + xo][2 * labels[u] + xu]
                assert res // 2 == labels[w]
                val[(xo, xu)] = res % 2
        g = val[(0, 0)]
        al, be = val[(1, 0)] ^ g, val[(0, 1)] ^ g
        assert val[(1, 1)] == al ^ be ^ g
        r = [0] * (na + 1)
        r[w] ^= 1
        r[o] ^= al
        r[u] ^= be
        r[na] = g
        rows.append(r)
    return f2_affine_dimension(rows, na)


def f2_laplacian_nullity(n, E):
    L = [[0] * n for _ in range(n)]
    for u, v in E:
        if u == v:
            continue
        L[u][u] ^= 1
        L[v][v] ^= 1
        L[u][v] ^= 1
        L[v][u] ^= 1
    rows = [r + [0] for r in L]
    return f2_affine_dimension(rows, n)


def s4_count(n, edges, rot, k=3, detail=False):
    ne, nrot = thicken(n, edges, rot, k)
    na, cr, nc = diagram(n, ne, nrot)
    total, per = 0, []
    for labels in s3_colourings(na, cr):
        d = lift_dimension(na, cr, labels)
        total += 2 ** d
        if detail:
            D = frozenset(j // k for j, (o, u, w) in enumerate(cr) if labels[o] != labels[u])
            per.append((D, d))
    return total, nc, per


# ---------------------------------------------------------------------------------------------------- counts and polynomials
def potts(n, E, q, v):
    tot = Fraction(0)
    for r in range(len(E) + 1):
        for A in itertools.combinations(range(len(E)), r):
            tot += Fraction(q) ** components(n, [E[i] for i in A]) * Fraction(v) ** r
    return tot


def chromatic(n, E, q):
    return potts(n, E, q, -1)


def parity_form(n, E):
    tot = 0
    for st in itertools.product(range(6), repeat=n):
        par = [0] * n
        for u, v in E:
            if st[u] // 2 == st[v] // 2 and st[u] % 2 != st[v] % 2:
                par[u] ^= 1
                par[v] ^= 1
        tot += not any(par)
    return tot


STATES = [(t, p, x) for t in (0, 1) for p in range(3) for x in (0, 1)]
NU = {z: (1 - z[0], z[1], 1 - z[2]) for z in STATES}
SIDX = {z: i for i, z in enumerate(STATES)}
NMAT = [[1 if NU[STATES[i]] == STATES[j] else 0 for j in range(12)] for i in range(12)]
MMAT = [[1 - 2 * NMAT[i][j] for j in range(12)] for i in range(12)]


def twelve_state(n, E, mat):
    tot = 0
    for zs in itertools.product(range(12), repeat=n):
        w = 1
        for u, v in E:
            w *= mat[zs[u]][zs[v]]
            if not w:
                break
        tot += w
    return tot


def pg_coefficients(n, E):
    """N[(i, j)] = number of z in Z12^n with i equal edges and j N-related edges"""
    N = {}
    for zs in itertools.product(range(12), repeat=n):
        i = j = 0
        for u, v in E:
            if zs[u] == zs[v]:
                i += 1
            elif NMAT[zs[u]][zs[v]]:
                j += 1
        N[(i, j)] = N.get((i, j), 0) + 1
    return N


def tree_count(n, E):
    """matrix-tree theorem with exact fractions"""
    if n == 1:
        return 1
    L = [[Fraction(0)] * n for _ in range(n)]
    for u, v in E:
        if u == v:
            continue
        L[u][u] += 1
        L[v][v] += 1
        L[u][v] -= 1
        L[v][u] -= 1
    A = [row[1:] for row in L[1:]]
    det, size = Fraction(1), n - 1
    for c in range(size):
        pr = next((i for i in range(c, size) if A[i][c] != 0), None)
        if pr is None:
            return 0
        if pr != c:
            A[c], A[pr] = A[pr], A[c]
            det = -det
        det *= A[c][c]
        for i in range(c + 1, size):
            if A[i][c] != 0:
                f = A[i][c] / A[c][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[c])]
    return int(abs(det))


# --------------------------------------------------------------------------------------------------------------- gadgets
def parse(s, i=0):
    if s[i] == "e":
        return ("e",), i + 1
    op = s[i]
    a, j = parse(s, i + 2)
    b, k = parse(s, j + 1)
    return (op, a, b), k + 1


def tree_of(desc):
    return parse(desc)[0]


def draw(tree, edges, rot, nv, t0, t1):
    if tree[0] == "e":
        e = len(edges)
        edges.append((t0, t1))
        return [e], [e]
    if tree[0] == "P":
        a0, a1 = draw(tree[1], edges, rot, nv, t0, t1)
        b0, b1 = draw(tree[2], edges, rot, nv, t0, t1)
        return a0 + b0, a1 + b1
    m = nv[0]
    nv[0] += 1
    a0, a1 = draw(tree[1], edges, rot, nv, t0, m)
    b0, b1 = draw(tree[2], edges, rot, nv, m, t1)
    rot[m] = a1 + list(reversed(b0))
    return a0, b1


def substitute(n, E, R, tree):
    edges, rot, nv, at = [], {}, [n], {}
    for e, (u, v) in enumerate(E):
        o0, o1 = draw(tree, edges, rot, nv, u, v)
        at[(e, u)] = list(reversed(o0))
        at[(e, v)] = o1
    for u in range(n):
        rot[u] = [x for e in R[u] for x in at[(e, u)]]
    return nv[0], edges, rot


def parallel_power(tree, k):
    t = tree
    for _ in range(k - 1):
        t = ("P", tree, t)
    return t


# algebra span{J, I, N} on Z12: (alpha, beta, gamma)
def alg_ser(A, B):
    a, b, g = A
    a2, b2, g2 = B
    return (12 * a * a2 + a * b2 + a * g2 + b * a2 + g * a2, b * b2 + g * g2, b * g2 + g * b2)


def alg_par(A, B):
    a, b, g = A
    a2, b2, g2 = B
    return (a * a2, a * b2 + b * a2 + b * b2, a * g2 + g * a2 + g * g2)


def alg_eval(tree):
    if tree[0] == "e":
        return (1, 0, -2)
    A, B = alg_eval(tree[1]), alg_eval(tree[2])
    return alg_ser(A, B) if tree[0] == "S" else alg_par(A, B)


def matrix_eval(tree):
    """effective 12x12 interaction by summing internal vertices (series = product, parallel = entrywise)"""
    if tree[0] == "e":
        return [row[:] for row in MMAT]
    A, B = matrix_eval(tree[1]), matrix_eval(tree[2])
    if tree[0] == "S":
        return [[sum(A[i][k] * B[k][j] for k in range(12)) for j in range(12)] for i in range(12)]
    return [[A[i][j] * B[i][j] for j in range(12)] for i in range(12)]


def tf_counts(tree):
    """(t, f): spanning trees of the two-terminal network, and spanning forests with two trees separating the terminals"""
    if tree[0] == "e":
        return (1, 1)
    (t1, f1), (t2, f2) = tf_counts(tree[1]), tf_counts(tree[2])
    if tree[0] == "S":
        return (t1 * t2, t1 * f2 + f1 * t2)
    return (t1 * f2 + f1 * t2, f1 * f2)


def gadget_trees(size):
    out = {1: [("e",)]}
    for s in range(2, size + 1):
        out[s] = []
        for s1 in range(1, s):
            for A in out[s1]:
                for B in out[s - s1]:
                    out[s].append(("S", A, B))
                    out[s].append(("P", A, B))
    return out


def desc_of(tree):
    return "e" if tree[0] == "e" else f"{tree[0]}({desc_of(tree[1])},{desc_of(tree[2])})"


# ------------------------------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    out = {}
    ok_all = True
    rng = random.Random(20261025)
    tests = dict(GRAPHS)
    while len(tests) < len(GRAPHS) + 8:
        W, H = rng.choice([(3, 3), (2, 4), (3, 4)])
        g = grid_subgraph(W, H, rng.uniform(0.6, 0.9), rng)
        if g is None or len(g[1]) > 13 or g[0] > 9:
            continue
        tests[f"random grid subgraph {len(tests) - len(GRAPHS) + 1}"] = g

    # ------------------------------------------------------------------ part 3 (local lemma) first
    s3_trivial = True
    for a in range(3):
        for b in range(3):
            x, y = a, b
            for _ in range(3):
                x, y = (2 * x - y) % 3, x
            s3_trivial &= (x, y) == (a, b)
    swap_ok = True
    for a in range(6):
        for b in range(6):
            x, y = a, b
            for _ in range(3):
                x, y = CONJ[x][y], x
            same = a // 2 == b // 2
            if same:
                swap_ok &= (x, y) == (b, a) or (x // 2, y // 2) == (b // 2, a // 2) and (x, y) == (b, a)
            else:
                # positions keep their colours and the bit at each position changes by a constant independent of the other bit
                swap_ok &= (x // 2, y // 2) == (a // 2, b // 2)
    # the bit transfer for unequal colours: as a map of (bit_left, bit_right) it is position-preserving up to constants
    pos_ok = True
    for ca in range(3):
        for cb in range(3):
            if ca == cb:
                continue
            maps = {}
            for xa in (0, 1):
                for xb in (0, 1):
                    x, y = 2 * ca + xa, 2 * cb + xb
                    for _ in range(3):
                        x, y = CONJ[x][y], x
                    maps[(xa, xb)] = (x % 2, y % 2)
            c0 = maps[(0, 0)]
            pos_ok &= all(maps[(xa, xb)] == (xa ^ c0[0], xb ^ c0[1]) for xa in (0, 1) for xb in (0, 1))
    p3 = {"3-twist fixes S3 colours": s3_trivial, "equal colours: bits follow strands": swap_ok,
          "unequal colours: bits keep positions (plus constants)": pos_ok}
    out["3_local_lemma"] = p3
    ok3 = all(p3.values())
    print("part 3 local lemma:", p3, flush=True)
    ok_all &= ok3

    # ------------------------------------------------------------------ part 1: bicycle law
    p1 = {}
    ok1 = True
    for name, (n, E, R) in tests.items():
        total, nc, per = s4_count(n, E, R, detail=True)
        # potentials: the multiset of jump sets equals that of phi in Z3^V
        jumps = Counter(D for D, d in per)
        pot = Counter(frozenset(e for e, (u, v) in enumerate(E) if phi[u] != phi[v]) for phi in itertools.product(range(3), repeat=n))
        law = all(d == f2_laplacian_nullity(n, [E[e] for e in range(len(E)) if e not in D]) for D, d in per)
        # left-right cycles of the monochromatic subgraphs (Rosenstiehl-Read): components of D(H) = nullity, H as a plane subgraph
        rr = True
        for D in list(jumps)[:40]:
            keep = [e for e in range(len(E)) if e not in D]
            sub_e = [E[e] for e in keep]
            ren = {e: i for i, e in enumerate(keep)}
            sub_r = {u: [ren[e] for e in R[u] if e in ren] for u in range(n)}
            isolated = sum(1 for u in range(n) if not sub_r[u])
            lc = (diagram(n, sub_e, sub_r)[2] if sub_e else 0) + isolated
            rr &= lc == f2_laplacian_nullity(n, sub_e)
        good = jumps == pot and law and rr
        p1[name] = {"vertices": n, "edges": len(E), "colourings": len(per), "potential bijection": jumps == pot,
                    "lift dimension = F2 Laplacian nullity": law, "left-right cycles = nullity": rr, "S4 count": total,
                    "components": nc}
        ok1 &= good
        print(f"part 1 {name:28s} n={n} m={len(E)}: potentials {jumps == pot}, law {law}, left-right {rr} ({time.time() - t0:.0f} s)",
              flush=True)
    out["1_bicycle_law"] = {"rows": p1, "ok": ok1}
    ok_all &= ok1

    # ------------------------------------------------------------------ part 2: parity form, 12-state model, Potts (links)
    p2 = {}
    ok2 = True
    for name in ("single edge", "path", "C3", "C4", "theta2", "theta3", "diamond", "K4", "triangle with pendant"):
        n, E, R = GRAPHS[name]
        total = p1[name]["S4 count"]
        pf = parity_form(n, E)
        ts = Fraction(twelve_state(n, E, MMAT), 2 ** n)
        n2, E2, R2 = subdivide(n, E, R)
        if 3 ** n2 <= 60000:
            tot2, nc2, _ = s4_count(n2, E2, R2)
        else:
            tot2, nc2 = None, link_components(*((n2,) + thicken(n2, E2, R2, 3)))
        z = Fraction(4) ** len(E) * potts(n, E, 12, Fraction(1, 2)) / Fraction(2) ** n
        beta1 = len(E) - n + 1
        good = total == pf == ts and (tot2 is None or tot2 == z) and nc2 == 1 + beta1
        p2[name] = {"S4": total, "parity form": pf, "12-state": str(ts), "subdivided S4": tot2, "2^-n 4^m Z(G;12,1/2)": str(z),
                    "subdivided link components": nc2, "1 + beta1": 1 + beta1, "ok": good}
        ok2 &= good
        print(f"part 2 {name:22s}: S4 {total} parity {pf} 12-state {ts}; subdivided {tot2} vs Potts {z}; components {nc2} "
              f"(1 + beta1 = {1 + beta1}) {'ok' if good else 'FAIL'}", flush=True)
    out["2_counts"] = {"rows": p2, "ok": ok2}
    ok_all &= ok2

    # ------------------------------------------------------------------ part 4: gadgets
    trees = gadget_trees(5)
    p4 = {"algebra": True, "knots": {}, "breaks": {}}
    knot_hosts = {"triangle with pendant": GRAPHS["triangle with pendant"], "C3": GRAPHS["C3"], "grid 2x3": square_grid(3, 2)}
    for name, (n, E, R) in knot_hosts.items():
        assert tree_count(n, E) % 2 == 1
    seen = set()
    for size in range(1, 6):
        for tr in trees[size]:
            d = desc_of(tr)
            vec = alg_eval(tr)
            a, b, g = vec
            if size <= 4:
                Mx = matrix_eval(tr)
                pred = [[a + (b if i == j else 0) + (g if NMAT[i][j] else 0) for j in range(12)] for i in range(12)]
                p4["algebra"] &= Mx == pred
            t, f = tf_counts(tr)
            key = (vec, t % 2, f % 2)
            if key in seen:
                continue
            seen.add(key)
            comps = {}
            for hn, (n, E, R) in knot_hosts.items():
                N, E2, R2 = substitute(n, E, R, tr)
                assert tree_count(N, E2) == tree_count(n, E) * t ** (n - 1) * f ** (len(E) - n + 1)
                ne, nrot = thicken(N, E2, R2, 3)
                comps[hn] = diagram(N, ne, nrot)[2]
            if t % 2 == 1 and f % 2 == 1:
                p4["knots"][d] = comps
            else:
                p4["breaks"][d] = comps
    knots_ok = all(all(c == 1 for c in v.values()) for v in p4["knots"].values())
    breaks_ok = all(any(c > 1 for c in v.values()) for v in p4["breaks"].values())
    ok4 = p4["algebra"] and knots_ok and breaks_ok
    p4["odd-odd gadgets keep knots"] = knots_ok
    p4["other gadgets break knots on some host"] = breaks_ok
    p4["ok"] = ok4
    out["4_gadgets"] = {"algebra on gadgets up to 4 edges": p4["algebra"], "odd tree and forest counts keep knots": knots_ok,
                        "number of knot-keeping gadget classes": len(p4["knots"]), "number of other classes": len(p4["breaks"]),
                        "other classes break knots": breaks_ok, "ok": ok4}
    print(f"part 4 gadgets: algebra {p4['algebra']}, knot-keeping classes {len(p4['knots'])} all knots {knots_ok}, "
          f"other classes {len(p4['breaks'])} break {breaks_ok} ({time.time() - t0:.0f} s)", flush=True)
    ok_all &= ok4

    # ------------------------------------------------------------------ part 5: end-to-end knot counts
    G1 = tree_of("S(e,P(e,S(e,e)))")
    G2 = tree_of("P(e,S(e,P(e,S(e,S(e,e)))))")
    p5 = {}
    ok5 = True
    for hn, gtree in (("single edge", G1), ("path", G1), ("C3", G1), ("single edge", G2)):
        n, E, R = GRAPHS[hn]
        N, E2, R2 = substitute(n, E, R, gtree)
        total, nc, _ = s4_count(N, E2, R2)
        a, b, g = alg_eval(gtree)
        Nco = pg_coefficients(n, E)
        Bh, Gh = Fraction(a + b, a), Fraction(a + g, a)
        pg = sum(c * Bh ** i * Gh ** j for (i, j), c in Nco.items())
        pred = Fraction(a) ** len(E) * pg / Fraction(2) ** N
        good = total == pred and nc == 1
        p5[f"{hn} with {desc_of(gtree)}"] = {"vertices": N, "components": nc, "S4": total, "predicted": str(pred), "ok": good}
        ok5 &= good
        print(f"part 5 {hn} with {desc_of(gtree)}: components {nc}, S4 {total}, predicted {pred} {'ok' if good else 'FAIL'}",
              flush=True)
    out["5_knot_counts"] = {"rows": p5, "ok": ok5}
    ok_all &= ok5

    # ------------------------------------------------------------------ part 6: interpolation recovers P(H, 12)
    p6 = {}
    ok6 = True
    a1, b1, g1 = alg_eval(G1)
    B1, Gm1 = Fraction(a1 + b1, a1), Fraction(a1 + g1, a1)
    assert (B1, Gm1) == (Fraction(25, 17), Fraction(15, 17))
    for hn in ("K4", "C5", "diamond"):
        n, E, R = GRAPHS[hn]
        # spanning tree by BFS; double the other edges (parallel copies drawn next to the originals)
        seen_v, tree_e, st = {0}, set(), [0]
        while st:
            u = st.pop()
            for e in R[u]:
                w = E[e][0] + E[e][1] - u
                if w not in seen_v:
                    seen_v.add(w)
                    tree_e.add(e)
                    st.append(w)
        Ht, Rt = [], {u: [] for u in range(n)}
        newid = {}
        for e, (u, v) in enumerate(E):
            newid[e] = [len(Ht)] if e in tree_e else [len(Ht), len(Ht) + 1]
            Ht += [(u, v)] * len(newid[e])
        for u in range(n):
            for e in R[u]:
                Rt[u].extend(newid[e] if E[e][0] == u else list(reversed(newid[e])))
        tau_t = tree_count(n, Ht)
        Pt, P0 = chromatic(n, Ht, 12), chromatic(n, E, 12)
        knot1 = diagram(n, *thicken(n, Ht, Rt, 3))[2]
        Nco = pg_coefficients(n, Ht)
        m2 = len(Ht)
        keys = sorted(Nco)
        # oracle values from the proved formula: E(k) = sum N_ij (B1^i G1^j)^k for k = 1, 3, 5, ...
        Ev = [sum(c * (B1 ** i * Gm1 ** j) ** k for (i, j), c in Nco.items()) for k in range(1, 2 * len(keys), 2)]
        # solve for unknown coefficients over the candidate bases (i + j <= m2) by exact elimination
        cand = [(i, j) for i in range(m2 + 1) for j in range(m2 + 1 - i)]
        bases = [B1 ** i * Gm1 ** j for (i, j) in cand]
        distinct = len(set(bases)) == len(bases)
        rows = [[bb ** k for bb in bases] for k in range(1, 2 * len(cand), 2)]
        rhs = [sum(c * (B1 ** i * Gm1 ** j) ** k for (i, j), c in Nco.items()) for k in range(1, 2 * len(cand), 2)]
        A = [r + [y] for r, y in zip(rows, rhs)]
        K = len(cand)
        for c in range(K):
            pr = next(i for i in range(c, K) if A[i][c] != 0)
            A[c], A[pr] = A[pr], A[c]
            inv = 1 / A[c][c]
            A[c] = [x * inv for x in A[c]]
            for i in range(K):
                if i != c and A[i][c] != 0:
                    f = A[i][c]
                    A[i] = [x - f * y for x, y in zip(A[i], A[c])]
        sol = {cand[i]: A[i][K] for i in range(K)}
        recovered = sum(v for (i, j), v in sol.items() if i == 0)
        # the knot diagrams for the first two odd powers really are knots
        kn = []
        for k in (1, 3):
            N, E2, R2 = substitute(n, Ht, Rt, parallel_power(G1, k))
            kn.append(diagram(N, *thicken(N, E2, R2, 3))[2])
        good = tau_t % 2 == 1 and Pt == P0 and knot1 == 1 and distinct and recovered == P0 and all(c == 1 for c in kn)
        p6[hn] = {"trees of doubled graph": tau_t, "P(H,12)": str(P0), "P(doubled,12)": str(Pt), "doubled diagram components": knot1,
                  "bases distinct": distinct, "recovered P(H,12)": str(recovered), "knot components for k=1,3": kn, "ok": good}
        ok6 &= good
        print(f"part 6 {hn}: tau {tau_t}, P(H,12) {P0}, recovered {recovered}, knots {kn} {'ok' if good else 'FAIL'} "
              f"({time.time() - t0:.0f} s)", flush=True)
    out["6_interpolation"] = {"rows": p6, "ok": ok6}
    ok_all &= ok6

    # ------------------------------------------------------------------ part 7: controls
    c = {}
    n, E, R = GRAPHS["C4 with two pendants"]
    _, _, per = s4_count(n, E, R, detail=True)
    c["law without the bicycle term fails on C4 with two pendants"] = any(
        d != components(n, [E[e] for e in range(len(E)) if e not in D]) for D, d in per)
    six = True
    for name in ("C3", "C4", "diamond"):
        n, E, R = GRAPHS[name]
        tot6, nc6, _ = s4_count(n, E, R, k=6)
        six &= tot6 == 3 ** n * 2 ** nc6
    c["6-twists decouple: count = 3^n 2^components"] = six
    n, E, R = GRAPHS["C4"]
    n2, E2, R2 = subdivide(n, E, R)
    tot2 = p2["C4"]["subdivided S4"]
    c["wrong Potts parameters rejected"] = all(tot2 != Fraction(4) ** len(E) * potts(n, E, q, v) / Fraction(2) ** n
                                               for q, v in ((6, Fraction(1, 2)), (12, Fraction(-1, 2)), (12, 1)))
    n, E, R = GRAPHS["C3"]
    N, E2, R2 = substitute(n, E, R, parallel_power(G1, 2))
    c["even parallel power of the gadget gives a link"] = diagram(N, *thicken(N, E2, R2, 3))[2] > 1
    ok7 = all(c.values())
    out["7_controls"] = {"rows": c, "ok": ok7}
    print("part 7 controls:", c, flush=True)
    ok_all &= ok7

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "BOUNDED-H1-20261025-001A-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
