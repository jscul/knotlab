import sys, json, random, time
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from ref import *

out = {}
# (2) full census odd p <= 21
for p in range(3, 22, 2):
    t = time.time()
    L = lyndon(p)
    W = np.array(L, dtype=np.int8)
    P, G = good_pairs_batch(W)
    tally = {}
    others = []
    for n, u in enumerate(L):
        gp = [P[k] for k in np.nonzero(G[n])[0]]
        kind, c, r0 = certify(u, gp)
        tally[kind] = tally.get(kind, 0) + 1
        if kind == 'other':
            others.append(''.join(map(str, u)))
    out[p] = dict(n=len(L), tally=tally, others=others)
    print(p, len(L), tally, round(time.time() - t, 1), flush=True)

# random samples p = 23..29 : uniform random words of minimal period p, reduced to Lyndon rep
rng = random.Random(12345)
for p in (23, 25, 27, 29):
    tally = {}
    seen = set()
    while len(seen) < 300:
        u = tuple(rng.randint(0, 1) for _ in range(p))
        if min_period(u) != p: continue
        u = min(u[i:] + u[:i] for i in range(p))
        if u in seen: continue
        seen.add(u)
        kind, c, r0 = certify(u, gp_of(u))
        tally[kind] = tally.get(kind, 0) + 1
    print('sample', p, tally, flush=True)
    out['sample%d' % p] = tally
json.dump(out, open('census.json', 'w'))
