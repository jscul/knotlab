"""Library for CODIST-THREE-20261110-001A: the second vector of the reduction on the pair of solutions (sides 2^m).

G = Q(Y) + k P(Y) (G monic, the least polynomial at a), the Bezout cofactors P Q'' + Q P'' = 1, N = G(k) G(k + 1) in F[Y], L(Y) = Y + Y^2 +
... + Y^(h/2). Builds on LEADING-FORM-20261110-001A's wronski_lib."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LEADING-FORM-20261110-001A/LEADING-FORM-20261110-001A-P001_the_reductions_vectors_order_by_order"))
import wronski_lib as WL  # noqa: E402

OL, CH, BL, RL = WL.OL, WL.CH, WL.BL, WL.RL


def ydivmod(F, num, den):
    num = [int(x) for x in num]
    den = [int(x) for x in den]
    while den and den[-1] == 0:
        den.pop()
    while num and num[-1] == 0:
        num.pop()
    if len(num) < len(den):
        return [0], num or [0]
    q = [0] * (len(num) - len(den) + 1)
    inv = F.inv(den[-1])
    for i in range(len(num) - len(den), -1, -1):
        c = F.m(num[i + len(den) - 1], inv)
        q[i] = c
        if c:
            for j, d in enumerate(den):
                if d:
                    num[i + j] ^= F.m(c, d)
    return q, num[:len(den) - 1] or [0]


def ymul(F, a, b):
    return [int(x) for x in BL.poly_mul(F, np.array(a, dtype=np.int64), np.array(b, dtype=np.int64))]


def yadd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0) for i in range(n)]


def bezout(F, P, Q):
    """(Q'', P'') with P Q'' + Q P'' = 1 (extended Euclid); fails if gcd(P, Q) is not constant"""
    r0, r1 = list(Q), list(P)
    s0, s1 = [0], [1]
    t0, t1 = [1], [0]
    while any(r1):
        q, r = ydivmod(F, r0, r1)
        r0, r1 = r1, r
        s0, s1 = s1, yadd(s0, ymul(F, q, s1))
        t0, t1 = t1, yadd(t0, ymul(F, q, t1))
    g = list(r0)
    while g and g[-1] == 0:
        g.pop()
    if len(g) != 1:
        raise ValueError("gcd(P, Q) not constant")
    ci = F.inv(g[0])
    return [F.m(ci, x) for x in s0], [F.m(ci, x) for x in t0]


def to_k(F, p, n):
    """a polynomial in Y as k-coefficients (length n)"""
    out = np.zeros(n, dtype=np.int64)
    Yp = np.zeros(n, dtype=np.int64)
    Yp[0] = 1
    for c in p:
        if c:
            out ^= F.mul_np(np.full(n, int(c), dtype=np.int64), Yp)
        nx = np.zeros(n, dtype=np.int64)
        nx[1:] ^= Yp[:-1]
        nx[2:] ^= Yp[:-2]
        Yp = nx
    return out


def components(F, G, h):
    """(Q, P) with G = Q(Y) + k P(Y)"""
    g = WL.pad(G, h)
    P = [int(x) for x in WL.to_Y_exact(F, WL.wronskian(F, g, np.concatenate([[1], np.zeros(h - 1, dtype=np.int64)])))]
    Pk = to_k(F, P, 2 * h)
    kP = np.concatenate([[0], Pk[:-1]])
    Q = [int(x) for x in WL.to_Y_exact(F, WL.pad(g, 2 * h) ^ kP)]
    return Q, P


def L_poly(h):
    Ly = np.zeros(h, dtype=np.int64)
    t = 1
    while t <= h // 2:
        Ly[t] ^= 1
        t *= 2
    return Ly


def canonical_second_vector(F, G, h, Wx, Q, P, Qpp):
    """psi_hat = R + k (W + P R)/Q, R = (W Q'') mod Q; returns k-coefficients (length h) or raises"""
    _, R = ydivmod(F, ymul(F, Wx, Qpp), Q)
    Chat, rem = ydivmod(F, yadd(list(Wx), ymul(F, P, R)), Q)
    if any(rem):
        raise ValueError("C not a polynomial")
    v = to_k(F, R, 2 * h) ^ np.concatenate([[0], to_k(F, Chat, 2 * h)[:-1]])
    if v[h:].any():
        raise ValueError("degree >= h")
    return v[:h]
