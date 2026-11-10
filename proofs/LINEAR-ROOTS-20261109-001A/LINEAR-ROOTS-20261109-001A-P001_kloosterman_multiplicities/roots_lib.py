"""Library for LINEAR-ROOTS-20261109-001A: Kloosterman multiplicities of the cut-open torus at sides n = 2^m.

GF(2^K) elements are ints (bit i = coefficient of the generator's i-th power), multiplied through log tables built on the least
primitive polynomial (collapse_lib.field). q = 2n, h = n/2. The kernel of I + C_s(a) is computed in the normalized form of Theorem 2:
F in F[k]/(k^h) with (k + 1) F(k + 1) = Omega_b(k) F(k) mod k^h, b = sqrt(a), Omega_b(k) = b + sum_(i=2..m) b^(2^i) k^(h - 2^(i-2))."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DIGITS_LIB = ROOT / "proofs/RETURN-DIGITS-20261109-001A/RETURN-DIGITS-20261109-001A-P001_a_one_dimensional_return_map"
sys.path.insert(0, str(DIGITS_LIB))
import digits_lib as D  # noqa: E402

CL = D.CL


class GF:
    """GF(2^K) by log tables, with vectorized products on numpy arrays"""

    def __init__(self, K):
        self.f, mul = CL.field(K)
        self.K = K
        self.q1 = (1 << K) - 1                 # order of the multiplicative group
        self.exp = [1]
        for _ in range(self.q1 - 1):
            self.exp.append(mul(self.exp[-1], 2))
        self.log = {v: i for i, v in enumerate(self.exp)}
        self.exp_np = np.array(self.exp * 3, dtype=np.int64)
        self.log_np = np.zeros(self.q1 + 1, dtype=np.int64)
        for v, i in self.log.items():
            self.log_np[v] = i

    def m(self, a, b):
        return 0 if a == 0 or b == 0 else self.exp[(self.log[a] + self.log[b]) % self.q1]

    def inv(self, a):
        return self.exp[(-self.log[a]) % self.q1]

    def pw(self, a, e):
        if e == 0:
            return 1
        return 0 if a == 0 else self.exp[(self.log[a] * e) % self.q1]

    def sqrt(self, a):
        return self.pw(a, (self.q1 + 1) // 2)

    def tr(self, x):
        t, y = 0, x
        for _ in range(self.K):
            t ^= y
            y = self.m(y, y)
        return t

    def kloosterman(self, a):
        """K(a) = sum over x in GF(q) of (-1)^Tr(x + a/x), 1/0 = 0 (the term x = 0 is 1)"""
        s = 1
        for x in self.exp:
            s += -1 if self.tr(x ^ self.m(a, self.inv(x))) else 1
        return s

    def ev(self, coeffs, y):
        v, p = 0, 1
        for c in coeffs:
            if c:
                v ^= self.m(c, p)
            p = self.m(p, y)
        return v

    def mul_np(self, a, b):
        r = self.exp_np[self.log_np[a] + self.log_np[b]]
        return np.where((a == 0) | (b == 0), 0, r)

    def rank(self, M):
        """rank over GF(2^K) by Gauss-Jordan elimination on a numpy array"""
        A = np.array(M, dtype=np.int64)
        rows, cols = A.shape
        r = 0
        for c in range(cols):
            nz = np.nonzero(A[r:, c])[0]
            if len(nz) == 0:
                continue
            p = r + nz[0]
            if p != r:
                A[[r, p]] = A[[p, r]]
            A[r] = self.mul_np(np.full(cols, self.inv(int(A[r, c])), dtype=np.int64), A[r])
            f = A[:, c].copy()
            f[r] = 0
            idx = np.nonzero(f)[0]
            if len(idx):
                A[idx] ^= self.mul_np(f[idx][:, None], A[r][None, :])
            r += 1
            if r == rows:
                break
        return r


def omega(F, b, m, h):
    """Omega_b(k) = b eps(b^-4 k) mod k^h for b in GF(2^(m+1)): b + sum_(i=2..m) b^(2^i) k^(h - 2^(i-2)), as a coefficient list"""
    om = [0] * h
    om[0] = b
    for i in range(2, m + 1):
        om[h - (1 << (i - 2))] ^= F.pw(b, 1 << i)
    return om


def star_matrix(F, b, m, h):
    """matrix (monomial basis k^0..k^(h-1)) of F -> (k + 1) F(k + 1) + Omega_b(k) F(k) mod k^h"""
    M = np.zeros((h, h), dtype=np.int64)
    for j in range(h):
        for i in range(min(j + 1, h - 1) + 1):
            if D.binom_odd(j + 1, i):
                M[i, j] ^= 1
    for d, coef in enumerate(omega(F, b, m, h)):
        if coef:
            idx = np.arange(h - d)
            M[idx + d, idx] ^= coef
    return M


def return_map_kernel_dim(F, a, n, T):
    """dim ker(I + C_s(a)), C_s(w) = w^(n+1) T_h(w^-2) (RETURN-DIGITS Theorem 1), T = digits_lib.T_matrix(n/2)"""
    h = n // 2
    c = F.inv(F.m(a, a))
    wn1 = F.pw(a, n + 1)
    M = np.array([[F.m(wn1, F.ev([(x >> i) & 1 for i in range(x.bit_length())], c)) ^ (1 if i == j else 0)
                   for j, x in enumerate(row)] for i, row in enumerate(T)], dtype=np.int64)
    return h - F.rank(M)


def law(K):
    """the Kloosterman law at K = K(a): (algebraic multiplicity, geometric multiplicity, Jordan blocks)"""
    s = K // 4
    if s > 0:
        blocks = [4 * j + 1 for j in range(s)]
    else:
        blocks = [4 * j + 3 for j in range(-s)]
    return K * (K - 2) // 8, abs(s), sorted(blocks, reverse=True)


def k_index(K):
    """k with k(k + 1)/2 the multiplicity: |K - 1| = 2k + 1"""
    return (abs(K - 1) - 1) // 2
