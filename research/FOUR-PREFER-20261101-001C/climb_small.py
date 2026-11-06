"""Hill-climb over signings (one member relation per line) to minimise the number of solutions, on simple 4-regular systems
without repeated lines, n = 5..8; report whether some class reaches 0 (a failure)."""
import json, random, sys, time
sys.path.insert(0, "/home/jscul/p-vs-np-contact-first/proofs/FOUR-PLACE-20261031-001A/FOUR-PLACE-20261031-001A-P001_the_value_free_four_place_knots")
import four_lib as F
H4 = F.H4
knots = []
for m in range(1, 1 << 16):
    R = frozenset(s for i, s in enumerate(H4) if m >> i & 1)
    if F.is_knot(R): knots.append(R)
cls = {}
for R in knots: cls.setdefault(F.canonical(R), []).append(R)
CL = sorted(cls.items(), key=lambda kv: (len(kv[0]), sorted(kv[0])))
census = json.load(open("/home/jscul/p-vs-np-contact-first/research/MUTUAL-SELECTION-20261031-001C/census.json"))
rng = random.Random(11)
def rand_simple(n):
    while True:
        stubs = [p for p in range(n) for _ in range(4)]
        rng.shuffle(stubs)
        lines = [tuple(stubs[4 * i:4 * i + 4]) for i in range(n)]
        if all(len(set(L)) == 4 for L in lines) and len({frozenset(L) for L in lines}) == n:
            return lines
systems = [L for n in (5, 6, 7) for L in F.systems(n, census) if len({frozenset(x) for x in L}) == len(L)]
systems += [rand_simple(8) for _ in range(6)] + [rand_simple(9) for _ in range(4)]
todo = [int(x) for x in sys.argv[1].split(",")]
t0 = time.time()
for ci in todo:
    c, mem = CL[ci]
    best_overall, hits = None, 0
    for lines in systems:
        n = 1 + max(max(L) for L in lines)
        opts = [[F.line_mask(L, n, R) for R in mem] for L in lines]
        for restart in range(6):
            cur = [rng.randrange(len(mem)) for _ in lines]
            def count(ch):
                acc = (1 << (1 << n)) - 1
                for i, j in enumerate(ch):
                    acc &= opts[i][j]
                return bin(acc).count("1")
            val = count(cur)
            improved = True
            while improved and val > 0:
                improved = False
                order = list(range(len(lines))); rng.shuffle(order)
                for i in order:
                    for j in rng.sample(range(len(mem)), len(mem)):
                        if j == cur[i]: continue
                        old = cur[i]; cur[i] = j
                        v = count(cur)
                        if v < val:
                            val = v; improved = True; break
                        cur[i] = old
                    if val == 0: break
            best_overall = val if best_overall is None else min(best_overall, val)
            if val == 0:
                hits += 1
                break
    print(f"class {ci:2d} (states {len(c)}, relations {len(mem)}): failures reached on {hits} of {len(systems)} simple systems; best minimum {best_overall}", round(time.time() - t0, 1), "s", flush=True)
