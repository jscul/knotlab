#!/usr/bin/env python3
"""NEXT-DIRECTION-SCAN-20261026-001A (lane A): pattern-1 mixing on actual knots (p = 7, r = 6, zeta = 3).

Uses the pattern-1 steering configurations of COPRIME-CLASS2-20261026-001B (base [3_1, 6_1, 5_2] x 3, 6-cabled Borromean
insertions; cp_lib.py imported read-only). On M = S^3_6(K) it computes the three cup-product bimaps
  V_z x V_z2 -> H^2(F_z3),  V_z x V_z3 -> H^2(F_z4),  V_z2 x V_z3 -> H^2(F_z5)
(Heisenberg groups (3,2), (3,6), (2,6)) and counts, for the free class-2 group on three generators with characters
(z, z^2, z^3) and all three commutators nonzero ("free3"),
  N_free3 = #{(c1, c2, c3) : c1 u c2 = 0, c1 u c3 = 0, c2 u c3 = 0}.
The same count is predicted from the steered tensor T_pred (leaf functionals, steering law of B); a match means the three
commutator components are read off ONE tensor on the actual manifold. Also reports each single-component (Heisenberg)
count and their product, which is what "isolating one component" would give.

Run: /home/jscul/p-vs-np-contact-first/.venv/bin/python -B knot_pattern1.py   (well under a minute)
"""
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_heisenberg_counting_splits_into_eigen_triple_forms_that_borromean_moves_steer"))
import cp_lib as C  # noqa: E402

T31, K52, S61 = ([1, 1, 1], 2), ([1, 1, 1, 2, -1, 2], 3), ([1, 1, 2, -1, -3, 2, -3], 4)
P, R = 7, 6


def zero_vec(v):
    return not any(v)


def lin(B, a, b, da, db, L):
    """sum_{i,j} a_i b_j B[(i, j)]"""
    v = [0] * L
    for i in range(da):
        if a[i]:
            for j in range(db):
                if b[j]:
                    f = a[i] * b[j] % P
                    v = [(x + f * y) % P for x, y in zip(v, B[(i, j)])]
    return v


def kernel_dim_cols(cols, n):
    """dim {x in F_p^n : sum_j x_j cols[j] = 0}"""
    if not cols or not cols[0]:
        return n
    rows = [[cols[j][t] for j in range(n)] for t in range(len(cols[0]))]
    return n - C.rank(rows, P)


def compress(B):
    """restrict the class vectors to the coordinates where some vector is nonzero (canonical reductions are sparse)"""
    supp = sorted({t for v in B.values() for t, x in enumerate(v) if x})
    return {key: [v[t] for t in supp] for key, v in B.items()}, max(len(supp), 1)


def counts_from_bimaps(B12, B13, B23, d1, d2, d3, L12, L13, L23):
    (B12, L12), (B13, L13), (B23, L23) = compress(B12), compress(B13), compress(B23)
    for B, L in ((B12, L12), (B13, L13), (B23, L23)):
        for key in B:
            if not B[key]:
                B[key] = [0] * L
    out = {"free3": 0, "H12": 0, "H13": 0, "H23": 0}
    for c1 in itertools.product(range(P), repeat=d1):
        # H13 needs only c1: kernel of c3 -> c1 u c3
        k13 = kernel_dim_cols([lin(B13, c1, [int(l == t) for t in range(d3)], d1, d3, L13) for l in range(d3)], d3)
        k12 = kernel_dim_cols([lin(B12, c1, [int(j == t) for t in range(d2)], d1, d2, L12) for j in range(d2)], d2)
        out["H12"] += P ** k12
        out["H13"] += P ** k13
        for c2 in itertools.product(range(P), repeat=d2):
            if not zero_vec(lin(B12, c1, c2, d1, d2, L12)):
                continue
            cols = []
            for l in range(d3):
                e = [int(l == t) for t in range(d3)]
                cols.append(lin(B13, c1, e, d1, d3, L13) + lin(B23, c2, e, d2, d3, L23))
            out["free3"] += P ** kernel_dim_cols(cols, d3)
    for c2 in itertools.product(range(P), repeat=d2):
        out["H23"] += P ** kernel_dim_cols([lin(B23, c2, [int(l == t) for t in range(d3)], d2, d3, L23) for l in range(d3)], d3)
    return out


def tensor_bimaps(T, d1, d2, d3):
    """bimaps read off a tensor T[i][j][l]: (c1 u c2) <-> T(c1, c2, .), (c1 u c3) <-> T(c1, ., c3), (c2 u c3) <-> T(., c2, c3)"""
    B12 = {(i, j): [T[i][j][l] for l in range(d3)] for i in range(d1) for j in range(d2)}
    B13 = {(i, l): [T[i][j][l] for j in range(d2)] for i in range(d1) for l in range(d3)}
    B23 = {(j, l): [T[i][j][l] for i in range(d1)] for j in range(d2) for l in range(d3)}
    return B12, B13, B23


def main():
    t0 = time.time()
    G = C.Group(P, R, 3, 2)                      # x char z = 3, y char z^2 = 2, gamma = z^3 = 6
    word0, n = C.connected_sum([T31, S61, K52] * 3)
    rows = {}
    ok = True
    for ins in ([(1, 1)], [(17, 1)], [(1, 1), (18, 1)]):
        w, tops = C.insert_at(word0, ins, R)
        U, rels, arc = C.presentation(w, n, R)
        H1, _, B12, _ = C.obstruction(C.Group(P, R, 3, 2), U, rels, 1)
        H1b, H3, B13, _ = C.obstruction(C.Group(P, R, 3, 6), U, rels, 1)
        H2, H3b, B23, _ = C.obstruction(C.Group(P, R, 2, 6), U, rels, 1)
        assert H1 == H1b and H3 == H3b
        d1, d2, d3 = len(H1), len(H2), len(H3)
        actual = counts_from_bimaps(B12, B13, B23, d1, d2, d3, len(B12[(0, 0)]), len(B13[(0, 0)]), len(B23[(0, 0)]))
        # prediction from the steering law: T = sum over insertions of sum_sigma sgn(sigma) l_s1 (x) m_s2 (x) n_s3
        leaves = C.leaf_sets(G, (H1, H2, H3), arc, tops, [o for _, o in ins], R)
        T = [[[0] * d3 for _ in range(d2)] for _ in range(d1)]
        for L in leaves:
            for (s1, s2, s3), sg in C.PERMS:
                for i in range(d1):
                    if L[0][s1][i]:
                        for j in range(d2):
                            if L[1][s2][j]:
                                for l in range(d3):
                                    if L[2][s3][l]:
                                        T[i][j][l] = (T[i][j][l] + sg * L[0][s1][i] * L[1][s2][j] * L[2][s3][l]) % P
        P12, P13, P23 = tensor_bimaps(T, d1, d2, d3)
        pred = counts_from_bimaps(P12, P13, P23, d1, d2, d3, d3, d2, d1)
        good = actual == pred
        ok &= good
        rows[str(ins)] = {"dims (V_z, V_z2, V_z3)": (d1, d2, d3), "actual (cup products)": actual, "predicted (steered T)": pred,
                          "match": good}
        print(ins, rows[str(ins)], flush=True)
    out = {"rows": rows, "ok": ok, "seconds": round(time.time() - t0, 1)}
    (HERE / "knot_pattern1_result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("ALL OK" if ok else "MISMATCH", out["seconds"], "s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
