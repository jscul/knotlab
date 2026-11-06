"""SAT census of connected cubic multi-systems that are not 2-colourable (THREEFOLD-GRAMMAR-20261030-001B).

A multi-system has n points and n lines; line l contains point p with multiplicity m(l, p) in {0, 1, 2, 3}, every line has three
incidences and every point three.  A line is properly coloured when its points (counted once) carry both colours.  A twist at the
incidence (line 0, point 0), of multiplicity one, complements point 0's colour on line 0.

Variables y(k, l, p) mean m(l, p) >= k (k = 1, 2, 3, so y3 -> y2 -> y1).  Constraints:
- cardinality: every row and every column of m sums to 3 (sequential counters over the y variables);
- WLOG point 0 lies on line 0 (relabelling); with a twist, that incidence has multiplicity one and carries the twist;
- not 2-colourable: for every colouring with point 0 coloured 0, some line is monochromatic (support y1);
- minimal: for every line a witness colouring under which every other line is proper.  Minimality forces connectivity; conversely a
  connected multi-system without a triple incidence that is not 2-colourable is minimal (Seymour 1974 plus regularity, see proof.md);
- lexicographic symmetry breaking: rows 1..n-1 and columns 1..n-1 in non-increasing lexicographic order, each row (column) read as the
  thermometer codes (y1, y2, y3) of its entries, so that the order on entries is the order on multiplicities.  Sound: alternately
  sorting rows 1..n-1 and columns 1..n-1 never decreases the matrix read row by row, so it ends in a doubly sorted matrix, and row 0 and
  column 0 (with point 0 on line 0 and the twist) are never moved."""
import itertools
import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def build(n, twisted=False, lex=True):
    pool = IDPool()
    y = lambda k, l, p: pool.id(('y', k, l, p))  # noqa: E731
    cnf = CNF()
    for l in range(n):
        for p in range(n):
            cnf.append([-y(2, l, p), y(1, l, p)])
            cnf.append([-y(3, l, p), y(2, l, p)])
    for l in range(n):
        cnf.extend(CardEnc.equals([y(k, l, p) for p in range(n) for k in (1, 2, 3)], 3, vpool=pool, encoding=EncType.seqcounter).clauses)
    for p in range(n):
        cnf.extend(CardEnc.equals([y(k, l, p) for l in range(n) for k in (1, 2, 3)], 3, vpool=pool, encoding=EncType.seqcounter).clauses)
    cnf.append([y(1, 0, 0)])
    if twisted:
        cnf.append([-y(2, 0, 0)])

    def colour_of(c, l, p):
        return 1 - c[p] if (twisted and l == 0 and p == 0) else c[p]
    for cc in itertools.product((0, 1), repeat=n - 1):
        c = (0,) + cc
        lits = []
        for l in range(n):
            r, b = pool.id(('r', cc, l)), pool.id(('b', cc, l))
            for p in range(n):
                cnf.append([-r if colour_of(c, l, p) == 1 else -b, -y(1, l, p)])
            lits += [r, b]
        cnf.append(lits)
    for l in range(n):
        for l2 in range(n):
            if l2 == l:
                continue
            us, vs = [], []
            for p in range(n):
                u, v, w = pool.id(('u', l, l2, p)), pool.id(('v', l, l2, p)), pool.id(('w', l, p))
                flip = twisted and l2 == 0 and p == 0
                cnf.append([-u, y(1, l2, p)])
                cnf.append([-v, y(1, l2, p)])
                cnf.append([-u, -w if flip else w])
                cnf.append([-v, w if flip else -w])
                us.append(u)
                vs.append(v)
            cnf.append(us)
            cnf.append(vs)
    if lex:
        for i in range(1, n - 1):
            lex_geq(cnf, pool, [y(k, i, p) for p in range(n) for k in (1, 2, 3)], [y(k, i + 1, p) for p in range(n) for k in (1, 2, 3)], ('r', i))
        for j in range(1, n - 1):
            lex_geq(cnf, pool, [y(k, l, j) for l in range(n) for k in (1, 2, 3)], [y(k, l, j + 1) for l in range(n) for k in (1, 2, 3)], ('c', j))
    return cnf, pool, y


def lex_geq(cnf, pool, a, b, tag):
    """a >=_lex b (true > false) for lists of literals"""
    e_prev = None
    for j, (aj, bj) in enumerate(zip(a, b)):
        cond = [] if e_prev is None else [-e_prev]
        cnf.append(cond + [aj, -bj])
        e = pool.id(('lex', tag, j))
        if e_prev is not None:
            cnf.append([-e, e_prev])
        cnf.append([-e, -aj, bj])
        cnf.append([-e, aj, -bj])
        cnf.append(cond + [aj, bj, e])
        cnf.append(cond + [-aj, -bj, e])
        e_prev = e


def decode(model, y, n):
    m = set(v for v in model if v > 0)
    return [tuple(p for p in range(n) for k in (1, 2, 3) if y(k, l, p) in m) for l in range(n)]


def graph(H, twisted=False):
    """incidence graph with multiplicities as edge attributes and the twist marked (twisted: True for the incidence (line 0, point 0),
    or a pair (line index, point))"""
    tw = (0, 0) if twisted is True else (twisted or None)
    g = nx.Graph()
    for i, l in enumerate(H):
        g.add_node(('L', i), kind='L')
        for p in set(l):
            g.add_node(('P', p), kind='P')
            g.add_edge(('L', i), ('P', p), m=l.count(p), tw=tw == (i, p))
    return g


def _nm(a, b):
    return a['kind'] == b['kind']


def _em(a, b):
    return a['m'] == b['m'] and a['tw'] == b['tw']


def census(n, twisted=False, lex=True, solver='cadical153'):
    """all symmetry-broken solutions, grouped into isomorphism classes (twist marked): list of [representative, number of solutions]"""
    cnf, pool, y = build(n, twisted, lex)
    classes = []
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        while s.solve():
            model = s.get_model()
            H = decode(model, y, n)
            g = graph(H, twisted)
            for c in classes:
                if nx.is_isomorphic(g, c[2], node_match=_nm, edge_match=_em):
                    c[1] += 1
                    break
            else:
                classes.append([H, 1, g])
            m = set(v for v in model if v > 0)
            s.add_clause([-y(k, l, p) if y(k, l, p) in m else y(k, l, p) for l in range(n) for p in range(n) for k in (1, 2, 3)])
    return [[H, c] for H, c, g in classes]


def colourable(H, twist=False):
    """brute force: some colouring makes every line proper (the twist complements point 0 on line 0)"""
    n = 1 + max(p for l in H for p in l)
    for bits in range(1 << (n - 1)):
        c = [0] + [(bits >> i) & 1 for i in range(n - 1)]
        if all(len({(1 - c[p]) if (twist and i == 0 and p == 0) else c[p] for p in l}) == 2 for i, l in enumerate(H)):
            return True
    return False


def simple(H):
    return all(len(set(l)) == 3 for l in H)


# ------------------------------------------------------------------------------------------------ decoration by Fano pieces
FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def repeated_classes(H):
    """(line, point) pairs of multiplicity at least two"""
    return [(i, p) for i, l in enumerate(H) for p in sorted(set(l)) if l.count(p) >= 2]


def decorate_pieces(H, points, lines, twist=None):
    """replace the points in `points` by Fano blocks (Fano minus the line (0, 1, 2), attached at 0, 1, 2) and the lines in `lines` by
    dual blocks (Fano minus the point 0; the three lines through 0 take the replaced line's three points, one each); returns a system
    on integer labels, and with twist = (line, point) of multiplicity one also the position of that incidence afterwards"""
    lines_ = [list(l) for l in H]
    mark = None if twist is None else [twist[0], H[twist[0]].index(twist[1])]     # (line, position) of the twisted incidence
    for p in points:
        k = 0
        for l in lines_:
            for j, q in enumerate(l):
                if q == p:
                    l[j] = ('b', p, k)
                    k += 1
        assert k == 3
        lines_ += [[('b', p, q) for q in fl] for fl in FANO[1:]]
    out = []
    for i, l in enumerate(lines_):
        if i in lines:
            through0 = [fl for fl in FANO if 0 in fl]
            for j, (slot, fl) in enumerate(zip(l, through0)):
                if mark is not None and mark[0] == i and mark[1] == j:
                    newmark = (len(out), slot)
                out.append([('d', i, q) for q in fl if q != 0] + [slot])
            out += [[('d', i, q) for q in fl] for fl in FANO if 0 not in fl]
        else:
            if mark is not None and mark[0] == i:
                newmark = (len(out), l[mark[1]])
            out.append(l)
    pts = sorted({x for l in out for x in l}, key=lambda x: (isinstance(x, tuple), str(x)))
    pid = {x: k for k, x in enumerate(pts)}
    D = [tuple(sorted(pid[x] for x in l)) for l in out]
    return D if twist is None else (D, (newmark[0], pid[newmark[1]]))


def covers(H, L, forbid=()):
    """all sets S of L elements (points ('P', p) and lines ('L', i)), none in forbid, meeting every repeated class"""
    reps = repeated_classes(H)
    n = len(H)
    elems = [e for e in [('P', p) for p in range(n)] + [('L', i) for i in range(n)] if e not in forbid]
    for S in itertools.combinations(elems, L):
        Sset = set(S)
        if all(('P', p) in Sset or ('L', i) in Sset for i, p in reps):
            yield S


def classify(systems, twists=None):
    """isomorphism classes of simple systems (incidence graphs, points and lines kept apart; twists: one marked incidence per system)"""
    reps = []
    for k, H in enumerate(systems):
        g = graph(H, None if twists is None else twists[k])
        for r in reps:
            if nx.is_isomorphic(g, r[1], node_match=_nm, edge_match=_em):
                r[2] += 1
                break
        else:
            reps.append([H, g, 1, None if twists is None else twists[k]])
    return [(H, c, t) for H, g, c, t in reps]
