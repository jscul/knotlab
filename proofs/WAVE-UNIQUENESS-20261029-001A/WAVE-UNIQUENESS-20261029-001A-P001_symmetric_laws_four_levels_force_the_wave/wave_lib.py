"""Laws symmetric in the two non-base corners on the level-k Sierpinski gaskets (WAVE-UNIQUENESS-20261029-001A).

A law is w(a, b, c) = f(a, b + c): six weights f = (f00, f01, f02, f10, f11, f12).  SG_k has the up triangles T(i, j) = ((i, j), (i+1, j),
(i, j+1)) for i + j <= k - 1, roles a, b, c in that order, corners A = (0, 0), B = (k, 0), C = (0, k).  The corner relation R_k is the sum
over every other vertex of the product of the copies; w is exact at level k when R_k is a nonzero multiple of w.

Two-sector laws: w = u1 (x) v1 (x) v1 + u2 (x) v2 (x) v2 (vectors in C^2 indexed by the bit).  Summing a vertex pairs the vectors that meet
there: P_ij = <u_i, v_j> (a base corner with a b- or c-corner), G_ij = <v_i, v_j> (a b-corner with a c-corner), H_tij = sum_x u_t(x) v_i(x)
v_j(x) (all three).  When u1 is orthogonal to v2 and u2 to v1 (biorthogonal), the triangles along the two edges from A carry one sector,
and R_k = Z_k(1) u1 v1 v1 + Z_k(2) u2 v2 v2 with Z_k(s) the sum over the sectors of the other triangles."""
import itertools
import sympy as sp

P = sp.symbols("f00 f01 f02 f10 f11 f12")
CORNERS6 = [(0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 1)]   # (x_A, x_B, x_C) with x_B <= x_C, in the order of f


def gasket(k):
    V = [(i, j) for i in range(k + 1) for j in range(k + 1 - i)]
    tris = [((i, j), (i + 1, j), (i, j + 1)) for i in range(k) for j in range(k - i)]
    return V, tris, [(0, 0), (k, 0), (0, k)]


def relation(k, weights=P):
    """the corner relation of the law f(a, b + c) at level k as six polynomials (brute force over the summed vertices)"""
    V, tris, corners = gasket(k)
    internal = [v for v in V if v not in corners]
    out = []
    for cv in CORNERS6:
        tot = 0
        for bits in itertools.product((0, 1), repeat=len(internal)):
            val = dict(zip(internal, bits))
            val.update(zip(corners, cv))
            term = 1
            for a, b, c in tris:
                term *= weights[3 * val[a] + val[b] + val[c]]
            tot += term
        out.append(sp.expand(tot))
    return out


def two_sector(u1, v1, u2, v2):
    """the six weights of u1 v1 v1 + u2 v2 v2"""
    return [u1[a] * v1[b] * v1[c] + u2[a] * v2[b] * v2[c] for a, b, c in CORNERS6]


def J(v):
    return (-v[1], v[0])


def dot(x, y):
    return x[0] * y[0] + x[1] * y[1]


def sector_Z(k, u, v, s0):
    """Z_k(s0) for a biorthogonal two-sector law: u, v dicts sector -> 2-vector; triangles with i = 0 or j = 0 carry s0, the others are summed"""
    V, tris, corners = gasket(k)
    free = [(i, j) for i in range(1, k) for j in range(1, k - i)]
    summed = [x for x in V if x not in corners]
    tot = 0
    for taus in itertools.product((1, 2), repeat=len(free)):
        sec = {(i, j): s0 for i in range(k) for j in range(k - i)}
        sec.update(zip(free, taus))
        term = 1
        for (i, j) in summed:
            vecs = []
            if i + j <= k - 1:
                vecs.append(u[sec[(i, j)]])                 # base corner of T(i, j)
            if i >= 1:
                vecs.append(v[sec[(i - 1, j)]])             # b-corner of T(i-1, j)
            if j >= 1:
                vecs.append(v[sec[(i, j - 1)]])             # c-corner of T(i, j-1)
            fac = 0
            for x in (0, 1):
                pr = 1
                for vec in vecs:
                    pr *= vec[x]
                fac += pr
            term *= fac
        tot += term
    return tot


def generic(p, q, A, B):
    """the biorthogonal generic law with v1 = (1, p), v2 = (1, q), u1 = A J v2, u2 = B J v1, as (u, v) dicts"""
    v = {1: (1, p), 2: (1, q)}
    u = {1: tuple(A * x for x in J(v[2])), 2: tuple(B * x for x in J(v[1]))}
    return u, v


def wave_weights(y):
    """the standing wave (-1)^a U_(E-1)(y/2) as six weights: E = 3, 1, -1 for a = 0 and 1, -1, -3 for a = 1 (with the sign (-1)^a)"""
    g1, g3 = 1, y ** 2 - 1
    return [g3, g1, -g1, -g1, g1, g3]


def tangent(p, a0, a1, b0, b1, chart=0):
    """tangent pencil u1 v v + u2 (v e + e v): chart 0: v = (1, p), e = (0, 1); chart 1: v = (0, 1), e = (1, 0)"""
    v, e = ((1, p), (0, 1)) if chart == 0 else ((0, 1), (1, 0))
    u1, u2 = (a0, a1), (b0, b1)
    return [u1[a] * v[b] * v[c] + u2[a] * (v[b] * e[c] + e[b] * v[c]) for a, b, c in CORNERS6]


def rank_one(u0, u1, Q0, Q1, Q2):
    """w = u (x) Q with Q the symmetric matrix [[Q0, Q1], [Q1, Q2]]"""
    Q = (Q0, Q1, Q2)
    return [(u0, u1)[a] * Q[b + c] for a, b, c in CORNERS6]


def table(f):
    """the 2x2x2 table of six symmetric weights"""
    import numpy as np
    W = np.zeros((2, 2, 2), dtype=complex)
    for a, b, c in itertools.product((0, 1), repeat=3):
        W[a, b, c] = complex(f[3 * a + b + c])
    return W
