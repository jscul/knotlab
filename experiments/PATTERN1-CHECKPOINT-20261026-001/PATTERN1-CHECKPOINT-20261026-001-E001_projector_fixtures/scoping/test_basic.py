import time, itertools
import numpy as np
import pc_core as PC
from pc_core import Comp, BraidLayout, Diagram, cohomology, obstruction_bimap, counts_from_bimaps, P, R
import cp_lib as C

def knot_comp(word, n, framing, gaps=None):
    L = BraidLayout(word, n, gaps)
    assert L.is_knot
    return L, Comp("K", L.pts, 1, framing, "knot")

# 1. same presentation data as cp_lib for braid knots: cohomology dims and Heisenberg kernel counts
for name, (word, n) in {"3_1": PC.T31, "4_1": ([1, -2, 1, -2], 3), "5_2": PC.K52, "6_1": PC.S61}.items():
    L, K = knot_comp(word, n, 6)
    D = Diagram([K])
    rels = D.crossing_rels + D.framing_rels()
    U = len(D.gens)
    Uc, relc, _ = C.presentation(word, n, 6)
    for chi in (3, 2, 6, 4, 5):
        H, z, b = cohomology(U, rels, D.psi, chi)
        Hc, zc, bc = C.cohomology(Uc, relc, chi, 1, P)
        assert len(H) == len(Hc), (name, chi, len(H), len(Hc))
    print(name, "crossings", len(D.crossings), "gens", U, "writhe", D.writhe, "dims ok")
t = time.time()
# 2. a big braid: cp_lib's pattern-1 insertion knot; compare N_free3 with lane A's 938791 (insertion [(1, 1)])
word0, n = C.connected_sum([PC.T31, PC.S61, PC.K52] * 3)
for ins, expect in (([(1, 1)], 938791), ([(1, 1), (18, 1)], 49735)):
    w, tops = C.insert_at(word0, ins, R)
    L, K = knot_comp(w, n, 6)
    D = Diagram([K])
    rels = D.crossing_rels + D.framing_rels()
    U = len(D.gens)
    H1, _, _ = cohomology(U, rels, D.psi, 3)
    H2, _, _ = cohomology(U, rels, D.psi, 2)
    H3, _, _ = cohomology(U, rels, D.psi, 6)
    B12 = obstruction_bimap(U, rels, D.psi, 3, 2, H1, H2)
    B13 = obstruction_bimap(U, rels, D.psi, 3, 6, H1, H3)
    B23 = obstruction_bimap(U, rels, D.psi, 2, 6, H2, H3)
    cnt = counts_from_bimaps(B12, B13, B23, len(H1), len(H2), len(H3))
    print(ins, "gens", U, "dims", (len(H1), len(H2), len(H3)), cnt, "expected free3", expect, "ok" if cnt["free3"] == expect else "MISMATCH", round(time.time() - t, 1), "s")
