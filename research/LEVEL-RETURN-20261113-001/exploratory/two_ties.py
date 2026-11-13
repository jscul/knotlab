"""Exploratory (proof attempt for #2's dying half; levels <= 12 only): which equalities among the special knots' addresses does the
rest of the pattern force at even levels?"""
import sys, itertools
import numpy as np
from pysat.solvers import Cadical195
sys.path.insert(0, 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels')
from certify import pattern
TWO = [3, [1, 0, 1], [0, 2, 2], [2, 1, 1], [[0, 8, 10], [1, 8, 12], [1, 9, 10]]]
for n in (4, 6, 8, 10, 12):
    K = pattern(TWO, n); X = np.arange(1 << n)
    par = np.array([bin(int(t)).count('1') & 1 for t in X]); V = par[K]
    bad = K[V.min(1) == V.max(1)]; rest = K[V.min(1) != V.max(1)]
    S = Cadical195()
    for a, b, c in rest.tolist(): S.add_clause([a + 1, b + 1, c + 1]); S.add_clause([-a - 1, -b - 1, -c - 1])
    addrs = sorted(set(bad.ravel().tolist()))
    forced = []
    for u, v in itertools.combinations(addrs, 2):
        # u != v possible?  (u xor v) as two solves with assumptions
        ne = S.solve(assumptions=[u + 1, -v - 1]) or S.solve(assumptions=[-u - 1, v + 1])
        eq = S.solve(assumptions=[u + 1, v + 1]) or S.solve(assumptions=[-u - 1, -v - 1])
        if not ne: forced.append((format(u, f'0{n}b'), format(v, f'0{n}b'), '='))
        if not eq: forced.append((format(u, f'0{n}b'), format(v, f'0{n}b'), '!='))
    print(n, 'bad knots', [[format(int(a), f'0{n}b') for a in k] for k in bad.tolist()], 'rest alive', S.solve(), 'forced', forced, flush=True)
