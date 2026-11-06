"""post-hoc diagnostic: on-variety locality for A1 on the cumulative and the zero-jump designs"""
import sys, itertools, time
sys.path.insert(0, "/home/jscul/p-vs-np-contact-first/experiments/COPRIME-PAIRS-20261027-001D/COPRIME-PAIRS-20261027-001D-E001_interacting_pairs_on_zero_jump_gadgets")
from pf_lib import *
t0 = time.time()
p, d = 11, 5
L = free_graded(p, d, [1, 1], 3)
T = summand_types(p, d, (1, 1, 2))
for zj in (False, True):
    K2 = Gadget(L, d, p, T, 2, [(0, 1)], zero_jump=zj)
    P3 = Gadget(L, d, p, T, 3, [(0, 1), (1, 2)], zero_jump=zj)
    vs = P3.var_sites(); eqs = P3.eq_sites()
    i0 = [j for j, s in enumerate(vs) if s == ("e", 0)]; i1 = [j for j, s in enumerate(vs) if s == ("e", 1)]
    v0 = [j for j, s in enumerate(vs) if s == ("v", 0)]; v1 = [j for j, s in enumerate(vs) if s == ("v", 1)]; v2 = [j for j, s in enumerate(vs) if s == ("v", 2)]
    c_e0 = [c for c, s in enumerate(eqs) if s == ("e", 0)]; c_e1 = [c for c, s in enumerate(eqs) if s == ("e", 1)]
    combos = np.array(list(itertools.product(range(p), repeat=len(i0))), dtype=np.int64)
    rng = np.random.default_rng(5)
    cmp_, mism, e1nonzero = 0, 0, 0
    for trial in range(6):
        s1, s2 = rng.integers(0, p, len(v1)), rng.integers(0, p, len(v2))
        _, _, _, S1 = edge_count(K2, s1, s2)
        if len(S1) == 0: continue
        pi1 = S1[rng.integers(0, len(S1))]
        for k in range(2):
            s0 = rng.integers(0, p, len(v0))
            vals = np.zeros((len(combos), len(P3.var)), dtype=np.int64)
            vals[:, i0] = combos; vals[:, v0] = s0; vals[:, v1] = s1; vals[:, v2] = s2; vals[:, i1] = pi1
            E = evaluate_chunked(P3, vals) % p
            sol = ~E[:, c_e0].any(axis=1)
            _, _, _, S0 = edge_count(K2, s0, s1)
            same = set(map(tuple, S0.tolist())) == set(map(tuple, combos[sol].tolist()))
            cmp_ += 1; mism += int(not same)
            e1nonzero += int(E[sol][:, c_e1].any(axis=1).sum())
    print("zero-jump" if zj else "cumulative", "comparisons", cmp_, "mismatches", mism, "e1 equations nonzero on e0 solutions", e1nonzero, f"{time.time()-t0:.0f}s", flush=True)
