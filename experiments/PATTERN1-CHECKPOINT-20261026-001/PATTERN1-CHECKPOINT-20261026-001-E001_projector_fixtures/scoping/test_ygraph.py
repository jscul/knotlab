import time
import numpy as np
import pc_core as PC
from pc_core import Comp, BraidLayout, Diagram, cohomology, obstruction_bimap, counts_from_bimaps, P, R, smith_diagonal
from pc_build import y_graph, leaf_bundle
import cp_lib as C

def full_counts(comps, label):
    t = time.time()
    D = Diagram(comps)
    rels = D.crossing_rels + D.framing_rels()
    U = len(D.gens)
    # H1 from the linking matrix with framings
    Lm = D.lk.copy()
    for i, c in enumerate(comps):
        Lm[i, i] = c.framing
    sd = smith_diagonal(Lm.tolist())
    H1, _, _ = cohomology(U, rels, D.psi, 3)
    H2, _, _ = cohomology(U, rels, D.psi, 2)
    H3, _, _ = cohomology(U, rels, D.psi, 6)
    B12 = obstruction_bimap(U, rels, D.psi, 3, 2, H1, H2)
    B13 = obstruction_bimap(U, rels, D.psi, 3, 6, H1, H3)
    B23 = obstruction_bimap(U, rels, D.psi, 2, 6, H2, H3)
    cnt = counts_from_bimaps(B12, B13, B23, len(H1), len(H2), len(H3))
    print(label, "crossings", len(D.crossings), "gens", U, "min|dz|", round(D.min_dz, 3), "SNF", [d for d in sd if d != 1],
          "dims", (len(H1), len(H2), len(H3)), cnt, round(time.time() - t, 1), "s", flush=True)
    return cnt

word0, n = C.connected_sum([PC.T31, PC.S61, PC.K52] * 3)
L = BraidLayout(word0, n, gaps={0: 6.0})
y_lo, y_hi = L.gap(0)
K = Comp("K", L.pts, 1, 6, "knot")
leaves, roots = [], []
for k, (lo, hi) in enumerate(((1, 6), (7, 12), (13, 18))):
    lf, root = leaf_bundle(f"A{k}", float(lo), float(hi), y_lo + 1.5 + 0.8 * k)
    leaves.append(lf); roots.append(root)
B = y_graph(0, (-12.0, y_lo + 2.0, 20.0), roots, 24.0)
cnt = full_counts([K] + leaves + B, "Y-graph link on bundles (expect free3 938791, H 18865)")
cnt0 = full_counts([K], "base knot alone (expect 7^9 = 40353607)")
