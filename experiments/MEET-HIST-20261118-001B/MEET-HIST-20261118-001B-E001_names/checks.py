"""Gate checks for MEET-HIST-20261118-001B.

  ../../../.venv/bin/python -B checks.py
"""
import hashlib
import random
import sys
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

# G2. The unnamed reading equals the engine's state class (canon with no pairs) as a partition, on reached bases of six.
ok = True
for T in M.bracketings(0, 5)[:6]:
    for L in M.exact(6, T, 9, use_canon=False):
        a, b = {}, {}
        for (S, G) in L["dist"]:
            u = job.colored_canon(S, L["n"], [0] * L["n"])
            e = M.canon(S, L["n"], frozenset())[0]
            ok &= a.setdefault(u, e) == e and b.setdefault(e, u) == u
check("G2 the unnamed reading = the engine's state classes (six, six bracketings, to n0 + 3)", ok)

# G3. Each reading is invariant under the renamings it allows, and the readings are nested: N finer than NL and NO, both finer
# than U (checked on random reached bases).
rng = random.Random("MEET-HIST-G3")
ok = True
for trial in range(25):
    T = rng.choice(M.bracketings(0, 5))
    n0 = 6
    S, G, n = M.base(n0, T), M.pairs_of(T), n0
    for _ in range(rng.choice([1, 2, 3])):
        _, top = M.zero_cost_top(S, n, G)
        a0, a1, ks = rng.choice(top)
        S, G, n = M.apply(S, n, a0, a1), G | M.pairs_of(ks), n + 1
    r = job.readings(S, n, n0)
    line = list(range(n0)); rng.shuffle(line)
    new = list(range(n0, n)); rng.shuffle(new)
    perm_line = line + list(range(n0, n))
    perm_new = list(range(n0)) + new
    ok &= job.readings(job.relabel(S, perm_line), n, n0)["NO"] == r["NO"]
    ok &= job.readings(job.relabel(S, perm_new), n, n0)["NL"] == r["NL"]
    ok &= job.readings(job.relabel(S, perm_line), n, n0)["U"] == r["U"] == job.readings(job.relabel(S, perm_new), n, n0)["U"]
    mirror = [n0 - 1 - u if u < n0 else u for u in range(n)]
    ok &= job.readings(job.relabel(S, mirror), n, n0)["N"] == r["N"]
check("G3 readings invariant under their allowed renamings and the line's reversal (25 bases)", ok)

# G4. The referee's named shares at five (MEET-DIST-R1): line named 0.70, 0.69, 0.51 and all named 1.0 at k = 2, 3, 4.
sys.path.insert(0, str(HERE))
import math
from fractions import Fraction
from collections import defaultdict
rows = [job.run("x", {"n0": 5, "depth": 4, "knots": T}) for T in M.bracketings(0, 4)]


def share(rows, lev, r):
    w = Fraction(1, len(rows)); pk = defaultdict(Fraction); pc = defaultdict(Fraction); j = defaultdict(Fraction)
    for x in rows:
        pk[x["bare"]] += w
        for c, q in x["levels"][lev]["laws"][r].items():
            j[(x["bare"], c)] += w * Fraction(q); pc[c] += w * Fraction(q)
    H = -sum(float(p) * math.log2(float(p)) for p in pk.values())
    return sum(float(q) * math.log2(float(q) / (float(pk[k]) * float(pc[c]))) for (k, c), q in j.items()) / H


vals = [round(share(rows, k, "NL"), 2) for k in (2, 3, 4)] + [round(share(rows, k, "N"), 2) for k in (2, 3, 4)]
check("G4 the referee's named shares at five reproduce", vals == [0.70, 0.69, 0.51, 1.0, 1.0, 1.0], vals)

print("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS))
sys.exit(1 if FAILS else 0)
