"""Exploratory: is #2's pattern without the two special knots rigid at even levels (only the parity state and its complement), and
does unit propagation from one fixed value determine every address?"""
import sys
import numpy as np
from pysat.solvers import Cadical195
sys.path.insert(0, 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels')
from certify import pattern
TWO = [3, [1, 0, 1], [0, 2, 2], [2, 1, 1], [[0, 8, 10], [1, 8, 12], [1, 9, 10]]]
for n in (4, 5, 6, 7, 8, 10, 12):
    K = pattern(TWO, n); X = np.arange(1 << n)
    par = np.array([bin(int(t)).count('1') & 1 for t in X]); V = par[K]
    rest = K[V.min(1) != V.max(1)] if n % 2 == 0 else K
    used = sorted(set(rest.ravel().tolist()))
    S = Cadical195()
    for a, b, c in rest.tolist(): S.add_clause([a + 1, b + 1, c + 1]); S.add_clause([-a - 1, -b - 1, -c - 1])
    m0 = used[0]; S.add_clause([m0 + 1])
    count = 0; models = []
    while S.solve() and count < 5:
        mdl = S.get_model(); count += 1
        S.add_clause([-l for l in mdl if abs(l) - 1 in set(used)])
        models.append(mdl)
    # unit propagation from the fixed value
    val = {m0: 1}; changed = True
    clauses = [[a + 1, b + 1, c + 1] for a, b, c in rest.tolist()] + [[-a - 1, -b - 1, -c - 1] for a, b, c in rest.tolist()]
    while changed:
        changed = False
        for cl in clauses:
            unass = [l for l in cl if abs(l) - 1 not in val]
            sat = any((l > 0) == (val[abs(l) - 1] == 1) for l in cl if abs(l) - 1 in val)
            if not sat and len(unass) == 1:
                l = unass[0]; val[abs(l) - 1] = 1 if l > 0 else 0; changed = True
    print(n, 'knots', len(rest), 'addresses used', len(used), 'states (fixed one value, up to 5)', count,
          'unit propagation fixes', len(val), 'of', len(used), flush=True)
