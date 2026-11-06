#!/usr/bin/env python3
"""NEXT-DIRECTION-SCAN-20261026-001A (lane A), question (iii): the p = 2 Bockstein diagonal at q = 4, r = 3.

For M = S^3_3(K) and V = H^1(M; F4 twisted by w^2), the diagonal D(a) = a u a (in H^2(M; F4_w)) is invariant under Borromean
moves with leaves in ker psi; a gadget base needs D = 0. Conjecture tested here (sketch in report.md):
   a u a = Frob_*(Bockstein of a) for the Teichmueller-twisted sequence F4 -> W2(F4) -> F4, so for a cyclic Alexander module
   D = 0  <=>  Delta_K(w~) = 0 in W2(F4) = Z4[x]/(x^2 + x + 1)  (w~ = Teichmueller lift of w = x).
D is read from the obstruction bimap of tp_lib.py (COPRIME's F4 machinery, imported read-only); Delta from Fox calculus.

Run: /home/jscul/p-vs-np-contact-first/.venv/bin/python -B bockstein_q4.py   (sympy; under a minute)
"""
import json
import random
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/TRIPLE-PRODUCT-20261026-001A/TRIPLE-PRODUCT-20261026-001A-P001_counting_maps_is_a_twisted_cubic_gauss_sum"))
import tp_lib as TP  # noqa: E402

t = sp.symbols("t")


def alexander(word, n):
    """Delta of the closure of `word` by Fox calculus on the Wirtinger relators of tp_lib.presentation (all but the surgery
    relator); returned as an integer polynomial, normalized up to +-t^k"""
    U, rels, _ = TP.presentation(word, n, 3)
    knot_rels = rels[:-1]
    rows = []
    for rel in knot_rels:
        row = [sp.Integer(0)] * U
        pref = sp.Integer(1)
        for g, s in rel:
            for _ in range(abs(s)):
                if s > 0:
                    row[g] += pref
                    pref *= t
                else:
                    pref /= t
                    row[g] -= pref
        rows.append(row)
    M = sp.Matrix(rows)[:, 1:]
    d = sp.factor(sp.simplify(M.det()))
    num, den = sp.fraction(sp.together(d))
    P = sp.Poly(sp.expand(num), t)
    # strip powers of t
    coeffs = P.all_coeffs()
    while coeffs and coeffs[-1] == 0:
        coeffs.pop()
    if coeffs and coeffs[0] < 0:
        coeffs = [-c for c in coeffs]
    return coeffs


def eval_teich_mod4(coeffs):
    """Delta(w~) in Z4[x]/(x^2+x+1): returns (a, b) with value a + b x, reduced mod 4"""
    x = sp.symbols("x")
    P = sp.Poly(sum(c * x ** (len(coeffs) - 1 - i) for i, c in enumerate(coeffs)), x)
    R = P.rem(sp.Poly(x ** 2 + x + 1, x))
    cs = R.all_coeffs()
    cs = [0] * (2 - len(cs)) + cs
    b, a = cs
    return (int(a) % 4, int(b) % 4)


def diagonal(word, n):
    U, rels, _ = TP.presentation(word, n, 3)
    H, Bm, _ = TP.obstruction_data(U, rels)
    d2 = len(H)
    sym = all(Bm[(i, j)] == Bm[(j, i)] for i in range(d2) for j in range(d2))
    diag_zero = all(Bm[(i, i)] == 0 for i in range(d2))
    any_nonzero = any(Bm[(i, j)] for i in range(d2) for j in range(d2))
    return d2 // 2, sym, diag_zero, any_nonzero


def main():
    t0 = time.time()
    named = {"3_1": ([1, 1, 1], 2), "4_1": ([1, -2, 1, -2], 3), "T(2,9)": ([1] * 9, 2), "T(3,4) = 8_19": ([1, 2] * 4, 3),
             "8_18": ([1, -2] * 4, 3), "7_2 (twist, m = -3)": ([1, 1, 1, 2, -1, 2, 3, -2, 3], 4), "T(2,15)": ([1] * 15, 2),
             "3_1 # 4_1": ([1, 1, 1, 2, -3, 2, -3], 4), "5_2": ([1, 1, 1, 2, -1, 2], 3)}
    rows = {}
    rng = random.Random(20261026)
    cand = list(named.items())
    tries = 0
    while len(cand) < len(named) + 40 and tries < 4000:
        tries += 1
        n = rng.choice([3, 3, 4])
        L = rng.randint(4, 9)
        w = [rng.choice([1, -1]) * rng.randint(1, n - 1) for _ in range(L)]
        try:
            TP.presentation(w, n, 3)
        except AssertionError:
            continue
        cand.append((f"random {w} on {n}", (w, n)))
    agree = disagree = 0
    for name, (w, n) in cand:
        d, sym, dz, anyz = diagonal(w, n)
        if d == 0 and not name.startswith(("3_1", "4_1", "5_2")):
            continue
        coeffs = alexander(w, n)
        val = eval_teich_mod4(coeffs)
        pred = val == (0, 0)
        row = {"dim_F4 V": d, "bimap symmetric": sym, "diagonal zero": dz, "T != 0": anyz, "Delta": coeffs,
               "Delta(w~) mod 4 (a + b w~)": val, "predicted diagonal zero": pred}
        if d == 1:
            row["criterion agrees (dim 1)"] = pred == dz
            agree += pred == dz
            disagree += pred != dz
        rows[name] = row
        print(name, row, flush=True)
    out = {"rows": rows, "dim-1 cases agreeing with the criterion": agree, "dim-1 cases disagreeing": disagree,
           "ok": disagree == 0, "seconds": round(time.time() - t0, 1)}
    (HERE / "bockstein_q4_result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("agree", agree, "disagree", disagree, out["seconds"], "s")
    return 0 if disagree == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
