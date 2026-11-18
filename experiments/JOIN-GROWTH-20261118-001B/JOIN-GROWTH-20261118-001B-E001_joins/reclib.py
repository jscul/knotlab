"""Reading per-round counts (JOIN-GROWTH-20261118-001B): exact recurrences and annihilators, standard library only.

An annihilator is a polynomial p(x) = sum_k p_k x^k (coefficients listed from the constant term up); it annihilates the counts c
from round t0 when sum_k p_k c(t - deg p + k) = 0 for every t with t0 <= t - deg p and t <= the last round."""
from fractions import Fraction


def berlekamp_massey(s):
    s = [Fraction(x) for x in s]
    C, B, L, m, b = [Fraction(1)], [Fraction(1)], 0, 1, Fraction(1)
    for n in range(len(s)):
        d = s[n] + sum(C[i] * s[n - i] for i in range(1, L + 1))
        if d == 0:
            m += 1
            continue
        T = C[:]
        coef = d / b
        C = C + [Fraction(0)] * (len(B) + m - len(C))
        for i in range(len(B)):
            C[i + m] -= coef * B[i]
        if 2 * L <= n:
            L, B, b, m = n + 1 - L, T, d, 1
        else:
            m += 1
    return L, C[:L + 1]


def minimal_recurrence(c, starts=range(2, 13), spare=2):
    """The least-order recurrence found by Berlekamp-Massey on c[st:], over the starts tried, with at least `spare` times its order
    of terms (and two more): returns (order, start, annihilator coefficients from the constant term up, as integers when they
    are), or None."""
    best = None
    for st in starts:
        s = c[st:]
        if len(s) < 8:
            break
        L, C = berlekamp_massey(s)
        if spare * L + 2 <= len(s) and (best is None or L < best[0]):
            # recurrence s[n] + C1 s[n-1] + ... + CL s[n-L] = 0  <->  annihilator x^L + C1 x^(L-1) + ... + CL
            p = [C[L - k] for k in range(L + 1)]
            den = 1
            for q in p:
                den = den * q.denominator // _gcd(den, q.denominator)
            best = (L, st, [int(q * den) for q in p])
    return best


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def annihilates(p, c, t0=0):
    """True when p annihilates c from round t0, with the residual rounds tested; False and the first failing round otherwise."""
    d = len(p) - 1
    tested = 0
    for t in range(t0 + d, len(c)):
        if sum(p[k] * c[t - d + k] for k in range(d + 1)) != 0:
            return False, t
        tested += 1
    return tested > 0, tested


def first_round_annihilated(p, c, last_needed=4):
    """The least t0 from which p annihilates c, if it holds on at least `last_needed` rounds; else None."""
    d = len(p) - 1
    bad = [t for t in range(d, len(c)) if sum(p[k] * c[t - d + k] for k in range(d + 1)) != 0]
    t0 = (max(bad) - d + 1) if bad else 0
    if len(c) - (t0 + d) < last_needed:
        return None
    return t0


def polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def polypow(a, k):
    out = [1]
    for _ in range(k):
        out = polymul(out, a)
    return out


def polyadd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]


def polyneg(a):
    return [-x for x in a]


def reverse(a, deg=None):
    """x^deg a(1/x) (deg defaults to the degree of a)."""
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    deg = len(a) - 1 if deg is None else deg
    out = [0] * (deg + 1)
    for i, x in enumerate(a):
        out[deg - i] = x
    return out


def dominant_root(p, lo=1.0, hi=16.0):
    """The largest real root above lo of the integer polynomial p (constant term first), by bisection on sign changes."""
    def f(x):
        return sum(q * x ** k for k, q in enumerate(p))
    xs = [lo + (hi - lo) * i / 4000 for i in range(4001)]
    root = None
    for a, b in zip(xs, xs[1:]):
        if f(a) == 0:
            root = a
        elif f(a) * f(b) < 0:
            for _ in range(200):
                m = (a + b) / 2
                if f(a) * f(m) <= 0:
                    b = m
                else:
                    a = m
            root = (a + b) / 2
    return root


def fit_power_exponential(c, lo):
    """Least squares of log c(t) = a + t log(lambda) + alpha log t on rounds lo..end: (lambda, alpha, max residual)."""
    import math
    ts = list(range(max(lo, 1), len(c)))
    rows = [(1.0, float(t), math.log(t)) for t in ts]
    ys = [math.log(c[t]) for t in ts]
    # normal equations, 3x3
    M = [[sum(r[i] * r[j] for r in rows) for j in range(3)] for i in range(3)]
    v = [sum(r[i] * y for r, y in zip(rows, ys)) for i in range(3)]
    sol = _solve3(M, v)
    res = max(abs(y - sum(s * x for s, x in zip(sol, r))) for r, y in zip(rows, ys))
    return math.exp(sol[1]), sol[2], res


def _solve3(M, v):
    A = [row[:] + [x] for row, x in zip(M, v)]
    for i in range(3):
        piv = max(range(i, 3), key=lambda r: abs(A[r][i]))
        A[i], A[piv] = A[piv], A[i]
        for r in range(3):
            if r != i:
                f = A[r][i] / A[i][i]
                A[r] = [a - f * b for a, b in zip(A[r], A[i])]
    return [A[i][3] / A[i][i] for i in range(3)]
