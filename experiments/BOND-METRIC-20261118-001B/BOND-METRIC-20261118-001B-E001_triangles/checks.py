"""Gates for BOND-METRIC-20261118-001B-E001.   .venv/bin/python -B checks.py   (writes checks_output.json)"""
import itertools
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments/FREE-READ-20261118-001B/FREE-READ-20261118-001B-E001_bonds"))
sys.path.insert(0, str(ROOT / "research/FREE-READ-20261118-001/referee-R1"))
import metriclib as M  # noqa: E402
import freelib as F  # noqa: E402  (FREE-READ's bond search, a separate implementation)
import referee_free as RF  # noqa: E402  (the FREE-READ referee's bond search and state builder)

out = {}


def gate(name, ok, detail=""):
    out[name] = {"pass": bool(ok), "detail": detail}
    print("PASS" if ok else "FAIL", name, detail)


# G1: bond matrix against FREE-READ's Supports on random mixed bases
rng = random.Random(1)
bad = 0
for _ in range(150):
    n = rng.randint(4, 7)
    ts = sorted({tuple(sorted(rng.sample(range(n), 3))) for _ in range(rng.randint(2, 5))})
    knots = [(rng.choice(M.k2_laws()), t) for t in ts]
    st = M.states(n, knots)
    if len(st) == 0:
        continue
    D = M.bond_matrix(n, st)
    sup = F.Supports(list(st), n)
    for x, y in itertools.combinations(range(n), 2):
        b = sup.bond_distance(x, y, n)
        bad += (math.inf if b is None else b) != D[x][y]
gate("bond-matrix-vs-freelib", bad == 0, f"{bad} pairs differ")

# G2: the exploration's exhibits, read with the referee's code
ex = [(4, [("N", (0, 1, 2)), ("N", (0, 1, 3))], (2, 0, 3), (2, 2, None)),
      (6, [("P", (0, 1, 2)), ("P", (0, 3, 4)), ("N", (1, 3, 5)), ("N", (2, 4, 5))], (0, 1, 5), (2, 2, None)),
      (8, [("N", t) for t in [(0, 4, 6), (1, 2, 7), (0, 3, 7), (2, 5, 6), (1, 3, 5)]], (1, 0, 4), (3, 2, None)),
      (10, [("N", t) for t in [(1, 6, 7), (4, 5, 7), (2, 4, 5), (0, 7, 9), (0, 6, 9), (6, 8, 9), (0, 3, 7), (1, 4, 5), (5, 8, 9)]],
       (2, 4, 7), (2, 2, 5))]
ok = True
for n, knots, (x, y, z), want in ex:
    sup = RF.Sup(RF.RC.states(n, knots), n)
    got = (sup.b(x, y), sup.b(y, z), sup.b(x, z))
    ok &= got == want
    lawmap = {"N": M.NAE, "P": M.P0}
    D = M.bond_matrix(n, M.states(n, [(lawmap[l], t) for l, t in knots]))
    ok &= tuple(None if D[a][b] == math.inf else D[a][b] for a, b in ((x, y), (y, z), (x, z))) == want
gate("exhibits", ok, "two NAE knots sharing two; mixed Pasch; NAE meeting once on 8; NAE finite failure on 10")

# G2b: the advisor's exhibits for R6 and R5, and the twisted languages by switching distinctions (bonds are invariant under
# switching; each switched knot is a copy of the twisted law)
def lmat(n, knots):
    return M.bond_matrix(n, M.states(n, knots))


def switched(knots, flip):
    return [(M.switch(R, sum(1 << i for i, v in enumerate(t) if v in flip)), t) for R, t in knots]


a, b, f1, g1, c, f2, g2, d = range(8)
r5 = [(M.R5, t) for t in [(a, b, f1), (a, b, g1), (f1, g1, c), (a, b, f2), (a, b, g2), (f2, g2, d)]]
cases_ = {
    "NAE": (4, [(M.NAE, (0, 1, 2)), (M.NAE, (0, 1, 3))], set(), (2, 0, 3)),
    "betweenness": (4, [(M.NAE, (0, 1, 2)), (M.NAE, (0, 1, 3))], {2, 3}, (2, 0, 3)),
    "clause": (4, [(M.CLAUSE, (0, 1, 2)), (M.CLAUSE, (0, 1, 3))], set(), (2, 0, 3)),
    "clause-twisted": (4, [(M.CLAUSE, (0, 1, 2)), (M.CLAUSE, (0, 1, 3))], {2, 3}, (2, 0, 3)),
    "R6": (4, [(M.R6, (1, 2, 0)), (M.R6, (1, 2, 3))], set(), (0, 1, 3)),
    "R6-twisted": (4, [(M.R6, (1, 2, 0)), (M.R6, (1, 2, 3))], {2}, (0, 1, 3)),
    "R5": (8, r5, set(), (c, a, d)),
    "R5-twisted": (8, r5, {a, c, d}, (c, a, d)),
}
ok, detail = True, []
for name, (n, knots, flip, (x, y, z)) in cases_.items():
    kk = switched(knots, flip)
    langs = {M.language(R) for R, _ in kk}
    Dm = lmat(n, kk)
    good = langs == {M.language(M.LANGUAGES[name])} and Dm[x][z] == math.inf and Dm[x][y] == 2 and Dm[y][z] == 2
    ok &= good
    detail.append(f"{name}:{'ok' if good else 'NO'}")
Dm = lmat(5, [(M.R6, (1, 2, 0)), (M.R6, (3, 4, 0))])
ok &= Dm[1][0] == 2 and Dm[0][3] == 2 and Dm[1][3] == math.inf
gate("language-exhibits", ok, ", ".join(detail) + "; R6 meeting once on 5")
gate("languages", len({M.language(R) for R in M.k2_laws()}) == 9 and len({M.language(R) for R in M.LANGUAGES.values()}) == 9,
     "34 laws in 9 languages, one representative each")

# G3: on parity bases, bonds are the minimal supports of sums of the checks (dual codewords)
def dual_supports(n, knots):
    rows = []
    for R, t in knots:
        rows.append(sum(1 << v for v in t))
    words = set()
    for r in range(1, len(rows) + 1):
        for c in itertools.combinations(rows, r):
            w = 0
            for x in c:
                w ^= x
            if w:
                words.add(w)
    return sorted(w for w in words if not any(u != w and u & w == u for u in words))


bad = 0
for _ in range(100):
    n = rng.randint(4, 8)
    ts = sorted({tuple(sorted(rng.sample(range(n), 3))) for _ in range(rng.randint(2, 6))})
    knots = [(rng.choice((M.P0, M.P1)), t) for t in ts]
    st = M.states(n, knots)
    if len(st) == 0:
        continue
    bad += sorted(M.bonds(n, M.free_table(n, st))) != dual_supports(n, knots)
gate("parity-bonds-are-circuits", bad == 0, f"{bad} bases differ")

# G4: the violation finder
path = [[abs(i - j) if i != j else 0 for j in range(5)] for i in range(5)]
planted = [row[:] for row in path]
planted[0][4] = planted[4][0] = math.inf
gate("violation-finder", not M.violations(path, 5) and len(M.violations(planted, 5)) == 3, "none on a path; three middles on a planted infinite pair")

# G5: the laws
laws = M.k2_laws()
gate("laws", len(laws) == 34 and len({M.law_class(R) for R in laws}) == 5 and
     [len(M.orders(R)) for R in (M.P0, M.NAE, M.CLAUSE, M.R5, M.R6)] == [1, 1, 1, 1, 3], "34 laws, 5 classes; orders 1,1,1,1,3")

# G6: correlation of the two thirds of two NAE knots sharing two distinctions is 1/5
st4 = M.states(4, [(M.NAE, (0, 1, 2)), (M.NAE, (0, 1, 3))])
gate("correlation", abs(M.correlation(st4, 2, 3) - 0.2) < 1e-12 and M.correlated(st4, 2, 3) and abs(M.correlation(st4, 0, 1) + 0.6) < 1e-12
     and not M.correlated(np.arange(4, dtype=np.int64), 0, 1), "1/5 for the thirds, -3/5 for the shared pair; the exact test is False on two free bits")

json.dump(out, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in out.values()) else "SOME FAIL")
