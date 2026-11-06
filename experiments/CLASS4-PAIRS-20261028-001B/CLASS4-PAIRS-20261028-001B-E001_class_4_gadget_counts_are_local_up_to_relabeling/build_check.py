"""Construction-only check for CLASS4-PAIRS-20261028-001B-E001 (no measurement): every gadget of run.py builds, and every
cocycle space has dimension 1 + (number of blocks with a class there).  Run before the frozen run."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from c4_lib import *  # noqa: E402
T0 = time.time()
SHAPES = [("P3", 3, [(0, 1), (1, 2)]), ("skip", 3, [(0, 2)]), ("star", 4, [(0, 1), (0, 2), (0, 3)]),
          ("triangle", 3, [(0, 1), (0, 2), (1, 2)]), ("P3 reversed", 3, [(0, 2), (1, 2)]),
          ("C4", 4, [(0, 1), (1, 2), (2, 3), (0, 3)]), ("K4", 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])]
ok = True
for name, gens, slots, zj, shapes in [("K11", [1, 1], (1, 1, 2), True, SHAPES), ("K011", [0, 1, 1], (1, 1, 2), True, SHAPES),
                                      ("K111", [1, 1, 1], (1, 1, 2), True, SHAPES), ("X1 cumulative K11", [1, 1], (1, 1, 2), False, SHAPES[:4]),
                                      ("X2 K12", [1, 2], (1, 2, 3), True, [])]:
    C = Case(gens, slots, zero_jump=zj)
    for sname, nv, edges in [("K2", 2, [(0, 1)])] + shapes:
        G = Gadget(C.L, 5, 11, C.T, nv, edges, zero_jump=zj)
        good = all(len(fixed(G.word, G.n, pow(G.zeta, c, 11), 11)) == 1 + sum(1 for (bi, cc) in G.cls if cc == c) for c in range(1, 5))
        ok &= good
        print(name, sname, "strands", G.n, "crossings", len(G.word), "vars", len(G.var), "eqs", len(G.eqs), "cocycles ok", good, f"{time.time()-T0:.0f}s", flush=True)
print("BUILD OK" if ok else "BUILD FAILED")
