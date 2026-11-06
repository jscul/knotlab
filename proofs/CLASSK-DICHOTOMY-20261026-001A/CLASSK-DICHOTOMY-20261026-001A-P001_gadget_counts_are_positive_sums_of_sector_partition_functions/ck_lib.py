"""Class-(K) groups over F_p with a split C_r action, gadget triple products and sector partition functions.

Used by CLASSK-DICHOTOMY-20261026-001A (proof check) and, read-only, by the later tickets of the epic.

Conventions.
- p is an odd prime, r | p - 1 and Z is a fixed element of order r in F_p^x. A character of C_r is an exponent e in Z/r: the
  generator acts by Z^e. Products of characters add exponents; the inverse negates; the trivial character is 0.
- G = N x| C_r of class (K) is given by eigenbases of B and A with exponents bexp[i], aexp[j] and a bilinear equivariant cocycle
  beta (dict (i, i2, j) -> value). The commutator pairing is kappa = beta - beta^T. For p odd the count depends on kappa only.
- A gadget model is the cohomological data of a gadget surgery: spaces V_theta (theta in the slot set S) with coordinates, and
  the alternating triple-product form T = sum over edges of f1 ^ f2 ^ f3 (zero on every component that is not a permutation
  of S). Spaces V_theta for theta outside S carry no form; they enter only through their dimensions d_theta(n, m).
"""
import itertools

import numpy as np


# ------------------------------------------------------------------------------------------------ arithmetic mod p

def elem_of_order(p, r):
    """the smallest element of F_p^x of exact order r"""
    for g in range(2, p):
        if pow(g, r, p) == 1 and all(pow(g, r // q, p) != 1 for q in prime_factors(r)):
            return g
    assert r == 1
    return 1


def prime_factors(n):
    out, d = set(), 2
    while d * d <= n:
        while n % d == 0:
            out.add(d)
            n //= d
        d += 1
    if n > 1:
        out.add(n)
    return out


def rref(rows, p):
    """reduced row echelon form mod p of a list of rows; returns (rows, pivots)"""
    rows = [[x % p for x in r] for r in rows]
    piv, rk = [], 0
    ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        k = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if k is None:
            continue
        rows[rk], rows[k] = rows[k], rows[rk]
        iv = pow(rows[rk][c], p - 2, p)
        rows[rk] = [x * iv % p for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(x - f * y) % p for x, y in zip(rows[i], rows[rk])]
        piv.append(c)
        rk += 1
    return rows[:rk], piv


def rank(rows, p):
    return len(rref(rows, p)[0]) if rows and rows[0] else 0


def nullspace(rows, n, p):
    """basis of {x in F_p^n : rows x = 0}"""
    if not rows:
        return [[int(i == j) for j in range(n)] for i in range(n)]
    R, piv = rref(rows, p)
    free = [j for j in range(n) if j not in set(piv)]
    out = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for row, c in zip(R, piv):
            v[c] = (-row[f]) % p
        out.append(v)
    return out


def batch_rank(A, p):
    """ranks mod p of a batch of matrices A (P, m, n) (int64), by vectorized Gaussian elimination"""
    A = np.array(A, dtype=np.int64) % p
    P, m, n = A.shape
    row = np.zeros(P, dtype=np.int64)
    if P == 0 or m == 0 or n == 0:
        return row
    inv = np.array([0] + [pow(x, p - 2, p) for x in range(1, p)], dtype=np.int64)
    idx = np.arange(m)[None, :]
    for c in range(n):
        cand = (A[:, :, c] != 0) & (idx >= row[:, None])
        has = cand.any(axis=1)
        if not has.any():
            continue
        b = np.nonzero(has)[0]
        piv = np.argmax(cand[b], axis=1)
        r0 = row[b]
        top = A[b, r0, :].copy()
        A[b, r0, :] = A[b, piv, :]
        A[b, piv, :] = top
        A[b, r0, :] = (A[b, r0, :] * inv[A[b, r0, c]][:, None]) % p
        f = A[b, :, c].copy()
        f[np.arange(len(b)), r0] = 0
        A[b] = (A[b] - f[:, :, None] * A[b, r0, :][:, None, :]) % p
        row[b] += 1
    return row


def all_vectors(p, d):
    """all of F_p^d as an array (p^d, d)"""
    if d == 0:
        return np.zeros((1, 0), dtype=np.int64)
    return np.array(list(itertools.product(range(p), repeat=d)), dtype=np.int64)


# ------------------------------------------------------------------------------------------------ class-(K) groups

class KGroup:
    """G = N x| C_r with N = A x B, (a, b)(a', b') = (a + a' + beta(b, b'), b + b'), eigenbases with exponents"""

    def __init__(self, p, r, bexp, aexp, beta):
        self.p, self.r = p, r
        self.bexp, self.aexp = [e % r for e in bexp], [e % r for e in aexp]
        self.Z = elem_of_order(p, r)
        self.beta = {}
        for (i, i2, j), v in beta.items():
            v %= p
            if v:
                assert (self.bexp[i] + self.bexp[i2] - self.aexp[j]) % r == 0, "beta not equivariant"
                self.beta[(i, i2, j)] = (self.beta.get((i, i2, j), 0) + v) % p
        self.kap = {}
        for (i, i2, j), v in self.beta.items():
            self.kap[(i, i2, j)] = (self.kap.get((i, i2, j), 0) + v) % p
            self.kap[(i2, i, j)] = (self.kap.get((i2, i, j), 0) - v) % p
        self.kap = {k: v for k, v in self.kap.items() if v}
        self.bmul = [pow(self.Z, e, p) for e in self.bexp]
        self.amul = [pow(self.Z, e, p) for e in self.aexp]

    @property
    def dB(self):
        return len(self.bexp)

    @property
    def dA(self):
        return len(self.aexp)

    def kappa_entry(self, i, i2, j):
        return self.kap.get((i, i2, j), 0)

    def hard_pairs(self):
        """exponent pairs (e, e2) with e, e2, e + e2 nonzero carrying a nonzero commutator component"""
        out = set()
        for (i, i2, j), v in self.kap.items():
            e, e2 = self.bexp[i], self.bexp[i2]
            if e and e2 and (e + e2) % self.r:
                out.add((e, e2))
        return out

    def alternating_version(self):
        """the same group with beta replaced by kappa / 2 (p odd): an equivariant change of section"""
        h = pow(2, self.p - 2, self.p)
        return KGroup(self.p, self.r, self.bexp, self.aexp, {k: v * h % self.p for k, v in self.kap.items()})

    # group law, for independent lifting counts
    def act(self, e, a, b):
        p = self.p
        return (tuple(pow(m, e, p) * x % p for m, x in zip(self.amul, a)),
                tuple(pow(m, e, p) * x % p for m, x in zip(self.bmul, b)))

    def mul(self, g1, g2):
        (a, b, e), (a2, b2, e2) = g1, g2
        p = self.p
        ta, tb = self.act(e, a2, b2)
        out = [(x + y) % p for x, y in zip(a, ta)]
        for (i, i2, j), v in self.beta.items():
            if b[i] and tb[i2]:
                out[j] = (out[j] + v * b[i] * tb[i2]) % p
        return (tuple(out), tuple((x + y) % p for x, y in zip(b, tb)), (e + e2) % self.r)

    def identity(self):
        return (tuple([0] * self.dA), tuple([0] * self.dB), 0)

    def inv(self, g):
        a, b, e = g
        p = self.p
        # (a, b, e)^-1 = (e^-1)(a, b)^-1 with (a, b)^-1 = (-a + beta(b, b), -b)
        na = [(-x) % p for x in a]
        for (i, i2, j), v in self.beta.items():
            na[j] = (na[j] + v * b[i] * b[i2]) % p
        nb = tuple((-x) % p for x in b)
        ta, tb = self.act((-e) % self.r, tuple(na), nb)
        return (ta, tb, (-e) % self.r)

    def word(self, w, images):
        out = self.identity()
        for g, s in w:
            x = images[g] if s > 0 else self.inv(images[g])
            for _ in range(abs(s)):
                out = self.mul(out, x)
        return out

    def regraded(self, k):
        """the coordinates of B and A grouped by the exponent of the k-th power of the action"""
        B, A = {}, {}
        for i, e in enumerate(self.bexp):
            B.setdefault(k * e % self.r, []).append(i)
        for j, e in enumerate(self.aexp):
            A.setdefault(k * e % self.r, []).append(j)
        return B, A


def random_kgroup(rng, p, r, bexp, density=0.7, alt_only=False, reuse=0.5):
    """a random class-(K) group with B exponents bexp; one A coordinate per needed exponent and pair (free-ish), with random
    equivariant entries; beta random bilinear (not alternating unless alt_only)"""
    aexp, beta = [], {}
    slots = {}
    pairs = [(i, i2) for i in range(len(bexp)) for i2 in range(len(bexp)) if (alt_only and i < i2) or not alt_only]
    for (i, i2) in pairs:
        if rng.random() > density:
            continue
        e = (bexp[i] + bexp[i2]) % r
        # reuse an A coordinate of the same exponent sometimes, so components share targets
        if e in slots and rng.random() < reuse:
            j = rng.choice(slots[e])
        else:
            j = len(aexp)
            aexp.append(e)
            slots.setdefault(e, []).append(j)
        beta[(i, i2, j)] = rng.randrange(1, p)
    if not aexp:
        aexp = [0]
    return KGroup(p, r, bexp, aexp, beta)


# ------------------------------------------------------------------------------------------------ gadget models

def pattern_of(S, r):
    s1, s2, s3 = (x % r for x in S)
    assert (s1 + s2 + s3) % r == 0 and s1 and s2 and s3
    if len({s1, s2, s3}) == 3:
        return "distinct"
    if len({s1, s2, s3}) == 1:
        return "sss"
    return "sst"


def normalize_slots(S, r):
    """order a slot triple as (a, b, c) distinct, (s, s, t), or (s, s, s)"""
    S = tuple(x % r for x in S)
    pat = pattern_of(S, r)
    if pat == "sst":
        s = next(x for x in S if S.count(x) == 2)
        t = next(x for x in S if S.count(x) == 1)
        return (s, s, t), pat
    return S, pat


class Gadget:
    """coordinates and the alternating triple-product form of the gadget tensor of a multigraph (n vertices, edges (u, v))"""

    def __init__(self, S, n, edges, r, p):
        self.S, self.pattern = normalize_slots(S, r)
        self.r, self.p, self.n, self.edges = r, p, n, list(edges)
        m = len(self.edges)
        s1, s2, s3 = self.S
        coords = []                       # (theta, label)
        xs = [len(coords) + u for u in range(n)]
        coords += [(s1, ("x", u)) for u in range(n)]
        if self.pattern == "distinct":
            ys = list(range(len(coords), len(coords) + m))
            coords += [(s2, ("y", e)) for e in range(m)]
            ts = list(range(len(coords), len(coords) + m))
            coords += [(s3, ("t", e)) for e in range(m)]
        elif self.pattern == "sst":
            ys = list(range(len(coords), len(coords) + m))
            coords += [(s1, ("p", e)) for e in range(m)]
            ts = list(range(len(coords), len(coords) + m))
            coords += [(s3, ("w", e)) for e in range(m)]
        else:
            ys = list(range(len(coords), len(coords) + m))
            coords += [(s1, ("p", e)) for e in range(m)]
            ts = list(range(len(coords), len(coords) + m))
            coords += [(s1, ("q", e)) for e in range(m)]
        self.coords = coords
        self.dim = len(coords)
        self.thetas = sorted({s1, s2, s3})
        self.coords_of = {th: [a for a, (t, _) in enumerate(coords) if t == th] for th in self.thetas}
        # functionals per edge: f1 = x_u - x_v, f2 = y_e (or p_e), f3 = t_e (or w_e, q_e)
        self.funcs = []
        for e, (u, v) in enumerate(self.edges):
            f1 = {}
            f1[xs[u]] = f1.get(xs[u], 0) + 1
            f1[xs[v]] = f1.get(xs[v], 0) - 1
            self.funcs.append((f1, {ys[e]: 1}, {ts[e]: 1}))
        self.T = self._tensor()

    def _tensor(self):
        p, d = self.p, self.dim
        T = np.zeros((d, d, d), dtype=np.int64)
        for f1, f2, f3 in self.funcs:
            F = [f1, f2, f3]
            supp = sorted(set(f1) | set(f2) | set(f3))
            for a in supp:
                for b in supp:
                    for c in supp:
                        M = [[F[i].get(a, 0), F[i].get(b, 0), F[i].get(c, 0)] for i in range(3)]
                        det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
                               - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                               + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
                        T[a, b, c] = (T[a, b, c] + det) % p
        return T

    def summand_counts(self):
        """twist-knot summands of the base, by type: {exponent: count}"""
        n, m = self.n, len(self.edges)
        s1, s2, s3 = self.S
        if self.pattern == "distinct":
            return {s1: n, s2: m, s3: m}
        if self.pattern == "sst":
            return {s1: n + m, s3: m}
        return {s1: n + 2 * m}


def base_dims(pattern_counts, r):
    """d_theta = number of summands whose root set {tau, -tau} contains theta"""
    d = {}
    for tau, c in pattern_counts.items():
        for th in {tau % r, (-tau) % r}:
            d[th] = d.get(th, 0) + c
    return d


def dims_linear(S, r):
    """d_theta(n, m) = (coefficient of n, coefficient of m) for the base of the pattern of S"""
    Sn, pat = normalize_slots(S, r)
    s1, s2, s3 = Sn
    if pat == "distinct":
        types = {s1: (1, 0), s2: (0, 1), s3: (0, 1)}
    elif pat == "sst":
        types = {s1: (1, 1), s3: (0, 1)}
    else:
        types = {s1: (1, 2)}
    d = {}
    for tau, (cn, cm) in types.items():
        for th in {tau % r, (-tau) % r}:
            a, b = d.get(th, (0, 0))
            d[th] = (a + cn, b + cm)
    return d


# ------------------------------------------------------------------------------------------------ counting

def count_bilinear_zeros(p, groups, forms, chunk=20000, max_enum=None):
    """#{x : every form vanishes}, x = concatenation of the variable groups; each form is a dict {(v1, v2): coef} of
    monomials x_v1 x_v2 (no squares within a group are allowed unless the group is enumerated). A minimum-weight vertex cover
    of the group interaction graph is enumerated; the rest is linear."""
    nvar = sum(len(g) for g in groups)
    gof = {}
    for gi, g in enumerate(groups):
        for v in g:
            gof[v] = gi
    inter, self_loop = set(), set()
    for f in forms:
        for (v1, v2), c in f.items():
            if c % p == 0:
                continue
            g1, g2 = gof[v1], gof[v2]
            if g1 == g2:
                self_loop.add(g1)
            else:
                inter.add((min(g1, g2), max(g1, g2)))
    best = None
    ng = len(groups)
    for mask in range(1 << ng):
        cov = {gi for gi in range(ng) if mask >> gi & 1}
        if not self_loop <= cov or any(a not in cov and b not in cov for a, b in inter):
            continue
        w = sum(len(groups[gi]) for gi in cov)
        if best is None or w < best[0]:
            best = (w, cov)
    cov = best[1]
    if max_enum is not None and p ** best[0] > max_enum:
        return None, nvar, best[0]
    cvars = [v for gi in sorted(cov) for v in groups[gi]]
    rvars = [v for gi in range(ng) if gi not in cov for v in groups[gi]]
    ci = {v: k for k, v in enumerate(cvars)}
    ri = {v: k for k, v in enumerate(rvars)}
    nf, nc, nr = len(forms), len(cvars), len(rvars)
    Q = np.zeros((nf, nc, nc), dtype=np.int64)       # constant part (cover x cover)
    L = np.zeros((nf, nc, nr), dtype=np.int64)       # linear part (cover x rest)
    for fi, f in enumerate(forms):
        for (v1, v2), c in f.items():
            c %= p
            if not c:
                continue
            if v1 in ci and v2 in ci:
                Q[fi, ci[v1], ci[v2]] = (Q[fi, ci[v1], ci[v2]] + c) % p
            elif v1 in ci:
                L[fi, ci[v1], ri[v2]] = (L[fi, ci[v1], ri[v2]] + c) % p
            elif v2 in ci:
                L[fi, ci[v2], ri[v1]] = (L[fi, ci[v2], ri[v1]] + c) % p
            else:
                raise AssertionError("cover misses a monomial")
    total = 0
    X = all_vectors(p, nc)
    for s in range(0, len(X), chunk):
        Xs = X[s:s + chunk]
        if nf == 0:
            total += len(Xs) * p ** nr
            continue
        M = np.einsum("Pc,fcr->Pfr", Xs, L) % p
        b = np.einsum("Pc,fcd,Pd->Pf", Xs, Q, Xs) % p
        rM = batch_rank(M, p) if nr else np.zeros(len(Xs), dtype=np.int64)
        rMb = batch_rank(np.concatenate([M, b[:, :, None]], axis=2), p)
        ok = rM == rMb
        total += int(sum(p ** (nr - int(x)) for x in rM[ok]))
    return total, nvar, len(cvars)


def direct_count(G, gad, k, max_enum=None):
    """the generic obstruction count for sector k (psi_k = k psi) on the gadget model, restricted to the slot spaces:
    #{x = sum_i x_i, x_i in V_{k bexp_i} : <o(x), w (x) phi> = 0 for all tests}, o(x) = (1/2) sum kappa(x_i, x_i2) T(., ., w),
    without any regrouping by the regraded group"""
    p, r = G.p, G.r
    I = [i for i in range(G.dB) if (k * G.bexp[i]) % r in gad.coords_of]
    groups, var = [], {}
    for i in I:
        th = (k * G.bexp[i]) % r
        g = []
        for a in gad.coords_of[th]:
            var[(i, a)] = len(var)
            g.append(var[(i, a)])
        groups.append(g)
    forms = []
    T = gad.T
    for j in range(G.dA):
        rho = (k * G.aexp[j]) % r
        th3 = (-rho) % r
        if th3 not in gad.coords_of:
            continue
        for c in gad.coords_of[th3]:
            f = {}
            for i in I:
                for i2 in I:
                    if i >= i2:
                        continue
                    v = G.kappa_entry(i, i2, j)
                    if not v:
                        continue
                    for a in gad.coords_of[(k * G.bexp[i]) % r]:
                        for b in gad.coords_of[(k * G.bexp[i2]) % r]:
                            t = int(T[a, b, c])
                            if t:
                                key = (var[(i, a)], var[(i2, b)])
                                f[key] = (f.get(key, 0) + v * t) % p
            f = {key: v for key, v in f.items() if v}
            if f:
                forms.append(f)
    return count_bilinear_zeros(p, groups, forms, max_enum=max_enum)


class SectorData:
    """the template data of sector k: coefficient spaces B1, B2, B3 (coordinates of the regraded slot eigenspaces), target
    coordinate lists A12, A13, A23 and the pairings as dense arrays"""

    def __init__(self, G, gad, k):
        p, r = G.p, G.r
        s1, s2, s3 = gad.S
        Bk, Ak = G.regraded(k)
        self.B1, self.B2, self.B3 = Bk.get(s1, []), Bk.get(s2, []), Bk.get(s3, [])
        self.A12, self.A13, self.A23 = Ak.get((s1 + s2) % r, []), Ak.get((s1 + s3) % r, []), Ak.get((s2 + s3) % r, [])

        def arr(Bx, By, Aj):
            K = np.zeros((len(Bx), len(By), len(Aj)), dtype=np.int64)
            for a, i in enumerate(Bx):
                for b, i2 in enumerate(By):
                    for c, j in enumerate(Aj):
                        K[a, b, c] = G.kappa_entry(i, i2, j)
            return K
        self.k12 = arr(self.B1, self.B2, self.A12)
        self.k13 = arr(self.B1, self.B3, self.A13)
        self.k23 = arr(self.B2, self.B3, self.A23)
        self.p = p

    def nonzero(self):
        return bool(self.k12.any() or self.k13.any() or self.k23.any())


def template_count(G, gad, k, chunk=20000):
    """#{X in B1^V, Y in B2^E, Z in B3^E : k12(X_u - X_v, Y_e) = 0, k13(X_u - X_v, Z_e) = 0, sum_e +-k23(Y_e, Z_e) = 0 at
    every vertex}"""
    sd = SectorData(G, gad, k)
    p, n, E = G.p, gad.n, gad.edges
    m = len(E)
    d1, d2, d3 = len(sd.B1), len(sd.B2), len(sd.B3)
    XY = all_vectors(p, n * d1 + m * d2)
    total = 0
    for s in range(0, len(XY), chunk):
        V = XY[s:s + chunk]
        P = len(V)
        X = V[:, :n * d1].reshape(P, n, d1)
        Y = V[:, n * d1:].reshape(P, m, d2)
        ok = np.ones(P, dtype=bool)
        Ls = []
        for e, (u, v) in enumerate(E):
            Le = (X[:, u, :] - X[:, v, :]) % p
            Ls.append(Le)
            if sd.A12:
                val = np.einsum("Pa,Pb,abc->Pc", Le, Y[:, e, :], sd.k12) % p
                ok &= ~val.any(axis=1)
        idx = np.nonzero(ok)[0]
        if len(idx) == 0:
            continue
        # linear system in Z (m * d3 unknowns): rows k13(L_e, Z_e) per edge, vertex sums of k23(Y_e, Z_e)
        rows = []
        for e, (u, v) in enumerate(E):
            if sd.A13 and d3:
                Me = np.einsum("Pa,abc->Pcb", Ls[e][idx], sd.k13) % p      # (P, |A13|, d3)
                blk = np.zeros((len(idx), len(sd.A13), m * d3), dtype=np.int64)
                blk[:, :, e * d3:(e + 1) * d3] = Me
                rows.append(blk)
        if sd.A23 and d3:
            for w in range(n):
                blk = np.zeros((len(idx), len(sd.A23), m * d3), dtype=np.int64)
                for e, (u, v) in enumerate(E):
                    sgn = (1 if u == w else 0) - (1 if v == w else 0)
                    if sgn:
                        Me = np.einsum("Pb,bzc->Pcz", Y[idx, e, :], sd.k23) % p   # (P, |A23|, d3)
                        blk[:, :, e * d3:(e + 1) * d3] = (blk[:, :, e * d3:(e + 1) * d3] + sgn * Me) % p
                rows.append(blk)
        nz = m * d3
        if rows and nz:
            M = np.concatenate(rows, axis=1)
            rk = batch_rank(M, p)
            total += int(sum(p ** (nz - int(x)) for x in rk))
        else:
            total += len(idx) * p ** nz
    return total


def weight_table(G, gad, k):
    """W_k(xi, eta) = |K2(xi)| |K3(xi)| p^(-rank(eta o k23 on K2(xi) x K3(xi))) on U = B1 + A23* (itertools.product order),
    as a dict, the ordered list U and the sector data"""
    sd = SectorData(G, gad, k)
    p = G.p
    d1, d2, d3, dA = len(sd.B1), len(sd.B2), len(sd.B3), len(sd.A23)
    U = [tuple(u) for u in all_vectors(p, d1 + dA).tolist()]
    etas = all_vectors(p, dA)
    W = {}
    for xi in all_vectors(p, d1).tolist():
        M2 = [[sum(xi[a] * int(sd.k12[a, b, c]) for a in range(d1)) % p for b in range(d2)] for c in range(len(sd.A12))]
        M3 = [[sum(xi[a] * int(sd.k13[a, b, c]) for a in range(d1)) % p for b in range(d3)] for c in range(len(sd.A13))]
        K2 = nullspace([row for row in M2 if any(row)], d2, p) if d2 else []
        K3 = nullspace([row for row in M3 if any(row)], d3, p) if d3 else []
        base = len(K2) + len(K3)
        if K2 and K3 and dA:
            K2a, K3a = np.array(K2, dtype=np.int64), np.array(K3, dtype=np.int64)
            Fc = np.einsum("yb,bzc,wz->cyw", K2a, sd.k23, K3a) % p          # (dA, |K2|, |K3|)
            F = np.einsum("Ec,cyw->Eyw", etas, Fc) % p
            rk = batch_rank(F, p)
        else:
            rk = np.zeros(len(etas), dtype=np.int64)
        for eta, rr in zip(etas.tolist(), rk.tolist()):
            W[tuple(xi) + tuple(eta)] = p ** (base - int(rr))
    return W, U, sd


def weight_matrix(W, U, p):
    """the matrix [W(x - y)] over U (U in itertools.product order), as a list of lists of Python integers"""
    N = len(U)
    D = len(U[0]) if U else 0
    Wv = [W[u] for u in U]
    if D == 0:
        return [[Wv[0]]]
    Ua = np.array(U, dtype=np.int64).reshape(N, D)
    place = np.array([p ** (D - 1 - i) for i in range(D)], dtype=np.int64)
    code = (((Ua[:, None, :] - Ua[None, :, :]) % p) @ place)
    Wa = np.array(Wv, dtype=object)
    return Wa[code].tolist()


def partition_function(W, U, n, edges, p):
    """Z_W(Gamma) = sum over sigma: V -> U of prod over edges W(sigma_u - sigma_v), exactly. W is a function of differences,
    so one vertex per connected component is fixed at 0 (factor |U| each); the last free vertex is summed with numpy object
    arithmetic (exact integers)."""
    assert all(u != v for u, v in edges), "loops are not inputs"
    N = len(U)
    D = len(U[0]) if U else 0
    if n == 0:
        return 1, None
    # components and roots
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for u, v in edges:
        parent[find(u)] = find(v)
    roots = sorted({find(a) for a in range(n)})
    free = [a for a in range(n) if a not in roots]
    Ua = np.array(U, dtype=np.int64).reshape(N, D) if D else np.zeros((N, 0), dtype=np.int64)
    place = np.array([p ** (D - 1 - i) for i in range(D)], dtype=np.int64)
    Wa = np.array([W[u] for u in U], dtype=object)

    def code(vals):
        return (vals % p) @ place if D else np.zeros(len(vals), dtype=np.int64)
    total = 0
    if not free:
        prod = 1
        for (u, v) in edges:
            prod *= W[tuple([0] * D)]
        return prod * N ** len(roots), None
    last = free[-1]
    others = free[:-1]
    zero = np.zeros(D, dtype=np.int64)
    for sig in itertools.product(range(N), repeat=len(others)):
        val = {a: zero for a in roots}
        for a, t in zip(others, sig):
            val[a] = Ua[t]
        prod = 1
        for (u, v) in edges:
            if last in (u, v):
                continue
            prod *= W[tuple(((val[u] - val[v]) % p).tolist())] if D else W[()]
            if not prod:
                break
        if not prod:
            continue
        vec = np.ones(N, dtype=object)
        for (u, v) in edges:
            if last == u:
                vec = vec * Wa[code(Ua - val[v])]
            elif last == v:
                vec = vec * Wa[code(val[u] - Ua)]
        total += prod * int(vec.sum())
    return total * N ** len(roots), None


def fourier_count(G, gad, k):
    W, U, sd = weight_table(G, gad, k)
    Z, Mat = partition_function(W, U, gad.n, gad.edges, G.p)
    q = G.p ** (gad.n * len(sd.A23))
    assert Z % q == 0, "partition function not divisible by |A23|^n"
    return Z // q, W, U, sd, Mat


def sector_constants(G, S, k):
    """c_k = |B^1(B_psik)| |B^1(A_psik)| and the exponent (a, b) of lambda_k^n mu_k^m = |H^1(A_psik)| * free factors *
    |A23|^(-n), from the linear dimensions of the base"""
    p, r = G.p, G.r
    Sn, pat = normalize_slots(S, r)
    dl = dims_linear(Sn, r)
    ck = p ** (sum(1 for e in G.bexp if k * e % r) + sum(1 for e in G.aexp if k * e % r))
    a = b = 0
    for e in G.aexp:
        th = k * e % r
        if th:
            cn, cm = dl.get(th, (0, 0))
            a, b = a + cn, b + cm
    slotset = set(Sn)
    for e in G.bexp:
        th = k * e % r
        if th and th not in slotset:
            cn, cm = dl.get(th, (0, 0))
            a, b = a + cn, b + cm
    s1, s2, s3 = Sn
    a23 = sum(1 for e in G.aexp if k * e % r == (s2 + s3) % r)
    return ck, a - a23, b


def model_hom_count(G, gad, use="template"):
    """|Hom| of the gadget model: sum over k of c_k |H^1(A_psik)| (free factors) N_k, with N_k from the template"""
    p, r = G.p, G.r
    n, m = gad.n, len(gad.edges)
    d = base_dims(gad.summand_counts(), r)
    tot = 0
    parts = []
    for k in range(r):
        ck = p ** (sum(1 for e in G.bexp if k * e % r) + sum(1 for e in G.aexp if k * e % r))
        h1a = p ** sum(d.get(k * e % r, 0) for e in G.aexp if k * e % r)
        free = p ** sum(d.get(k * e % r, 0) for e in G.bexp if k * e % r and (k * e % r) not in set(gad.S))
        Nk = template_count(G, gad, k)
        parts.append((ck, h1a, free, Nk))
        tot += ck * h1a * free * Nk
    return tot, parts
