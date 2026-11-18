"""KNOT-SWITCH-20261118-001B-E001: gate checks, run before the freeze.  Each prints PASS or FAIL."""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import knotlib as K  # noqa: E402

M, L, P = K.M, K.L, K.P
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS" if ok else "FAIL"), name, detail, flush=True)


# 1. homology on known complexes: a triangle (disc), the four triangles of four points (closed: b2 = 1), two copies glued on an
#    edge (b2 = 2), an annulus of triangles (b1 = 1), a bracketing (contractible)
ok = K.betti(3, [(0, 1, 2)]) == {"b0": 1, "b1": 0, "b2": 0, "edges": 3, "triangles": 1, "duplicate_knots": 0}
ok &= K.betti(4, [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])["b2"] == 1
b = K.betti(5, [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3), (0, 1, 4), (0, 2, 4), (1, 2, 4)])
ok &= b["b2"] == 2 and b["b1"] == 0
ring = [(0, 1, 3), (1, 3, 4), (1, 2, 4), (2, 4, 5), (2, 0, 5), (0, 5, 3)]          # three squares around: an annulus
b = K.betti(6, ring)
ok &= b["b1"] == 1 and b["b2"] == 0
for n0 in (5, 6, 7, 8):
    for ks in M.bracketings(0, n0 - 1):
        b = K.betti(n0, ks)
        ok &= b["b0"] == 1 and b["b1"] == 0 and b["b2"] == 0
check("homology: disc, closed four, two closed fours, annulus, every bracketing of 5-8 contractible", ok)

# 2. the cyclic-pair-graph test
ok = K.cyc([(0, 1), (1, 2), (0, 2)]) and not K.cyc([(0, 1), (1, 2)]) and not K.cyc([(0, 1)])
check("pair graph cycle test", ok)

# 3. first step from every bracketing of 5-7: every fill is a single knot's fill with a triangle as pair graph, and it makes
#    b2 = 1 and the first crossing
ok = True
cnt = 0
for n0 in (5, 6, 7):
    for ks in M.bracketings(0, n0 - 1):
        S, G = M.base(n0, ks), M.pairs_of(ks)
        for a0, a1, k in L.moves(S, n0, G):
            if P.pc(a0) + P.pc(a1) != len(S):
                continue
            pairs = [tuple(sorted(x for x in kk if x != n0)) for kk in k]
            S2 = M.apply(S, n0, a0, a1)
            ok &= len(k) == 3 and K.cyc(pairs) and len(set(pairs)) == 3
            ok &= K.betti(n0 + 1, list(ks) + list(k))["b2"] == 1 and not K.nothing_crosses(S2, n0 + 1)
            cnt += 1
check("first fills: three knots on a triangle of pairs; b2 = 1 and a crossing", ok, f"{cnt} fills")

# 4. along short random KF3, NN and SEEDK runs: K stays connected; b2 never falls; each move changes b1 and b2 as the cone over
#    its pair graph L requires (Euler: b1' - b1 = b2' - b2 - 1 + |V_L| - |E_L|); and no crossing iff b2 = 0
ok = True
cnt = 0
rng = random.Random(4)
for trial in range(12):
    n0 = rng.choice((5, 6, 7))
    ks = rng.choice(M.bracketings(0, n0 - 1))
    for rule in ("KF3", "SEEDK", "NN"):
        tr = K.grow(ks, n0, n0 + 7, rule, 100 * trial + len(rule))
        rows = [r for r in tr if "stopped" not in r]
        for r0, r in zip(rows, rows[1:]):
            ok &= r["b0"] == 1 and r["b2"] >= r0["b2"]
            ok &= r["b1"] - r0["b1"] == r["b2"] - r0["b2"] - 1 + r["pair_vertices"] - r["pairs_used"]
            ok &= (r["b2"] == 0) == r["nothing_crosses"]
            if rule == "SEEDK":
                ok &= r["switch_by_knots"] == r["switch_by_crossings"]
            cnt += 1
check("short runs: connected, b2 never falls, cone bookkeeping, no crossing iff b2 = 0", ok, f"{cnt} steps")

# 5. K2 exhaustively: on four distinctions a, b, c, r the four knots of a filled knot allow exactly the two constant patterns and
#    the two patterns ac|br and ar|cb (with complements), which cross
pat = []
knots4 = [(0, 2, 1), (0, 3, 1), (2, 0, 3), (2, 1, 3)]                 # a = 0, b = 1, c = 2, r = 3
for s in range(16):
    if all(M.ok_btw(s, *k) for k in knots4):
        pat.append(s)
ok = sorted(pat) == sorted([0, 15, 0b0101, 0b1010, 0b1001, 0b0110])
check("K2: a filled knot allows only the constants and two crossing patterns", ok, str(sorted(pat)))

# 6. K4: a line presented by every implied knot: nothing crosses, no filled knot, b2 = C(n - 1, 3)
import math
ok = True
for n in range(4, 9):
    allk = [(a, c, b) for a, c, b in itertools.combinations(range(n), 3)]
    S = M.base(n, allk)
    ok &= len(S) == 2 * n and K.nothing_crosses(S, n) and K.betti(n, allk)["b2"] == math.comb(n - 1, 3)
    ok &= len(K.filled_knots(allk)) == 0
check("K4: saturated lines have b2 = C(n-1, 3) and no filled knot", ok)

# 7. along the short runs: a filled knot exists iff some two splits cross
ok = True
rng = random.Random(7)
cnt = 0
for trial in range(10):
    n0 = rng.choice((5, 6, 7))
    ks = rng.choice(M.bracketings(0, n0 - 1))
    for rule in ("KF3", "SEEDK"):
        for r in K.grow(ks, n0, n0 + 6, rule, 70 + trial):
            if "stopped" in r:
                continue
            ok &= (r["filled_knots"] > 0) == (not r["nothing_crosses"])
            cnt += 1
check("short runs: a filled knot iff a crossing", ok, f"{cnt} steps")

print(sum(results), "of", len(results), "checks pass")
