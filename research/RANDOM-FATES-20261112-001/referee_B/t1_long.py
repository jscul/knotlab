import random, sys
sys.path.insert(0, '.')
from t1_check import check
rng = random.Random(int(sys.argv[1]))
stats = {"graphs": 0, "pairs": 0, "bonds": 0, "chains": 0, "by_d": {}, "bond_eq_leafset": 0, "max_hub": 0}
nv = 0
for it in range(int(sys.argv[2])):
    # long, hub-bearing hypertrees on 13 vertices: knots of one existing + two new, existing biased to the newest
    E = [(0, 1, 2)]; n = 3
    while n + 2 <= 13:
        r = rng.random()
        a = rng.choice([n - 1, n - 2]) if r < 0.6 else (rng.choice([x for e in E for x in e]) if r < 0.85 else rng.randrange(n))
        E.append((a, n, n + 1)); n += 2
    # random relabel
    perm = list(range(n)); rng.shuffle(perm)
    E = [tuple(sorted(perm[x] for x in e)) for e in E]
    v = check(n, E, stats); stats["graphs"] += 1
    if v: nv += 1; print("VIOL", E, v[:3])
print(stats, "graphs with violations", nv)
