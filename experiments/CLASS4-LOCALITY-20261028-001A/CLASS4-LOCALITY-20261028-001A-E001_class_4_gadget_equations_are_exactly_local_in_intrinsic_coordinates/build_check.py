"""Construction-only check for CLASS4-LOCALITY-20261028-001A-E001 (no measurement): every gadget of run.py builds, every cocycle
space has dimension 1 + (number of blocks with a class there), and every block carrying layer-3 data has a base strand where its
class colouring vanishes and a reading strand where it does not.  Run before the frozen run."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from l4_lib import *  # noqa: E402
T0 = time.time()
SHAPES = [("P3", 3, [(0, 1), (1, 2)]), ("skip", 3, [(0, 2)]), ("star", 4, [(0, 1), (0, 2), (0, 3)]),
          ("triangle", 3, [(0, 1), (0, 2), (1, 2)]), ("P3 reversed", 3, [(0, 2), (1, 2)]),
          ("C4", 4, [(0, 1), (1, 2), (2, 3), (0, 3)]), ("K4", 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])]
ok = True
for name, gens, slots, shapes in [("K11", [1, 1], (1, 1, 2), SHAPES), ("K011", [0, 1, 1], (1, 1, 2), SHAPES),
                                  ("K111", [1, 1, 1], (1, 1, 2), SHAPES), ("XA", [0, 1, 2], (1, 2, 3), SHAPES[:5]),
                                  ("XB", [1, 2], (2, 1, 3), SHAPES[:5])]:
    C = IntrinsicCase(gens, slots)
    for sname, nv, edges in [("K2", 2, [(0, 1)])] + shapes:
        G = Gadget(C.L, 5, 11, C.T, nv, edges)
        good = all(len(fixed(G.word, G.n, pow(G.zeta, c, 11), 11)) == 1 + sum(1 for (bi, cc) in G.cls if cc == c) for c in range(1, 5))
        top = int(C.L.layer.max())
        for (bi, k) in [G.var[j] for j in range(len(G.var)) if int(C.L.layer[G.var[j][1]]) == top - 1]:
            base, read = block_pos(G, bi)
            cv = G.cls[(bi, int(C.L.chars[k]) % 5)]
            good &= bool(cv[base] % 11 == 0 and cv[read] % 11)
        ok &= good
        print(name, sname, "strands", G.n, "crossings", len(G.word), "vars", len(G.var), "eqs", len(G.eqs), "ok", good,
              f"{time.time() - T0:.0f}s", flush=True)
print("BUILD OK" if ok else "BUILD FAILED")
