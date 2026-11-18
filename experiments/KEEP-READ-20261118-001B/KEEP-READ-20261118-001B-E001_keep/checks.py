"""KEEP-READ-20261118-001B-E001: gate checks, run before the freeze.  Each prints PASS or FAIL."""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import keeplib as KL  # noqa: E402

M, L, P, K = KL.M, KL.L, KL.P, KL.K
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS" if ok else "FAIL"), name, detail, flush=True)


# 1. the closure picture's implied betweenness equals a brute-force check over the states
ok = True
rng = random.Random(1)
cnt = 0
for trial in range(20):
    n0 = rng.choice((5, 6))
    ks = rng.choice(M.bracketings(0, n0 - 1))
    S, n = M.base(n0, ks), n0
    G = M.pairs_of(ks)
    for _ in range(rng.randrange(1, 5)):
        mv = [x for x in L.moves(S, n, G) if P.pc(x[0]) + P.pc(x[1]) <= len(S) + 2]
        a0, a1, k = rng.choice(mv)
        S, G, n = M.apply(S, n, a0, a1), G | M.pairs_of(k), n + 1
    mv = L.moves(S, n, G)
    a0, a1, k = rng.choice(mv)
    pic = KL.picture_closure(S, n, k)
    D = sorted({v for kk in k for v in kk if v != n})
    implied = set()
    for x, y, z in itertools.permutations(D, 3):
        if x < z and all(M.ok_btw(s, x, y, z) for s in S):
            implied.add((x, y, z))
    got = set()
    for v, d in pic.nodes(data=True):
        if d["kind"] == "implied":
            ends = sorted(u[1] for u in pic[v] if pic[v][u]["role"] == "end")
            mid = [u[1] for u in pic[v] if pic[v][u]["role"] == "mid"][0]
            got.add((ends[0], mid, ends[1]))
    ok &= got == implied
    cnt += 1
check("closure picture = brute-force implied betweenness", ok, f"{cnt} moves")

# 2. pictures are invariant under renaming the old distinctions: on grown bases, each move's picture (every tier) has the same hash
#    as the renamed move's picture on the renamed base
ok = True
cnt = 0
rng = random.Random(2)
for trial in range(6):
    ks = list(rng.choice(M.bracketings(0, 5)))
    S, G, n, knots = M.base(6, ks), M.pairs_of(ks), 6, list(ks)
    for _ in range(4):
        mv = [x for x in L.moves(S, n, G) if P.pc(x[0]) + P.pc(x[1]) <= len(S) + 2]
        a0, a1, k = rng.choice(mv)
        S, G, n, knots = M.apply(S, n, a0, a1), G | M.pairs_of(k), n + 1, knots + list(k)
    perm = list(range(n))
    rng.shuffle(perm)
    S_r = tuple(sorted(sum(1 << perm[u] for u in range(n) if (st >> u) & 1) for st in S))
    knots_r = [tuple(perm[v] for v in k) for k in knots]
    pm = lambda k: tuple(perm[v] if v < n else v for v in k)
    for a0, a1, k in [x for x in L.moves(S, n, G) if P.pc(x[0]) + P.pc(x[1]) == len(S)][:30]:
        k_r = [pm(kk) for kk in k]
        for r in (0, 1, 2):
            ok &= KL.wl(KL.picture(knots, k, n, r)) == KL.wl(KL.picture(knots_r, k_r, n, r))
        ok &= KL.wl(KL.picture_closure(S, n, k)) == KL.wl(KL.picture_closure(S_r, n, k_r))
        cnt += 1
check("picture hashes unchanged by renaming the old distinctions", ok, f"{cnt} moves")

# 3. exact isomorphism confirms equal hashes on a sample, and separates unequal ones
ok = True
S = M.base(6, ks)
G = M.pairs_of(ks)
mv = [x for x in L.moves(S, 6, G) if P.pc(x[0]) + P.pc(x[1]) == len(S)]
pics = [KL.picture(list(ks), x[2], 6, 1) for x in mv]
for a, b in itertools.combinations(range(len(pics)), 2):
    ok &= (KL.wl(pics[a]) == KL.wl(pics[b])) == KL.same(pics[a], pics[b])
check("hash equality = isomorphism on the first fills of a bracketing", ok, f"{len(pics)} pictures")

print(sum(results), "of", len(results), "checks pass")
