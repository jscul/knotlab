"""scoping: base terms of the four-way algebra at characters (alpha, alpha^-1, alpha^-1), alpha of order d > 2, on
S^3_(d/q)(sum of knots): local forms and cross-summand channels, slope q = 1 versus q = p"""
import sys, os, itertools
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cd")
d0 = "/home/jscul/p-vs-np-contact-first/proofs/COPRIME-CLASS2-20261026-001B/"; sys.path.insert(1, d0 + os.listdir(d0)[0])
import cp_lib as C
from lmc import LieAlgC, CyclicBraidModel

def fourway(p, d, zeta, e=1):
    return LieAlgC(p, d, zeta, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [e, -e, -e, 0, 0, -e],
                   {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}})

KN = {"3_1": ([1, 1, 1], 2), "4_1": ([1, -2, 1, -2], 3), "5_2": ([1, 1, 1, 2, -1, 2], 3), "6_1": ([1, 1, 2, -1, -3, 2, -3], 4),
      "5_1": ([1] * 5, 2), "7_1": ([1] * 7, 2)}
rng = np.random.default_rng(0)
for (p, d, zeta) in [(7, 3, 2), (7, 6, 3), (13, 3, 3), (13, 4, 5), (13, 6, 4), (11, 5, 3), (5, 4, 2)]:
    L = fourway(p, d, zeta)
    ix, iy, iw = (L.idx[s] for s in "xyw")
    for name, (w, n) in KN.items():
        for q in (1, p):
            Mo = CyclicBraidModel(w, n, L, q)
            dims = {c: len(Mo.cocycles[c]) for c in range(d)}
            if dims[1 % d] <= 1 or dims[(-1) % d] <= 1:      # needs a nontrivial class (Z1 = B1 + H1) at alpha and alpha^-1
                continue
            bs = 64
            def rc(c): return (rng.integers(0, p, (bs, len(Mo.cocycles[c]))) @ Mo.cocycles[c]) % p
            ok, ff, _ = Mo.solve({ix: rc(1), iy: rc(d - 1), iw: rc(d - 1)})
            print(f"p={p} d={d} {name} slope {d}/{q}: dim Z1 at alpha, alpha^-1 = {dims[1]}, {dims[d - 1]}; "
                  f"lift fraction {ok.mean():.2f}", flush=True)
