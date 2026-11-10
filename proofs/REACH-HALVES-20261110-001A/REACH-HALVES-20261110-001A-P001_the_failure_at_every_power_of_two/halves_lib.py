"""Library for REACH-HALVES-20261110-001A: the cut-open torus walk on rectangles, the conveyor grid and GF(2^r) arithmetic.

Doubled coordinates of FULL-REACH-PROOF-20261108-001A: contacts are points (X, Y) with X + Y odd; an h (X odd) reads (X - 1, Y - 1)
and (X + 1, Y + 1), a v (X even) reads (X + 1, Y - 1) and (X - 1, Y + 1); on a rectangle [0, NX] x [0, NY] reads leaving it die.
Vectors are Python ints over the full grid (bit X (NY + 1) + Y); x -> x A is the row action (walk forward)."""
from __future__ import annotations


class Rect:
    def __init__(s, NX, NY):
        s.NX, s.NY = NX, NY
        W = s.W = NY + 1
        H = V = Y0 = YN = X0 = XN = 0
        for X in range(NX + 1):
            for Y in range(NY + 1):
                b = 1 << (X * W + Y)
                if (X + Y) % 2:
                    if X % 2:
                        H |= b
                    else:
                        V |= b
                if Y >= 1:
                    Y0 |= b
                if Y <= NY - 1:
                    YN |= b
                if X >= 1:
                    X0 |= b
                if X <= NX - 1:
                    XN |= b
        s.H, s.V = H, V
        s.hm, s.hp = H & Y0 & X0, H & YN & XN
        s.vp, s.vm = V & XN & Y0, V & X0 & YN
        s.contacts = [(X, Y) for X in range(NX + 1) for Y in range(NY + 1) if (X + Y) % 2]

    def idx(s, X, Y):
        return X * s.W + Y

    def inside(s, X, Y):
        return 0 <= X <= s.NX and 0 <= Y <= s.NY

    def step(s, x):
        W = s.W
        return ((x & s.hm) >> (W + 1)) ^ ((x & s.hp) << (W + 1)) ^ ((x & s.vp) << (W - 1)) ^ ((x & s.vm) >> (W - 1))

    def series(s, start, target, K):
        """bit k = A^k[start, target], k < K"""
        x, i, out = 1 << s.idx(*start), s.idx(*target), 0
        for k in range(K):
            if (x >> i) & 1:
                out |= 1 << k
            x = s.step(x)
        return out


def box(n):
    return Rect(2 * n - 2, 2 * n - 2)


def reads(X, Y):
    return [(X - 1, Y - 1), (X + 1, Y + 1)] if X % 2 else [(X + 1, Y - 1), (X - 1, Y + 1)]


class Conveyor:
    """the grid [0, n - 2] x [0, n - 1]: moves to 4-neighbours, but none leftwards on row 0 and none rightwards on row n - 1"""
    def __init__(s, n):
        s.n, s.I, s.J = n, n - 1, n

    def idx(s, i, j):
        return i * s.J + j

    def nbrs(s, i, j):
        out = []
        if j >= 1:
            out.append((i, j - 1))
        if j <= s.J - 2:
            out.append((i, j + 1))
        if i <= s.I - 2 and j <= s.J - 2:
            out.append((i + 1, j))
        if i >= 1 and j >= 1:
            out.append((i - 1, j))
        return out

    def step(s, x):
        out = 0
        for i in range(s.I):
            for j in range(s.J):
                if (x >> s.idx(i, j)) & 1:
                    for (a, b) in s.nbrs(i, j):
                        out ^= 1 << s.idx(a, b)
        return out


# ---------- GF(2^r)
PRIM = {4: 0b10011, 5: 0b100101, 6: 0b1000011, 8: 0b100011101, 10: 0b10000001001, 12: 0b1000001010011}


class GF:
    def __init__(s, r):
        s.r, s.q, s.poly = r, 1 << r, PRIM[r]
        s.exp, s.log = [0] * (2 * s.q), [0] * s.q
        x = 1
        for i in range(s.q - 1):
            s.exp[i], s.log[x] = x, i
            x <<= 1
            if x & s.q:
                x ^= s.poly
        for i in range(s.q - 1, 2 * s.q):
            s.exp[i] = s.exp[i - (s.q - 1)]

    def mul(s, a, b):
        return 0 if a == 0 or b == 0 else s.exp[s.log[a] + s.log[b]]

    def inv(s, a):
        return s.exp[(s.q - 1 - s.log[a]) % (s.q - 1)]


def det(F, M):
    M = [r[:] for r in M]
    d, D = len(M), 1
    for c in range(d):
        p = next((r for r in range(c, d) if M[r][c]), None)
        if p is None:
            return 0
        M[c], M[p] = M[p], M[c]
        D = F.mul(D, M[c][c])
        inv = F.inv(M[c][c])
        for r in range(c + 1, d):
            if M[r][c]:
                f = F.mul(M[r][c], inv)
                M[r] = [a ^ F.mul(f, b) for a, b in zip(M[r], M[c])]
    return D
