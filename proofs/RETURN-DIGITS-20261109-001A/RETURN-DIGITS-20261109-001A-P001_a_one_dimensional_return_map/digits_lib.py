"""Library for RETURN-DIGITS-20261109-001A: the return map of the cut-open torus at n = 2^m as a one-dimensional operator.

Polynomials over GF(2) are Python ints (bit i = coefficient of the i-th power), in whichever variable the function says (K, c, k
or mu). A_h = F[K]/(K^h), h = n/2, with the ball basis W_k(t + 1/t) = sum over |j| <= k of t^j (k < h): W_0 = 1, W_1 = 1 + K,
W_(k+1) = K W_k + W_(k-1). T_h(c) is the matrix in that basis of f -> (K + c) (iota f)(K + c) mod K^h, iota(W_k) = W_(h-1-k);
S_h(c) = T_h(c) R is the same map without the reversal. The torus side comes from CONE-COLLAPSE-20261109-001A's collapse_lib."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONE_LIB = ROOT / "proofs/CONE-COLLAPSE-20261109-001A/CONE-COLLAPSE-20261109-001A-P001_the_cone_and_its_return_map"
sys.path.insert(0, str(CONE_LIB))
import collapse_lib as CL  # noqa: E402

pmul, pdivmod, pdeg, val, factor, pstr = CL.pmul, CL.pdivmod, CL.pdeg, CL.val, CL.factor, CL.pstr


def binom_odd(i, j):
    return (j & ~i) == 0


def W_poly(k):
    """W_k(K) as an int in K"""
    a, b = 1, 1        # W_0 = 1, W_(-1) = W_0 = 1
    if k == 0:
        return 1
    cur, prev = 0b11, 1  # W_1 = 1 + K
    for _ in range(k - 1):
        cur, prev = (cur << 1) ^ prev, cur
    return cur


def to_W(poly_coeffs, h, Ws):
    """coefficients (list of GF(2)[c] ints, indexed by the power of K, length h) in the W basis"""
    mon = list(poly_coeffs) + [0] * (h - len(poly_coeffs))
    coef = [0] * h
    for i in range(h - 1, -1, -1):
        cc = mon[i]
        if cc:
            coef[i] = cc
            Wi = Ws[i]
            for j in range(Wi.bit_length()):
                if (Wi >> j) & 1:
                    mon[j] ^= cc
    return coef


def shift_times(p, h):
    """(K + c) p(K + c) mod K^h for p an int polynomial in K over GF(2); result: list of GF(2)[c] ints by power of K"""
    q = p << 1                                   # K p(K)
    out = [0] * h
    for i in range(q.bit_length()):              # K^i -> (K + c)^i = sum_j binom(i, j) c^(i - j) K^j
        if (q >> i) & 1:
            for j in range(min(i, h - 1) + 1):
                if binom_odd(i, j):
                    out[j] ^= 1 << (i - j)
    return out


def T_matrix(h):
    """T_h(c) in the W basis: entries GF(2)[c] ints, T[i][k] = coefficient of W_i in (K + c) W_(h-1-k)(K + c) mod K^h"""
    Ws = [W_poly(k) for k in range(h)]
    cols = [to_W(shift_times(Ws[h - 1 - k], h), h, Ws) for k in range(h)]
    return [[cols[k][i] for k in range(h)] for i in range(h)]


def reversal(h):
    return [[1 if i + j == h - 1 else 0 for j in range(h)] for i in range(h)]


def S_matrix(h):
    return CL.pmat_mul(T_matrix(h), reversal(h))


def eps_poly(h):
    return W_poly(h - 1)


def mulmod(a, b, h):
    return pmul(a, b) & ((1 << h) - 1)


def substitute_scale(Mx, sc):
    """entries are GF(2)[c] ints; return the matrix with c -> sc(c) given as a function on ints"""
    return [[sc(x) for x in r] for r in Mx]


def linearized_matrix(m):
    """L(mu) = mu S^-1 + sum_(i=1..m) mu^(2^i) N^(h - 2^(i-1)) on F[k]/(k^h), h = 2^(m-1), in the monomial basis k^0..k^(h-1);
    S g = (k + 1) g(k + 1) mod k^h, N = multiplication by k; entries GF(2)[mu] ints"""
    h = 1 << (m - 1)
    S = [[0] * h for _ in range(h)]
    for j in range(h):                     # S(k^j) = (k + 1)^(j + 1) mod k^h
        for i in range(min(j + 1, h - 1) + 1):
            if binom_odd(j + 1, i):
                S[i][j] = 1
    # invert over GF(2)
    A = [S[i][:] + [1 if i == j else 0 for j in range(h)] for i in range(h)]
    for col in range(h):
        p = next(i for i in range(col, h) if A[i][col])
        A[col], A[p] = A[p], A[col]
        for i in range(h):
            if i != col and A[i][col]:
                A[i] = [x ^ y for x, y in zip(A[i], A[col])]
    Si = [r[h:] for r in A]
    Lm = [[Si[i][j] << 1 for j in range(h)] for i in range(h)]
    for i in range(1, m + 1):
        e = h - (1 << (i - 1))
        for r in range(e, h):
            Lm[r][r - e] ^= 1 << (1 << i)
    return Lm


def trace_poly(d):
    """L_d(x) = x + x^2 + x^4 + ... + x^(2^(d-1)) as an int"""
    return sum(1 << (1 << i) for i in range(d))


def charpoly_symbolic(Mx):
    """det(z I + M) as a list [e_0 = 1, e_1, ..., e_h] of GF(2)[c] ints (coefficient of z^(h - j))"""
    return CL.charpoly_berkowitz(Mx)
