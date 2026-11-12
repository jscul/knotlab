"""T4 checks against the frozen fates.py (imported read-only)."""
import itertools, random, sys
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/experiments/RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census')
import fates
from fates import proc_band, proc_overlap, proc_tree, grow

def span_max(knots):
    return max(t[2] - t[0] for t in knots)

# (b) w = 4: every knot within four consecutive, every pattern a base, over many runs and q values
mx = 0; dead = 0; runs = 0
for q in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99):
    for seed in range(40):
        knots, d = grow(proc_band(4, q, random.Random(seed)), 3000)
        runs += 1; dead += d; mx = max(mx, span_max(knots))
        assert len(set(knots)) == len(knots)
print("(b) w=4 runs", runs, "max (last - first) over knots", mx, "dead", dead)

# (c) q = 1: the generator after (0,1,2) yields only None, so the pattern never ends
g = proc_band(5, 1.0, random.Random(0))
first = [next(g) for _ in range(1000)]
print("(c) w=5, q=1: distinct non-None yields in 1000 moves:", {x for x in first if x is not None})
knots, d = grow(proc_band(6, 1.0, random.Random(1)), 5000)
print("(c) w=6, q=1, horizon 5000: knots", knots, "dead", d)

# (c) from the initial history (3 distinctions) C(w,3) closing moves add nothing; with 4 distinctions they add K4^(3), a base
from math import comb
for w in (5, 6):
    # force the history: the first knot, then one new-distinction move, then only closing moves
    class R(random.Random):
        def __init__(self, seq, seed=0):
            super().__init__(seed); self.seq = list(seq)
        def random(self):
            return self.seq.pop(0) if self.seq else 0.0  # 0.0 < q: closing
    for news in (0, 1, 2):
        g = proc_band(w, 0.5, R([0.9] * news, seed=w))
        knots = [next(g)]
        for _ in range(news + comb(w, 3)):
            t = next(g)
            if t is not None: knots.append(t)
        n = max(v for t in knots for v in t) + 1
        sat = any(all(len({(s >> v) & 1 for v in t}) == 2 for t in knots) for s in range(1 << n))
        print(f"(c) w={w}: history with {3+news} distinctions, then C(w,3)={comb(w,3)} closing moves: {len(knots)} knots on {n}, still a base: {sat}")

# (a) O global (0) and T: every new knot has a new distinction; never ends
for name, mk in (("O global (0)", lambda s: proc_overlap(0.0, random.Random(s), False)), ("T", lambda s: proc_tree(random.Random(s)))):
    dd = 0; newok = True
    for s in range(30):
        knots, d = grow(mk(s), 1500); dd += d
        seen = set()
        for t in knots:
            if not (set(t) - seen) and seen: newok = False
            seen |= set(t)
    print("(a)", name, "dead", dd, "every knot after the first has a new distinction:", newok)
