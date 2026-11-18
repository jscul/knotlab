"""MID-RULE-20261118-001B-E001: gate checks, run before the freeze.  Each prints PASS or FAIL."""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import midlib as ML  # noqa: E402

M, L, P, K = ML.M, ML.L, ML.P, ML.K
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS" if ok else "FAIL"), name, detail, flush=True)


def random_bases(count, seed):
    """Bases from lines, the 2 x 2 pattern and Q3 by random fills and subdivisions (free), with at most 40 states."""
    rng = random.Random(seed)
    out = []
    while len(out) < count:
        S, n = P.start(rng.choice(["line5", "line6", "line7", "2x2", "Q3"]))
        for _ in range(rng.randrange(1, 9)):
            ops = P.fills(S, n) + P.subdivisions(S, n)
            if not ops:
                break
            a0, a1 = rng.choice(ops)
            S, n = M.apply(S, n, a0, a1), n + 1
            if len(S) > 40:
                break
        out.append((tuple(sorted(S)), n))
    return out


# 1. M1 on every fill of random bases: a fill certified with at most one end knot makes no new crossing; and every fill that makes
#    a new crossing has no such certificate (both directions of the test on the same fills)
ok = True
cnt = new_cross = one_end = 0
for S, n in random_bases(80, 1):
    for f in P.fills(S, n):
        new, _ = P.new_crossings(S, n, f[1])
        c1 = ML.certified(S, n, f[0], f[1], "ONE")
        ok &= not (c1 and new)
        cnt += 1
        new_cross += bool(new)
        one_end += c1
check("M1: no fill certified with at most one end knot makes a crossing", ok, f"{cnt} fills, {new_cross} crossing, {one_end} one-end")

# 2. MID2's certificate test implies ONE's (two middle knots among at most three leave at most one end knot)
ok = True
for S, n in random_bases(40, 2):
    for f in P.fills(S, n):
        if ML.certified(S, n, f[0], f[1], "MID2"):
            ok &= ML.certified(S, n, f[0], f[1], "ONE")
check("MID2's certificates are ONE's", ok)

# 3. the certificate tests against an independent brute force over all knot sets of at most three consistent knots
ok = True
cnt = 0
for S, n in random_bases(25, 3)[:25]:
    O, Z, full = M.cols(S, n)
    knots = []
    import itertools
    for u, v in itertools.combinations(range(n), 2):
        eq = (O[u] & O[v]) | (Z[u] & Z[v])
        ne = full ^ eq
        knots.append(("mid", Z[u] & Z[v], O[u] & O[v]))
        knots.append(("end", ne & Z[v], ne & O[v]))
        knots.append(("end", ne & Z[u], ne & O[u]))
    for f in P.fills(S, n)[:15]:
        F0, F1 = f
        cons = [k for k in knots if not (k[1] & F1) and not (k[2] & F0) and (k[1] | k[2])]
        best = {"MID2": False, "ONE": False}
        for r in (1, 2, 3):
            for ks in itertools.combinations(cons, r):
                cov = 0
                for k in ks:
                    cov |= k[1] | k[2]
                if cov != full:
                    continue
                mids = sum(k[0] == "mid" for k in ks)
                best["MID2"] |= mids >= 2
                best["ONE"] |= (len(ks) - mids) <= 1
        ok &= best["MID2"] == ML.certified(S, n, F0, F1, "MID2") and best["ONE"] == ML.certified(S, n, F0, F1, "ONE")
        cnt += 1
check("certificate tests = brute force over consistent knot sets", ok, f"{cnt} fills")

# 4. M3: at full two-way grids grown by NNF, no fill has a certificate with at most one end knot (so MID2F and ONEF subdivide
#    there), and after a subdivision the median of the new distinction and two old cells qualifies under MID2
ok = True
cnt = 0
rng = random.Random(4)
S, n = L.square_states(), 4
while n < 20:
    r = P.reading(S, n)
    if r["full_grid"]:
        ok &= not any(ML.certified(S, n, f[0], f[1], "ONE") for f in P.fills(S, n))
        cnt += 1
    ops, _ = L.free_options(S, n)
    (a0, a1), _ = rng.choice(ops)
    S2 = M.apply(S, n, a0, a1)
    if len(S2) > len(S):
        ops2, kind = ML.mid2f_options(tuple(sorted(S2)), n + 1, "MID2")
        ok &= kind == "fill"
    S, n = S2, n + 1
check("M3: full grids offer no one-end fill; after a subdivision MID2 has a fill", ok, f"{cnt} full grids")

print(sum(results), "of", len(results), "checks pass")
