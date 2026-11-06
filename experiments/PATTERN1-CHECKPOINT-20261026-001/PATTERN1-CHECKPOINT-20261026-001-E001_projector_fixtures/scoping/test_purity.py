import time
import numpy as np
import pc_core as PC
from pc_core import Comp, P
from pc_fixtures import Base, choose_arcs, leaf_functionals, CHI, leaf_height
from pc_build import leaf_simple, leaf_projector, leaf_band_sum

WDIR = -1
slots = ["x", "x", "y", "t"]
base = Base(slots, {0: 2, 1: 2, 2: 2, 3: 2})       # room for one projector leaf and one reference copy each
base.gap_choice = choose_arcs(base)
L = base.layout()
K = Comp("K", L.pts, 1, 6, "knot")
(ku, qu), (kv, qv), (ky, qy), (kt, qt) = (base.gap_choice[i] for i in range(4))
top = lambda k: L.gap(k)[1] - 1.0
t0 = time.time()
lf_l, _, _ = leaf_band_sum("ell", float(qu), top(ku), float(qv), top(kv), CHI["x"], WDIR, 6.0)
lf_y, _, _ = leaf_projector("y", float(qy), top(ky), CHI["y"], WDIR)
lf_t, _, _ = leaf_projector("t", float(qt), top(kt), CHI["t"], WDIR)
refs = []
for name, (k, q), s in (("ref_u", (ku, qu), "x"), ("ref_v", (kv, qv), "x"), ("ref_y", (ky, qy), "y"), ("ref_t", (kt, qt), "t")):
    lo, hi = L.gap(k)
    lf, _ = leaf_simple(name, float(q), lo + 1.0)
    refs.append(lf)
F, D = leaf_functionals(K, [lf_l, lf_y, lf_t] + refs)
print("crossings", len(D.crossings), "generators", len(D.gens), "min|dz|", round(D.min_dz, 3), round(time.time() - t0, 1), "s")
for chi in (3, 2, 6, 4, 5):
    print("chi", chi, {k: v for k, v in F[chi].items()})
f = lambda chi, n: np.array(F[chi][n]) % P
print("ell = ref_u - ref_v on V_3:", bool(np.all((f(3, "ell") - (f(3, "ref_u") - f(3, "ref_v"))) % P == 0)))
print("y = ref_y on V_2:", bool(np.all((f(2, "y") - f(2, "ref_y")) % P == 0)), " t = ref_t on V_6:", bool(np.all((f(6, "t") - f(6, "ref_t")) % P == 0)))
