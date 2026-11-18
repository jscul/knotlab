"""Gates for TREE-STEPS-20261118-001B-E001."""
import itertools
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import treelib as T  # noqa: E402

L = T.L
results = {}


def gate(name, ok, detail=""):
    results[name] = {"pass": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""), flush=True)

# 1. both() agrees with CUMULANT-DIST's delta (unchanged) on random small bases, and delta_K >= delta
rng = random.Random(11)
bad = badorder = 0
for _ in range(40):
    n = rng.randint(5, 7)
    triples = list(itertools.combinations(range(n), 3))
    kn = [(rng.choice("PNB"), tuple(rng.sample(t, 3))) for t in rng.sample(triples, rng.randint(2, 5))]
    st = L.states_from_knots(n, kn)
    if not st:
        continue
    B = L.Base(st, n)
    for x, y in itertools.combinations(range(n), 2):
        v, vK = T.both(B, x, y, n)
        ref = B.delta(x, y)[0]
        bad += not ((v == ref == math.inf) or abs(v - ref) < 1e-9)
        badorder += vK < v - 1e-9
gate("both-delta-equals-cumlib", bad == 0, f"{bad} pairs differ")
gate("deltaK-at-least-delta", badorder == 0, f"{badorder} pairs with delta_K < delta")

# 2. irreducibility by brute force on random small bases
bad = 0
for _ in range(30):
    n = rng.randint(5, 6)
    triples = list(itertools.combinations(range(n), 3))
    kn = [(rng.choice("PN"), tuple(rng.sample(t, 3))) for t in rng.sample(triples, rng.randint(2, 4))]
    st = L.states_from_knots(n, kn)
    if not st:
        continue
    B = L.Base(st, n)
    for x, y in itertools.combinations(range(n), 2):
        best = math.inf
        others = [z for z in range(n) if z not in (x, y)]
        for m in range(2, n + 1):
            for extra in itertools.combinations(others, m - 2):
                S = (x, y) + extra
                k = B.cumulant(S)
                if k == 0.0:
                    continue
                if all(B.cumulant(tuple((x, y) + sub)) == 0.0 for r in range(0, m - 2) for sub in itertools.combinations(extra, r)):
                    best = min(best, (m - 2) + max(0.0, -math.log(abs(k), 3)))
        vK = T.both(B, x, y, n)[1]
        bad += not ((vK == best == math.inf) or abs(vK - best) < 1e-9)
gate("deltaK-vs-brute-force", bad == 0, f"{bad} pairs differ")

# 3. the hub identity: kappa = kappa_{2D+2}(coin) (-1/3)^(2D+k) for NAE hubs with both children, D <= 3
coin = {2: 1, 4: -2, 6: 16, 8: -272}
ok = True
for D, k in ((1, 1), (2, 1), (2, 2), (3, 1)):
    knots, n, ch = [], 1, []
    for i in range(D):
        knots.append(("N", (0, n, n + 1)))
        ch += [n, n + 1]
        n += 2
    prev = 0
    for j in range(k):
        knots.append(("N", (prev, n, n + 1)))
        prev = n + 1
        n += 2
    B = L.Base(L.states_from_knots(n, knots), n)
    ok &= abs(B.cumulant(tuple(sorted([0, prev] + ch))) - coin[2 * D + 2] * (-1 / 3) ** (2 * D + k)) < 1e-12
gate("hub-identity", ok)

# 4. the tangent numbers and the threshold: least even N with log3 |kappa_{N+2}(coin)| > 2N is 32
from fractions import Fraction
def coin_cumulants(m):
    """Exact cumulants of a fair +-1 coin to order m, from moments (1 at even orders) by the partition recursion on one variable."""
    from math import comb
    mom = [Fraction(1) if j % 2 == 0 else Fraction(0) for j in range(m + 1)]
    kap = [Fraction(0)] * (m + 1)
    for n in range(1, m + 1):
        kap[n] = mom[n] - sum(comb(n - 1, j - 1) * kap[j] * mom[n - j] for j in range(1, n))
    return kap
kap = coin_cumulants(40)
first = next(N for N in range(2, 39, 2) if math.log(abs(kap[N + 2]), 3) > 2 * N)
gate("hub-threshold-32", first == 32 and [abs(int(kap[j])) for j in (2, 4, 6, 8, 10)] == [1, 2, 16, 272, 7936],
     f"first N = {first}, log3|kappa_34| = {math.log(abs(kap[34]), 3):.4f}")

json.dump(results, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in results.values()) else "SOME FAIL")
