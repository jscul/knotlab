"""Construction-only check for COPRIME-PAIRS-20261027-001D-E001 (no measurement): every gadget of run.py builds, every insertion
fits, closures are knots, and machinery checks M1-M3 pass.  Run before the frozen run."""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pf_lib import *  # noqa: E402
T0 = time.time()
CASES = [("A1", 11, 5, [1, 1], 3, (1, 1, 2)), ("A2", 11, 5, [1, 2], 3, (1, 2, 3)), ("A3", 11, 5, [0, 1], 4, (1, 1, 2)),
         ("A4", 5, 4, [1, 2, 2], 3, (2, 1, 3)), ("A5", 5, 4, [1, 2], 3, (2, 1, 3)), ("X2", 11, 5, [1, 1], 3, (1, 1, 1))]
ok = True
for (name, p, d, gens, cls, slots) in CASES:
    L = free_graded(p, d, gens, cls)
    T = summand_types(p, d, slots)
    for nv, edges, zj in [(2, [(0, 1)], True), (3, [(0, 1), (1, 2)], True)] + ([(2, [(0, 1)], False), (3, [(0, 1), (1, 2)], False)] if name == "A1" else []):
        G = Gadget(L, d, p, T, nv, edges, zero_jump=zj)
        braid_meta(G.word, G.n)
        good = True
        for c in range(1, d):
            want = 1 + sum(1 for (bi, cc) in G.cls if cc == c)
            good &= len(fixed(G.word, G.n, pow(G.zeta, c, p), p)) == want
        ok &= good
        print(name, nv, "zero-jump" if zj else "plain", "strands", G.n, "crossings", len(G.word), "vars", len(G.var), "eqs", len(G.eqs),
              "cocycle dimensions ok", good, f"{time.time() - T0:.0f}s", flush=True)
print("BUILD OK" if ok else "BUILD FAILED")
