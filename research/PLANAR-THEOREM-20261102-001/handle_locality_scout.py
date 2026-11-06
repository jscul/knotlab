"""Scout (not a ticket check) for PLANAR-THEOREM-20261102-001: in a knot space made by splicing the Fano plane into a plane space, which
pinnings by two non-port points lose access - only those near the Fano part, or all?  The removed line M and the gluing line L are
located by side (Fano part / plane part / across the cut).  Run from the repository root with .venv/bin/python -B; output is recorded
in handle_locality_scout.txt."""
import sys, itertools, collections, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
import planar_lib as PL
G = PL.G
src = (ROOT / "proofs/PLANAR-COMPOSE-20261102-001A/PLANAR-COMPOSE-20261102-001A-P001_the_hub_reaches_the_ports_on_a_plane_side/check.py").read_text()
exec(src[src.index("def solutions("):src.index("def classify_pinnings(")])
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
T0 = time.time()


def where(line, side):
    s = {side[q] for q in line}
    return "Fano part" if s == {0} else ("plane part" if s == {1} else "across")


def run(H1, s1, n1, H2, s2, n2, li, label, fano_side):
    ls, ss, n, side, ports = G.splice(H1, s1, n1, li, H2, s2, n2, 0)
    full = G.states(n)[G.sat_matrix(ls, ss, n).all(axis=1)]
    assert len(full) == 0, "not a knot space"
    sidename = {fano_side: 0, 1 - fano_side: 1}
    sd = [sidename[side[q]] for q in range(n)]
    out = collections.Counter()
    for mi, M in enumerate(ls):
        A = solutions(ls, ss, n, mi)
        tie = {p: tied_to(A, p, n) for p in range(n)}
        for lj, L1 in enumerate(ls):
            if lj == mi:
                continue
            X = list(L1)
            I = {tuple(int(b) for b in r) for r in A[:, X]}
            if len(I) != 6:
                continue
            sigma = next(t for t in itertools.product((0, 1), repeat=3) if t not in I)
            for p in range(n):
                if p in X:
                    continue
                tied = [i for i, y in enumerate(X) if y in tie[p]]
                for a in range(n):
                    if a == p or a in X or a in tie[p]:
                        continue
                    for pv, av in itertools.product((0, 1), repeat=2):
                        rows = A[(A[:, p] == pv) & (A[:, a] == av)]
                        pats = {tuple(int(b) for b in r) for r in rows[:, X]}
                        if len(pats) != 1:
                            continue
                        tau = next(iter(pats))
                        oi = odd_index(tau, sigma)
                        if tied:
                            kind = "access" if tied[0] != oi else "NO"
                        else:
                            j, k = [i for i in range(3) if i != oi]
                            allowed = {(int(r[X[j]]), int(r[X[k]])) for r in A if int(r[p]) == pv}
                            excl = {(b1, b2) for b1 in (0, 1) for b2 in (0, 1)} - allowed
                            kind = "access" if any((e[0] != tau[j]) + (e[1] != tau[k]) == 1 for e in excl) else "NO"
                        out[("M in " + where(M, sd), "L in " + where(L1, sd), kind)] += 1
    print(label, "n =", n, round(time.time() - T0), "s")
    for k in sorted(out):
        print("   ", out[k], k)


Hf, sf, nf = SP[21]
for seed in (0, 1):
    Hp, sp, np_ = PL.to_space(PL.grow(10, seed))
    run(Hf, sf, nf, Hp, sp, np_, 0, "Fano line 0 spliced into a plane 10-point space (seed %d)" % seed, 0)
    run(Hp, sp, np_, Hf, sf, nf, 0, "plane 10-point space (seed %d) line 0 spliced into a Fano point" % seed, 1)
