import sys
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
from lp import *
p = 5
for name, (w, n) in {"4_1": ([1, -2, 1, -2], 3), "T(2,5)": ([1] * 5, 2), "T25#T25": ([1] * 5 + [2] * 5, 3)}.items():
    Mo = Model(w, n, 2, p)
    print(name, "U", Mo.U, "dim Z1", len(Mo.Z1), "dim H1", len(Mo.H))
    for var in range(4):
        print("   variant", var, "y(s) in left kernel for all s in Z1:", all(Mo.in_leftker(Mo.y_of(s, var)) for s in Mo.Z1))
    lk = B.nullspace([[Mo.Ab[t][g] for t in range(len(Mo.rels))] for g in range(Mo.U)], len(Mo.rels), p)
    print("   dim left kernel", len(lk), " surgery components of a basis:", [v[-1] for v in lk])
