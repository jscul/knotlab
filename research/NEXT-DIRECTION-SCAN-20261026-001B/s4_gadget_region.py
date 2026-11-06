"""Lane B of NEXT-DIRECTION-SCAN-20261026-001: the region of effective interactions reachable by S4 knot gadgets.

A two-terminal series-parallel network of tripled edges (BOUNDED-H1-20261025-001A Section 5) has effective interaction
alpha (R + x I + y N) on Z_12, with R = J - I - N. Claim (proved in report.md): the region {x >= 1, -1 <= y <= 1} contains the single
tripled edge (1, -1) and is closed under series composition (eigenvalues multiply; the region is |L_s| <= L_a <= 4 + L_s in the
normalization alpha = 1, with L_s = x + y - 2, L_a = x - y) and parallel composition (x, y multiply). So the equal-pair weight is
never below the generic weight: no such gadget implements a proper-colouring constraint (x -> 0), the hard constraint behind
planar colouring hardness. This script enumerates all such networks up to MAXE edges (default 10) and checks the claim exactly.
Standard library only. Run: python3 -B s4_gadget_region.py [MAXE]
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    maxe = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    by = {1: {(F(0), F(-2), 1, 1)}}             # (b, g) of J + bI + gN with x = 1 + b, y = 1 + g; parities of t and f
    rows, ok = {}, True
    for m in range(2, maxe + 1):
        s = set()
        for a in range(1, m // 2 + 1):
            for (b1, g1, t1, f1) in by[a]:
                for (b2, g2, t2, f2) in by[m - a]:
                    S = 12 + b1 + b2 + g1 + g2
                    s.add(((b1 * b2 + g1 * g2) / S, (b1 * g2 + g1 * b2) / S, (t1 * t2) % 2, (t1 * f2 + f1 * t2) % 2))
                    s.add(((1 + b1) * (1 + b2) - 1, (1 + g1) * (1 + g2) - 1, (t1 * f2 + f1 * t2) % 2, (f1 * f2) % 2))
        by[m] = s
        inside = all(1 + b >= 1 and -1 <= 1 + g <= 1 for (b, g, t, f) in s)
        knots = [(1 + b, 1 + g) for (b, g, t, f) in s if t == 1 and f == 1]
        rows[m] = {"distinct (x, y, t mod 2, f mod 2)": len(s), "all in {x >= 1, -1 <= y <= 1}": inside,
                   "knot-keeping (t, f odd)": len(knots),
                   "min x": str(min(1 + b for (b, g, t, f) in s)), "max y": str(max(1 + g for (b, g, t, f) in s)),
                   "min y": str(min(1 + g for (b, g, t, f) in s))}
        ok &= inside
        print(m, rows[m], flush=True)
    out = {"rows": rows, "ok": ok}
    (HERE / "s4_gadget_region.json").write_text(json.dumps(out, indent=1) + "\n")
    print("ALL INSIDE" if ok else "VIOLATION")


if __name__ == "__main__":
    main()
