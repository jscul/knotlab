"""What handles cost (HANDLE-COUNT-20261106-001A).

A cubic system H is a list of lines (triples of distinct points); its incidence graph B is cubic bipartite. A signing is a set of negated
incidences (line index, point). For a coupling lam, Z(H, sign; lam) sums over point colourings the product over lines of lam if the line sees
three equal values (colour xor sign) and 1 otherwise; lam = 0 counts proper 2-colourings.

The network form used throughout: every edge of a graph is a binary variable (the colour of its point end, as that point carries it); every
vertex is a factor on its incident edges (a point: all equal; a line: the weight above, with its incidence signs; a contracted vertex: the
tensor its side computes). Graphs are edge-labelled multigraphs {vertex: [(edge id, neighbour), ...]}; edge ids are the incidences of B and
survive every contraction, so a tight cut's three edges carry the same ids on both sides.

Exact arithmetic: int, Fraction or GQ (Gaussian rationals)."""
import itertools
from collections import Counter
from fractions import Fraction

import networkx as nx

import grammar_lib as M
import seymour_lib as SL


# ------------------------------------------------------------------------------------------------ Gaussian rationals
class GQ:
    __slots__ = ("re", "im")

    def __init__(self, re, im=0):
        self.re, self.im = Fraction(re), Fraction(im)

    @staticmethod
    def of(x):
        return x if isinstance(x, GQ) else GQ(x, 0)

    def __add__(self, o):
        o = GQ.of(o)
        return GQ(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __sub__(self, o):
        o = GQ.of(o)
        return GQ(self.re - o.re, self.im - o.im)

    def __rsub__(self, o):
        return GQ.of(o) - self

    def __neg__(self):
        return GQ(-self.re, -self.im)

    def __mul__(self, o):
        o = GQ.of(o)
        return GQ(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = GQ.of(o)
        d = o.re * o.re + o.im * o.im
        return self * GQ(o.re / d, -o.im / d)

    def __eq__(self, o):
        try:
            o = GQ.of(o)
        except (TypeError, ValueError):
            return NotImplemented
        return self.re == o.re and self.im == o.im

    def __hash__(self):
        return hash((self.re, self.im))

    def __bool__(self):
        return bool(self.re) or bool(self.im)

    def __repr__(self):
        return f"({self.re}{'+' if self.im >= 0 else '-'}{abs(self.im)}i)"

    def json(self):
        return [str(self.re), str(self.im)]


def div(x, y):
    """exact quotient for int, Fraction and GQ"""
    if isinstance(x, GQ) or isinstance(y, GQ):
        return GQ.of(x) / GQ.of(y)
    q = Fraction(x) / Fraction(y)
    return int(q) if q.denominator == 1 else q


def num_json(x):
    if isinstance(x, GQ):
        return x.json()
    return str(x)


# ------------------------------------------------------------------------------------------------ factors and elimination
def weight(vals, lam):
    return lam if vals[0] == vals[1] == vals[2] else 1


def eliminate(factors, keep):
    """sum out every variable not in keep; factors are (vars tuple, dict bits -> value); returns dict over keep (in the given order)"""
    factors = [(tuple(v), dict(t)) for v, t in factors]
    keep = tuple(keep)
    allv = {x for v, t in factors for x in v} - set(keep)
    while allv:
        def width(x):
            return len({y for v, t in factors if x in v for y in v})
        x = min(allv, key=lambda y: (width(y), str(y)))
        inv = [f for f in factors if x in f[0]]
        rest = [f for f in factors if x not in f[0]]
        nv = tuple(sorted({y for v, t in inv for y in v} - {x}, key=str))
        tab = {}
        for bits in itertools.product((0, 1), repeat=len(nv)):
            a = dict(zip(nv, bits))
            tot = 0
            for b in (0, 1):
                a[x] = b
                pr = 1
                for v, t in inv:
                    val = t.get(tuple(a[y] for y in v), 0)
                    if not val:
                        pr = 0
                        break
                    pr = pr * val
                if pr:
                    tot = tot + pr
            if tot:
                tab[bits] = tot
        factors = rest + [(nv, tab)]
        allv.discard(x)
    out = {}
    for bits in itertools.product((0, 1), repeat=len(keep)):
        a = dict(zip(keep, bits))
        pr = 1
        for v, t in factors:
            val = t.get(tuple(a[y] for y in v), 0)
            if not val:
                pr = 0
                break
            pr = pr * val
        if pr:
            out[bits] = pr
    return out


def direct_count(H, sign, lam):
    """Z(H, sign; lam) by elimination over the point colours (independent of the network form)"""
    sign = set(map(tuple, sign))
    factors = []
    for i, l in enumerate(H):
        vs = tuple(sorted(set(l)))
        tab = {}
        for bits in itertools.product((0, 1), repeat=len(vs)):
            x = dict(zip(vs, bits))
            w = weight([x[p] ^ (1 if (i, p) in sign else 0) for p in l], lam)
            if w:
                tab[bits] = w
        factors.append((vs, tab))
    return eliminate(factors, ()).get((), 0)


# ------------------------------------------------------------------------------------------------ labelled graphs and tight cuts
def labelled(H):
    """B(H) as {vertex: [(edge id, neighbour)]}; edge id = (line, point, copy)"""
    g = {}
    for i, l in enumerate(H):
        g.setdefault(('L', i), [])
        for c, (p, k) in enumerate(Counter(l).items()):
            for j in range(k):
                e = (i, p, j)
                g[('L', i)].append((e, ('P', p)))
                g.setdefault(('P', p), []).append((e, ('L', i)))
    return g


def counter_view(g):
    return {v: Counter(w for e, w in nb) for v, nb in g.items()}


def contract_labelled(g, X, name):
    out = {}
    for v, nb in g.items():
        if v in X:
            continue
        out[v] = [(e, name if w in X else w) for e, w in nb]
    out[name] = [(e, w) for v in X for e, w in g[v] if w not in X]
    return out


def decompose(g, counter=None):
    """tight-cut decomposition of a labelled cubic bipartite multigraph: list of braces, contracted vertices ('X', kind, k); the brace
    containing ('X', ., k) and the one containing its partner share the cut's three edge ids"""
    if counter is None:
        counter = [0]
    X = M.find_tight_cut(counter_view(g))
    if X is None:
        return [g]
    pts = sum(1 for v in X if M.kind(v) == 'P')
    maj = 'P' if pts > len(X) - pts else 'L'
    k = counter[0]
    counter[0] += 1
    rest = set(g) - set(X)
    a1 = contract_labelled(g, X, ('X', maj, k))
    a2 = contract_labelled(g, rest, ('X', 'L' if maj == 'P' else 'P', k))
    return decompose(a1, counter) + decompose(a2, counter)


def brace_kind(g):
    if len(g) == 2:
        return 'theta'
    return M.brace_type(counter_view(g))[0]


def simple_graph(g):
    return nx.Graph([(v, w) for v, nb in g.items() for e, w in nb])


def brace_tree(braces):
    """{k: (index of the brace holding ('X', ., k) on one side, index on the other side)}"""
    where = {}
    for i, b in enumerate(braces):
        for v in b:
            if v[0] == 'X':
                where.setdefault(v[2], []).append((i, v))
    return where


# ------------------------------------------------------------------------------------------------ vertex factors
def vertex_factor(g, v, sign, lam, tensors):
    """factor of vertex v of the labelled brace g on its incident edge ids (in adjacency order)"""
    edges = tuple(e for e, w in g[v])
    if v[0] == 'X':
        order, tab = tensors[v]                 # the tensor carries its own edge order (the child brace's)
        assert set(order) == set(edges)
        return order, tab
    if M.kind(v) == 'P':
        return edges, {(0,) * len(edges): 1, (1,) * len(edges): 1}
    tab = {}
    s = [1 if (v[1], e[1]) in sign else 0 for e in edges]
    for bits in itertools.product((0, 1), repeat=len(edges)):
        w = weight([b ^ t for b, t in zip(bits, s)], lam)
        if w:
            tab[bits] = w
    return edges, tab


def brace_factors(g, sign, lam, tensors, skip=()):
    return [vertex_factor(g, v, sign, lam, tensors) for v in g if v not in skip]


# ------------------------------------------------------------------------------------------------ the Hadamard basis
def hadamard(tab, n):
    """y-basis coefficients: sum over x of f(x) (-1)^(x.y), as a dict over all y"""
    out = {}
    for y in itertools.product((0, 1), repeat=n):
        tot = 0
        for x, val in tab.items():
            tot = tot + (val if sum(a * b for a, b in zip(x, y)) % 2 == 0 else -val)
        out[y] = tot
    return out


def is_even(hat):
    return all(not v for y, v in hat.items() if sum(y) % 2)


def mgi(hat):
    f = lambda *y: hat.get(tuple(y), 0)  # noqa: E731
    return f(0, 0, 0, 0) * f(1, 1, 1, 1) - f(1, 1, 0, 0) * f(0, 0, 1, 1) + f(1, 0, 1, 0) * f(0, 1, 0, 1) - f(1, 0, 0, 1) * f(0, 1, 1, 0)


PAIRS = [((0, 0, 0, 0), (1, 1, 1, 1), 1), ((1, 1, 0, 0), (0, 0, 1, 1), -1), ((1, 0, 1, 0), (0, 1, 0, 1), 1), ((1, 0, 0, 1), (0, 1, 1, 0), -1)]


def split_hat(hat):
    """two matchgate signatures summing to an even 4-ary hat: (M, C) with MGI(M) = 0 and C supported on one entry (Lemma 3)"""
    if not mgi(hat):
        return dict(hat), {}
    for z, zb, sgn in PAIRS:
        for a, b in ((z, zb), (zb, z)):
            if hat.get(a, 0):
                Mh = dict(hat)
                # MGI is linear in Mh[b] with coefficient sgn * hat[a]; solve for the value making it vanish
                Mh[b] = 0
                rest = mgi(Mh)
                Mh[b] = div(-rest, sgn * hat[a])
                C = {b: hat.get(b, 0) - Mh[b]}
                return Mh, C
    raise ValueError("an even 4-ary tensor with no nonzero entry has MGI 0")


def unhadamard(hat, n):
    """inverse transform back to a table over x (exact; divides by 2^n)"""
    tab = {}
    for x in itertools.product((0, 1), repeat=n):
        tot = 0
        for y, val in hat.items():
            tot = tot + (val if sum(a * b for a, b in zip(x, y)) % 2 == 0 else -val)
        if tot:
            tab[x] = div(tot, 2 ** n)
    return tab


# ------------------------------------------------------------------------------------------------ trisum evaluation of one brace
_TREES = {}


def trisum_tree_of(g):
    """the trisum tree of a labelled brace (seymour_lib), cached by the brace's edge set"""
    sg = simple_graph(g)
    key = frozenset(frozenset(e) for e in sg.edges())
    if key not in _TREES:
        _TREES[key] = SL.trisum_tree(sg, {v for v in sg if M.kind(v) == 'L'})
    return _TREES[key]


def trisum_eval(g, factor_of, expand=True, root=0, tree=None):
    """value of the closed network of a non-planar Pfaffian brace g (labelled, simple) through its Robertson-Seymour-Thomas trisum tree.
    factor_of(v) -> (edge ids, table). Each junction is formed from its two closed branches; when its Hadamard tensor violates the
    matchgate identity it is split into two matchgate terms and the host is evaluated on each (if expand). Returns (value, records):
    records per piece: (piece index, number of hosted junctions, number of them violating MGI, number of evaluations)."""
    if tree is None:
        tree = trisum_tree_of(g)
    leaves, squares = tree
    at = {S: [i for i, (h, s) in enumerate(leaves) if S in s] for S in squares}
    own = []
    for h, sqs in leaves:
        sv = {v for S in sqs for v in S}
        own.append([v for v in h if v not in sv])
    # the edge from square vertex d into piece i: the edge of g from d to its one neighbour in piece i outside the square (an own vertex
    # of the piece, or a vertex of another square of the piece)
    def leg(S, t, i):
        d = S[t]
        h = leaves[i][0]
        nb = [w for w in h[d] if w not in S]
        assert len(nb) == 1, (S, t, i, nb)
        es = [e for e, w in g[d] if w == nb[0]]
        assert len(es) == 1, (S, t, i, es)
        return es[0]
    records = []
    junction_mgi = {}

    def piece_value(i, parent):
        """factors of piece i (own vertices) and the junction tensors of its child squares; returns (open legs, table)"""
        h, sqs = leaves[i]
        fac = [factor_of(v) for v in own[i]]
        children = [D for D in sqs if D != parent]
        juncs = []
        for D in children:
            q, r = [l for l in at[D] if l != i]
            FQ, FR = branch(q, D), branch(r, D)
            hl = tuple(leg(D, t, i) for t in range(4))
            ql = tuple(leg(D, t, q) for t in range(4))
            rl = tuple(leg(D, t, r) for t in range(4))
            jf = [(ql, FQ), (rl, FR)] + [factor_of(D[t]) for t in range(4)]
            W = eliminate(jf, hl)
            junction_mgi[D] = mgi(hadamard(W, 4))
            juncs.append((hl, W))
        return fac, juncs

    def host_eval(fac, juncs, keep):
        """evaluate a host with its junctions, splitting the ones that violate MGI; returns (table over keep, #violating, #evaluations)"""
        parts = []
        bad = 0
        for hl, W in juncs:
            hat = hadamard(W, 4)
            assert is_even(hat)
            if mgi(hat) and expand:
                Mh, Ch = split_hat(hat)
                assert not mgi(Mh) and not mgi(Ch)
                parts.append([(hl, unhadamard(Mh, 4)), (hl, unhadamard(Ch, 4))])
                bad += 1
            else:
                bad += 1 if mgi(hat) else 0
                parts.append([(hl, W)])
        total, nev = {}, 0
        for choice in itertools.product(*parts):
            t = eliminate(fac + list(choice), keep)
            nev += 1
            for k, val in t.items():
                total[k] = total.get(k, 0) + val
        return {k: v for k, v in total.items() if v}, bad, nev

    memo = {}

    def branch(i, S):
        if (i, S) in memo:
            return memo[(i, S)]
        fac, juncs = piece_value(i, S)
        keep = tuple(leg(S, t, i) for t in range(4))
        tab, bad, nev = host_eval(fac, juncs, keep)
        records.append((i, len(juncs), bad, nev))
        memo[(i, S)] = tab
        return tab

    fac, juncs = piece_value(root, None)
    tab, bad, nev = host_eval(fac, juncs, ())
    records.append((root, len(juncs), bad, nev))
    trisum_eval.last_junction_mgi = junction_mgi
    return tab.get((), 0), records, len(squares), len(leaves)


# ------------------------------------------------------------------------------------------------ the whole count through braces
def count_by_braces(H, sign, lam, use_trisum=True, expand=True):
    """Z(H, sign; lam) through the tight-cut decomposition: braces evaluated leaf to root, each contracted side acting through its
    3-ary tensor; non-planar non-Heawood braces through their trisum trees. Returns (value, report)."""
    sign = set(map(tuple, sign))
    braces = decompose(labelled(H))
    kinds = [brace_kind(b) for b in braces]
    where = brace_tree(braces)
    adj = {i: [] for i in range(len(braces))}
    for k, lst in where.items():
        (i, vi), (j, vj) = lst
        adj[i].append((j, k, vi, vj))
        adj[j].append((i, k, vj, vi))
    report = {"braces": Counter(kinds), "junctions": [], "trisum records": [], "ternary tensors even": True}
    tensors = {}

    def value(i, parent):
        """table of brace i over the edges of its parent contracted vertex (or scalar at the root)"""
        b = braces[i]
        for j, k, vi, vj in adj[i]:
            if parent is not None and j == parent[0] and k == parent[1]:
                continue
            tensors[vi] = value(j, (i, k))
            hat = hadamard(tensors[vi][1], 3)
            report["ternary tensors even"] &= is_even(hat)
        pv = None
        if parent is not None:
            pv = next(vi for j, k, vi, vj in adj[i] if j == parent[0] and k == parent[1])
        keep = tuple(e for e, w in b[pv]) if pv is not None else ()
        if use_trisum and kinds[i] == 'other':
            # the parent's three legs are read in the Hadamard basis: the parent vertex is replaced by the character chi_y of an even
            # pattern y (an even signature), so every junction stays even; the table is recovered by the inverse transform
            hat = {}
            ys = [y for y in itertools.product((0, 1), repeat=len(keep)) if sum(y) % 2 == 0] if keep else [()]
            for y in ys:
                def factor_of(v, y=y):
                    if v == pv:
                        return keep, {x: (1 if sum(a * c for a, c in zip(x, y)) % 2 == 0 else -1)
                                      for x in itertools.product((0, 1), repeat=len(keep))}
                    return vertex_factor(b, v, sign, lam, tensors)
                val, recs, nsq, npieces = trisum_eval(b, factor_of, expand=expand)
                hat[y] = val
                report["trisum records"].append(recs)
            report["junctions"].append(nsq)
            if not keep:
                return keep, ({(): hat[()]} if hat[()] else {})
            return keep, unhadamard(hat, len(keep))
        fac = brace_factors(b, sign, lam, tensors, skip=(pv,) if pv is not None else ())
        return keep, eliminate(fac, keep)
    keep, tab = value(0, None)
    return tab.get((), 0), report


def structure(H):
    """(atoms, planar braces, trisum braces' junction counts, brace kinds) of the tight-cut decomposition of B(H)"""
    braces = decompose(labelled(H))
    kinds = Counter()
    js = []
    for b in braces:
        t = brace_kind(b)
        kinds[t] += 1
        if t == 'other':
            leaves, squares = trisum_tree_of(b)
            js.append(len(squares))
    return kinds.get('heawood', 0), kinds.get('planar', 0), js, kinds
