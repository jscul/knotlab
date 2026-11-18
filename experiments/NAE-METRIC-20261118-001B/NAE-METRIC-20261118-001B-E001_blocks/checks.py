"""Gates for NAE-METRIC-20261118-001B-E001.   .venv/bin/python -B checks.py   (writes checks_output.json)"""
import itertools
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import naelib as N  # noqa: E402

M, nx, np = N.M, N.nx, N.np
out = {}


def gate(name, ok, detail=""):
    out[name] = {"pass": bool(ok), "detail": detail}
    print("PASS" if ok else "FAIL", name, detail)


rng = random.Random(11)
# G1: the triple criterion for complement-closed state sets with both constants, against the brute-force bond matrix
bad = tot = 0
for _ in range(200):
    n = rng.randint(4, 9)
    full = (1 << n) - 1
    S = {0, full}
    for _ in range(rng.randint(1, 8)):
        a = rng.randrange(1, full)
        S |= {a, full ^ a}
    S = sorted(S)
    D = M.bond_matrix(n, np.array(S, dtype=np.int64))
    for (x, y), v in N.split_b(S, n).items():
        tot += 1
        bad += min(D[x][y], 3) != v
gate("split-criterion", bad == 0, f"{bad} of {tot} pairs differ")
# G2: series-parallel test on known graphs
K4s = nx.Graph([(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (4, 3), (2, 3)])  # K4 with one edge subdivided
gate("series-parallel", (not N.series_parallel(nx.complete_graph(4))) and N.series_parallel(nx.cycle_graph(6)) and
     N.series_parallel(nx.complete_bipartite_graph(2, 4)) and not N.series_parallel(K4s) and not N.series_parallel(nx.petersen_graph()),
     "K4, subdivided K4 and Petersen have a K4 minor; cycles and K(2,4) do not")
# G3: steps on a knot tree
ts = [(0, 1, 2), (2, 3, 4), (4, 5, 6), (2, 7, 8)]
S = N.steps(ts, 9)
gate("steps", S[0][6] == 3 and S[0][1] == 1 and S[8][6] == 3 and S[1][5] == 3 and S[7][8] == 1, "path lengths in knots")
# G4: primal blocks equal incidence blocks for three-place knots
bad = 0
for _ in range(200):
    n = rng.randint(4, 9)
    ts = sorted({tuple(sorted(rng.sample(range(n), 3))) for _ in range(rng.randint(2, 6))})
    a = sorted(sorted(b) for b in N.blocks(ts))
    b = sorted(sorted(idx) for vs, idx in N.primal_blocks(ts) if idx)
    bad += a != b
gate("blocks", bad == 0, f"{bad} of 200 bases differ")
# G5: states_any agrees with metriclib.states on three-place knots; NAE4 is complement-closed
bad = 0
for _ in range(100):
    n = rng.randint(4, 8)
    ts = sorted({tuple(sorted(rng.sample(range(n), 3))) for _ in range(rng.randint(1, 5))})
    kn = [(rng.choice(N.NAE_CLASS), t) for t in ts]
    bad += not np.array_equal(N.states_any(n, kn), M.states(n, kn))
st4 = N.states_any(5, [(N.NAE4, (0, 1, 2, 3)), (N.NAE4, (1, 2, 3, 4))])
gate("states", bad == 0 and set(int(s) for s in st4) == set(31 ^ int(s) for s in st4), "agree on 100 bases; four-place base complement-closed")
# G6: rings are built right, and the two-knot not-all-equal base fails
n, kn = N.ring(4, False)
D2 = M.bond_matrix(4, M.states(4, [(N.NAE3, (0, 1, 2)), (N.NAE3, (0, 1, 3))]))
gate("ring-and-exhibit", [t for _, t in kn] == [(0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0)] and D2[2][3] == math.inf and N.is_block([(0, 1, 2), (0, 1, 3)]),
     "ring of four; two knots sharing two distinctions: no bond holds their thirds")
# G7: bond count identity on a two-knot tree (bonds: the two knots and the path set)
st = M.states(5, [(N.NAE3, (0, 1, 2)), (N.NAE3, (2, 3, 4))])
gate("bond-count", len(N.bonds_list(5, st)) == 3, "1 + 1 + 1 x 1")
json.dump(out, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in out.values()) else "SOME FAIL")
