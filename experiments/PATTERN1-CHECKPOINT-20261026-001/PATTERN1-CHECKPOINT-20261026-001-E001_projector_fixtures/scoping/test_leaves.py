import time
import numpy as np
import pc_core as PC
from pc_core import Comp, BraidLayout, P
from pc_fixtures import Base, choose_arcs, leaf_functionals, CHI
from pc_build import leaf_simple, projector_leaf, multiplicities
from pc_core import copy_loop, tooth_centerline, dedupe, EPS, XSP, XRAIL

slots = ["x", "x", "y", "t"]
base = Base(slots, {0: 1, 1: 1, 2: 1, 3: 1})
t = time.time()
base.gap_choice = choose_arcs(base)
print("arc choice (summand -> (gap k, position q))", base.gap_choice, round(time.time() - t, 1), "s")
L = base.layout()
K = Comp("K", L.pts, 1, 6, "knot")

def one_copy_leaf(name, xa, ytop, j, wdir):
    """root, spine, a single tooth with j windings, the copy, rail (a comb with one copy)"""
    m = [0] * 6
    m[j] = 1
    pts, ybot, info = projector_leaf(xa, ytop, m, wdir)
    return Comp(name, pts, 0, 0, "leaf")

# T1/T2: functionals of a single copy with j = 0, 1, 2 windings, both directions, on summand 0 (trefoil, chi = 3)
k, q = base.gap_choice[0]
lo, hi = L.gap(k)
leaves = [one_copy_leaf(f"j{j}d{d}", float(q), hi - 1.0 - 4.0 * idx, j, d)
          for idx, (j, d) in enumerate([(0, 1), (1, 1), (1, -1), (2, 1), (2, -1)])]
F, D = leaf_functionals(K, leaves)
for chi in (3, 5):
    f0 = F[chi]["j0d1"]
    print("chi", chi, "copy j=0:", f0)
    for name in ("j1d1", "j1d-1", "j2d1", "j2d-1"):
        f = F[chi][name]
        ratio = None
        for e in range(6):
            if all((pow(chi, e, P) * a - b) % P == 0 for a, b in zip(f0, f)):
                ratio = e
        print("   ", name, f, "= chi^%s x (j=0 copy)" % ratio)
