"""Braid model of BEYOND-CLASS2-20261027-001B-E001 (the measurement).

M = S^3_2(closure of a braid word on n strands), presented on the top strands: generators X_0..X_{n-1}, relators
X_q^-1 (bottom label of strand q) and X_0^2 lambda (lambda the Seifert longitude, read as in cp_lib.presentation).
G = U4(F_p) x| <D>, D = diag(1, -1, 1, -1), as 4x4 matrices: every meridian maps to U D with U unitriangular; the
superdiagonal (1,2), (2,3), (3,4) holds the layer-1 classes (c_y, c_x, c_w), the entries (1,3), (2,4) layer 2 and (1,4)
layer 3.  Labels are pushed through the braid as matrices (batched with numpy); each layer is solved as a linear system in
the n top values.  The four-way form is Q(c; s) = <o(c), (J^T s, 0)> with o the layer-3 relator values and J the
lower-unitriangular matrix with 2 (-1)^(q - q') below the diagonal."""
import numpy as np


def rref_solve(A, B, p):
    """solve A x = b for each column b of B over F_p, A of full column rank; returns X, or None if A is rank deficient,
    or 'inconsistent'"""
    A = np.array(A, dtype=np.int64) % p
    B = np.array(B, dtype=np.int64) % p
    rows, cols = A.shape
    M = np.concatenate([A, B], axis=1)
    r = 0
    for c in range(cols):
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0:
            return None
        k = r + nz[0]
        M[[r, k]] = M[[k, r]]
        M[r] = M[r] * pow(int(M[r, c]), p - 2, p) % p
        for o in np.nonzero(M[:, c])[0]:
            if o != r:
                M[o] = (M[o] - M[o, c] * M[r]) % p
        r += 1
    if (M[cols:, cols:] % p).any():
        return "inconsistent"
    return M[:cols, cols:]


def nullspace_mod(A, p):
    A = np.array(A, dtype=np.int64) % p
    rows, cols = A.shape
    R = A.copy()
    piv = []
    r = 0
    for c in range(cols):
        if r == rows:
            break
        nz = np.nonzero(R[r:, c])[0]
        if len(nz) == 0:
            continue
        k = r + nz[0]
        R[[r, k]] = R[[k, r]]
        R[r] = R[r] * pow(int(R[r, c]), p - 2, p) % p
        for o in np.nonzero(R[:, c])[0]:
            if o != r:
                R[o] = (R[o] - R[o, c] * R[r]) % p
        piv.append(c)
        r += 1
    basis = []
    for f in [c for c in range(cols) if c not in piv]:
        v = np.zeros(cols, dtype=np.int64)
        v[f] = 1
        for i, c in enumerate(piv):
            v[c] = (-R[i, f]) % p
        basis.append(v)
    return np.array(basis, dtype=np.int64).reshape(len(basis), cols)


def J_matrix(n, p):
    M = np.zeros((n, n), dtype=np.int64)
    for q in range(n):
        M[q, q] = 1
        for q2 in range(q):
            M[q, q2] = 2 * (-1) ** (q - q2)
    return M % p


def color_step(sv, g, p):
    """Fox-coloring transport (beta = -1) of a batch of color vectors through one letter"""
    i = abs(g) - 1
    a, b = sv[:, i].copy(), sv[:, i + 1].copy()
    if g > 0:
        sv[:, i], sv[:, i + 1] = (2 * a - b) % p, a
    else:
        sv[:, i], sv[:, i + 1] = b, (2 * b - a) % p


def transport(sv, word, upto, p):
    sv = np.array(sv, dtype=np.int64).copy()
    for g in word[:upto]:
        color_step(sv, g, p)
    return sv


class BraidModel:
    def __init__(self, word, n, p, r=2):
        self.word, self.n, self.p, self.r = list(word), n, p, r
        m = len(word)
        self.D = np.diag([1, p - 1, 1, p - 1]).astype(np.int64)
        order, q, l, steps = [], 0, 0, 0
        while True:
            g = word[l]
            i = abs(g) - 1
            if q in (i, i + 1):
                left = q == i
                over = (left and g > 0) or (not left and g < 0)
                if not over:
                    order.append(l)
                q = i + 1 if left else i
            l = (l + 1) % m
            steps += 1
            if l == 0 and q == 0:
                break
        assert steps == n * m, "closure is not a knot"
        self.lam_order = order
        self.writhe = sum(1 if g > 0 else -1 for g in word)
        self.Bur = transport(np.eye(n, dtype=np.int64), word, m, p).T % p     # top colors -> bottom colors
        self.Fix = nullspace_mod((self.Bur - np.eye(n, dtype=np.int64)) % p, p)
        self.L2 = self._linear_part((0, 2))
        self.L24 = self._linear_part((1, 3))
        self.L3 = self._linear_part((0, 3))
        self.J = J_matrix(n, p)

    def inv(self, X):
        p = self.p
        N = (X @ self.D - np.eye(4, dtype=np.int64)) % p
        N2 = N @ N % p
        U = (np.eye(4, dtype=np.int64) - N + N2 - N2 @ N) % p
        return self.D @ U % p

    def run(self, X):
        """X: (batch, n, 4, 4) top labels -> relator values (batch, n + 1, 4, 4)"""
        p, n = self.p, self.n
        cur = X.copy()
        overs = {}
        for l, g in enumerate(self.word):
            i = abs(g) - 1
            a, b = cur[:, i].copy(), cur[:, i + 1].copy()
            if g > 0:
                overs[l] = a
                cur[:, i], cur[:, i + 1] = self.inv(a) @ b % p @ a % p, a
            else:
                overs[l] = b
                cur[:, i], cur[:, i + 1] = b, b @ a % p @ self.inv(b) % p
        vals = np.zeros((X.shape[0], n + 1, 4, 4), dtype=np.int64)
        for q in range(n):
            vals[:, q] = self.inv(X[:, q]) @ cur[:, q] % p
        lam = np.broadcast_to(np.eye(4, dtype=np.int64), X[:, 0].shape).copy()
        for l in self.lam_order:
            lam = lam @ (overs[l] if self.word[l] > 0 else self.inv(overs[l])) % p
        x0 = X[:, 0]
        x0i = self.inv(x0)
        for _ in range(abs(self.writhe)):
            lam = lam @ (x0i if self.writhe > 0 else x0) % p
        S = x0
        for _ in range(self.r - 1):
            S = S @ x0 % p
        vals[:, n] = S @ lam % p
        return vals

    def labels(self, cy, cx, cw, a, b, t):
        p, n = self.p, self.n
        bs = cy.shape[0]
        U = np.broadcast_to(np.eye(4, dtype=np.int64), (bs, n, 4, 4)).copy()
        U[:, :, 0, 1], U[:, :, 1, 2], U[:, :, 2, 3] = cy, cx, cw
        U[:, :, 0, 2], U[:, :, 1, 3], U[:, :, 0, 3] = a, b, t
        return U @ self.D % p

    def _linear_part(self, ent):
        n = self.n
        Z = np.zeros((n, n), dtype=np.int64)
        args = [Z] * 6
        args = list(args)
        args[{(0, 2): 3, (1, 3): 4, (0, 3): 5}[ent]] = np.eye(n, dtype=np.int64)
        vals = self.run(self.labels(*args))
        return vals[:, :, ent[0], ent[1]].T % self.p        # (n + 1) x n

    def obstruction(self, cy, cx, cw):
        """batched (batch, n) top colorings -> layer-3 relator values (batch, n + 1); asserts layers 1 and 2"""
        p, n = self.p, self.n
        bs = cy.shape[0]
        Z = np.zeros((bs, n), dtype=np.int64)
        v0 = self.run(self.labels(cy, cx, cw, Z, Z, Z))
        assert not (v0[:, :, 0, 1] % p).any() and not (v0[:, :, 1, 2] % p).any() and not (v0[:, :, 2, 3] % p).any(), \
            "layer 1 is not a cocycle"
        A = rref_solve(self.L2, (-v0[:, :, 0, 2]).T % p, p)
        Bb = rref_solve(self.L24, (-v0[:, :, 1, 3]).T % p, p)
        assert A is not None and Bb is not None and not isinstance(A, str) and not isinstance(Bb, str), \
            "layer 2 not uniquely solvable"
        v1 = self.run(self.labels(cy, cx, cw, A.T, Bb.T, Z))
        assert not (v1[:, :, 0, 2] % p).any() and not (v1[:, :, 1, 3] % p).any()
        return v1[:, :, 0, 3] % p

    def y_of(self, s):
        return np.concatenate([(s @ self.J) % self.p, np.zeros((s.shape[0], 1), dtype=np.int64)], axis=1)

    def Q(self, cy, cx, cw, s):
        return (self.obstruction(cy, cx, cw) * self.y_of(s)).sum(axis=1) % self.p

    def Q_vanishes_identically(self, cy, cx, cw):
        """for each sample: Q(c; .) = 0 on all of Fix"""
        o = self.obstruction(cy, cx, cw)
        Y = self.y_of(self.Fix)
        return ~((o @ Y.T) % self.p).any(axis=1)
