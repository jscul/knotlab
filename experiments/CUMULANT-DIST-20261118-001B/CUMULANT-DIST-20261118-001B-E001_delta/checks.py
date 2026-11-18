"""Gates for CUMULANT-DIST-20261118-001B-E001 (run before the freeze)."""
import itertools
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cumlib as L  # noqa: E402

results = {}


def gate(name, ok, detail=""):
    results[name] = {"pass": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""), flush=True)


rng = random.Random(3)


def random_base(n):
    triples = list(itertools.combinations(range(n), 3))
    kn = [(rng.choice("PNB"), tuple(rng.sample(t, 3))) for t in rng.sample(triples, rng.randint(2, 5))]
    st = L.states_from_knots(n, kn)
    return (st, kn) if st else random_base(n)


def part_cum(B, S):
    tot = 0.0
    for p in L.partitions_of_size(len(S)):
        prod = 1.0
        for b in p:
            prod *= B.moment(tuple(S[i] for i in b))
        k = len(p)
        tot += (-1) ** (k - 1) * math.factorial(k - 1) * prod
    return tot

# 1. the cumulant recursion equals the partition formula
dev = 0.0
for _ in range(30):
    n = rng.randint(5, 7)
    st, _ = random_base(n)
    B = L.Base(st, n)
    for m in range(1, n + 1):
        for S in itertools.combinations(range(n), m):
            dev = max(dev, abs(B.cumulant(S) - part_cum(B, S)))
gate("cumulant-recursion-vs-partitions", dev < 1e-12, f"max {dev:.1e} over 30 random bases, every set")

# 2. the pruned search equals the full search; 3. invariance under renaming and under switching values
bad_prune = bad_rename = bad_switch = 0
for _ in range(40):
    n = rng.randint(5, 7)
    st, _ = random_base(n)
    B = L.Base(st, n)
    perm = list(range(n)); rng.shuffle(perm)
    st_r = sorted(sum(((s >> i) & 1) << perm[i] for i in range(n)) for s in st)
    flip = rng.randrange(1, 1 << n)
    st_s = sorted(s ^ flip for s in st)
    Br, Bs = L.Base(st_r, n), L.Base(st_s, n)
    for x, y in itertools.combinations(range(n), 2):
        v = B.delta(x, y)[0]
        full = math.inf
        for m in range(2, n + 1):
            for extra in itertools.combinations([z for z in range(n) if z not in (x, y)], m - 2):
                k = B.cumulant(tuple(sorted((x, y) + extra)))
                if k != 0.0:
                    full = min(full, (m - 2) + max(0.0, -math.log(abs(k), 3)))
        bad_prune += not ((v == full == math.inf) or abs(v - full) < 1e-9)
        vr = Br.delta(perm[x], perm[y])[0]
        bad_rename += not ((v == vr == math.inf) or abs(v - vr) < 1e-9)
        vs = Bs.delta(x, y)[0]
        bad_switch += not ((v == vs == math.inf) or abs(v - vs) < 1e-9)
gate("pruned-search-exact", bad_prune == 0, f"{bad_prune} pairs differ")
gate("invariant-under-renaming", bad_rename == 0, f"{bad_rename} pairs differ")
gate("invariant-under-switching-values", bad_switch == 0, f"{bad_switch} pairs differ")

# 4. circuits: the least circuit through a pair against brute force over sets whose states restrict to a parity knot
bad = 0
for _ in range(40):
    n = rng.randint(5, 7)
    triples = list(itertools.combinations(range(n), 3))
    kn = [("P", t) for t in rng.sample(triples, rng.randint(2, 5))]
    words = L.dual_codewords(kn, n)
    st = L.states_from_knots(n, kn)
    for x, y in itertools.combinations(range(n), 2):
        brute = math.inf
        for m in range(2, n + 1):
            for extra in itertools.combinations([z for z in range(n) if z not in (x, y)], m - 2):
                S = (x, y) + extra
                proj = {tuple((s >> v) & 1 for v in S) for s in st}
                whole = len(proj) < 2 ** m
                free = all(len({tuple((s >> v) & 1 for v in T) for s in st}) == 2 ** (m - 1)
                           for T in itertools.combinations(S, m - 1))
                if whole and free:
                    brute = min(brute, m)
        bad += brute != L.min_circuit_through(words, x, y)
gate("circuits-are-the-knot-sets", bad == 0, f"{bad} pairs differ (circuit = smallest set whose states form a knot)")

# 5. one knot = distance one, under each law
ok = True
for law in "PNB":
    B = L.Base(L.states_from_knots(3, [(law, (0, 1, 2))]), 3)
    ok &= all(abs(B.delta(x, y)[0] - 1) < 1e-12 for x, y in ((0, 1), (0, 2), (1, 2)))
gate("one-knot-distance-one", ok, "parity, not-all-equal and betweenness knots")

# 6. a mutant (moments in place of cumulants) must shortcut on a not-all-equal chain where the cumulant distance does not
kn = [("N", (2 * i, 2 * i + 1, 2 * i + 2)) for i in range(5)]
B = L.Base(L.states_from_knots(11, kn), 11)
mom = min((len(S) - 2) + max(0.0, -math.log(abs(B.moment(S)), 3)) for r in (2, 4) for S in itertools.combinations(range(11), r)
          if 0 in S and 10 in S and B.moment(S) != 0)
cum = B.delta(0, 10)[0]
gate("mutant-moments-shortcut", mom < cum - 0.5, f"moments give {mom:.3f}, cumulants {cum:.3f} (steps apart 5)")

json.dump(results, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in results.values()) else "SOME FAIL")
