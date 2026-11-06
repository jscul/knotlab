"""The group G = UT3(F4) x| <h> of order 192.

N = UT3(F4) is the set of triples (x, y, z) over F4 with
    (x, y, z)(u, v, t) = (x + u, y + v, z + t + x*v),
and h has order 3, acting by
    h n h^-1 = phi(n),   phi(x, y, z) = (w^2 x, w^2 y, w z).
The element n h^k is stored as the tuple (x, y, z, k), or as the integer code
    ((k*4 + x)*4 + y)*4 + z   in range(192).
Products:  (n h^k)(m h^l) = n phi^k(m) h^(k+l).

Independent replay code: written from scratch, standard library only.
"""
from f4 import MUL, wpow

ORDER = 192
IDENTITY = 0


def encode(x, y, z, k):
    return ((k * 4 + x) * 4 + y) * 4 + z


def decode(g):
    return (g >> 4) & 3, (g >> 2) & 3, g & 3, g >> 6


def _mul(g, h):
    x, y, z, k = g
    u, v, t, l = h
    s, c = wpow(2 * k), wpow(k)      # phi^k: (x, y) times w^(2k), z times w^k
    u, v, t = MUL[s][u], MUL[s][v], MUL[c][t]
    return (x ^ u, y ^ v, z ^ t ^ MUL[x][v], (k + l) % 3)


ELEMENTS = [decode(g) for g in range(ORDER)]
MULT = [[encode(*_mul(ELEMENTS[a], ELEMENTS[b])) for b in range(ORDER)]
        for a in range(ORDER)]
INV = [next(b for b in range(ORDER) if MULT[a][b] == IDENTITY)
       for a in range(ORDER)]
H = encode(0, 0, 0, 1)


def power(g, e):
    if e < 0:
        g, e = INV[g], -e
    r = IDENTITY
    for _ in range(e):
        r = MULT[r][g]
    return r


def conjugacy_classes():
    seen, classes = set(), []
    for g in range(ORDER):
        if g not in seen:
            cls = sorted({MULT[MULT[a][g]][INV[a]] for a in range(ORDER)})
            seen.update(cls)
            classes.append(cls)
    return classes


def self_check():
    """Group axioms (exhaustive associativity), the defining relations, and
    the expected class structure 1 + 3 + 5*12 + 64 + 64."""
    assert all(decode(encode(*ELEMENTS[g])) == ELEMENTS[g] for g in range(ORDER))
    M = MULT
    for a in range(ORDER):
        Ma = M[a]
        assert Ma[IDENTITY] == a and M[IDENTITY][a] == a
        assert Ma[INV[a]] == IDENTITY
        for b in range(ORDER):
            Mab = M[Ma[b]]
            Mb = M[b]
            for c in range(ORDER):
                if Mab[c] != Ma[Mb[c]]:
                    raise AssertionError("not associative")
    # N-multiplication as stated, and h n h^-1 = phi(n)
    for x, y, z in [(1, 2, 3), (3, 1, 0), (2, 2, 1)]:
        for u, v, t in [(1, 1, 1), (0, 3, 2), (2, 0, 1)]:
            g = MULT[encode(x, y, z, 0)][encode(u, v, t, 0)]
            assert decode(g) == (x ^ u, y ^ v, z ^ t ^ MUL[x][v], 0)
        n = encode(x, y, z, 0)
        conj = MULT[MULT[H][n]][INV[H]]
        assert decode(conj) == (MUL[3][x], MUL[3][y], MUL[2][z], 0)
    assert power(H, 3) == IDENTITY and power(H, 1) != IDENTITY
    sizes = sorted(len(c) for c in conjugacy_classes())
    assert sizes == [1, 3, 12, 12, 12, 12, 12, 64, 64], sizes
    return sizes
