import sys, os, itertools
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
from bm import *
import mlib
d = "/home/jscul/p-vs-np-contact-first/proofs/COPRIME-CLASS2-20261026-001B/"; sys.path.insert(0, d + os.listdir(d)[0])
import cp_lib as C
p = 5
rng = np.random.default_rng(1)
F41 = ([1, -2, 1, -2], 3)
base, n = C.connected_sum([F41] * 4)
Mo = BraidModel(base, n, p)
print("dim Fix", len(Mo.Fix), "rank L2", np.linalg.matrix_rank(Mo.L2), "L3 shape", Mo.L3.shape)
# y(s) in the left kernel of L3?
Y = Mo.y_of(Mo.Fix)
print("y(Fix) annihilates L3:", not (Y @ Mo.L3 % p).any())
# Q0 on random samples
def rand_col(bs): return (rng.integers(0, p, (bs, len(Mo.Fix))) @ Mo.Fix) % p
bs = 64
cy, cx, cw, s = rand_col(bs), rand_col(bs), rand_col(bs), rand_col(bs)
o, _ = Mo.obstruction(cy, cx, cw)
Q = (o * Mo.y_of(s)).sum(axis=1) % p
print("base Q0 zero on 64 random samples:", not Q.any())
# insertion: exact formula with constant k
st = mlib.artin_conj(mlib.P4, 4)
M3 = [{k: v for k, v in mlib.magnus(st[j][0], 3, p).items() if len(k) == 3} for j in range(4)]
for (lev, off) in [(0, 0), (4, 1), (6, 0), (9, 1)]:
    w = base[:lev] + C.cable(mlib.P4, 2, offset=off) + base[lev:]
    Mn = BraidModel(w, n, p)
    # top colorings coincide (insertion below the top or at the top: Burau(cable) = I)
    assert ((Mn.Bur - Mo.Bur) % p == 0).all() if lev == 0 else True
    o2, kept = Mn.obstruction(cy, cx, cw, keep_levels=(lev,))
    # bundle functionals at the insertion level: transport colorings to level lev with the new word
    def transport(sv, upto):
        sv = sv.copy()
        for g in w[:upto]:
            i = abs(g) - 1
            a, b = sv[:, i].copy(), sv[:, i + 1].copy()
            if g > 0: sv[:, i], sv[:, i + 1] = (2 * a - b) % p, a
            else: sv[:, i], sv[:, i + 1] = b, (2 * b - a) % p
        return sv
    T = {nm: transport(v, lev) for nm, v in (("y", cy), ("x", cx), ("w", cw), ("s", s))}
    ell = lambda nm, k: (T[nm][:, off + 2 * k + 1] - T[nm][:, off + 2 * k]) % p
    pred = np.zeros(bs, dtype=np.int64)
    for j in range(4):
        Lam = np.zeros(bs, dtype=np.int64)
        for (i1, i2, i3), v in M3[j].items():
            Lam = (Lam + v * ell("y", i1) * ell("x", i2) * ell("w", i3)) % p
        pred = (pred + Lam * ell("s", j)) % p
    Q2 = (o2 * Mn.y_of(s)).sum(axis=1) % p
    ratios = {int(a * pow(int(b), p - 2, p) % p) for a, b in zip(Q2, pred) if b}
    print("insert", lev, off, ": Q nonzero", int((Q2 != 0).sum()), "/", bs, " Q/pred ratios", ratios,
          " Q zero where pred zero:", all(a == 0 for a, b in zip(Q2, pred) if b == 0))
