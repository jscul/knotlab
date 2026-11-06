"""Second implementation (cross-check) for BEYOND-CLASS2-20261027-001B-E001: the level presentation of S^3_2(closure of a
braid word), with one generator per strand and level, one relator per strand and level and the surgery relator; layers are
solved with ticket A's Fox calculus (bc_lib), relators are evaluated as 4x4 matrices over F_p one by one, and the form is
Q(c; s) = <o(c), y(s)> with y(s)_{(l, q)} = (J s_{l+1})_q (J as in bm.py, untransposed) and surgery component 0."""
import itertools
import numpy as np


def level_presentation(word, n, r):
    m = len(word)

    def gen(l, q):
        return (l % m) * n + q

    rel = {}
    for l, g in enumerate(word):
        i = abs(g) - 1
        for q in range(n):
            if q not in (i, i + 1):
                rel[(l, q)] = [(gen(l + 1, q), -1), (gen(l, q), 1)]
        a, b = gen(l, i), gen(l, i + 1)
        if g > 0:
            rel[(l, i)] = [(gen(l + 1, i), -1), (a, -1), (b, 1), (a, 1)]
            rel[(l, i + 1)] = [(gen(l + 1, i + 1), -1), (a, 1)]
        else:
            rel[(l, i)] = [(gen(l + 1, i), -1), (b, 1)]
            rel[(l, i + 1)] = [(gen(l + 1, i + 1), -1), (b, 1), (a, 1), (b, -1)]
    lam, q, l, steps = [], 0, 0, 0
    while True:
        g = word[l]
        i = abs(g) - 1
        s = 1 if g > 0 else -1
        if q in (i, i + 1):
            left = q == i
            over = (left and g > 0) or (not left and g < 0)
            if not over:
                lam.append((gen(l, i + 1 if left else i), s))
            q = i + 1 if left else i
        l = (l + 1) % m
        steps += 1
        if l == 0 and q == 0:
            break
    assert steps == n * m, "closure is not a knot"
    w = sum(1 if g > 0 else -1 for g in word)
    lam += [(gen(0, 0), -1)] * w if w >= 0 else [(gen(0, 0), 1)] * (-w)
    keys = sorted(rel)
    return n * m, [rel[k] for k in keys] + [[(gen(0, 0), 1)] * r + lam], keys, gen


class LevelModel:
    def __init__(self, word, n, p, B, r=2):
        self.word, self.n, self.p, self.B, self.m = list(word), n, p, B, len(word)
        self.U, self.rels, self.keys, self.gen = level_presentation(word, n, r)
        self.Ab = B.fox(self.U, self.rels, p - 1, p)
        self.At = B.fox(self.U, self.rels, 1, p)
        self.Z1 = B.z1(self.U, self.rels, p - 1, p)
        basis = [[(p - 2) % p] * self.U]
        self.H = []
        for z in self.Z1:
            if B.rank(basis + [z], p) > len(basis):
                basis.append(z)
                self.H.append(z)
        self.D = np.diag([1, p - 1, 1, p - 1]).astype(np.int64)
        J = np.zeros((n, n), dtype=np.int64)
        for q in range(n):
            J[q, q] = 1
            for q2 in range(q):
                J[q, q2] = 2 * (-1) ** (q - q2)
        self.J = J % p

    def mats(self, cy, cx, cw, a, b, t):
        out = []
        for g in range(self.U):
            Ug = np.eye(4, dtype=np.int64)
            Ug[0, 1], Ug[1, 2], Ug[2, 3], Ug[0, 2], Ug[1, 3], Ug[0, 3] = cy[g], cx[g], cw[g], a[g], b[g], t[g]
            out.append(Ug.dot(self.D) % self.p)
        return out

    def evalrels(self, M):
        p = self.p
        inv = {}
        vals = []
        for R in self.rels:
            X = np.eye(4, dtype=np.int64)
            for g, s in R:
                if s > 0:
                    X = X.dot(M[g]) % p
                else:
                    if g not in inv:
                        N = (M[g].dot(self.D) - np.eye(4, dtype=np.int64)) % p
                        U = (np.eye(4, dtype=np.int64) - N + N.dot(N) - N.dot(N).dot(N)) % p
                        inv[g] = self.D.dot(U) % p
                    X = X.dot(inv[g]) % p
            vals.append(X)
        return vals

    def obstruction(self, cy, cx, cw):
        p, U, B = self.p, self.U, self.B
        z = [0] * U
        V0 = self.evalrels(self.mats(cy, cx, cw, z, z, z))
        assert all(X[0, 1] == 0 and X[1, 2] == 0 and X[2, 3] == 0 for X in V0), "layer 1"
        sa = B.solve_affine(self.At, [(-X[0, 2]) % p for X in V0], p)
        sb = B.solve_affine(self.At, [(-X[1, 3]) % p for X in V0], p)
        assert sa is not None and sb is not None and not sa[1] and not sb[1], "layer 2 not uniquely solvable"
        V1 = self.evalrels(self.mats(cy, cx, cw, sa[0], sb[0], z))
        assert all(X[0, 2] == 0 and X[1, 3] == 0 for X in V1)
        return [int(X[0, 3]) for X in V1]

    def y_of(self, s):
        p, n, m = self.p, self.n, self.m
        lev = [np.array([s[self.gen(l, q)] for q in range(n)]) for l in range(m)]
        return [int(self.J.dot(lev[(l + 1) % m])[q] % p) for (l, q) in self.keys] + [0]

    def in_left_kernel(self, y):
        p = self.p
        return all(sum(y[t] * self.Ab[t][g] for t in range(len(self.rels))) % p == 0 for g in range(self.U))

    def table(self, classes):
        """Q[(iw, ix, iy, is)] = <o(c_y = classes[iy], c_x = classes[ix], c_w = classes[iw]), y(classes[is])>"""
        ys = [self.y_of(s) for s in classes]
        T = {}
        for iw, ix, iy in itertools.product(range(len(classes)), repeat=3):
            o = self.obstruction(classes[iy], classes[ix], classes[iw])
            for i_s, y in enumerate(ys):
                T[(iw, ix, iy, i_s)] = sum(a * b for a, b in zip(o, y)) % self.p
        return T

    def matched(self, other_classes, other):
        """classes of this model with the same level-0 values as the given classes of another LevelModel"""
        p, n, B = self.p, self.n, self.B
        rows = [[z[self.gen(0, q)] for q in range(n)] for z in self.Z1]
        out = []
        for s in other_classes:
            target = [s[other.gen(0, q)] for q in range(n)]
            sol = B.solve_affine([list(col) for col in zip(*rows)], target, p)
            assert sol is not None
            out.append([sum(c * z[g] for c, z in zip(sol[0], self.Z1)) % p for g in range(self.U)])
        return out
