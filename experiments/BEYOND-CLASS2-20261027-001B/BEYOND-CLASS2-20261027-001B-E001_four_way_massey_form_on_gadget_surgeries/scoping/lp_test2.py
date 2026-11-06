import sys, os, itertools, random
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
from lp import *
import mlib
d = "/home/jscul/p-vs-np-contact-first/proofs/COPRIME-CLASS2-20261026-001B/"; sys.path.insert(0, d + os.listdir(d)[0])
import cp_lib as C

def Qtable(Mo, classes):
    """Q[(iw, ix, iy, is)] = <o(c_y = H[iy], c_x = H[ix], c_w = H[iw]), y(H[is])>"""
    p = Mo.p
    ys = [Mo.y_of(s) for s in classes]
    T = {}
    for iw, ix, iy in itertools.product(range(len(classes)), repeat=3):
        o = Mo.obstruction(classes[iy], classes[ix], classes[iw])
        for i_s, y in enumerate(ys):
            T[(iw, ix, iy, i_s)] = sum(a * b for a, b in zip(o, y)) % p
    return T

def matched(Mnew, Mold, classes_old):
    """new cocycles with the same level-0 values as the old ones"""
    p, n = Mold.p, Mold.n
    rows = [[z[Mnew.gen(0, q)] for q in range(n)] for z in Mnew.Z1]
    out = []
    for s in classes_old:
        target = [s[Mold.gen(0, q)] for q in range(n)]
        sol = B.solve_affine([list(col) for col in zip(*rows)], target, p)
        assert sol is not None
        coef = sol[0]
        out.append([sum(c * z[g] for c, z in zip(coef, Mnew.Z1)) % p for g in range(Mnew.U)])
    return out

p = 5
F41 = ([1, -2, 1, -2], 3)
for nsum in (1, 2, 3):
    base, n = C.connected_sum([F41] * nsum)
    Mo = Model(base, n, 2, p)
    T = Qtable(Mo, Mo.H)
    print("base 4_1 x%d: dim V" % nsum, len(Mo.H), " Q0 identically zero:", all(v == 0 for v in T.values()), flush=True)
for nsum in (1, 2, 3):
    base = sum(([k + 1] * 5 for k in range(nsum)), [])
    Mo = Model(base, nsum + 1, 2, p)
    T = Qtable(Mo, Mo.H)
    print("base T(2,5) x%d: dim V" % nsum, len(Mo.H), " Q0 identically zero:", all(v == 0 for v in T.values()), flush=True)

# insertion test on 4 summands of 4_1 (9 strands)
st = mlib.artin_conj(mlib.P4, 4)
M3 = []
for j in range(4):
    Mg = mlib.magnus(st[j][0], 3, p)
    M3.append({k: v for k, v in Mg.items() if len(k) == 3})
base, n = C.connected_sum([F41] * 4)
Mold = Model(base, n, 2, p)
H = Mold.H
Told = Qtable(Mold, H)
for (lev, off) in [(0, 0), (4, 1), (6, 0)]:
    cab = C.cable(mlib.P4, 2, offset=off)
    w = base[:lev] + cab + base[lev:]
    Mnew = Model(w, n, 2, p)
    Hn = matched(Mnew, Mold, H)
    Tnew = Qtable(Mnew, Hn)
    # bundle functionals at the insertion level (top of the cable) in the new model
    def ell(c, k): return (c[Mnew.gen(lev, off + 2 * k + 1)] - c[Mnew.gen(lev, off + 2 * k)]) % p
    d = len(H)
    pred = {}
    for iw, ix, iy, i_s in itertools.product(range(d), repeat=4):
        tot = 0
        for j in range(4):
            Lam = sum(v * ell(Hn[iy], k[0]) * ell(Hn[ix], k[1]) * ell(Hn[iw], k[2]) for k, v in M3[j].items())
            tot += Lam * ell(Hn[i_s], j)
        pred[(iw, ix, iy, i_s)] = tot % p
    diff = {k: (Tnew[k] - Told[k]) % p for k in Told}
    ratios = {(diff[k] * pow(pred[k], p - 2, p)) % p for k in diff if pred[k]}
    print("insert lev", lev, "off", off, ": nonzero diffs", sum(1 for v in diff.values() if v), "nonzero preds",
          sum(1 for v in pred.values() if v), " diff/pred ratios", ratios,
          " diff zero where pred zero:", all(diff[k] == 0 for k in diff if pred[k] == 0), flush=True)
