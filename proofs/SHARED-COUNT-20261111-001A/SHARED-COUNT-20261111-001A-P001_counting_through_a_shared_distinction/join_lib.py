"""Counting through a shared distinction (research/SHARED-COUNT-20261111-001/preregistration.md).

A joined base: copies of the 8-distinction counting weave (2, 0, 4) (drawn as a torus; PARITY-NEEDS-20261111-001), each a two-fold weave
of its own, joined by sharing distinctions: the read distinction of one copy is the same distinction as an input of the next. A shared
distinction lies in six knots, three from each copy, and its knots close into two tours, not one, so the joined base is not a two-fold
weave. Each copy keeps its own closed tours, so the dissonance W is the sum of the copies' (A66). The learner, its probe and the harness
are PARITY-FIVE-20261111-001's, unchanged; the engine's one count serves both distinctions and knots, so a joined base with fewer
distinctions than knots is padded with inert distinctions in no knot, never held, read or disturbed."""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PARITY-FIVE-20261111-001A/PARITY-FIVE-20261111-001A-P001_parity_of_five_held_points"))
import five_lib as F  # noqa: E402

SL, U = F.SL, F.U
COPY = (2, 0, 4)
IN, OUT = (0, 1, 4), 5  # in the copy's tightest class, 5 = 0 + 1 + 4 mod 2 (PARITY-NEEDS-20261111-001)


class Tours:
    """the closed tours (corners at each tour) of the joined base, in the shape the engine reads from a weave: vert[line] = its three
    corners' tour ids"""

    def __init__(self, vert):
        self.vert = vert


class Joined:
    """copies of a two-fold weave joined by shared distinctions. chain(m): m copies, the read distinction of copy j shared with the first
    input of copy j + 1. Global distinctions: copy 0's eight, then each later copy's seven unshared ones, then inert padding."""

    def __init__(self, m):
        self.m = m
        self.copies = [SL.KnotSpace(SL.torus(*COPY)) for _ in range(m)]
        K0 = self.copies[0]
        self.gid = []
        nxt = 0
        for j, K in enumerate(self.copies):
            g = {}
            for p in range(K.n):
                if j > 0 and p == IN[0]:
                    g[p] = self.gid[j - 1][OUT]
                else:
                    g[p] = nxt
                    nxt += 1
            self.gid.append(g)
        self.real = nxt
        self.nl = sum(K.n for K in self.copies)
        assert self.real <= self.nl
        self.n = self.nl  # the engine's single count: knots, and distinctions with padding
        self.pt, vert, self.lines, off = [], {}, [], 0
        for j, K in enumerate(self.copies):
            for i in range(K.n):
                li = len(self.pt)
                self.pt.append([self.gid[j][K.pt[i][k]] for k in range(3)])
                vert[li] = [off + K.S.vert[K.lines[i]][c] for c in range(3)]
                self.lines.append(li)
            off += K.V
        self.V = off
        self.S = Tours(vert)
        self.chi = sum(K.chi for K in self.copies)
        self.ports = [self.gid[0][p] for p in IN] + [self.gid[j][p] for j in range(1, m) for p in IN[1:]] + [self.gid[m - 1][OUT]]
        self.shared = [self.gid[j][IN[0]] for j in range(1, m)]

    def signing(self, classes=None):
        """the copies' signings, concatenated: each copy's base law, or the given class of each copy"""
        out = []
        for j, K in enumerate(self.copies):
            out += K.signing() if classes is None else U.all_classes(K)[classes[j]]
        return out

    def clauses(self, s):
        cl = []
        for i in range(self.nl):
            lits = [(self.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1) for k in range(3)]
            cl.append(lits)
            cl.append([-x for x in lits])
        return cl


def floor_states(J, s, cap=F.STATE_CAP):
    """every assignment of the real distinctions satisfying every knot, as ints"""
    from pysat.solvers import Solver
    out = []
    with Solver(name="cadical153", bootstrap_with=J.clauses(s)) as so:
        while so.solve():
            m = so.get_model()
            x = [int(m[p] > 0) if p < len(m) else 0 for p in range(J.real)]
            out.append(sum(b << p for p, b in enumerate(x)))
            if len(out) > cap:
                return None
            so.add_clause([-(p + 1) if b else (p + 1) for p, b in enumerate(x)])
    return out


def realizable(J):
    """every combination of the copies' classes: the floor count, the map at the joined interface (by SAT), and whether the floor states
    have a parity set of size 2m + 2 there (five_lib's exact test)"""
    rows = []
    for combo in itertools.product(range(4), repeat=J.m):
        s = J.signing(combo)
        st = floor_states(J, s)
        T = tuple(sorted(J.ports))
        sets = [t for t, c in F.parity_sets(st, J.real, len(J.ports)) if t == T] if st else []
        rows.append({"classes": list(combo), "floor states": len(st), "parity at the interface": bool(sets),
                     "map": F.read_map_k(J, s, J.ports)})
    return rows


class Space:
    """LEARN-PARITY-20261111-001's Bare, for a joined base: the start is the copies' base laws at the solver's first satisfying state"""

    def __init__(self, m):
        self.J = Joined(m)
        self.K, self.S = self.J, self.J.S
        self.floor2 = 0
        self.ports = list(self.J.ports)
        self.movable = [p for p in range(self.J.real) if p not in self.ports]
        self.name = "%d copies joined in a chain" % m

    def start(self):
        s = self.J.signing()
        from pysat.solvers import Solver
        with Solver(name="cadical153", bootstrap_with=self.J.clauses(s)) as so:
            assert so.solve()
            m = so.get_model()
        return s, [int(m[p] > 0) if p < len(m) else 0 for p in range(self.J.n)]


def run(m, targets, seed, budget=8_000_000):
    return F.run(Space(m), targets, seed, budget)
