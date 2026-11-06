"""scoping (machinery timing): direct_count (BCH four-way group, Wirtinger presentation) on S^3_2 of small knots, and
fix_f1 completions for colorings transported from the braid model"""
import sys, os, time, glob
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
from bm import BraidModel
import mlib
sys.path.insert(0, glob.glob("/home/jscul/p-vs-np-contact-first/proofs/BEYOND-CLASS2-20261027-001A/*P001_*")[0])
import bc_lib as Bc
d = "/home/jscul/p-vs-np-contact-first/proofs/COPRIME-CLASS2-20261026-001B/"; sys.path.insert(0, d + os.listdir(d)[0])
import cp_lib as C
p = 5
L = Bc.four_way_algebra(p, 2, 1)
for name, (w, n) in {"T(2,5)": ([1] * 5, 2), "4_1": ([1, -2, 1, -2], 3)}.items():
    U, rels, arc = C.presentation(w, n, 2)
    t0 = time.time()
    cnt = Bc.direct_count(L, U, rels, 1)
    print(name, "direct_count sector 1:", cnt, "predicted p^8 =", p ** 8, "time %.1f" % (time.time() - t0), flush=True)
# transfer: arcs of the Wirtinger presentation carry the transported colors
def arc_values(word, n, top, p):
    U, rels, arc = C.presentation(word, n, 2)
    vals = [None] * U
    cur = top.copy()
    for l, g in enumerate(word):
        for q in range(n):
            a = arc[(l, q)]
            if vals[a] is None: vals[a] = int(cur[q])
            else: assert vals[a] == int(cur[q]), "arc color mismatch"
        i = abs(g) - 1
        a_, b_ = cur[i], cur[i + 1]
        if g > 0: cur[i], cur[i + 1] = (2 * a_ - b_) % p, a_
        else: cur[i], cur[i + 1] = b_, (2 * b_ - a_) % p
    return U, rels, vals
base, n = C.connected_sum([([1, -2, 1, -2], 3)] * 4)
w = C.cable(mlib.P4, 2, offset=0) + base
Mo = BraidModel(w, n, p)
rng = np.random.default_rng(3)
U, rels, _ = C.presentation(w, n, 2)
zx = Bc.z1(U, rels, p - 1, p)
print("Wirtinger arcs", U, "dim Z1", len(zx), "braid-model dim Fix", len(Mo.Fix))
agree = 0; tot = 0; lifts = 0
t0 = time.time()
for trial in range(12):
    cols = [(rng.integers(0, p, (1, len(Mo.Fix))) @ Mo.Fix) % p for _ in range(3)]
    if trial % 3 == 0: cols[0] = (cols[0] * 0 + Mo.Fix[0] * rng.integers(0, p)) % p     # some structured samples
    o, _ = Mo.obstruction(cols[0], cols[1], cols[2])
    Qzero = all(int((o * Mo.y_of(Mo.Fix[k:k + 1])).sum()) % p == 0 for k in range(len(Mo.Fix)))
    vy, vx, vw = (arc_values(w, n, c[0], p)[2] for c in cols)
    assert all(B in [] or True for B in ())
    ix, iy, iw = (L.idx[s] for s in "xyw")
    fix = {ix: vx, iy: vy, iw: vw}
    c = Bc.direct_count(L, U, rels, 1, fix_f1=fix)
    lifts += c > 0
    agree += (c > 0) == Qzero; tot += 1
print("fix_f1: agreement", agree, "/", tot, "lifting samples", lifts, "time %.1f" % (time.time() - t0))
