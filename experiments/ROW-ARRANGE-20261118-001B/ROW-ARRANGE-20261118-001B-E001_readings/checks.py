"""Gates for ROW-ARRANGE-20261118-001B-E001 (run before the freeze)."""
import itertools
import json
import random
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import families as Fm  # noqa: E402
import readings as RD  # noqa: E402

results = {}


def gate(name, ok, detail=""):
    results[name] = {"pass": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""), flush=True)


canon, lv = RD.CB.reachable("one-split", 7)
p7 = [list(canon.reps[c][0]) for c in lv[7]]
p6 = [list(canon.reps[c][0]) for c in lv[6]]

# 1. reading a reproduces COUNT-BALLS at n = 7 (1,651 groups; 3 of them mix k)
groups = {}
for st in p7:
    groups.setdefault(RD.read_a(RD.table(st, 7)), []).append(RD.targets(st, 7)[0])
mixk = sum(len(set(v)) > 1 for v in groups.values())
gate("a-reproduces-COUNT-BALLS-n7", len(groups) == 1651 and mixk == 3, f"{len(groups)} groups, {mixk} mixing k")

# 2. every reading is invariant under renaming
rng = random.Random(5)
bad = 0
for st in rng.sample(p7, 120) + rng.sample(p6, 80):
    n = 7 if st in p7 else 6
    perm = list(range(n))
    rng.shuffle(perm)
    st2 = RD.R.relabel(st, n, perm)
    D1, D2 = RD.table(st, n), RD.table(st2, n)
    for name, f in RD.READINGS.items():
        if RD.intern(f(D1)) != RD.intern(f(D2)):
            bad += 1
    for r in (2, 4, 6, 8):
        if RD.read_B(D1, r) != RD.read_B(D2, r):
            bad += 1
gate("readings-invariant-under-renaming", bad == 0, f"{bad} differences over 200 random renamings")

# 3. the view canonical form against brute force over all orders fixing the marked start
def brute(M):
    m = len(M)
    best = None
    for rest in itertools.permutations(range(1, m)):
        order = (0,) + rest
        flat = tuple(M[order[i]][order[j]] for i in range(m) for j in range(i + 1, m))
        if best is None or flat < best:
            best = flat
    return best
views = []
for st in rng.sample(p6, 60):
    D = RD.table(st, 6)
    for x in range(6):
        r = rng.choice([4, 6, 8])
        ball = [x] + [y for y in range(6) if y != x and D[x][y] <= r]
        views.append([[D[u][v] for v in ball] for u in ball])
mism = 0
for M1, M2 in itertools.combinations(rng.sample(views, 120), 2):
    if len(M1) != len(M2):
        continue
    if (RD.canon_view(M1) == RD.canon_view(M2)) != (brute(M1) == brute(M2)):
        mism += 1
gate("view-canonical-form-vs-brute-force", mism == 0, f"{mism} disagreements over pairs of 120 random views")

# 4. the families
def base(G):
    st, n, _, _ = Fm.halfspace_base(G)
    return st, n
for G, name in ((Fm.F(2, 4), "F(2,4)"), (Fm.F(3, 3), "F(3,3)"), (Fm.kappa(nx.cycle_graph(4)), "kappa(C4)"),
                (Fm.kappa(nx.cycle_graph(6)), "kappa(C6)")):
    st, n = base(G)
    gate(f"partial-cube-is-a-base-{name}", Fm.betweenness_solutions(G) == st, f"n = {n}, N = {len(st)}")
(s1, n1), (s2, n2) = base(Fm.F(2, 4)), base(Fm.F(3, 3))
D1, D2 = RD.table(s1, n1), RD.table(s2, n2)
gate("F-pair", RD.targets(s1, n1)[0] == 4 and RD.targets(s2, n2)[0] == 3 and len(s1) == len(s2)
     and RD.read_B(D1, 2) == RD.read_B(D2, 2), f"k {RD.targets(s1, n1)} vs {RD.targets(s2, n2)}, N {len(s1)}, equal B2")
(s1, n1), (s2, n2) = base(Fm.kappa(nx.cycle_graph(10))), base(Fm.kappa(nx.disjoint_union(nx.cycle_graph(5), nx.cycle_graph(5))))
D1, D2 = RD.table(s1, n1), RD.table(s2, n2)
same = all(RD.intern(f(D1)) == RD.intern(f(D2)) for f in (RD.read_a, RD.read_N1, RD.read_W2, RD.read_WL))
gate("kappa-pair", RD.targets(s1, n1)[0] == 2 and RD.targets(s2, n2)[0] == 3 and same and RD.read_B(D1, 4) != RD.read_B(D2, 4),
     f"k {RD.targets(s1, n1)} vs {RD.targets(s2, n2)}, n {n1}, equal a, N1, W2, WL; B4 differs")

# 5. the ladder's order on every class at n = 6
cls = []
for st in p6:
    D = RD.table(st, 6)
    cls.append({k: RD.intern(f(D)) for k, f in RD.READINGS.items()})
viol = 0
for u, v in itertools.combinations(cls, 2):
    if u["N1"] == v["N1"] and u["a"] != v["a"]:
        viol += 1
    if u["W2"] == v["W2"] and (u["a"] != v["a"]):
        viol += 1
    if u["WL"] == v["WL"] and (u["N1"] != v["N1"] or u["W2"] != v["W2"]):
        viol += 1
gate("ladder-order-n6", viol == 0, f"{viol} violations")

json.dump(results, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in results.values()) else "SOME FAIL")
