"""Counting under branched twists is #P-hard (SOFT-CROSS-20261031-001B).

From a positive NAE-3SAT formula (clauses = triples of variables, repetitions allowed) build unsigned cubic bipartite graphs G_k:
  - a copy point for every occurrence; a clause line on the clause's three copies;
  - the copies of a variable on a cycle, consecutive copies joined by a merge path q - l1 - p1 - ... - p_(k-1) - lk - q' (k lines);
  - the pair (l_t, p_t) of a path closed by a dead cap (the cube minus an edge, cross_lib); the last line l_k's spare leg to an absorber:
    a dummy point with three caps, one per path (the number of paths is 3 times the number of clauses).
Each merge path acts by (3M)^k with M = [[1, 2], [2, 1]] = 3 P+ - P-; interpolation over k replaces it by the identity (an equality)."""
import itertools
import cross_lib as X


def merge_path(B, a, b, k, tag):
    """the path a - l_1 - p_1 - ... - p_(k-1) - l_k - b between two points, each pair (l_t, p_t) closed by a cap; returns l_k, whose spare
    leg is left open"""
    prev = a
    for t in range(k):
        li = ('ln', 'M', tag, t)
        B.edge(prev, li)
        if t < k - 1:
            pi = ('pt', 'M', tag, t)
            B.edge(li, pi)
            B.cap(('M', tag, t), li, pi)
            prev = pi
        else:
            B.edge(li, b)
    return li


def absorber(B, lines, tag, capped=True):
    """a dummy point closing the spare legs of three lines, through one cap each (capped) or directly (control)"""
    delta = ('pt', 'absorber', tag)
    for j, li in enumerate(lines):
        if capped:
            B.cap(('A', tag, j), li, delta)
        else:
            B.edge(li, delta)
    return delta


def build(formula, k, capped=True):
    """the graph G_k for a formula given as a list of variable triples"""
    assert k >= 2
    B = X.Builder()
    occ = {}
    for ci, clause in enumerate(formula):
        line = ('ln', 'C', ci)
        for pos, var in enumerate(clause):
            q = ('pt', 'q', ci, pos)
            B.edge(q, line)
            occ.setdefault(var, []).append(q)
    last_lines = []
    for var, copies in sorted(occ.items(), key=str):
        d = len(copies)
        for i in range(d):
            last_lines.append(merge_path(B, copies[i], copies[(i + 1) % d], k, (var, i)))
    assert len(last_lines) % 3 == 0
    for g in range(0, len(last_lines), 3):
        absorber(B, last_lines[g:g + 3], g, capped)
    return B


def lines(B):
    """(lines as tuples of point indices, point index) for amplitude_lib.count, without requiring degree 3 (gadgets with open legs)"""
    pts = sorted((v for v in B.g if X.is_point(v)), key=str)
    lns = sorted((v for v in B.g if not X.is_point(v)), key=str)
    pid = {v: i for i, v in enumerate(pts)}
    return [tuple(sorted(pid[w] for w in B.g[l])) for l in lns], pid


def count_formula(formula):
    """#solutions of the positive NAE-3SAT formula, by brute force"""
    vs = sorted({v for c in formula for v in c}, key=str)
    tot = 0
    for bits in itertools.product((0, 1), repeat=len(vs)):
        x = dict(zip(vs, bits))
        tot += all(len({x[v] for v in c}) == 2 for c in formula)
    return tot


def path_polynomial(formula):
    """p(t) = sum over colourings x of the copies, NAE on every clause, of prod over merge paths (q, q') of (1 + t (-1)^(x_q + x_q')) / 2,
    computed from the formula alone (sympy polynomial in t); p(1) = #formula"""
    import sympy as sp
    t = sp.Symbol('t')
    occ = {}
    for ci, clause in enumerate(formula):
        for pos, var in enumerate(clause):
            occ.setdefault(var, []).append((ci, pos))
    paths = [(c[i], c[(i + 1) % len(c)]) for var, c in sorted(occ.items(), key=str) for i in range(len(c))]
    D = len(paths)
    hist = {}
    copies = [(ci, pos) for ci in range(len(formula)) for pos in range(3)]
    for bits in itertools.product((0, 1), repeat=len(copies)):
        x = dict(zip(copies, bits))
        if all(len({x[(ci, pos)] for pos in range(3)}) == 2 for ci in range(len(formula))):
            d = sum(x[a] != x[b] for a, b in paths)
            hist[d] = hist.get(d, 0) + 1
    p = sum(n * (1 + t) ** (D - d) * (1 - t) ** d for d, n in hist.items()) / sp.Integer(2) ** D
    return sp.Poly(sp.expand(p), t), t


def recover(formula, counts):
    """solve #col(G_k) = 2^(D/3) 9^(k D) sum_j c_j (-1/3)^(k j) for the c_j (exact), and return sum_j c_j"""
    import sympy as sp
    D = 3 * len(formula)
    ks = sorted(counts)
    assert len(ks) >= D + 1
    rows = [[sp.Rational(-1, 3) ** (k * j) for j in range(D + 1)] for k in ks[:D + 1]]
    rhs = [sp.Rational(counts[k], 2 ** (D // 3) * 9 ** (k * D)) for k in ks[:D + 1]]
    c = sp.Matrix(rows).LUsolve(sp.Matrix(rhs))
    return sum(c), c
