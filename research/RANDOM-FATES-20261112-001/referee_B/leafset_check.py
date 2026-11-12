"""Extra: in a Berge-acyclic pattern, is the leaf set (span-degree-1 vertices) of EVERY connected knot set a bond?"""
import itertools, random, sys
sys.path.insert(0, '.')
from t1_check import allowed_states, free_table, random_forest
rng = random.Random(int(sys.argv[1]))
tot = bad = 0
for it in range(int(sys.argv[2])):
    n = rng.randint(7, 13)
    E = random_forest(n, rng, (n - 1) // 2, rng.random() < 0.5)
    st = allowed_states(n, E)
    free, pc = free_table(n, st)
    k = len(E)
    for r in range(1, k + 1):
        for T in itertools.combinations(range(k), r):
            # connected?
            seen = {T[0]}; frontier = [T[0]]
            while frontier:
                a = frontier.pop()
                for b in T:
                    if b not in seen and set(E[a]) & set(E[b]):
                        seen.add(b); frontier.append(b)
            if len(seen) != r:
                continue
            deg = {}
            for i in T:
                for x in E[i]:
                    deg[x] = deg.get(x, 0) + 1
            L = [x for x, c in deg.items() if c == 1]
            m = sum(1 << x for x in L)
            isb = (not free[m]) and all(free[m ^ (1 << x)] for x in L)
            tot += 1
            if not (isb and len(L) == r + 2):
                bad += 1
                print('FAIL', n, E, T, L)
print('connected knot sets', tot, 'leaf sets not bonds of size t+2:', bad)
