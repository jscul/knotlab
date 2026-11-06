"""Library for COPRIME-DICHOTOMY-20261027-001: graded nilpotent Lie algebras over F_p with a C_d-grading (characters mod d), free
graded algebras, quotients by bigraded ideals, the pair and triple criterion, and a closed-braid model of
S^3_(d/q)(closure of a braid word) with batched BCH (class <= 4)."""
import itertools
import numpy as np


# ------------------------------------------------------------------------------------------------ linear algebra mod p
def rref(A, p):
    A = np.array(A, dtype=np.int64) % p
    rows, cols = A.shape
    piv, r = [], 0
    for c in range(cols):
        if r == rows: break
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0: continue
        k = r + nz[0]; A[[r, k]] = A[[k, r]]
        A[r] = A[r] * pow(int(A[r, c]), p - 2, p) % p
        for o in np.nonzero(A[:, c])[0]:
            if o != r: A[o] = (A[o] - A[o, c] * A[r]) % p
        piv.append(c); r += 1
    return A[:r], piv


def rank(A, p):
    A = np.array(A, dtype=np.int64)
    if A.size == 0: return 0
    return len(rref(A, p)[1])


def nullspace(A, p):
    """right kernel basis (rows) of A"""
    A = np.array(A, dtype=np.int64) % p
    cols = A.shape[1]
    R, piv = rref(A, p) if A.shape[0] else (np.zeros((0, cols), dtype=np.int64), [])
    basis = []
    for f in [c for c in range(cols) if c not in piv]:
        v = np.zeros(cols, dtype=np.int64); v[f] = 1
        for i, c in enumerate(piv): v[c] = (-R[i, f]) % p
        basis.append(v)
    return np.array(basis, dtype=np.int64).reshape(len(basis), cols)


def solve_any(A, B, p):
    """columns X with A X = B where solvable; returns (X, bad) with bad[j] True if column j is not solvable"""
    A = np.array(A, dtype=np.int64) % p; B = np.array(B, dtype=np.int64) % p
    rows, cols = A.shape
    M = np.concatenate([A, B], axis=1); piv = []; r = 0
    for c in range(cols):
        if r == rows: break
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0: continue
        k = r + nz[0]; M[[r, k]] = M[[k, r]]
        M[r] = M[r] * pow(int(M[r, c]), p - 2, p) % p
        for o in np.nonzero(M[:, c])[0]:
            if o != r: M[o] = (M[o] - M[o, c] * M[r]) % p
        piv.append(c); r += 1
    bad = (M[r:, cols:] % p).any(axis=0)
    X = np.zeros((cols, B.shape[1]), dtype=np.int64)
    for i, c in enumerate(piv): X[c] = M[i, cols:]
    return X % p, bad


def root_of_unity(p, d):
    """an element of F_p^x of exact order d (d | p - 1)"""
    assert (p - 1) % d == 0
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in range(2, p) if (p - 1) % q == 0 and all(q % s for s in range(2, q))):
            return pow(g, (p - 1) // d, p)
    return 1


# ------------------------------------------------------------------------------------------------ graded Lie algebras
class GLie:
    """basis e_0..e_{D-1}, each of a layer (degree) and a character mod d; structure tensor C[i, j, k] (antisymmetric in i, j)"""

    def __init__(self, p, d, names, layers, chars, C, check=True):
        self.p, self.d = p, d
        self.names, self.D = list(names), len(names)
        self.idx = {nm: i for i, nm in enumerate(self.names)}
        self.layer = np.array(layers, dtype=np.int64)
        self.chars = np.array([c % d for c in chars], dtype=np.int64)
        self.C = np.array(C, dtype=np.int64).reshape(self.D, self.D, self.D) % p
        I, J, K = np.nonzero(self.C)
        self._sp = (I, J, K, self.C[I, J, K])
        if check: self.check()

    @classmethod
    def from_brackets(cls, p, d, names, layers, chars, brackets, check=True):
        D = len(names); idx = {nm: i for i, nm in enumerate(names)}
        C = np.zeros((D, D, D), dtype=np.int64)
        for (a, b), out in brackets.items():
            for c, v in out.items():
                C[idx[a], idx[b], idx[c]] += v
                C[idx[b], idx[a], idx[c]] -= v
        return cls(p, d, names, layers, chars, C, check)

    def br(self, X, Y):
        X = np.atleast_2d(X); Y = np.atleast_2d(Y)
        I, J, K, V = self._sp
        out = np.zeros((max(X.shape[0], Y.shape[0]), self.D), dtype=np.int64)
        if len(I):
            np.add.at(out.T, K, ((X[:, I] * Y[:, J]) % self.p * V).T)
        return out % self.p

    def unit(self, i):
        v = np.zeros((1, self.D), dtype=np.int64); v[0, i] = 1
        return v

    def check(self):
        p, D = self.p, self.D
        assert not ((self.C + self.C.transpose(1, 0, 2)) % p).any(), "antisymmetry"
        for i, j in itertools.product(range(D), repeat=2):
            for k in np.nonzero(self.C[i, j])[0]:
                assert self.layer[k] == self.layer[i] + self.layer[j], "grading"
                assert self.chars[k] == (self.chars[i] + self.chars[j]) % self.d, "equivariance"
        # Jacobi on basis triples, batched over the third argument
        E = np.eye(D, dtype=np.int64)
        for i, j in itertools.combinations(range(D), 2):
            a = np.repeat(E[i:i + 1], D, axis=0); b = np.repeat(E[j:j + 1], D, axis=0)
            jac = (self.br(a, self.br(b, E)) + self.br(b, self.br(E, a)) + self.br(E, self.br(a, b))) % p
            assert not jac.any(), "Jacobi"

    def comp(self, theta, d=None):
        d = self.d if d is None else d
        return [k for k in range(self.D) if self.chars[k] % d == theta % d]

    def coarsen(self, d2):
        """the same algebra with characters reduced mod d2 (d2 | d): the grading by the subgroup of order d2"""
        assert self.d % d2 == 0
        return GLie(self.p, d2, self.names, self.layer, self.chars % d2, self.C, check=False)

    def to_lmc(self, zeta):
        return BraidAlg(self, zeta)


def free_graded(p, d, gen_chars, c, gen_names=None):
    """free nilpotent Lie algebra of class c (< p) on generators with the given characters mod d; basis by elimination of
    left-normed words in the free associative algebra"""
    k = len(gen_chars)
    gen_names = gen_names or [chr(ord("a") + i) for i in range(k)]

    def mul(a, b):
        out = {}
        for wa, ca in a.items():
            for wb, cb in b.items():
                out[wa + wb] = (out.get(wa + wb, 0) + ca * cb) % p
        return {w: v for w, v in out.items() if v}

    def brk(a, b):
        out = dict(mul(a, b))
        for w, v in mul(b, a).items(): out[w] = (out.get(w, 0) - v) % p
        return {w: v for w, v in out.items() if v}

    basis = {1: [({(g,): 1}, (g,)) for g in range(k)]}
    for deg in range(2, c + 1):
        cands = [(brk(e, {(g,): 1}), lab + (g,)) for e, lab in basis[deg - 1] for g in range(k)]
        words = sorted({w for e, _ in cands for w in e})
        rows, keep = [], []
        for e, lab in cands:
            v = [e.get(w, 0) for w in words]
            if rank(rows + [v], p) > len(rows):
                rows.append(v); keep.append((e, lab))
        basis[deg] = keep
    names, layers, chars, elems = [], [], [], []
    for deg in range(1, c + 1):
        for e, lab in basis[deg]:
            names.append(gen_names[lab[0]] if deg == 1 else "[" + ",".join(gen_names[g] for g in lab) + "]")
            layers.append(deg); chars.append(sum(gen_chars[g] for g in lab) % d); elems.append(e)
    D = len(names)
    C = np.zeros((D, D, D), dtype=np.int64)
    by_layer = {deg: [i for i in range(D) if layers[i] == deg] for deg in range(1, c + 1)}
    for i in range(D):
        for j in range(i + 1, D):
            deg = layers[i] + layers[j]
            if deg > c: continue
            b = brk(elems[i], elems[j])
            if not b: continue
            idx = by_layer[deg]
            words = sorted({w for t in idx for w in elems[t]} | set(b))
            A = np.array([[elems[t].get(w, 0) for w in words] for t in idx], dtype=np.int64)
            X, bad = solve_any(A.T, np.array([[b.get(w, 0)] for w in words]), p)
            assert not bad.any()
            for t, v in zip(idx, X[:, 0]):
                C[i, j, t] = v % p; C[j, i, t] = (-v) % p
    return GLie(p, d, names, layers, chars, C, check=False)


def ideal_closure(L, vecs):
    """the ideal generated by the given vectors, in reduced row echelon form: the span closed under brackets with basis vectors"""
    p = L.p
    E = np.eye(L.D, dtype=np.int64)
    vecs = [np.array(v, dtype=np.int64) % p for v in vecs if np.any(np.array(v) % p)]
    if not vecs: return np.zeros((0, L.D), dtype=np.int64)
    span = rref(np.array(vecs), p)[0]
    while True:
        new = np.concatenate([L.br(np.repeat(v[None, :], L.D, axis=0), E) for v in span])
        R = rref(np.concatenate([span, new]), p)[0]
        if len(R) == len(span): return span
        span = R


def quotient(L, vecs):
    """L / (ideal generated by vecs); the ideal is bigraded when the generators are homogeneous (checked)"""
    p = L.p
    R = ideal_closure(L, vecs)
    piv = [int(np.nonzero(row)[0][0]) for row in R]
    for row in R:   # the ideal is bigraded: every reduced row lies in one (layer, character) block
        assert len({(int(L.layer[k]), int(L.chars[k])) for k in np.nonzero(row)[0]}) == 1
    keep = [k for k in range(L.D) if k not in piv]
    pos = {k: t for t, k in enumerate(keep)}

    def reduce(v):
        v = np.array(v, dtype=np.int64) % p
        for row, c in zip(R, piv):
            if v[c]: v = (v - v[c] * row) % p
        return v
    D2 = len(keep)
    C2 = np.zeros((D2, D2, D2), dtype=np.int64)
    for a, i in enumerate(keep):
        for b, j in enumerate(keep):
            w = reduce(L.br(L.unit(i), L.unit(j))[0])
            for k in np.nonzero(w)[0]:
                assert k in pos
                C2[a, b, pos[k]] = w[k]
    return GLie(p, L.d, [L.names[k] for k in keep], L.layer[keep], L.chars[keep], C2, check=False)


# ------------------------------------------------------------------------------------------------ the criterion
def pair_failures(L, d=None):
    """(alpha, beta) mod d with alpha, beta, alpha + beta nonzero and [n_alpha, n_beta] != 0"""
    d = L.d if d is None else d
    fails = []
    for a in range(1, d):
        for b in range(a, d):
            if (a + b) % d == 0: continue
            A, B = L.comp(a, d), L.comp(b, d)
            if any(L.br(L.unit(i), L.unit(j)).any() for i in A for j in B): fails.append((a, b))
    return fails


def triple_failures(L, d=None):
    """(alpha, beta) mod d, both nonzero, with [[n_alpha, n_-alpha], n_beta] != 0"""
    d = L.d if d is None else d
    fails = []
    for a in range(1, d):
        Z = [L.br(L.unit(i), L.unit(j))[0] for i in L.comp(a, d) for j in L.comp(-a, d)]
        Z = [z for z in Z if z.any()]
        if not Z: continue
        Zm = np.array(Z)
        for b in range(1, d):
            Bs = L.comp(b, d)
            if not Bs: continue
            for j in Bs:
                if L.br(Zm, np.repeat(L.unit(j), len(Zm), axis=0)).any():
                    fails.append((a, b)); break
    return fails


def criterion(L, d=None):
    return not pair_failures(L, d) and not triple_failures(L, d)


def lemma1(L, d=None):
    """the four conditions of Lemma 1 at d, evaluated independently"""
    d = L.d if d is None else d
    p = L.p
    nz = [k for k in range(L.D) if L.chars[k] % d]
    zero = [k for k in range(L.D) if L.chars[k] % d == 0]
    E = np.eye(L.D, dtype=np.int64)
    # (ii): [n', n'] in n_0 and [[n', n'], n'] = 0
    pairs = [L.br(E[i], E[j])[0] for i in nz for j in nz]
    pairs = [v for v in pairs if v.any()]
    in_zero = all(not v[nz].any() for v in pairs)
    trip = all(not L.br(np.repeat(v[None, :], len(nz), 0), E[nz]).any() for v in pairs) if pairs else True
    cond2 = in_zero and trip
    # (iii): the subalgebra generated by n' is n' + Z with Z = [n', n'] in n_0 central in it
    gen = E[nz] if nz else np.zeros((0, L.D), dtype=np.int64)
    span = rref(gen, p)[0] if len(gen) else gen
    while True:
        new = [L.br(u, v)[0] for u in span for v in span]
        allv = np.concatenate([span] + ([np.array(new)] if new else []))
        R = rref(allv, p)[0] if len(allv) else allv
        if len(R) == len(span): break
        span = R
    Zs = rref(np.array(pairs), p)[0] if pairs else np.zeros((0, L.D), dtype=np.int64)
    expected = rank(np.concatenate([E[nz], Zs]) if len(Zs) else E[nz], p) if nz else 0
    Z_in_zero = all(not z[nz].any() for z in Zs)
    Z_central = all(not L.br(z, s).any() for z in Zs for s in span)
    cond3 = len(span) == expected and Z_in_zero and Z_central
    # (iv): theta_d (+1 on n_0, -1 on n') is an automorphism, and its triple system is abelian
    th = np.where(L.chars % d == 0, 1, -1)
    auto = all(not ((L.br(E[i] * th, E[j] * th)[0] - L.br(E[i], E[j])[0] * th) % p).any()
               for i in range(L.D) for j in range(L.D))
    odd_triple = all(not L.br(L.br(E[i], E[j]), E[k]).any() for i in nz for j in nz for k in nz)
    cond4 = auto and odd_triple
    return {"(i) P2 and P3": criterion(L, d), "(ii) [n',n'] in n_0, [[n',n'],n'] = 0": cond2,
            "(iii) <n'> = n' + Z, Z central and fixed": cond3, "(iv) theta_d automorphism with abelian triple system": cond4,
            "P2 alone": not pair_failures(L, d), "theta_d automorphism": auto}


def criterion_quotient(L, d=None):
    """the quotient by the ideal generated by every failing pair and triple bracket"""
    d = L.d if d is None else d
    vecs = []
    for a in range(1, d):
        for b in range(1, d):
            if (a + b) % d:
                vecs += [L.br(L.unit(i), L.unit(j))[0] for i in L.comp(a, d) for j in L.comp(b, d)]
    for a in range(1, d):
        Z = [L.br(L.unit(i), L.unit(j))[0] for i in L.comp(a, d) for j in L.comp(-a, d)]
        for b in range(1, d):
            for z in Z:
                for j in L.comp(b, d):
                    vecs.append(L.br(z, L.unit(j))[0])
    vecs = [v for v in vecs if v.any()]
    return quotient(L, vecs) if vecs else L


# ------------------------------------------------------------------------------------------------ the braid model
class BraidAlg:
    """batched BCH (class <= 4) and the action of sigma^e (sigma acting on n_j by zeta^j) for a GLie"""

    def __init__(self, L, zeta):
        self.L, self.p, self.d, self.D = L, L.p, L.d, L.D
        self.zeta = zeta % L.p
        assert pow(self.zeta, L.d, L.p) == 1 and all(pow(self.zeta, k, L.p) != 1 for k in range(1, L.d))
        assert L.layer.max() <= 4 < L.p
        self.idx, self.names, self.chars, self.layer = L.idx, L.names, L.chars, L.layer
        p = L.p
        self.inv2, self.inv12, self.inv24 = pow(2, p - 2, p), pow(12, p - 2, p), pow(24, p - 2, p)

    def br(self, X, Y): return self.L.br(X, Y)

    def bch(self, X, Y):
        p = self.p
        XY = self.br(X, Y)
        return (X + Y + self.inv2 * XY + self.inv12 * (self.br(X, XY) - self.br(Y, XY))
                - self.inv24 * self.br(Y, self.br(X, XY))) % p

    def act(self, X, e):
        f = np.array([pow(self.zeta, int(e * c) % self.d, self.p) for c in self.chars], dtype=np.int64)
        return (X * f) % self.p


class Grp:
    """G = exp(n) x| C_d; elements (v, e)"""
    def __init__(self, A): self.A = A
    def mul(self, a, b):
        (v, e), (w, f) = a, b
        return (self.A.bch(v, self.A.act(w, e)), (e + f) % self.A.d)
    def inv(self, a):
        v, e = a
        return ((-self.A.act(v, (-e) % self.A.d)) % self.A.p, (-e) % self.A.d)


def braid_meta(word, n):
    """lambda (the longitude of strand 0 as the ordered list of letters it passes under) and the writhe"""
    m = len(word)
    order, q, l, steps = [], 0, 0, 0
    while True:
        g = word[l]; i = abs(g) - 1
        if q in (i, i + 1):
            left = q == i
            over = (left and g > 0) or (not left and g < 0)
            if not over: order.append(l)
            q = i + 1 if left else i
        l = (l + 1) % m; steps += 1
        if l == 0 and q == 0: break
    assert steps == n * m, "closure is not a knot"
    return order, sum(1 if g > 0 else -1 for g in word)


class CyclicBraidModel:
    """closed-braid presentation of S^3_(d/q)(closure): generators x_0..x_{n-1} (top meridians), relators
    x_q^-1 beta(x_q) (q < n) and x_0^d lambda^q; homomorphisms with every x_q in the coset N sigma (sector sigma^1)"""

    def __init__(self, word, n, A, q_slope=1):
        self.word, self.n, self.A, self.p, self.q = list(word), n, A, A.p, q_slope
        self.lam_order, self.writhe = braid_meta(word, n)
        self.Lin = {c: self._linear_part(c) for c in range(A.d)}
        self.cocycles = {c: nullspace(self.Lin[c], self.p) for c in range(A.d)}

    def run(self, V, A=None):
        A = A or self.A
        G, n = Grp(A), self.n
        cur = [(V[:, q].copy(), 1) for q in range(n)]
        overs = {}
        for l, g in enumerate(self.word):
            i = abs(g) - 1
            a, b = cur[i], cur[i + 1]
            if g > 0:
                overs[l] = a
                cur[i], cur[i + 1] = G.mul(G.mul(G.inv(a), b), a), a
            else:
                overs[l] = b
                cur[i], cur[i + 1] = b, G.mul(G.mul(b, a), G.inv(b))
        out = np.zeros((V.shape[0], n + 1, A.D), dtype=np.int64)
        for q in range(n):
            val = G.mul(G.inv((V[:, q], 1)), cur[q]); assert val[1] == 0
            out[:, q] = val[0]
        lam = (np.zeros_like(V[:, 0]), 0)
        for l in self.lam_order:
            lam = G.mul(lam, overs[l] if self.word[l] > 0 else G.inv(overs[l]))
        x0 = (V[:, 0], 1)
        for _ in range(abs(self.writhe)):
            lam = G.mul(lam, G.inv(x0) if self.writhe > 0 else x0)
        S = (np.zeros_like(V[:, 0]), 0)
        for _ in range(A.d): S = G.mul(S, x0)
        lq = (np.zeros_like(V[:, 0]), 0)
        for _ in range(self.q): lq = G.mul(lq, lam)
        val = G.mul(S, lq); assert val[1] == 0
        out[:, n] = val[0]
        return out

    def _linear_part(self, c):
        """Fox matrix (relators x generators) at the character zeta^c, by propagating a one-dimensional abelian algebra"""
        L1 = GLie(self.p, self.A.d, ["e"], [1], [c], np.zeros((1, 1, 1), dtype=np.int64), check=False)
        A1 = BraidAlg(L1, self.A.zeta)
        V = np.zeros((self.n, self.n, 1), dtype=np.int64)
        for q in range(self.n): V[q, q, 0] = 1
        return self.run(V, A1)[:, :, 0].T % self.p

    def solve(self, inputs):
        """inputs: {component: (bs, n) cocycle values} for free components (others: particular solutions).  Returns
        (ok, first_fail, V): ok[s] is False if some layer was obstructed for sample s (trivial characters never are)."""
        A, p, n = self.A, self.p, self.n
        bs = next(iter(inputs.values())).shape[0]
        V = np.zeros((bs, n, A.D), dtype=np.int64)
        ok = np.ones(bs, dtype=bool)
        first_fail = {}
        for lay in range(1, int(A.layer.max()) + 1):
            ks = [k for k in range(A.D) if A.layer[k] == lay]
            R = self.run(V)
            for k in ks:
                X, bad = solve_any(self.Lin[int(A.chars[k])], (-R[:, :, k]).T % p, p)
                if A.chars[k] == 0:   # H^1 = H^2 = 0 with trivial coefficients (samples obstructed earlier carry no meaning)
                    assert not (bad & ok).any(), f"trivial-character component {A.names[k]} obstructed"
                for s in np.nonzero(bad & ok)[0]: first_fail.setdefault(int(s), (lay, A.names[k]))
                ok &= ~bad
                V[:, :, k] = (X.T + (inputs[k] if k in inputs else 0)) % p
        return ok, first_fail, V
