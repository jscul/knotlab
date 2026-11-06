"""Level-k Sierpinski d-simplices SG^d_k with copies of a (d+1)-bit law on their up simplices (SIMPLEX-GASKETS-20261029-001A).

SG^d_k: vertices v in Z^d with v >= 0 and |v| = v_1 + ... + v_d <= k; up simplices T(v) = (v, v+e_1, ..., v+e_d) for |v| <= k - 1, with
role 0 the base corner v and role i the corner v + e_i; corners A = 0 and B_i = k e_i.  A law is a (2,)*(d+1) array W[x_0, ..., x_d].
The corner relation R(x_A, x_B1, ..., x_Bd) sums the product of the law over every other vertex.  It is computed by variable
elimination along a greedy plan that depends only on (d, k), with pairwise products, so that modulo a prime below 2^31 no
intermediate value overflows int64; exact integers come from the Chinese remainder theorem.  A leading batch axis on W evaluates
many laws at once."""
import itertools, math
from functools import lru_cache
import numpy as np

PRIMES = (2147483629, 2147483587, 2147483579, 2147483563, 2147483549, 2147483543)
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


@lru_cache(None)
def gasket(d, k):
    """(vertices, up simplices as tuples of vertex ids in role order, corners (A, B_1, ..., B_d))"""
    V = tuple(v for v in itertools.product(range(k + 1), repeat=d) if sum(v) <= k)
    vid = {v: n for n, v in enumerate(V)}
    unit = [tuple(int(j == i) for j in range(d)) for i in range(d)]
    simp = tuple(tuple([vid[v]] + [vid[tuple(a + b for a, b in zip(v, e))] for e in unit]) for v in V if sum(v) <= k - 1)
    corners = tuple([vid[(0,) * d]] + [vid[tuple(k * u for u in e)] for e in unit])
    return V, simp, corners


def counts(d, k):
    """(number of up simplices, number of summed vertices N)"""
    V, simp, corners = gasket(d, k)
    return len(simp), len(V) - len(corners)


def tower(d, k, m):
    """the level-m tower of SG^d_k as a complex (vertex count, simplices, corners): level 1 is SG^d_k, and level m + 1 puts a copy of level m
    on every up simplex of SG^d_k, scaled by k^m, glued at its corners"""
    V, simp, corners = gasket(d, k)
    cur = [tuple(V[u] for u in s) for s in simp]
    for level in range(1, m):
        scale = k ** level
        cur = [tuple(tuple(scale * a + b for a, b in zip(V[s[0]], u)) for u in t) for s in simp for t in cur]
    verts = sorted({u for t in cur for u in t})
    vid = {u: n for n, u in enumerate(verts)}
    K = k ** m
    cs = [(0,) * d] + [tuple(K * int(j == i) for j in range(d)) for i in range(d)]
    return len(verts), tuple(tuple(vid[u] for u in t) for t in cur), tuple(vid[c] for c in cs)


def complex_of(d, k):
    V, simp, corners = gasket(d, k)
    return len(V), simp, corners


@lru_cache(None)
def plan_complex(nv, simp, corners):
    """greedy elimination plan: factor variable lists (simplices first) and steps (vertex, factors joined, new factor id)"""
    facs = [tuple(s) for s in simp]
    live = list(range(len(facs)))
    internal = [v for v in range(nv) if v not in corners]
    steps = []
    while internal:
        best = None
        for v in internal:
            vs = set()
            for f in live:
                if v in facs[f]:
                    vs |= set(facs[f])
            if best is None or len(vs) < best[0]:
                best = (len(vs), v)
        v = best[1]
        group = tuple(f for f in live if v in facs[f])
        out = tuple(sorted(set().union(*[set(facs[f]) for f in group]) - {v}))
        facs.append(out)
        live = [f for f in live if f not in group] + [len(facs) - 1]
        steps.append((v, group, len(facs) - 1))
        internal.remove(v)
    return tuple(facs), tuple(steps), tuple(live), corners


def plan(d, k):
    return plan_complex(*complex_of(d, k))


def width(d, k):
    """the largest number of variables joined in one elimination step of the plan (cost 2^width per law)"""
    facs, steps, final, corners = plan(d, k)
    return max([len(set().union(*[set(facs[f]) for f in group])) for v, group, new in steps] + [d + 1])


def _mul(A, fa, B, fb, mod):
    out = tuple(sorted(set(fa) | set(fb)))
    lab = {u: LETTERS[i] for i, u in enumerate(out)}
    C = np.einsum("..." + "".join(lab[u] for u in fa) + ",..." + "".join(lab[u] for u in fb) + "->..." + "".join(lab[u] for u in out), A, B)
    if mod is not None:
        C %= mod
    return C, out


def contract_complex(cx, W, mod=None):
    """corner relation of a complex cx = (vertex count, simplices, corners), shape batch + (2,)*(d+1) in corner order"""
    nv, simp, corners = cx
    facs, steps, final, corners = plan_complex(nv, simp, corners)
    nb = W.ndim - len(corners)
    T = {i: W for i in range(len(simp))}
    for v, group, new in steps:
        P, fP = T.pop(group[0]), facs[group[0]]
        for g in group[1:]:
            P, fP = _mul(P, fP, T.pop(g), facs[g], mod)
        P = P.sum(axis=nb + fP.index(v))
        if mod is not None:
            P %= mod
        T[new] = P
    P, fP = T.pop(final[0]), facs[final[0]]
    for g in final[1:]:
        P, fP = _mul(P, fP, T.pop(g), facs[g], mod)
    perm = [fP.index(c) for c in corners]
    return np.transpose(P, list(range(nb)) + [nb + i for i in perm])


def contract(d, k, W, mod=None):
    """corner relation of SG^d_k, shape batch + (2,)*(d+1) in corner order (A, B_1, ..., B_d); W of shape batch + (2,)*(d+1)"""
    return contract_complex(complex_of(d, k), W, mod)


def corner_relation_mod(d, k, W, p, cx=None):
    return contract_complex(cx or complex_of(d, k), np.asarray(W, dtype=np.int64) % p, mod=p)


def corner_relation_int(d, k, W, primes=PRIMES[:4], cx=None):
    """exact integer corner relation by the Chinese remainder theorem (|values| below half the product of the primes)"""
    W = np.asarray(W, dtype=object)
    Rs = [corner_relation_mod(d, k, np.array(W % p, dtype=np.int64), p, cx) for p in primes]
    M = math.prod(primes)
    out = np.zeros(Rs[0].shape, dtype=object)
    for p, Rp in zip(primes, Rs):
        q = M // p
        out = out + Rp.astype(object) * (q * pow(q, -1, p))
    out = out % M
    return np.where(out > M // 2, out - M, out)


def corner_relation_float(d, k, W):
    return contract(d, k, np.asarray(W, dtype=float))


def tuples(d):
    return list(itertools.product((0, 1), repeat=d + 1))


def E(x):
    return sum((-1) ** xi for xi in x)


def table(d, f):
    W = np.zeros((2,) * (d + 1), dtype=object)
    for x in tuples(d):
        W[x] = f(x)
    return W


def wave(d, theta):
    """the standing wave w_theta(x) = (-1)^(x_0) sin(theta E)/sin(theta)"""
    return np.array(table(d, lambda x: (-1) ** x[0] * math.sin(theta * E(x)) / math.sin(theta)), dtype=float)


def cheb_u(n, y, mod=None):
    """sin((n+1) theta)/sin(theta) as a polynomial in y = 2 cos(theta), evaluated at y (U_n(y/2)); n >= -1, odd extension below"""
    if n < -1:
        return -cheb_u(-n - 2, y, mod)
    a, b = 0, 1  # U_{-1}, U_0
    for _ in range(n + 1):
        a, b = b, y * b - a
        if mod is not None:
            b %= mod
    return a


def wave_at(d, y, mod=None):
    """w_theta with y = 2 cos(theta) substituted (integers, or residues modulo mod): (-1)^(x_0) U_{E-1}(y/2)"""
    return table(d, lambda x: ((-1) ** x[0] * cheb_u(E(x) - 1, y, mod)) % mod if mod else (-1) ** x[0] * cheb_u(E(x) - 1, y))


def legendre(d):
    """(-1)^(x_0) (E | 3) = (-1)^d w_(pi/3)"""
    return table(d, lambda x: (-1) ** x[0] * (0, 1, -1)[E(x) % 3])


def tau(d):
    """1 + sum_i s_0 s_i = (-1)^(x_0) E = w_0 (the limit theta -> 0)"""
    return table(d, lambda x: (-1) ** x[0] * E(x))


def proportional_int(R, W):
    """(True, lambda) when R = lambda W exactly with lambda nonzero"""
    t0 = next(t for t in tuples(W.ndim - 1) if W[t] != 0)
    if R[t0] % W[t0] != 0:
        return False, None
    lam = R[t0] // W[t0]
    return bool(lam != 0 and all(R[t] == lam * W[t] for t in tuples(W.ndim - 1))), lam


def proportional_float(R, W):
    """(lambda, relative error of R - lambda W)"""
    t0 = max(tuples(W.ndim - 1), key=lambda t: abs(W[t]))
    lam = R[t0] / W[t0]
    err = float(np.max(np.abs(R - lam * W)) / max(1e-300, float(np.max(np.abs(R)))))
    return float(lam), err


def is_knot(allowed, n):
    """K1-K3 on a relation over n bits given as a set of allowed tuples: constrained, every one-variable projection full, nonempty"""
    allowed = set(allowed)
    if not allowed or len(allowed) == 2 ** n:
        return False
    for i in range(n):
        proj = {t[:i] + t[i + 1:] for t in allowed}
        if len(proj) < 2 ** (n - 1):
            return False
    return True


def interp_mod(xs, ys, p):
    """coefficients (low to high) of the polynomial of degree < len(xs) through the points, modulo p (Newton form)"""
    n = len(xs)
    coef = list(ys)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) * pow(xs[i] - xs[i - j], -1, p) % p
    poly = [0] * n
    for i in range(n - 1, -1, -1):
        new = [0] * n
        for a in range(n - 1):
            new[a + 1] = (new[a + 1] + poly[a]) % p
            new[a] = (new[a] - xs[i] * poly[a]) % p
        new[0] = (new[0] + coef[i]) % p
        poly = new
    return poly


def lambda_poly(d, k, primes=PRIMES[:3]):
    """the factor lambda as a polynomial in y = 2 cos(theta): (integer coefficients low to high by the Chinese remainder theorem, whether
    R = lambda w held at every sample, coefficients modulo each prime).  Samples y = 1, ..., d#T + 3 modulo each prime; at each, lambda is
    R(t0)/w(t0) for a tuple t0 with E = 1 (d even) or E = 2 (d odd), where w(t0) = +-1 or +-y."""
    nT, N = counts(d, k)
    M = d * nT + 3
    t0 = next(t for t in tuples(d) if E(t) == (1 if d % 2 == 0 else 2))
    per, ident = [], True
    for p in primes:
        ys = []
        for yv in range(1, M + 1):
            W = np.array(wave_at(d, yv, p), dtype=np.int64)
            R = corner_relation_mod(d, k, W, p)
            lam = int(R[t0]) * pow(int(W[t0]), -1, p) % p
            ident &= all((int(R[t]) - lam * int(W[t])) % p == 0 for t in tuples(d))
            ys.append(lam)
        per.append(interp_mod(list(range(1, M + 1)), ys, p))
    Mp = math.prod(primes)
    co = []
    for i in range(M):
        v = sum(per[j][i] * (Mp // p) * pow(Mp // p, -1, p) for j, p in enumerate(primes)) % Mp
        co.append(v - Mp if v > Mp // 2 else v)
    while co and co[-1] == 0:
        co.pop()
    return co, ident, per


def poly_eval(co, y):
    return sum(c * y ** i for i, c in enumerate(co))


def sector_lambda(d, k, theta):
    """lambda from the sector formula of the proof: D^(1 - #T) Z(1), Z(1) = sum over sectors s with s(T(0)) = +1 of prod_T s_T times, for every
    summed vertex u with S_u the sum of the sectors at u, zeta^S - zeta^-S if u is a base corner and zeta^S + zeta^-S otherwise"""
    V, simp, corners = gasket(d, k)
    nT = len(simp)
    zeta = complex(math.cos(theta), math.sin(theta))
    Dz = zeta - 1 / zeta
    inc = np.zeros((nT, len(V)), dtype=np.int64)
    for t, s in enumerate(simp):
        for u in s:
            inc[t, u] = 1
    base = {s[0] for s in simp}
    summed = [u for u in range(len(V)) if u not in corners]
    sig = np.array([[1] + [1 - 2 * b for b in bits] for bits in itertools.product((0, 1), repeat=nT - 1)], dtype=np.int64)
    S = sig @ inc
    val = np.prod(sig, axis=1).astype(complex)
    for u in summed:
        val *= zeta ** S[:, u] - zeta ** (-S[:, u]) if u in base else zeta ** S[:, u] + zeta ** (-S[:, u])
    return complex(val.sum() * Dz ** (1 - nT))


def edge_sets(d, k):
    """edge sets using at most one edge (v, v + e_i) per base corner v, with even degree at every vertex but the corners (direct enumeration)"""
    V, simp, corners = gasket(d, k)
    nT = len(simp)
    ch = np.array(list(itertools.product(range(d + 1), repeat=nT)), dtype=np.int8)
    deg = np.zeros((len(ch), len(V)), dtype=np.int8)
    for t, s in enumerate(simp):
        for i in range(1, d + 1):
            m = ch[:, t] == i
            deg[m, s[0]] += 1
            deg[m, s[i]] += 1
    summed = [u for u in range(len(V)) if u not in corners]
    ok = np.all(deg[:, summed] % 2 == 0, axis=1)
    return [frozenset((simp[t][0], simp[t][c]) for t, c in enumerate(row) if c) for row in ch[ok]]


def axis_paths(d, k):
    V, simp, corners = gasket(d, k)
    vid = {v: n for n, v in enumerate(V)}
    paths = []
    for i in range(d):
        pt = lambda j: vid[tuple(j * int(a == i) for a in range(d))]
        paths.append(frozenset((pt(j), pt(j + 1)) for j in range(k)))
    return paths
