"""Check for CORRECTIONS-20261026-001D-P001: counting maps to UT3(F4) x| C3 is #P-hard with H1 = Z/3.
Standard library only; imports tp_lib.py from the reissued proof CORRECTIONS-20261026-001A-P001 read-only.
Run: python3 check.py [--write]"""
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/CORRECTIONS-20261026-001A/CORRECTIONS-20261026-001A-P001_counting_maps_is_a_twisted_cubic_gauss_sum_reissued"))
import tp_lib as T  # noqa: E402

GRAPHS = {"K2": (2, [(0, 1)]), "K2 + vertex": (3, [(0, 1)]), "P3": (3, [(0, 1), (1, 2)]), "digon": (2, [(0, 1), (0, 1)]),
          "K3": (3, [(0, 1), (1, 2), (0, 2)])}


def mul(q):
    return (lambda a, b: a & b) if q == 2 else T.fmul


def rank(M, q):
    M = [row[:] for row in M]
    f = mul(q)
    r = 0
    for c in range(len(M[0]) if M else 0):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        if q == 4:
            iv = T.FINV[M[r][c]]
            M[r] = [f(iv, x) for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                g = M[i][c]
                M[i] = [x ^ f(g, y) for x, y in zip(M[i], M[r])]
        r += 1
    return r


def gadget(n, edges, gains=None):
    """alternating form sum_e (x_u + g_e x_v) ^ p_e ^ q_e on F_q^{n + 2m}, as a dict of symmetrized entries"""
    Tt = {}
    for e, (u, v) in enumerate(edges):
        p, s = n + 2 * e, n + 2 * e + 1
        for l, coef in ((u, 1), (v, gains[e] if gains else 1)):
            for perm in itertools.permutations((l, p, s)):
                Tt[perm] = Tt.get(perm, 0) ^ coef
    return n + 2 * len(edges), {k: v for k, v in Tt.items() if v}


def kernel_count(d, Tt, q):
    """N = #{(a, b) : A(a, b, .) = 0} = sum over a of q^corank(A(a, ., .))"""
    f = mul(q)
    by_i = {}
    for (i, j, k), v in Tt.items():
        by_i.setdefault(i, []).append((j, k, v))
    tot = 0
    for a in itertools.product(range(q), repeat=d):
        M = [[0] * d for _ in range(d)]
        for i in range(d):
            if a[i]:
                for j, k, v in by_i.get(i, ()):
                    M[j][k] ^= f(a[i], v)
        tot += q ** (d - rank(M, q))
    return tot


def potts(n, edges, Q, v):
    return sum(
        __import__("math").prod(1 + v * (s[a] == s[b]) for a, b in edges) for s in itertools.product(range(Q), repeat=n))


def tutte(n, edges, x, y):
    def r(S):
        par = list(range(n))
        def fd(z):
            while par[z] != z:
                par[z] = par[par[z]]
                z = par[z]
            return z
        k = 0
        for e in S:
            a, b = fd(edges[e][0]), fd(edges[e][1])
            if a != b:
                par[a] = b
                k += 1
        return k
    m = len(edges)
    rE = r(range(m))
    tot = Fraction(0)
    for size in range(m + 1):
        for S in itertools.combinations(range(m), size):
            rs = r(S)
            tot += (x - 1) ** (rE - rs) * (y - 1) ** (size - rs)
    return tot, n - rE


def main():
    t0 = time.time()
    out, ok_all = {}, True

    # part 1: the gadget lemma N = q^{2m-n} Z(q^3, q^2 - 1), and Z = Q^k v^{n-k} T(1 + Q/v, 1 + v)
    rows1, ok1 = {}, True
    for q in (2, 4):
        Q, v = q ** 3, q * q - 1
        for name, (n, edges) in GRAPHS.items():
            ts = time.time()
            d, Tt = gadget(n, edges)
            N = kernel_count(d, Tt, q)
            Z = potts(n, edges, Q, v)
            tv, k = tutte(n, edges, 1 + Fraction(Q, v), Fraction(1 + v))
            pred = Fraction(q) ** (2 * len(edges) - n) * Z
            good = N == pred and Z == Q ** k * v ** (n - k) * tv
            rows1[f"q={q} {name}"] = {"N": N, "q^(2m-n) Z(q^3, q^2-1)": str(pred), "Z": Z, "Tutte point": f"({1 + Fraction(Q, v)}, {1 + v})",
                                      "ok": good, "seconds": round(time.time() - ts, 1)}
            ok1 &= good
            print("part 1", f"q={q}", name, rows1[f"q={q} {name}"], flush=True)
    out["1_gadget"] = {"rows": rows1, "ok": ok1}
    ok_all &= ok1

    # part 2: figure-eight connected sums: dim V = number of summands, T = 0, H1 = Z/3; a band loop with nonzero functional
    rows2, ok2 = {}, True
    for k in range(1, 10):
        U, rels, arc = T.presentation(T.fig8_sum(k), 2 * k + 1, 3)
        H, Bm, _ = T.obstruction_data(U, rels)
        good = len(H) == 2 * k and not any(Bm.values()) and T.smith_invariants(U, rels) == [3]
        rows2[f"(4_1)^#{k}"] = {"dim_F4 V": len(H) // 2, "B = 0": not any(Bm.values()), "ok": good}
        ok2 &= good
    U, rels, arc = T.presentation(T.fig8_sum(1), 3, 3)
    H, Bm, _ = T.obstruction_data(U, rels)
    vals = T._vals(H[0], U)
    band = [(a, b) for a in range(U) for b in range(a + 1, U) if vals[a] != vals[b]]
    rows2["4_1: arc pairs (a, b) with c(x_a) + c(x_b) != 0, i.e. band loops x_a x_b^-1 with nonzero functional"] = band
    ok2 &= len(band) > 0
    out["2_figure_eight"] = {"rows": rows2, "ok": ok2}
    print("part 2:", rows2, flush=True)
    ok_all &= ok2

    # part 3: end to end: knots realizing a triangle and a digon configuration; |Hom| = 1 + 128 4^d N
    rows3, ok3 = {}, True
    cases = {"triangle (4_1)^#9, insertions (6,1) (14,5) (22,9)": (9, [(6, 1), (14, 5), (22, 9)], "K3"),
             "triangle (4_1)^#9, insertions (13,1) (21,5) (29,9)": (9, [(13, 1), (21, 5), (29, 9)], "K3"),
             "digon (4_1)^#6, insertions (6,1) (10,3)": (6, [(6, 1), (10, 3)], "digon"),
             "digon (4_1)^#6, insertions (13,1) (18,3)": (6, [(13, 1), (18, 3)], "digon")}
    for name, (k, ins, g) in cases.items():
        ts = time.time()
        n = 2 * k + 1
        w, tops = T.insert_at(T.fig8_sum(k), ins)
        U, rels, arc = T.presentation(w, n, 3)
        H, Bm, _ = T.obstruction_data(U, rels)
        lam = [[T.leaf_values(H, U, arc, L, list(bq)) for bq in T.window(o)] for L, (_, o) in zip(tops, ins)]
        # the leaf configuration: F4 ranks of each insertion's span, of pairs, and of all
        def f4rank(vecs):
            return rank([list(v) for v in vecs], 4)
        spans = [f4rank(l_) for l_ in lam]
        pairs = [f4rank(lam[i] + lam[j]) for i, j in itertools.combinations(range(len(lam)), 2)]
        total = f4rank([v for l_ in lam for v in l_])
        N, bad = T.compare_kernels(Bm, T.predicted_rows(H, lam))
        gn, ge = GRAPHS[g]
        expect = 4 ** (2 * len(ge) - gn) * potts(gn, ge, 64, 15)
        config_ok = spans == [3] * len(lam) and (pairs == [6, 6, 6] and total == 8 if g == "K3" else pairs == [5] and total == 5)
        good = bad == 0 and N == expect and config_ok and T.smith_invariants(U, rels) == [3] and len(H) // 2 == k
        rows3[name] = {"generators": U, "spans": spans, "pair spans": pairs, "total span": total, "mismatching a": bad, "N": N,
                       "gadget value 4^(2m-n) Z(64,15)": expect, "|Hom(pi1 M, G)| = 1 + 128 4^d N": 1 + 128 * 4 ** k * N, "ok": good,
                       "seconds": round(time.time() - ts, 1)}
        ok3 &= good
        print("part 3", name, rows3[name], flush=True)
    out["3_end_to_end"] = {"rows": rows3, "ok": ok3}
    ok_all &= ok3

    # part 4: control: the matroid matters. Gains on the triangle with product 1 give the same count; product w does not.
    n, edges = GRAPHS["K3"]
    d, Tb = gadget(n, edges, gains=[T.W, T.W2, 1])
    d, Tu = gadget(n, edges, gains=[1, 1, T.W])
    Nb, Nu = kernel_count(d, Tb, 4), kernel_count(d, Tu, 4)
    expect = 4 ** 3 * potts(3, edges, 64, 15)
    c = {"balanced gains (w, w^2, 1): N": Nb, "unbalanced gains (1, 1, w): N": Nu, "graphic value": expect}
    ok4 = Nb == expect and Nu != expect
    c["ok"] = ok4
    out["4_control"] = c
    print("part 4:", c, flush=True)
    ok_all &= ok4

    # part 5: knot groups: |Hom(knot group, G)| = |Hom(pi1 S^3_3(K), G)| + 63
    rows5, ok5 = {}, True
    for name, (w, n) in [("3_1", ([1, 1, 1], 2)), ("4_1", ([1, -2, 1, -2], 3)), ("5_2", ([1, 1, 1, 2, -1, 2], 3)), ("3_1 # 3_1", ([1, 1, 1, 2, 2, 2], 3))]:
        surgery = T.brute_count(w, n)
        U, rels, arc = T.presentation(w, n, 3)
        knot = 0
        for g0 in T.ELEMS:
            cls = T.conj_class(g0)
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
                        cur[i], cur[i + 1] = T.gmul(T.gmul(T.INV[x], y), x), x
                    else:
                        cur[i], cur[i + 1] = y, T.gmul(T.gmul(y, x), T.INV[y])
                if good and cur == top:
                    knot += 1
        rows5[name] = {"knot group": knot, "3-surgery": surgery, "difference": knot - surgery, "ok": knot - surgery == 63}
        ok5 &= knot - surgery == 63
    out["5_knot_groups"] = {"rows": rows5, "ok": ok5}
    print("part 5:", rows5, flush=True)
    ok_all &= ok5

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "CORRECTIONS-20261026-001D-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
