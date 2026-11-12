import sys, random
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from common import *
from small import newest_four, random_band
import exhpy
rng = random.Random(77)
tested = pairs = mism = 0; ex = []
while tested < 150:
    n = rng.randint(5, 13)
    if rng.random() < 0.7:
        knots = newest_four(rng.choice([0.0, 0.3, 0.5, 0.7, 0.9]), n, random.Random(rng.randrange(10**9)))
    else:
        knots = random_band(n, rng.choice([0.4, 0.7]), rng)
    if not knots: continue
    Lb, bonds, sat = brute_all_pairs(n, knots)
    if not sat: continue
    qs = []; keys = []
    for (i, j), lb in Lb.items():
        for mg in (0, 1, n):
            lo, hi = max(0, i - mg), min(n - 1, j + mg)
            qs.append((lo, hi, i, j, n, 10**9)); keys.append((i, j, lo, hi))
    res = exhpy.run(n, knots, qs)
    for (i, j, lo, hi), (b, nodes, hit, mem) in zip(keys, res):
        win = sum(1 << v for v in range(lo, hi + 1)); pm = (1 << i) | (1 << j)
        sz = [bin(x).count("1") for x in bonds if x & pm == pm and x & ~win == 0]
        lbw = min(sz) if sz else None
        pairs += 1
        if b != lbw or hit:
            mism += 1
            if len(ex) < 5: ex.append((n, knots, i, j, lo, hi, b, lbw))
    tested += 1
print("C exhaustive vs brute: patterns", tested, "queries", pairs, "mismatches", mism); print(ex)
