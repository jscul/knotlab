"""Hill-climb over signings on random simple 4-regular systems with n = 10..20 for the five weak classes: smallest number of solutions
reached (counted exactly by variable elimination over colourings)."""
import random, sys, time
sys.path.insert(0, "/home/jscul/p-vs-np-contact-first/proofs/FOUR-PREFER-20261101-001A/FOUR-PREFER-20261101-001A-P001_every_four_place_knot")
import prefer_lib as P
F = P.F
CL = P.classes()
ci = int(sys.argv[1]); rng = random.Random(int(sys.argv[2]))
mem = CL[ci][1]
def rand_simple(n):
    while True:
        stubs = [p for p in range(n) for _ in range(4)]; rng.shuffle(stubs)
        L = [tuple(stubs[4 * i:4 * i + 4]) for i in range(n)]
        if all(len(set(l)) == 4 for l in L) and len({frozenset(l) for l in L}) == n:
            return L
def count(lines, rels):
    """number of solutions, by brute force over colourings with bitmasks for n <= 20"""
    n = 1 + max(max(L) for L in lines)
    tot = 0
    for c in range(1 << n):
        if all(tuple(c >> p & 1 for p in L) in R for L, R in zip(lines, rels)):
            tot += 1
    return tot
t0 = time.time()
best = {}
for n in (10, 12, 14):
    for s in range(2):
        L = rand_simple(n)
        cur = [rng.choice(mem) for _ in L]
        val = count(L, cur)
        for sweep in range(3):
            for i in rng.sample(range(n), n):
                for R in rng.sample(mem, min(len(mem), 12)):
                    old = cur[i]; cur[i] = R
                    v = count(L, cur)
                    if v < val: val = v
                    else: cur[i] = old
                    if val == 0: break
                if val == 0: break
            if val == 0: break
        best[f"n={n} #{s}"] = val
        print(f"class {ci} n={n} #{s}: minimum solutions reached {val} ({round(time.time() - t0, 1)} s)", flush=True)
