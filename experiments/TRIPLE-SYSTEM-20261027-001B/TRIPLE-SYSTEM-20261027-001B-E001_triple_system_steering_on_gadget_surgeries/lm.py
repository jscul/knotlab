"""general nilpotent braid model (TRIPLE-SYSTEM-20261027-001B-E001, measurement; copy of ticket A's lm.py with a sparse bracket): N = exp(n) for a graded nilpotent Lie algebra n over F_p of class <= 4
(sign +-1 per basis vector), G = N x| <theta>; closed-braid presentation of S^3_2(closure of a braid word); batched numpy BCH."""
import itertools
import numpy as np

class LieAlg:
    def __init__(self, p, names, layers, signs, brackets):
        self.p, self.names, self.D = p, list(names), len(names)
        self.idx = {nm: i for i, nm in enumerate(names)}
        self.layer = np.array(layers); self.sign = np.array(signs, dtype=np.int64)
        C = np.zeros((self.D, self.D, self.D), dtype=np.int64)
        for (a, b), out in brackets.items():
            for c, v in out.items():
                C[self.idx[a], self.idx[b], self.idx[c]] += v
                C[self.idx[b], self.idx[a], self.idx[c]] -= v
        self.C = C % p
        self.inv2, self.inv12, self.inv24 = pow(2, p - 2, p), pow(12, p - 2, p), pow(24, p - 2, p)
        self.check()

    def br(self, X, Y):
        if not hasattr(self, "_sp"):
            I, J, K = np.nonzero(self.C)
            self._sp = (I, J, K, self.C[I, J, K])
        I, J, K, V = self._sp
        out = np.zeros((X.shape[0], self.D), dtype=np.int64)
        if len(I):
            np.add.at(out.T, K, (X[:, I] * Y[:, J] % self.p * V).T)
        return out % self.p

    def check(self):
        p, D = self.p, self.D
        E = np.eye(D, dtype=np.int64)
        for i, j, k in itertools.product(range(D), repeat=3):
            a, b, c = E[i:i + 1], E[j:j + 1], E[k:k + 1]
            jac = (self.br(a, self.br(b, c)) + self.br(b, self.br(c, a)) + self.br(c, self.br(a, b))) % p
            assert not jac.any(), "Jacobi"
            assert not ((self.br(a, b) + self.br(b, a)) % p).any()
        for i, j in itertools.product(range(D), repeat=2):
            v = self.C[i, j]
            for k in np.nonzero(v)[0]:
                assert self.layer[k] == self.layer[i] + self.layer[j], "grading"
                assert self.sign[k] == self.sign[i] * self.sign[j], "equivariance"

    def bch(self, X, Y):
        p = self.p
        XY = self.br(X, Y)
        Z = (X + Y + self.inv2 * XY + self.inv12 * (self.br(X, XY) - self.br(Y, XY))
             - self.inv24 * self.br(Y, self.br(X, XY))) % p
        return Z

    def theta(self, X):
        return (X * self.sign) % self.p

# group elements of G: (v, e) with e in {0, 1}; all braid labels have e = 1
class Grp:
    def __init__(self, L): self.L = L
    def mul(self, a, b):
        (v, e), (w, f) = a, b
        w2 = self.L.theta(w) if e % 2 else w
        return (self.L.bch(v, w2), (e + f) % 2)
    def inv(self, a):
        v, e = a
        return (((-self.L.theta(v)) if e % 2 else (-v)) % self.L.p, e)

def braid_meta(word, n):
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

def transport(sv, word, upto, p):
    sv = np.array(sv, dtype=np.int64).copy()
    for g in word[:upto]:
        i = abs(g) - 1
        a, b = sv[:, i].copy(), sv[:, i + 1].copy()
        if g > 0: sv[:, i], sv[:, i + 1] = (2 * a - b) % p, a
        else: sv[:, i], sv[:, i + 1] = b, (2 * b - a) % p
    return sv

def nullspace_mod(A, p):
    A = np.array(A, dtype=np.int64) % p
    rows, cols = A.shape
    R = A.copy(); piv = []; r = 0
    for c in range(cols):
        if r == rows: break
        nz = np.nonzero(R[r:, c])[0]
        if len(nz) == 0: continue
        k = r + nz[0]; R[[r, k]] = R[[k, r]]
        R[r] = R[r] * pow(int(R[r, c]), p - 2, p) % p
        for o in np.nonzero(R[:, c])[0]:
            if o != r: R[o] = (R[o] - R[o, c] * R[r]) % p
        piv.append(c); r += 1
    basis = []
    for f in [c for c in range(cols) if c not in piv]:
        v = np.zeros(cols, dtype=np.int64); v[f] = 1
        for i, c in enumerate(piv): v[c] = (-R[i, f]) % p
        basis.append(v)
    return np.array(basis, dtype=np.int64).reshape(len(basis), cols)

def solve_any(A, B, p):
    """one solution X of A X = B (columns), free variables 0; None if some column inconsistent"""
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
    if (M[r:, cols:] % p).any(): return None
    X = np.zeros((cols, B.shape[1]), dtype=np.int64)
    for i, c in enumerate(piv): X[c] = M[i, cols:]
    return X % p

def J_matrix(n, p):
    M = np.zeros((n, n), dtype=np.int64)
    for q in range(n):
        M[q, q] = 1
        for q2 in range(q): M[q, q2] = 2 * (-1) ** (q - q2)
    return M % p

class LieBraidModel:
    def __init__(self, word, n, L, r=2):
        self.word, self.n, self.L, self.p, self.r = list(word), n, L, L.p, r
        self.G = Grp(L)
        self.lam_order, self.writhe = braid_meta(word, n)
        p = self.p
        self.Bur = transport(np.eye(n, dtype=np.int64), word, len(word), p).T % p
        self.Fix = nullspace_mod((self.Bur - np.eye(n, dtype=np.int64)) % p, p)
        self.Lin = {s: self._linear_part(s) for s in (1, -1)}
        self.J = J_matrix(n, p)

    def run(self, V):
        """V: (batch, n, D) top label vectors (all labels in the theta-coset) -> relator vectors (batch, n + 1, D)"""
        G, p, n = self.G, self.p, self.n
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
        out = np.zeros((V.shape[0], n + 1, self.L.D), dtype=np.int64)
        for q in range(n):
            val = G.mul(G.inv((V[:, q], 1)), cur[q]); assert val[1] == 0
            out[:, q] = val[0]
        lam = (np.zeros_like(V[:, 0]), 0)
        for l in self.lam_order:
            lam = G.mul(lam, overs[l] if self.word[l] > 0 else G.inv(overs[l]))
        x0 = (V[:, 0], 1)
        for _ in range(abs(self.writhe)):
            lam = G.mul(lam, G.inv(x0) if self.writhe > 0 else x0)
        S = x0
        for _ in range(self.r - 1): S = G.mul(S, x0)
        val = G.mul(S, lam); assert val[1] == 0
        out[:, n] = val[0]
        return out

    def _linear_part(self, s):
        """linear map top component -> relator component for a one-dimensional module of sign s (via a basis vector of
        that sign if present, else a synthetic one)"""
        L, p, n = self.L, self.p, self.n
        cands = [k for k in range(L.D) if L.sign[k] == s]
        k = cands[-1] if cands else None
        assert k is not None
        V = np.zeros((n, n, L.D), dtype=np.int64)
        for q in range(n): V[q, q, k] = 1
        return self.run(V)[:, :, k].T % p          # (n + 1) x n

    def y_of(self, s):
        return np.concatenate([(s @ self.J) % self.p, np.zeros((s.shape[0], 1), dtype=np.int64)], axis=1)

    def solve(self, inputs, measured):
        """inputs: dict basis index -> (batch, n) colorings for free minus components; every other component is solved
        layer by layer (plus: unique; minus: any solution, asserting solvability).  Returns dict measured index ->
        obstruction vectors (batch, n + 1) of the measured (top-layer, minus) components with those components set to 0."""
        L, p, n = self.L, self.p, self.n
        bs = next(iter(inputs.values())).shape[0]
        V = np.zeros((bs, n, L.D), dtype=np.int64)
        out = {}
        for lay in range(1, int(L.layer.max()) + 1):
            ks = [k for k in range(L.D) if L.layer[k] == lay]
            if not ks: continue
            R = self.run(V)
            for k in ks:
                const = R[:, :, k]
                if k in measured:
                    out[k] = const % p
                    continue
                A = self.Lin[int(L.sign[k])]
                X = solve_any(A, (-const).T % p, p)
                assert X is not None, f"layer {lay} component {L.names[k]} obstructed"
                V[:, :, k] = (X.T + (inputs[k] if k in inputs else 0)) % p
        R = self.run(V)
        assert not any((R[:, :, k] % p).any() for k in range(L.D) if k not in measured), "relators not satisfied"
        return out


def free_nilpotent(p, gens, signs, c):
    """free nilpotent Lie algebra of class c on the given generators (signs +-1 for the involution), over F_p (c < p).
    Elements are noncommutative polynomials; a basis of each degree is extracted by elimination.  Returns LieAlg."""
    def mul(a, b):
        out = {}
        for wa, ca in a.items():
            for wb, cb in b.items():
                w = wa + wb
                out[w] = (out.get(w, 0) + ca * cb) % p
        return {w: v for w, v in out.items() if v}

    def br(a, b):
        ab, ba = mul(a, b), mul(b, a)
        out = dict(ab)
        for w, v in ba.items():
            out[w] = (out.get(w, 0) - v) % p
        return {w: v for w, v in out.items() if v}

    basis = {1: [({(g,): 1}, (g,)) for g in range(len(gens))]}
    for d in range(2, c + 1):
        cands = [(br(e, {(g,): 1}), lab + (g,)) for e, lab in basis[d - 1] for g in range(len(gens))]
        words = sorted({w for e, _ in cands for w in e})
        rows, keep = [], []
        for e, lab in cands:
            v = [e.get(w, 0) for w in words]
            if rank_rows(rows + [v], p) > len(rows):
                rows.append(v); keep.append((e, lab))
        basis[d] = keep
    names, layers, sgn, elems = [], [], [], []
    for d in range(1, c + 1):
        for e, lab in basis[d]:
            names.append("".join(gens[g] for g in lab) if d == 1 else "[" + ",".join(gens[g] for g in lab) + "]")
            layers.append(d)
            s = 1
            for g in lab: s *= signs[g]
            sgn.append(s); elems.append(e)
    brackets = {}
    for i in range(len(elems)):
        for j in range(i + 1, len(elems)):
            d = layers[i] + layers[j]
            if d > c: continue
            b = br(elems[i], elems[j])
            if not b: continue
            idx = [k for k in range(len(elems)) if layers[k] == d]
            words = sorted({w for k in idx for w in elems[k]} | set(b))
            A = [[elems[k].get(w, 0) for w in words] for k in idx]
            coef = solve_rows(A, [b.get(w, 0) for w in words], p)
            assert coef is not None
            out = {names[idx[t]]: int(v) for t, v in enumerate(coef) if v}
            if out: brackets[(names[i], names[j])] = out
    return LieAlg(p, names, layers, sgn, brackets)


def rank_rows(rows, p):
    if not rows: return 0
    A = np.array(rows, dtype=np.int64) % p
    r = 0
    for c in range(A.shape[1]):
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0: continue
        k = r + nz[0]; A[[r, k]] = A[[k, r]]
        A[r] = A[r] * pow(int(A[r, c]), p - 2, p) % p
        for o in np.nonzero(A[:, c])[0]:
            if o != r: A[o] = (A[o] - A[o, c] * A[r]) % p
        r += 1
        if r == A.shape[0]: break
    return r


def solve_rows(A, b, p):
    """coefficients x with x A = b (A rows independent), or None"""
    At = np.array(A, dtype=np.int64).T % p
    X = solve_any(At, np.array(b, dtype=np.int64).reshape(-1, 1) % p, p)
    if X is None: return None
    x = X[:, 0]
    assert ((At @ x - np.array(b)) % p == 0).all()
    return x


def triple_system(L):
    """span of [[a, b], c] for a, b, c in the minus part (as a matrix of vectors)"""
    minus = [k for k in range(L.D) if L.sign[k] == -1]
    E = np.eye(L.D, dtype=np.int64)
    vecs = []
    for a, b, c in itertools.product(minus, repeat=3):
        v = L.br(L.br(E[a:a + 1], E[b:b + 1]), E[c:c + 1])[0]
        if v.any(): vecs.append(v)
    return vecs
