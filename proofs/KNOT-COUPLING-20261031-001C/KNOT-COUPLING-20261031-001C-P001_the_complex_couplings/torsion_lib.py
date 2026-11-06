"""The complex couplings (KNOT-COUPLING-20261031-001C): torsion points on the curve of two atom ratios.

An atom is bad at lam when its ratio rho(lam) is 0, infinite or a root of unity. The pair (rho_F(lam), rho_S(lam)) runs over a curve
C in the plane; where both atoms are bad with finite nonzero ratios, (rho_F, rho_S) is a torsion point of C. Beukers and Smyth (2002,
Lemma 1): a torsion point of f(X, Y) = 0, f over Q, is also a zero of one of f(-X, Y), f(X, -Y), f(-X, -Y), f(+-X^2, +-Y^2). This module
computes f, the seven resultants, their cyclotomic factors (filtered at roots of unity in finite fields F_p with p = 1 mod m, then
confirmed by exact division), the torsion points, and the zeros and poles of each ratio."""
from math import gcd

import sympy as sp

lam, X, Y = sp.symbols('lam X Y')


def ratio_polys(MH, Me):
    """(numerator, denominator) of rho = (M_H - M_He)/(M_H + M_He) in lowest terms, as sympy Polys in lam (coefficient lists high first)"""
    n, d = sp.cancel((MH - Me) / (MH + Me)).as_numer_denom()
    return sp.Poly(n, lam), sp.Poly(d, lam)


def implicit_curve(nF, dF, nS, dS):
    return sp.Poly(sp.resultant((X * dF - nF).as_expr(), (Y * dS - nS).as_expr(), lam), X, Y)


def variants(f):
    fe = f.as_expr()
    out = {"f(-X, Y)": fe.subs(X, -X), "f(X, -Y)": fe.subs(Y, -Y), "f(-X, -Y)": fe.subs({X: -X, Y: -Y}, simultaneous=True)}
    for sx in (1, -1):
        for sy in (1, -1):
            out[f"f({'' if sx == 1 else '-'}X^2, {'' if sy == 1 else '-'}Y^2)"] = fe.subs({X: sx * X ** 2, Y: sy * Y ** 2}, simultaneous=True)
    return {k: sp.expand(v) for k, v in out.items()}


def totient(m):
    return sp.totient(m)


def ms_with_totient_at_most(D):
    """every m with phi(m) <= D: since phi(m) >= sqrt(m/2) for every m, it suffices to sieve m <= 2 D^2"""
    top = 2 * D * D + 2
    phi = list(range(top + 1))
    for i in range(2, top + 1):
        if phi[i] == i:
            for j in range(i, top + 1, i):
                phi[j] -= phi[j] // i
    return [m for m in range(1, top + 1) if phi[m] <= D]


def prime_1_mod(m, start=10 ** 6):
    k = start // m + 1
    while True:
        p = k * m + 1
        if sp.isprime(p):
            return p
        k += 1


def root_of_order(m, p):
    """an element of exact multiplicative order m in F_p (p = 1 mod m)"""
    fac = sp.factorint(m)
    g = 2
    while True:
        w = pow(g, (p - 1) // m, p)
        if all(pow(w, m // q, p) != 1 for q in fac):
            return w
        g += 1


def cyclotomic_factors(R, var):
    """the m with Phi_m | R (R a Poly over ZZ in var): filter by R(w) = 0 at a primitive m-th root w in two fields F_p, confirm exactly"""
    coeffs = [int(c) for c in R.all_coeffs()]
    D = len(coeffs) - 1
    found = []
    for m in ms_with_totient_at_most(D):
        ok = True
        for start in (10 ** 6, 10 ** 7):
            p = prime_1_mod(m, start)
            w = root_of_order(m, p)
            v = 0
            for c in coeffs:
                v = (v * w + c) % p
            if v:
                ok = False
                break
        if ok and sp.rem(R, sp.Poly(sp.cyclotomic_poly(m, var), var)).is_zero:
            found.append(m)
    return found


def torsion_points_numeric(f, mx, my, dps=60):
    """pairs (a/mx, b/my) in lowest terms with f(e^{2 pi i a/mx}, e^{2 pi i b/my}) = 0, found numerically and confirmed exactly"""
    import mpmath
    mpmath.mp.dps = dps
    fe = f.as_expr()
    lf = sp.lambdify((X, Y), fe, "mpmath")
    out = []
    for a in range(mx):
        if gcd(a, mx) != 1:
            continue
        for b in range(my):
            if gcd(b, my) != 1:
                continue
            zx = mpmath.exp(2j * mpmath.pi * a / mx)
            zy = mpmath.exp(2j * mpmath.pi * b / my)
            if abs(lf(zx, zy)) < mpmath.mpf(10) ** (-(dps // 2)):
                # exact: f(zeta^a, zeta^b) reduces to 0 modulo the cyclotomic polynomial of the common order
                N = mx * my // gcd(mx, my)
                z = sp.Symbol('z')
                val = sp.rem(sp.Poly(sp.expand(fe.subs({X: z ** (a * N // mx), Y: z ** (b * N // my)}, simultaneous=True)), z),
                             sp.Poly(sp.cyclotomic_poly(N, z), z))
                out.append(((a, mx), (b, my), val.is_zero))
    return out
