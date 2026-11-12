import sys, random, itertools, time
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from common import *
from small import newest_four, random_band
seed, count, nmin, nmax = map(int, sys.argv[1:5])
rng = random.Random(seed)
tested = pairs = mism = wpairs = wmism = 0
examples = []
dist = {}
t0 = time.time()
while tested < count:
    kind = rng.choice(["nf", "nf", "nf", "band"])
    n = rng.randint(nmin, nmax)
    if kind == "nf":
        q = rng.choice([0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.95])
        knots = newest_four(q, n, random.Random(rng.randrange(10**9)))
    else:
        knots = random_band(n, rng.choice([0.3, 0.5, 0.7, 0.85]), rng)
    if not knots:
        continue
    Lb, bonds, sat = brute_all_pairs(n, knots)
    if not sat:
        continue
    step = B.make_step(n, knots)
    for (i, j), lb in Lb.items():
        ld, S, stt = B.least_bond(n, knots, i, j, margin=n, step=step)
        pairs += 1
        dist[lb] = dist.get(lb, 0) + 1
        if ld != lb:
            mism += 1
            if len(examples) < 5: examples.append(("full", n, knots, i, j, ld, lb))
        if ld is not None and S is not None:
            m = sum(1 << v for v in S)
            if m not in bonds or len(S) != ld:
                mism += 1
                if len(examples) < 5: examples.append(("members-not-bond", n, knots, i, j, S))
        for mg in (0, 1, 2):
            lo, hi = max(0, i - mg), min(n - 1, j + mg)
            win = sum(1 << v for v in range(lo, hi + 1))
            pm = (1 << i) | (1 << j)
            sz = [bin(b).count("1") for b in bonds if b & pm == pm and b & ~win == 0]
            lbw = min(sz) if sz else None
            ldw = B.least_bond(n, knots, i, j, margin=mg, step=step)[0]
            wpairs += 1
            if ldw != lbw:
                wmism += 1
                if len(examples) < 5: examples.append(("win", mg, n, knots, i, j, ldw, lbw))
    tested += 1
print("seed", seed, "patterns", tested, "n", nmin, nmax, "pairs", pairs, "mismatches", mism, "window-pairs", wpairs, "window-mismatches", wmism,
      "time", round(time.time() - t0, 1))
print("L distribution", sorted(dist.items(), key=lambda kv: (kv[0] is None, kv[0] or 0)))
for e in examples: print(e)
