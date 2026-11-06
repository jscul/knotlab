#!/usr/bin/env python3
"""Checks for KNOT-COUPLING-20261031-001C: the complex couplings.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (sympy, mpmath)."""
import hashlib
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = ROOT / "proofs/KNOT-COUPLING-20261031-001A/KNOT-COUPLING-20261031-001A-P001_the_knots_atom_on_an_edge"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(A_DIR))
import atom_lib as A  # noqa: E402
import torsion_lib as T  # noqa: E402
from torsion_lib import lam, X, Y  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def mpoly(H, neg=frozenset()):
    return sp.Poly(list(reversed(A.mono_poly(H, neg))), lam).as_expr()


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
check("0 dependency artifacts bound by hash", not bad, {"parents": len(manifest["parent_bindings"]), "mismatched": bad})

# ------------------------------------------------------------------------------------------------ 1. the two ratios
MF, MFe = mpoly(A.FANO), mpoly(A.FANO, A.negate(frozenset(), (0, 0)))
classes = {}
for e0 in A.incidences(A.SPLICE):
    classes.setdefault(str(mpoly(A.SPLICE, A.negate(frozenset(), e0))), []).append(e0)
e12 = next(v[0] for v in classes.values() if len(v) == 12)
MS, MSe = mpoly(A.SPLICE), mpoly(A.SPLICE, A.negate(frozenset(), e12))
nF, dF = T.ratio_polys(MF, MFe)
nS, dS = T.ratio_polys(MS, MSe)
a_res = json.loads((A_DIR / "result.json").read_text())["checks"]
a_rhos = {k: v["rho"] for k, v in next(c for n, c in a_res.items() if n.startswith("4 "))["info"].items()}
ok = (sp.simplify(sp.sympify(a_rhos["Fano, class 1"]) - nF.as_expr() / dF.as_expr()) == 0
      and any(sp.simplify(sp.sympify(r) - nS.as_expr() / dS.as_expr()) == 0 for r in a_rhos.values()))
check("1 the two ratios (the Fano atom, and the splice class with 12 incidences) agree with ticket A", ok,
      {"rho_F": str(sp.factor(nF.as_expr() / dF.as_expr())), "rho_S": str(sp.factor(nS.as_expr() / dS.as_expr())), "splice incidence": str(e12)})

# ------------------------------------------------------------------------------------------------ 2. the curve
f = T.implicit_curve(nF, dF, nS, dS)
fl = sp.factor_list(f.as_expr())
check("2 the curve f(X, Y) = Res_lam(X dF - nF, Y dS - nS) is irreducible over Q of bidegree (13, 7); by ticket A (Proposition 7) the ratios "
      "are multiplicatively independent, so it is not a torsion coset and has finitely many torsion points (Lang; Ihara, Serre, Tate)",
      len(fl[1]) == 1 and fl[1][0][1] == 1 and f.degree(X) == 13 and f.degree(Y) == 7,
      {"bidegree": [f.degree(X), f.degree(Y)], "terms": len(f.terms())})

# ------------------------------------------------------------------------------------------------ 3. Beukers-Smyth
res, allx, ally = {}, {}, {}
for name, g in T.variants(f).items():
    rx = sp.Poly(sp.resultant(f.as_expr(), g, Y), X)
    ry = sp.Poly(sp.resultant(f.as_expr(), g, X), Y)
    mx = T.cyclotomic_factors(rx, X)
    my = T.cyclotomic_factors(ry, Y)
    allx[name], ally[name] = mx, my
    res[name] = {"resultant degrees (X, Y)": [rx.degree(), ry.degree()], "f divides g": rx.is_zero or ry.is_zero,
                 "m with Phi_m | Res_Y": mx, "m with Phi_m | Res_X": my}
check("3 Beukers-Smyth (Lemma 1): for each of the seven substitutions g, f does not divide g, and the cyclotomic factors of the resultants "
      "(filtered at roots of unity in finite fields, confirmed by exact division) are Phi_1 and Phi_2 only", all(
          not v["f divides g"] and set(v["m with Phi_m | Res_Y"]) <= {1, 2} and set(v["m with Phi_m | Res_X"]) <= {1, 2} for v in res.values()),
      res)

# ------------------------------------------------------------------------------------------------ 4. the torsion points
pts = set()
for name in allx:
    for mx in allx[name]:
        for my in ally[name]:
            for pt in T.torsion_points_numeric(f, mx, my):
                pts.add(pt)
torsion = sorted(p for p in pts if p[2])
check("4 the torsion points of the curve are exactly (1, 1) and (-1, -1)", [(a, b) for a, b, _ in torsion] == [((0, 1), (0, 1)), ((1, 2), (1, 2))],
      {"torsion points (a/m for X, b/m for Y)": [[f"{a[0]}/{a[1]}", f"{b[0]}/{b[1]}"] for a, b, _ in torsion]})

# ------------------------------------------------------------------------------------------------ 5. back to the coupling
g_minus = sp.gcd(sp.Poly(MF, lam), sp.Poly(MS, lam))          # rho = -1  <=>  M = 0
g_plus = sp.gcd(sp.Poly(MFe, lam), sp.Poly(MSe, lam))         # rho = +1  <=>  M^e0 = 0
info = {"gcd(M_F, M_S) (both ratios -1)": str(g_minus.as_expr()), "gcd(M_F^e, M_S^e) (both ratios +1)": str(g_plus.as_expr()),
        "limits at lam = oo": [str(sp.limit(nF.as_expr() / dF.as_expr(), lam, sp.oo)), str(sp.limit(nS.as_expr() / dS.as_expr(), lam, sp.oo))]}
check("5 the torsion points come from lam = 0 ((-1, -1)) and lam = oo ((1, 1)) only", g_minus.monic().as_expr() == lam
      and g_plus.degree() == 0 and info["limits at lam = oo"] == ["1", "1"], info)

# ------------------------------------------------------------------------------------------------ 6. zeros and poles
def other_values(phi, n_other, d_other):
    """the polynomial whose roots are the other ratio at the roots of phi, and whether that ratio is 0, infinite or torsion there"""
    if sp.rem(sp.Poly(n_other, lam), sp.Poly(phi, lam)).is_zero:
        return "0"
    if sp.rem(sp.Poly(d_other, lam), sp.Poly(phi, lam)).is_zero:
        return "infinite"
    P = sp.Poly(sp.resultant(phi, Y * d_other - n_other, lam), Y)
    ms = T.cyclotomic_factors(P, Y)
    return "torsion " + str(ms) if ms else "finite, nonzero, not torsion"


res = {}
for label, num, den, n_o, d_o in (("zeros of rho_F", nF, None, nS.as_expr(), dS.as_expr()), ("poles of rho_F", None, dF, nS.as_expr(), dS.as_expr()),
                                  ("zeros of rho_S", nS, None, nF.as_expr(), dF.as_expr()), ("poles of rho_S", None, dS, nF.as_expr(), dF.as_expr())):
    poly = num if num is not None else den
    for phi, m in sp.factor_list(poly.as_expr())[1]:
        if sp.degree(phi, lam) == 0:
            continue
        res[f"{label}: {phi}"] = other_values(phi, n_o, d_o)
bad_factors = sorted(k for k, v in res.items() if v != "finite, nonzero, not torsion")
check("6 where one ratio is 0 or infinite, the other is finite, nonzero and of infinite order, except at lam = 1 and lam = -1 (both 0)",
      all(k.endswith(": lam - 1") or k.endswith(": lam + 1") for k in bad_factors), {"cases": res, "bad": bad_factors})

# ------------------------------------------------------------------------------------------------ 7. deficiency one over C
polys = []
for Ldel in range(1, 7):
    Hm = [l for k, l in enumerate(A.FANO) if k != Ldel]
    pa = mpoly(Hm) / 2
    pb = mpoly(Hm, frozenset({(0, 0)})) / 2
    polys.append(sp.Poly(sp.expand((pa + pb) * (pa - pb)), lam))
common = polys[0]
for q in polys[1:]:
    common = sp.gcd(common, q)
check("7 deficiency one: the six line-deleted Fano atoms degenerate together only where their gcd vanishes, and its roots lie in "
      "{0, 1, -1, -3}", all(sp.Poly(phi, lam).degree() == 1 and sp.solve(phi, lam)[0] in (0, 1, -1, -3)
                             for phi, m in sp.factor_list(common.as_expr())[1] if sp.degree(phi, lam) > 0),
      {"gcd": str(sp.factor(common.as_expr()))})

# ------------------------------------------------------------------------------------------------ 8. controls
dep = T.implicit_curve(nF, dF, sp.Poly((nF.as_expr()) ** 2, lam), sp.Poly((dF.as_expr()) ** 2, lam))
dep_irreducible = sp.factor_list(dep.as_expr())[1]
controls = {"a dependent pair (rho_F, rho_F^2) gives the curve Y = X^2, a subtorus": str(sp.factor(dep_irreducible[0][0])),
            "lam = 0 is found as the torsion point (-1, -1)": ((1, 2), (1, 2), True) in torsion,
            "the special values: rho_F(0) = rho_S(0) = -1": [str(sp.simplify((nF.as_expr() / dF.as_expr()).subs(lam, 0))),
                                                             str(sp.simplify((nS.as_expr() / dS.as_expr()).subs(lam, 0)))]}
ok = (sp.expand(dep_irreducible[0][0] - (Y - X ** 2)) == 0 or sp.expand(dep_irreducible[0][0] + (Y - X ** 2)) == 0) and \
    controls["lam = 0 is found as the torsion point (-1, -1)"] and controls["the special values: rho_F(0) = rho_S(0) = -1"] == ["-1", "-1"]
check("8 controls: a dependent pair gives a subtorus (infinitely many torsion points), and the known torsion point at lam = 0 is found", ok,
      controls)

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
