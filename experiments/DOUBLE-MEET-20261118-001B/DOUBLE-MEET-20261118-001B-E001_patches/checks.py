"""Gates for DOUBLE-MEET-20261118-001B-E001.   .venv/bin/python -B checks.py   (writes checks_output.json)"""
import itertools
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import weavelib as W  # noqa: E402

M, N = W.M, W.N
out = {}


def gate(name, ok, detail=""):
    out[name] = {"pass": bool(ok), "detail": detail}
    print("PASS" if ok else "FAIL", name, detail)


# G1: disc test on known shapes
gate("discs", W.is_disc({("u", 0, 0), ("d", 0, 0)}) and W.is_disc(W.parallelogram(3, 3)) and not W.is_disc({("u", 0, 0), ("u", 1, 1)})
     and len(W.all_discs(4)) == 2 + 3 + 6 + 14, "two knots, a parallelogram; two knots meeting at one distinction only is not a disc; 25 discs to four knots")
# G2: parallelogram builder and lone distinctions
T = W.parallelogram(3, 4)
V, ix, D, S, lone, _ = W.read(T)
gate("parallelogram", len(T) == 12 and sorted(lone) == [(0, 0), (2, 3)], "3 x 4 has 12 knots and two lone distinctions")
# G3: facing
gate("facing", W.facing((0, 0), ("u", 0, 0), (2, 3)) == (2, 3) and sorted(W.facing((2, 3), ("d", 1, 2), (0, 0))) == [2, 3]
     and W.facing((0, 0), ("u", 0, 0), (2, 0)) is None, "the parallelogram's lone distinctions face each other both ways")
# G4: the two-knot base: no bond holds the thirds; height distances give D + D = 3 steps
T2 = {("u", 0, 0), ("d", 0, 0)}
V, ix, D, S, lone, _ = W.read(T2)
DD = W.height_distances(T2)
gate("two-knot", D[ix[(0, 0)]][ix[(1, 1)]] == math.inf and all(DD[a][b] + DD[b][a] == 3 * S[ix[a]][ix[b]] for a, b in itertools.combinations(V, 2)),
     "lone double meeting; the identity on its pairs")
# G5: the tight-set criterion on the two-knot base reproduces its constrained sets
tight = W.tight_sets(V, DD)
st = M.states(len(V), [(N.NAE3, tuple(sorted(ix[v] for v in W.verts(t)))) for t in sorted(T2)])
free = M.free_table(len(V), st)
gate("criterion", all((any((m & mask) == m for m in tight)) == (not free[mask]) for mask in range(1 << len(V))), "all 16 sets")
json.dump(out, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in out.values()) else "SOME FAIL")
