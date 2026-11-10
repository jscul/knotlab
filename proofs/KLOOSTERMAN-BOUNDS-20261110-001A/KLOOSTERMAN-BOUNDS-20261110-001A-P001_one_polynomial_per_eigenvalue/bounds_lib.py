"""Library for KLOOSTERMAN-BOUNDS-20261110-001A: the kernels of the cut-open torus at sides n = 2^m, one polynomial per eigenvalue.

Builds on LINEAR-ROOTS-20261109-001A's roots_lib (GF(2^K) by log tables, Omega_b, the matrix of
X_b: F -> (k + 1) F(k + 1) + Omega_b(k) F(k) mod k^h). Polynomials are coefficient lists over GF(2^K), lowest degree first."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROOTS_LIB = ROOT / "proofs/LINEAR-ROOTS-20261109-001A/LINEAR-ROOTS-20261109-001A-P001_kloosterman_multiplicities"
sys.path.insert(0, str(ROOTS_LIB))
import roots_lib as RL  # noqa: E402

D = RL.D


def gram(h):
    """Gram matrix of <F, G> = sum over j < h of [k^j](F G) in the monomial basis: [i + j <= h - 1]"""
    return np.array([[1 if i + j <= h - 1 else 0 for j in range(h)] for i in range(h)], dtype=np.int64)


def matmul(F, A, B):
    """product of two matrices over GF(2^K) (numpy int arrays)"""
    A, B = np.asarray(A, dtype=np.int64), np.asarray(B, dtype=np.int64)
    out = np.zeros((A.shape[0], B.shape[1]), dtype=np.int64)
    for l in range(A.shape[1]):
        col, row = A[:, l], B[l, :]
        if col.any() and row.any():
            out ^= F.mul_np(col[:, None], row[None, :])
    return out


def nullspace(F, M):
    """basis of the right kernel of M over GF(2^K), as a list of numpy vectors"""
    A = np.array(M, dtype=np.int64)
    rows, cols = A.shape
    piv, r = [], 0
    for c in range(cols):
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0:
            continue
        p = r + nz[0]
        if p != r:
            A[[r, p]] = A[[p, r]]
        A[r] = F.mul_np(np.full(cols, F.inv(int(A[r, c])), dtype=np.int64), A[r])
        f = A[:, c].copy()
        f[r] = 0
        idx = np.nonzero(f)[0]
        if len(idx):
            A[idx] ^= F.mul_np(f[idx][:, None], A[r][None, :])
        piv.append(c)
        r += 1
        if r == rows:
            break
    free = [c for c in range(cols) if c not in set(piv)]
    basis = []
    for fc in free:
        v = np.zeros(cols, dtype=np.int64)
        v[fc] = 1
        for i, pc in enumerate(piv):
            v[pc] = A[i, fc]
        basis.append(v)
    return basis


def top_degrees(F, basis):
    """the set of degrees of the nonzero elements of span(basis): echelon form from the top"""
    rows = [b.copy() for b in basis]
    degs, out = [], []
    h = len(rows[0]) if rows else 0
    for col in range(h - 1, -1, -1):
        idx = next((i for i, r in enumerate(rows) if r[col]), None)
        if idx is None:
            continue
        p = rows.pop(idx)
        p = F.mul_np(np.full(h, F.inv(int(p[col])), dtype=np.int64), p)
        for i, r in enumerate(rows):
            if r[col]:
                rows[i] = r ^ F.mul_np(np.full(h, int(r[col]), dtype=np.int64), p)
        degs.append(col)
        out.append(p)
    return sorted(degs), out


def low_degrees(F, basis):
    """the set of valuations (lowest degrees) of the nonzero elements of span(basis)"""
    rows = [b.copy() for b in basis]
    vals = []
    h = len(rows[0]) if rows else 0
    for col in range(h):
        idx = next((i for i, r in enumerate(rows) if r[col]), None)
        if idx is None:
            continue
        p = rows.pop(idx)
        for i, r in enumerate(rows):
            if r[col]:
                f = F.m(int(r[col]), F.inv(int(p[col])))
                rows[i] = r ^ F.mul_np(np.full(h, f, dtype=np.int64), p)
        vals.append(col)
    return sorted(vals)


def times_Y(v):
    """multiply a coefficient vector by Y = k^2 + k (over GF(2^K), characteristic 2)"""
    out = np.zeros(len(v) + 2, dtype=np.int64)
    out[1:len(v) + 1] ^= v
    out[2:len(v) + 2] ^= v
    return out


def shift_poly(v):
    """coefficients of F(k + 1) from those of F(k) (Lucas: binomials mod 2)"""
    out = np.zeros(len(v), dtype=np.int64)
    for j, c in enumerate(v):
        if c:
            for i in range(j + 1):
                if D.binom_odd(j, i):
                    out[i] ^= int(c)
    return out


def poly_mul(F, a, b):
    out = np.zeros(len(a) + len(b) - 1, dtype=np.int64)
    for i, x in enumerate(a):
        if x:
            out[i:i + len(b)] ^= F.mul_np(np.full(len(b), int(x), dtype=np.int64), np.asarray(b, dtype=np.int64))
    return out


def k_index(K):
    return (abs(K - 1) - 1) // 2


# ---------- the Pade form (Theorem 4)
def _trunc(p, d):
    return (list(p) + [0] * d)[:d]


def _pmul(F, a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    out[i + j] ^= F.m(x, y)
    return out


def _inv_series(F, a, d):
    out = [0] * d
    i0 = F.inv(a[0])
    out[0] = i0
    for i in range(1, d):
        s = 0
        for j in range(1, min(i, len(a) - 1) + 1):
            if a[j]:
                s ^= F.m(a[j], out[i - j])
        out[i] = F.m(s, i0)
    return out


def _shift(p):
    out = [0] * len(p)
    for j, c in enumerate(p):
        if c:
            for i in range(j + 1):
                if D.binom_odd(j, i):
                    out[i] ^= c
    return out


def u_hat(F, b, m, h):
    """the element U of B = F[k]/(k^h (k + 1)^h) with U = Omega_b(k)/(k + 1) mod k^h and U = k/Omega_b(k + 1) mod (k + 1)^h,
    as (U_0, U_1) with U = U_0(Y) + k U_1(Y), Y = k^2 + k, deg U_0, U_1 < h"""
    om = RL.omega(F, b, m, h)
    u0 = _trunc(_pmul(F, om, _inv_series(F, [1, 1], h)), h)
    u1 = _shift(_trunc(_pmul(F, [1, 1], _inv_series(F, om, h)), h))     # in j = k + 1: (j + 1)/Omega_b(j), then j -> k + 1
    diff = [x ^ y for x, y in zip(_trunc(u1, 2 * h), _trunc(u0, 2 * h))]
    red = _shift(_trunc(_shift(diff), h))                                 # (u1 - u0) mod (k + 1)^h
    P = _trunc(u0, 2 * h)
    for i, c in enumerate(red):                                           # k^h = 1 mod (k + 1)^h
        if c:
            P[i + h] ^= c
    A, C = [0] * h, [0] * h
    Ypow = [[1]]
    for _ in range(h):
        Ypow.append(_pmul(F, Ypow[-1], [0, 1, 1]))
    for deg in range(2 * h - 1, -1, -1):
        c = P[deg]
        if not c:
            continue
        j, odd = divmod(deg, 2)
        term = ([0] + Ypow[j]) if odd else Ypow[j]
        (C if odd else A)[j] ^= c
        for i, x in enumerate(term):
            if x:
                P[i] ^= F.m(c, x)
    assert not any(P)
    return A, C


def pade_series(F, b, m, h):
    """psi_b = (1 + U_0)/(1 + Y U_1) mod Y^h"""
    A, C = u_hat(F, b, m, h)
    num = [1 ^ A[0]] + A[1:]
    den = [1] + C[:h - 1]
    return _trunc(_pmul(F, num, _inv_series(F, den, h)), h)


def pade_toeplitz(psi, h):
    """the (h/2) x (h/2) matrix T[j][i] = psi_(h/2 + j - i): A -> coefficients of Y^(h/2..h-1) in psi A"""
    N = h // 2
    return np.array([[psi[N + j - i] for i in range(N)] for j in range(N)], dtype=np.int64)
