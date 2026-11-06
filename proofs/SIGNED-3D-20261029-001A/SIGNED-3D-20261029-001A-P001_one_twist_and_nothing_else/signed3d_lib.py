"""Signed ordered edge laws in three dimensions (SIGNED-3D-20261029-001A).

Setting of TWIST-3D-20261025-001A: ordered tetrahedra (vertices 0 < 1 < 2 < 3, edges in the order 01, 02, 03, 12, 13, 23), one bit per
edge, ordered 2-3 and 1-4 moves on the 4-simplex [01234] with facets F_i (vertex i removed); with global orientation eps the facet F_i
has orientation eps (-1)^i on the new side and -eps (-1)^i on the old side.  A signed law gives each labelling l of the six edges a
weight W_s(l) in {-1, 0, 1} for each orientation s = +-1.  Identity: for every labelling of a move's boundary edges, the sum over the
new edges of the product of the new tetrahedra's weights equals lambda (2-3) or mu (1-4) times the product of the old ones.

SAT encoding: every weight is two variables, nz (nonzero) and ng (negative).  A product of weights gets an AND variable and an XOR
variable.  A 2-3 identity forbids, under a selector literal for lambda, every value triple (old, new0, new1) with new0 + new1 != lambda
old.  A 1-4 identity counts its 16 signed terms with a two-sided totalizer (c_k <=> at least k of the 32 inputs P_t and not-N_t hold) and
fixes the count to 16 + mu old under a selector literal for mu.  One solver answers every (lambda, mu) under assumptions."""
import itertools
from collections import Counter
from pysat.solvers import Solver

E5 = [(a, b) for a in range(5) for b in range(a + 1, 5)]
EDGES4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
FACES4 = list(itertools.combinations(range(4), 3))
LABS = list(itertools.product((0, 1), repeat=6))
LAMS = (0, 1, -1, 2, -2)
MUS = tuple([0] + [m for a in range(1, 17) for m in (a, -a)])


def tet_lab(x, verts):
    v = sorted(verts)
    return tuple(x[(v[i], v[j])] for i, j in EDGES4)


def facet(i):
    return tuple(v for v in range(5) if v != i)


def identities():
    """(kind, old items, list of new item tuples); kind 0 = 2-3, 1 = 1-4; item = (orientation sign, labelling); every boundary labelling"""
    out = []
    for eps in (1, -1):
        for p, q in itertools.combinations(range(5), 2):
            others = [v for v in range(5) if v not in (p, q)]
            bnd = [e for e in E5 if e != (p, q)]
            for lab in itertools.product((0, 1), repeat=9):
                x = dict(zip(bnd, lab))
                old = tuple((-eps * (-1) ** i, tet_lab(x, facet(i))) for i in (p, q))
                new = []
                for e in (0, 1):
                    y = dict(x)
                    y[(p, q)] = e
                    new.append(tuple((eps * (-1) ** r, tet_lab(y, facet(r))) for r in others))
                out.append((0, old, new))
        for r in range(5):
            F = facet(r)
            bnd = [e for e in E5 if r not in e]
            newe = [e for e in E5 if r in e]
            for lab in itertools.product((0, 1), repeat=6):
                x = dict(zip(bnd, lab))
                old = ((-eps * (-1) ** r, tet_lab(x, F)),)
                new = []
                for nl in itertools.product((0, 1), repeat=4):
                    y = dict(x)
                    y.update(zip(newe, nl))
                    new.append(tuple((eps * (-1) ** s, tet_lab(y, facet(s))) for s in range(5) if s != r))
                out.append((1, old, new))
    return out


class Census:
    """one solver holding every identity, with selector literals for lambda and mu"""

    def __init__(self, ids, use14=True):
        self.top = 0
        self.nz = {(s, l): self.var() for s in (1, -1) for l in LABS}
        self.ng = {(s, l): self.var() for s in (1, -1) for l in LABS}
        self.sel_l = {lam: self.var() for lam in LAMS}
        self.sel_m = {mu: self.var() for mu in MUS}
        self.cl, self.cache = [], {}
        for kind, old, new in ids:
            if kind == 0:
                self._two_three(old, new)
            elif use14:
                self._one_four(old, new)
        self.cl.append([self.nz[k] for k in self.nz])          # a nonzero law
        self.solver = Solver(name="cadical195", bootstrap_with=self.cl)

    def var(self):
        self.top += 1
        return self.top

    def term(self, items):
        """(nz literal, ng literal or None when the product is never negative) of a product of weights"""
        c = Counter(items)
        key = tuple(sorted(c.items()))
        if key in self.cache:
            return self.cache[key]
        nzs = [self.nz[it] for it in c]
        ngs = [self.ng[it] for it, m in c.items() if m % 2 == 1]
        if len(nzs) == 1:
            tnz = nzs[0]
        else:
            tnz = self.var()
            self.cl += [[-tnz, v] for v in nzs] + [[tnz] + [-v for v in nzs]]
        if not ngs:
            tng = None
        elif len(ngs) == 1:
            tng = ngs[0]
        else:
            tng = self.var()
            for bits in itertools.product((0, 1), repeat=len(ngs)):
                # if the inputs equal bits then tng equals their parity
                self.cl.append([(-v if b else v) for v, b in zip(ngs, bits)] + ([-tng] if sum(bits) % 2 == 0 else [tng]))
        self.cache[key] = (tnz, tng)
        return tnz, tng

    @staticmethod
    def cond(t, val):
        """literals whose conjunction says that term t has value val (None: impossible)"""
        tnz, tng = t
        if val == 0:
            return [-tnz]
        if tng is None:
            return [tnz] if val == 1 else None
        return [tnz, -tng] if val == 1 else [tnz, tng]

    def _two_three(self, old, new):
        O, A, B = self.term(old), self.term(new[0]), self.term(new[1])
        for lam in LAMS:
            for o, a, b in itertools.product((-1, 0, 1), repeat=3):
                if a + b == lam * o:
                    continue
                cs = [self.cond(O, o), self.cond(A, a), self.cond(B, b)]
                if any(c is None for c in cs):
                    continue
                self.cl.append([-l for c in cs for l in c] + [-self.sel_l[lam]])

    def _unary(self, lits):
        """two-sided totalizer: returns c with c[k] <=> (at least k of lits), c[0] true, c[n+1] false (as None)"""
        if len(lits) == 1:
            return [True, lits[0]]
        h = len(lits) // 2
        A, B = self._unary(lits[:h]), self._unary(lits[h:])
        p, q = len(A) - 1, len(B) - 1
        C = [True] + [self.var() for _ in range(p + q)]
        def lit(V, i):
            return True if i == 0 else (False if i >= len(V) else V[i])
        for i in range(p + 1):
            for j in range(q + 1):
                if i + j >= 1:      # a_i and b_j imply c_(i+j)
                    cl = [-x for x in (lit(A, i), lit(B, j)) if x is not True]
                    self.cl.append(cl + [C[i + j]])
                k = i + j + 1       # not a_(i+1) and not b_(j+1) imply not c_(i+j+1)
                if k <= p + q:
                    cl = [x for x in (lit(A, i + 1), lit(B, j + 1)) if x is not False]
                    self.cl.append(cl + [-C[k]])
        return C

    def _one_four(self, old, new):
        O = self.term(old)
        lits, const = [], 0
        for t in new:
            tnz, tng = self.term(t)
            if tng is None:
                lits.append(tnz)
                const += 1                      # "not negative" always holds
            else:
                P, Nn = self.var(), self.var()
                self.cl += [[-P, tnz], [-P, -tng], [P, -tnz, tng], [-Nn, tnz], [-Nn, tng], [Nn, -tnz, -tng]]
                lits += [P, -Nn]
        C = self._unary(lits)
        n = len(lits)
        def fix(target, extra):
            """count of lits = target - const, under the literals extra (a list of negated conditions)"""
            k = target - const
            if k < 0 or k > n:
                self.cl.append(extra)
                return
            if k >= 1:
                self.cl.append(extra + [C[k]])
            if k + 1 <= n:
                self.cl.append(extra + [-C[k + 1]])
        for o in (-1, 0, 1):
            c = self.cond(O, o)
            if c is None:
                continue
            neg = [-l for l in c]
            if o == 0:
                fix(16, neg)
            else:
                for mu in MUS:
                    fix(16 + mu * o, neg + [-self.sel_m[mu]])

    def assume(self, lam, mu):
        return [self.sel_l[lam], self.sel_m[mu]]

    def solve(self, lam, mu, extra=()):
        ok = self.solver.solve(assumptions=self.assume(lam, mu) + list(extra))
        return set(v for v in self.solver.get_model() if v > 0) if ok else None

    def weights(self, model):
        return {(s, l): (0 if self.nz[(s, l)] not in model else (-1 if self.ng[(s, l)] in model else 1)) for s in (1, -1) for l in LABS}

    def supports(self, lam, mu, cap=10000):
        """every support (pair of sets of labellings) of a law with factors (lam, mu), by enumeration with blocking clauses"""
        act = self.var()
        out = []
        while len(out) < cap:
            m = self.solve(lam, mu, [act])
            if m is None:
                break
            sp = {s: frozenset(l for l in LABS if self.nz[(s, l)] in m) for s in (1, -1)}
            out.append(sp)
            self.solver.add_clause([-act] + [(-self.nz[k] if self.nz[k] in m else self.nz[k]) for k in self.nz])
        self.solver.add_clause([-act])
        return out

    def sign_solutions(self, lam, mu, sup, cap=10000):
        """every law with factors (lam, mu) and support sup = {s: set of labellings}, as weight dicts"""
        act = self.var()
        fixed = [(self.nz[(s, l)] if l in sup[s] else -self.nz[(s, l)]) for s in (1, -1) for l in LABS]
        ngv = [self.ng[(s, l)] for s in (1, -1) for l in sorted(sup[s])]
        out = []
        while len(out) < cap:
            m = self.solve(lam, mu, [act] + fixed)
            if m is None:
                break
            out.append(self.weights(m))
            self.solver.add_clause([-act] + [(-v if v in m else v) for v in ngv])
        self.solver.add_clause([-act])
        return out


# ------------------------------------------------------------------ the laws
def face_labels(l):
    x = dict(zip(EDGES4, l))
    return [(x[(a, b)], x[(b, c)], x[(a, c)]) for a, b, c in FACES4]


def face_parities(l):
    return tuple(sum(f) % 2 for f in face_labels(l))


ZEVEN = frozenset(l for l in LABS if face_parities(l) == (0, 0, 0, 0))
ZODD = frozenset(l for l in LABS if face_parities(l) == (1, 1, 1, 1))
SUPPORTS = {"all 0": frozenset([(0,) * 6]), "all 1": frozenset([(1,) * 6]), "all equal": frozenset([(0,) * 6, (1,) * 6]),
            "even cocycles": ZEVEN, "odd cocycles": ZODD, "even or odd": ZEVEN | ZODD, "free": frozenset(LABS)}
FACTORS = {"all 0": (1, 1), "all 1": (1, 1), "all equal": (1, 1), "even cocycles": (1, 2), "odd cocycles": (1, 2), "even or odd": (1, 2),
           "free": (2, 16)}


def spine(l):
    """x_01 x_12 x_23: the edges of the path 0-1-2-3 given by the vertex order"""
    x = dict(zip(EDGES4, l))
    return x[(0, 1)] * x[(1, 2)] * x[(2, 3)]


def twist_even(l):
    """the Dijkgraaf-Witten weight (-1)^(x_01 x_12 x_23) on even cocycles"""
    return -1 if spine(l) else 1


def twist_odd(l):
    """its translate on odd cocycles: x = c + 1 with c an even cocycle"""
    return -1 if spine(tuple(1 - b for b in l)) else 1


def law(support, sign=lambda l: 1):
    return {(s, l): (sign(l) if l in support else 0) for s in (1, -1) for l in LABS}


def mixed(te, to):
    """the even-or-odd law with the twist (te, to) on the even and odd parts"""
    return {(s, l): (0 if l not in ZEVEN | ZODD else (twist_even(l) if te and l in ZEVEN else (twist_odd(l) if to and l in ZODD else 1)))
            for s in (1, -1) for l in LABS}


def direct_ok(ids, W, lam, mu):
    """every identity by direct evaluation"""
    for kind, old, new in ids:
        lhs = 0
        for n in new:
            p = 1
            for it in n:
                p *= W[it]
                if p == 0:
                    break
            lhs += p
        rhs = 1
        for it in old:
            rhs *= W[it]
        if lhs != (lam if kind == 0 else mu) * rhs:
            return False
    return True


def gauge(W, tau):
    """the face gauge: multiply W_s(l) by the product over the four faces of tau(face labelling) (tau: dict face labelling -> +-1)"""
    out = {}
    for (s, l), w in W.items():
        g = 1
        for f in face_labels(l):
            g *= tau.get(f, 1)
        out[(s, l)] = w * g
    return out


def orbit_key(W):
    """canonical member of the face-gauge orbit of W (over the face labellings that occur in the support)"""
    used = sorted({f for (s, l), w in W.items() if w for f in face_labels(l)})
    best = None
    for bits in itertools.product((1, -1), repeat=len(used)):
        img = gauge(W, dict(zip(used, bits)))
        key = tuple(img[(s, l)] for s in (1, -1) for l in LABS)
        if best is None or key < best:
            best = key
    return best


def s4_images(l):
    x = dict(zip(EDGES4, l))
    out = []
    for p in itertools.permutations(range(4)):
        y = {}
        for a, b in EDGES4:
            u, v = sorted((p[a], p[b]))
            y[(u, v)] = x[(a, b)]
        out.append(tuple(y[e] for e in EDGES4))
    return out


def symmetric_member(W):
    """whether some face-gauge copy of W is the same for both orientations and invariant under the 24 vertex permutations"""
    used = sorted({f for (s, l), w in W.items() if w for f in face_labels(l)})
    for bits in itertools.product((1, -1), repeat=len(used)):
        G = gauge(W, dict(zip(used, bits)))
        if all(G[(1, l)] == G[(-1, l)] for l in LABS) and all(G[(1, m)] == G[(1, l)] for l in LABS for m in s4_images(l)):
            return True
    return False
