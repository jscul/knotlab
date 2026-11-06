"""scoping: cross-summand channels on 3_1 # 3_1 (p = 7, d = 6) and 6_1 # 6_1 (p = 7, d = 3): x and y on summand 1, w on summand 2
(channel only), versus x, y, w on one summand (local), slope d/1 versus d/p"""
import sys, os
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cd")
d0 = "/home/jscul/p-vs-np-contact-first/proofs/COPRIME-CLASS2-20261026-001B/"; sys.path.insert(1, d0 + os.listdir(d0)[0])
import cp_lib as C
from lmc import LieAlgC, CyclicBraidModel, nullspace_mod
from scope_c1 import fourway, KN

rng = np.random.default_rng(1)
for (p, d, zeta, kn) in [(7, 6, 3, "3_1"), (7, 3, 2, "6_1"), (11, 5, 3, "5_2")]:
    L = fourway(p, d, zeta)
    ix, iy, iw = (L.idx[s] for s in "xyw")
    base, n = C.connected_sum([KN[kn]] * 2)
    for q in (1, p):
        Mo = CyclicBraidModel(base, n, L, q)
        # split cocycles by summand: a class supported on summand k vanishes (up to coboundary) on the other summand's arcs;
        # build the projection using the top colours: summand blocks occupy strand ranges; use random classes and project
        Z = {c: Mo.cocycles[c] for c in (1, d - 1)}
        print(f"p={p} d={d} {kn}#{kn} slope {d}/{q}: dim Z1 alpha, alpha^-1 = {len(Z[1])}, {len(Z[d - 1])}", flush=True)
        # find, for each character, a basis adapted to summands: cocycles vanishing on summand-2 strands (positions >= n0)
        n1 = KN[kn][1]          # strands of the first summand block in cp_lib.connected_sum layout (0 .. n1-1)
        def adapted(c):
            B = Z[c]
            # coboundary = constant direction (all ones times (chi - 1)); classes: restrict to top colours
            on2 = B[:, n1:] - B[:, [n1 - 1]]          # variation on summand 2 relative to the shared strand
            on1 = B[:, :n1] - B[:, [n1 - 1]]
            k1 = nullspace_mod(on2.T, p)              # combos with no variation on summand 2
            k2 = nullspace_mod(on1.T, p)
            return (k1 @ B) % p, (k2 @ B) % p
        A1, A2 = {}, {}
        for c in (1, d - 1):
            A1[c], A2[c] = adapted(c)
        bs = 64
        def rc(Bm): return (rng.integers(0, p, (bs, len(Bm))) @ Bm) % p
        tests = {"x,y,w on summand 1 (local)": (A1[1], A1[d - 1], A1[d - 1]),
                 "x,y on 1, w on 2 (z-channel)": (A1[1], A1[d - 1], A2[d - 1]),
                 "x on 1, y,w on 2 (no common pair)": (A1[1], A2[d - 1], A2[d - 1]),
                 "x,w on 1, y on 2 (u-channel)": (A1[1], A2[d - 1], A1[d - 1])}
        for tname, (bx, by, bw) in tests.items():
            ok, _, _ = Mo.solve({ix: rc(bx), iy: rc(by), iw: rc(bw)})
            print(f"    {tname}: lift fraction {ok.mean():.2f}", flush=True)
