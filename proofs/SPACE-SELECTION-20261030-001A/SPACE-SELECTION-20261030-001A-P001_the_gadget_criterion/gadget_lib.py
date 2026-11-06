"""Gadgets for the standing wave (SPACE-SELECTION-20261030-001A).

A gadget with n triangles: triangle t has slots (t, r) in roles r = 0, 1, 2 (a, b, c).  Corner A fills slot (0, 0), corner B slot (tB, 1),
corner C slot (tC, 2); every other slot belongs to an inner vertex, a block of at least two slots from distinct triangles; the triangles are
connected through inner vertices.  A key (tB, tC, blocks) describes a gadget; complex_of turns it into (vertex count, triangles as vertex
triples in role order, corners (A, B, C) = (0, 1, 2)).

Laws are 3-bit tables W[x_a, x_b, x_c] (bit x, spin s = 1 - 2x).  Three pencils through a not-all-equal knot, parameter t = 0 the knot:
  sine    (-1)^a (t, 1, -1, -t)[x_a + x_b + x_c]   the standing wave, t = q = sin(3 theta) / sin(theta) = 1 + 2 cos(2 theta)
  cosine  (-1)^a (t, 1, 1, t)[...]                 the cosine wave, t = p = cos(3 theta) / cos(theta) = 2 cos(2 theta) - 1
  plain   (t, 1, 1, t)[...]                        no signs; t = 0 is plain not-all-equal
The corner relation R(x_A, x_B, x_C) sums the product of the law over the inner vertices.  The law is exact on the gadget when R is a nonzero
multiple of the law.  Corner relations are computed by direct summation over the inner spins at integer parameter values and interpolated
exactly (degree <= n in the parameter)."""
import itertools, math
from fractions import Fraction
from functools import lru_cache
import numpy as np

TU = list(itertools.product((0, 1), repeat=3))
FAM = {
    'sine': lambda x, t: (-1) ** x[0] * (t, 1, -1, -t)[sum(x)],
    'cosine': lambda x, t: (-1) ** x[0] * (t, 1, 1, t)[sum(x)],
    'plain': lambda x, t: (t, 1, 1, t)[sum(x)],
}
QS = tuple(range(-4, 5))


# ------------------------------------------------------------------------------------------------ enumeration
def partitions(slots):
    """set partitions of slots into blocks of size >= 2, no two slots of one triangle in a block"""
    out = []

    def rec(i, blocks):
        if i == len(slots):
            if all(len(b) >= 2 for b in blocks):
                out.append([tuple(b) for b in blocks])
            return
        if sum(1 for b in blocks if len(b) == 1) > len(slots) - i:
            return
        s = slots[i]
        for b in blocks:
            if all(x[0] != s[0] for x in b):
                b.append(s)
                rec(i + 1, blocks)
                b.pop()
        blocks.append([s])
        rec(i + 1, blocks)
        blocks.pop()
    rec(0, [])
    return out


def canonical(n, tB, tC, blocks):
    """canonical key under relabelings of triangles 1..n-1 (triangle 0 holds A)"""
    best = None
    for perm in itertools.permutations(range(1, n)):
        p = (0,) + perm
        key = (p[tB], p[tC], tuple(sorted(tuple(sorted((p[t], r) for t, r in b)) for b in blocks)))
        if best is None or key < best:
            best = key
    return best


def connected(n, blocks):
    parent = list(range(n))

    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for b in blocks:
        for t, r in b[1:]:
            parent[f(t)] = f(b[0][0])
    return len({f(t) for t in range(n)}) == 1


def gadgets(n):
    """all gadgets with n triangles up to isomorphism (relabeling triangles and inner vertices), as canonical keys"""
    seen = set()
    for tB in range(min(n, 2)):
        for tC in range(min(n, 3)):
            if tC > tB + 1:
                continue
            slots = [(t, r) for t in range(n) for r in range(3) if (t, r) not in {(0, 0), (tB, 1), (tC, 2)}]
            for blocks in partitions(slots):
                if connected(n, blocks):
                    seen.add(canonical(n, tB, tC, blocks))
    return seen


def complex_of(n, key):
    tB, tC, blocks = key
    where = {(0, 0): 0, (tB, 1): 1, (tC, 2): 2}
    for j, b in enumerate(blocks):
        for s in b:
            where[s] = 3 + j
    return (3 + len(blocks), tuple(tuple(where[(t, r)] for r in range(3)) for t in range(n)), (0, 1, 2))


def linear(cx):
    """any two triangles share at most one vertex"""
    return all(len(set(s) & set(t)) <= 1 for s, t in itertools.combinations(cx[1], 2))


# ------------------------------------------------------------------------------------------------ corner relations
def corner_values(cx, W):
    """corner relation for a batch of laws W (shape (m, 2, 2, 2)), by direct summation over inner spins: shape (m, 2, 2, 2), exact for
    integer W of moderate size (object dtype keeps it exact)"""
    nv, tris, corners = cx
    inner = [v for v in range(nv) if v not in corners]
    W = np.asarray(W, dtype=object)
    out = np.zeros((W.shape[0], 2, 2, 2), dtype=object)
    states = list(itertools.product((0, 1), repeat=len(inner)))
    for c in TU:
        val = dict(zip(corners, c))
        tot = np.zeros(W.shape[0], dtype=object)
        for s in states:
            val.update(zip(inner, s))
            term = np.ones(W.shape[0], dtype=object)
            for tri in tris:
                term = term * W[:, val[tri[0]], val[tri[1]], val[tri[2]]]
            tot = tot + term
        out[(slice(None),) + c] = tot
    return out


def fast_values(cx, W):
    """the same with int64 numpy vectorization (exact while |values| < 2^62); W shape (m, 2, 2, 2)"""
    nv, tris, corners = cx
    inner = [v for v in range(nv) if v not in corners]
    N = len(inner)
    pos = {v: i for i, v in enumerate(inner)}
    st = np.array(list(itertools.product((0, 1), repeat=N)), dtype=np.int64).reshape(-1, N) if N else np.zeros((1, 0), dtype=np.int64)
    W = np.asarray(W, dtype=np.int64).reshape(W.shape[0], 8)
    out = np.zeros((W.shape[0], 2, 2, 2), dtype=np.int64)
    for c in TU:
        bits = {corners[i]: np.full(st.shape[0], c[i], dtype=np.int64) for i in range(3)}
        for v in inner:
            bits[v] = st[:, pos[v]]
        term = np.ones((W.shape[0], st.shape[0]), dtype=np.int64)
        for tri in tris:
            idx = 4 * bits[tri[0]] + 2 * bits[tri[1]] + bits[tri[2]]
            term *= W[:, idx]
        out[(slice(None),) + c] = term.sum(axis=1)
    return out


@lru_cache(None)
def law_batch(fam, qs=QS):
    W = np.zeros((len(qs), 2, 2, 2), dtype=np.int64)
    for i, t in enumerate(qs):
        for x in TU:
            W[(i,) + x] = FAM[fam](x, t)
    return W


@lru_cache(None)
def _vinv(n, qs=QS):
    pts = qs[:n + 1]
    M = [[Fraction(t) ** j for j in range(n + 1)] for t in pts]
    k = n + 1
    A = [row[:] + [Fraction(int(i == j)) for j in range(k)] for i, row in enumerate(M)]
    for col in range(k):
        piv = next(r for r in range(col, k) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
    return [row[k:] for row in A]


def pnorm(c):
    c = list(c)
    while c and c[-1] == 0:
        c.pop()
    return c


def interpolate(vals, n, qs=QS):
    """ascending integer coefficients of the polynomial of degree <= n through (qs, vals), checked at every point"""
    V = _vinv(n, qs)
    c = [sum(V[i][j] * vals[j] for j in range(n + 1)) for i in range(n + 1)]
    assert all(x.denominator == 1 for x in c), "non-integer coefficient"
    c = pnorm(int(x) for x in c)
    assert all(sum(ci * t ** i for i, ci in enumerate(c)) == v for t, v in zip(qs, vals)), "degree check failed"
    return c


def points(n):
    """integer parameter values for degree <= n: QS, or a wider symmetric range"""
    if len(QS) >= n + 2:
        return QS
    k = (n + 2) // 2
    return tuple(range(-k, k + 1))


def relation_polys(cx, fam, fast=True):
    """the corner relation as integer polynomials in the pencil parameter: dict corner bits -> ascending coefficients"""
    n = len(cx[1])
    qs = points(n)
    R = (fast_values if fast else corner_values)(cx, law_batch(fam, qs))
    return {x: interpolate([int(R[(i,) + x]) for i in range(len(qs))], n, qs) for x in TU}


def pmul(a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def psub(a, b):
    m = max(len(a), len(b))
    return pnorm([(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(m)])


def pgcd(a, b):
    a, b = [Fraction(x) for x in a], [Fraction(x) for x in b]
    while b:
        r = a[:]
        while len(r) >= len(b) and r:
            f = r[-1] / b[-1]
            sh = len(r) - len(b)
            for i, y in enumerate(b):
                r[sh + i] -= f * y
            r = pnorm(r)
        a, b = b, r
    return [x / a[-1] for x in a]


def peval(c, t):
    return sum(ci * t ** i for i, ci in enumerate(c))


def classify(polys, fam):
    """('generic', lambda, None) when the corner relation is lambda(t) times the law identically; ('special', lambda, G) with G the monic gcd
    (ascending Fractions) of the proportionality defects, whose roots outside the zeros of lambda are the parameters where the law is exact;
    ('none', lambda, None) when the defects have no common root; ('zero', [], None) when lambda vanishes identically"""
    lam = polys[(0, 0, 1)]
    if not lam:
        return ('zero', [], None)
    defects = []
    for x in TU:
        tx = pnorm([FAM[fam](x, 0), FAM[fam](x, 1) - FAM[fam](x, 0)])
        d = psub(polys[x], pmul(lam, tx))
        if d:
            defects.append(d)
    if not defects:
        return ('generic', lam, None)
    g = defects[0]
    for d in defects[1:]:
        g = pgcd(g, d)
        if len(g) == 1:
            break
    return ('special', lam, g) if len(g) > 1 else ('none', lam, None)


def exact_at(cls, t):
    """exactness at the parameter value t (an integer or Fraction)"""
    kind, lam, g = cls
    if kind == 'generic':
        return peval(lam, t) != 0
    if kind == 'special':
        return peval(g, t) == 0 and peval(lam, t) != 0
    return False


# ------------------------------------------------------------------------------------------------ sectors
def incidences(cx):
    nv, tris, corners = cx
    inc = {}
    for t, tri in enumerate(tris):
        for r, v in enumerate(tri):
            inc.setdefault(v, []).append((t, r))
    return inc


def corner_triangles(cx):
    tris = cx[1]
    return (next(t for t, tri in enumerate(tris) if tri[0] == 0), next(t for t, tri in enumerate(tris) if tri[1] == 1),
            next(t for t, tri in enumerate(tris) if tri[2] == 2))


def base_parity(cx):
    """m_v = number of role-a incidences of each inner vertex"""
    inc = incidences(cx)
    return {v: sum(1 for t, r in lst if r == 0) for v, lst in inc.items() if v not in cx[2]}


def lmul(a, b):
    out = {}
    for i, x in a.items():
        for j, y in b.items():
            out[i + j] = out.get(i + j, 0) + x * y
    return {k: v for k, v in out.items() if v}


def ladd(a, b, s=1):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + s * v
    return {k: v for k, v in out.items() if v}


def vertex_factor(m, S):
    """f(S) = zeta^S + (-1)^m zeta^-S as a Laurent polynomial {exponent: coefficient}"""
    if S == 0:
        return {0: 2} if m % 2 == 0 else {}
    return {S: 1, -S: (-1) ** (m % 2)}


def sector_sums(cx, signed=True):
    """Z(eps) for the eight corner sector patterns: sum over sector assignments sigma extending eps of (prod sigma if signed) times prod_v
    f_v(S_v), S_v the sum of the sectors at v.  Then R_theta = (zeta - 1/zeta)^-n sum_eps s_A zeta^(eps . s) Z(eps) for the standing wave
    (signed) and (zeta + 1/zeta)^-n times the same for the cosine wave (unsigned)."""
    nv, tris, corners = cx
    n = len(tris)
    inc = incidences(cx)
    m = base_parity(cx)
    tA, tB, tC = corner_triangles(cx)
    Z = {e: {} for e in itertools.product((1, -1), repeat=3)}
    for sig in itertools.product((1, -1), repeat=n):
        term = {0: math.prod(sig) if signed else 1}
        for v, mv in m.items():
            term = lmul(term, vertex_factor(mv, sum(sig[t] for t, r in inc[v])))
            if not term:
                break
        e = (sig[tA], sig[tB], sig[tC])
        Z[e] = ladd(Z[e], term)
    return Z


def mixed(e):
    return not (e[0] == e[1] == e[2])


def mechanism(cx, k=0):
    """how the mixed corner patterns vanish, at generic angle (k = 0) or at theta = pi/k: 'lock' when every mixed sector assignment has a
    vertex factor vanishing there; 'balanced' when the survivors cancel within classes of equal factor multisets (generic only); else
    'algebraic' (generic), 'none' at an angle"""
    nv, tris, corners = cx
    n = len(tris)
    inc = incidences(cx)
    m = base_parity(cx)
    tA, tB, tC = corner_triangles(cx)

    def zero(mv, S):
        if k == 0:
            return mv % 2 == 1 and S == 0
        return S % k == 0 if mv % 2 == 1 else (2 * S) % (2 * k) == k
    kinds = set()
    classes = {}
    for sig in itertools.product((1, -1), repeat=n):
        e = (sig[tA], sig[tB], sig[tC])
        if not mixed(e):
            continue
        S = {v: sum(sig[t] for t, r in inc[v]) for v in m}
        if any(zero(m[v], S[v]) for v in m):
            continue
        if k:
            return 'none'
        sign = math.prod(sig) * math.prod((1 if S[v] > 0 else -1) for v in m if m[v] % 2 == 1)
        key = (e, tuple(sorted((m[v] % 2, abs(S[v])) for v in m)))
        classes[key] = classes.get(key, 0) + sign
    if not classes:
        return 'lock'
    return 'balanced' if all(c == 0 for c in classes.values()) else 'algebraic'


# ------------------------------------------------------------------------------------------------ growth of corner chains
def corner_paths(cx):
    """Pareto-minimal traversal-count vectors (ab, ac, bc) of simple corner paths, for the corner pairs AB, AC, BC"""
    nv, tris, corners = cx
    adj = {}
    for tri in tris:
        for (i, j), col in (((0, 1), 0), ((0, 2), 1), ((1, 2), 2)):
            adj.setdefault(tri[i], []).append((tri[j], col))
            adj.setdefault(tri[j], []).append((tri[i], col))

    def paths(src, dst):
        found = set()

        def rec(u, seen, cnt):
            if u == dst:
                found.add(tuple(cnt))
                return
            for v, col in adj.get(u, []):
                if v not in seen:
                    cnt[col] += 1
                    seen.add(v)
                    rec(v, seen, cnt)
                    cnt[col] -= 1
                    seen.discard(v)
        rec(src, {src}, [0, 0, 0])
        return sorted(c for c in found if not any(d != c and all(d[i] <= c[i] for i in range(3)) for d in found))
    A, B, C = corners
    return [paths(A, B), paths(A, C), paths(B, C)]


def growth(cx):
    """(rho, policy matrix): the least spectral radius over choices of one minimal corner path per corner pair; the corner chains of the
    tower grow like k^j rho^k"""
    best = None
    for rows in itertools.product(*corner_paths(cx)):
        M = np.array(rows, dtype=float)
        ev = float(max(abs(np.linalg.eigvals(M))))
        if best is None or ev < best[0] - 1e-12:
            best = (ev, rows)
    return best


def chain_lengths(cx, levels):
    """exact corner chain lengths (number of triangles in a shortest chain AB, AC, BC) of the tower levels 0..levels"""
    import heapq
    nv, tris, corners = cx
    d = [1, 1, 1]
    hist = [d]
    for _ in range(levels):
        adj = {}
        for tri in tris:
            for (i, j), col in (((0, 1), 0), ((0, 2), 1), ((1, 2), 2)):
                adj.setdefault(tri[i], []).append((tri[j], d[col]))
                adj.setdefault(tri[j], []).append((tri[i], d[col]))

        def dist(s, t):
            D = {s: 0}
            pq = [(0, s)]
            while pq:
                du, u = heapq.heappop(pq)
                if u == t:
                    return du
                if du > D[u]:
                    continue
                for v, w in adj.get(u, []):
                    if du + w < D.get(v, float('inf')):
                        D[v] = du + w
                        heapq.heappush(pq, (D[v], v))
        A, B, C = corners
        d = [dist(A, B), dist(A, C), dist(B, C)]
        hist.append(d)
    return hist


# ------------------------------------------------------------------------------------------------ substitution
def substitute(G, t, H):
    """replace triangle t of the complex G by a copy of the complex H, its corners (A, B, C) glued to the vertices of t in roles (a, b, c)"""
    nvG, trisG, cornersG = G
    nvH, trisH, cornersH = H
    tri = trisG[t]
    vmap = {cornersH[i]: tri[i] for i in range(3)}
    nxt = nvG
    for v in range(nvH):
        if v not in vmap:
            vmap[v] = nxt
            nxt += 1
    new = [tr for i, tr in enumerate(trisG) if i != t] + [tuple(vmap[v] for v in tr) for tr in trisH]
    return (nxt, tuple(new), cornersG)


def substitute_all(G, H):
    out = G
    for t in reversed(range(len(G[1]))):
        out = substitute(out, t, H)
    return out


def attach(G, v, H, at):
    """glue the complex H (a tadpole) to G by identifying its vertex `at` with the vertex v of G"""
    nvG, trisG, cornersG = G
    nvH, trisH, _ = H
    vmap = {at: v}
    nxt = nvG
    for u in range(nvH):
        if u not in vmap:
            vmap[u] = nxt
            nxt += 1
    return (nxt, trisG + tuple(tuple(vmap[u] for u in tr) for tr in trisH), cornersG)
