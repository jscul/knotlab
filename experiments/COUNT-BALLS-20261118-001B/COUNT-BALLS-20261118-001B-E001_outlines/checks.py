"""Gates for COUNT-BALLS-20261118-001B-E001 (run before the freeze; each prints PASS or FAIL)."""
import itertools
import json
import math
import sys
from pathlib import Path

import mpmath as mp
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import census as G  # noqa: E402
import chain as C  # noqa: E402
import outline as O  # noqa: E402
import weave as W  # noqa: E402

results = {}


def gate(name, ok, detail=""):
    results[name] = {"pass": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""), flush=True)


# ---- weave ----
p = [float(W.kinv(*d)) for d in ((0, 0), (0, -1), (-1, 0))]
gate("W-edge-probabilities", all(abs(x - 1 / 3) < 1e-15 for x in p), str(p))
dev = max(abs(float(W.kinv(a, b)) - W.kinv_quad(a, b)) for a, b in ((0, 1), (1, 0), (3, 2), (-2, 5), (7, 1), (0, 9), (2, 3)))
gate("W-kernel-exact-vs-quadrature", dev < 1e-9, f"max deviation {dev:.1e}")
gate("W-nearest", abs(float(W.corr(W.walk([W.E]))) + 1 / 3) < 1e-20)
pi_dev = []
for target, alt in (((1, 1), [W.N, W.E]), ((2, 0), [W.N, W.SE, W.E]), ((3, 0), [W.N, W.E, W.E, W.SE]),
                    ((2, 2), [W.N, W.N, W.E, W.E]), ((4, -1), [W.E, W.SE, W.E, W.E])):
    a = W.corr(W.walk(W.steps_to(*target)))
    b = W.corr(W.walk(alt))
    assert W.walk(alt)[-1] == target
    pi_dev.append(float(abs(a - b)))
gate("W-path-independence", max(pi_dev) < 1e-30, f"max {max(pi_dev):.1e}")
td = max(float(abs(W.corr(W.walk([W.E] * r)) - W.row_toeplitz(r))) for r in range(1, 13))
gate("W-row-dimer-equals-row-Toeplitz", td < 1e-40, f"max {td:.1e} over r = 1..12")
fd = 0.0
for t in [(1, 1), (3, 0), (-2, 5), (4, -7), (-3, -3), (5, 2), (6, 3), (-8, 1), (0, 9), (7, -2)]:
    path = W.walk(W.steps_to(*t))
    fd = max(fd, abs(W.corr_float(path) - float(W.corr(path))))
gate("W-float-equals-mp", fd < 1e-10, f"max {fd:.1e}")
# mutant: a wrong pair map (swapping two kinds of co-knotted pair) must break path independence
orig = W.edge
def wrong(p, q):
    w, b = orig(p, q)
    d = (q[0] - p[0], q[1] - p[1])
    if d in ((1, 0), (-1, 0)):
        return w, (b[0] - 1, b[1] + 1)
    return w, b
W.edge = wrong
mut = abs(float(W.corr(W.walk([W.E, W.N])) - W.corr(W.walk([W.N, W.E]))))
W.edge = orig
gate("W-mutant-detected", mut > 1e-3, f"mutant path disagreement {mut:.3f}")
# finite weaves of L x L (exact row transfer), approaching the endless values
def torus_corr(L, targets):
    S = 1 << L
    bits = [[(s >> i) & 1 for i in range(L)] for s in range(S)]
    T = np.zeros((S, S), dtype=object)
    for r in range(S):
        a = bits[r]
        for s in range(S):
            b = bits[s]
            ok = True
            for i in range(L):
                i1 = (i + 1) % L
                if (a[i] == a[i1] == b[i]) or (a[i1] == b[i] == b[i1]):
                    ok = False
                    break
            if ok:
                T[r, s] = 1
    P = [np.identity(S, dtype=object)]
    for _ in range(L):
        P.append(P[-1].dot(T))
    Z = sum(P[L][i, i] for i in range(S))
    out = {}
    for (pp, q) in targets:
        D0 = np.diag([1 - 2 * bits[s][0] for s in range(S)]).astype(object)
        Dp = np.diag([1 - 2 * bits[s][pp % L] for s in range(S)]).astype(object)
        M = D0.dot(P[q]).dot(Dp).dot(P[L - q])
        out[(pp, q)] = float(mp.mpf(int(sum(M[i, i] for i in range(S)))) / int(Z))
    return out
tg = [(1, 1), (3, 0), (2, 2), (2, 0)]
t6, t9 = torus_corr(6, tg), torus_corr(9, tg)
inf = {t: float(W.corr(W.walk(W.steps_to(*t)))) for t in tg}
mono = all(abs(t9[t] - inf[t]) < abs(t6[t] - inf[t]) for t in tg)
gate("W-finite-weaves-approach", mono, json.dumps({str(t): [round(t6[t], 6), round(t9[t], 6), round(inf[t], 6)] for t in tg}))

# ---- chain grids ----
for l in (1, 2, 3):
    cells, links = C.patch(2, 2)
    gate(f"C-reduction-2x2-l{l}", C.literal_counts(cells, links, l) == C.reduced_counts(cells, links, l))
cells, links = C.patch(3, 3)
lit = C.literal_counts(cells, links, 1)
gate("C-reduction-3x3-open-l1", lit == C.reduced_counts(cells, links, 1))
Nn, D = lit
sg = all(((1 - 2 * D[(i, j)] / Nn) * (-1) ** (abs(cells[i][0] - cells[j][0]) + abs(cells[i][1] - cells[j][1]))) > 0
         for i, j in itertools.combinations(range(len(cells)), 2))
gate("C-two-classes-open-l1", sg, "sign of 1 - 2d/N is (-1)^(steps apart) on every pair of grid distinctions")
cells, links = C.torus(3)
gate("C-reduction-3x3-wrapped-l1", C.literal_counts(cells, links, 1) == C.reduced_counts(cells, links, 1),
     "frustrated wrap, compared at tanh = -1/3 directly")
# loose distinction identity C(x, c) = -[C(x, a) + C(x, b)]/2 for the loose c of knot (a, b, c), on the literal open 3 x 3
names, knots = C.chain_grid_base(*C.patch(3, 3), 1)
idx = {z: i for i, z in enumerate(names)}
n = len(names)
s = np.arange(1 << n, dtype=np.uint64)
ok = np.ones(len(s), dtype=bool)
for a, b, c in knots:
    x, y, z = [(s >> np.uint64(idx[v])) & np.uint64(1) for v in (a, b, c)]
    ok &= ~((x == y) & (y == z))
s = s[ok]
spin = lambda v: 1.0 - 2.0 * ((s >> np.uint64(idx[v])) & np.uint64(1)).astype(float)
x0 = spin((0, 0))
devs = []
for a, b, c in knots:
    lhs = float(np.mean(x0 * spin(c)))
    rhs = -(float(np.mean(x0 * spin(a))) + float(np.mean(x0 * spin(b)))) / 2
    devs.append(abs(lhs - rhs))
gate("C-loose-identity", max(devs) < 1e-12, f"max {max(devs):.1e} over {len(knots)} loose distinctions")
# mutant: wrong pair weights must disagree with the literal counts
cells, links = C.patch(2, 2)
orig_w = C.pair_weights
C.pair_weights = lambda l: (1, 3)
mut = C.literal_counts(cells, links, 1) != C.reduced_counts(cells, links, 1)
C.pair_weights = orig_w
gate("C-mutant-detected", mut)
# Kac-Ward against brute force on a 4 x 4 free patch (finite version of the same formula)
def kw_box(Wd, H, wt):
    edges = [((x, y), d) for x in range(Wd) for y in range(H) for d, (dx, dy) in enumerate(C.DIRS)
             if 0 <= x + dx < Wd and 0 <= y + dy < H]
    ix = {e: i for i, e in enumerate(edges)}
    L = np.zeros((len(edges), len(edges)), dtype=complex)
    for (pp, d), i in ix.items():
        q = (pp[0] + C.DIRS[d][0], pp[1] + C.DIRS[d][1])
        for d2 in range(4):
            if d2 != (d + 2) % 4 and (q, d2) in ix:
                r = (q[0] + C.DIRS[d2][0], q[1] + C.DIRS[d2][1])
                L[i, ix[(q, d2)]] = wt(q, r) * np.exp(1j * C.TURN[(d2 - d) % 4] / 2)
    return np.linalg.det(np.eye(len(edges)) - L)
t = 1 / 3
base = kw_box(4, 4, lambda u, v: t)
def kw_corr(path):
    pe = {frozenset(e) for e in zip(path, path[1:])}
    r = kw_box(4, 4, lambda u, v: (1 / t) if frozenset((u, v)) in pe else t) / base
    return (t ** len(pe) * np.sqrt(r)).real
sites = [(x, y) for x in range(4) for y in range(4)]
bonds = [((x, y), (x + 1, y)) for x in range(3) for y in range(4)] + [((x, y), (x, y + 1)) for x in range(4) for y in range(3)]
K = math.atanh(t)
Zb, Cb = 0.0, {}
targets = {((0, 0), (1, 0)): [(0, 0), (1, 0)], ((0, 0), (2, 1)): [(0, 0), (1, 0), (2, 0), (2, 1)],
           ((1, 1), (3, 3)): [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)]}
acc = {k: 0.0 for k in targets}
for conf in itertools.product((1, -1), repeat=16):
    sv = dict(zip(sites, conf))
    w = math.exp(K * sum(sv[a] * sv[b] for a, b in bonds))
    Zb += w
    for (a, b) in targets:
        acc[(a, b)] += w * sv[a] * sv[b]
kd = max(abs(kw_corr(pth) - acc[k] / Zb) for k, pth in targets.items())
gate("C-KacWard-vs-brute-4x4", kd < 1e-12, f"max {kd:.1e}")
for l in (1, 2, 3):
    tt = 3.0 ** -l
    R = C.Resolvent(tt)
    nn = C.corr_reweight(R, tt, C.path([(1, 0)]))
    gate(f"C-Onsager-nearest-l{l}", abs(nn - C.onsager_nn(tt)) < 1e-12, f"{nn:.15f} vs {C.onsager_nn(tt):.15f}")
R = C.Resolvent(1 / 3)
a1 = C.corr_reweight(R, 1 / 3, C.path([(1, 0), (1, 0), (0, 1)]))
a2 = C.corr_reweight(R, 1 / 3, C.path([(0, 1), (1, 0), (1, 0)]))
gate("C-path-independence", abs(a1 - a2) < 1e-14, f"{a1:.15f} {a2:.15f}")

# ---- outline (Golab) ----
gate("O-golab-circle", abs(O.golab_pi(lambda a: 1.0) - math.pi) < 1e-6)
gate("O-golab-taxicab", abs(O.golab_pi(lambda a: abs(math.cos(a)) + abs(math.sin(a))) - 4) < 1e-6)
gate("O-golab-hexagon", abs(O.golab_pi(lambda a: max(abs(math.cos(a - k * math.pi / 3)) for k in range(3))) - 3) < 1e-6)

# ---- census ----
import random
rng = random.Random(7)
bad = 0
for _ in range(60):
    n = rng.randint(4, 6)
    full = (1 << n) - 1
    sp = sorted({min(m, full ^ m) for m in (rng.randrange(1, full) for _ in range(rng.randint(1, 5)))})
    if G.R.lattice_dimension(sp, full) != G.R.lattice_dimension_brute(sp, full):
        bad += 1
gate("G-lattice-dimension-vs-brute", bad == 0, f"{bad} of 60 random split systems disagree")
pts, (st, n) = G.box((7, 7))
gate("G-box-layers", list(G.layers(st, n, pts.index((3, 3))).values())[:3] == [4, 8, 12])
m = 10
lad = G.layers(*G.box((2, m))[1], G.box((2, m))[0].index((0, 5)))
edges = [(i, i + 1) for i in range(m - 1)] + [(i, m + i - 1) for i in range(1, m - 1)]
pts, (st, n) = G.tree(edges, 2 * m - 2)
comb = G.layers(st, n, 5)
gate("G-ladder-and-comb-layers", [lad[c] for c in (4, 6, 8)] == [4, 4, 4] == [comb[c] for c in (4, 6, 8)],
     f"ladder {lad}, comb {comb}")

json.dump(results, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in results.values()) else "SOME FAIL")
