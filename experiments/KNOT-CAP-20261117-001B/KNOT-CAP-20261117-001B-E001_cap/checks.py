"""Controls for caplib.py and run.py, run before the freeze."""
import collections
import itertools
import random
import sys

import caplib as C
import run as RUN

R = C.R
rng = random.Random("KNOT-CAP checks")
fails = 0


def check(name, ok, detail=""):
    global fails
    print(("ok   " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    fails += not ok


# 1. the caps hold, and with no cap the moves are the knot arm's
bad = 0
for trial in range(60):
    n = rng.randint(3, 6)
    ks = [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(1, n))]
    st = R.base_from_knots(n, ks)
    if len(st) < 2:
        continue
    for local in (None, "knot"):
        free = {(a0, a1, kk) for a0, a1, kk in C.cap_moves(st, n, ks, RUN.INF, local)}
        if free != {(a0, a1, kk) for a0, a1, kk in R.knot_moves(st, n, ks, 3, local)}:
            bad += 1
        for c in (2, 3, 4):
            for a0, a1, kk in C.cap_moves(st, n, ks, c, local):
                if max(C.degrees(ks + list(kk), n + 1)) > max(c, max(C.degrees(ks, n))) or \
                        any(C.degrees(ks + list(kk), n + 1)[x] > c for k in kk for x in k):
                    bad += 1
        for a0, a1, kk in C.cap_moves(st, n, ks, RUN.INF, local, pair=2):
            pcs = C.pair_counts(ks + list(kk))
            if any(pcs[q] > 2 for k in kk for q in [(min(a, b), max(a, b)) for a, b in itertools.combinations(k, 2)]):
                bad += 1
check("caps: no cap = the knot arm's moves; degree and pair caps hold for every allowed move (60 bases)", bad == 0, f"{bad}")

# 2. the cap of 3 from one knot: the square, then a stall
levels, _ = C.cap_exact("line", 5, 3)
check("c = 3 from one knot: the 2 x 2 pattern at n = 4, then every run stalls",
      levels[1]["kinds"] if False else (RUN.kinds(levels[1]["dist"]) == {"two orders": 1.0} and levels[-1]["stalled_before"] == 1.0),
      f"{RUN.kinds(levels[1]['dist'])}, stalled {levels[-1]['stalled_before']}")

# 3. the exact states-only continuation of a single class equals rules.exact
sc = R.Canon()
n, st = R.seed("line")
mix = {sc.cid(st, n): 1.0}
mine = C.states_exact_from(mix, sc, 7)
ref, rc = R.exact("fewest", 3, "line", 7)
ok = True
for (nn, d), L in zip(mine, ref):
    k1 = collections.Counter()
    for cl, p in d.items():
        s2, n2, _ = sc.reps[cl]
        k1[R.measure(list(s2), n2)["kind"]] += p
    k2 = collections.Counter()
    for _, p, m in L["dist"]:
        k2[m["kind"]] += p
    ok &= all(abs(k1[k] - k2[k]) < 1e-9 for k in set(k1) | set(k2))
check("states-only continuation from one class = rules.exact (F3, one knot, to n = 7)", ok)

# 4. the matched five-starts: the same ten states, three knots each, different classes; the shared distinction an end or the middle
f5, m5 = R.SEEDS["fan5"][1], R.SEEDS["mid5"][1]
l5 = R.base_from_knots(5, list(itertools.combinations(range(5), 3)))
c5 = R.Canon()
hub = lambda ks: [x for x in range(5) if all(x in k for k in ks)]
check("fan5 and mid5: the line of five's 10 states, different knot classes, shared distinction 0 (an end) and 2 (the middle)",
      R.base_from_knots(5, f5) == l5 == R.base_from_knots(5, m5) and len(l5) == 10 and c5.cid(l5, 5, f5) != c5.cid(l5, 5, m5)
      and hub(f5) == [0] and hub(m5) == [2], f"{hub(f5)}, {hub(m5)}")

# 5. erasure: after erase_at every step is a states-only step, and the knots no longer grow
_, kn, nn, tr = C.cap_grow("fan6", 10, "erase-check", RUN.INF, "knot", erase_at=8)
check("erasure: knots stop growing at n = 8, steps after are states-only", all(r.get("erased") for r in tr if r["n"] > 8) and
      len(kn) == 4 + sum(r["knots"] for r in tr if 6 < r["n"] <= 8))

# 6. TV and the permutation test behave: identical samples give 0 and p near 1; disjoint give 1 and a small p
check("TV of a distribution with itself is 0; of disjoint ones 1", C.tv({1: .5, 2: .5}, {1: .5, 2: .5}) == 0 and C.tv({1: 1}, {2: 1}) == 1)
pp = RUN.permutation_p([1] * 50 + [2] * 50, [1] * 50 + [2] * 50, 0.0, 50, "s")
pq = RUN.permutation_p([1] * 50, [2] * 50, 1.0, 50, "s")
check("permutation test: p = 1 for equal samples, small for disjoint ones", pp == 1.0 and pq < 0.05, f"{pp}, {pq}")

print("FAILURES:", fails)
sys.exit(1 if fails else 0)
