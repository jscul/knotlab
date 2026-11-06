"""Scout (not a ticket check) for HANDLE-LOCALITY-20261103-001: is a plane gluing line reached by an opened handle (the Fano plane attached
at a point, the removal inside it) exactly when fixing the split point's three copies on the plane piece leaves at most two of its
patterns?  Run from the repository root with .venv/bin/python -B; output is recorded in reach_condition_scout.txt."""
import sys, itertools, collections, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-LOCALITY-20261103-001B/HANDLE-LOCALITY-20261103-001B-P001_where_creation_happens"))
import planar_lib as PL
import elim_lib as E
import join_lib as J
G = PL.G
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
FARS = [("K4", SP[1]), ("c6", SP[6]), ("Fano", SP[21])]


def lab(space, name):
    H, s, n = space
    return (H, s, n, [name] * len(H), [name] * n)


tot = collections.Counter()
for size, seed in ((10, 0), (10, 1), (12, 0), (12, 1), (14, 0)):
    Hp = lab(PL.to_space(PL.grow(size, seed)), "plane")
    S = J.splice_pieces(G, lab(SP[21], "handle"), Hp, 0, 0)
    HS, sS, nS, llab, plab = S
    ports = list(SP[21][0][0])                    # the Fano line spliced out: its points are the cut ports
    plines = [k for k in range(len(HS)) if llab[k] == "plane"]
    ppts = sorted({q for k in plines for q in HS[k]})
    Q = J.solve(G, [HS[k] for k in plines], [sS[k] for k in plines], ppts)
    col = {q: i for i, q in enumerate(ppts)}
    reached = {}
    for L in plines:
        X = list(HS[L])
        best = 6
        for w in {tuple(int(r[col[y]]) for y in ports) for r in Q}:
            rows = Q[np.all(Q[:, [col[y] for y in ports]] == w, axis=1)]
            pats = {tuple(int(r[col[q]]) for q in X) for r in rows}
            best = min(best, len(pats))
        reached[L] = best
    for M in range(len(HS)):
        if llab[M] == "plane":
            continue
        AN = np.array(G.removal(HS, sS, nS, M), dtype=np.int8)
        for L in plines:
            X = list(HS[L])
            if len({tuple(int(b) for b in r) for r in AN[:, X]}) != 6:
                continue
            creates = False
            for fname, F in FARS:
                newraw, rep, far, AF = J.new_knots(E, G, AN, HS, sS, nS, L, F, 3)
                creates |= bool(newraw)
            tot[("fixing the three copies leaves %d of L's patterns" % reached[L], "creates" if creates else "none")] += 1
    print(size, seed, flush=True)
for k in sorted(tot):
    print(tot[k], k)
