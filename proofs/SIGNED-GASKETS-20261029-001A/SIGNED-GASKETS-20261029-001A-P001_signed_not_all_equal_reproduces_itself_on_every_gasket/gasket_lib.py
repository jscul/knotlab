"""Level-k Sierpinski gaskets SG_k with copies of a three-bit law on their up triangles (SIGNED-GASKETS-20261029-001A).

SG_k: vertices (i, j) with i, j >= 0 and i + j <= k; up triangles T(i, j) = ((i, j), (i+1, j), (i, j+1)) = (a, b, c) for i + j <= k - 1.
Corners A = (0, 0), B = (k, 0), C = (0, k).  The corner relation R_k(x_A, x_B, x_C) sums the product of the law over all the other
vertices.  Row j holds the vertices (i, j); the triangles of row j join row j to row j + 1, and every vertex of row j + 1 is the
c-corner of exactly one of them, so R_k is computed by a zipper transfer over the rows (state = one row, 2^(k+1) values at most),
exactly modulo primes, or in floating point for real laws."""
import itertools
import numpy as np

PRIMES = (2147483629, 2147483587, 2147483579, 2147483563)
TUPLES = list(itertools.product((0, 1), repeat=3))


def law(neg, excl):
    """weights +-1 on the tuples not in excl, -1 on those in neg; index a*4 + b*2 + c"""
    w = [0] * 8
    for t in TUPLES:
        s = "".join(map(str, t))
        if s not in excl:
            w[t[0] * 4 + t[1] * 2 + t[2]] = -1 if s in neg else 1
    return w


NAE_SIGNED = law({"011", "100"}, {"000", "111"})  # -1 exactly when the a-corner is the odd one


def _zipper(k, W, x, y, mod=None):
    """vector over the apex value: sum over SG_k with bottom-row ends x, y fixed (W as a (2, 2, 2) array W[a, b, c])"""
    dt = np.int64 if mod is not None else W.dtype
    v = np.zeros((2,) * (k + 1), dtype=dt)
    idx = [slice(None)] * (k + 1)
    idx[0] = x
    idx[k] = y
    v[tuple(idx)] = 1
    for row in range(k):
        n = k - row
        for i in range(n):
            v = np.moveaxis(v, (i, i + 1), (0, 1))
            sh = v.shape
            v2 = v.reshape(2, 2, -1)
            out = np.empty_like(v2)
            for c in (0, 1):
                out[c] = v2[0] * W[0, :, c][:, None] + v2[1] * W[1, :, c][:, None]
                if mod is not None:
                    out[c] %= mod
            v = np.moveaxis(out.reshape(sh), (0, 1), (i, i + 1))
        v = v.sum(axis=n)
        if mod is not None:
            v %= mod
    return v


def corner_relation_mod(k, w, p):
    W = (np.array(w, dtype=np.int64).reshape(2, 2, 2)) % p
    R = np.zeros((2, 2, 2), dtype=np.int64)
    for x, y in itertools.product((0, 1), repeat=2):
        R[x, y] = _zipper(k, W, x, y, mod=p)
    return R


def corner_relation(k, w, primes=PRIMES):
    """exact integer corner relation by the Chinese remainder theorem (|values| < half the product of the primes)"""
    Rs = [corner_relation_mod(k, w, p) for p in primes]
    M = 1
    for p in primes:
        M *= p
    out = np.zeros((2, 2, 2), dtype=object)
    for t in TUPLES:
        v = 0
        for p, Rp in zip(primes, Rs):
            q = M // p
            v += int(Rp[t]) * q * pow(q, -1, p)
        v %= M
        out[t] = v - M if v > M // 2 else v
    return out


def corner_relation_float(k, w):
    W = np.array(w, dtype=float).reshape(2, 2, 2)
    R = np.zeros((2, 2, 2))
    for x, y in itertools.product((0, 1), repeat=2):
        R[x, y] = _zipper(k, W, x, y)
    return R


def proportional(R, w):
    """(True, lambda) when R = lambda w with lambda nonzero, exactly (integers)"""
    t0 = next(t for t in TUPLES if w[t[0] * 4 + t[1] * 2 + t[2]] != 0)
    w0 = w[t0[0] * 4 + t0[1] * 2 + t0[2]]
    lam = R[t0] // w0 if R[t0] % w0 == 0 else None
    if lam is None or lam == 0:
        return False, lam
    return all(R[t] == lam * w[t[0] * 4 + t[1] * 2 + t[2]] for t in TUPLES), lam


def w_theta(theta):
    """(-1)^a sin(theta E)/sin(theta), E = (-1)^a + (-1)^b + (-1)^c"""
    return [(-1) ** t[0] * np.sin(theta * sum((-1) ** x for x in t)) / np.sin(theta) for t in TUPLES]


def sector_lambda(k):
    """lambda_k from the sector formula: sectors d on the triangle positions (i, j), i + j <= k - 1, fixed to 0 on the bottom row and
    the left column; product over interior vertices (i, j) (i, j >= 1) of NAE_SIGNED(d(i,j), d(i-1,j), d(i,j-1)), times, for every
    hypotenuse vertex (i, k - i) with 1 <= i <= k - 1, the factor 2 if its two triangles differ in sector and -1 if they agree"""
    w = NAE_SIGNED
    pos = [(i, j) for i in range(k) for j in range(k - i)]
    free = [(i, j) for (i, j) in pos if i >= 1 and j >= 1]
    tot = 0
    for bits in itertools.product((0, 1), repeat=len(free)):
        d = {p: 0 for p in pos}
        d.update(zip(free, bits))
        wt = 1
        for (i, j) in free:
            wt *= w[d[(i, j)] * 4 + d[(i - 1, j)] * 2 + d[(i, j - 1)]]
            if wt == 0:
                break
        if wt == 0:
            continue
        for i in range(1, k):
            wt *= 2 if d[(i - 1, k - i)] != d[(i, k - i - 1)] else -1
        tot += wt
    return tot


def even_edge_sets(k):
    """edge sets made of horizontal edges (i,j)-(i+1,j) and vertical edges (i,j)-(i,j+1), i + j <= k - 1, never both at one (i, j),
    with even degree at every vertex but the corners; returned as frozensets of edges"""
    V = [(i, j) for i in range(k + 1) for j in range(k + 1 - i)]
    owners = [(i, j) for (i, j) in V if i + j <= k - 1]
    corners = {(0, 0), (k, 0), (0, k)}
    found = []
    for choice in itertools.product((None, "h", "v"), repeat=len(owners)):
        deg = {v: 0 for v in V}
        E = []
        for (i, j), c in zip(owners, choice):
            if c == "h":
                e = ((i, j), (i + 1, j))
            elif c == "v":
                e = ((i, j), (i, j + 1))
            else:
                continue
            E.append(e)
            deg[e[0]] += 1
            deg[e[1]] += 1
        if all(deg[v] % 2 == 0 for v in V if v not in corners):
            found.append(frozenset(E))
    return found
