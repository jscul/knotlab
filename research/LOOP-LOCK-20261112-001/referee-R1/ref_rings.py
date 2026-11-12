#!/usr/bin/env python3
"""Referee LOOP-LOCK-R1: rings (j, j+1, j+2) under one order, by the pair transfer, with the referee's own code (ref_endless.py of
the ENDLESS-BLOCK referee folder and ref_lib.py of the BASES-WITHIN referee folder, the referee's; no import of loop_lib.py,
endless_lib.py or nest_lib.py).

    python3 -B ref_rings.py [--nmax 120]      (writes result_rings.json)

A ring of n knots under one order is a closed walk of length n of the pair transfer: vertices (u, v), pairs of states of consecutive
copies, and an edge (u, v) -> (v, w) when R(u, v, w). The ring locks (every copy equal to every other, place by place, in every
state) exactly when every closed walk of length n stays on the diagonal {(u, u)}. A closed walk lies in one strongly connected
component; lengths of closed walks in a component of period d are multiples of d (by the definition of the period), and all large
multiples occur. So for every n: the ring locks unless some component holding an off-diagonal vertex has a closed walk of length n
through such a vertex. The script finds the components (scipy), their periods, whether each touches the diagonal, whether its
off-diagonal vertices are shears (v = shift_c(u) with one c), the exact lock lengths up to nmax, and a certificate that the pattern
beyond nmax is the residue pattern (each component's closed-walk lengths through a vertex form a numerical semigroup in dZ; it is full
beyond x once it holds min/d consecutive multiples from x)."""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "ENDLESS-BLOCK-20261112-001" / "referee-R1"))
import ref_endless as E  # noqa: E402
import ref_lib as R  # noqa: E402


def main():
    nmax = int(sys.argv[sys.argv.index("--nmax") + 1]) if "--nmax" in sys.argv else 120
    rows = []
    for idx, h in enumerate(R.harmonies()):
        t0 = time.time()
        W, ok = E.relation(h)
        n = len(W)
        P = h["P"]
        trip = np.argwhere(ok)                       # (u, v, w)
        src = trip[:, 0] * n + trip[:, 1]
        dst = trip[:, 1] * n + trip[:, 2]
        N = n * n
        A = csr_matrix((np.ones(len(src), dtype=np.int8), (src, dst)), shape=(N, N))
        ncomp, lab = connected_components(A, directed=True, connection="strong")
        diag = np.zeros(N, dtype=bool)
        diag[np.arange(n) * n + np.arange(n)] = True
        comps = []
        for c in range(ncomp):
            vs = np.nonzero(lab == c)[0]
            if not np.any(~diag[vs]):
                continue
            sub = A[vs][:, vs]
            if sub.nnz == 0:
                continue                             # a single vertex with no loop: no closed walk
            # period: BFS levels from vs[0]; d = gcd of level(u) + 1 - level(v) over edges inside
            idx_of = {int(v): i for i, v in enumerate(vs)}
            level = -np.ones(len(vs), dtype=int)
            level[0] = 0
            fr = [0]
            sub = sub.tocsr()
            while fr:
                nx = []
                for i in fr:
                    for j in sub.indices[sub.indptr[i]:sub.indptr[i + 1]]:
                        if level[j] < 0:
                            level[j] = level[i] + 1
                            nx.append(j)
                fr = nx
            d = 0
            coo = sub.tocoo()
            for i, j in zip(coo.row, coo.col):
                d = math.gcd(d, int(level[i] + 1 - level[j]))
            d = abs(d)
            off = [i for i, v in enumerate(vs) if not diag[v]]
            pairs = [(int(v) // n, int(v) % n) for v in vs if not diag[v]]
            # shears: v = shift_c(u) for one c for every off-diagonal pair
            Wt = [tuple(w) for w in W]
            shifts = set()
            for u, v in pairs:
                cs = {c for c in range(P) if tuple(Wt[u][(i + c) % P] for i in range(P)) == Wt[v]}
                shifts.add(frozenset(cs))
            # closed walks through off-diagonal vertices, lengths 1..nmax, by boolean powers restricted to the component
            S = sub.astype(bool).astype(np.int32)
            M = S.copy()
            lengths = []
            per_vertex = {i: [] for i in off[:200]}
            for L in range(1, nmax + 1):
                dg = M.diagonal()
                if np.any(dg[off] > 0):
                    lengths.append(L)
                for i in per_vertex:
                    if dg[i] > 0:
                        per_vertex[i].append(L)
                M = (M @ S)
                M.data[:] = 1
            # certificate for one vertex: its semigroup is full beyond x
            cert = None
            for i, Ls in per_vertex.items():
                if not Ls:
                    continue
                s = Ls[0]
                need = s // d if d else 1
                Lset = set(Ls)
                for x in range(s, nmax - need * d + 1, d):
                    if all(x + t * d in Lset for t in range(need)):
                        cert = {"vertex": i, "full from": x}
                        break
                if cert:
                    break
            comps.append({"size": int(len(vs)), "off-diagonal vertices": len(off), "touches the diagonal": bool(np.any(diag[vs])),
                          "period": d, "closed-walk lengths (to nmax)": lengths,
                          "all off-diagonal pairs are shears": all(len(c) > 0 for c in shifts),
                          "shear slopes seen": sorted({c for cs in shifts for c in cs})[:12], "certificate": cert})
        unlock = sorted({L for c in comps for L in c["closed-walk lengths (to nmax)"]})
        locks = [L for L in range(3, nmax + 1) if L not in unlock]
        periods = sorted({c["period"] for c in comps})
        rows.append({"i": idx, "orbits": h["orbits"], "P": P, "states": n, "components with off-diagonal cycles": comps,
                     "ring lengths 3..nmax that lock": locks, "periods": periods, "seconds": round(time.time() - t0, 1)})
        print(idx, h["orbits"][:2], "P", P, "periods", periods, "locks", locks[:14], "...", round(time.time() - t0, 1), flush=True)
    (HERE / "result_rings.json").write_text(json.dumps({"nmax": nmax, "rows": rows}, indent=1) + "\n")
    print("wrote result_rings.json")


if __name__ == "__main__":
    main()
