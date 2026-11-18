"""Gate checks for MEET-DIST-20261118-001B (run before the freeze; all must pass).

  ../../../.venv/bin/python -B checks.py
"""
import hashlib
import random
import sys
from collections import defaultdict
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

# G2. DISTANCE-ORDER 3(a) on these bases: classes of disagreement tables (with N) are exactly classes of states.
ok = True
detail = []
for n0, d in ((5, 3), (6, 3)):
    for T, w in job.reps(n0):
        for L in M.exact(n0, T, n0 + d):
            by_table = defaultdict(set)
            by_state = defaultdict(set)
            for (S, G) in L["dist"]:
                sc = M.canon(S, L["n"], frozenset())[0]
                tc = job.table_class(S, L["n"])
                by_table[tc].add(sc)
                by_state[sc].add(tc)
            ok &= all(len(v) == 1 for v in by_table.values()) and all(len(v) == 1 for v in by_state.values())
check("G2 table classes = state classes on every reached base of five and six to n0 + 3", ok)

# G3. The table class is invariant under random renaming.
rng = random.Random("MEET-DIST-G3")
ok = True
for trial in range(20):
    T = rng.choice(M.bracketings(0, 5))
    S, G, n = M.base(6, T), M.pairs_of(T), 6
    for _ in range(2):
        _, top = M.zero_cost_top(S, n, G)
        a0, a1, ks = rng.choice(top)
        S, G, n = M.apply(S, n, a0, a1), G | M.pairs_of(ks), n + 1
    perm = list(range(n))
    rng.shuffle(perm)
    S2 = tuple(sorted(sum(1 << perm[u] for u in range(n) if (s >> u) & 1) for s in S))
    ok &= job.table_class(S, n) == job.table_class(S2, n)
check("G3 table class invariant under random renaming (20 bases)", ok)

# G4. At k = 0 all presentations have one table law (the line), and at k = 1 the hand count for five holds (prior uniform over the
# five labelled presentations: end and next to an end count twice, the middle once): bare bracketing named
# with chance 13/15, presentation 11/15.
sys.path.insert(0, str(HERE))
import merge
from fractions import Fraction
rows = [job.run("x", {"n0": 5, "depth": 1, "knots": T, "mirror_weight": w}) for T, w in job.reps(5)]
ok = len({tuple(sorted(r["levels"][0]["table_law"].items())) for r in rows}) == 1
i_bare = merge.identification(rows, 1, lambda r: r["bare"])
i_pres = merge.identification(rows, 1, lambda r: r["ordered"])
check("G4 k = 0 one law; k = 1 identification 13/15 (bare) and 11/15 (presentation) at five", ok and i_bare == Fraction(13, 15) and i_pres == Fraction(11, 15), (i_bare, i_pres))

print("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS))
sys.exit(1 if FAILS else 0)
