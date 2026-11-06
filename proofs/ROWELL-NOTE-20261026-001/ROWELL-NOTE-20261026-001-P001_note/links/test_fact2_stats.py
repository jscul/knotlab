"""Re-run the formula check and record how often d, e, r are nonzero (so that r_S is
actually exercised)."""
import sys, random, math
sys.path.insert(0, '.')
from braidlab import *
from test_fact2 import holonomy_rank
random.seed(7)
stats = {'sectors': 0, 'd>0': 0, 'e>0': 0, 'r>0': 0, 'r>0 and d>0': 0, 'fail': 0}
for trial in range(600):
    n = random.choice([3, 4, 5, 6])
    if trial % 2 == 0:
        w = []
        for _ in range(random.randint(1, 7)):
            i, j = sorted(random.sample(range(n), 2))
            e = random.choice([1, -1, 2, 3])
            g = A_gen(i, j)
            w += g * e if e > 0 else [-x for x in reversed(g)]
        # sprinkle some ordinary crossings to knot/twist things
        w += [random.choice([1, -1]) * random.randint(1, n - 1) for _ in range(random.randint(0, 4))]
        w += [random.choice([1, -1]) * random.randint(1, n - 1) for _ in range(0)]
    else:
        w = [random.choice([1, -1]) * random.randint(1, n - 1) for _ in range(random.randint(2, 14))]
    comps, lk, wr = linking_and_writhe(w, n)
    c = len(comps)
    tot, sectors = count_psi(w, n, return_sectors=True)
    for psi, T in sectors.items():
        S = [k for k in range(c) if psi[k]]
        if not S:
            assert T == 3 ** c
            continue
        S_strands = set(p for k in S for p in comps[k])
        evenK = [j for j in range(c) if j not in S and sum(lk[j, i] for i in S) % 2 == 0]
        r, dimfox = holonomy_rank(w, n, S_strands, evenK, comps)
        d = dimfox - 1
        e = len(evenK)
        stats['sectors'] += 1
        stats['d>0'] += d > 0
        stats['e>0'] += e > 0
        stats['r>0'] += r > 0
        stats['r>0 and d>0'] += (r > 0 and d > 0)
        if T != 3 ** (1 + d + e - r):
            stats['fail'] += 1
print(stats)
