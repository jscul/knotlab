"""Braid helpers for BEYOND-CLASS2-20261027-001B-E001: Artin action (cp_lib's propagation convention), geometric
conjugators of a braid, Magnus expansion, and the degree-3 tensor of a pure braid in the third lower central term.

Convention (as cp_lib.presentation): the letter g acts on 0-based positions i = |g| - 1 and i + 1.  For g > 0 the left strand
(position i) passes over and moves to i + 1; the under strand gets x_i^-1 x_{i+1} x_i.  For g < 0 the right strand passes over
and moves to i; the under strand gets x_{i+1} x_i x_{i+1}^-1.  Words in the free group are lists of (generator, +-1)."""


def red(w):
    out = []
    for t in w:
        if out and out[-1][0] == t[0] and out[-1][1] == -t[1]:
            out.pop()
        else:
            out.append(t)
    return out


def inv(w):
    return [(g, -s) for g, s in reversed(w)]


def artin_conj(word, n):
    """geometric conjugators: entry q is (W_q, g_q) with image of x_q = W_q x_{g_q} W_q^-1 (W_q not reduced against x_g)"""
    st = [([], i) for i in range(n)]

    def full(e):
        W, g = e
        return W + [(g, 1)] + inv(W)

    for g in word:
        i = abs(g) - 1
        a, b = st[i], st[i + 1]
        if g > 0:
            st[i], st[i + 1] = (red(inv(full(a)) + b[0]), b[1]), a
        else:
            st[i], st[i + 1] = b, (red(full(b) + a[0]), a[1])
    return st


def artin(word, n):
    return [red(W + [(g, 1)] + inv(W)) for W, g in artin_conj(word, n)]


def subst(W, Yof):
    out = []
    for g, s in W:
        out += Yof(g) if s > 0 else inv(Yof(g))
    return out


def magnus(w, deg, p):
    """Magnus expansion x -> 1 + X, x^-1 -> 1 - X + X^2 - ..., truncated at degree deg, coefficients mod p"""
    poly = {(): 1}
    for g, s in w:
        if s > 0:
            factor = {(): 1, (g,): 1}
        else:
            factor = {(): 1}
            for k in range(1, deg + 1):
                factor[(g,) * k] = (-1) ** k
        new = {}
        for a, ca in poly.items():
            for b, cb in factor.items():
                if len(a) + len(b) <= deg:
                    new[a + b] = (new.get(a + b, 0) + ca * cb) % p
        poly = {k: v for k, v in new.items() if v}
    return poly


def degree3_tensor(word, n, p):
    """for a pure braid whose conjugators lie in the third lower central term: M[j] = {(i1, i2, i3): coefficient} (degree-3
    Magnus part of W_j); asserts purity and the vanishing of degrees 1 and 2"""
    st = artin_conj(word, n)
    M = []
    for j, (W, g) in enumerate(st):
        assert g == j, "not a pure braid"
        mg = magnus(W, 3, p)
        assert all(len(k) == 0 or len(k) == 3 for k in mg), "conjugator not in the third lower central term"
        M.append({k: v for k, v in mg.items() if len(k) == 3})
    return M


X12_23 = [1, 1, 2, 2, -1, -1, -2, -2]             # [A12, A23]
P4 = X12_23 + [3, 3] + [2, 2, 1, 1, -2, -2, -1, -1] + [-3, -3]        # [[A12, A23], A34]
X23_34 = [2, 2, 3, 3, -2, -2, -3, -3]             # [A23, A34]
P4B = X23_34 + [1, 1] + [3, 3, 2, 2, -3, -3, -2, -2] + [-1, -1]       # [[A23, A34], A12]
