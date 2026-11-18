"""Referee R1 for CUMULANT-DIST-20261118-001: the hub mechanism behind the study's Block (D6), checked independently.

  ../../../.venv/bin/python -B referee_hub.py > referee_hub.txt      (from this directory)

1. The cumulants of a fair coin from log cosh t (sympy): kappa_2, kappa_4, ... = 1, -2, 16, -272, 7936, ... (the tangent numbers
   with signs); for each even N + 2, log_3 |kappa_(N+2)| - 2N, which must be positive for the hub to shortcut.
2. The identity kappa_S = kappa_(N+2)(coin) (-1/3)^(N+k) on actual bases: a path of k not-all-equal knots from x to y and N
   not-all-equal knots hung on x, S = {x, y} and one child of each hung knot, by the referee's partition-formula cumulant.
"""
import math, itertools, json, sys
from fractions import Fraction
import sympy as sp
sys.path.insert(0, ".")
import referee_cumulant as RCU
t = sp.symbols("t")
ser = sp.series(sp.log(sp.cosh(t)), t, 0, 42).removeO()
kap = {m: sp.factorial(m) * ser.coeff(t, m) for m in range(2, 42, 2)}          # cumulants of a uniform +-1 spin
print({m: int(v) for m, v in kap.items() if m <= 12})
for m in range(2, 42, 2):
    N = m - 2
    L = math.log(abs(int(kap[m])), 3)
    if N >= 24:
        print("N", N, "log3|kappa_{N+2}|", round(L, 4), "minus 2N", round(L - 2 * N, 4))
# the identity on actual bases: path of k NAE knots from x = 0 to y, N NAE knots hung on x; S = {x, y} + one child per hung knot
for N, k in ((2, 1), (4, 1), (2, 2), (4, 2), (6, 1)):
    knots, n = [], 1
    for i in range(k):
        knots.append(("N", (n - 1, n, n + 1)))
        n += 2
    y = n - 1
    kids = []
    for i in range(N):
        knots.append(("N", (0, n, n + 1)))
        kids.append(n)
        n += 2
    B = RCU.Base(RCU.states(n, knots), n)
    S = tuple([0, y] + kids)
    print("N", N, "k", k, "n", n, "kappa_S", B.k(S), "predicted", float(kap[N + 2]) * (-1 / 3) ** (N + k))
