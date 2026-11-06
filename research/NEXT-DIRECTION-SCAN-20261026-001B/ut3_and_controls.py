"""Lane B of NEXT-DIRECTION-SCAN-20261026-001: UT3(F4) x| C3 sectors on the end-to-end knots, and the nilpotent control.

1. On the end-to-end knots of TRIPLE-PRODUCT-20261026-001D (digon on (4_1)^#6, triangle on (4_1)^#9), the obstruction kernel
   count over psi and over psi^2 (tp_lib.obstruction_data with psi = 2 on meridians). Theorem 1(c) of TRIPLE-PRODUCT-001A says
   they agree (Frobenius automorphism), so |Hom| = 1 + 128 4^d N and the steered part is all of |Hom| - 1: the reduction from
   Z(64, 15) is approximation-preserving with ratio 1 + 1/(128 4^d N).
2. Negative control (Eisermann): for nilpotent targets, |Hom(knot group, G)| = |G| on every knot: H(F_3), H(F_5) and
   UT3(F4), by brute force over braid closures; nothing depends on the knot, so no reduction can pass through these counts.
Standard library only; imports tp_lib.py and cp_lib.py read-only. Run: python3 -B ut3_and_controls.py   (about 1-2 minutes)
"""
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/TRIPLE-PRODUCT-20261026-001A/TRIPLE-PRODUCT-20261026-001A-P001_counting_maps_is_a_twisted_cubic_gauss_sum"))
sys.path.insert(0, str(ROOT / "proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_heisenberg_counting_splits_into_eigen_triple_forms_that_borromean_moves_steer"))
import tp_lib as T  # noqa: E402
import cp_lib as C  # noqa: E402

KNOTS = {"3_1": ([1, 1, 1], 2), "4_1": ([1, -2, 1, -2], 3), "5_2": ([1, 1, 1, 2, -1, 2], 3), "3_1 # 3_1": ([1, 1, 1, 2, 2, 2], 3)}


def ut3_sectors():
    rows = {}
    for name, (k, ins, gadget) in {"digon (4_1)^#6, insertions (6,1) (10,3)": (6, [(6, 1), (10, 3)], 326656),
                                   "triangle (4_1)^#9, insertions (6,1) (14,5) (22,9)": (9, [(6, 1), (14, 5), (22, 9)], 45162496)}.items():
        ts = time.time()
        w, _ = T.insert_at(T.fig8_sum(k), ins)
        U, rels, _ = T.presentation(w, 2 * k + 1, 3)
        H1, B1, _ = T.obstruction_data(U, rels)
        H2, B2, _ = T.obstruction_data(U, rels, psi=[2] * U)
        N1, N2 = T.kernel_count(H1, B1), T.kernel_count(H2, B2)
        d = len(H1) // 2
        hom = 1 + 128 * 4 ** d * N1
        rows[name] = {"d": d, "N over psi": N1, "N over psi^2": N2, "gadget value": gadget, "|Hom|": hom,
                      "|Hom| / steered part": f"{hom / (128 * 4 ** d * N1):.17g}",
                      "ok": N1 == N2 == gadget, "seconds": round(time.time() - ts, 1)}
        print(name, rows[name], flush=True)
    return rows


def closure_count(mul, inv, elems, word, n):
    tot = 0
    for top in itertools.product(elems, repeat=n):
        cur = list(top)
        for g in word:
            i = abs(g) - 1
            x, y = cur[i], cur[i + 1]
            if g > 0:
                cur[i], cur[i + 1] = mul(mul(inv(x), y), x), x
            else:
                cur[i], cur[i + 1] = y, mul(mul(y, x), inv(y))
        tot += cur == list(top)
    return tot


def nilpotent_control():
    rows = {}
    groups = {}
    for p in (3, 5):
        G = C.Group(p, 1, 1, 1)
        groups[f"H(F_{p}) (order {p ** 3})"] = (G.mul, G.inv, G.elements(), p ** 3)
    N = [g for g in T.ELEMS if g[3] == 0]
    groups["UT3(F4) (order 64)"] = (T.gmul, lambda g: T.INV[g], N, 64)
    for gname, (mul, inv, elems, order) in groups.items():
        for kname, (w, n) in KNOTS.items():
            if order ** n > 300000:
                continue
            c = closure_count(mul, inv, elems, w, n)
            rows[f"{gname}, {kname}"] = {"|Hom|": c, "|G|": order, "ok": c == order}
    print("control:", rows, flush=True)
    return rows


def main():
    out = {"1_ut3_sectors": ut3_sectors(), "2_nilpotent_control": nilpotent_control()}
    (HERE / "ut3_and_controls.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
