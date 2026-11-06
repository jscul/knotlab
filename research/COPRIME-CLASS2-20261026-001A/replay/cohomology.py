"""Twisted cocycles, coboundaries and the lifting obstruction for M = S^3_p(K).

Presentation (see braids.py): generators = top arcs x_0..x_{n-1}; relators =
n closure relators and the surgery relator.  A homomorphism to G with
meridians in N h^k_mu is given by lifts x_q -> (a_q, b_q, z_q, k_mu).

* The subgroup {(c, 0, 0, k)} of G is F4 twisted by w^(2k) (x-coordinate);
  {(0, 0, c, k)} is F4 twisted by w^k (z-coordinate).  Evaluating the relators
  on top arcs (c_q, 0, 0, k_mu) gives the Fox-calculus matrix of 1-cocycles
  with coefficients F4_{w^(2 k_mu)} (k_mu = 1: the w^2 twist of the claim);
  on (0, 0, z_q, k_mu) it gives the coboundary map delta: C^1 -> C^2 of the
  central coefficients F4_{w^(k_mu)}.
* For cocycles a, b, the relators evaluated on (a_q, b_q, 0, k_mu) lie in the
  centre; their z-coordinates o(a, b) form a bilinear map, and (a, b) lifts to
  a homomorphism iff o(a, b) lies in im(delta) (z_q shifts o by delta(z)).
  o(a, b) mod im(delta) is the cup-product obstruction a u b.
* N = #{(a, b) in V x V : o(a, b) in im(delta)}, V a complement of the
  coboundaries B^1 in Z^1 (so V ~ H^1, dim V = d).  For fixed a the condition
  is linear in b, so N = sum_a 4^(d - rank L_a).

Independent replay code: written from scratch, standard library only.
"""
import random

from f4 import (MUL, nullspace, transpose, mat_vec, lin_comb, dot, in_span,
                pack, scale_bits, rank_bits, projective_points, rref, rank)
from group import MULT, IDENTITY, encode, decode


def relator_matrix(knot, k_mu, coord, p):
    """(n+1) x n matrix: top-arc values in F4 -> relator values, for the
    abelian subgroup given by coord ('x' or 'z')."""
    n = knot.n
    base = encode(0, 0, 0, k_mu)
    unit = encode(1, 0, 0, k_mu) if coord == 'x' else encode(0, 0, 1, k_mu)
    cols = []
    for j in range(n):
        top = [base] * n
        top[j] = unit
        col = []
        for r in knot.relator_values(knot.propagate(top), p):
            x, y, z, k = decode(r)
            assert k == 0 and y == 0 and (z == 0 if coord == 'x' else x == 0)
            col.append(x if coord == 'x' else z)
        cols.append(col)
    return transpose(cols, n + 1)


def _check_linear(knot, M, k_mu, coord, p, rng, trials=3):
    n = knot.n
    for _ in range(trials):
        v = [rng.randrange(4) for _ in range(n)]
        top = [encode(c, 0, 0, k_mu) if coord == 'x' else encode(0, 0, c, k_mu)
               for c in v]
        got = [decode(r)[0 if coord == 'x' else 2]
               for r in knot.relator_values(knot.propagate(top), p)]
        assert got == mat_vec(M, v), "relator map not F4-linear"


def obstruction_vector(knot, a, b, k_mu, p):
    top = [encode(a[q], b[q], 0, k_mu) for q in range(knot.n)]
    out = []
    for r in knot.relator_values(knot.propagate(top), p):
        x, y, z, k = decode(r)
        assert (x, y, k) == (0, 0, 0), "relator value not central: (a, b) not cocycles"
        out.append(z)
    return out


class TwistedData:
    """d, V, the annihilator P of im(delta), and the projected obstruction
    tensor T[i][j] = P o(V_i, V_j) for the meridian character k_mu."""

    def __init__(self, knot, k_mu=1, p=3, seed=1):
        rng = random.Random(seed)
        n = knot.n
        self.knot, self.k_mu, self.p, self.n = knot, k_mu, p, n
        Mx = relator_matrix(knot, k_mu, 'x', p)
        Mz = relator_matrix(knot, k_mu, 'z', p)
        _check_linear(knot, Mx, k_mu, 'x', p, rng)
        _check_linear(knot, Mz, k_mu, 'z', p, rng)
        self.Z1 = nullspace(Mx, n)
        ones = [1] * n                      # coboundary of m: c(x_q) = (t - 1) m
        assert in_span(ones, self.Z1, n)
        self.coboundary = ones
        self.V = nullspace(Mx + [[1] + [0] * (n - 1)], n)    # c(x_0) = 0
        self.d = len(self.V)
        assert self.d == len(self.Z1) - 1
        # cocycles of the knot group already satisfy the surgery relator
        self.surgery_free_on_cocycles = (len(nullspace(Mx[:n], n)) == len(self.Z1))
        self.ker_delta_dim = len(nullspace(Mz, n))           # lifts per pair
        self.P = nullspace(transpose(Mz, n), n + 1)           # annihilates im delta
        self.q = len(self.P)
        d = self.d
        self.T = [[self.project(obstruction_vector(knot, self.V[i], self.V[j], k_mu, p))
                   for j in range(d)] for i in range(d)]
        self._check_classes_and_bilinearity(rng)

    def project(self, o):
        return [dot(row, o) for row in self.P]

    def obstruction(self, a, b):
        return self.project(obstruction_vector(self.knot, a, b, self.k_mu, self.p))

    def _check_classes_and_bilinearity(self, rng):
        n, d, zero = self.n, self.d, [0] * self.q
        u = self.coboundary
        # the obstruction only depends on cohomology classes
        assert self.obstruction(u, u) == zero
        for v in self.V:
            assert self.obstruction(u, v) == zero and self.obstruction(v, u) == zero
        # bilinearity of (a, b) -> P o(a, b) on random elements of V
        for _ in range(4):
            al = [rng.randrange(4) for _ in range(d)]
            be = [rng.randrange(4) for _ in range(d)]
            a = lin_comb(al, self.V, n)
            b = lin_comb(be, self.V, n)
            expect = [0] * self.q
            for i in range(d):
                for j in range(d):
                    c = MUL[al[i]][be[j]]
                    if c:
                        for t in range(self.q):
                            expect[t] ^= MUL[c][self.T[i][j][t]]
            assert self.obstruction(a, b) == expect, "obstruction not bilinear"

    def is_identically_zero(self):
        return all(not any(v) for row in self.T for v in row)

    def count_pairs(self):
        return count_vanishing_pairs(self.T, self.d)

    def hom_count_term(self, N):
        """Homomorphisms with meridian in N h^k_mu: |B^1|^2 N |Z^1(F4_z)|."""
        return 16 * N * 4 ** self.ker_delta_dim


def _packed(T, d):
    """scaled[i][c][j] = c * T[i][j], bit-sliced."""
    return [[[scale_bits(c, *pack(T[i][j])) for j in range(d)] for c in range(4)]
            for i in range(d)]


def _rows(scaled, a, d):
    rows = []
    for j in range(d):
        lo = hi = 0
        for i, c in a:
            slo, shi = scaled[i][c][j]
            lo ^= slo
            hi ^= shi
        rows.append((lo, hi))
    return rows


def count_vanishing_pairs(T, d):
    """#{(a, b) in F4^d x F4^d : sum_ij a_i b_j T[i][j] = 0} where each T[i][j]
    is a vector over F4.  Sum over a (one per line, times 3) of 4^dim ker."""
    if d == 0:
        return 1
    scaled = _packed(T, d)
    total = 4 ** d                                      # a = 0
    for a in projective_points(d):
        total += 3 * 4 ** (d - rank_bits(_rows(scaled, a, d)))
    return total


def compare_pair_conditions(T1, T2, d):
    """Count for both tensors and test, for every a, that the b-solution spaces
    {b : T1(a, b) = 0} and {b : T2(a, b) = 0} coincide (rank test on the
    concatenation).  Returns (N1, N2, number of lines a where they differ)."""
    if d == 0:
        return 1, 1, 0
    s1, s2 = _packed(T1, d), _packed(T2, d)
    width = max(len(T1[0][0]), 1)
    N1 = N2 = 4 ** d
    differ = 0
    for a in projective_points(d):
        r1, r2 = _rows(s1, a, d), _rows(s2, a, d)
        k1, k2 = rank_bits(r1), rank_bits(r2)
        both = rank_bits([(l1 | (l2 << width), h1 | (h2 << width))
                          for (l1, h1), (l2, h2) in zip(r1, r2)])
        N1 += 3 * 4 ** (d - k1)
        N2 += 3 * 4 ** (d - k2)
        if not (k1 == k2 == both):
            differ += 1
    return N1, N2, differ


# ------------------------------------------------------------ steering law
def leaf_functionals(knot, V, k_mu, level, offset, size=3, order="right_to_left"):
    """l_j(e) = c_e(x_{q+2} x_{q+1} x_q), q = offset + size*j, for the arcs at
    the given level of `knot`, for each basis cocycle e in V.  Returns a
    d x 3 list.  order="left_to_right" uses x_q x_{q+1} x_{q+2} instead
    (diagnostic only)."""
    arcs = knot.level_arcs[level]
    out = []
    for v in V:
        img = knot.propagate([encode(c, 0, 0, k_mu) for c in v])
        row = []
        for j in range(3):
            q = offset + size * j
            g = IDENTITY
            rs = reversed(range(size)) if order == "right_to_left" else range(size)
            for r in rs:                          # default: x_{q+2} x_{q+1} x_q
                g = MULT[g][img[arcs[q + r]]]
            x, y, z, k = decode(g)
            assert (y, z, k) == (0, 0, 0)
            row.append(x)
        out.append(row)
    return out


def det3(r1, r2, r3):
    """3x3 determinant over F4 (characteristic 2: signs are irrelevant)."""
    m = MUL
    return (m[r1[0]][m[r2[1]][r3[2]] ^ m[r2[2]][r3[1]]]
            ^ m[r1[1]][m[r2[0]][r3[2]] ^ m[r2[2]][r3[0]]]
            ^ m[r1[2]][m[r2[0]][r3[1]] ^ m[r2[1]][r3[0]]])


def predicted_tensor(leaf_lists, d, coefficients=None):
    """T[i][j] = (sum_ins c_ins det(l(e_i), l(e_j), l(e_k)))_k."""
    if coefficients is None:
        coefficients = [1] * len(leaf_lists)
    T = [[[0] * d for _ in range(d)] for _ in range(d)]
    for leaves, c in zip(leaf_lists, coefficients):
        for i in range(d):
            for j in range(d):
                for k in range(d):
                    T[i][j][k] ^= MUL[c][det3(leaves[i], leaves[j], leaves[k])]
    return T


def solve(A_rows, b, ncols):
    """One solution x of A x = b over F4, or None if inconsistent."""
    R, piv = rref([list(r) + [v] for r, v in zip(A_rows, b)], ncols + 1)
    if ncols in piv:
        return None
    x = [0] * ncols
    for i, c in enumerate(piv):
        x[c] = R[i][ncols]
    return x


def linear_identification(T_direct, T_pred, d, q):
    """Is there a linear map Phi: F4^d -> F4^q with T_direct[i][j] =
    Phi(T_pred[i][j]) for all i, j, injective on the span S of the T_pred
    values?  Returns (exists, dim S, rank of Phi on S)."""
    A = [T_pred[i][j] for i in range(d) for j in range(d)]
    Phi = []
    for t in range(q):
        phi = solve(A, [T_direct[i][j][t] for i in range(d) for j in range(d)], d)
        if phi is None:
            return False, rank(A, d), None
        Phi.append(phi)
    S = [list(v) for v in A]
    images = [mat_vec(Phi, v) for v in S]
    return True, rank(S, d), rank(images, q)
