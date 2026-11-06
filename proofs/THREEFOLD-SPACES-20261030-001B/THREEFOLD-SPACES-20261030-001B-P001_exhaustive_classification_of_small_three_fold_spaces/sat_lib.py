"""SAT encodings for minimally non-2-colourable cubic triple systems (THREEFOLD-SPACES-20261030-001B).

Variables x(l, p): point p lies on line l (n lines, n points).  Constraints:
- every line has three points and every point is on three lines (sequential-counter cardinality encodings);
- WLOG line 0 = {0, 1, 2} and point 0 lies on lines 0, 1, 2 (relabelling);
- not 2-colourable: for every colouring with point 0 coloured 0, some line is monochromatic (auxiliary literals r, b per colouring and line);
- minimal: for every line l a witness colouring y(l, .) under which every other line is proper (this forces connectivity);
- optionally a twist: point 0 enters line 0 with its colour complemented (in both the non-colourability and the witness constraints);
- optionally lexicographic symmetry breaking: rows 1..n-1 and columns 1..n-1 in non-increasing lexicographic order (row 0, column 0 fixed).
  Sound: alternately sorting rows 1..n-1 and columns 1..n-1 never decreases the matrix read row by row, so it terminates in a matrix with
  both orders; the WLOG constraints survive because rows containing point 0 and columns on line 0 sort first."""
import itertools
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType


def build(n, twisted=False, lex=True, noncolour=True):
    pool = IDPool()
    x = lambda l, p: pool.id(('x', l, p))  # noqa: E731
    cnf = CNF()
    for l in range(n):
        cnf.extend(CardEnc.equals([x(l, p) for p in range(n)], 3, vpool=pool, encoding=EncType.seqcounter).clauses)
    for p in range(n):
        cnf.extend(CardEnc.equals([x(l, p) for l in range(n)], 3, vpool=pool, encoding=EncType.seqcounter).clauses)
    for p in (0, 1, 2):
        cnf.append([x(0, p)])
    for l in (1, 2):
        cnf.append([x(l, 0)])

    def colour_of(c, l, p):
        return 1 - c[p] if (twisted and l == 0 and p == 0) else c[p]
    for cc in (itertools.product((0, 1), repeat=n - 1) if noncolour else ()):
        c = (0,) + cc
        lits = []
        for l in range(n):
            r, b = pool.id(('r', cc, l)), pool.id(('b', cc, l))
            for p in range(n):
                if colour_of(c, l, p) == 1:
                    cnf.append([-r, -x(l, p)])
                else:
                    cnf.append([-b, -x(l, p)])
            lits += [r, b]
        cnf.append(lits)
    for l in range(n):
        for l2 in range(n):
            if l2 == l:
                continue
            us, vs = [], []
            for p in range(n):
                u, v = pool.id(('u', l, l2, p)), pool.id(('v', l, l2, p))
                y = pool.id(('y', l, p))
                flip = twisted and l2 == 0 and p == 0
                cnf.append([-u, x(l2, p)])
                cnf.append([-v, x(l2, p)])
                if not flip:
                    cnf.append([-u, y])
                    cnf.append([-v, -y])
                else:
                    cnf.append([-u, -y])
                    cnf.append([-v, y])
                us.append(u)
                vs.append(v)
            cnf.append(us)
            cnf.append(vs)
    if lex:
        for i in range(1, n - 1):
            lex_geq(cnf, pool, [x(i, p) for p in range(n)], [x(i + 1, p) for p in range(n)], ('r', i))
        for j in range(1, n - 1):
            lex_geq(cnf, pool, [x(l, j) for l in range(n)], [x(l, j + 1) for l in range(n)], ('c', j))
    return cnf, pool, x


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


def decode(model, x, n):
    m = set(v for v in model if v > 0)
    return [tuple(p for p in range(n) if x(l, p) in m) for l in range(n)]
