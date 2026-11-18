"""NEVER-NEST-20261118-001B-E001: gate checks, run before the freeze.  Each prints PASS or FAIL."""
import hashlib
import itertools
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nnlib as L  # noqa: E402

M = L.M
ROOT = L.ROOT
sys.path.append(os.path.join(ROOT, "experiments", "STATE-RULES-20261117-001B", "STATE-RULES-20261117-001B-E001_rules"))
import rules as R  # noqa: E402

PIN = {
    "experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/melib.py":
        "9d1b32f3c600a8e489862bc14bff8a78eb0b7c925eb73adcff1635205d1788a4",
    "experiments/STATE-RULES-20261117-001B/STATE-RULES-20261117-001B-E001_rules/rules.py":
        "d1ee374ca2c6784bdbad72c32878d7c6a3c98c60a28da73f34f14f76c8d10172",
    "experiments/LOCAL-ROOM-20261118-001B/LOCAL-ROOM-20261118-001B-E001_local/locallib.py":
        "30a724e34e4f6e6319fb01420d3eb791c5be65a8b7932b84d72961e57230327b",
}
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS" if ok else "FAIL"), name, detail, flush=True)


def random_bases(count, seed, nmax=10):
    """Bases reached by random KF3 moves (any cost, kept to at most 62 states) from random bracketings, with their knot-sharing
    pairs."""
    rng = random.Random(seed)
    out = []
    while len(out) < count:
        n0 = rng.choice((4, 5, 6))
        ks = rng.choice(M.bracketings(0, n0 - 1))
        S, G, n = M.base(n0, ks), M.pairs_of(ks), n0
        for _ in range(rng.randrange(0, nmax - n0 + 1)):
            mv = [x for x in M.moves(S, n, G) if R.pc(x[0]) + R.pc(x[1]) <= 62]
            if not mv:
                break
            a0, a1, k = rng.choice(mv)
            S, G, n = M.apply(S, n, a0, a1), G | M.pairs_of(k), n + 1
        out.append((S, n, G))
    return out


# 1. pinned code
for path, h in PIN.items():
    got = hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()
    check("pin " + os.path.basename(path), got == h)

# 2. the fast two-order test against melib's measure
bases = random_bases(60, 1)
bad = tot = 0
for S, n, G in bases:
    for a0, a1, k in M.moves(S, n, G)[:150]:
        S2 = M.apply(S, n, a0, a1)
        tot += 1
        bad += L.two(S2, n + 1) != M.two_orders(M.measure(S2, n + 1))
check("two() = melib two orders", bad == 0, f"{tot} bases")

# 2b. the wide enumeration of KF3's moves = melib.moves
ok = True
for S, n, G in bases[:40]:
    ok &= sorted(L.moves(S, n, G, wide=True)) == sorted(M.moves(S, n, G))
check("wide moves = melib.moves", ok, "40 bases")

# 3. free fills of a line: the C(n, 3) fills of its triples, each keeping two orders (STATE-RULES S3)
ok = True
for n in range(3, 9):
    S = L.line_states(n)
    z = L.free_zero(S, n)
    ok &= len(z) == math.comb(n, 3) and all(L.two(M.apply(S, n, *k), n + 1) for k in z)
check("free fills of a line = C(n,3), all two orders", ok, "n = 3..8")

# 4. free_zero against STATE-RULES's unrestricted extensions (zero-cost part), on small bases
ok = True
cnt = 0
for S, n, G in random_bases(25, 2, nmax=8) + [(L.square_states(), 4, None), (L.line_states(5), 5, None)]:
    S = tuple(sorted(S))
    ref = {k for k in R.extensions(list(S), n, 3) if R.pc(k[0]) + R.pc(k[1]) == len(S)}
    ok &= set(L.free_zero(S, n)) == ref
    cnt += 1
check("free_zero = rules.extensions at zero cost", ok, f"{cnt} bases")

# 4b. the fills that keep two orders, from the empty cells (connected crossing graphs), = all fills filtered by two orders
ok = True
cnt = 0
rng = random.Random(41)
pool = []
for trial in range(12):
    S, n = (L.square_states(), 4) if trial % 2 else (L.line_states(5 + trial % 3), 5 + trial % 3)
    for _ in range(rng.randrange(1, 9)):
        ops, _ = L.free_options(S, n)
        (a0, a1), _ = rng.choice(ops)
        S, n = M.apply(S, n, a0, a1), n + 1
        pool.append((S, n))
for S, n in pool + [(S, n) for S, n, G in random_bases(30, 5, nmax=9)]:
    S = tuple(sorted(S))
    if L.free_cells(S, n) is None:
        continue
    ref = {k for k in L.free_zero(S, n) if L.two(M.apply(S, n, *k), n + 1)}
    ok &= set(L.free_two_fills(S, n)) == ref
    cnt += 1
check("two-order fills from the empty cells = all fills filtered", ok, f"{cnt} connected bases")

# 5. free_subs against STATE-RULES's single middle knots at disagreement two
ok = True
for S, n, G in random_bases(25, 3, nmax=8):
    S = tuple(sorted(S))
    ref = set()
    masks, Z, O = R.knot_masks(list(S), n)
    ties = {(Z[u], O[u]) for u in range(n)}
    for k, a0, a1 in masks:
        if k[1] == n and L.dis(S, k[0], k[2]) == 2 and (a0, a1) not in ties:
            ref.add((a0, a1))
    ok &= set(L.free_subs(S, n)) == ref
check("free_subs = single middle knots at disagreement two", ok)

# 6. N1: every subdivision keeps k and lambda (knot-sharing and free), on random bases
ok = True
cnt = 0
for S, n, G in random_bases(80, 4, nmax=11):
    m0 = M.measure(S, n)
    for (a0, a1) in L.free_subs(tuple(sorted(S)), n):
        m1 = M.measure(M.apply(S, n, a0, a1), n + 1)
        ok &= (m1["k"], m1["lam"]) == (m0["k"], m0["lam"])
        cnt += 1
check("N1: subdivisions keep k and lambda", ok, f"{cnt} subdivisions")

# 7. N3 on NNF from the 2 x 2 pattern to n = 16: at every step two orders and a complete bipartite crossing graph, the fills
#    that keep two orders are exactly the empty cells of the grid of the two chains, and with none left the options are
#    subdivisions
ok = True
rng = random.Random(7)
cnt = 0
for trial in range(8):
    S, n = L.square_states(), 4
    while n < 16:
        r = L.reading(S, n)
        ok &= r["two"] and r["complete"]
        empty = (r["parts"][0] + 1) * (r["parts"][1] + 1) - n
        ops, info = L.free_options(S, n)
        ok &= info["zero_two_ext"] == empty
        if empty == 0:
            ok &= all(len(ks) == 1 and ks[0][1] == n and L.dis(S, ks[0][0], ks[0][2]) == 2 for _, ks in ops)
        (a0, a1), ks = rng.choice(ops)
        S, n = M.apply(S, n, a0, a1), n + 1
        cnt += 1
check("N3: fills that keep two orders = empty cells; else subdivisions", ok, f"{cnt} steps")


# 8. odd sets on the tracked line = melib's while no state is added; where every odd set is a triple, Lemma C's verdict = two
#    orders (NN also takes fills with larger odd sets that keep two orders: counted, not checked by Lemma C)
ok = True
cnt = big = 0
for n0 in (5, 6, 7):
    for ks in M.bracketings(0, n0 - 1):
        S, G, n = M.base(n0, ks), M.pairs_of(ks), n0
        rng = random.Random(n0 * 1000 + len(ks))
        for _ in range(3):
            ops, _ = L.options(S, n, G, "NN")
            a0, a1, k = rng.choice(ops)
            S2 = M.apply(S, n, a0, a1)
            if len(S2) != len(S):
                break
            S, G, n = S2, G | M.pairs_of(k), n + 1
            mine = L.odd_sets_line(S, n, list(range(n0)))
            ref = M.odd_sets(S, n, n0)
            ok &= mine is not None and [mine[u] for u in range(n0, n)] == ref
            if L.lemma_c(mine) is None:
                big += 1
            else:
                ok &= L.lemma_c(mine) == (2 if L.two(S, n) else 3)
            cnt += 1
check("odd sets = melib's; Lemma C = two orders on triples", ok, f"{cnt} bases, {big} with a larger odd set")

# 8b. Lemma C on random line bases with fills of triples (not only NN's): its verdict = the measured number of orders
ok = True
rng = random.Random(81)
for trial in range(300):
    n0 = rng.choice((5, 6, 7, 8))
    S, n = L.line_states(n0), n0
    for _ in range(rng.randrange(1, 4)):
        tri = [z for z in L.free_zero(S, n)]
        odd_all = []
        for z in tri:
            S2 = M.apply(S, n, *z)
            o = L.odd_sets_line(S2, n + 1, list(range(n0)))
            if o is not None and len(o[n]) == 3:
                odd_all.append(S2)
        if not odd_all:
            break
        S, n = rng.choice(odd_all), n + 1
    o = L.odd_sets_line(S, n, list(range(n0)))
    v = L.lemma_c(o)
    m = M.measure(S, n)
    want = 1 if m["lam"] == 1 else (2 if (m["k"] == 2 and m["lam"] == 2) else 3)
    ok &= v == want
check("Lemma C = measured orders on random fills of triples", ok, "300 bases")


# 9. NN's first step from a bracketing: the fills of its knots (Lemma A), all keeping two orders; second step: the options that
#    keep two orders are MEET-ORDERS's Lemma B 'good' ones
ok = True
for n0 in (5, 6, 7):
    for ks in M.bracketings(0, n0 - 1):
        S, G = M.base(n0, ks), M.pairs_of(ks)
        ops, info = L.options(S, n0, G, "NN")
        ok &= len(ops) == n0 - 2 and info["zero_two"] == n0 - 2
        for first in ks:
            c = M.classify_second_step(ks, first)
            a0, a1, k1 = [o for o in ops if M.old_pairs(o[2], n0) == M.pairs_of([first])][0]
            S1, G1 = M.apply(S, n0, a0, a1), G | M.pairs_of(k1)
            o2, i2 = L.options(S1, n0 + 1, G1, "NN")
            ok &= c["ok"] and i2["zero_two"] == c["good"] and len(o2) == c["good"]
check("NN steps 1 and 2 = Lemmas A and B", ok)

# 10. subdivisions always exist for NN on the line with fills (adjacent line distinctions share a knot and differ in two states)
ok = True
for n0 in (5, 6, 7, 8):
    for ks in M.bracketings(0, n0 - 1):
        G = M.pairs_of(ks)
        ok &= all((i, i + 1) in G for i in range(n0 - 1))
check("every adjacent pair of every bracketing shares a knot", ok)

# 11. exact NN: probabilities sum to one, two orders with probability one after the first fill; SUB keeps the line
ok = True
for ks in M.bracketings(0, 4)[:2]:
    lv = L.exact(ks, 5, 9, "NN")
    ok &= all(sum(l["N"].values()) + l["stalled"] == 1 for l in lv)
    ok &= all(l["two"] == 1 for l in lv[1:])
    lv = L.exact(ks, 5, 8, "SUB")
    ok &= all(l["two"] == 0 and l["N"] == {2 * l["n"]: 1} for l in lv)
check("exact NN sums to one, two orders after the first fill; SUB keeps the line", ok)

# 12. labelled runs: decisions recomputed from the states and pairs alone (no memory): replaying a run from its recorded bases
#     gives the same option sets
ok = True
ks = M.bracketings(0, 5)[4]
import random as _r
rng = _r.Random(12)
S, G, n = M.base(6, ks), M.pairs_of(ks), 6
for _ in range(10):
    ops, _ = L.options(S, n, G, "NN")
    perm = list(range(n))
    rng.shuffle(perm)
    S_r = tuple(sorted(sum(1 << perm[u] for u in range(n) if (s >> u) & 1) for s in S))
    G_r = frozenset((min(perm[a], perm[b]), max(perm[a], perm[b])) for a, b in G)
    ops_r, _ = L.options(S_r, n, G_r, "NN")
    ok &= len(ops) == len(ops_r)
    a0, a1, k = rng.choice(ops)
    S, G, n = M.apply(S, n, a0, a1), G | M.pairs_of(k), n + 1
check("NN's option count is unchanged by renaming the distinctions", ok)

# 13. N4: NNF from the line of 5 to 8 never subdivides before its first full grid, which has (s0 + 1)(s1 + 1) distinctions
#     with s0 + s1 = n0 - 1
ok = True
for n0 in (5, 6, 7, 8):
    for seed in range(4):
        tr = L.free_grow(L.line_states(n0), n0, 24, 100 * n0 + seed)
        first = next((r for r in tr if r.get("full_grid") and r["n"] > n0), None)
        ok &= first is not None
        if first is None:
            continue
        ok &= all(r.get("kind") != "sub" for r in tr if r["n"] <= first["n"])
        a, b = first["parts"]
        ok &= a + b == n0 - 1 and first["n"] == (a + 1) * (b + 1)
        ok &= all(r["two"] for r in tr[1:] if "two" in r)
check("N4: NNF reaches a full grid from the line before any subdivision", ok)

# 14. N5: CC's fills are NNF fills (empty cells) wherever both are defined; from the 2 x 2 pattern CC keeps two orders and is a
#     full grid after every new row or column; from a line it never fills
ok = True
cnt = 0
for S, n in pool:
    if L.free_cells(S, n) is None:
        continue
    ok &= set(L.cc_fills(S, n)) <= set(L.free_two_fills(S, n))
    cnt += 1
for seed in range(6):
    tr = L.free_grow(L.square_states(), 4, 20, 300 + seed, rule="CC")
    ok &= all(r["two"] and r["complete"] for r in tr)
    for r0, r1 in zip(tr, tr[1:]):
        if r1["kind"] == "sub":
            ok &= r0["full_grid"]
        ok &= (r1["kind"] == "sub") == (r0["empty"] == 0)
    tr = L.free_grow(L.line_states(5 + seed % 3), 5 + seed % 3, 12, 400 + seed, rule="CC")
    ok &= all(r["kind"] in ("start", "sub") for r in tr) and all(r["lam"] == 1 for r in tr)
check("N5: CC fills = empty cells, refills from 2 x 2, never fills a line", ok, f"{cnt} bases")

print(sum(results), "of", len(results), "checks pass")
