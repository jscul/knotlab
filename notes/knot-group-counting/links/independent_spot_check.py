"""Independent spot check (written separately from the scripts above): brute-force H_L(S3) on the braids of L(j) for Gamma = K2
(j = 0, 1) with my own S3 (permutations) and my own Hurwitz loop, and recompute linking numbers of L_Gamma by hand."""
import itertools, sys
import numpy as np
sys.path.insert(0, ".")
from potts_reduction import build_Lj, L_gamma, count_psi_parallel

S3 = list(itertools.permutations(range(3)))
ix = {g: i for i, g in enumerate(S3)}
MUL = np.array([[ix[tuple(a[b[k]] for k in range(3))] for b in S3] for a in S3])
INV = np.array([ix[tuple(sorted(range(3), key=lambda k: a[k]))] for a in S3])

def brute(word, n):
    tup = np.array(list(itertools.product(range(6), repeat=n)), dtype=np.int64)
    cur = tup.copy()
    for g in word:
        i = abs(g) - 1
        a, b = cur[:, i].copy(), cur[:, i + 1].copy()
        if g > 0:
            cur[:, i], cur[:, i + 1] = MUL[MUL[a, b], INV[a]], a
        else:
            cur[:, i], cur[:, i + 1] = b, MUL[MUL[INV[b], a], b]
    return int(np.all(cur == tup, axis=1).sum())

def linking(word, n):
    # strand ids follow positions; component = cycle of the closure permutation
    order = list(range(n)); cross = []
    for g in word:
        i = abs(g) - 1
        cross.append((order[i], order[i + 1], 1 if g > 0 else -1))
        order[i], order[i + 1] = order[i + 1], order[i]
    bottom = {sid: q for q, sid in enumerate(order)}
    comp, c = {}, 0
    for s in range(n):
        if s in comp: continue
        x = s
        while x not in comp:
            comp[x] = c; x = bottom[x]
        c += 1
    lk = np.zeros((c, c), dtype=int)
    for a, b, sg in cross:
        if comp[a] != comp[b]:
            lk[comp[a], comp[b]] += sg; lk[comp[b], comp[a]] += sg
    return lk // 2, comp

w, N = L_gamma(2, [(0, 1)])
print("L_Gamma for K2: strands", N, "linking matrix\n", linking(w, N)[0])
for j in (0, 1):
    wj, nj = build_Lj(2, [(0, 1)], j)
    b = brute(wj, nj)
    s = count_psi_parallel(wj, nj, procs=4)
    print(f"L({j}): strands {nj}, crossings {len(wj)}, brute force {b}, sector method {s}, equal {b == s}")
