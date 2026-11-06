"""scoping: additivity of two cabled insertions (rank comparisons only)"""
import itertools, sys
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
from massey_scope import B, C, massey_map
import mlib

p, r = 5, 2
L = B.four_way_algebra(p, r, 1)
F41 = ([1, -2, 1, -2], 3)
mu = mlib.milnor(mlib.P4, 4, p)

def bundle_functional(H, arc_at, lev, qs, p, mult):
    gens = [arc_at[(lev, q)] for q in reversed(qs)]
    out = []
    for h in H:
        tot, pref = 0, 1
        for g in gens:
            tot = (tot + pref * h[g]) % p
            pref = pref * mult % p
        out.append(tot)
    return out

def tensor(lams, d):
    T = {}
    for args in itertools.product(range(d), repeat=4):
        tot = 0
        for key, v in mu.items():
            tot = (tot + v * lams[key[0]][args[0]] * lams[key[1]][args[1]] * lams[key[2]][args[2]] * lams[key[3]][args[3]]) % p
        T[args] = tot
    return T

def ranks(tab, T, d):
    cols = sorted({c for v in tab.values() for c, x in enumerate(v) if x})
    Mm = [[tab[(i, j, k)][c] for c in cols] for i in range(d) for j in range(d) for k in range(d)]
    Mp = [[T[(i, j, k, l)] for l in range(d)] for i in range(d) for j in range(d) for k in range(d)]
    return B.rank(Mm, p), B.rank(Mp, p), B.rank([a + b for a, b in zip(Mm, Mp)], p)

base, n = C.connected_sum([F41] * 6)
cab = C.cable(mlib.P4, r, offset=0)
cab4 = C.cable(mlib.P4, r, offset=4)
w = cab + base[:6] + cab4 + base[6:]
U, rels, arc_at = C.presentation(w, n, r)
Hx, Hy, Hw, tab = massey_map(L, U, rels)
d = len(Hx)
lev1, lev2 = 0, len(cab) + 6
l1 = [bundle_functional(Hx, arc_at, lev1, [2 * j, 1 + 2 * j], p, p - 1) for j in range(4)]
l2 = [bundle_functional(Hx, arc_at, lev2, [4 + 2 * j, 5 + 2 * j], p, p - 1) for j in range(4)]
T1, T2 = tensor(l1, d), tensor(l2, d)
for name, T in [("sum", {k: (T1[k] + T2[k]) % p for k in T1}), ("difference", {k: (T1[k] - T2[k]) % p for k in T1}),
                ("first only", T1), ("second only", T2)]:
    print("two insertions, dim", d, name, "ranks meas/pred/joint", ranks(tab, T, d), flush=True)
