"""Graded Lie algebras of class at most 3 over F_p with a split C_r action, their BCH groups, and layered counts of
homomorphisms from finitely presented groups (BEYOND-CLASS2-20261027-001A; read-only for later tickets of the epic).

Conventions.
- p >= 5 prime, r | p - 1, Z = the smallest element of order r in F_p^x. A character is an exponent e in Z/r.
- A graded Lie algebra is given by basis elements with (degree, character exponent) and a bracket table
  br[(i, j)] = {k: coefficient} for basis indices i, j (antisymmetric, compatible with degrees and characters, Jacobi checked).
- The group is (F_p^n, *) with the Baker-Campbell-Hausdorff product to degree 3:
  X * Y = X + Y + (1/2)[X, Y] + (1/12)([X, [X, Y]] - [Y, [X, Y]]),
  which for class at most 3 and p >= 5 is a group of exponent p (Lazard correspondence). C_r acts on basis element i by
  Z^(k e_i), an automorphism because the bracket respects characters.
- A homomorphism pi -> N x| C_r over psi_k (every generator a meridian mapped to the k-th power of the generator) is a map f on
  generators with f(gh) = f(g) * (g . f(h)); relators must evaluate to the identity.
"""
import itertools

import numpy as np


def elem_of_order(p, r):
    for g in range(2, p):
        if pow(g, r, p) == 1 and all(pow(g, d, p) != 1 for d in range(1, r)):
            return g
    return 1


# ------------------------------------------------------------------------------------------------ linear algebra mod p

def rref(rows, p):
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
    if not rows:
        return [[int(i == j) for j in range(n)] for i in range(n)]
    R, piv = rref(rows, p)
    out = []
    for f in [j for j in range(n) if j not in set(piv)]:
        v = [0] * n
        v[f] = 1
        for row, c in zip(R, piv):
            v[c] = (-row[f]) % p
        out.append(v)
    return out


def span_all(vectors, p, n):
    """every element of the span (vectors nonempty list of length-n lists); [0] if empty"""
    if not vectors:
        return [tuple([0] * n)]
    out = []
    for coefs in itertools.product(range(p), repeat=len(vectors)):
        out.append(tuple(sum(c * v[g] for c, v in zip(coefs, vectors)) % p for g in range(n)))
    return out


def solve_affine(A, b, p):
    """all x with A x = b (A: list of rows, n columns): (particular solution, kernel basis) or None"""
    n = len(A[0]) if A else 0
    if not A:
        return [0] * n, [[int(i == j) for j in range(n)] for i in range(n)]
    aug = [list(row) + [bb] for row, bb in zip(A, b)]
    R, piv = rref(aug, p)
    if n in piv:
        return None
    x = [0] * n
    for row, c in zip(R, piv):
        x[c] = row[n] % p
    return x, nullspace(A, n, p)


# ------------------------------------------------------------------------------------------------ graded Lie algebras

class GradedLie:
    """basis with degrees and character exponents; bracket table on basis pairs"""

    def __init__(self, p, r, names, degrees, chars, brackets):
        self.p, self.r = p, r
        self.names, self.deg, self.chi = list(names), list(degrees), [c % r for c in chars]
        self.n = len(names)
        self.idx = {nm: i for i, nm in enumerate(self.names)}
        self.br = {}
        for (a, b), val in brackets.items():
            i, j = self.idx[a], self.idx[b]
            vec = {self.idx[k]: c % p for k, c in val.items() if c % p}
            self.br[(i, j)] = vec
            self.br[(j, i)] = {k: (-c) % p for k, c in vec.items()}
        self.Z = elem_of_order(p, r)
        self.half = pow(2, p - 2, p)
        self.twelfth = pow(12, p - 2, p)
        self.check()

    def check(self):
        p, r = self.p, self.r
        for (i, j), vec in self.br.items():
            for k, c in vec.items():
                assert self.deg[k] == self.deg[i] + self.deg[j], "bracket not graded"
                assert (self.chi[i] + self.chi[j] - self.chi[k]) % r == 0, "bracket not equivariant"
        # Jacobi on basis triples
        for a in range(self.n):
            for b in range(self.n):
                for c in range(self.n):
                    s = self.add(self.add(self.bracket(self.unit(a), self.bracket(self.unit(b), self.unit(c))),
                                          self.bracket(self.unit(b), self.bracket(self.unit(c), self.unit(a)))),
                                 self.bracket(self.unit(c), self.bracket(self.unit(a), self.unit(b))))
                    assert not any(s), f"Jacobi fails on {self.names[a]}, {self.names[b]}, {self.names[c]}"
        assert max(self.deg) <= 3

    def unit(self, i):
        v = [0] * self.n
        v[i] = 1
        return tuple(v)

    def zero(self):
        return tuple([0] * self.n)

    def add(self, X, Y):
        return tuple((a + b) % self.p for a, b in zip(X, Y))

    def scale(self, c, X):
        return tuple(c * a % self.p for a in X)

    def bracket(self, X, Y):
        p = self.p
        out = [0] * self.n
        for i, a in enumerate(X):
            if not a:
                continue
            for j, b in enumerate(Y):
                if not b:
                    continue
                vec = self.br.get((i, j))
                if vec:
                    ab = a * b % p
                    for k, c in vec.items():
                        out[k] = (out[k] + ab * c) % p
        return tuple(out)

    def act(self, e, X):
        """the generator to the power e acting on X"""
        p, Z = self.p, self.Z
        return tuple(pow(Z, (e * self.chi[i]) % self.r, p) * a % p for i, a in enumerate(X))

    def bch(self, X, Y):
        XY = self.bracket(X, Y)
        out = self.add(self.add(X, Y), self.scale(self.half, XY))
        cubic = self.add(self.bracket(X, XY), self.scale(self.p - 1, self.bracket(Y, XY)))
        return self.add(out, self.scale(self.twelfth, cubic))

    # group N x| C_r: elements (X, e)
    def mul(self, g, h):
        (X, e), (Y, f) = g, h
        return (self.bch(X, self.act(e, Y)), (e + f) % self.r)

    def inv(self, g):
        X, e = g
        return (self.act((-e) % self.r, self.scale(self.p - 1, X)), (-e) % self.r)

    def ident(self):
        return (self.zero(), 0)

    def word(self, w, images):
        out = self.ident()
        for g, s in w:
            x = images[g] if s > 0 else self.inv(images[g])
            for _ in range(abs(s)):
                out = self.mul(out, x)
        return out

    def layer(self, d):
        return [i for i in range(self.n) if self.deg[i] == d]


def cross_layer_algebra(p, r, alpha_exp):
    """free class 3 on x (trivial character) and y (character Z^alpha_exp): z = [x, y], a = [x, z], b = [y, z]"""
    e = alpha_exp
    return GradedLie(p, r, ["x", "y", "z", "a", "b"], [1, 1, 2, 3, 3], [0, e, e, e, 2 * e],
                     {("x", "y"): {"z": 1}, ("x", "z"): {"a": 1}, ("y", "z"): {"b": 1}})


def four_way_algebra(p, r, alpha_exp):
    """x (alpha), y (alpha^-1), w (alpha^-1); z = [x, y], u = [w, x] (trivial characters); t = [w, z] = -[y, u] (alpha^-1);
    [w, y] = 0 and every other bracket zero. No pair of nontrivial characters with nontrivial product brackets nontrivially."""
    e = alpha_exp
    return GradedLie(p, r, ["x", "y", "w", "z", "u", "t"], [1, 1, 1, 2, 2, 3], [e, -e, -e, 0, 0, -e],
                     {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}})


def heisenberg_algebra(p, r, a_exp, b_exp):
    return GradedLie(p, r, ["x", "y", "z"], [1, 1, 2], [a_exp, b_exp, a_exp + b_exp], {("x", "y"): {"z": 1}})


def graded_hard_pairs(L):
    """pairs of basis elements with nontrivial characters, nontrivial product, and nonzero bracket"""
    out = []
    for (i, j), vec in L.br.items():
        if i < j and vec and L.chi[i] and L.chi[j] and (L.chi[i] + L.chi[j]) % L.r:
            out.append((L.names[i], L.names[j]))
    return out


# ------------------------------------------------------------------------------------------------ twisted Fox calculus

def fox(U, rels, mult, p):
    """rows: c(relator) in terms of c(generator), for a cocycle twisted by mult on every (meridian) generator"""
    inv = pow(mult, p - 2, p)
    rows = []
    for rel in rels:
        row, pref = [0] * U, 1
        for g, s in rel:
            for _ in range(abs(s)):
                if s > 0:
                    row[g] = (row[g] + pref) % p
                    pref = pref * mult % p
                else:
                    pref = pref * inv % p
                    row[g] = (row[g] - pref) % p
        rows.append(row)
    return rows


def z1(U, rels, mult, p):
    return nullspace(fox(U, rels, mult, p), U, p)


# ------------------------------------------------------------------------------------------------ layered direct counts

def direct_count(L, U, rels, k, fix_f1=None):
    """#Hom over psi_k by the group law: enumerate layer-1 cocycles, solve the affine layer-2 system (L2 central modulo L3),
    enumerate its solutions, and test the affine layer-3 system. fix_f1: optional dict basis index -> list of values on
    generators (then only that layer-1 map is completed; returns the number of completions)."""
    p, r = L.p, L.r
    L1, L2, L3 = L.layer(1), L.layer(2), L.layer(3)
    mult = {i: pow(L.Z, (k * L.chi[i]) % r, p) for i in range(L.n)}
    foxm = {i: fox(U, rels, mult[i], p) for i in range(L.n)}
    nrel = len(rels)
    # layer 3: number of solutions when solvable, and reducers
    z1_size3 = 1
    red3 = {}
    for i in L3:
        cols = [[foxm[i][t][g] for t in range(nrel)] for g in range(U)]
        red3[i] = rref(cols, p)
        z1_size3 *= p ** (U - rank(foxm[i], p))

    def in_image(i, vec):
        R, piv = red3[i]
        v = list(vec)
        for row, c in zip(R, piv):
            f = v[c]
            if f:
                v = [(x - f * y) % p for x, y in zip(v, row)]
        return not any(v)

    def evaluate(F):
        """relator values for the map with coordinates F[i][g] (all layers), as lists over relators of N-components"""
        imgs = [(tuple(F[i][g] for i in range(L.n)), k % r) for g in range(U)]
        vals = []
        for rel in rels:
            X, e = L.word(rel, imgs)
            assert e == 0
            vals.append(X)
        return vals

    if fix_f1 is None:
        spaces = [span_all(z1(U, rels, mult[i], p), p, U) for i in L1]
        f1_iter = itertools.product(*spaces)
    else:
        f1_iter = [tuple(tuple(fix_f1[i]) for i in L1)]
    total = 0
    for f1 in f1_iter:
        F = {i: [0] * U for i in range(L.n)}
        for i, vals in zip(L1, f1):
            F[i] = list(vals)
        vals = evaluate(F)
        if any(v[i] for v in vals for i in L1):
            raise AssertionError("not a layer-1 cocycle")
        # layer 2: Fox_i f2_i = -const_i for each i in L2
        sols = []
        ok = True
        for i in L2:
            const = [v[i] for v in vals]
            s = solve_affine(foxm[i], [(-c) % p for c in const], p)
            if s is None:
                ok = False
                break
            sols.append(s)
        if not ok:
            continue
        f2_spaces = []
        for (part, ker) in sols:
            pts = span_all(ker, p, U) if ker else [tuple([0] * U)]
            f2_spaces.append([tuple((a + b) % p for a, b in zip(part, q)) for q in pts])
        for f2 in itertools.product(*f2_spaces):
            G = {i: list(F[i]) for i in F}
            for i, vals2 in zip(L2, f2):
                G[i] = list(vals2)
            v3 = evaluate(G)
            assert not any(v[i] for v in v3 for i in L1 + L2)
            if all(in_image(i, [v[i] for v in v3]) for i in L3):
                total += z1_size3
    return total


def b1_size(U, rels, mult, p):
    return p if mult != 1 else 1
