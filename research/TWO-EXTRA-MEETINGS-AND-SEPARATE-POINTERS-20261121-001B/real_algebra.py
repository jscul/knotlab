"""Exact rational matrices and the real instruments on the three active word addresses."""

from fractions import Fraction as F
from functools import reduce
from itertools import product
from math import gcd, lcm
import numpy as np


class Mat:
    """A rational matrix with one reduced denominator and unbounded integer entries."""

    def __init__(self, entries, den=1):
        a = np.array(entries, dtype=object)
        if a.ndim != 2 or not den:
            raise ValueError("A matrix and a nonzero denominator are required")
        g = reduce(gcd, (int(x) for x in a.flat), abs(int(den)))
        if den < 0:
            g = -g
        self.a, self.d = a // g, int(den) // g

    def __add__(self, other):
        n = lcm(self.d, other.d)
        return Mat(self.a * (n // self.d) + other.a * (n // other.d), n)

    def __sub__(self, other):
        return self + other.scale(-1)

    def __matmul__(self, other):
        return Mat(self.a @ other.a, self.d * other.d)

    @property
    def T(self):
        return Mat(self.a.T, self.d)

    def scale(self, factor):
        factor = F(factor)
        return Mat(self.a * factor.numerator, self.d * factor.denominator)

    def tr(self):
        return F(sum(self.a.diagonal()), self.d)

    def diag(self):
        return [str(F(x, self.d)) for x in self.a.diagonal()]

    def key(self):
        return (self.a.shape, self.d, tuple(self.a.flat))

    def __eq__(self, other):
        return self.d == other.d and np.array_equal(self.a, other.a)

    def dump(self):
        return {"den": self.d, "rows": self.a.tolist()}


def identity(n):
    return Mat(np.eye(n, dtype=int))


def zero(n):
    return Mat(np.zeros((n, n), dtype=int))


def tensor(*items):
    out = Mat([[1]])
    for m in items:
        out = Mat(np.kron(out.a, m.a), out.d * m.d)
    return out


def outer(v, w=None):
    return Mat(np.outer(v, v if w is None else w))


def ray(v):
    return outer(v).scale(F(1, sum(x * x for x in v)))


def add(items, n):
    return reduce(lambda a, b: a + b, items, zero(n))


def normalize(rho):
    return rho.scale(1 / rho.tr()) if rho.tr() else None


def partial_b(m, da, db):
    return Mat(
        m.a.reshape(da, db, da, db).transpose(0, 3, 2, 1).reshape(da * db, da * db), m.d
    )


def local_projection(m, n=3):
    return (m + partial_b(m, n, n)).scale(F(1, 2))


def reduce_sites(m):
    a = m.a.reshape(3, 3, 3, 3)
    return [Mat(np.trace(a, axis1=h, axis2=h + 2), m.d) for h in (1, 0)]


def diag_only(m):
    return Mat(np.diag(m.a.diagonal()), m.d)


def perm_image(p):
    out = np.zeros((len(p), len(p)), dtype=int)
    for j, k in enumerate(p):
        out[k, j] = 1
    return Mat(out)


class Catalogue:
    def __init__(self):
        self.ids = {}
        self.matrices = []

    def put(self, m):
        key = m.key()
        if key not in self.ids:
            self.ids[key] = len(self.matrices)
            self.matrices.append(m.dump())
        return self.ids[key]


C = perm_image((1, 2, 0))
T = perm_image((1, 0, 2))
I = identity(3)
H = (1, 1, 1)
R = (1, -1, 0)
S = (1, 1, -2)
LOCAL = {
    "word": [(1, 0, 0), (0, 1, 0), (0, 0, 1)],
    "ab": [(1, 1, 0), (1, -1, 0), (0, 0, 1)],
    "hrs": [H, R, S],
}
MEAS = {name: [ray(v) for v in vs] for name, vs in LOCAL.items()}
P = I - ray(H)
D = C - C.T
PROJECTORS = {
    j: ray(v)
    for j, v in enumerate(
        [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
    )
}


def powers(g):
    return (identity(g.a.shape[0]), g, g @ g)


def group(g):
    """Each row is an integer Kraus numerator and its squared normalization."""
    i, g, g2 = powers(g)
    return ((i + g + g2, 9), (i - g, 6), (i + g - g2.scale(2), 18))


def instrument(rho, ks):
    return [(k @ rho @ k.T).scale(F(1, n)) for k, n in ks]


def cycling(g, rho):
    return g @ rho @ g.T


def twirl(g, rho):
    return add([cycling(k, rho) for k in powers(g)], rho.a.shape[0]).scale(F(1, 3))


def real_charge(a, b):
    """Real part of the supplied complex charge-pair density, a,b in {-1,1}."""
    return (tensor(P, P) - tensor(D, D).scale(F(a * b, 3))).scale(F(1, 4))


def ideal_complex_charge(a, b):
    """Complete density as coefficients in 1,omega where omega^2=-1-omega."""
    words = list(product(range(3), repeat=2))
    roots = ((1, 0), (0, 1), (-1, -1))
    out = [[roots[(a * (v - x) + b * (w - y)) % 3] for v, w in words] for x, y in words]
    re_part = Mat([[2 * u - v for u, v in row] for row in out], 18)
    assert re_part == real_charge(a, b)
    return {"den": 9, "entries_in_1_omega": out}


def born(rho, effect):
    return F(sum(x * y for x, y in zip(rho.a.flat, effect.a.T.flat)), rho.d * effect.d)


def angles_rank(mats):
    """Exact fraction elimination for the real tomography-rank certificates."""
    from sympy import Matrix

    return int(Matrix([list(m.a.flat) for m in mats]).rank())
