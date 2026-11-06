"""Random stress test of T' = T0 + sum det(leaves) on figure-eight bases and on a trefoil + figure-eight base (T0 = xi^3).
Own implementation only (knotlib.py)."""
import sys, random, time
sys.path.insert(0, '.')
import knotlib as KL

def xi_from_base(B, d, h2):
    rows = []
    for j in range(d):
        for t in range(h2):
            rows.append([B[i][j][t] for i in range(d)])
    K0 = KL.nullspace(rows, d)
    assert len(K0) == d - 1, len(K0)
    xi = KL.nullspace(K0, d)
    assert len(xi) == 1
    return xi[0]

def run(base, n, ins_specs, T0fun=None, label=""):
    ins = []
    leafspecs = []
    for (L, bw, sizes, o, conj) in ins_specs:
        iw, _ = KL.cable_unequal(bw, sizes, o)
        cinv = [-x for x in reversed(conj)]
        ins.append((L, conj + iw + cinv))
    w, tops = KL.insert(base, ins)
    U, rels, K, mu, lam = KL.presentation(w, n, 3)
    Z1, H = KL.cocycle_space(U, rels)
    d = len(H)
    B, h2 = KL.obstruction(U, rels, H)
    kb = KL.kernels_from_bimap(B, d, h2)
    leafsets = []
    for (spec, top) in zip(ins_specs, tops):
        L, bw, sizes, o, conj = spec
        level = top + len(conj)
        p, bundles = o, []
        for s in sizes:
            bundles.append(tuple(range(p, p + s))); p += s
        leafsets.append([KL.leaf_values(H, K["arc_at"], level, b) for b in bundles])
    T0 = None
    if T0fun:
        T0 = T0fun(H, K)
    kp, _ = KL.kernels_from_leaves(leafsets, d, T0)
    bad = sum(1 for a in kb if kb[a] != kp[a])
    return d, KL.count(kb), KL.count(kp), bad

random.seed(20261026)
BW = {"B": KL.BORR, "Bmir": [-1, 2] * 3, "Binv": [2, -1] * 3}
summary = []
t0 = time.time()
# figure-eight base (4_1)^#6, 13 strands, d = 6
base, n = KL.fig8_sum(6), 13
for trial in range(40):
    m = random.choice([1, 2, 2, 3, 3, 4])
    specs = []
    for _ in range(m):
        sizes = random.choice([[3, 3, 3], [3, 3, 3], [3, 3, 6], [3, 6, 3], [6, 3, 3]])
        tot = sum(sizes)
        o = random.randint(0, n - tot)
        L = random.randint(0, len(base))
        conj = [random.choice([1, -1]) * random.randint(1, n - 1) for _ in range(random.choice([0, 0, 2, 4]))]
        specs.append((L, BW[random.choice(list(BW))], sizes, o, conj))
    d, N, Np, bad = run(base, n, specs)
    summary.append((trial, m, d, N, Np, bad))
    print(f"fig8 trial {trial:2d}: insertions={m} d={d} N={N} predicted={Np} mismatching a={bad}", flush=True)
print("fig8 trials: all match:", all(s[5] == 0 and s[2] == 6 for s in summary), " distinct N values:", sorted({s[3] for s in summary}),
      f"({time.time() - t0:.0f}s)")

# trefoil + figure-eights base: 3_1 # (4_1)^#5 on 12 strands, d = 6; T0 = xi^3 with xi from the base bimap
base3 = [1, 1, 1] + [x + (1 if x > 0 else -1) for x in KL.fig8_sum(5)]
n3 = 12
U0, rels0, K0, _, _ = KL.presentation(base3, n3, 3)
Z0, H0 = KL.cocycle_space(U0, rels0)
B0, h20 = KL.obstruction(U0, rels0, H0)
xi0 = xi_from_base(B0, len(H0), h20)
top0 = [[h[K0["arc_at"][(0, q)]] for q in range(n3)] for h in H0]
# xi as a function of cocycle values on the top arcs: solve for a linear form on top-arc values reproducing xi on H0
# (top arcs carry the identification across insertions). Build: xi(h) = sum_q f_q h(top arc q); find f by solving.
rows = []
rhs = []
const = [KL.W] * n3
mat = top0 + [const]
target = list(xi0) + [0]
# solve f (length n3) with mat f = target  (augmented system)
aug = [row + [t] for row, t in zip(mat, target)]
R, piv = KL.rref(aug, n3 + 1)
assert n3 not in piv, "inconsistent"
f = [0] * n3
for r, pc in zip(R, piv):
    f[pc] = r[n3]
def T0fun(H, K):
    xs = []
    for h in H:
        s = 0
        for q in range(n3):
            s ^= KL.m4(f[q], h[K["arc_at"][(0, q)]])
        xs.append(s)
    d = len(H)
    return [[[KL.m4(KL.m4(xs[i], xs[j]), xs[k]) for k in range(d)] for j in range(d)] for i in range(d)]
d, N, Np, bad = run(base3, n3, [], T0fun)
print(f"trefoil base: d={d} N={N} predicted(xi^3)={Np} mismatching a={bad}")
summ3 = []
for trial in range(25):
    m = random.choice([1, 2, 3])
    specs = []
    for _ in range(m):
        sizes = random.choice([[3, 3, 3], [3, 3, 3], [3, 3, 6], [6, 3, 3]])
        o = random.randint(0, n3 - sum(sizes))
        L = random.randint(0, len(base3))
        conj = [random.choice([1, -1]) * random.randint(1, n3 - 1) for _ in range(random.choice([0, 2]))]
        specs.append((L, BW[random.choice(list(BW))], sizes, o, conj))
    d, N, Np, bad = run(base3, n3, specs, T0fun)
    summ3.append((trial, d, N, Np, bad))
    print(f"trefoil trial {trial:2d}: insertions={m} d={d} N={N} predicted={Np} mismatching a={bad}", flush=True)
    # control: drop T0
    if trial < 5:
        d2, N2, Np2, bad2 = run(base3, n3, specs, None)
        print(f"      control without T0: mismatching a={bad2}")
print("trefoil trials: all match:", all(s[4] == 0 and s[1] == 6 for s in summ3), " distinct N:", sorted({s[2] for s in summ3}),
      f"({time.time() - t0:.0f}s)")
