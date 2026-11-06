"""Five knots and the pinning theorem (PINNING-20261031-001A): shared library.

A relation is a frozenset of states in {0,1}^3. A signed law is the orbit of a relation under flips and permutations of the three places;
a cubic system over a law is a set of lines, each an ordered triple of distinct points carrying a relation of the law, with every point on
exactly three lines. A piece (gadget) has internal points (three incidences) and three ports a, b, c (one incidence each); it accepts a port
assignment when some internal assignment satisfies every line."""
import itertools

CUBE = tuple(itertools.product((0, 1), repeat=3))
PAIRS = ((0, 1), (0, 2), (1, 2))


def flip(R, f):
    return frozenset(tuple(s[i] ^ f[i] for i in range(3)) for s in R)


def permute(R, perm):
    return frozenset(tuple(s[perm[i]] for i in range(3)) for s in R)


def orbit(R):
    return {flip(permute(R, perm), f) for perm in itertools.permutations(range(3)) for f in CUBE}


def canonical(R):
    return min(orbit(R), key=lambda S: (len(S), sorted(S)))


def is_knot(R):
    """K1-K3 on three places: not everything allowed, something allowed, every two-place projection full"""
    R = frozenset(R)
    return 0 < len(R) < 8 and all({(s[i], s[j]) for s in R} == {(0, 0), (0, 1), (1, 0), (1, 1)} for i, j in PAIRS)


def all_knots():
    return [frozenset(R) for r in range(1, 8) for R in itertools.combinations(CUBE, r) if is_knot(R)]


NAMES = {}


def name_of(R):
    c = canonical(R)
    sizes = {4: "parity", 5: "Fibonacci (no-lone)", 7: "clause"}
    if len(c) == 6:
        return "not-all-equal" if all(flip(c, (1, 1, 1)) == c for _ in [0]) and complement_invariant(c) else "x or (y != z)"
    return sizes[len(c)]


def complement_invariant(R):
    return flip(R, (1, 1, 1)) == frozenset(R)


# ------------------------------------------------------------------------------------------------ Schaefer classes
def closed_under(R, op):
    return all(tuple(op(a[i], b[i], c[i]) for i in range(3)) in R for a in R for b in R for c in R)


SCHAEFER = {
    "0-valid": lambda R: (0, 0, 0) in R,
    "1-valid": lambda R: (1, 1, 1) in R,
    "Horn (closed under and)": lambda R: closed_under(R, lambda a, b, c: a & b),
    "dual-Horn (closed under or)": lambda R: closed_under(R, lambda a, b, c: a | b),
    "bijunctive (closed under majority)": lambda R: closed_under(R, lambda a, b, c: (a & b) | (a & c) | (b & c)),
    "affine (closed under a+b+c)": lambda R: closed_under(R, lambda a, b, c: a ^ b ^ c),
}


def schaefer_classes(language):
    return [name for name, test in SCHAEFER.items() if all(test(R) for R in language)]


# ------------------------------------------------------------------------------------------------ pieces
def structures(k, simple=True):
    """k internal points (three incidences) and ports a, b, c (one incidence) in k + 1 lines of three distinct points"""
    pts = list(range(k)) + ['a', 'b', 'c']
    need = {p: (3 if isinstance(p, int) else 1) for p in pts}
    triples = list(itertools.combinations(pts, 3))
    out = []

    def rec(start, chosen, deg):
        if len(chosen) == k + 1:
            if all(deg[p] == need[p] for p in pts):
                out.append(list(chosen))
            return
        for t in range(start, len(triples)):
            tri = triples[t]
            if any(deg[p] + 1 > need[p] for p in tri):
                continue
            for p in tri:
                deg[p] += 1
            chosen.append(tri)
            rec(t + 1 if simple else t, chosen, deg)
            chosen.pop()
            for p in tri:
                deg[p] -= 1
    rec(0, [], {p: 0 for p in pts})
    return out


def accepted(lines, rels, k):
    """the accepted port set of a piece (lines over internal points 0..k-1 and ports 'a','b','c'; rels[i] the relation of line i)"""
    acc = set()
    for ports in CUBE:
        for inner in itertools.product((0, 1), repeat=k):
            val = dict(zip(('a', 'b', 'c'), ports))
            val.update(enumerate(inner))
            if all(tuple(val[p] for p in l) in R for l, R in zip(lines, rels)):
                acc.add(ports)
                break
    return frozenset(acc)


def find_piece(variants, target, kmax=4):
    """the first simple piece whose accepted set satisfies target(acc); lines may carry any relation in variants"""
    variants = sorted(variants, key=sorted)
    for k in range(2, kmax + 1):
        for lines in structures(k):
            pts = list(range(k)) + ['a', 'b', 'c']
            idx = {p: i for i, p in enumerate(pts)}
            N = 1 << (k + 3)
            masks = []
            for l in lines:
                per = []
                for V in variants:
                    m = 0
                    for x in range(N):
                        if tuple((x >> idx[p]) & 1 for p in l) in V:
                            m |= 1 << x
                    per.append(m)
                masks.append(per)
            port_masks = {}
            for ports in CUBE:
                m = 0
                for x in range(N):
                    if all(((x >> idx[q]) & 1) == v for q, v in zip(('a', 'b', 'c'), ports)):
                        m |= 1 << x
                port_masks[ports] = m
            for choice in itertools.product(range(len(variants)), repeat=len(lines)):
                m = -1
                for li, vi in enumerate(choice):
                    m &= masks[li][vi]
                    if not m:
                        break
                acc = frozenset(pt for pt, pm in port_masks.items() if m & pm)
                if target(acc):
                    return {"k": k, "lines": lines, "rels": [variants[vi] for vi in choice], "accepted": acc}
    return None


def faces():
    return {(i, v): frozenset(s for s in CUBE if s[i] == v) for i in range(3) for v in (0, 1)}


def pinned_binary(R):
    """(coordinate i, value c, kind) such that pinning coordinate i of R to c leaves equality or disequality on the other two, if any"""
    for i in range(3):
        rest = [j for j in range(3) if j != i]
        for c in (0, 1):
            pairs = {(s[rest[0]], s[rest[1]]) for s in R if s[i] == c}
            if pairs == {(0, 0), (1, 1)}:
                return i, c, "equality"
            if pairs == {(0, 1), (1, 0)}:
                return i, c, "disequality"
    return None


# ------------------------------------------------------------------------------------------------ the reduction of the pinning theorem
class Builder:
    def __init__(self):
        self.lines, self.deg, self.fresh = [], {}, 0

    def point(self, tag):
        self.fresh += 1
        p = (tag, self.fresh)
        self.deg[p] = 0
        return p

    def line(self, pts, R):
        assert len(set(pts)) == 3
        for p in pts:
            self.deg[p] += 1
            assert self.deg[p] <= 3, p
        self.lines.append((tuple(pts), frozenset(R)))

    def piece(self, g, ports):
        inner = {i: self.point('in') for i in range(g["k"])}
        name = dict(zip(('a', 'b', 'c'), ports))
        name.update(inner)
        for l, R in zip(g["lines"], g["rels"]):
            self.line([name[p] for p in l], R)


def to_cubic(n, constraints, pin, full, link):
    """constraints: (three variables, relation) with any number of occurrences per variable. pin: a piece accepting a face, with
    (port index, value); full: a piece accepting everything; link: (relation, i, c, kind) from pinned_binary. Returns a Builder whose system
    is cubic and has the same solvability."""
    (pin_piece, (pin_port, pin_value)), (link_R, link_i, link_c, link_kind) = pin, link
    B = Builder()
    occ = {v: [] for v in range(n)}
    for ci, (vs, R) in enumerate(constraints):
        for j, v in enumerate(vs):
            occ[v].append((ci, j))
    spare, pinned = [], []

    def pinned_incidence():
        if not pinned:
            ports = [B.point('d'), B.point('d'), B.point('d')]
            B.piece(pin_piece, ports)
            pinned.extend([ports[pin_port]] * 2)
            spare.extend([q for i, q in enumerate(ports) if i != pin_port for _ in range(2)])
        return pinned.pop()

    def link_line(x, y):
        """a line of link_R through a pinned point (seen as link_c) and x, y, making x = y"""
        # orient: the pinned point goes to coordinate link_i; flip it so that it is seen as link_c; flip y for disequality
        rest = [j for j in range(3) if j != link_i]
        order = [None, None, None]
        order[link_i] = pinned_incidence()
        order[rest[0]], order[rest[1]] = x, y
        f = [0, 0, 0]
        f[link_i] = pin_value ^ link_c
        if link_kind == "disequality":
            f[rest[1]] = 1
        B.line(order, flip(link_R, tuple(f)))

    slot = {}
    for v in range(n):
        copies = [B.point(('v', v)) for _ in range(max(1, len(occ[v])))]
        for x, y in zip(copies, copies[1:]):
            link_line(x, y)
        for o, p in zip(occ[v], copies):
            slot[o] = p
        uses = {}
        for o, p in slot.items():
            uses[p] = uses.get(p, 0) + 1
        for p in copies:
            spare.extend([p] * (3 - B.deg[p] - uses.get(p, 0)))
    for ci, (vs, R) in enumerate(constraints):
        B.line([slot[(ci, j)] for j in range(3)], R)
    spare.extend(pinned)
    demand = {}
    for p in spare:
        demand[p] = demand.get(p, 0) + 1
    total = sum(demand.values())
    assert total % 3 == 0
    while demand and max(demand.values()) > total // 3:
        demand[B.point('pad')] = 3
        total += 3
    while demand:
        trio = sorted(demand, key=lambda q: (-demand[q], repr(q)))[:3]
        assert len(trio) == 3
        B.piece(full, trio)
        for q in trio:
            demand[q] -= 1
            if not demand[q]:
                del demand[q]
    return B


def sat(lines):
    """SAT check for lines (points, relation): each forbidden state of a line is one clause"""
    from pysat.solvers import Minisat22
    pts = sorted({p for l, R in lines for p in l}, key=repr)
    var = {p: i + 1 for i, p in enumerate(pts)}
    with Minisat22() as solver:
        for l, R in lines:
            for s in CUBE:
                if s not in R:
                    solver.add_clause([-var[p] if b else var[p] for p, b in zip(l, s)])
        return solver.solve()


def solvable_direct(n, constraints):
    return any(all(tuple(x[v] for v in vs) in R for vs, R in constraints) for x in itertools.product((0, 1), repeat=n))
