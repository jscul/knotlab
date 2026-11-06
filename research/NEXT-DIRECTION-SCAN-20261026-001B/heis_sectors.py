"""Lane B of NEXT-DIRECTION-SCAN-20261026-001: sector decomposition of |Hom| for the Heisenberg end-to-end knots.

Question: |Hom(pi1 S^3_r(K), G)| = sum over the r maps psi^k (k = 0..r-1) of c_k N_k (COPRIME-CLASS2-20261026-001B/D).
The hardness reduction steers the k = 1 sector to a Potts gadget. Is that sector a non-negligible share of the total
(so that a multiplicative approximation of |Hom| gives one of the gadget value), or do other sectors dominate?

For each end-to-end instance of COPRIME-CLASS2-20261026-001D check part 3 (same base knots, same Borromean insertions),
this script computes, from the counting formula of B (brute-force-verified there on small knots):
  - every sector: dims of the x and y spaces, the kernel count N_k, the coefficient c_k, the contribution c_k N_k;
  - the same for the base knot without insertions (all forms zero, N_k = p^(dx + dy));
  - the "pure-leaf" counterfactual of proof D section 4 (only sector 1 steered, all other sectors at their base value);
  - the knot-group counts (surgery relator dropped).
Standard library only; imports cp_lib.py read-only from COPRIME-CLASS2-20261026-001B-P001.
Run: python3 -B heis_sectors.py   (about 3-6 minutes)
"""
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_heisenberg_counting_splits_into_eigen_triple_forms_that_borromean_moves_steer"))
import cp_lib as C  # noqa: E402

S61 = ([1, 1, 2, -1, -3, 2, -3], 4)
F8 = ([1, -2, 1, -2], 3)
NINE = [S61, F8, S61, S61, F8, S61, S61, F8, S61]

# (label, (p, r, a, b), summands, cable k, insertion windows found by D's search, gadget value from D's result.json)
CASES = [
    ("p=7 r=3 (a,b)=(2,2) pattern 3 digon", (7, 3, 2, 2), [S61] * 6, 3, [(0, 0), (1, 5)], 46101601),
    ("p=5 r=4 (a,b)=(2,4) pattern 4 triangle", (5, 4, 2, 4), NINE, 4, [(0, 0), (1, 13), (26, 8)], 25925),
    ("p=5 r=4 (a,b)=(2,2) pattern 2 triangle", (5, 4, 2, 2), NINE, 4, [(0, 0), (1, 13), (26, 8)], 3240625),
]


def sectors(G, U, rels):
    p, out = G.p, []
    for k in range(G.r):
        Hx, Hy, Bm, (zx, bx, zy, by) = C.obstruction(G, U, rels, k)
        _, zz, _ = C.cohomology(U, rels, G.a * G.b % p, k, p)
        N, _ = C.kernel_counts(Hx, Hy, Bm, p)
        c = p ** (zz + bx + by)
        out.append({"k": k, "chars (x, y, z)": (pow(G.a, k, p), pow(G.b, k, p), pow(G.a * G.b, k, p)),
                    "dx": len(Hx), "dy": len(Hy), "N_k": N, "max N_k = p^(dx+dy)": p ** (len(Hx) + len(Hy)),
                    "c_k": c, "c_k N_k": c * N})
    return out


def summary(rows, steered=1):
    total = sum(r["c_k N_k"] for r in rows)
    main = rows[steered]["c_k N_k"]
    return total, main, Fraction(total, main)


def main():
    t0 = time.time()
    out = {}
    for label, (p, r, a, b), summands, k, ins, gadget in CASES:
        ts = time.time()
        G = C.Group(p, r, a, b)
        word, n = C.connected_sum(summands)
        w, _ = C.insert_at(word, ins, k)
        res = {}
        for name, wd in (("base knot (no insertions)", word), ("end-to-end knot (D's insertions)", w)):
            U, rels, _ = C.presentation(wd, n, r)
            for kind, rr in (("surgery S^3_r(K)", rels), ("knot group", rels[:-1])):
                rows = sectors(G, U, rr)
                total, main, ratio = summary(rows)
                res[f"{name}, {kind}"] = {"sectors": rows, "|Hom|": total, "sector-1 term": main,
                                          "|Hom| / sector-1 term": f"{float(ratio):.6g}"}
                print(label, "|", name, "|", kind, "| |Hom| =", total, "| ratio =", f"{float(ratio):.6g}",
                      "| N_k =", [x["N_k"] for x in rows], f"({time.time() - ts:.0f}s)", flush=True)
        # the pure-leaf counterfactual (proof D section 4): sector 1 = gadget, every other sector at its base value
        e2e = res["end-to-end knot (D's insertions), surgery S^3_r(K)"]["sectors"]
        base = res["base knot (no insertions), surgery S^3_r(K)"]["sectors"]
        assert e2e[1]["N_k"] == gadget, "sector 1 must reproduce the gadget value"
        pure_total = sum(x["c_k N_k"] for x in base[:1]) + e2e[1]["c_k N_k"] + sum(x["c_k N_k"] for x in base[2:])
        res["pure-leaf counterfactual (surgery)"] = {
            "|Hom|": pure_total, "sector-1 term": e2e[1]["c_k N_k"],
            "|Hom| / sector-1 term": f"{pure_total / e2e[1]['c_k N_k']:.6g}",
            "note": "sectors k != 1 keep the base value p^(dx+dy) when the leaves are pure in the sector-1 eigenspaces"}
        res["base forms vanish (N_k = p^(dx+dy) for every k)"] = all(
            x["N_k"] == x["max N_k = p^(dx+dy)"] for x in base)
        res["sector-1 N equals the gadget value"] = e2e[1]["N_k"] == gadget
        res["seconds"] = round(time.time() - ts, 1)
        out[label] = res
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "heis_sectors.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("done", out["seconds"], "s")


if __name__ == "__main__":
    main()
