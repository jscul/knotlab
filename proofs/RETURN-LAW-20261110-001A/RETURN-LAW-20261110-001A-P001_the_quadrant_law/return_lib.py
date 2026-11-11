"""Library for RETURN-LAW-20261110-001: the corner's returns on the cut-open torus walk, in the quadrant, the half-strips and the box.

Doubled coordinates of FULL-REACH-PROOF-20261108-001A, as in REACH-HALVES-20261110-001A (whose Rect this imports): contacts are the
points (X, Y) with X + Y odd, an h (X odd) reads (X - 1, Y - 1) and (X + 1, Y + 1), a v (X even) reads (X + 1, Y - 1) and
(X - 1, Y + 1), and reads leaving the region die. The corner contact is c = (0, 1).

The v-grid: the v contacts (2a, 2b + 1) with the walk A^2 between them (moves E, W, N, S, with bans; see the proof of ticket A).
GF(2)[s]/(s^T) polynomials are Python ints (bit k = coefficient of s^k); matrices are lists of rows, M[b][b'] = generating function
from b to b' (products in time order)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/REACH-HALVES-20261110-001A/REACH-HALVES-20261110-001A-P001_the_failure_at_every_power_of_two"))
from halves_lib import Rect  # noqa: E402


# ---------- series in one variable over GF(2) ----------

def catalan2(K):
    """C(z) mod 2 = sum_j z^(2^j - 1), as a bit mask below z^K"""
    out, j = 0, 1
    while j - 1 < K:
        out |= 1 << (j - 1)
        j *= 2
    return out


def trace_poly(n):
    """L(z) = z + z^2 + z^4 + ... + z^n (n a power of two)"""
    out, j = 0, 1
    while j <= n:
        out |= 1 << j
        j *= 2
    return out


def pmul(a, b, K):
    r, mask = 0, (1 << K) - 1
    while b:
        if b & 1:
            r ^= a
        a = (a << 1) & mask
        b >>= 1
    return r & mask


def pinv(a, K):
    """1/a below z^K, a(0) = 1"""
    assert a & 1
    r = 1
    for k in range(1, K):
        # coefficient k of a * r must vanish
        c = 0
        for j in range(1, k + 1):
            if (a >> j) & 1 and (r >> (k - j)) & 1:
                c ^= 1
        if c:
            r |= 1 << k
    return r


def spread(a, m, K):
    """a(z^m) below z^K"""
    out, k = 0, 0
    while a >> k:
        if (a >> k) & 1 and k * m < K:
            out |= 1 << (k * m)
        k += 1
    return out


def box_law_sequence(n, K):
    """the registered box law at a power of two n: bit k = coefficient of w^k in 1/(1 + L(w^4)), i.e. 1 at k = 4j exactly
    when j mod (2n - 1) is 2^i - 1 with 2^i <= n"""
    out = 0
    for k in range(0, K, 4):
        j = (k // 4) % (2 * n - 1)
        if ((j + 1) & j) == 0 and j + 1 <= n:
            out |= 1 << k
    return out


# ---------- the walk on rectangles ----------

class FastRect:
    """the same walk as halves_lib.Rect (bit X (NY + 1) + Y, x -> xA forward), with its four masks built from column patterns in
    linear time, for rectangles of millions of contacts"""
    def __init__(s, NX, NY):
        s.NX, s.NY = NX, NY
        W = s.W = NY + 1

        def col(pred):
            return "".join("1" if pred(Y) else "0" for Y in range(NY, -1, -1))     # most significant bit first
        zero = "0" * W
        h_m = col(lambda Y: Y % 2 == 0 and Y >= 1)            # an h (X odd, Y even) with Y >= 1
        h_p = col(lambda Y: Y % 2 == 0 and Y <= NY - 1)
        v_p = col(lambda Y: Y % 2 == 1)                        # a v (X even, Y odd); Y >= 1 holds
        v_m = col(lambda Y: Y % 2 == 1 and Y <= NY - 1)

        def mask(colfun):
            return int("".join(colfun(X) for X in range(NX, -1, -1)), 2)
        s.hm = mask(lambda X: h_m if X % 2 == 1 and X >= 1 else zero)
        s.hp = mask(lambda X: h_p if X % 2 == 1 and X <= NX - 1 else zero)
        s.vp = mask(lambda X: v_p if X % 2 == 0 and X <= NX - 1 else zero)
        s.vm = mask(lambda X: v_m if X % 2 == 0 and X >= 1 else zero)

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


def corner_returns(NX, NY, K):
    """bit k = A^k[c, c] on the rectangle [0, NX] x [0, NY], k < K"""
    return FastRect(NX, NY).series((0, 1), (0, 1), K)


# ---------- polynomial matrices over GF(2)[s]/(s^T) ----------

class Ring:
    def __init__(s, T):
        s.T = T
        s.MASK = (1 << T) - 1

    def pm(s, a, b):
        r, M = 0, s.MASK
        while b:
            if b & 1:
                r ^= a
            a = (a << 1) & M
            b >>= 1
        return r

    def mm(s, A, B):
        n, m, k = len(A), len(B[0]), len(B)
        C = [[0] * m for _ in range(n)]
        for i in range(n):
            Ai, Ci = A[i], C[i]
            for l in range(k):
                a = Ai[l]
                if not a:
                    continue
                Bl = B[l]
                for j in range(m):
                    if Bl[j]:
                        Ci[j] ^= s.pm(a, Bl[j])
        return C

    @staticmethod
    def eye(n):
        return [[1 if i == j else 0 for j in range(n)] for i in range(n)]

    @staticmethod
    def add(*Ms):
        n, m = len(Ms[0]), len(Ms[0][0])
        R = [[0] * m for _ in range(n)]
        for M in Ms:
            for i in range(n):
                Ri, Mi = R[i], M[i]
                for j in range(m):
                    Ri[j] ^= Mi[j]
        return R

    def scal(s, c, M):
        return [[s.pm(c, x) for x in r] for r in M]

    def inv_unip(s, A):
        """A = I + N with N = O(s): A^-1 = sum N^k"""
        n = len(A)
        N = s.add(A, s.eye(n))
        R, P = s.eye(n), s.eye(n)
        for _ in range(s.T):
            P = s.mm(P, N)
            if not any(any(r) for r in P):
                break
            R = s.add(R, P)
        return R

    def evaluate(s, c, X):
        """sum_h c_h X^h, c a bit mask in one variable, X a matrix that is O(s)"""
        n = len(X)
        tot, P, h = [[0] * n for _ in range(n)], s.eye(n), 0
        while c >> h:
            if (c >> h) & 1:
                tot = s.add(tot, P)
            P = s.mm(P, X)
            h += 1
            if not any(any(r) for r in P):
                break
        return tot


def path(n):
    return [[1 if abs(i - j) == 1 else 0 for j in range(n)] for i in range(n)]


def lower(n):
    """D: from b to b - 1"""
    return [[1 if j == i - 1 else 0 for j in range(n)] for i in range(n)]


def raise_(n):
    """D^T: from b to b + 1"""
    return [[1 if j == i + 1 else 0 for j in range(n)] for i in range(n)]


def f_of(R, P):
    """f(P) = (I + sP)^-1 C(s^2 (I + sP)^-2) over GF(2) (the excursion operator of ticket A's Theorem 3, divided by s^2)"""
    n = len(P)
    Rinv = R.inv_unip(R.add(R.eye(n), R.scal(2, P)))
    w = R.scal(4, R.mm(Rinv, Rinv))
    x, tot = R.eye(n), R.eye(n)
    while True:
        x = R.mm(R.mm(x, x), w)       # w^(2^j - 1)
        if not any(any(r) for r in x):
            break
        tot = R.add(tot, x)
    return R.mm(Rinv, tot)


def arch_one_sided(R, rows):
    """ticket A, Theorem 3 over GF(2): R(s) = [(I + sD + s^2 f(P))^-1]_00 on the given number of rows (the half-line truncated
    at T rows stands for the quadrant: no walk below s^T reaches row T)"""
    P, D = path(rows), lower(rows)
    E = R.inv_unip(R.add(R.eye(rows), R.scal(2, D), R.scal(4, f_of(R, P))))
    return E


def first_passage(R, n):
    """N_LL(x), N_LR(x) as bit masks below x^T: walks on the column path [0, n - 1] from one end to the same end / the other end
    that stay strictly inside in between (ticket C, Theorem 7)"""
    if n == 2:
        return 0, 0b10
    m = n - 2
    G = Ring(R.T).inv_unip(Ring(R.T).add(Ring.eye(m), Ring(R.T).scal(2, path(m))))
    return (G[0][0] << 2) & R.MASK, (G[0][m - 1] << 2) & R.MASK


def arch_two_sided(R, n, NLL=None, NLR=None):
    """ticket C, Theorem 7 over GF(2): the block operator K_n on V_L + V_R (V = the n - 1 rows); R(s) = [K_n^-1]_00"""
    L = n - 1
    Pv, D, Dt = path(L), lower(L), raise_(L)
    IsP = R.add(R.eye(L), R.scal(2, Pv))
    Pi = R.scal(2, R.inv_unip(IsP))
    if NLL is None:
        NLL, NLR = first_passage(R, n)
    SLL = R.mm(IsP, R.evaluate(NLL, Pi))
    SLR = R.mm(IsP, R.evaluate(NLR, Pi))
    A = R.add(R.eye(L), R.scal(2, D), SLL)
    B = R.add(R.eye(L), R.scal(2, Dt), SLL)
    K = [A[i] + SLR[i] for i in range(L)] + [SLR[i] + B[i] for i in range(L)]
    return R.inv_unip(K), K


# ---------- determinants of paths over GF(2) ----------

def det_path(k):
    """det(I + x P_k) over GF(2) as a bit mask in x: D_0 = 1, D_1 = 1, D_k = D_(k-1) + x^2 D_(k-2)"""
    a, b = 1, 1
    if k == 0:
        return 1
    for _ in range(k - 1):
        a, b = b, b ^ (a << 2)
    return b


def det_looped_path(k):
    """det(I + x P_k^o), P_k^o the path on k sites with a loop at one end: E_1 = 1 + x, E_k = E_(k-1) + x^2 E_(k-2), E_0 = 1"""
    a, b = 1, 0b11
    if k == 0:
        return 1
    for _ in range(k - 1):
        a, b = b, b ^ (a << 2)
    return b


def truncated_catalan(m):
    """C_m(x) = sum_{j <= m} x^(2^j - 1)"""
    return sum(1 << (2 ** j - 1) for j in range(m + 1))
