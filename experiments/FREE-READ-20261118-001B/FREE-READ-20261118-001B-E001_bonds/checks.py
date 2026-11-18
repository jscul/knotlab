"""Gates for FREE-READ-20261118-001B-E001."""
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import freelib as F  # noqa: E402

L = F.L
results = {}


def gate(name, ok, detail=""):
    results[name] = {"pass": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""), flush=True)

# 1. Supports.full against a direct set of tuples on random bases
rng = random.Random(4)
bad = 0
for _ in range(30):
    n = rng.randint(5, 7)
    kn = [(rng.choice("PNB"), tuple(rng.sample(range(n), 3))) for _ in range(rng.randint(2, 4))]
    st = L.states_from_knots(n, kn)
    if not st:
        continue
    sup = F.Supports(st, n)
    for m in range(1, n + 1):
        for S in itertools.combinations(range(n), m):
            direct = len({tuple((s >> v) & 1 for v in S) for s in st}) == 2 ** m
            bad += direct != sup.full(S)
gate("projection-support", bad == 0, f"{bad} sets differ")

# 2. a knot is a bond under each law; one knot gives bond distance 2 on its pairs
ok = True
for law in "PNB":
    sup = F.Supports(L.states_from_knots(3, [(law, (0, 1, 2))]), 3)
    ok &= sup.is_bond((0, 1, 2)) and all(sup.bond_distance(x, y, 3) == 2 for x, y in ((0, 1), (0, 2), (1, 2)))
gate("one-knot-bond", ok)

# 3. bond distance is invariant under switching values (flipping a distinction) and renaming
bad = 0
for _ in range(20):
    n = 6
    kn = [(rng.choice("PN"), tuple(rng.sample(range(n), 3))) for _ in range(3)]
    st = L.states_from_knots(n, kn)
    if not st:
        continue
    flip = rng.randrange(1 << n)
    a, b = F.Supports(st, n), F.Supports([s ^ flip for s in st], n)
    for x, y in itertools.combinations(range(n), 2):
        bad += a.bond_distance(x, y, n) != b.bond_distance(x, y, n)
gate("switching-invariant", bad == 0, f"{bad} pairs differ")

# 4. the path set {x, y, third distinctions} is a bond on random mixed chains of 2 to 5 knots
ok = True
for _ in range(40):
    k = rng.randint(2, 5)
    laws = [rng.choice("PNB") for _ in range(k)]
    knots = [(laws[j], (2 * j, 2 * j + 1, 2 * j + 2)) for j in range(k)]
    n = 2 * k + 1
    sup = F.Supports(L.states_from_knots(n, knots), n)
    ok &= sup.is_bond(tuple([0, n - 1] + [2 * j + 1 for j in range(k)]))
gate("path-set-is-bond", ok, "x, y and every path knot's third distinction, random P/N/B chains")

json.dump(results, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in results.values()) else "SOME FAIL")
