"""Lane B of NEXT-DIRECTION-SCAN-20261026-001: does the steering law of COPRIME-CLASS2-20261026-001B also govern the
inverse sector psi^-1 of the end-to-end knots, and why do sectors psi and psi^-1 have equal kernel counts there?

The psi^-1 sector of G = H(F_p) x| C_r with characters (a, b) is the psi sector of the group with characters (a^-1, b^-1).
So cp_lib.steer_test on that group compares the actual psi^-1 obstruction kernels with the kernels predicted from the
inverse-sector leaf functionals of the same Borromean insertions. The script also reports, per sector, the rank of each
insertion's leaf functionals in each slot space and the rank of all of them together.
Standard library only; imports cp_lib.py read-only. Run: python3 -B heis_inverse_sector.py   (about 3-5 minutes)
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_heisenberg_counting_splits_into_eigen_triple_forms_that_borromean_moves_steer"))
import cp_lib as C  # noqa: E402
from heis_sectors import CASES  # noqa: E402


def leaf_ranks(G, word, n, ins, k):
    p = G.p
    w, tops = C.insert_at(word, ins, k)
    U, rels, arc = C.presentation(w, n, G.r)
    gam = pow(G.a * G.b % p, p - 2, p)
    H3 = [C.cohomology(U, rels, z, 1, p)[0] for z in (G.a, G.b, gam)]
    leaves = C.leaf_sets(G, H3, arc, tops, [o for _, o in ins], k)
    out = {}
    for t, name in enumerate(("x", "y", "test")):
        per = [C.rank([list(v) for v in L[t]], p) if H3[t] else 0 for L in leaves]
        allv = [list(v) for L in leaves for v in L[t]]
        out[f"slot {name} (dim {len(H3[t])})"] = {"per insertion": per, "all": C.rank(allv, p) if H3[t] else 0}
    return out


def main():
    t0 = time.time()
    out = {}
    for label, (p, r, a, b), summands, k, ins, gadget in CASES:
        ts = time.time()
        word, n = C.connected_sum(summands)
        ai, bi = pow(a, p - 2, p), pow(b, p - 2, p)
        res = {}
        for sec, (x, y) in (("psi", (a, b)), ("psi^-1", (ai, bi))):
            G = C.Group(p, r, x, y)
            st = C.steer_test(G, word, n, ins, k)
            res[sec] = {"characters (x, y)": (x, y), "dims": st["dims"], "N": st["N"], "gadget value": gadget,
                        "kernel mismatches against the steering prediction": st["mismatches"][1],
                        "leaf ranks": leaf_ranks(G, word, n, ins, k)}
            print(label, sec, res[sec], f"({time.time() - ts:.0f}s)", flush=True)
        res["equal kernel counts"] = res["psi"]["N"] == res["psi^-1"]["N"]
        out[label] = res
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "heis_inverse_sector.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("done", out["seconds"], "s")


if __name__ == "__main__":
    main()
