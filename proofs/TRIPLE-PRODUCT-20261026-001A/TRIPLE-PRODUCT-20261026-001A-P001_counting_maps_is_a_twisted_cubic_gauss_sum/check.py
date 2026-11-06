"""Check for TRIPLE-PRODUCT-20261026-001A-P001: counting maps to UT3(F4) x| C3 is a twisted cubic Gauss sum.
Standard library only (tp_lib.py in this directory). Run: python3 check.py [--write]"""
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tp_lib as T  # noqa: E402

KNOTS = {  # braid words; all closures are knots
    "3_1": ([1, 1, 1], 2),
    "5_1": ([1] * 5, 2),
    "4_1": ([1, -2, 1, -2], 3),
    "5_2": ([1, 1, 1, 2, -1, 2], 3),
    "8_18": ([1, -2] * 4, 3),
    "3_1 # 3_1": ([1, 1, 1, 2, 2, 2], 3),
}


def main():
    t0 = time.time()
    out, ok_all = {}, True

    # part 1: the group and the automorphism exchanging psi and psi^2
    G = T.ELEMS
    rng = random.Random(20261026)
    assoc = all(T.gmul(T.gmul(a, b), c) == T.gmul(a, T.gmul(b, c)) for a, b, c in
                ((rng.choice(G), rng.choice(G), rng.choice(G)) for _ in range(20000)))
    frob = all(T.frobenius_aut(T.gmul(a, b)) == T.gmul(T.frobenius_aut(a), T.frobenius_aut(b)) for a in G for b in G)
    bij = len({T.frobenius_aut(g) for g in G}) == len(G)
    centre = [g for g in G if all(T.gmul(g, k) == T.gmul(k, g) for k in G)]
    ok1 = len(G) == 192 and assoc and frob and bij and centre == [T.ONE]
    out["1_group"] = {"|G|": len(G), "associativity (20000 random triples)": assoc,
                      "(n, h^e) -> (Frobenius(n), h^2e) is an automorphism": frob and bij, "centre trivial": centre == [T.ONE], "ok": ok1}
    print("part 1:", out["1_group"], flush=True)
    ok_all &= ok1

    # part 2: |Hom| = 1 + 128 4^d N against brute force, H1 = Z/3, and psi^2 contributes as psi
    rows2, ok2 = {}, True
    for name, (w, n) in KNOTS.items():
        ts = time.time()
        U, rels, _ = T.presentation(w, n, 3)
        H, Bm, _ = T.obstruction_data(U, rels)
        N = T.kernel_count(H, Bm)
        H2, Bm2, _ = T.obstruction_data(U, rels, psi=[2] * U)
        N2 = T.kernel_count(H2, Bm2)
        d = len(H) // 2
        formula = 1 + 2 * 16 * 4 ** (d + 1) * N
        brute = T.brute_count(w, n)
        h1 = T.smith_invariants(U, rels)
        good = brute == formula and N2 == N and len(H2) == len(H) and h1 == [3]
        rows2[name] = {"d": d, "N": N, "N for psi^2": N2, "1 + 128 4^d N": formula, "brute force": brute, "H1": h1, "ok": good,
                       "seconds": round(time.time() - ts, 1)}
        print("part 2", name, rows2[name], flush=True)
        ok2 &= good
    out["2_brute_force"] = {"rows": rows2, "ok": ok2}
    ok_all &= ok2

    # part 3: B is the contraction of a symmetric, F4-balanced trilinear form with injective pairing (Poincare duality);
    # the cubic character sum |V|^-1 sum (-1)^{tr T(a,b,c)} equals N
    cases = {"3_1": KNOTS["3_1"], "8_18": KNOTS["8_18"], "3_1 # 3_1": KNOTS["3_1 # 3_1"],
             "(3_1)^#3": ([1, 1, 1, 2, 2, 2, 3, 3, 3], 4),
             "coupled n = 6": ([i for i in range(1, 6) for _ in range(3)] + [i for _ in range(6) for i in range(1, 6)], 6)}
    w5, _ = T.insert_at(T.fig8_sum(5), [(6, 1)])
    cases["(4_1)^#5 with a Borromean insertion"] = (w5, 11)
    rows3, ok3 = {}, True
    for name, (w, n) in cases.items():
        ts = time.time()
        U, rels, _ = T.presentation(w, n, 3)
        H, Bm, _ = T.obstruction_data(U, rels)
        N = T.kernel_count(H, Bm)
        sols, t_of, wdim, inj, _ = T.recover_trace_form(H, Bm, U)
        s = T.injective_solution(sols, inj)
        row = {"dim_F2 V": len(H), "dim W": wdim, "symmetric balanced solutions (F2 dim)": len(sols), "injective solution": s is not None,
               "N": N}
        good = s is not None
        if good:
            t = t_of(s)
            row["N from T"] = T.count_from_rows(T.trace_form_rows(t))
            good &= row["N from T"] == N
            if len(H) <= 6:
                row["cubic character sum"] = T.cubic_character_sum(t)
                good &= row["cubic character sum"] == N
        row["ok"] = good
        row["seconds"] = round(time.time() - ts, 1)
        rows3[name] = row
        print("part 3", name, row, flush=True)
        ok3 &= good
    out["3_duality"] = {"rows": rows3, "ok": ok3}
    ok_all &= ok3

    # part 4: regression against the probes' closed forms
    rows4, ok4 = {}, True
    for k in (1, 2, 3):
        w = [i + 1 for i in range(k) for _ in range(3)]
        d, N, f, h1 = T.count_formula(w, k + 1)
        rows4[f"(3_1)^#{k}"] = {"count": f, "1 + 128 28^k": 1 + 128 * 28 ** k}
        ok4 &= f == 1 + 128 * 28 ** k
    for k in (1, 2):
        d, N, f, h1 = T.count_formula(T.fig8_sum(k), 2 * k + 1)
        rows4[f"(4_1)^#{k}"] = {"count": f, "1 + 128 64^k": 1 + 128 * 64 ** k}
        ok4 &= f == 1 + 128 * 64 ** k
    out["4_regression"] = {"rows": rows4, "ok": ok4}
    print("part 4:", rows4, flush=True)
    ok_all &= ok4

    # part 5: controls that can fail
    w, n = KNOTS["3_1"]
    U, rels, _ = T.presentation(w, n, 3)
    H, Bm, _ = T.obstruction_data(U, rels)
    d = len(H) // 2
    c = {"dropping the obstruction overcounts on S3_3(3_1)": 1 + 128 * 4 ** d * 16 ** d != rows2["3_1"]["brute force"],
         "the figure-eight has zero obstruction (N = |V|^2)": rows2["4_1"]["N"] == 16 ** rows2["4_1"]["d"]}
    ok5 = all(c.values())
    out["5_controls"] = {"rows": c, "ok": ok5}
    print("part 5:", c, flush=True)
    ok_all &= ok5

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "TRIPLE-PRODUCT-20261026-001A-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
