"""Top-level check for the decision of NEXT-DIRECTION-SCAN-20261031-001: is lane B's depth-two failure an artifact of the y-basis?

A matchgate algorithm after a holographic transformation T needs the transformed point signature [1,0,1,0] (by T on each leg) and line
signature [1,0,x^2,0] (by T^-T) to be matchgates, so in particular parity-definite. Both are sums of two cubes:
[1,0,1,0] = ((1,1)^3 + (1,-1)^3)/2 and [1,0,x^2,0] = ((1,x)^3 + (1,-x)^3)/2.
  1. For a symbolic coupling x, the only invertible T keeping both parity-definite are diagonal or antidiagonal.
  2. Under those, the matchgate identity of any 4-ary signature is multiplied by a nonzero constant, so lane B's verdicts do not change.
Run: .venv/bin/python -B basis_check.py"""
import itertools
import json

import sympy as sp

a, b, c, d, x, lam = sp.symbols('a b c d x lambda')


def cube_sum(u, v):
    return [sp.expand(u[0] ** (3 - k) * u[1] ** k + v[0] ** (3 - k) * v[1] ** k) for k in range(4)]


P = cube_sum((a + b, c + d), (a - b, c - d))                       # T (1, +-1)
L = cube_sum((d - c * x, -b + a * x), (d + c * x, -b - a * x))     # T^-T (1, +-x), up to the factor 1/det
parity = {"even": lambda f: [f[1], f[3]], "odd": lambda f: [f[0], f[2]]}
out = {}
for pp, lp in itertools.product(parity, parity):
    sols = sp.solve(parity[pp](P) + parity[lp](L), [a, b, c, d], dict=True)
    out[f"points {pp}, lines {lp}"] = [str(s) for s in sols if sp.simplify((a * d - b * c).subs(s)) != 0]
ok1 = out == {"points even, lines even": [str({b: 0, c: 0})], "points even, lines odd": [], "points odd, lines even": [],
              "points odd, lines odd": [str({a: 0, d: 0})]}

W = {y: sp.Symbol('w' + ''.join(map(str, y))) for y in itertools.product((0, 1), repeat=4)}


def mgi(f):
    return sp.expand(f[(0, 0, 0, 0)] * f[(1, 1, 1, 1)] - f[(1, 1, 0, 0)] * f[(0, 0, 1, 1)] + f[(1, 0, 1, 0)] * f[(0, 1, 0, 1)]
                     - f[(1, 0, 0, 1)] * f[(0, 1, 1, 0)])


diag = {y: lam ** sum(y) * W[y] for y in W}
anti = {y: lam ** (4 - sum(y)) * W[tuple(1 - t for t in y)] for y in W}
ok2 = sp.expand(mgi(diag) - lam ** 4 * mgi(W)) == 0 and sp.expand(mgi(anti) - lam ** 4 * mgi(W)) == 0
res = {"1 parity-definite bases (invertible T = [[a, b], [c, d]])": out, "1 only diagonal or antidiagonal": ok1,
       "2 MGI(T W) = lambda^4 MGI(W) for T = diag(1, lambda) and its antidiagonal twin": ok2}
print(json.dumps(res, indent=1))
print("ALL OK" if ok1 and ok2 else "FAIL")
