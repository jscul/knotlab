"""Lane B of NEXT-DIRECTION-SCAN-20261026-001: the Potts points produced by the reductions, against the hypotheses of the
approximation-hardness theorems, and the size of the unsteered inverse sector in the pure-leaf recipe.

1. For each (Q, B = 1 + v) produced by a reduction: Q > 2 (Goldberg-Jerrum 2012, Theorem 1: #BIS <=_AP Tutte(q, gamma) for
   q > 2, gamma > 0), and the least Delta >= 3 with B > B_o(Q, Delta) = (Q - 2) / ((Q - 1)^(1 - 2/Delta) - 1)
   (Galanis-Stefankovic-Vigoda-Yang, Theorem 2: #BIS <=_AP #BipFerroPotts(q, B, Delta) for q >= 3, Delta >= 3, B > B_o).
   Control: (Q, B) = (2, any) is outside both theorems (Jerrum-Sinclair: FPRAS for ferromagnetic Ising).
2. The pure-leaf recipe of COPRIME-CLASS2-20261026-001D Section 3 leaves the psi^-1 sector at its base value p^(dx + dy).
   Relative to the steered sector its size is Q^n (1 + v)^m / Z(Q, v) (same for all four patterns), which is at least
   (Q (1 + v) / (Q + v))^rank(Gamma), since Z(Q, v) <= (1 + v)^(m - |F|) Q^(n - |F|) (Q + v)^|F| for any spanning forest F.
   (The psi^-1 sector is never a permutation of (a, b, c) for a hard pair: an inversion-closed 3-multiset with product 1 would
   contain -1 and then have product -1.) Exact values on paths and cycles.
Standard library only. Run: python3 -B potts_points.py
"""
import json
import math
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def B_o(Q, D):
    return (Q - 2) / ((Q - 1) ** (1 - 2 / D) - 1)


def least_delta(Q, B):
    for D in range(3, 10 ** 4):
        if B > B_o(Q, D):
            return D
    return None


POINTS = {
    "UT3(F4) x| C3 (Lemma 6, q = 4)": (64, 16),
    "Heisenberg patterns 1, 3, p = 7": (343, 49),
    "Heisenberg patterns 1, 3, p = 13": (2197, 169),
    "Heisenberg patterns 2, 4, p = 5": (25, 5),
    "Heisenberg patterns 2, 4, p = 13": (169, 13),
    "S4 links (Theorem 2 of BOUNDED-H1-20261025-001A)": (12, Fraction(3, 2)),
    "control: ferromagnetic Ising": (2, 16),
}


def path_ratio(Q, v, n):        # Q^n (1+v)^m / Z(P_n), m = n - 1, Z(P_n) = Q (Q + v)^(n - 1)
    return Fraction(Q ** n * (1 + v) ** (n - 1), Q * (Q + v) ** (n - 1))


def cycle_ratio(Q, v, n):       # Z(C_n) = (Q + v)^n + (Q - 1) v^n
    return Fraction(Q ** n * (1 + v) ** n, (Q + v) ** n + (Q - 1) * v ** n)


def main():
    out = {"1_hypotheses": {}, "2_inverse_sector_excess": {}}
    for name, (Q, B) in POINTS.items():
        D = least_delta(Q, float(B)) if Q >= 3 else None
        out["1_hypotheses"][name] = {"Q": Q, "B = 1 + v": str(B), "Q > 2 (GJ Theorem 1 applies)": Q > 2,
                                     "B_o(Q, 3)": round(B_o(Q, 3), 4) if Q >= 3 else None,
                                     "least Delta with B > B_o (GSVY Theorem 2)": D}
    for name, (Q, v) in {"pattern 3, p = 7: (Q, v) = (343, 48)": (343, 48), "patterns 2, 4, p = 5: (Q, v) = (25, 4)": (25, 4)}.items():
        rows = {}
        for n in (2, 4, 8, 16, 32):
            rows[f"path P_{n}"] = f"{float(path_ratio(Q, v, n)):.4g}"
            rows[f"cycle C_{n}"] = f"{float(cycle_ratio(Q, v, n)):.4g}"
        rows["per matched edge, Q(1+v)/(Q+v)"] = f"{Q * (1 + v) / (Q + v):.4g}"
        out["2_inverse_sector_excess"][name] = rows
    # the digon of the p = 7 end-to-end instance: Q^2 (1+v)^2 / Z(digon) + 1 should be the counterfactual ratio 301.234
    Q, v = 343, 48
    Zd = Q * (Q - 1) + Q * (1 + v) ** 2
    out["2_inverse_sector_excess"]["digon, p = 7: 1 + Q^2 (1+v)^2 / Z (compare heis_sectors.json: 301.234)"] = \
        f"{1 + Q ** 2 * (1 + v) ** 2 / Zd:.6g}"
    Q, v = 25, 4
    Zt = sum(math.prod(1 + v * (s[a] == s[b]) for a, b in ((0, 1), (1, 2), (0, 2))) for s in
             ((i, j, k) for i in range(Q) for j in range(Q) for k in range(Q)))
    out["2_inverse_sector_excess"]["triangle, p = 5 patterns 2, 4: 1 + Q^3 (1+v)^3 / Z (compare 76.3375)"] = \
        f"{1 + Q ** 3 * (1 + v) ** 3 / Zt:.6g}"
    (HERE / "potts_points.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
