#!/usr/bin/env python3
"""NEXT-DIRECTION-SCAN-20261026-001A (lane A), question (iii): characteristic 2 at q = 4, r = 3 (abstract layer).

For p = 2 the cocycle beta has a symmetric part: its diagonal q_beta(e) = beta(e, e) is the squaring map of N. It enters the
obstruction only through the diagonal terms T(c_a, c_a, w) q_beta(e_a), so it should be invisible when the triple product has
zero Bockstein diagonal (T(a, a, .) = 0), and visible otherwise. Groups (F4-linear, h acting by w^2 on B and w on A):
  UT3:  beta(e0, e1) = z                         (TRIPLE-PRODUCT's UT3(F4) x| C3)
  SQ:   beta(e0, e1) = z, beta(e0, e0) = z        (squaring map x(x + y): isomorphic to UT3 via y -> x + y; control)
  ANI:  beta(e0, e1) = z, beta(e0, e0) = z, beta(e1, e1) = w z   (squaring map xy + x^2 + w y^2, anisotropic: Arf
        invariant w is not in {t^2 + t} = {0, 1}, so not isomorphic to UT3 as an extension; same commutator pairing)
Forms on V = F4^4 (the K2 gadget of TRIPLE-PRODUCT, coordinates x_u, x_v, p, s):
  A  = (x_u + x_v) ^ p ^ s                          (zero diagonal; BG / Potts prediction 4^(2m-n) Z(64, 15) = 5056)
  A + x_u^3  (a trefoil-type diagonal term T(x_u, x_u, x_u) = 1 added)
Run: python3 -B gf4_check.py   (standard library; a few seconds)
"""
import itertools
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = [None, 0, 1, 2]                 # F4 = {0, 1, w = 2, w^2 = 3}, addition = XOR
EXP = [1, 2, 3]


def fmul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[(LOG[a] + LOG[b]) % 3]


def T_sym(base):
    """symmetric trilinear form from a dict of sorted index triples (char 2: all orderings get the same value)"""
    T = {}
    for key, v in base.items():
        for perm in set(itertools.permutations(key)):
            T[perm] = T.get(perm, 0) ^ v
    return T


def gadget_A():
    # x_u = 0, x_v = 1, p = 2, s = 3 ; (x_u + x_v) ^ p ^ s = x_u^p^s + x_v^p^s (char 2 wedge = symmetrization, zero diagonal)
    return {(0, 2, 3): 1, (1, 2, 3): 1}


def count(T, beta, d=4):
    """#{c = (c0, c1) in V x V : o(c) = 0}, <o(c), w> = sum_{a, a'} T(c_a, c_a', w) beta(a, a')"""
    N = 0
    for c0 in itertools.product(range(4), repeat=d):
        for c1 in itertools.product(range(4), repeat=d):
            c = (c0, c1)
            ok = True
            for w in range(d):
                tot = 0
                for (a, a2), bv in beta.items():
                    if not bv:
                        continue
                    s = 0
                    for i in range(d):
                        if c[a][i] == 0:
                            continue
                        for j in range(d):
                            if c[a2][j] == 0:
                                continue
                            tv = T.get((i, j, w), 0)
                            if tv:
                                s ^= fmul(fmul(c[a][i], c[a2][j]), tv)
                    tot ^= fmul(s, bv)
                if tot:
                    ok = False
                    break
            N += ok
    return N


def potts(n, edges, Q, v):
    return sum(math.prod(1 + v * (s[a] == s[b]) for a, b in edges) for s in itertools.product(range(Q), repeat=n))


def main():
    UT3 = {(0, 1): 1}
    SQ = {(0, 1): 1, (0, 0): 1}
    ANI = {(0, 1): 1, (0, 0): 1, (1, 1): 2}
    A = T_sym(gadget_A())
    A_diag = T_sym({**gadget_A(), (0, 0, 0): 1})
    pred = potts(2, [(0, 1)], 64, 15)          # 4^(2m - n) = 1 for K2
    res = {"Potts prediction 4^(2m-n) Z(64,15) on K2": pred,
           "UT3, A": count(A, UT3), "SQ, A": count(A, SQ),
           "UT3, A + diagonal": count(A_diag, UT3), "SQ, A + diagonal": count(A_diag, SQ),
           "ANI, A": count(A, ANI), "ANI, A + diagonal": count(A_diag, ANI)}
    res["squaring map invisible when the diagonal vanishes"] = res["UT3, A"] == res["SQ, A"] == res["ANI, A"] == pred
    res["isomorphic control agrees with the diagonal"] = res["UT3, A + diagonal"] == res["SQ, A + diagonal"]
    res["squaring map visible when the diagonal is nonzero"] = res["UT3, A + diagonal"] != res["ANI, A + diagonal"]
    res["ok"] = (res["squaring map invisible when the diagonal vanishes"] and res["isomorphic control agrees with the diagonal"]
                 and res["squaring map visible when the diagonal is nonzero"])
    print(json.dumps(res, indent=1))
    (HERE / "gf4_check_result.json").write_text(json.dumps(res, indent=1) + "\n")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
