"""Library for signed laws under shared subdivision of the triangular-lattice torus (exact modular arithmetic).

Rules (as SHARED-SUBDIVISION-20261029-001A): S2 puts a law on every up triangle (sites (i,j), (i+1,j), (i,j+1)); S1 puts one law on up
triangles and one on down triangles (sites (i+1,j), (i,j+1), (i+1,j+1)).  Rows of the torus of side L are states of a transfer matrix
T[r, s] = prod_i w_up(r_i, r_{i+1}, s_i) * w_dn(r_{i+1}, s_i, s_{i+1}).  Scale k: the coarse sites are the fine sites (k i, k j).
F(x) = sum over fine assignments restricting to the coarse assignment x of the product of weights = trace(prod_j D_{x_j} T^k).
W(x) = the coarse weight = prod_j T_m[x_j, x_{j+1}].  Exact: F = c W for one nonzero c; support-exact: same support.
All values are integers (weights in {-1, 1}); they are computed modulo six primes below 2^18 and decided exactly, because every
|F(x) W(y)| is below 2^81 < (product of the primes) / 2."""
import itertools
import numpy as np

cube = list(itertools.product((0, 1), repeat=3))
PRIMES = (262139, 262133, 262127, 262121, 262111, 262109)


def knots():
    res = []

    def grow(start, E):
        if E:
            res.append(frozenset(s for s in cube if s not in E))
        for i in range(start, 8):
            s = cube[i]
            if all(sum(a != b for a, b in zip(s, e)) >= 2 for e in E):
                grow(i + 1, E + [s])
    grow(0, [])
    return res


def permute(K, p):
    return frozenset(tuple(s[p[i]] for i in range(3)) for s in K)


def placements(K):
    return sorted({permute(K, p) for p in itertools.permutations(range(3))}, key=sorted)


K34 = knots()
_cls = {}
for _K in K34:
    _cls.setdefault(min(tuple(sorted(P)) for P in placements(_K)), _K)
REPS = list(_cls.values())


def kind(K):
    E = [s for s in cube if s not in K]
    if len(E) == 4:
        return "parity"
    if len(E) == 3:
        return "three excluded"
    if len(E) == 2:
        return "two excluded at distance two" if sum(a != b for a, b in zip(*E)) == 2 else "not-all-equal type"
    return "atom"


def rule_shapes():
    out = [("S2", K, None) for K in K34]
    for K in REPS:
        for P1 in placements(K):
            for P2 in placements(K):
                out.append(("S1", P1, P2))
    return out


def sign_patterns(n):
    """weights up to a global sign (the first allowed tuple carries +1)"""
    return [(1,) + p for p in itertools.product((1, -1), repeat=n - 1)]


def wvec(K, eps):
    w = np.zeros(8, dtype=np.int64)
    for t, e in zip(sorted(K), eps):
        w[t[0] * 4 + t[1] * 2 + t[2]] = e
    return w


_BITS = {}


def bits_of(L):
    if L not in _BITS:
        r = np.arange(1 << L)
        _BITS[L] = (r[:, None] >> np.arange(L)[None, :]) & 1
    return _BITS[L]


def transfer(L, wup, wdn, p):
    bits = bits_of(L)
    n = 1 << L
    T = np.ones((n, n), dtype=np.int64)
    for i in range(L):
        a = bits[:, i][:, None]; b = bits[:, (i + 1) % L][:, None]; c = bits[:, i][None, :]
        T = (T * (wup[a * 4 + b * 2 + c] % p)) % p
        if wdn is not None:
            d = bits[:, (i + 1) % L][:, None]; e = bits[:, i][None, :]; f = bits[:, (i + 1) % L][None, :]
            T = (T * (wdn[d * 4 + e * 2 + f] % p)) % p
    return T


def _mm(A, B, p):
    """exact (A @ B) mod p for integer matrices with entries in [0, p): float64 products stay below 2^53"""
    return np.mod(np.asarray(A, dtype=np.float64) @ np.asarray(B, dtype=np.float64), p).astype(np.int64)


def fine_sums(m, k, wup, wdn, p):
    """dict coarse assignment (tuple of m row-values) -> F mod p"""
    L = k * m
    T = transfer(L, wup, wdn, p)
    bits = bits_of(L)
    key = (bits[:, ::k] * (1 << np.arange(m))[None, :]).sum(1)
    Tk = np.eye(T.shape[0], dtype=np.int64)
    for _ in range(k):
        Tk = _mm(Tk, T, p)
    B = [(Tk * (key == x)[:, None]) % p for x in range(1 << m)]
    out = {}
    if m == 2:
        for x0, x1 in itertools.product(range(1 << m), repeat=2):
            out[(x0, x1)] = int(np.sum((B[x0] * B[x1].T) % p) % p)
    elif m == 3:
        for x0, x1 in itertools.product(range(1 << m), repeat=2):
            C = _mm(B[x0], B[x1], p)
            for x2 in range(1 << m):
                out[(x0, x1, x2)] = int(np.sum((C * B[x2].T) % p) % p)
    elif m == 4:
        Bs = np.stack(B)
        n = T.shape[0]
        C = np.zeros((16, 16, n, n), dtype=np.int64)
        for x0 in range(16):
            for x1 in range(16):
                C[x0, x1] = _mm(Bs[x0], Bs[x1], p)
        Cf = C.reshape(256, n * n)
        CT = np.transpose(C, (0, 1, 3, 2)).reshape(256, n * n)
        N = _mm(Cf, CT.T, p)  # N[a, b] = trace(C_a C_b) = sum_ij C_a[i,j] C_b[j,i]; dot length n^2 = 2^16, sums < 2^52
        for a in range(256):
            x0, x1 = divmod(a, 16)
            for b in range(256):
                x2, x3 = divmod(b, 16)
                out[(x0, x1, x2, x3)] = int(N[a, b])
    else:
        raise ValueError("coarse side 2, 3 or 4")
    return out


def coarse_weights(m, wup, wdn, p):
    T = transfer(m, wup, wdn, p)
    out = {}
    for xs in itertools.product(range(1 << m), repeat=m):
        v = 1
        for j in range(m):
            v = v * int(T[xs[j], xs[(j + 1) % m]]) % p
        out[xs] = v
    return out


def decide(m, k, wup, wdn, primes=PRIMES):
    """returns dict: vacuous (no coarse solutions), support_exact, exact"""
    supp_F, supp_W, cross_ok = None, None, True
    Fs, Ws = [], []
    for p in primes:
        F = fine_sums(m, k, wup, wdn, p)
        W = coarse_weights(m, wup, wdn, p)
        Fs.append(F); Ws.append(W)
    xs = list(Fs[0])
    supp_F = {x for x in xs if any(F[x] for F in Fs)}
    supp_W = {x for x in xs if any(W[x] for W in Ws)}
    if not supp_W:
        return {"vacuous": True, "support_exact": not supp_F, "exact": not supp_F}
    if supp_F != supp_W:
        return {"vacuous": False, "support_exact": False, "exact": False}
    x0 = next(iter(sorted(supp_W)))
    for F, W, p in zip(Fs, Ws, primes):
        for y in xs:
            if (F[x0] * W[y] - F[y] * W[x0]) % p:
                cross_ok = False
                break
        if not cross_ok:
            break
    return {"vacuous": False, "support_exact": True, "exact": cross_ok}
