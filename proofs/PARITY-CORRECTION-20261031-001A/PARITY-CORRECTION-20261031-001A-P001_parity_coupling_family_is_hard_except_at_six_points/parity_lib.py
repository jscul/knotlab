"""Parity's coupling family on cubic systems (PARITY-CORRECTION-20261031-001A): shared library.

A cubic system is a list of lines, each a tuple of three points, with points 0..n-1, every point on exactly three lines and as many
lines as points. A signing gives each line a bit b (the parity of its negated incidences). Parity's coupling weighs a colouring c by
lam^(number of lines whose colour sum differs from b mod 2); the knot's coupling (not-all-equal) weighs it by lam^(number of
monochromatic lines). Values are exact: Fractions, or Gaussian rationals (class GQ)."""
import itertools
from fractions import Fraction


class GQ:
    """Gaussian rational re + im i"""
    __slots__ = ("re", "im")

    def __init__(self, re, im=0):
        self.re, self.im = Fraction(re), Fraction(im)

    @staticmethod
    def of(x):
        return x if isinstance(x, GQ) else GQ(x)

    def __add__(self, o):
        o = GQ.of(o)
        return GQ(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __neg__(self):
        return GQ(-self.re, -self.im)

    def __sub__(self, o):
        return self + (-GQ.of(o))

    def __rsub__(self, o):
        return GQ.of(o) - self

    def __mul__(self, o):
        o = GQ.of(o)
        return GQ(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def inverse(self):
        d = self.re * self.re + self.im * self.im
        return GQ(self.re / d, -self.im / d)

    def __truediv__(self, o):
        return self * GQ.of(o).inverse()

    def __rtruediv__(self, o):
        return GQ.of(o) * self.inverse()

    def __pow__(self, k):
        base, out = (self, GQ(1)) if k >= 0 else (self.inverse(), GQ(1))
        for _ in range(abs(k)):
            out = out * base
        return out

    def __eq__(self, o):
        if isinstance(o, (int, Fraction, GQ)):
            o = GQ.of(o)
            return self.re == o.re and self.im == o.im
        return NotImplemented

    def __hash__(self):
        return hash((self.re, self.im))

    def __repr__(self):
        return f"({self.re}{'+' if self.im >= 0 else '-'}{abs(self.im)}i)"


I = GQ(0, 1)


def show(x):
    return repr(x) if isinstance(x, GQ) else str(x)


# ------------------------------------------------------------------------------------------------ systems
def npoints(lines):
    return 1 + max(max(L) for L in lines)


def is_cubic(lines):
    n = npoints(lines)
    deg = [0] * n
    for L in lines:
        for p in L:
            deg[p] += 1
    return len(lines) == n and all(d == 3 for d in deg)


def is_simple(lines):
    """every line has three distinct points"""
    return all(len(set(L)) == 3 for L in lines)


def has_repeated_lines(lines):
    keys = [frozenset(L) for L in lines]
    return len(set(keys)) < len(keys)


def is_connected(lines):
    n = npoints(lines)
    adj = [set() for _ in range(n)]
    for L in lines:
        for p in L:
            adj[p].update(L)
    seen, stack = {0}, [0]
    while stack:
        for q in adj[stack.pop()]:
            if q not in seen:
                seen.add(q)
                stack.append(q)
    return len(seen) == n


def theta(lines):
    """replace each line {x, y, z} by {x, u, v}, {y, u, v}, {z, u, v} with two new points u, v (Fan-Cai's gadget G4)"""
    n = npoints(lines)
    out = []
    for i, L in enumerate(lines):
        u, v = n + 2 * i, n + 2 * i + 1
        out += [(p, u, v) for p in L]
    return out


# ------------------------------------------------------------------------------------------------ line tables and evaluation
def bits(x):
    return (x & 1, x >> 1 & 1, x >> 2 & 1)


def par_table(lam, b=0):
    """parity's coupling on one line: index x = c0 + 2 c1 + 4 c2; weight lam when c0 + c1 + c2 + b is odd"""
    one = lam ** 0
    return [lam if (sum(bits(x)) + b) & 1 else one for x in range(8)]


def nae_table(lam):
    one = lam ** 0
    return [lam if x in (0, 7) else one for x in range(8)]


def brute(lines, tables):
    n = npoints(lines)
    total = 0
    for c in range(1 << n):
        w = 1
        for L, T in zip(lines, tables):
            w = w * T[(c >> L[0] & 1) | (c >> L[1] & 1) << 1 | (c >> L[2] & 1) << 2]
        total = total + w
    return total


def evaluate(lines, tables):
    """exact variable elimination (min-degree order) of the sum over colourings of the product of line tables"""
    factors = []
    for L, T in zip(lines, tables):
        vs = tuple(sorted(set(L)))
        pos = {v: i for i, v in enumerate(vs)}
        tab = [T[sum(((a >> pos[p]) & 1) << j for j, p in enumerate(L))] for a in range(1 << len(vs))]
        factors.append((vs, tab))
    remaining = {v for vs, _ in factors for v in vs}
    while remaining:
        best = None
        for v in remaining:
            u = set()
            for vs, _ in factors:
                if v in vs:
                    u.update(vs)
            if best is None or len(u) < best[0]:
                best = (len(u), v)
        v = best[1]
        remaining.discard(v)
        touching = [f for f in factors if v in f[0]]
        factors = [f for f in factors if v not in f[0]]
        scope = tuple(sorted(set().union(*[set(f[0]) for f in touching]) - {v}))
        full = scope + (v,)
        idx = {w: i for i, w in enumerate(full)}
        maps = [(tab, [idx[w] for w in vs]) for vs, tab in touching]
        new = []
        for a in range(1 << len(scope)):
            s = None
            for xv in (0, 1):
                aa = a | (xv << len(scope))
                prod = None
                for tab, where in maps:
                    val = tab[sum(((aa >> i) & 1) << j for j, i in enumerate(where))]
                    prod = val if prod is None else prod * val
                s = prod if s is None else s + prod
            new.append(s)
        factors.append((scope, new))
    out = 1
    for vs, tab in factors:
        out = out * tab[0]
    return out


def m_par(lines, lam, signs=None, method=evaluate):
    signs = signs or [0] * len(lines)
    return method(lines, [par_table(lam, b) for b in signs])


def m_nae(lines, lam, method=evaluate):
    return method(lines, [nae_table(lam)] * len(lines))


def distribution(lines, signs=None, law="parity"):
    """integer coefficients of the coupling as a polynomial in lam (n <= 10)"""
    n = npoints(lines)
    signs = signs or [0] * len(lines)
    cnt = [0] * (len(lines) + 1)
    for c in range(1 << n):
        k = 0
        for L, b in zip(lines, signs):
            s = (c >> L[0] & 1) + (c >> L[1] & 1) + (c >> L[2] & 1)
            k += ((s + b) & 1) if law == "parity" else (s in (0, 3))
        cnt[k] += 1
    return cnt


# ------------------------------------------------------------------------------------------------ GF(2): the code picture
def line_masks_of_points(lines):
    """for each point, the set of lines through it as a bitmask over lines (incidences counted mod 2)"""
    n = npoints(lines)
    rows = [0] * n
    for i, L in enumerate(lines):
        for p in L:
            rows[p] ^= 1 << i
    return rows


def reduce_basis(vectors):
    """row-echelon basis of the GF(2) span (dict pivot -> vector)"""
    basis = {}
    for v in vectors:
        while v:
            top = v.bit_length() - 1
            if top in basis:
                v ^= basis[top]
            else:
                basis[top] = v
                break
    return basis


def in_span(basis, v):
    while v:
        top = v.bit_length() - 1
        if top not in basis:
            return False
        v ^= basis[top]
    return True


def span(basis):
    out = [0]
    for v in basis.values():
        out += [x ^ v for x in out]
    return out


def solvable(lines, signs):
    """parity's law is solvable iff b lies in D, the span of the points' line sets"""
    b = sum(bit << i for i, bit in enumerate(signs))
    return in_span(reduce_basis(line_masks_of_points(lines)), b)


def kernel_basis(lines):
    """basis of ker N: line sets covering every point an even number of times (Gaussian elimination)"""
    m = len(lines)
    rows = line_masks_of_points(lines)          # each point gives the equation sum over its lines of s_l = 0
    piv_rows, pivots = [], []
    for r in rows:
        for pr, pc in zip(piv_rows, pivots):
            if r >> pc & 1:
                r ^= pr
        if r:
            pc = r.bit_length() - 1
            for k in range(len(piv_rows)):
                if piv_rows[k] >> pc & 1:
                    piv_rows[k] ^= r
            piv_rows.append(r)
            pivots.append(pc)
    free = [j for j in range(m) if j not in pivots]
    basis = []
    for f in free:
        s = 1 << f
        for pr, pc in zip(piv_rows, pivots):
            if pr >> f & 1:
                s |= 1 << pc
        basis.append(s)
    return basis


def popcount(x):
    return bin(x).count("1")


# ------------------------------------------------------------------------------------------------ the points lam = i, -i
def gauss_sum(a, c):
    """sum over u in GF(2)^k of i^(sum a_j u_j) (-1)^(sum over j<l of c_jl u_j u_l), a_j in Z/4, c symmetric over GF(2);
    polynomial time: each step sums out one variable, and either fixes a linear constraint or adds a quadratic term"""
    k = len(a)
    a = [x % 4 for x in a]
    c = [[c[j][l] & 1 if j != l else 0 for l in range(k)] for j in range(k)]
    alive = set(range(k))
    mult = GQ(1)
    while alive:
        t = min(alive)
        alive.discard(t)
        nb = [j for j in alive if c[t][j]]
        if a[t] % 2 == 1:                       # 1 + i^a (-1)^l = (1 + i^a) i^(e l), l = xor of the neighbours
            mult = mult * (1 + I ** a[t])
            e = 3 if a[t] == 1 else 1
            for j in nb:
                a[j] = (a[j] + e) % 4
            for j, l in itertools.combinations(nb, 2):
                c[j][l] ^= 1
                c[l][j] ^= 1
        else:                                   # 1 + (-1)^(a/2 + l) = 2 [l = a/2 mod 2]
            beta = a[t] // 2
            if not nb:
                if beta:
                    return GQ(0)
                mult = mult * 2
                continue
            mult = mult * 2
            j0, R = nb[0], nb[1:]                # u_j0 = beta xor (xor of R)
            alive.discard(j0)
            aj = a[j0]
            sgn = -1 if beta else 1
            mult = mult * I ** (aj * beta)
            for j in R:
                a[j] = (a[j] + sgn * aj) % 4
            for j, l in itertools.combinations(R, 2):
                if aj % 2:
                    c[j][l] ^= 1
                    c[l][j] ^= 1
            for m in list(alive):
                if c[j0][m]:
                    a[m] = (a[m] + 2 * beta) % 4
                    for j in R:
                        if j == m:
                            a[m] = (a[m] + 2) % 4
                        else:
                            c[j][m] ^= 1
                            c[m][j] ^= 1
            for m in range(k):
                c[j0][m] = c[m][j0] = 0
    return mult


def m_par_at_i(lines, signs, sign=1):
    """M(H, b; sign * i) in polynomial time: the dual form (1 + lam)^n sum over s in ker N of (-1)^(b.s) ((1 - lam)/(1 + lam))^|s|,
    with (1 - lam)/(1 + lam) = -i for lam = i and i for lam = -i, is a quadratic Gauss sum over a basis of ker N"""
    lam = sign * I
    e = 3 if sign == 1 else 1
    g = kernel_basis(lines)
    b = sum(bit << i for i, bit in enumerate(signs))
    a = [e * popcount(x) + 2 * (popcount(x & b) & 1) for x in g]
    c = [[popcount(g[j] & g[l]) & 1 for l in range(len(g))] for j in range(len(g))]
    return (1 + lam) ** len(lines) * gauss_sum(a, c)
