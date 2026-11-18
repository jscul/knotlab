"""Gate checks for MEET-ADDED-20261118-001B.

  ../../../.venv/bin/python -B checks.py
"""
import hashlib
import math
import random
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job
import melib as M

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" -- " + str(detail) if detail else ""), flush=True)
    if not ok:
        FAILS.append(name)


src = HERE.parents[2] / "experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/melib.py"
h = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
check("G1 melib.py is MEET-ORDERS's engine unchanged", h(HERE / "melib.py") == h(src))


def share(rows, lev, r):
    w = Fraction(1, len(rows)); pk = defaultdict(Fraction); pc = defaultdict(Fraction); j = defaultdict(Fraction)
    for x in rows:
        pk[x["bare"]] += w
        for c, q in x["levels"][lev]["laws"][r].items():
            j[(x["bare"], c)] += w * Fraction(q); pc[c] += w * Fraction(q)
    H = -sum(float(p) * math.log2(float(p)) for p in pk.values())
    return sum(float(q) * math.log2(float(q) / (float(pk[k]) * float(pc[c]))) for (k, c), q in j.items()) / H


rows5 = [job.run("x", {"n0": 5, "depth": 3, "knots": T}) for T in M.bracketings(0, 4)]
rows6 = [job.run("x", {"n0": 6, "depth": 3, "knots": T}) for T in M.bracketings(0, 5)]
p0 = [round(share(rows5, k, "P0"), 3) for k in range(4)] + [round(share(rows6, k, "P0"), 3) for k in (1, 2, 3)]
check("G2 the referee's preview: added pairs alone carry 0 at five (k <= 3) and 0, 0.009, 0.040 at six", p0 == [0, 0, 0, 0, 0, 0.009, 0.04], p0)
u5 = [round(share(rows5, k, "U"), 4) for k in (1, 2, 3)]
n5 = [round(share(rows5, k, "N"), 4) for k in (1, 2, 3)]
check("G3 the unnamed and all-named shares at five reproduce MEET-HIST", u5 == [0.6306, 0.6035, 0.3948] and n5 == [0.6306, 1.0, 1.0], (u5, n5))
check("G4 with the starting pairs the nesting is read at k = 0 (sanity ceiling)", round(share(rows5, 0, "SG"), 6) == 1.0)

# G5. Each arm is invariant under random renaming of a reached base.
rng = random.Random("MEET-ADDED-G5")
ok = True
for trial in range(15):
    T = rng.choice(M.bracketings(0, 5))
    n0 = 6
    lv = job.exact_with_knots(n0, T, 2)
    (S, K), _ = rng.choice(sorted(lv[2].items()))
    n = n0 + 2
    perm = list(range(n)); rng.shuffle(perm)
    S2 = tuple(sorted(sum(1 << perm[u] for u in range(n) if (s >> u) & 1) for s in S))
    K2 = frozenset(job.norm_knot((perm[a], perm[c], perm[b])) for (a, c, b) in K)
    G0 = M.pairs_of(T)
    G02 = frozenset((min(perm[a], perm[b]), max(perm[a], perm[b])) for a, b in G0)
    r1 = job.readings(S, K, n, n0, G0)
    r2 = job.readings(S2, K2, n, n0, G02)
    ok &= all(r1[a] == r2[a] for a in ("P0", "U", "P1", "T1", "K1", "SG"))
check("G5 every unnamed arm invariant under random renaming (15 bases)", ok)

print("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS))
sys.exit(1 if FAILS else 0)
