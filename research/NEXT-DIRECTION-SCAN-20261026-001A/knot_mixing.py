#!/usr/bin/env python3
"""NEXT-DIRECTION-SCAN-20261026-001A (lane A): end-to-end mixing test on an actual knot.

Rebuilds the p = 5, r = 4 pattern-2 triangle knot of COPRIME-CLASS2-20261026-001D (same search, same base, read-only imports
of cp_lib.py and e2e_lib.py), computes on M = S^3_4(K) the two Heisenberg obstruction bimaps
  V_2 x V_2 -> H^2(F_4)   (group (alpha, beta) = (2, 2))   and   V_2 x V_4 -> H^2(F_3)   (group (2, 4)),
which are two readings of ONE triple-product tensor on the V-multiset {2, 2, 4}, and then counts for the group
  mix(5):  B = B_2^2 (+) B_4 = <e1, e2> (+) <f>,  A = A_4 (+) A_3,  [e1, e2] = z4,  [e1, f] = z3,
whose two commutator components both sit on that multiset:
  N_mix = #{(a1, a2, c) in V_2 x V_2 x V_4 : a1 u a2 = 0, a1 u c = 0}.
It compares N_mix with the Bulatov-Grohe prediction of bg_route.py for the triangle (a hierarchical, non-Potts weight), and
the two Heisenberg counts with the Potts values 3240625 and 25925 (positive controls).

Run: /home/jscul/p-vs-np-contact-first/.venv/bin/python -B knot_mixing.py   (about 1-2 minutes)
"""
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIB_B = ROOT / "proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_heisenberg_counting_splits_into_eigen_triple_forms_that_borromean_moves_steer"
LIB_D = ROOT / "proofs/COPRIME-CLASS2-20261026-001D/COPRIME-CLASS2-20261026-001D-P001_with_a_hard_pair_heisenberg_counting_is_sharp_p_hard"
sys.path.insert(0, str(LIB_B))
sys.path.insert(0, str(LIB_D))
sys.path.insert(0, str(HERE))
import cp_lib as C  # noqa: E402
import e2e_lib as E  # noqa: E402
import bg_route as BG  # noqa: E402

F8, S61 = ([1, -2, 1, -2], 3), ([1, 1, 2, -1, -3, 2, -3], 4)


def find_case2(G, summands, k):
    """the configuration search of e2e_lib.run_case, mode 'case2' (triangle), returning the knot word"""
    p = G.p
    word, n = C.connected_sum(summands)
    data, dims = E.window_data(G, word, n, k)
    items = []
    for w, ls in data:
        tf = E.two_form(ls[0], ls[2], ls[1], p)
        if tf and C.rank(tf[1], p) == 2:
            items.append((w, tf[0], C.rref(tf[1], p)[0]))
    for (w1, s1, P1), (w2, s2, P2), (w3, s3, P3) in itertools.combinations(items, 3):
        if len({w1[0], w2[0], w3[0]}) < 3 or C.rank([s1, s2, s3], p) < 3:
            continue
        if (C.rank(P1 + P2, p), C.rank(P1 + P3, p), C.rank(P2 + P3, p), C.rank(P1 + P2 + P3, p)) == (4, 4, 4, 5):
            found = [w1, w2, w3]
            kw, tops = C.insert_at(word, found, k)
            return kw, n, found, dims
    return None


def kernel_dim(vectors_by_j, p):
    """dim of {b : sum_j b_j v_j = 0}"""
    dy = len(vectors_by_j)
    if not dy:
        return 0
    L = len(vectors_by_j[0])
    cols = [[vectors_by_j[j][t] for j in range(dy)] for t in range(L)]
    return dy - C.rank(cols, p) if cols else dy


def comb(Bm, a, j, di, p, L):
    v = [0] * L
    for i in range(di):
        if a[i]:
            w = Bm[(i, j)]
            v = [(x + a[i] * y) % p for x, y in zip(v, w)]
    return v


def main():
    t0 = time.time()
    p, r = 5, 4
    G22 = C.Group(p, r, 2, 2)
    G24 = C.Group(p, r, 2, 4)
    summands = [S61, F8, S61, S61, F8, S61, S61, F8, S61]
    res = find_case2(G22, summands, 4)
    assert res, "configuration not found"
    word, n, found, dims = res
    print("knot: strands", n, "crossings", len(word), "insertions", found, "dims (x, y, test)", dims, flush=True)
    U, rels, arc = C.presentation(word, n, r)
    Hx, Hy, B22, _ = C.obstruction(G22, U, rels, 1)
    Hx2, Hy4, B24, _ = C.obstruction(G24, U, rels, 1)
    assert Hx == Hy == Hx2
    d2, d4 = len(Hx), len(Hy4)
    L22 = len(B22[(0, 0)])
    L24 = len(B24[(0, 0)])
    N22 = N24 = Nmix = 0
    for a in itertools.product(range(p), repeat=d2):
        k22 = kernel_dim([comb(B22, a, j, d2, p, L22) for j in range(d2)], p)
        k24 = kernel_dim([comb(B24, a, j, d2, p, L24) for j in range(d4)], p)
        N22 += p ** k22
        N24 += p ** k24
        Nmix += p ** (k22 + k24)
    # Bulatov-Grohe predictions (abstract gadget on the triangle; V-characters 1 = zeta^1 = 2, 2 = zeta^2 = 4)
    nV, Ed = BG.GRAPHS["K3"]
    Gs = BG.groups()
    preds = {}
    for name, key in [("H(5) (z,z) [Heisenberg, pattern 2]", "N22"), ("H(5) (z,z^2) [Heisenberg, pattern 4]", "N24"),
                      ("mix(5): [e1,e2]->A_{z^2}, [e1,f]->A_{z^3}", "Nmix")]:
        Gm = Gs[name]
        m = len(Ed)
        vchar = [1] * (nV + m) + [2] * m
        _, tests = BG.variables(Gm, vchar, 1)
        preds[key] = BG.bg_sum(Gm, (1, 1, 2), 1, nV, Ed, len(tests))
    # the weight matrix of mix(5): hierarchical, not Potts
    U_, table = BG.g_table(Gs["mix(5): [e1,e2]->A_{z^2}, [e1,f]->A_{z^3}"], (1, 1, 2), 1, explicit=True)
    levels = {}
    for delta, (v, rk) in table.items():
        levels.setdefault((v, rk), 0)
        levels[(v, rk)] += 1
    out = {"knot": {"strands": n, "crossings": len(word), "insertions (level, offset)": found, "dims V_2, V_4": (d2, d4)},
           "N (2,2) Heisenberg": N22, "N (2,4) Heisenberg": N24, "N mix(5)": Nmix,
           "BG predictions": preds, "product of the Heisenberg counts (what isolation would give)": N22 * N24,
           "mix(5) weight levels {(g, rank K): #delta}": {str(k_): v for k_, v in levels.items()},
           "ok": N22 == 3240625 and N24 == 25925 and Nmix == preds["Nmix"] and N22 == preds["N22"] and N24 == preds["N24"],
           "seconds": round(time.time() - t0, 1)}
    print(json.dumps(out, indent=1, default=str))
    (HERE / "knot_mixing_result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
