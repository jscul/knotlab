"""Check for COPRIME-CLASS2-20261026-001C-P001: without a hard pair, counting is polynomial with bounded homology.
Standard library only; imports cp_lib.py read-only from COPRIME-CLASS2-20261026-001B-P001. Run: python3 check.py [--write]"""
import itertools
import json
from fractions import Fraction
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_heisenberg_counting_splits_into_eigen_triple_forms_that_borromean_moves_steer"))
import cp_lib as C  # noqa: E402

T31, F8, S61 = ([1, 1, 1], 2), ([1, -2, 1, -2], 3), ([1, 1, 2, -1, -3, 2, -3], 4)


def easy_N(G, U, rels, k):
    """the polynomial route for one character psi_k: (count, method)"""
    p = G.p
    Hx, Hy, Bm, _ = C.obstruction(G, U, rels, k)
    dx, dy = len(Hx), len(Hy)
    ax, by, ab = pow(G.a, k, p), pow(G.b, k, p), pow(G.a * G.b, k, p)
    if not dx or not dy:
        return p ** (dx + dy), "one side empty"
    w = len(next(iter(Bm.values())))
    if ab == 1:
        vals = [list(Bm[(i, j)]) for i in range(dx) for j in range(dy)]
        R, piv = C.rref(vals, p)
        kk = len(R)
        Bc = {(i, j): [Bm[(i, j)][c] for c in piv] for i in range(dx) for j in range(dy)}
        tot = Fraction(0)
        for th in itertools.product(range(p), repeat=kk):
            M = [[sum(t * x for t, x in zip(th, Bc[(i, j)])) % p for j in range(dy)] for i in range(dx)]
            tot += Fraction(p) ** (dx + dy - kk - C.rank(M, p))
        assert tot.denominator == 1
        # N = p^(dx + dy - kk) * sum over theta of p^(-rank(theta o B)): a sum over the bounded space of theta
        return int(tot), f"sum over theta in F_{p}^{kk} of ranks"
    if ax == 1 or by == 1:
        tot = 0
        triv, other = (dx, dy) if ax == 1 else (dy, dx)
        for s in itertools.product(range(p), repeat=triv):
            rows = []
            for t in range(other):
                v = [0] * w
                for u in range(triv):
                    key = (u, t) if ax == 1 else (t, u)
                    v = [(x + s[u] * y) % p for x, y in zip(v, Bm[key])]
                rows.append(v)
            cols = [[rows[t][c] for t in range(other)] for c in range(w)]
            tot += p ** len(C.nullspace(cols, other, p))
        return tot, "enumerate the trivial-character side, then linear algebra"
    return None, "hard pattern"


def main():
    t0 = time.time()
    out, ok_all = {}, True
    rows, ok = {}, True
    groups = [(5, 4, 2, 3), (5, 4, 4, 4), (5, 4, 2, 1), (5, 4, 1, 2), (7, 3, 2, 4), (7, 6, 3, 5), (7, 6, 1, 3)]
    for (p, r, a, b) in groups:
        G = C.Group(p, r, a, b)
        for name, (w, n) in [("6_1", S61), ("4_1", F8), ("3_1", T31)]:
            for s in (r, r * p):
                U, rels, _ = C.presentation(w, n, s)
                for k in range(r):
                    N1, how = easy_N(G, U, rels, k)
                    Hx, Hy, Bm, _ = C.obstruction(G, U, rels, k)
                    N2, _ = C.kernel_counts(Hx, Hy, Bm, p)
                    good = N1 == N2
                    ok &= good
                    if len(Hx) and len(Hy):
                        rows[f"p={p} r={r} (a,b)=({a},{b}) S3_{s}({name}) psi_{k}"] = {"dims": (len(Hx), len(Hy)), "enumeration": N2,
                                                                                    "polynomial route": N1, "method": how, "ok": good}
    out["1_easy_route"] = {"rows": rows, "ok": ok, "cases with nonempty sides": len(rows)}
    print("part 1:", ok, len(rows), flush=True)
    ok_all &= ok
    # part 2: totals against brute force on rp-surgeries (trivial-character components present)
    rows2, ok2 = {}, True
    for (p, r, a, b) in [(5, 4, 2, 3), (5, 4, 4, 4), (5, 4, 2, 1), (7, 3, 2, 4)]:
        G = C.Group(p, r, a, b)
        for name, (w, n) in [("3_1", T31), ("4_1", F8)]:
            f, _ = C.hom_count(G, w, n, r * p)
            bf = C.brute_count(G, w, n, r * p)
            rows2[f"p={p} r={r} (a,b)=({a},{b}) S3_{r * p}({name})"] = {"formula": f, "brute force": bf, "ok": f == bf}
            ok2 &= f == bf
    out["2_brute_force"] = {"rows": rows2, "ok": ok2}
    print("part 2:", ok2, flush=True)
    ok_all &= ok2
    # part 3: control: a hard pattern is not covered by the easy route
    G = C.Group(5, 4, 2, 2)
    U, rels, _ = C.presentation(*S61, 4)
    N1, how = easy_N(G, U, rels, 1)
    out["3_control"] = {"hard pattern (2,2) at p=5": how, "ok": N1 is None}
    ok_all &= N1 is None
    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "COPRIME-CLASS2-20261026-001C-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
