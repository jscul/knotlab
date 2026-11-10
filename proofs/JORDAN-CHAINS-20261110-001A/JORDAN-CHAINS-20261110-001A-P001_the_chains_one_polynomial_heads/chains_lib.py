"""Library for JORDAN-CHAINS-20261110-001A: the Jordan chains that one polynomial heads, on the cut-open torus at sides 2^m.

The family Z(w) = S + w^(1-n) M_(eps(w^-2 k)) on F[k]_(<h): S F = (k + 1) F(k + 1) mod k^h, M the multiplication mod k^h. Its Taylor
coefficients at w = a are Z_0 = X_b (b = sqrt(a)) and, for i >= 1, the multiplications by Omega_i(k) = sum over e of
binom(1 - n - 2e, i) a^(1 - n - 2e - i) k^e (e = 0 and h - h/2^j). Builds on KLOOSTERMAN-BOUNDS-20261110-001A's bounds_lib."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BOUNDS_LIB = ROOT / "proofs/KLOOSTERMAN-BOUNDS-20261110-001A/KLOOSTERMAN-BOUNDS-20261110-001A-P001_one_polynomial_per_eigenvalue"
sys.path.insert(0, str(BOUNDS_LIB))
import bounds_lib as BL  # noqa: E402

RL = BL.RL


def binom2(d, i):
    """binom(d, i) mod 2 for an integer d (negative allowed) and i >= 0"""
    if d >= 0:
        return 1 if i <= d and (i & ~d) == 0 else 0
    t = -d + i - 1                      # binom(-r, i) = (-1)^i binom(r + i - 1, i)
    return 1 if (i & ~t) == 0 else 0


def exponents(m):
    h, n = 1 << (m - 1), 1 << m
    return [(e, 1 - n - 2 * e) for e in [0] + [h - h // (1 << j) for j in range(1, m)]]


def taylor(F, a, m, L):
    """Omega_i for i = 0..L-1 (coefficient lists of length h)"""
    h = 1 << (m - 1)
    out = []
    for i in range(L):
        om = [0] * h
        for e, d in exponents(m):
            if binom2(d, i):
                om[e] ^= F.pw(a, (d - i) % F.q1)
        out.append(om)
    return out


def mult(om, h):
    M = np.zeros((h, h), dtype=np.int64)
    for d, c in enumerate(om):
        if c:
            idx = np.arange(h - d)
            M[idx + d, idx] ^= c
    return M


def coefficients(F, a, m, L):
    """Z_0, ..., Z_(L-1) as matrices"""
    h = 1 << (m - 1)
    S = RL.star_matrix(F, 0, m, h)
    oms = taylor(F, a, m, L)
    return [S ^ mult(oms[0], h)] + [mult(om, h) for om in oms[1:]]


def chain_exists(F, Zs, v0, l):
    """is there a Jordan chain phi_0 = v0, ..., phi_(l-1) with sum over i <= r of Z_i phi_(r-i) = 0 for r < l?"""
    h = Zs[0].shape[0]
    if l <= 1:
        return not BL.matmul(F, Zs[0], v0[:, None]).any()
    N = (l - 1) * h
    T = np.zeros((N, N), dtype=np.int64)
    rhs = np.zeros(N, dtype=np.int64)
    for r in range(1, l):
        T[(r - 1) * h:r * h, (r - 1) * h:r * h] = Zs[0]
        for i in range(1, r):
            T[(r - 1) * h:r * h, (r - 1 - i) * h:(r - i) * h] ^= Zs[i]
        rhs[(r - 1) * h:r * h] = BL.matmul(F, Zs[r], v0[:, None])[:, 0]
    return F.rank(T) == F.rank(np.concatenate([T, rhs[:, None]], axis=1))


def partial_multiplicities(F, Zs, L):
    """the partial multiplicities (Jordan blocks) at a, from the kernels of the block Toeplitz matrices of Z_0..Z_(l-1), l <= L"""
    h = Zs[0].shape[0]
    dims = []
    for l in range(1, L + 1):
        N = l * h
        T = np.zeros((N, N), dtype=np.int64)
        for r in range(l):
            for i in range(r + 1):
                T[r * h:(r + 1) * h, (r - i) * h:(r - i + 1) * h] ^= Zs[i]
        dims.append(N - F.rank(T))
    ge = [dims[0]] + [dims[l] - dims[l - 1] for l in range(1, len(dims))]     # number of blocks of size >= l
    out = []
    for l in range(len(ge)):
        out += [l + 1] * (ge[l] - (ge[l + 1] if l + 1 < len(ge) else 0))
    return sorted(out, reverse=True)


def least_polynomial(F, X):
    """the kernel of X and its least-degree element G (trimmed), or (kernel, None)"""
    ker = BL.nullspace(F, X)
    if not ker:
        return ker, None
    degs, ech = BL.top_degrees(F, ker)
    return ker, ech[-1][:degs[0] + 1]


def cyclic_basis(G, h):
    fam, v = [], G.copy()
    while len(v) - 1 < h:
        fam.append(np.concatenate([v, np.zeros(h - len(v), dtype=np.int64)]))
        v = BL.times_Y(v)
    return fam


def chain_lemma_at(F, a, m):
    """for one a: k, the lengths 2k - 1 - 4j, whether each G Y^j heads a chain of exactly that length, and the partial multiplicities"""
    h = 1 << (m - 1)
    b = F.sqrt(a)
    ker, G = least_polynomial(F, RL.star_matrix(F, b, m, h))
    if G is None:
        return {"k": 0, "ok": True, "blocks": []}
    k = h - (len(G) - 1)
    L = 2 * k + 1
    Zs = coefficients(F, a, m, L + 1)
    lengths = [2 * k - 1 - 4 * j for j in range((k + 1) // 2)]
    fam = cyclic_basis(G, h)
    heads = [chain_exists(F, Zs, v, l) and not chain_exists(F, Zs, v, l + 1) for v, l in zip(fam, lengths)]
    blocks = partial_multiplicities(F, Zs, L)
    return {"k": k, "lengths": lengths, "heads exactly": heads, "blocks": blocks,
            "ok": len(fam) == len(lengths) and all(heads) and blocks == lengths}
