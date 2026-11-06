"""Real weights under shared subdivision (SIGNED-SUBDIVISION-20261029-001B): gauge classes, explicit solution sets, exact algebra.

Uses ss_lib.py (copied unchanged from SIGNED-SUBDIVISION-20261029-001A-P001) for the rule shapes and the exact transfer-matrix sums.
- Sign classes: sign patterns on the knot's tuples (up tuples, then down tuples) modulo the sign gauge (global signs per law, and the
  edge sign functions of S1 or the corner sign functions with product one of S2), as cosets of a GF(2) subspace.
- Gauge slice: the real gauge (positive gauge functions and scales) acts on log|w| through an integer matrix G; magnitudes are fixed
  to 1 on a maximal set of tuples whose rows of G are independent, and free elsewhere.  Every nonzero real weighting is
  gauge-equivalent to (a sign-class representative) x (magnitudes in the slice).
- Solution sets: candidates from the explicit families of SHARED-SUBDIVISION-20261029-001B (Newman-Moore rows, colour-class
  patterns, configurations constant along one of the three lattice directions), verified triangle by triangle, and complete when
  their number equals trace(T^L) computed exactly modulo two primes."""
import itertools
from collections import Counter, defaultdict
import numpy as np
import sympy as sp
import ss_lib as S

PAIRS = list(itertools.product((0, 1), repeat=2))


def tuples(P1, P2):
    return sorted(P1), (sorted(P2) if P2 is not None else [])


# ------------------------------------------------------------------ gauge
def gauge_columns(P1, P2, signs=False):
    """columns of the gauge action on (up tuples, down tuples): integer (log) or GF(2) (signs)"""
    K1, K2 = tuples(P1, P2)
    cols = []
    if P2 is None:
        cols.append([1] * len(K1))
        betas = ((1, 1, 0), (0, 1, 1)) if signs else ((1, -1, 0), (0, 1, -1))
        for beta in betas:
            cols.append([sum(b * x for b, x in zip(beta, t)) % 2 if signs else sum(b * x for b, x in zip(beta, t)) for t in K1])
        return cols
    cols.append([1] * len(K1) + [0] * len(K2))
    cols.append([0] * len(K1) + [1] * len(K2))
    for cls in "HDV":
        for uv in PAIRS:
            col = [1 if {"H": (a, b), "D": (b, c), "V": (a, c)}[cls] == uv else 0 for (a, b, c) in K1]
            col += [(1 if signs else -1) if {"H": (e, f), "D": (d, e), "V": (d, f)}[cls] == uv else 0 for (d, e, f) in K2]
            cols.append(col)
    return cols


def _reduced_basis(vecs):
    basis = {}
    for v in vecs:
        for lb in sorted(basis, reverse=True):
            if (v >> lb) & 1:
                v ^= basis[lb]
        if v:
            lb = v.bit_length() - 1
            for b2 in list(basis):
                if (basis[b2] >> lb) & 1:
                    basis[b2] ^= v
            basis[lb] = v
    return basis


def _canon(v, basis):
    for lb in sorted(basis, reverse=True):
        if (v >> lb) & 1:
            v ^= basis[lb]
    return v


def sign_classes(P1, P2):
    """representatives (tuples of +-1, up then down) of the sign patterns modulo the sign gauge; and the class sizes"""
    n = len(P1) + (len(P2) if P2 is not None else 0)
    to_int = lambda col: sum((c % 2) << i for i, c in enumerate(col))
    basis = _reduced_basis([to_int(c) for c in gauge_columns(P1, P2, signs=True)])
    seen = Counter()
    for v in range(1 << n):
        seen[_canon(v, basis)] += 1
    reps = [tuple(-1 if (c >> i) & 1 else 1 for i in range(n)) for c in sorted(seen)]
    return reps, [seen[c] for c in sorted(seen)]


def slice_free(P1, P2):
    G = sp.Matrix(gauge_columns(P1, P2)).T  # n x g
    fixed, rank = [], 0
    for i in range(G.rows):
        if G.extract(fixed + [i], list(range(G.cols))).rank() > rank:
            fixed.append(i)
            rank += 1
    return [i for i in range(G.rows) if i not in fixed], rank


# ------------------------------------------------------------------ solution sets
def allowed(X, P1, P2):
    """X: (N, L, L) array, X[c, i, j]; True where every up (and down) triangle is allowed"""
    a = X; b = np.roll(X, -1, axis=1); c = np.roll(X, -1, axis=2)
    up = (a * 4 + b * 2 + c).reshape(len(X), -1)
    ok = np.isin(up, [t[0] * 4 + t[1] * 2 + t[2] for t in P1]).all(1)
    if P2 is not None:
        d = b; e = c; f = np.roll(b, -1, axis=2)
        dn = (d * 4 + e * 2 + f).reshape(len(X), -1)
        ok &= np.isin(dn, [t[0] * 4 + t[1] * 2 + t[2] for t in P2]).all(1)
    return ok


def candidates(L):
    i = np.arange(L)
    out = []
    rows = ((np.arange(1 << L)[:, None] >> i[None, :]) & 1).astype(np.int8)  # rows[r, i]
    for b in (0, 1):  # Newman-Moore: x(i, j+1) = x(i, j) + x(i+1, j) + b
        X = np.zeros((1 << L, L, L), dtype=np.int8)
        cur = rows.copy()
        for j in range(L):
            X[:, :, j] = cur
            cur = (cur + np.roll(cur, -1, axis=1) + b) % 2
        out.append(X[(cur == rows).all(1)])
    if L % 3 == 0:  # constant on the colour classes (i - j) mod 3
        col = (i[:, None] - i[None, :]) % 3
        out.append(np.array([np.array(v, dtype=np.int8)[col] for v in itertools.product((0, 1), repeat=3)]))
    for direction in ("i", "j", "i+j"):  # constant along one lattice direction
        idx = {"i": np.broadcast_to(i[:, None], (L, L)), "j": np.broadcast_to(i[None, :], (L, L)),
               "i+j": (i[:, None] + i[None, :]) % L}[direction]
        out.append(rows[:, idx])
    X = np.concatenate(out)
    return np.unique(X.reshape(len(X), -1), axis=0).reshape(-1, L, L)


def count_solutions(L, P1, P2, primes=S.PRIMES[:2]):
    """residues of trace(T^L), the number of solutions on the L-torus"""
    res = []
    for p in primes:
        T = S.transfer(L, S.wvec(P1, [1] * len(P1)), S.wvec(P2, [1] * len(P2)) if P2 is not None else None, p)
        R = np.eye(T.shape[0], dtype=np.int64)
        B, e = T, L
        while e:
            if e & 1:
                R = S._mm(R, B, p)
            e >>= 1
            if e:
                B = S._mm(B, B, p)
        res.append(int(np.trace(R) % p))
    return res


def solutions(L, P1, P2):
    """the solutions on the L-torus from the explicit families; raises if they are not all of them"""
    X = candidates(L)
    X = X[allowed(X, P1, P2)]
    cnt = count_solutions(L, P1, P2)
    if any(len(X) % p != c for p, c in zip(S.PRIMES[:2], cnt)):
        raise ValueError(f"explicit families incomplete on the {L}-torus: {len(X)} found, residues {cnt}")
    return X


def usage(X, P1, P2):
    """(N, n) counts of each allowed tuple (up tuples then down tuples) in each configuration"""
    K1, K2 = tuples(P1, P2)
    a = X; b = np.roll(X, -1, axis=1); c = np.roll(X, -1, axis=2)
    up = (a * 4 + b * 2 + c).reshape(len(X), -1)
    cols = [(up == t[0] * 4 + t[1] * 2 + t[2]).sum(1) for t in K1]
    if P2 is not None:
        dn = (b * 4 + c * 2 + np.roll(b, -1, axis=2)).reshape(len(X), -1)
        cols += [(dn == t[0] * 4 + t[1] * 2 + t[2]).sum(1) for t in K2]
    return np.stack(cols, 1)


def tables(m, k, P1, P2):
    """fine: {coarse key: Counter(usage tuple)}; coarse: {coarse key: usage tuple}"""
    Xf = solutions(k * m, P1, P2)
    Uf = usage(Xf, P1, P2)
    keys = Xf[:, ::k, ::k].reshape(len(Xf), -1)
    fine = defaultdict(Counter)
    for kk, u in zip(map(tuple, keys.tolist()), map(tuple, Uf.tolist())):
        fine[kk][u] += 1
    Xc = solutions(m, P1, P2)
    coarse = {tuple(x.reshape(-1).tolist()): tuple(u) for x, u in zip(Xc, usage(Xc, P1, P2).tolist())}
    return fine, coarse


# ------------------------------------------------------------------ exact algebra in the slice
def system(tabs, sign, free, syms):
    """exactness equations (F(x0) W(y) - F(y) W(x0) for coarse solutions y, F(y) for extended non-solutions y) and F(x0)"""
    eqs, Fx0s = [], []
    for fine, coarse in tabs:
        def mono(u):
            s = 1
            for t, e in enumerate(u):
                if sign[t] < 0 and e % 2:
                    s = -s
            return s * sp.Mul(*[syms[free.index(t)] ** u[t] for t in free])
        F = {x: sp.expand(sum(c * mono(u) for u, c in cnt.items())) for x, cnt in fine.items()}
        W = {x: mono(u) for x, u in coarse.items()}
        x0 = sorted(W)[0]
        Fx0 = F.get(x0, sp.Integer(0))
        Fx0s.append(Fx0)
        for y in W:
            e = sp.expand(Fx0 * W[y] - F.get(y, 0) * W[x0])
            if e != 0:
                eqs.append(e)
        for y, f in F.items():
            if y not in W and f != 0:
                eqs.append(f)
    return eqs, Fx0s


def positive_solutions(eqs, Fx0s, syms):
    """all points (without repetition) with positive free magnitudes where every equation vanishes and every F(x0) is nonzero.
    Returns ('all', None) if the system is empty (every point), else ('points', list of tuples of exact numbers)."""
    if not eqs:
        return "all", None
    if len(syms) == 1:
        x = syms[0]
        g = sp.Integer(0)
        for e in eqs:
            g = sp.gcd(g, e)
        if g == 0:
            return "all", None
        gp = sp.Poly(g, x)
        if gp.degree() <= 0:
            return "points", []
        pts = []
        for r in gp.sqf_part().real_roots():
            if r > 0 and all(sp.simplify(f.subs(x, r)) != 0 for f in Fx0s):
                pts.append((r,))
        return "points", pts
    G = sp.groebner(eqs, *syms, order="lex")
    if list(G.exprs) == [1]:
        return "points", []
    if not G.is_zero_dimensional:
        raise ValueError("positive-dimensional exactness locus: " + str(G.exprs)[:300])
    last = [g for g in G.exprs if g.free_symbols <= {syms[-1]}]
    pts = []
    for r in sp.Poly(last[0], syms[-1]).sqf_part().real_roots():
        if r <= 0:
            continue
        sub = [sp.expand(g.subs(syms[-1], r)) for g in G.exprs]
        sub = [g for g in sub if g != 0]
        h = sp.Integer(0)
        for g in sub:
            h = sp.gcd(h, g)
        for r0 in (sp.Poly(h, syms[0]).sqf_part().real_roots() if h.free_symbols else []):
            pt = {syms[0]: r0, syms[-1]: r}
            if r0 > 0 and all(sp.simplify(e.subs(pt)) == 0 for e in eqs) and all(sp.simplify(f.subs(pt)) != 0 for f in Fx0s):
                pts.append((r0, r))
    return "points", pts


# ------------------------------------------------------------------ exact and float sums for given weights
def fine_exact(m, k, wup, wdn, primes=S.PRIMES[:3]):
    """F(x) as Python integers (integer weights), by the Chinese remainder theorem over three primes (|F| < 2^52)"""
    Fs = [S.fine_sums(m, k, wup, wdn, p) for p in primes]
    M = 1
    for p in primes:
        M *= p
    out = {}
    for x in Fs[0]:
        v = 0
        for p, F in zip(primes, Fs):
            q = M // p
            v += F[x] * q * pow(q, -1, p)
        v %= M
        out[x] = v - M if v > M // 2 else v
    return out


def _transfer_float(L, wup, wdn):
    bits = S.bits_of(L)
    T = np.ones((1 << L, 1 << L))
    for i in range(L):
        a = bits[:, i][:, None]; b = bits[:, (i + 1) % L][:, None]; c = bits[:, i][None, :]
        T = T * wup[a * 4 + b * 2 + c]
        if wdn is not None:
            d = bits[:, (i + 1) % L][:, None]; e = bits[:, i][None, :]; f = bits[:, (i + 1) % L][None, :]
            T = T * wdn[d * 4 + e * 2 + f]
    return T


def fine_float(m, k, wup, wdn):
    L = k * m
    T = _transfer_float(L, np.asarray(wup, float), None if wdn is None else np.asarray(wdn, float))
    bits = S.bits_of(L)
    key = (bits[:, ::k] * (1 << np.arange(m))[None, :]).sum(1)
    Tk = np.linalg.matrix_power(T, k)
    B = [Tk * (key == x)[:, None] for x in range(1 << m)]
    out = {}
    for xs in itertools.product(range(1 << m), repeat=m):
        M = B[xs[0]]
        for x in xs[1:]:
            M = M @ B[x]
        out[xs] = float(np.trace(M))
    return out


def coarse_float(m, wup, wdn):
    T = _transfer_float(m, np.asarray(wup, float), None if wdn is None else np.asarray(wdn, float))
    return {xs: float(np.prod([T[xs[j], xs[(j + 1) % m]] for j in range(m)])) for xs in itertools.product(range(1 << m), repeat=m)}


def float_residual(m, k, wup, wdn):
    """|| F/|F| - s W/|W| || over the coarse assignments of the m-torus, s the sign of <F, W>"""
    F = fine_float(m, k, wup, wdn)
    W = coarse_float(m, wup, wdn)
    f = np.array([F[x] for x in sorted(F)]); w = np.array([W[x] for x in sorted(F)])
    f, w = f / np.linalg.norm(f), w / np.linalg.norm(w)
    return float(np.linalg.norm(f - np.sign(f @ w or 1.0) * w))


def candidates_all(L):
    """every assignment of the L-torus (L <= 4)"""
    n = L * L
    return ((np.arange(1 << n)[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8).reshape(-1, L, L)


_MINPOLY = {}


def vanishes_at(e, syms, pt):
    """exact test that the polynomial e vanishes at pt (real algebraic coordinates): rational coordinates are substituted; one
    remaining irrational coordinate is handled by reduction modulo its minimal polynomial; several by the minimal polynomial of
    the value"""
    rat = {x: v for x, v in zip(syms, pt) if getattr(v, "is_Rational", False)}
    irr = [(x, v) for x, v in zip(syms, pt) if not getattr(v, "is_Rational", False)]
    e1 = sp.expand(sp.sympify(e).subs(rat))
    if not irr:
        return e1 == 0
    if len(irr) == 1:
        x, v = irr[0]
        if v not in _MINPOLY:
            _MINPOLY[v] = sp.Poly(sp.minimal_polynomial(v, x), x)
        mp = _MINPOLY[v]
        return sp.Poly(e1, x).rem(sp.Poly(mp.as_expr(), x)).is_zero
    val = sp.expand(e1.subs(dict(irr)))
    if val == 0:
        return True
    z = sp.Dummy("z")
    return sp.minimal_polynomial(val, z) == z
