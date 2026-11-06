"""Arithmetic and linear algebra over F4 = {0, 1, w, w^2} with w^2 = w + 1.

Encoding: a0 + a1*w is stored as the integer a0 + 2*a1, so
    0 -> 0,   1 -> 1,   2 -> w,   3 -> w^2 = w + 1.
Addition is XOR of codes; multiplication uses the table MUL.

Two vector formats are used:
  * plain lists of codes, for the small systems (kernels, annihilators);
  * bit-sliced pairs (lo, hi) of Python ints, where bit i of lo (of hi) is the
    1-coefficient (w-coefficient) of coordinate i.  Only the hot loop that
    counts pairs (a, b) uses this format, through rank_bits.

Independent replay code: written from scratch, standard library only.
"""
from itertools import product

MUL = ((0, 0, 0, 0),
       (0, 1, 2, 3),
       (0, 2, 3, 1),
       (0, 3, 1, 2))
INV = (None, 1, 3, 2)
W, W2 = 2, 3


def wpow(k):
    """w**k for any integer k (w has multiplicative order 3)."""
    return (1, W, W2)[k % 3]


def self_check():
    """Exhaustive check of the field axioms for the tables."""
    assert W2 == W ^ 1 and MUL[W][W] == W2          # w^2 = w + 1
    for a in range(4):
        assert MUL[1][a] == a and MUL[0][a] == 0
        if a:
            assert MUL[a][INV[a]] == 1
        for b in range(4):
            assert MUL[a][b] == MUL[b][a]
            for c in range(4):
                assert MUL[MUL[a][b]][c] == MUL[a][MUL[b][c]]
                assert MUL[a][b ^ c] == MUL[a][b] ^ MUL[a][c]
    assert [wpow(k) for k in range(6)] == [1, W, W2, 1, W, W2]
    assert MUL[W][W2] == 1


# --------------------------------------------------------------- list format
def dot(u, v):
    s = 0
    for a, b in zip(u, v):
        s ^= MUL[a][b]
    return s


def mat_vec(M, v):
    return [dot(row, v) for row in M]


def lin_comb(coeffs, vectors, length):
    out = [0] * length
    for c, vec in zip(coeffs, vectors):
        if c:
            row = MUL[c]
            for t in range(length):
                out[t] ^= row[vec[t]]
    return out


def transpose(M, ncols):
    return [[row[j] for row in M] for j in range(ncols)]


def rref(rows, ncols):
    """Reduced row echelon form; returns (nonzero rows, pivot columns)."""
    M = [list(r) for r in rows]
    pivots = []
    r = 0
    for c in range(ncols):
        if r == len(M):
            break
        piv = next((i for i in range(r, len(M)) if M[i][c]), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        s = MUL[INV[M[r][c]]]
        M[r] = [s[x] for x in M[r]]
        for i in range(len(M)):
            f = M[i][c]
            if i != r and f:
                fr = MUL[f]
                M[i] = [x ^ fr[y] for x, y in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
    return M[:r], pivots


def rank(rows, ncols):
    return len(rref(rows, ncols)[1])


def nullspace(rows, ncols):
    """Basis of {v in F4^ncols : M v = 0} for M given by its rows."""
    R, piv = rref(rows, ncols)
    pivset = set(piv)
    basis = []
    for f in range(ncols):
        if f in pivset:
            continue
        v = [0] * ncols
        v[f] = 1
        for i, c in enumerate(piv):
            v[c] = R[i][f]          # v[c] = -R[i][f] and -1 = 1 in F4
        basis.append(v)
    return basis


def same_span(A, B, ncols):
    """Do the lists of vectors A and B span the same subspace?"""
    return rref(A, ncols)[0] == rref(B, ncols)[0]


def in_span(v, A, ncols):
    return rank(A, ncols) == rank(list(A) + [v], ncols)


# --------------------------------------------------------- bit-sliced format
def pack(vec):
    lo = hi = 0
    for i, a in enumerate(vec):
        if a & 1:
            lo |= 1 << i
        if a & 2:
            hi |= 1 << i
    return lo, hi


def scale_bits(c, lo, hi):
    """c * (lo, hi) for c in F4 (w*(x0 + x1 w) = x1 + (x0 + x1) w)."""
    if c == 0:
        return 0, 0
    if c == 1:
        return lo, hi
    if c == 2:
        return hi, lo ^ hi
    return lo ^ hi, lo


def rank_bits(rows):
    """Rank over F4 of a list of bit-sliced vectors."""
    pivots = {}
    r = 0
    for lo, hi in rows:
        while lo | hi:
            m = lo | hi
            b = m & -m                               # lowest nonzero coordinate
            c = (1 if lo & b else 0) | (2 if hi & b else 0)
            if b in pivots:
                plo, phi = pivots[b]                 # normalised: 1 at bit b
                slo, shi = scale_bits(c, plo, phi)
                lo ^= slo
                hi ^= shi
            else:
                pivots[b] = scale_bits(INV[c], lo, hi)
                r += 1
                break
    return r


def projective_points(d):
    """One representative of each line of F4^d (first nonzero entry = 1),
    yielded as the sparse list [(index, value), ...] of nonzero entries."""
    for lead in range(d):
        for tail in product(range(4), repeat=d - 1 - lead):
            pts = [(lead, 1)]
            pts.extend((lead + 1 + t, x) for t, x in enumerate(tail) if x)
            yield pts


def all_vectors(d):
    return product(range(4), repeat=d)
