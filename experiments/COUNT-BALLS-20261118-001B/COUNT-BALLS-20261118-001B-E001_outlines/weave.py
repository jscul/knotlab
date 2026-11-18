"""The endless six-regular weave under not-all-equal: exact pair counts on the infinite weave.

Distinctions sit at pairs of whole numbers (i, j); the co-knotted pairs are (i, j)-(i+1, j), (i, j)-(i, j+1) and
(i+1, j)-(i, j+1); the knots are the up triples {(i,j), (i+1,j), (i,j+1)} and down triples {(i+1,j), (i,j+1), (i+1,j+1)}.
The class of a distinction is (i + 2j) mod 3.  Allowed states leave every knot not all equal; the weighting is uniform, read
on the endless weave as the limit of uniform weightings (the maximal-entropy measure).

In every allowed state each knot has exactly one co-knotted pair with equal values; marking those pairs gives a perfect
matching of the honeycomb whose vertices are the knots (white = up, black = down), two states per matching.  Along a row of
co-knotted pairs from x to y, s_x s_y = prod (2 D_b - 1) with D_b = 1 on marked pairs, so the pair correlation is
(-1)^L E[prod (1 - 2 D_b)] = (-1)^L det(I - 2M), M_ef = K^{-1}(b_e, w_f) (Kenyon's local statistics, uniform weights).

K^{-1}(B(x + D), W(x)) = I(D) is computed exactly: for D2 <= -1 it is a finite sum, rational plus sqrt(3)/pi times a
rational; other D reduce to that case by the three-fold symmetry about a white knot, I(D) = I(f(D)),
f(D) = (-D1 - D2 - 1, D1).
The disagreement rate of x and y is (1 - C)/2, C the correlation; tau = -log_3 |C|."""
import functools
import math
from fractions import Fraction

import mpmath as mp

mp.mp.dps = 60
E, N, NW, W_, S_, SE = (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)


def cls(p):
    return (p[0] + 2 * p[1]) % 3


def position(p):
    """Drawing coordinates, used only to report the literature's Euclidean separation."""
    return (p[0] + p[1] / 2, p[1] * math.sqrt(3) / 2)


def euclid(p):
    x, y = position(p)
    return math.hypot(x, y)


@functools.lru_cache(maxsize=None)
def kinv_exact(a, b):
    """I(a, b) = rat + (sqrt3/pi) * irr, as two Fractions."""
    if b >= 0:
        if a <= -1:
            return kinv_exact(-a - b - 1, a)        # f
        return kinv_exact(b, -a - b - 1)            # f o f
    n = -b - 1
    rat, irr = Fraction(0), Fraction(0)
    sign = -1 if n % 2 else 1
    for m in range(n + 1):
        j = a - m
        c = math.comb(n, m) * sign
        if j == 0:
            rat += Fraction(c, 3)                       # 1 - 2/3
        else:
            r = j % 3
            if r == 0:
                continue
            chi = 1 if r == 1 else -1                   # sin(2 pi j/3) = (sqrt3/2) chi
            irr += Fraction(-c * chi, 2 * j)            # -sin(2pi j/3)/(pi j) = -(sqrt3/pi) chi/(2j)
    return rat, irr


def kinv(a, b):
    rat, irr = kinv_exact(a, b)
    return mp.mpf(rat.numerator) / rat.denominator + mp.sqrt(3) / mp.pi * mp.mpf(irr.numerator) / irr.denominator


@functools.lru_cache(maxsize=None)
def _gauss(nodes):
    from numpy.polynomial.legendre import leggauss
    return leggauss(nodes)


def kinv_quad(a, b, nodes=600):
    """Independent numerical value of I(a, b) for b >= 0 (Gauss-Legendre), a check only."""
    import numpy as np
    x, w = _gauss(nodes)
    L = 2 * math.pi / 3
    k, w = x * L, w * L
    c = 1 + np.exp(-1j * k)
    return float((np.sum(w * np.exp(1j * k * a) * (-1) ** b * c ** (-b - 1)) / (2 * math.pi)).real)


def edge(p, q):
    """The honeycomb pair (white, black) of the co-knotted pair p-q."""
    d = (q[0] - p[0], q[1] - p[1])
    if d in (W_, S_, SE):
        p, q, d = q, p, (-d[0], -d[1])
    i, j = p
    if d == E:
        return (i, j), (i, j - 1)
    if d == N:
        return (i, j), (i - 1, j)
    if d == NW:
        return (i - 1, j), (i - 1, j)
    raise ValueError(d)


def walk(steps, start=(0, 0)):
    p = [start]
    for s in steps:
        p.append((p[-1][0] + s[0], p[-1][1] + s[1]))
    return p


def corr(path):
    edges = [edge(path[t], path[t + 1]) for t in range(len(path) - 1)]
    if len(set(edges)) != len(edges):
        raise ValueError("a row of co-knotted pairs must not repeat a pair")
    m = len(edges)
    A = mp.matrix(m, m)
    for e, (_, be) in enumerate(edges):
        for f, (wf, _) in enumerate(edges):
            A[e, f] = (1 if e == f else 0) - 2 * kinv(be[0] - wf[0], be[1] - wf[1])
    return (-1) ** m * mp.det(A)


# rays of one class, as repeated step sequences; the target of k repeats is k * vector
RAYS = {
    "row (0 deg)": ((3, 0), [E, E, E]),
    "(4,1) (10.9 deg)": ((4, 1), [E, E, E, E, N]),
    "(5,2) (16.1 deg)": ((5, 2), [E, N, E, E, N, E, E]),
    "(1,1) (30 deg)": ((1, 1), [E, N]),
}


def steps_to(a, b):
    """A shortest row of co-knotted pairs from (0, 0) to (a, b): steps apart = max(|a|, |b|, |a + b|)."""
    out = []
    if a * b < 0:
        k = min(abs(a), abs(b))
        out += [NW if a < 0 else SE] * k
        a, b = a + (k if a < 0 else -k), b + (-k if b > 0 else k)
    out += [E if a > 0 else W_] * abs(a) + [N if b > 0 else S_] * abs(b)
    return out


def kinv_float(a, b):
    rat, irr = kinv_exact(a, b)
    return float(rat) + math.sqrt(3) / math.pi * float(irr)


def corr_float(path):
    import numpy as np
    edges = [edge(path[t], path[t + 1]) for t in range(len(path) - 1)]
    m = len(edges)
    A = np.empty((m, m))
    for e, (_, be) in enumerate(edges):
        for f, (wf, _) in enumerate(edges):
            A[e, f] = (1.0 if e == f else 0.0) - 2.0 * kinv_float(be[0] - wf[0], be[1] - wf[1])
    return (-1) ** m * float(np.linalg.det(A))


def row_toeplitz(r):
    """Independent row formula (advisor's derivation, checked here): C(r) = (-1)^r det[delta - 2 g(j - k)],
    g(0) = 1/3, g(n) = (-1)^n sin(n pi/3)/(pi n)."""
    def g(n):
        return mp.mpf(1) / 3 if n == 0 else (-1) ** n * mp.sin(n * mp.pi / 3) / (mp.pi * n)
    A = mp.matrix(r, r)
    for j in range(r):
        for k in range(r):
            A[j, k] = (1 if j == k else 0) - 2 * g(j - k)
    return (-1) ** r * mp.det(A)


# the literature's exact amplitude of sqrt(r) C(r) along any ray of the start's class (Stephenson 1970, as the advisor
# recalled it: a = 2 3^(-1/4) E0^2, E0 = 2^(1/12) e^(3 zeta'(-1))); registered as a prediction, not assumed
def amplitude_literature():
    E0 = mp.mpf(2) ** (mp.mpf(1) / 12) * mp.e ** (3 * mp.zeta(-1, derivative=1))
    return 2 * mp.mpf(3) ** (-mp.mpf(1) / 4) * E0 ** 2
