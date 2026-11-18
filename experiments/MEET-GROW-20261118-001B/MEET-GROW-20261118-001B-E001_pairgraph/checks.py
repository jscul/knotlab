"""Gate checks for MEET-GROW-20261118-001B (run before the freeze; all must pass).

  ../../../.venv/bin/python -B checks.py
"""
import hashlib
import itertools
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
check("G1 melib.py is MEET-ORDERS's engine unchanged (its 15 gate checks passed there)", h(HERE / "melib.py") == h(src))


def carried(a, b):
    return any(all(La["per_alpha"][k] == Lb["per_alpha"][0] for La, Lb in zip(a["levels"], b["levels"]))
               for k in range(len(a["levels"][0]["per_alpha"])))


# G2. Positive control: a presentation and its mirror image (an isomorphism of everything) are carried, with equal renaming
# digests and equal two-order chances at every level.
ok = True
for n0 in (5, 6):
    for T in M.bracketings(0, n0 - 1):
        a = job.run("x", {"n0": n0, "depth": 2, "knots": T})
        b = job.run("x", {"n0": n0, "depth": 2, "knots": M.mirror(T, n0 - 1)})
        ok &= carried(a, b) and carried(b, a)
        ok &= all(La["renaming_digest"] == Lb["renaming_digest"] and La["two"] == Lb["two"] for La, Lb in zip(a["levels"], b["levels"]))
check("G2 every presentation of 5 and 6 is carried onto its mirror image (depth 2)", ok)

# G3. Negative control: presentations with different meeting patterns are never carried (different canonical patterns), and a
# perturbed distribution (one probability moved) breaks the digest.
r6 = [job.run("x", {"n0": 6, "depth": 2, "knots": T}) for T in job.reps(6)]
pats = defaultdict(list)
for r in r6:
    pats[r["pattern"]].append(r)
check("G3a six has three meeting patterns among its seven presentations up to mirror", len(pats) == 3, sorted(len(v) for v in pats.values()))
d1 = job.digest([((1, 2), "1/2"), ((1, 3), "1/2")])
d2 = job.digest([((1, 2), "1/3"), ((1, 3), "2/3")])
check("G3b the digest separates distributions that differ in one probability", d1 != d2)

# G4. The digest comparison agrees with a direct comparison of the labelled distributions through every meeting-pattern
# isomorphism (brute force over all bijections), on the line of five to depth 3.
def labelled(n0, T, d):
    out = []
    for L in M.exact(n0, T, n0 + d, use_canon=False):
        dist = defaultdict(Fraction)
        for (S, G), q in L["dist"].items():
            dist[G] += q
        out.append(dict(dist))
    return out


Ts = M.bracketings(0, 4)
agree = 0
pairs = 0
for A, B in itertools.combinations(Ts, 2):
    isos = [p for p in itertools.permutations(range(5))
            if {frozenset(p[v] for v in k) for k in A} == {frozenset(k) for k in B}]
    la, lb = labelled(5, A, 3), labelled(5, B, 3)
    direct = any(all({frozenset((min(f(u), f(v)), max(f(u), f(v))) for u, v in G): q
                      for G, q in la[d].items()} == lb[d] for d in range(4))
                 for p in isos for f in [lambda x, p=p: p[x] if x < 5 else x])
    via = carried(job.run("x", {"n0": 5, "depth": 3, "knots": A}), job.run("x", {"n0": 5, "depth": 3, "knots": B}))
    agree += direct == via
    pairs += 1
check("G4 digest comparison = direct comparison on all 10 pairs of five's presentations (depth 3)", agree == pairs, f"{agree}/{pairs}")

# G5. The renaming digest is invariant under a random renaming of a reached pair graph.
rng = random.Random("MEET-GROW-G5")
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
    G2 = frozenset((min(perm[u], perm[v]), max(perm[u], perm[v])) for u, v in G)
    ok &= M.canon((), n, G)[1] == M.canon((), n, G2)[1]
check("G5 renaming class of a pair graph invariant under random renaming (20 graphs)", ok)

print("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS))
sys.exit(1 if FAILS else 0)
