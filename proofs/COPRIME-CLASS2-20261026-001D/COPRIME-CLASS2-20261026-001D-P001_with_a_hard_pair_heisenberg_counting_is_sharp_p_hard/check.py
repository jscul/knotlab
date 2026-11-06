"""Check for COPRIME-CLASS2-20261026-001D-P001: with a hard pair, Heisenberg counting is #P-hard with H1 = Z/r.
Standard library only; imports cp_lib.py read-only from COPRIME-CLASS2-20261026-001B-P001. Run: python3 check.py [--write]"""
import itertools
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_heisenberg_counting_splits_into_eigen_triple_forms_that_borromean_moves_steer"))
import cp_lib as C  # noqa: E402

T31, F8, K52, S61 = ([1, 1, 1], 2, -1), ([1, -2, 1, -2], 3, 1), ([1, 1, 1, 2, -1, 2], 3, -2), ([1, 1, 2, -1, -3, 2, -3], 4, 2)
GRAPHS = {"K2": (2, [(0, 1)]), "P3": (3, [(0, 1), (1, 2)]), "digon": (2, [(0, 1), (0, 1)]), "K3": (3, [(0, 1), (1, 2), (0, 2)])}
PERMS = [((0, 1, 2), 1), ((1, 2, 0), 1), ((2, 0, 1), 1), ((0, 2, 1), -1), ((2, 1, 0), -1), ((1, 0, 2), -1)]


def potts(n, edges, Q, v):
    return sum(math.prod(1 + v * (s[a] == s[b]) for a, b in edges) for s in itertools.product(range(Q), repeat=n))


def tutte(n, edges, x, y):
    def rk(S):
        par = list(range(n))
        def f(z):
            while par[z] != z:
                z = par[z]
            return z
        c = 0
        for e in S:
            a, b = f(edges[e][0]), f(edges[e][1])
            if a != b:
                par[a] = b
                c += 1
        return c
    m, rE = len(edges), rk(range(len(edges)))
    return sum((x - 1) ** (rE - rk(S)) * (y - 1) ** (len(S) - rk(S)) for size in range(m + 1)
               for S in itertools.combinations(range(m), size)), n - rE


def count(T, dims, q):
    dA, dB, dC = dims
    N = 0
    for a in itertools.product(range(q), repeat=dA):
        M = [[0] * dC for _ in range(dB)]
        for (i, j, k), c in T.items():
            if a[i]:
                M[j][k] = (M[j][k] + c * a[i]) % q
        N += q ** len(C.nullspace([[M[j][k] for j in range(dB)] for k in range(dC)], dB, q))
    return N


def gadget(pattern, n, edges, q):
    m, T = len(edges), {}
    def add(key, c):
        T[key] = (T.get(key, 0) + c) % q
    if pattern in (1, 3):     # alternating 3-form sum_e (x_u - x_v) ^ p_e ^ s_e (pattern 1: transported to three spaces)
        for e, (u, v) in enumerate(edges):
            P, S = n + 2 * e, n + 2 * e + 1
            for x, s in ((u, 1), (v, -1)):
                for perm, sg in PERMS:
                    idx = (x, P, S)
                    add(tuple(idx[t] for t in perm), s * sg)
        d = n + 2 * m
        return T, (d, d, d), Fraction(q) ** (2 * m - n) * potts(n, edges, q ** 3, q * q - 1), (1 + Fraction(q ** 3, q * q - 1), q * q)
    if pattern == 2:          # x, y in X + P, test in F^m: sum_e w_e ((x_u - x_v) ^ p_e)(x, y)
        for e, (u, v) in enumerate(edges):
            P = n + e
            for x, s in ((u, 1), (v, -1)):
                add((x, P, e), s)
                add((P, x, e), -s)
        return T, (n + m, n + m, m), Fraction(q) ** m * potts(n, edges, q * q, q - 1), (1 + Fraction(q * q, q - 1), q)
    if pattern == 4:          # x, test in X + P, y in F^m: sum_e s_e(y) ((x_u - x_v) ^ p_e)(x, test)
        for e, (u, v) in enumerate(edges):
            P = n + e
            for x, s in ((u, 1), (v, -1)):
                add((x, e, P), s)
                add((P, e, x), -s)
        return T, (n + m, m, n + m), Fraction(q) ** (m - n) * potts(n, edges, q * q, q - 1), (1 + Fraction(q * q, q - 1), q)


def main():
    t0 = time.time()
    out, ok_all = {}, True

    # part 1: the gadget lemma for the four patterns, and the Potts-Tutte conversion
    rows1, ok1 = {}, True
    for q in (3, 5):
        for pattern in (1, 2, 3, 4):
            for name, (n, E) in GRAPHS.items():
                T, dims, pred, (x, y) = gadget(pattern, n, E, q)
                if q ** dims[0] > 300000:
                    continue
                N = count(T, dims, q)
                tv, k = tutte(n, E, x, y)
                Q, v = (q ** 3, q * q - 1) if pattern in (1, 3) else (q * q, q - 1)
                good = N == pred and potts(n, E, Q, v) == Q ** k * v ** (n - k) * tv and (x - 1) * (y - 1) not in (0, 1)
                rows1[f"q={q} pattern {pattern} {name}"] = {"N": N, "predicted": str(pred), "Tutte point": f"({x}, {y})",
                                                             "(x-1)(y-1)": str((x - 1) * (y - 1)), "ok": good}
                ok1 &= good
    out["1_gadgets"] = {"rows": rows1, "ok": ok1}
    print("part 1:", ok1, len(rows1), flush=True)
    ok_all &= ok1

    # part 2: twist knots: twisted cohomology sits exactly at the roots of m t^2 - (2m+1) t + m, in dimension one
    bad, tested = 0, 0
    for p in (5, 7, 11, 13):
        for name, (w, n, m) in {"3_1": T31, "4_1": F8, "5_2": K52, "6_1": S61}.items():
            U, rels, _ = C.presentation(w, n, p - 1)
            for z in range(2, p):
                dim = len(C.cohomology(U, rels, z, 1, p)[0])
                root = (m * z * z - (2 * m + 1) * z + m) % p == 0
                tested += 1
                bad += (dim > 0) != root or dim > 1
    out["2_twist_knots"] = {"tested (p, knot, zeta)": tested, "mismatches": bad, "ok": bad == 0}
    print("part 2:", bad == 0, flush=True)
    ok_all &= bad == 0

    # part 3: end to end on knots: Borromean insertions found by search realize the gadget configuration; N equals the gadget value
    sys.path.insert(0, str(HERE))
    from e2e_lib import run_case  # noqa: E402
    rows3, ok3 = {}, True
    for label, G, summands, k, mode, gn, gm, gE in [
            ("p=7 r=3 (a,b)=(2,2), pattern 3, digon", C.Group(7, 3, 2, 2), [S61[:2]] * 6, 3, "alt3", 2, 2, [(0, 1), (0, 1)]),
            ("p=5 r=4 (a,b)=(2,4), pattern 4, triangle", C.Group(5, 4, 2, 4), [S61[:2], F8[:2], S61[:2], S61[:2], F8[:2], S61[:2], S61[:2], F8[:2], S61[:2]], 4, "case4", 3, 3, [(0, 1), (1, 2), (0, 2)]),
            ("p=5 r=4 (a,b)=(2,2), pattern 2, triangle", C.Group(5, 4, 2, 2), [S61[:2], F8[:2], S61[:2], S61[:2], F8[:2], S61[:2], S61[:2], F8[:2], S61[:2]], 4, "case2", 3, 3, [(0, 1), (1, 2), (0, 2)])]:
        res = run_case(G, summands, k, mode, gn, gm, gE)
        rows3[label] = res
        ok3 &= res["ok"]
        print("part 3", label, res, flush=True)
    out["3_end_to_end"] = {"rows": rows3, "ok": ok3}
    ok_all &= ok3

    # part 4: knot groups (Corollary 5): the counting formula on the knot group against brute force
    rows4, ok4 = {}, True
    for (p, r, a, b) in [(7, 3, 2, 2), (5, 4, 2, 2), (5, 4, 2, 4)]:
        G = C.Group(p, r, a, b)
        for name, (w, n, _) in [("3_1", T31), ("4_1", F8)]:
            f, bf = C.knot_group_count(G, w, n), C.brute_count(G, w, n, knot_group=True)
            rows4[f"p={p} r={r} (a,b)=({a},{b}) knot group of {name}"] = {"formula": f, "brute force": bf, "ok": f == bf}
            ok4 &= f == bf
    # the q = 4, r = 3 group: |Hom(knot group)| = |Hom(pi1 S^3_3(K))| + 63 (the surgery relation is automatic)
    sys.path.insert(0, str(ROOT / "proofs/TRIPLE-PRODUCT-20261026-001A/TRIPLE-PRODUCT-20261026-001A-P001_counting_maps_is_a_twisted_cubic_gauss_sum"))
    import tp_lib as TP  # noqa: E402
    for name, (w, n) in [("3_1", ([1, 1, 1], 2)), ("4_1", ([1, -2, 1, -2], 3)), ("5_2", ([1, 1, 1, 2, -1, 2], 3)), ("3_1 # 3_1", ([1, 1, 1, 2, 2, 2], 3))]:
        surgery = TP.brute_count(w, n)
        U, rels, arc = TP.presentation(w, n, 3)
        knot = 0
        for g0 in TP.ELEMS:
            cls = TP.conj_class(g0)
            for rest in itertools.product(cls, repeat=n - 1):
                top = [g0, *rest]
                cur, img, good = list(top), [None] * U, True
                for L, g in enumerate(w):
                    for q in range(n):
                        aa = arc[(L, q)]
                        if img[aa] is None:
                            img[aa] = cur[q]
                        elif img[aa] != cur[q]:
                            good = False
                            break
                    if not good:
                        break
                    i = abs(g) - 1
                    x, y = cur[i], cur[i + 1]
                    if g > 0:
                        cur[i], cur[i + 1] = TP.gmul(TP.gmul(TP.INV[x], y), x), x
                    else:
                        cur[i], cur[i + 1] = y, TP.gmul(TP.gmul(y, x), TP.INV[y])
                if good and cur == top:
                    knot += 1
        rows4[f"UT3(F4) x| C3, {name}: knot group minus 3-surgery"] = {"knot group": knot, "3-surgery": surgery, "difference": knot - surgery,
                                                                        "ok": knot - surgery == 63}
        ok4 &= knot - surgery == 63
    out["4_knot_groups"] = {"rows": rows4, "ok": ok4}
    print("part 4:", ok4, {k: v.get("difference", v.get("formula")) for k, v in rows4.items()}, flush=True)
    ok_all &= ok4

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "COPRIME-CLASS2-20261026-001D-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
