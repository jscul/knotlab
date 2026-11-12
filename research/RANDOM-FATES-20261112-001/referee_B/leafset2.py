"""Extra: bonds of a Berge-acyclic NAE pattern == leaf sets of connected knot sets whose span-degrees are all <= 2?"""
import itertools, random, sys
sys.path.insert(0, '.')
from t1_check import allowed_states, free_table, random_forest, bonds_of
rng = random.Random(int(sys.argv[1]))
tot = mism = 0; ngraph = 0
for it in range(int(sys.argv[2])):
    n = rng.randint(7, 13)
    E = random_forest(n, rng, (n - 1) // 2, rng.random() < 0.6)
    st = allowed_states(n, E)
    free, pc = free_table(n, st)
    bonds = set(bonds_of(n, free, pc))
    pred = set()
    k = len(E)
    for r in range(1, k + 1):
        for T in itertools.combinations(range(k), r):
            seen = {T[0]}; fr = [T[0]]
            while fr:
                a = fr.pop()
                for b in T:
                    if b not in seen and set(E[a]) & set(E[b]):
                        seen.add(b); fr.append(b)
            if len(seen) != r: continue
            deg = {}
            for i in T:
                for x in E[i]: deg[x] = deg.get(x, 0) + 1
            if max(deg.values()) > 2: continue
            pred.add(sum(1 << x for x, c in deg.items() if c == 1))
    ngraph += 1; tot += len(bonds)
    if bonds != pred:
        mism += 1; print('MISMATCH', n, E, len(bonds), len(pred))
print('graphs', ngraph, 'bonds', tot, 'graphs where bonds != predicted leaf sets:', mism)
