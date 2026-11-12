import sys, random, itertools, time
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from common import *

def newest_four(q, n, rng):
    gen = F.proc_band(4, q, rng)
    knots = []
    while True:
        t = next(gen)
        if t is None:
            # all four triples present; draw again (as grow_to does)
            continue
        if max(t) >= n:
            return knots
        knots.append(t)

def random_band(n, p, rng):
    allt = [t for t in itertools.combinations(range(n), 3) if t[2] - t[0] <= 3]
    return [t for t in allt if rng.random() < p]

if __name__ == "__main__":
    rng = random.Random(20261112)
    tested = pairs = mism = 0
    examples = []
    t0 = time.time()
    kinds = {"nf": 0, "band": 0}
    while tested < int(sys.argv[1]):
        kind = rng.choice(["nf", "nf", "band"])
        n = rng.randint(5, int(sys.argv[2]))
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
            if ld != lb:
                mism += 1
                if len(examples) < 5:
                    examples.append((n, knots, i, j, ld, lb))
            # also check margin-restricted version against brute restricted bonds
        tested += 1
        kinds[kind] += 1
    print("patterns", tested, kinds, "pairs", pairs, "mismatches", mism, "time", round(time.time() - t0, 1))
    for e in examples: print(e)
