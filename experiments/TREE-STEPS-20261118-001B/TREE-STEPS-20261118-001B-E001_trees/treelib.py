"""Both cumulant distances on knot trees (TREE-STEPS-20261118-001B).

delta   (CUMULANT-DIST-20261118-001): min over sets S holding x and y with kappa_S != 0 of (|S| - 2) + max(0, -log_3 |kappa_S|).
delta_K (the irreducible-set distance): the same minimum over irreducible sets only, those with kappa_S != 0 and kappa_T = 0 for
every T with {x, y} contained in T strictly inside S (the cumulant form of the knot test's K2: the set is bound, and no smaller set
holding the pair is). If the pair's own correlation is nonzero, {x, y} is the only irreducible set and delta_K = tau."""
import itertools
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/CUMULANT-DIST-20261118-001B/CUMULANT-DIST-20261118-001B-E001_delta"))
import cumlib as L  # noqa: E402  (unchanged)


def both(B, x, y, smax):
    """(delta, delta_K) for the pair, sets up to smax; exact when smax >= steps apart + 2 on knot trees (delta, delta_K <= steps)."""
    others = [z for z in range(B.n) if z not in (x, y)]
    best, bestK = math.inf, math.inf
    nonzero = set()
    for m in range(2, smax + 1):
        if m - 2 >= best and m - 2 >= bestK:
            break
        for extra in itertools.combinations(others, m - 2):
            S = tuple(sorted((x, y) + extra))
            k = B.cumulant(S)
            if k == 0.0:
                continue
            v = (m - 2) + max(0.0, -math.log(abs(k), 3))
            best = min(best, v)
            irreducible = not any(tuple(sorted((x, y) + sub)) in nonzero
                                  for r in range(0, m - 2) for sub in itertools.combinations(extra, r))
            if irreducible:
                bestK = min(bestK, v)
            nonzero.add(S)
    return best, bestK


def random_tree(k, max_per, rng):
    """A random knot tree of k knots, each new knot attached at a distinction lying in fewer than max_per knots."""
    knots, n, deg = [(0, 1, 2)], 3, {0: 1, 1: 1, 2: 1}
    while len(knots) < k:
        v = rng.choice([u for u in range(n) if deg[u] < max_per])
        knots.append((v, n, n + 1))
        deg[v] += 1
        deg[n] = deg[n + 1] = 1
        n += 2
    return knots, n
