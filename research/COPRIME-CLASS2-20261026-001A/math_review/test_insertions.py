"""Independent tests of Theorem 2(b) of 001C on Borromean insertions (own presentation, own obstruction code).
Reproduces two of the repo's numbers, then tries new configurations: unequal bundles (3,3,6), mirror/inverse Borromean
braids, conjugated (non-adjacent) bundles, and a control with bundles outside ker psi."""
import sys, time, itertools
sys.path.insert(0, '.')
import knotlib as KL

def analyse(word, n, leafspecs, T0=None, label=""):
    t0 = time.time()
    U, rels, K, mu, lam = KL.presentation(word, n, 3)
    Z1, H = KL.cocycle_space(U, rels)
    d = len(H)
    B, h2 = KL.obstruction(U, rels, H)
    kb = KL.kernels_from_bimap(B, d, h2)
    N = KL.count(kb)
    leafsets = []
    for (level, bundles) in leafspecs:
        leafsets.append([KL.leaf_values(H, K["arc_at"], level, b) for b in bundles])
    kp, Tb = KL.kernels_from_leaves(leafsets, d, T0)
    bad = sum(1 for a in kb if kb[a] != kp[a])
    # rank of the leaf configuration
    allv = [l for ls in leafsets for l in ls]
    rk = KL.rank([list(v) for v in allv], d) if allv else 0
    toparcs = [[h[K["arc_at"][(0, q)]] for q in range(n)] for h in H]
    print(f"{label}: arcs={U} d={d} dimH2={h2} N={N} predicted N={KL.count(kp)} mismatching a={bad}/{len(kb)} "
          f"leaf rank={rk} ({time.time() - t0:.1f}s)", flush=True)
    return d, N, bad, toparcs, B

def same_span(A, Bv, n):
    const = [KL.W] * n
    r1 = KL.rank(A + [const], n); r2 = KL.rank(Bv + [const], n); r12 = KL.rank(A + Bv + [const], n)
    return r1 == r2 == r12

def bundles_at(offset, sizes):
    out, p = [], offset
    for s in sizes:
        out.append(tuple(range(p, p + s))); p += s
    return out

results = {}
# ---- base checks
for k in (2, 3, 5, 6):
    d, N, bad, top, B = analyse(KL.fig8_sum(k), 2 * k + 1, [], label=f"base (4_1)^#{k}")
    assert all(all(x == 0 for x in v) for row in B for v in row), "base bimap not zero"
    results[f"base{k}"] = (d, N)

# ---- reproduce repo numbers: (4_1)^#5, one insertion at level 6, offset 1 -> N = 80896 (repo, tp_lib)
k, n = 5, 11
base = KL.fig8_sum(k)
_, _, _, top0, _ = analyse(base, n, [], label="(4_1)^#5 base")
iw, _ = KL.cable_unequal(KL.BORR, [3, 3, 3], 1)
w, tops = KL.insert(base, [(6, iw)])
d, N, bad, top, _ = analyse(w, n, [(tops[0], bundles_at(1, [3, 3, 3]))], label="repro: (4_1)^#5 level 6 offset 1")
print("   same cocycle span on top arcs:", same_span(top0, top, n), " repo N = 80896")

# digon (4_1)^#6, insertions (6,1) (10,3) -> repo N = 326656
k, n = 6, 13
base6 = KL.fig8_sum(k)
_, _, _, top6, _ = analyse(base6, n, [], label="(4_1)^#6 base")
ins = [(6, KL.cable_unequal(KL.BORR, [3, 3, 3], 1)[0]), (10, KL.cable_unequal(KL.BORR, [3, 3, 3], 3)[0])]
w, tops = KL.insert(base6, ins)
d, N, bad, top, _ = analyse(w, n, [(tops[0], bundles_at(1, [3, 3, 3])), (tops[1], bundles_at(3, [3, 3, 3]))],
                            label="repro: digon (4_1)^#6 (6,1)(10,3)")
print("   same cocycle span on top arcs:", same_span(top6, top, n), " repo N = 326656")

# ---- new: unequal bundles (3, 3, 6) on (4_1)^#6 (13 strands), at several levels/offsets
for (L, o) in ((6, 1), (9, 0), (13, 1), (17, 0), (20, 1)):
    iw, _ = KL.cable_unequal(KL.BORR, [3, 3, 6], o)
    w, tops = KL.insert(base6, [(L, iw)])
    d, N, bad, top, _ = analyse(w, n, [(tops[0], bundles_at(o, [3, 3, 6]))], label=f"new: bundles (3,3,6) level {L} offset {o}")
    print("   same cocycle span on top arcs:", same_span(top6, top, n))

# ---- new: (6, 3, 3) and (3, 6, 3)
for sizes, (L, o) in (([6, 3, 3], (8, 1)), ([3, 6, 3], (14, 0))):
    iw, _ = KL.cable_unequal(KL.BORR, sizes, o)
    w, tops = KL.insert(base6, [(L, iw)])
    analyse(w, n, [(tops[0], bundles_at(o, sizes))], label=f"new: bundles {tuple(sizes)} level {L} offset {o}")

# ---- new: mirror and inverse Borromean braids (char 2: same change expected)
for name, bw in (("mirror (s1^-1 s2)^3", [-1, 2] * 3), ("inverse (s2 s1^-1)^3", [2, -1] * 3)):
    iw, _ = KL.cable_unequal(bw, [3, 3, 3], 1)
    w, tops = KL.insert(base6, [(6, iw)])
    analyse(w, n, [(tops[0], bundles_at(1, [3, 3, 3]))], label=f"new: {name} level 6 offset 1")

# ---- new: conjugated insertion beta * B * beta^-1, leaves read at the top of B (non-adjacent strands in the original level)
beta = [4, 5, -3, 7, 6, -8, 2]            # an arbitrary braid on positions within 0..12
beta_inv = [-x for x in reversed(beta)]
for (L, o) in ((6, 1), (13, 1)):
    iw, _ = KL.cable_unequal(KL.BORR, [3, 3, 3], o)
    w, tops = KL.insert(base6, [(L, beta + iw + beta_inv)])
    analyse(w, n, [(tops[0] + len(beta), bundles_at(o, [3, 3, 3]))], label=f"new: conjugated insertion level {L} offset {o}")

# ---- new: two insertions, one nested inside the other's span of levels? (disjoint levels, overlapping strands)
ins = [(6, KL.cable_unequal(KL.BORR, [3, 3, 6], 0)[0]), (13, KL.cable_unequal(KL.BORR, [3, 3, 3], 2)[0]),
       (20, KL.cable_unequal(KL.BORR, [6, 3, 3], 1)[0])]
w, tops = KL.insert(base6, ins)
analyse(w, n, [(tops[0], bundles_at(0, [3, 3, 6])), (tops[1], bundles_at(2, [3, 3, 3])), (tops[2], bundles_at(1, [6, 3, 3]))],
        label="new: three insertions (3,3,6)@6 (3,3,3)@13 (6,3,3)@20")

# ---- control: bundles of sizes (2, 2, 2) (leaves NOT in ker psi): theorem does not apply
for (L, o) in ((6, 1), (13, 2)):
    iw, _ = KL.cable_unequal(KL.BORR, [2, 2, 2], o)
    w, tops = KL.insert(base6, [(L, iw)])
    try:
        analyse(w, n, [(tops[0], bundles_at(o, [2, 2, 2]))], label=f"control: bundles (2,2,2) level {L} offset {o}")
    except AssertionError as e:
        print("control raised", e)
