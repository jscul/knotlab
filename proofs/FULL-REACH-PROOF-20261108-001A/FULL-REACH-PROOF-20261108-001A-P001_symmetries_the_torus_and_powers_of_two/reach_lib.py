"""Library for FULL-REACH-PROOF-20261108-001A: the cut-open torus walk and the side-2n torus walk over GF(2).

Doubled coordinates (FULL-REACH-20261108-001A): the contacts of the n x n torus cut open both ways are the points (X, Y) of
[0, 2n - 2]^2 with X + Y odd; h = X odd, v = X even. An h reads (X - 1, Y - 1) and (X + 1, Y + 1), a v reads (X + 1, Y - 1) and
(X - 1, Y + 1); reads leaving the box die. A[c, d] = 1 when c reads d. Vectors and matrix rows are Python ints (bit k = point k).
GF(2) polynomials are ints too (bit i = coefficient of x^i)."""
from __future__ import annotations

import random


# ---------- GF(2) polynomials
def pdeg(a):
    return a.bit_length() - 1


def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pdivmod(a, b):
    q, db = 0, pdeg(b)
    while a and pdeg(a) >= db:
        s = pdeg(a) - db
        q ^= 1 << s
        a ^= b << s
    return q, a


def pmod(a, b):
    return pdivmod(a, b)[1]


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def plcm(a, b):
    return pdivmod(pmul(a, b), pgcd(a, b))[0]


def ppowmod(a, e, m):
    r, a = 1, pmod(a, m)
    while e:
        if e & 1:
            r = pmod(pmul(r, a), m)
        a = pmod(pmul(a, a), m)
        e >>= 1
    return r


def prev(a, n):
    """the reversal x^n a(1/x)"""
    return int(format(a, "0%db" % (n + 1))[::-1], 2)


def deriv(f):
    r, i = 0, 1
    while f >> i:
        if (f >> i) & 1 and i % 2:
            r ^= 1 << (i - 1)
        i += 1
    return r


def psqrt(f):
    r, i = 0, 0
    while f >> i:
        if (f >> i) & 1:
            r |= 1 << (i // 2)
        i += 1
    return r


def ddf(f):
    out, h, d = [], 2, 0
    while pdeg(f) > 0:
        d += 1
        if 2 * d > pdeg(f):
            out.append((pdeg(f), f))
            break
        h = pmod(pmul(h, h), f)
        g = pgcd(h ^ 2, f)
        if g != 1:
            out.append((d, g))
            f = pdivmod(f, g)[0]
            h = pmod(h, f)
    return out


def edf(f, d, rng):
    if pdeg(f) == d:
        return [f]
    while True:
        a = rng.getrandbits(pdeg(f))
        if pdeg(a) < 1:
            continue
        t = s = a
        for _ in range(d - 1):
            s = pmod(pmul(s, s), f)
            t ^= s
        g = pgcd(t, f)
        if 0 < pdeg(g) < pdeg(f):
            return edf(g, d, rng) + edf(pdivmod(f, g)[0], d, rng)


def factor(f):
    """irreducible factorization over GF(2): {irreducible: multiplicity}"""
    res, rng = {}, random.Random(1)

    def rec(f, mult):
        if pdeg(f) <= 0:
            return
        if deriv(f) == 0:
            rec(psqrt(f), 2 * mult)
            return
        sq = pdivmod(f, pgcd(f, deriv(f)))[0]
        for d, prod in ddf(sq):
            for p in edf(prod, d, rng):
                m = 0
                while True:
                    q, r = pdivmod(f, p)
                    if r:
                        break
                    f, m = q, m + 1
                res[p] = res.get(p, 0) + m * mult
        rec(f, mult)
    rec(f, 1)
    return res


# ---------- matrices as lists of int rows
def vec_mat(v, rows):
    """row vector v times the matrix"""
    r = 0
    while v:
        low = v & -v
        r ^= rows[low.bit_length() - 1]
        v ^= low
    return r


def mat_mul(A, B):
    return [vec_mat(r, B) for r in A]


def transpose(rows, n):
    cols = [0] * n
    for i, r in enumerate(rows):
        x = r
        while x:
            low = x & -x
            cols[low.bit_length() - 1] |= 1 << i
            x ^= low
    return cols


def identity(n):
    return [1 << i for i in range(n)]


def mat_pow(A, k):
    R, B = identity(len(A)), A
    while k:
        if k & 1:
            R = mat_mul(R, B)
        B = mat_mul(B, B)
        k >>= 1
    return R


def rank(rows):
    basis, r = {}, 0
    for row in rows:
        x = row
        while x:
            p = x.bit_length() - 1
            if p not in basis:
                basis[p] = x
                r += 1
                break
            x ^= basis[p]
    return r


def minpoly_vec(rows, v):
    """minimal polynomial of the row vector v under v -> v A"""
    basis, k, cur = {}, 0, v
    while True:
        x, combo = cur, 1 << k
        while x:
            p = x.bit_length() - 1
            if p not in basis:
                break
            bv, bc = basis[p]
            x ^= bv
            combo ^= bc
        if not x:
            return combo
        basis[x.bit_length() - 1] = (x, combo)
        cur = vec_mat(cur, rows)
        k += 1


def charpoly(rows, n):
    """characteristic polynomial det(xI - A) over GF(2), by reduction to upper Hessenberg form"""
    H = [[(rows[i] >> j) & 1 for j in range(n)] for i in range(n)]
    for j in range(n - 2):
        piv = next((i for i in range(j + 1, n) if H[i][j]), None)
        if piv is None:
            continue
        if piv != j + 1:
            H[piv], H[j + 1] = H[j + 1], H[piv]
            for r in H:
                r[piv], r[j + 1] = r[j + 1], r[piv]
        for i in range(j + 2, n):
            if H[i][j]:
                # row_i += row_{j+1}; then column_{j+1} += column_i (inverse similarity)
                H[i] = [a ^ b for a, b in zip(H[i], H[j + 1])]
                for r in H:
                    r[j + 1] ^= r[i]
    p = [1]
    for k in range(1, n + 1):
        pk = pmul(0b10 ^ H[k - 1][k - 1], p[k - 1])
        prod = 1
        for i in range(k - 1, 0, -1):
            prod &= H[i][i - 1]
            if prod and H[i - 1][k - 1]:
                pk ^= p[i - 1]
        p.append(pk)
    return p[n]


def poly_det(M):
    """determinant of a square matrix of GF(2)[w] polynomials (fraction-free elimination)"""
    M = [r[:] for r in M]
    n, prev_p = len(M), 1
    for k in range(n - 1):
        if M[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if M[i][k]), None)
            if sw is None:
                return 0
            M[k], M[sw] = M[sw], M[k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                q, r = pdivmod(pmul(M[i][j], M[k][k]) ^ pmul(M[i][k], M[k][j]), prev_p)
                assert r == 0
                M[i][j] = q
            M[i][k] = 0
        prev_p = M[k][k]
    return M[n - 1][n - 1]


# ---------- the cut-open torus
def points(n):
    return [(X, Y) for X in range(2 * n - 1) for Y in range(2 * n - 1) if (X + Y) % 2]


def reads(n, p):
    X, Y = p
    steps = [(-1, -1), (1, 1)] if X % 2 else [(1, -1), (-1, 1)]
    return [(X + dx, Y + dy) for dx, dy in steps if 0 <= X + dx <= 2 * n - 2 and 0 <= Y + dy <= 2 * n - 2]


def ring(n, i, j):
    cand = [(2 * i + 1, 2 * j), (2 * i - 1, 2 * j), (2 * i, 2 * j + 1), (2 * i, 2 * j - 1)]
    return [q for q in cand if 0 <= q[0] <= 2 * n - 2 and 0 <= q[1] <= 2 * n - 2]


def box(n):
    P = points(n)
    ix = {p: k for k, p in enumerate(P)}
    return P, ix, [sum(1 << ix[q] for q in reads(n, p)) for p in P]


def perm_matrix(P, ix, f):
    """rows of the permutation matrix (Pi)[c, f(c)] = 1"""
    return [1 << ix[f(p)] for p in P]


def layer(p):
    X, Y = p
    return {(0, 0): 0, (1, 0): 1, (1, 1): 2, (0, 1): 3}[((X + Y - 1) // 2 % 2, (X - Y - 1) // 2 % 2)]


def layer_Q(n):
    """Q = A^4 restricted to layer 0, as rows over the layer's own index"""
    P, ix, rows = box(n)
    L0 = [k for k, p in enumerate(P) if layer(p) == 0]
    pos = {k: a for a, k in enumerate(L0)}
    Q = []
    for k in L0:
        v = 1 << k
        for _ in range(4):
            v = vec_mat(v, rows)
        r, x = 0, v
        while x:
            low = x & -x
            r |= 1 << pos[low.bit_length() - 1]
            x ^= low
        Q.append(r)
    return Q


# ---------- the side-2n torus and its cut lines
def torus(n):
    L = 2 * n
    T = [(X, Y) for X in range(L) for Y in range(L) if (X + Y) % 2]
    ix = {p: k for k, p in enumerate(T)}

    def rd(p):
        X, Y = p
        st = [(-1, -1), (1, 1)] if X % 2 else [(1, -1), (-1, 1)]
        return [((X + a) % L, (Y + b) % L) for a, b in st]
    return T, ix, [sum(1 << ix[q] for q in rd(p)) for p in T]


def cut_lines(n):
    L = 2 * n
    return [(L - 1, Y) for Y in range(0, L, 2)], [(X, L - 1) for X in range(0, L, 2)]


def mat_vec(rows, v):
    r = 0
    for i, row in enumerate(rows):
        if bin(row & v).count("1") & 1:
            r |= 1 << i
    return r


def resolvent_block(rows, ix, S, kmax):
    """[(I - wM)^-1]_{S,S} truncated at w^kmax: entry (a, b) = sum_k w^k (M^k)[a, b] (a reads b at lag k)"""
    R = [[0] * len(S) for _ in S]
    for b, sb in enumerate(S):
        v = 1 << ix[sb]
        for k in range(kmax):
            for a, sa in enumerate(S):
                if (v >> ix[sa]) & 1:
                    R[a][b] ^= 1 << k
            v = mat_vec(rows, v)
            if not v:
                break
    return R


# ---------- the two-step walk on h and the transfer identity
def chebyshev(k, y_mat, size):
    """u_k(y) for the matrix y with GF(2)[x] entries: u_{-1} = 0, u_0 = I, u_{k+1} = y u_k + u_{k-1}"""
    I = [[1 if i == j else 0 for j in range(size)] for i in range(size)]
    Z = [[0] * size for _ in range(size)]
    us = [Z, I]
    for _ in range(k):
        us.append(madd(mmul(y_mat, us[-1]), us[-2]))
    return us[1:]  # u_0 .. u_k


def mmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    out = [[0] * p for _ in range(n)]
    for i in range(n):
        for t in range(m):
            if A[i][t]:
                a = A[i][t]
                for j in range(p):
                    if B[t][j]:
                        out[i][j] ^= pmul(a, B[t][j])
    return out


def madd(A, B):
    return [[a ^ b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def h_grid_walk(n):
    """M_h = A^2 on h(i, j), i in [0, n-2], j in [0, n-1], as rows over that grid"""
    pts = [(i, j) for j in range(n) for i in range(n - 1)]
    ix = {p: k for k, p in enumerate(pts)}
    rows = []
    for (i, j) in pts:
        r = 0
        for (a, b) in ((i, j - 1), (i, j + 1)):
            if 0 <= b < n:
                r ^= 1 << ix[(a, b)]
        if j >= 1 and i >= 1:
            r ^= 1 << ix[(i - 1, j)]
        if j <= n - 2 and i <= n - 3:
            r ^= 1 << ix[(i + 1, j)]
        rows.append(r)
    return pts, ix, rows
