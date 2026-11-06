"""scoping: do knots with a vanishing local four-way form exist at NON-square roots t (order >= 3)?  random closed 3-, 4- and
5-braids; for every (p, d, e) with t = zeta^e and one-dimensional H1 at t, t^-1, record vanishing versus squareness of t"""
import sys
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cd")
from lmc import CyclicBraidModel
from amph_test import fourway, prim

def is_knot(word, n):
    perm = list(range(n))
    for g in word:
        i = abs(g) - 1
        perm[i], perm[i + 1] = perm[i + 1], perm[i]
    seen, q = set(), 0
    while q not in seen:
        seen.add(q); q = perm[q]
    return len(seen) == n

seed = int(sys.argv[1]); ntrials = int(sys.argv[2])
rng = np.random.default_rng(seed)
CASES = []
for p in (5, 7, 11, 13, 17):
    g = prim(p)
    for d in range(3, p):
        if (p - 1) % d: continue
        zeta = pow(g, (p - 1) // d, p)
        for e in range(1, d):
            if np.gcd(e, d) != 1: continue
            t = pow(zeta, e, p)
            CASES.append((p, d, zeta, e, t, pow(t, (p - 1) // 2, p) == 1))
stats = {}
seen = set()
for trial in range(ntrials):
    n = int(rng.choice([3, 4, 5]))
    m = int(rng.integers(4, 13))
    word = [int(rng.integers(1, n)) * int(rng.choice([1, -1])) for _ in range(m)]
    if not is_knot(word, n) or tuple(word) in seen: continue
    seen.add(tuple(word))
    for (p, d, zeta, e, t, sq) in CASES:
        L = fourway(p, d, zeta, e)
        Mo = CyclicBraidModel(word, n, L, p)
        if len(Mo.cocycles[e % d]) != 2 or len(Mo.cocycles[(-e) % d]) != 2: continue
        ix, iy, iw = (L.idx[s] for s in "xyw")
        bs = 24
        def rc(c): return (rng.integers(0, p, (bs, 2)) @ Mo.cocycles[c]) % p
        ok, _, _ = Mo.solve({ix: rc(e % d), iy: rc((-e) % d), iw: rc((-e) % d)})
        van = bool(ok.all())
        key = ("square" if sq else "nonsquare", van)
        stats[key] = stats.get(key, 0) + 1
        if van and not sq:
            print(f"NONSQUARE VANISHING: p={p} d={d} t={t} word={word} n={n}", flush=True)
print(seed, stats, flush=True)
