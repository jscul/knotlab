"""Library for CONE-COLLAPSE-20261109-001A: the cut-open torus walk, its quarter-turn cone, and the return map of the cut line.

Doubled coordinates (FULL-REACH-20261108-001A): the contacts of the n x n torus of rule-60 rings cut open both ways are the points
(X, Y) of [0, N]^2, N = 2n - 2, with X + Y odd; h = X odd, v = X even. An h reads (X - 1, Y - 1) and (X + 1, Y + 1), a v reads
(X + 1, Y - 1) and (X - 1, Y + 1); reads leaving the box die. A[c, d] = 1 when c reads d. The uncut walk M lives on the side-2n torus,
coordinates mod 2n, and the box is the torus without its cut lines C1 (X = 2n - 1, Y even) and C2 (Y = 2n - 1, X even).
GF(2)[w] polynomials are Python ints (bit i = coefficient of w^i); GF(2) matrices are numpy arrays (float64 holding 0 and 1, so
that products go through BLAS exactly and are reduced mod 2)."""
from __future__ import annotations

import random

import numpy as np


# ---------- GF(2)[w]
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


def prev(a, d):
    """w^d a(1/w)"""
    return sum(((a >> i) & 1) << (d - i) for i in range(d + 1))


def val(a):
    """w-adic valuation (lowest exponent)"""
    return (a & -a).bit_length() - 1


def deriv(f):
    return sum(((f >> i) & 1) << (i - 1) for i in range(1, f.bit_length()) if i % 2)


def psqrt(f):
    return sum(((f >> i) & 1) << (i // 2) for i in range(0, f.bit_length(), 2))


def psquare(f):
    return sum(((f >> i) & 1) << (2 * i) for i in range(f.bit_length()))


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


def pstr(a):
    if a == 0:
        return "0"
    t = ["w^%d" % i if i > 1 else ("w" if i == 1 else "1") for i in range(pdeg(a), -1, -1) if (a >> i) & 1]
    return " + ".join(t)


# ---------- polynomial matrices (lists of lists of ints)
def pmat_mul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    out = [[0] * m for _ in range(n)]
    for i in range(n):
        for t in range(k):
            a = A[i][t]
            if a:
                for j in range(m):
                    if B[t][j]:
                        out[i][j] ^= pmul(a, B[t][j])
    return out


def pmat_plus_identity(M):
    return [[x ^ (1 if i == j else 0) for j, x in enumerate(r)] for i, r in enumerate(M)]


def bareiss_det(Mx):
    M = [r[:] for r in Mx]
    n = len(M)
    prev_p = 1
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


def charpoly_berkowitz(M):
    """det(z I + M) for a polynomial matrix M, as the list of coefficients of z^h, z^(h-1), ..., z^0 (each a GF(2)[w] int)"""
    n = len(M)

    def xsum(lst):
        r = 0
        for x in lst:
            r ^= x
        return r
    vect = [1, M[0][0]]
    for r in range(1, n):
        A = [row[:r] for row in M[:r]]
        Rw = M[r][:r]
        v = [M[i][r] for i in range(r)]
        col = [1, M[r][r]]
        for _ in range(r):
            col.append(xsum([pmul(Rw[i], v[i]) for i in range(r)]))
            v = [xsum([pmul(A[i][j], v[j]) for j in range(r)]) for i in range(r)]
        col = col[: r + 2]
        vect = [xsum([pmul(col[i - j], vect[j]) for j in range(r + 1) if 0 <= i - j < len(col)]) for i in range(r + 2)]
    return vect


def smith_form(M):
    """invariant factors over GF(2)[w], d_1 | d_2 | ..., by Euclidean elimination"""
    A = [r[:] for r in M]
    n = len(A)
    diag = []
    for t in range(n):
        while True:
            best = None
            for i in range(t, n):
                for j in range(t, n):
                    if A[i][j] and (best is None or pdeg(A[i][j]) < pdeg(A[best[0]][best[1]])):
                        best = (i, j)
            if best is None:
                return diag + [0] * (n - t)
            i, j = best
            A[t], A[i] = A[i], A[t]
            for r in A:
                r[t], r[j] = r[j], r[t]
            p = A[t][t]
            clean = True
            for i in range(t + 1, n):
                if A[i][t]:
                    q = pdivmod(A[i][t], p)[0]
                    A[i] = [x ^ pmul(q, y) for x, y in zip(A[i], A[t])]
                    clean &= A[i][t] == 0
            for j in range(t + 1, n):
                if A[t][j]:
                    q = pdivmod(A[t][j], p)[0]
                    for r in A:
                        r[j] ^= pmul(q, r[t])
                    clean &= A[t][j] == 0
            if not clean:
                continue
            bad = next(((i, j) for i in range(t + 1, n) for j in range(t + 1, n) if A[i][j] and pmod(A[i][j], p)), None)
            if bad:
                A[t] = [x ^ y for x, y in zip(A[t], A[bad[0]])]
                continue
            diag.append(p)
            break
    return diag


# ---------- GF(2) dense linear algebra
def mm2(A, B):
    return np.mod(A @ B, 2.0)


def charpoly(A):
    """det(xI - A) over GF(2) of a 0/1 array, by reduction to upper Hessenberg form"""
    n = A.shape[0]
    H = [[int(x) & 1 for x in row] for row in A]
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


def rank2(M):
    """rank over GF(2) of a 0/1 array, by elimination on packed rows"""
    A = np.packbits(np.asarray(M, dtype=np.uint8) & 1, axis=1)
    rows, cols = M.shape
    r = 0
    for c in range(cols):
        if r == rows:
            break
        byte, mask = c // 8, np.uint8(1 << (7 - c % 8))
        hit = np.nonzero(A[r:, byte] & mask)[0]
        if hit.size == 0:
            continue
        p = r + hit[0]
        if p != r:
            A[[r, p]] = A[[p, r]]
        below = r + 1 + np.nonzero(A[r + 1:, byte] & mask)[0]
        if below.size:
            A[below, byte:] ^= A[r, byte:]
        r += 1
    return r


# ---------- the box, the two-particle form, the cone
def points(n):
    N = 2 * n - 2
    return [(X, Y) for X in range(N + 1) for Y in range(N + 1) if (X + Y) % 2]


def reads(n, p):
    X, Y = p
    N = 2 * n - 2
    steps = [(-1, -1), (1, 1)] if X % 2 else [(1, -1), (-1, 1)]
    return [(X + a, Y + b) for a, b in steps if 0 <= X + a <= N and 0 <= Y + b <= N]


def box(n):
    P = points(n)
    ix = {p: k for k, p in enumerate(P)}
    A = np.zeros((len(P), len(P)))
    for k, p in enumerate(P):
        for q in reads(n, p):
            A[k, ix[q]] = 1
    return P, ix, A


def two_particle(n):
    """T_e, T_o (bond swaps of a side's even and odd bonds), R (x reads x + 1), L (x + 1 reads x), on the 2n - 1 sites of a side"""
    S = 2 * n - 1
    Te, To, R, L = (np.zeros((S, S)) for _ in range(4))
    for e in range(S - 1):
        M = Te if e % 2 == 0 else To
        M[e, e + 1] = M[e + 1, e] = 1
    for x in range(S - 1):
        R[x, x + 1] = 1
        L[x + 1, x] = 1
    return Te, To, R, L


def quarter_turn(n):
    N = 2 * n - 2
    return lambda p: (p[1], N - p[0])


def cone(n):
    """orbit representatives, orbit index of every contact, and the cone walk A_cone[o, o'] = #(contacts of o' read by o's rep) mod 2"""
    P = points(n)
    rho = quarter_turn(n)
    orb, reps = {}, []
    for p in P:
        if p in orb:
            continue
        o, q = [p], rho(p)
        while q != p:
            o.append(q)
            q = rho(q)
        if len(o) != 4:
            raise ValueError("quarter turn not free")
        for q in o:
            orb[q] = len(reps)
        reps.append(min(o))
    Ac = np.zeros((len(reps), len(reps)))
    for a, r in enumerate(reps):
        for q in reads(n, r):
            Ac[a, orb[q]] += 1
    return reps, orb, np.mod(Ac, 2.0)


# ---------- GF(2^k) and the (2^k - 1)-th roots of unity
def field(k):
    """the least primitive polynomial of degree k and multiplication modulo it"""
    q = (1 << k) - 1
    for f in range((1 << k) + 1, 1 << (k + 1), 2):
        def mul(a, b, f=f):
            r = 0
            while b:
                if b & 1:
                    r ^= a
                b >>= 1
                a <<= 1
                if a >> k:
                    a ^= f
            return r
        x, e = 2, 1
        while x != 1 and e <= q:
            x, e = mul(x, 2), e + 1
        if e == q:
            return f, mul
    raise ValueError(k)


def cosets(q):
    seen, out = set(), []
    for s in range(q):
        if s in seen:
            continue
        c, t = [], s
        while t not in c:
            c.append(t)
            t = (2 * t) % q
        seen.update(c)
        out.append(c)
    return out


def minpoly_of_coset(c, mul, k):
    """prod over j in the coset of (x + z^j), z the primitive root, as a GF(2)[x] int"""
    q = (1 << k) - 1
    pw = [1]
    for _ in range(q):
        pw.append(mul(pw[-1], 2))
    poly = [1]
    for j in c:
        new = [0] * (len(poly) + 1)
        for i, a in enumerate(poly):
            new[i + 1] ^= a
            new[i] ^= mul(a, pw[j])
        poly = new
    assert all(a in (0, 1) for a in poly)
    return sum(a << i for i, a in enumerate(poly))


def trace_of_power(s, mul, k):
    """Tr(z^s) in GF(2), z the primitive root"""
    q = (1 << k) - 1
    pw = [1]
    for _ in range(q):
        pw.append(mul(pw[-1], 2))
    t = 0
    for j in range(k):
        t ^= pw[(s << j) % q]
    assert t in (0, 1)
    return t


def poly_at_matrix(A, f):
    m = A.shape[0]
    R = np.zeros_like(A)
    for i in range(pdeg(f), -1, -1):
        R = mm2(R, A)
        if (f >> i) & 1:
            R = R + np.eye(m)
        R = np.mod(R, 2.0)
    return R


def cone_spectrum(n, Ac=None):
    """for every cyclotomic coset s mod 2n - 1 (n a power of two): the eigenvalue class z^s, its minimal polynomial, and the
    kernel dimensions of m_s(A_cone)^j divided by deg m_s, j = 1, 2, ... until they stop growing"""
    if Ac is None:
        Ac = cone(n)[2]
    k = (2 * n).bit_length() - 1
    q = 2 * n - 1
    f, mul = field(k)
    m = Ac.shape[0]
    out = []
    for c in cosets(q):
        mp = minpoly_of_coset(c, mul, k)
        d = pdeg(mp)
        Mp = poly_at_matrix(Ac, mp)
        Pw, dims = np.eye(m), []
        while True:
            Pw = mm2(Pw, Mp)
            kd = m - rank2(Pw)
            assert kd % d == 0
            if dims and kd // d == dims[-1]:
                break
            dims.append(kd // d)
            if kd == 0:
                break
        out.append({"coset": c[0], "size": d, "minpoly": mp, "alg": dims[-1], "kernel dims": dims,
                    "Tr(1/lambda)": trace_of_power((-c[0]) % q, mul, k)})
    return {"field polynomial": f, "classes": out}


def triangular_index(a):
    k = int(((8 * a + 1) ** 0.5 - 1) / 2 + 0.5)
    return k if k * (k + 1) // 2 == a else None


def clebsch_gordan_dims(k):
    """kernel dimensions, power by power, of a nilpotent with Jordan blocks 2k - 1, 2k - 5, ... (the last 1 or 3)"""
    blocks = [b for b in range(2 * k - 1, 0, -4)]
    return [sum(min(b, j) for b in blocks) for j in range(1, (blocks[0] if blocks else 0) + 1)]


def cone_polynomial(n, spec):
    """det(I - w A_cone) assembled from the spectrum: prod over classes of rev(m_s)^alg"""
    P = 1
    for r in spec["classes"]:
        rv = prev(r["minpoly"], pdeg(r["minpoly"]))
        for _ in range(r["alg"]):
            P = pmul(P, rv)
    return P


# ---------- the side-2n torus and its cut lines (n a power of two)
def cut_line_resolvent(n, steps=None):
    """R_CC(w) = sum_k w^k (M^k)_CC over the 2n cut contacts (C1 by Y = 2y, then C2 by X = 2x), as int polynomials.
    Walks are pushed along reads on the torus Z_(2n)^2, all starting contacts at once."""
    L = 2 * n
    steps = steps or 2 * n
    C = [(L - 1, Y) for Y in range(0, L, 2)] + [(X, L - 1) for X in range(0, L, 2)]
    S = len(C)
    st = np.zeros((S, L, L), dtype=np.uint8)
    for a, (X, Y) in enumerate(C):
        st[a, X, Y] = 1
    Xodd = (np.arange(L)[:, None] % 2 == 1) & np.ones((1, L), dtype=bool)
    R = [[0] * S for _ in range(S)]
    for k in range(steps):
        vals = st[:, [c[0] for c in C], [c[1] for c in C]]
        for a in range(S):
            for b in np.nonzero(vals[a])[0]:
                R[a][b] |= 1 << k
        h = st * Xodd
        v = st * (~Xodd)
        new = (np.roll(np.roll(h, 1, 1), 1, 2) ^ np.roll(np.roll(h, -1, 1), -1, 2)
               ^ np.roll(np.roll(v, 1, 1), -1, 2) ^ np.roll(np.roll(v, -1, 1), 1, 2))
        st = new
        if not st.any():
            break
    return C, R


def return_map(n):
    """G, H, H2 (the blocks of R_CC), the inverse G^-1 = I + w^2 K, B = G^-1 H, C = B J and its J-symmetric part C_s"""
    C, R = cut_line_resolvent(n)
    G = [[R[a][b] for b in range(n)] for a in range(n)]
    Gv = [[R[n + a][n + b] for b in range(n)] for a in range(n)]
    H = [[R[a][n + b] for b in range(n)] for a in range(n)]
    H2 = [[R[n + a][b] for b in range(n)] for a in range(n)]
    J = [[1 if i + j == n - 1 else 0 for j in range(n)] for i in range(n)]
    Gi = [[0] * n for _ in range(n)]
    for i in range(n):
        Gi[i][i] ^= 1
        Gi[i][(i + 1) % n] ^= 0b100
        Gi[i][(i - 1) % n] ^= 0b100
    B = pmat_mul(Gi, H)
    Cm = pmat_mul(B, J)
    h = n // 2
    Cs = [[Cm[i][k] ^ Cm[i][n - 1 - k] for k in range(h)] for i in range(h)]
    return {"R": R, "G": G, "Gv": Gv, "H": H, "H2": H2, "J": J, "Ginv": Gi, "B": B, "C": Cm, "Cs": Cs}
