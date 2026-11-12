import sys, random
sys.path.insert(0, '.')
from ref import *
rng = random.Random(7)
for p in (23, 25, 27, 29):
    tally = {}; seen = set()
    while len(seen) < 200:
        u = tuple(rng.randint(0, 1) for _ in range(p))
        if min_period(u) != p: continue
        gp = gp_of(u)
        if not gp: continue
        u = min(u[i:] + u[:i] for i in range(p))
        if u in seen: continue
        seen.add(u)
        k = certify(u, gp_of(u))[0]; tally[k] = tally.get(k, 0) + 1
    print('nontrivial sample', p, tally, flush=True)
