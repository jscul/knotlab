"""Away from the knot's law, counting on the knot's spaces is #P-hard (KNOT-COUPLING-20261031-001B).

Exact arithmetic in Q(i): a number is a pair (re, im) of Fractions. Systems are lists of 3-point lines; a signing is a set of
(line index, point) incidences. This module does not import ticket A's library: it has its own counter, its own atom builder and its own
interpolation, so the end-to-end check is independent of the code that established the gadget lemmas."""
import itertools
from fractions import Fraction

import networkx as nx


# ------------------------------------------------------------------------------------------------ exact complex rationals
def C(a, b=0):
    return (Fraction(a), Fraction(b))


def cadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


def csub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def cmul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def cinv(x):
    d = x[0] * x[0] + x[1] * x[1]
    return (x[0] / d, -x[1] / d)


def cdiv(x, y):
    return cmul(x, cinv(y))


def cpow(x, k):
    if k < 0:
        return cpow(cinv(x), -k)
    out, base = C(1), x
    while k:
        if k & 1:
            out = cmul(out, base)
        base = cmul(base, base)
        k >>= 1
    return out


ZERO, ONE = C(0), C(1)


# ------------------------------------------------------------------------------------------------ counting by a junction-tree pass
def count(lines, lam, neg=frozenset()):
    """M(H, sigma; lam) = sum over 2-colourings of lam ** (number of monochromatic lines), exactly, lam in Q(i).
    Elimination order from networkx's min-fill-in tree decomposition heuristic on the primal graph (points adjacent when collinear)."""
    pts = sorted({p for l in lines for p in l}, key=repr)
    primal = nx.Graph()
    primal.add_nodes_from(pts)
    for l in lines:
        primal.add_edges_from(itertools.combinations(l, 2))
    order = []
    g = primal.copy()
    while g.number_of_nodes():
        def fill(v):
            nb = list(g[v])
            return sum(1 for a, b in itertools.combinations(nb, 2) if not g.has_edge(a, b))
        v = min(g.nodes, key=lambda v: (fill(v), g.degree(v), repr(v)))
        nb = list(g[v])
        g.add_edges_from(itertools.combinations(nb, 2))
        g.remove_node(v)
        order.append(v)
    pos = {v: k for k, v in enumerate(order)}
    buckets = {v: [] for v in order}
    for i, l in enumerate(lines):
        scope = tuple(sorted(set(l), key=lambda p: pos[p]))
        tab = {}
        for a in itertools.product((0, 1), repeat=len(scope)):
            col = dict(zip(scope, a))
            tab[a] = lam if len({col[p] ^ ((i, p) in neg) for p in l}) == 1 else ONE
        buckets[scope[0]].append((scope, tab))
    result = ONE
    for v in order:
        fs = buckets[v]
        scope = tuple(sorted({q for s, _ in fs for q in s if q != v}, key=lambda p: pos[p]))
        tab = {}
        for a in itertools.product((0, 1), repeat=len(scope)):
            asg = dict(zip(scope, a))
            tot = ZERO
            for cv in (0, 1):
                asg[v] = cv
                prod = ONE
                for s, t in fs:
                    prod = cmul(prod, t[tuple(asg[q] for q in s)])
                tot = cadd(tot, prod)
            tab[a] = tot
        if scope:
            buckets[scope[0]].append((scope, tab))
        else:
            result = cmul(result, tab[()])
    return result


# ------------------------------------------------------------------------------------------------ atoms in series
def with_chains(G, lengths, H, e0):
    """G with a chain of lengths[e] copies of the atom H<e0> on each incidence e = (line index, point) of G. In each atom the point p
    of the current incidence moves into H's line l0 (in p0's place) and the atom's p0 moves into the current line."""
    l0, p0 = e0
    lines = [list(l) for l in G]
    extra = []
    for (li, p), k in lengths.items():
        cur_line, cur_pt = ('G', li), p
        for j in range(k):
            tag = ('atom', li, repr(p), j)
            new = [[(tag, q) for q in L] for L in H]
            new[l0][new[l0].index((tag, p0))] = cur_pt                 # p takes p0's place in l0
            # p0 takes p's place in the current line
            if cur_line[0] == 'G':
                L = lines[cur_line[1]]
            else:
                L = extra[cur_line[1]]
            L[L.index(cur_pt)] = (tag, p0)
            base = len(extra)
            extra.extend(new)
            cur_line, cur_pt = cur_line, (tag, p0)
    return [tuple(l) for l in lines] + [tuple(l) for l in extra]


# ------------------------------------------------------------------------------------------------ interpolation
def newton_interpolate(xs, ys):
    """coefficients c_0..c_d of the polynomial through (xs, ys), exactly in Q(i) (distinct xs)"""
    n = len(xs)
    coef = list(ys)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = cdiv(csub(coef[i], coef[i - 1]), csub(xs[i], xs[i - j]))
    poly = [ZERO] * n
    basis = [ONE]
    for j in range(n):
        for k, c in enumerate(basis):
            poly[k] = cadd(poly[k], cmul(coef[j], c))
        nxt = [ZERO] * (len(basis) + 1)
        for k, c in enumerate(basis):
            nxt[k + 1] = cadd(nxt[k + 1], c)
            nxt[k] = csub(nxt[k], cmul(xs[j], c))
        basis = nxt
    return poly


def recover_colourings(G, O, H, e0, lam0, Da, Db, oracle=count):
    """the reduction of Theorem 1: #col(G) from the values M(G_ij; lam0) of the knot's spaces G_ij (even chains of 2i atoms off O, odd
    chains of 2j + 1 atoms on O), i <= Da, j <= Db. Returns (#col recovered, number of oracle calls, largest instance size)."""
    n = len({p for l in G for p in l})
    alpha = cdiv(count(H, lam0), C(2))
    beta = cdiv(count(H, lam0, frozenset({e0})), C(2))
    s, d = cadd(alpha, beta), csub(alpha, beta)
    rho = cdiv(d, s)
    u0 = cdiv(csub(lam0, ONE), cadd(lam0, C(3)))
    incs = [(i, p) for i, l in enumerate(G) for p in l]
    norm0 = cmul(cpow(C(2), n), cpow(cdiv(cadd(lam0, C(3)), C(4)), n))
    vals, biggest = {}, 0
    for i in range(Da + 1):
        for j in range(Db + 1):
            lengths = {e: (2 * j + 1 if e in O else 2 * i) for e in incs}
            inst = with_chains(G, lengths, H, e0)
            biggest = max(biggest, len(inst))
            m = oracle(inst, lam0)
            K = cmul(norm0, cpow(s, sum(lengths.values())))
            vals[(i, j)] = cdiv(m, K)                                   # = Q(rho^{2i}, rho^{2j})
    a_nodes = [cpow(rho, 2 * i) for i in range(Da + 1)]
    b_nodes = [cpow(rho, 2 * j) for j in range(Db + 1)]
    # first in b for each i, then in a for each power of b
    rows = {i: newton_interpolate(b_nodes, [vals[(i, j)] for j in range(Db + 1)]) for i in range(Da + 1)}
    q = {}
    for sdeg in range(Db + 1):
        col = newton_interpolate(a_nodes, [rows[i][sdeg] for i in range(Da + 1)])
        for r in range(Da + 1):
            q[(r, sdeg)] = col[r]
    target = ZERO
    w = cdiv(C(-1), cmul(C(3), u0))                                     # -1/(3 u0)
    for (r, sdeg), c in q.items():
        if (r + sdeg) % 2:
            continue                                                    # bipartite: every even subgraph has an even size
        target = cadd(target, cmul(cmul(c, cpow(rho, -sdeg)), cpow(w, (r + sdeg) // 2)))
    col_count = cmul(cmul(cpow(C(2), n), cpow(cdiv(C(3), C(4)), n)), target)
    return col_count, (Da + 1) * (Db + 1), biggest, rho, q


def even_subgraph_degrees(G, O):
    """largest |chi minus O| and |chi & O| over even subgraphs chi of the incidence graph (small graphs: cycle-space enumeration)"""
    g = nx.Graph()
    for i, l in enumerate(G):
        for p in l:
            g.add_edge(('l', i), ('p', p))
    edges = [frozenset(e) for e in g.edges()]
    idx = {e: k for k, e in enumerate(edges)}
    span = [0]
    for cyc in nx.cycle_basis(g):
        m = 0
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            m ^= 1 << idx[frozenset((a, b))]
        span += [x ^ m for x in span]
    omask = sum(1 << idx[frozenset((('l', i), ('p', p)))] for i, p in O)
    return max(bin(x & ~omask).count("1") for x in span), max(bin(x & omask).count("1") for x in span)


def remove_line(lines, idx):
    return [l for k, l in enumerate(lines) if k != idx]


def recover_deficiency_one(G, O, estar, H, e0, Ldel, lam0, Da, Db, oracle=count):
    """#col(G) from deficiency-one knot's spaces: H'_ijk = G_ij with 2k + 2 atoms on estar (an incidence outside O), minus the line Ldel of
    the first atom on estar. The first atom then acts by the edge function of H - Ldel."""
    n = len({p for l in G for p in l})
    alpha = cdiv(count(H, lam0), C(2))
    beta = cdiv(count(H, lam0, frozenset({e0})), C(2))
    s, d = cadd(alpha, beta), csub(alpha, beta)
    rho = cdiv(d, s)
    Hm = remove_line(H, Ldel)
    alpha2 = cdiv(count(Hm, lam0), C(2))
    beta2 = cdiv(count(Hm, lam0, frozenset({e0 if e0[0] < Ldel else (e0[0] - 1, e0[1])})), C(2))
    s2, d2 = cadd(alpha2, beta2), csub(alpha2, beta2)
    rho2 = cdiv(d2, s2)
    u0 = cdiv(csub(lam0, ONE), cadd(lam0, C(3)))
    incs = [(i, p) for i, l in enumerate(G) for p in l]
    norm0 = cmul(cpow(C(2), n), cpow(cdiv(cadd(lam0, C(3)), C(4)), n))
    vals, biggest = {}, 0
    for i in range(Da + 1):
        for j in range(Db + 1):
            pair = []
            for k in (0, 1):
                lengths = {e: (2 * j + 1 if e in O else 2 * i) for e in incs}
                lengths[estar] = 2 * k + 2
                inst = with_chains(G, lengths, H, e0)
                # the first atom on estar is tagged ('atom', li, repr(p), 0); delete its copy of the line Ldel
                tag = ('atom', estar[0], repr(estar[1]), 0)
                pos = [m for m, l in enumerate(inst) if all(isinstance(q, tuple) and q[:1] == (tag,) for q in l) and
                       sorted(q[1] for q in l) == sorted(H[Ldel])]
                assert len(pos) == 1, pos
                inst = remove_line(inst, pos[0])
                biggest = max(biggest, len(inst))
                m = oracle(inst, lam0)
                normal = sum(lengths.values()) - 1
                K = cmul(cmul(norm0, cpow(s, normal)), s2)
                pair.append(cdiv(m, K))
            # pair[k] = Q0(a, b) + rho^(2k+1) rho2 Q1(a, b)
            c0, c1 = cmul(rho, rho2), cmul(cpow(rho, 3), rho2)
            Q1 = cdiv(csub(pair[1], pair[0]), csub(c1, c0))
            Q0 = csub(pair[0], cmul(c0, Q1))
            vals[(i, j)] = cadd(Q0, cmul(cpow(rho, 2 * i), Q1))           # estar weighted like the other incidences off O
    a_nodes = [cpow(rho, 2 * i) for i in range(Da + 1)]
    b_nodes = [cpow(rho, 2 * j) for j in range(Db + 1)]
    rows = {i: newton_interpolate(b_nodes, [vals[(i, j)] for j in range(Db + 1)]) for i in range(Da + 1)}
    target = ZERO
    w = cdiv(C(-1), cmul(C(3), u0))
    for sdeg in range(Db + 1):
        col = newton_interpolate(a_nodes, [rows[i][sdeg] for i in range(Da + 1)])
        for r in range(Da + 1):
            if (r + sdeg) % 2 == 0:
                target = cadd(target, cmul(cmul(col[r], cpow(rho, -sdeg)), cpow(w, (r + sdeg) // 2)))
    return cmul(cmul(cpow(C(2), n), cpow(cdiv(C(3), C(4)), n)), target), 2 * (Da + 1) * (Db + 1), biggest, rho2


# ------------------------------------------------------------------------------------------------ the tractable couplings
def quad_exp_sum(n, const, lin, quad):
    """sum over x in GF(2)^n of (-1)^Q(x), Q = const + sum lin[i] x_i + sum_{(i,j) in quad} x_i x_j, in polynomial time
    (eliminate a variable: if it has no quadratic partner it contributes 2 or kills the sum; otherwise summing it out forces a linear
    relation, which is substituted)"""
    lin = {i: lin.get(i, 0) % 2 for i in range(n)}
    quad = {frozenset(e) for e in quad if len(set(e)) == 2}
    const %= 2
    free = set(range(n))
    factor = 1
    while free:
        x = min(free)
        partners = {next(iter(e - {x})) for e in quad if x in e}
        if not partners:
            if lin[x]:
                return 0
            factor *= 2
            free.discard(x)
            continue
        # sum_x (-1)^{x (a + sum_{y in partners} y)} = 2 [a + sum y = 0]: substitute y0 = a + sum_{y != y0} y
        a = lin[x]
        y0 = min(partners)
        rest = partners - {y0}
        quad = {e for e in quad if x not in e}
        lin.pop(x)
        free.discard(x)
        factor *= 2
        # Q contains y0 * (lin[y0] + sum over quadratic partners z of y0): replace y0 by a + sum(rest)
        zs = {next(iter(e - {y0})) for e in quad if y0 in e}
        quad = {e for e in quad if y0 not in e}
        ly0 = lin.pop(y0)
        free.discard(y0)
        # linear part: ly0 * (a + sum rest)
        const = (const + ly0 * a) % 2
        for y in rest:
            lin[y] = (lin[y] + ly0) % 2
        # quadratic part: (a + sum rest) * z for every z in zs
        for z in zs:
            if a:
                lin[z] = (lin[z] + 1) % 2
            for y in rest:
                if y == z:
                    lin[z] = (lin[z] + 1) % 2          # y * y = y
                else:
                    quad ^= {frozenset((y, z))}
    return factor * (-1) ** const


def M_at_minus_one(lines, neg=frozenset()):
    """M(H, sigma; -1) as a quadratic exponential sum: [line monochromatic] = 1 + e1 + e2 of its three signed bits (mod 2)"""
    pts = sorted({p for l in lines for p in l}, key=repr)
    idx = {p: k for k, p in enumerate(pts)}
    const, lin, quad = 0, {}, set()
    for i, l in enumerate(lines):
        bits = [(idx[p], int((i, p) in neg)) for p in l]
        # 1 + sum b + sum_{a<b} b_a b_b, with b = x + s
        const += 1
        for v, s in bits:
            const += s
            lin[v] = lin.get(v, 0) + 1
        for (v, s), (w, t) in itertools.combinations(bits, 2):
            # (x_v + s)(x_w + t) = x_v x_w + t x_v + s x_w + s t
            quad ^= {frozenset((v, w))}
            lin[v] = lin.get(v, 0) + t
            lin[w] = lin.get(w, 0) + s
            const += s * t
    return quad_exp_sum(len(pts), const, lin, quad)


def M_at_infinity(lines, neg=frozenset()):
    """the leading coefficient: colourings with every line monochromatic = 2^(nullity) of a GF(2) system, or 0"""
    pts = sorted({p for l in lines for p in l}, key=repr)
    idx = {p: k for k, p in enumerate(pts)}
    rows = []
    for i, l in enumerate(lines):
        for p, q in zip(l, l[1:]):
            rows.append(((1 << idx[p]) | (1 << idx[q]), int((i, p) in neg) ^ int((i, q) in neg)))
    piv = {}
    for r, b in rows:
        for c, (pr, pb) in sorted(piv.items(), reverse=True):
            if r >> c & 1:
                r ^= pr
                b ^= pb
        if r == 0:
            if b:
                return 0
            continue
        c = r.bit_length() - 1
        for c2 in list(piv):
            if piv[c2][0] >> c & 1:
                piv[c2] = (piv[c2][0] ^ r, piv[c2][1] ^ b)
        piv[c] = (r, b)
    return 2 ** (len(pts) - len(piv))


def det_exact(rows):
    """exact determinant of an integer matrix (Fraction Gaussian elimination)"""
    m = [[Fraction(v) for v in r] for r in rows]
    n = len(m)
    det = Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if m[r][c] != 0), None)
        if p is None:
            return 0
        if p != c:
            m[c], m[p] = m[p], m[c]
            det = -det
        det *= m[c][c]
        for r in range(c + 1, n):
            f = m[r][c] / m[c][c]
            if f:
                m[r] = [a - f * b for a, b in zip(m[r], m[c])]
    return det


def M_at_minus_three_knot(lines):
    """for a knot's space (plain): M(H; -3) = (-2)^n #PM = (-2)^n |det| of the incidence matrix"""
    pts = sorted({p for l in lines for p in l}, key=repr)
    idx = {p: k for k, p in enumerate(pts)}
    mat = [[0] * len(pts) for _ in lines]
    for i, l in enumerate(lines):
        for p in l:
            mat[i][idx[p]] = 1
    return (-2) ** len(pts) * abs(det_exact(mat))
