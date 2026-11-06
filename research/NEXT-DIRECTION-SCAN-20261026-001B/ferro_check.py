"""Lane B of NEXT-DIRECTION-SCAN-20261026-001: which kind of spin system do the reductions produce?

1. Kernel-count edge gadgets are ferromagnetic. If an edge contributes w(x) = #{P : B(x, P) = 0} for a bilinear map
   B: F_p^s x F_p^k -> F_p^l (x = difference of the endpoint values), then the interaction W(s, s') = w(s - s') is positive
   semidefinite, because its Fourier transform is sum_P |K_P| [xi in K_P^perp] >= 0 with K_P = ker B(., P).
   Checked here on random bilinear maps over F_3 and F_5 (all Fourier coefficients >= 0, all eigenvalues >= 0).
2. The S4 gadget algebra is not confined to the ferromagnetic regime. Two-terminal series-parallel networks of tripled edges have
   effective interactions alpha (R + x I + y N) on Z_12 (R = J - I - N); the eigenvalues are 12 + x + y - 2 (all-ones),
   x + y - 2 (nu-symmetric, 5-dim) and x - y (nu-antisymmetric, 6-dim). The script lists small gadgets with their (x, y),
   the parity of t (spanning trees) and f (separating 2-forests), which decides whether knots are kept (BOUNDED-H1 Lemma 5.2),
   and whether W is entrywise nonnegative and positive semidefinite.
Standard library only. Run: python3 -B ferro_check.py
"""
import cmath
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def fourier_check(p, s, k, l, trials, rng):
    worst = None
    for _ in range(trials):
        B = [[[rng.randrange(p) for _ in range(l)] for _ in range(k)] for _ in range(s)]   # B[i][j] in F_p^l: x_i P_j coefficient
        def zero(x, P):
            return all(sum(x[i] * P[j] * B[i][j][t] for i in range(s) for j in range(k)) % p == 0 for t in range(l))
        xs = list(itertools.product(range(p), repeat=s))
        Ps = list(itertools.product(range(p), repeat=k))
        w = {x: sum(zero(x, P) for P in Ps) for x in xs}
        for xi in xs:
            val = sum(w[x] * cmath.exp(-2j * cmath.pi * sum(a * b for a, b in zip(xi, x)) / p) for x in xs)
            worst = val.real if worst is None else min(worst, val.real)
    return worst


def sp_gadgets(max_edges):
    """two-terminal series-parallel networks: (description, edges, (b, g) of the normalized J + bI + gN form, t, f)"""
    E = (1, Fraction(0), Fraction(-2), 1, 1)           # M = J - 2N; t = 1 spanning tree, f = 1 separating 2-forest
    by = {1: [("e", E)]}
    for m in range(2, max_edges + 1):
        out = {}
        for a in range(1, m):
            for (da, A) in by[a]:
                for (db, Bg) in by[m - a]:
                    _, b1, g1, t1, f1 = A
                    _, b2, g2, t2, f2 = Bg
                    # series: matrix product (J + b1 I + g1 N)(J + b2 I + g2 N); t = t1 t2, f = t1 f2 + f1 t2
                    S = 12 + b1 + b2 + g1 + g2
                    sb, sg = (b1 * b2 + g1 * g2) / S, (b1 * g2 + g1 * b2) / S
                    out.setdefault(f"S({da},{db})", (m, sb, sg, t1 * t2, t1 * f2 + f1 * t2))
                    # parallel: entrywise product in Hadamard coordinates (1 + b, 1 + g); t = t1 f2 + f1 t2, f = f1 f2
                    x, y = (1 + b1) * (1 + b2), (1 + g1) * (1 + g2)
                    out.setdefault(f"P({da},{db})", (m, x - 1, y - 1, t1 * f2 + f1 * t2, f1 * f2))
        # deduplicate by (b, g, t mod 2, f mod 2)
        seen, lst = set(), []
        for d, v in sorted(out.items(), key=lambda kv: len(kv[0])):
            key = (v[1], v[2], v[3] % 2, v[4] % 2)
            if key not in seen:
                seen.add(key)
                lst.append((d, v))
        by[m] = lst
    return by


def main():
    rng = random.Random(20261026)
    out = {"1_kernel_gadgets_PSD": {}}
    for (p, s, k, l) in [(3, 2, 2, 1), (3, 3, 2, 2), (5, 2, 2, 1), (3, 3, 3, 1)]:
        worst = fourier_check(p, s, k, l, 20, rng)
        out["1_kernel_gadgets_PSD"][f"F_{p}, x in F^{s}, P in F^{k}, values in F^{l}, 20 random B"] = {
            "min Fourier coefficient": round(worst, 9), "all >= 0": worst > -1e-9}
    print(out["1_kernel_gadgets_PSD"], flush=True)
    rows = {}
    for m, lst in sp_gadgets(4).items():
        for d, (_, b, g, t, f) in lst:
            x, y = 1 + b, 1 + g
            eig = (12 + x + y - 2, x + y - 2, x - y)
            rows[d] = {"edges": m, "(x, y) Hadamard": f"({x}, {y})", "t odd": t % 2 == 1, "f odd": f % 2 == 1,
                       "nonnegative": x >= 0 and y >= 0, "PSD": min(eig) >= 0,
                       "eigenvalues (ones, nu-sym, nu-antisym)": [str(e) for e in eig]}
    out["2_s4_sp_gadgets_up_to_4_edges"] = rows
    keep = {d: r for d, r in rows.items() if r["t odd"] and r["f odd"] and r["nonnegative"] and not r["PSD"]}
    out["2_knot_keeping_nonnegative_non_PSD"] = keep
    print(json.dumps(keep, indent=1))
    (HERE / "ferro_check.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
