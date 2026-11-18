"""Chain grids: pair counts of grid distinctions on the endless chain grid, and the reduction to a two-valued pair law.

Chain grid of length l: distinctions at the pairs of whole numbers (grid distinctions); each neighbouring pair (u, v) of the
literature's square grid is joined by a chain of l not-all-equal knots (u, c1, p1), (c1, c2, p2), ..., (c_{l-1}, v, p_l), with
chain distinctions c_i and one loose distinction p_i per knot.  Uniform weighting over the allowed states.

Summing out the loose and chain distinctions leaves, on the grid distinctions, weight w_eq(l) or w_ne(l) per neighbouring pair by
whether its two values are equal, with (w_eq - w_ne)/(w_eq + w_ne) = (-1/3)^l: the literature's Ising model at tanh K = (-1/3)^l,
high temperature for every l.  On grid distinctions the correlation is (-1)^(l |x - y|_1) times the ferromagnetic one at
t = 3^-l.  Exact infinite-plane correlations come from the Kac-Ward resolvent (Fourier inverse of a 4 x 4 symbol), by two
independent formulas:
- reweighting: <s_0 s_x> = t^|P| Z(t -> 1/t on a path P)/Z, the ratio a determinant over the path's directed pairs;
- the dual count: <s_0 s_x> = Z_w(signs flipped on the pairs crossing P)/Z_w at the dual weight w = (1 - t)/(1 + t)."""
import itertools
import math

import numpy as np

DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]
TURN = {0: 0.0, 1: math.pi / 2, 3: -math.pi / 2}


def pair_weights(l):
    """(w_eq, w_ne): number of completions of a chain of l knots between two distinctions with equal / unequal values."""
    # transfer over one knot: w1(a, b) = 1 if a == b else 2 (the loose distinction is forced or free)
    T = np.array([[1, 2], [2, 1]], dtype=object)
    M = np.identity(2, dtype=object)
    for _ in range(l):
        M = M.dot(T)
    return int(M[0, 0]), int(M[0, 1])


class Resolvent:
    def __init__(self, w, N=256):
        k = 2 * np.pi * np.arange(N) / N
        K1, K2 = np.meshgrid(k, k, indexing="ij")
        Lh = np.zeros((N, N, 4, 4), dtype=complex)
        for d in range(4):
            ph = np.exp(1j * (K1 * DIRS[d][0] + K2 * DIRS[d][1]))
            for d2 in range(4):
                if d2 != (d + 2) % 4:
                    Lh[:, :, d, d2] = w * np.exp(1j * TURN[(d2 - d) % 4] / 2) * ph
        self.G = np.fft.ifft2(np.linalg.inv(np.eye(4)[None, None] - Lh), axes=(0, 1))
        self.N = N

    def g(self, x, d, y, d2):
        return self.G[(x[0] - y[0]) % self.N, (x[1] - y[1]) % self.N, d, d2]


def _directed(u, v):
    d = DIRS.index((v[0] - u[0], v[1] - u[1]))
    return [(u, d), (v, (d + 2) % 4)]


def _ratio(R, undirected, factor):
    E = [e for (u, v) in undirected for e in _directed(u, v)]
    m = len(E)
    A = np.empty((m, m), dtype=complex)
    for i, (x, d) in enumerate(E):
        for j, (y, d2) in enumerate(E):
            A[i, j] = R.g(x, d, y, d2) - (1.0 if i == j else 0.0)
    return np.linalg.det(np.eye(m) - A * factor)


def path(steps, start=(0, 0)):
    p = [start]
    for s in steps:
        p.append((p[-1][0] + s[0], p[-1][1] + s[1]))
    return p


def corr_reweight(R, t, p):
    und = list(zip(p, p[1:]))
    return (t ** len(und) * np.sqrt(_ratio(R, und, 1 / t ** 2 - 1))).real


def _dual(p):
    out = []
    for (x, y), (X, Y) in zip(p, p[1:]):
        d = (X - x, Y - y)
        if d == (1, 0):
            out.append(((x, y - 1), (x, y)))
        elif d == (-1, 0):
            out.append(((X, Y - 1), (X, Y)))
        elif d == (0, 1):
            out.append(((x - 1, y), (x, y)))
        else:
            out.append(((X - 1, Y), (X, Y)))
    return out


def corr_dual(Rd, p):
    return np.sqrt(_ratio(Rd, _dual(p), -2.0)).real


def onsager_nn(t):
    from scipy.special import ellipk
    K = math.atanh(t)
    kap = 2 * math.sinh(2 * K) / math.cosh(2 * K) ** 2
    return 0.5 / math.tanh(2 * K) * (1 + (2 / math.pi) * (2 * math.tanh(2 * K) ** 2 - 1) * ellipk(kap ** 2))


# ---------- literal brute force of small chain grids (the reduction gate) ----------

def chain_grid_base(cells, links, l):
    """Distinctions and knots of a chain grid on the given grid distinctions and neighbouring pairs."""
    names = list(cells)
    knots = []
    for (u, v) in links:
        prev = u
        for i in range(l):
            nxt = v if i == l - 1 else ("c", u, v, i)
            loose = ("p", u, v, i)
            for z in (nxt, loose):
                if z not in names:
                    names.append(z)
            knots.append((prev, nxt, loose))
            prev = nxt
    return names, knots


def literal_counts(cells, links, l, chunk=1 << 22):
    """Allowed-state count N and disagreement counts of every pair of grid distinctions, by enumerating every assignment."""
    names, knots = chain_grid_base(cells, links, l)
    idx = {z: i for i, z in enumerate(names)}
    n = len(names)
    K = [(idx[a], idx[b], idx[c]) for a, b, c in knots]
    pairs = list(itertools.combinations(range(len(cells)), 2))
    N = 0
    D = np.zeros(len(pairs), dtype=np.int64)
    for start in range(0, 1 << n, chunk):
        s = np.arange(start, min(start + chunk, 1 << n), dtype=np.uint64)
        ok = np.ones(len(s), dtype=bool)
        for a, b, c in K:
            x, y, z = (s >> np.uint64(a)) & np.uint64(1), (s >> np.uint64(b)) & np.uint64(1), (s >> np.uint64(c)) & np.uint64(1)
            ok &= ~((x == y) & (y == z))
        s = s[ok]
        N += len(s)
        for q, (i, j) in enumerate(pairs):
            D[q] += int(np.count_nonzero(((s >> np.uint64(i)) ^ (s >> np.uint64(j))) & np.uint64(1)))
    return N, {pairs[q]: int(D[q]) for q in range(len(pairs))}


def reduced_counts(cells, links, l):
    """The same counts from the reduced pair law (weights w_eq, w_ne per neighbouring pair), by enumerating grid values."""
    weq, wne = pair_weights(l)
    m = len(cells)
    ci = {c: i for i, c in enumerate(cells)}
    L = [(ci[u], ci[v]) for u, v in links]
    pairs = list(itertools.combinations(range(m), 2))
    N = 0
    D = {p: 0 for p in pairs}
    for s in range(1 << m):
        w = 1
        for a, b in L:
            w *= weq if ((s >> a) & 1) == ((s >> b) & 1) else wne
        N += w
        for (i, j) in pairs:
            if ((s >> i) ^ (s >> j)) & 1:
                D[(i, j)] += w
    return N, D


def torus(L):
    cells = [(i, j) for i in range(L) for j in range(L)]
    links = [((i, j), ((i + 1) % L, j)) for i in range(L) for j in range(L)] + \
            [((i, j), (i, (j + 1) % L)) for i in range(L) for j in range(L)]
    return cells, links


def patch(W, H):
    cells = [(i, j) for i in range(W) for j in range(H)]
    links = [((i, j), (i + 1, j)) for i in range(W - 1) for j in range(H)] + \
            [((i, j), (i, j + 1)) for i in range(W) for j in range(H - 1)]
    return cells, links


RAYS = {"(1,0)": ((1, 0), [(1, 0)]), "(1,1)": ((1, 1), [(1, 0), (0, 1)]),
        "(2,1)": ((2, 1), [(1, 0), (1, 0), (0, 1)]), "(3,1)": ((3, 1), [(1, 0), (1, 0), (1, 0), (0, 1)])}
