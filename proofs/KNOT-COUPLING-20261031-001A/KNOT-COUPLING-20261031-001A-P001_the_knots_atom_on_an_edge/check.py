#!/usr/bin/env python3
"""Checks for KNOT-COUPLING-20261031-001A: the knot's atom on an edge.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (sympy, networkx)."""
import hashlib
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import atom_lib as A  # noqa: E402

T0 = time.time()
OUT = {}
lam = sp.Symbol('lam')
LANE_B = ROOT / "research/NEXT-DIRECTION-SCAN-20261031-001B/fermion.py"


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def poly(coeffs):
    return sp.Poly(list(reversed(coeffs)), lam)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
check("0 dependency artifacts bound by hash", not bad, {"parents": len(manifest["parent_bindings"]), "mismatched": bad})

K4 = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]                          # K4^(3): incidence graph = the cube, colourable (6)
P6 = [(0, 1, 2), (0, 1, 3), (2, 4, 5), (3, 4, 5), (0, 4, 'z'), ('z', 'y', 'w')]   # placeholder, replaced below


def prism_system(n):
    """the cubic triple system whose incidence graph is the circular ladder on 2n vertices (n even): bipartition of nx.circular_ladder_graph"""
    import networkx as nx
    g = nx.circular_ladder_graph(n)
    col = nx.bipartite.color(g)
    return [tuple(sorted(g[v])) for v in sorted(g) if col[v] == 1]


P6 = prism_system(6)
SYSTEMS = {"Fano": A.FANO, "13-point splice": A.SPLICE, "K4^(3) (cube)": K4, "6-prism system": P6}
assert all(A.is_cubic(s) for s in SYSTEMS.values())

# ------------------------------------------------------------------------------------------------ 1. the even-subgraph form
res = {}
for name, H in SYSTEMS.items():
    if len(H) > 7:
        continue
    for neg in (frozenset(), frozenset({A.incidences(H)[0]}), frozenset(A.incidences(H)[:5:2])):
        for l0 in (Fraction(2), Fraction(-1, 2), Fraction(5, 3)):
            res[f"{name}, {len(neg)} negations, lam = {l0}"] = A.even_form(H, l0, neg) == A.evaluate(H, l0, neg)
check("1 even-subgraph form: M = 2^|P| ((lam+3)/4)^|L| sum_chi u^(|chi|/2) (-1)^|sigma & chi|, u = (lam-1)/(lam+3)", all(res.values()),
      {"cases": len(res), "all equal": all(res.values())})

# ------------------------------------------------------------------------------------------------ 2. the atom's edge function
res = {}
for name in ("Fano", "13-point splice", "K4^(3) (cube)"):
    H = SYSTEMS[name]
    ok = True
    for e0 in A.incidences(H):
        for l0 in (Fraction(3), Fraction(-2, 7)):
            g = A.edge_function(H, e0, l0)
            al, be = A.rho_parts(H, e0, l0)
            ok &= g[(0, 0)] == g[(1, 1)] == al and g[(0, 1)] == g[(1, 0)] == be
    res[name] = {"incidences": len(A.incidences(H)), "edge function = [[M(H)/2, M(H^e0)/2], [M(H^e0)/2, M(H)/2]]": ok}
check("2 the atom's edge function is [[alpha, beta], [beta, alpha]], alpha = M(H)/2, beta = M(H with e0 negated)/2", all(
    v["edge function = [[M(H)/2, M(H^e0)/2], [M(H^e0)/2, M(H)/2]]"] for v in res.values()), res)

# ------------------------------------------------------------------------------------------------ 3. decoration and chains
res = {}
atoms = [("Fano", A.FANO, (0, 0)), ("13-point splice", A.SPLICE, A.incidences(A.SPLICE)[0])]
for gname in ("K4^(3) (cube)", "6-prism system"):
    G = SYSTEMS[gname]
    e1, e2 = A.incidences(G)[0], A.incidences(G)[4]
    for aname, H, e0 in atoms:
        for k1, k2 in ((1, 0), (2, 0), (3, 0), (1, 1), (2, 1)):
            if aname == "13-point splice" and k1 + k2 > 2:
                continue
            D = A.chain(G, e1, H, e0, k1, tag="x")
            D = A.chain(D, e2, H, e0, k2, tag="y") if k2 else D
            assert A.is_cubic(D)
            for l0 in (Fraction(2), Fraction(-3, 5)):
                al, be = A.rho_parts(H, e0, l0)
                c = lambda k, s: ((al + be) ** k + s * (al - be) ** k) / 2          # noqa: E731
                pred = 0
                for n1, n2 in itertools.product((0, 1), repeat=2):
                    neg = frozenset({e for e, n in ((e1, n1), (e2, n2)) if n})
                    pred += c(k1, (-1) ** n1) * c(k2, (-1) ** n2) * A.evaluate(G, l0, neg)
                res[f"{gname}, {aname}, chains ({k1}, {k2}), lam = {l0}"] = A.evaluate(D, l0) == pred
check("3 decoration: a chain of k atoms on an incidence acts by ((a+b)^k P+ + (a-b)^k P-), so M(G') = sum over the decorated edges of "
      "products of ((a+b)^k +- (a-b)^k)/2 times M(G with those edges negated)", all(res.values()),
      {"cases": len(res), "all equal": all(res.values())})

# ------------------------------------------------------------------------------------------------ 4. ratios as exact rational functions
POLYS = {}
for aname, H in (("Fano", A.FANO), ("13-point splice", A.SPLICE)):
    MH = poly(A.mono_poly(H))
    classes = {}
    for e0 in A.incidences(H):
        Me = poly(A.mono_poly(H, A.negate(frozenset(), e0)))
        classes.setdefault(str(Me.as_expr()), (e0, Me))
    POLYS[aname] = (MH, classes)
res = {}
for aname, (MH, classes) in POLYS.items():
    for j, (key, (e0, Me)) in enumerate(classes.items()):
        num, den = sp.cancel((MH - Me).as_expr() / (MH + Me).as_expr()).as_numer_denom()
        rho = num / den
        vals = {str(v): str(sp.limit(rho, lam, v) if v == sp.oo else sp.simplify(rho.subs(lam, v))) for v in (0, 1, -1, -3, sp.oo)}
        res[f"{aname}, class {j + 1}"] = {"incidences in class": sum(1 for e in A.incidences(A.FANO if aname == 'Fano' else A.SPLICE)
                                                                      if str(poly(A.mono_poly(A.FANO if aname == 'Fano' else A.SPLICE,
                                                                                              A.negate(frozenset(), e))).as_expr()) == key),
                                          "M(H)": str(MH.as_expr()), "M(H^e0)": str(Me.as_expr()),
                                          "rho": str(sp.factor(rho)), "values at lam = 0, 1, -1, -3, oo": vals}
check("4 ratios: every atom is a negation at the knot's law (rho(0) = -1), degenerate (rho in {0, 1}) at lam = 1, -1 and transparent at "
      "lam = oo; at the dimer coupling lam = -3 every atom has rho = 2", all(
          v["values at lam = 0, 1, -1, -3, oo"]["0"] == "-1" and v["values at lam = 0, 1, -1, -3, oo"]["1"] in ("0", "1")
          and v["values at lam = 0, 1, -1, -3, oo"]["-1"] in ("0", "1") and v["values at lam = 0, 1, -1, -3, oo"]["oo"] == "1"
          and v["values at lam = 0, 1, -1, -3, oo"]["-3"] == "2" for v in res.values()), res)

# ------------------------------------------------------------------------------------------------ 5. the knot's coupling
res = {}
for aname, (MH, classes) in POLYS.items():
    res[aname] = {"M(H; 0) (= #col)": int(MH.eval(0)), "M(H^e0; 0) per class (= #col with e0 negated)": [int(Me.eval(0)) for e0, Me in classes.values()]}
G = K4
found = None
for r in range(1, 4):
    for O in itertools.combinations(A.incidences(G), r):
        if A.evaluate(G, 0, frozenset(O)) == 0:
            found = O
            break
    if found:
        break
dec, dec_bad = G, G
for j, e in enumerate(found):
    dec = A.decorate(dec, e, A.FANO, (0, 0), ('o', j))
dec_bad = A.decorate(G, A.incidences(G)[0], A.FANO, (0, 0), 'b')
al0, be0 = A.rho_parts(A.FANO, (0, 0), 0)
res["K4^(3) decorated on a Pfaffian negation set"] = {"negation set": [list(map(str, e)) for e in found], "#col(G^O)": 0,
                                                       "#col(decorated)": A.evaluate(dec, 0),
                                                       "predicted beta^|O| #col(G^O)": be0 ** len(found) * A.evaluate(G, 0, frozenset(found))}
res["K4^(3) decorated on one incidence (not Pfaffian)"] = {"#col(decorated)": A.evaluate(dec_bad, 0),
                                                            "predicted beta #col(G^e)": be0 * A.evaluate(G, 0, frozenset({A.incidences(G)[0]}))}
ok = (all(v["M(H; 0) (= #col)"] == 0 and all(m != 0 for m in v["M(H^e0; 0) per class (= #col with e0 negated)"]) for k, v in res.items()
          if k in POLYS)
      and al0 == 0 and res["K4^(3) decorated on a Pfaffian negation set"]["#col(decorated)"] == 0
      and res["K4^(3) decorated on one incidence (not Pfaffian)"]["#col(decorated)"] == res["K4^(3) decorated on one incidence (not Pfaffian)"]["predicted beta #col(G^e)"] != 0)
check("5 the knot's coupling: alpha(0) = 0 and beta(0) != 0 for every atom, so an atom is an exact negation; decorating a Pfaffian negation "
      "set gives a knot's space, decorating a non-Pfaffian set does not", ok, res)

# ------------------------------------------------------------------------------------------------ 6. real exceptional points
def exceptional_factors(MH, Me):
    out = {}
    for name, p in (("M(H) [rho = -1]", MH), ("M(H^e0) [rho = 1]", Me), ("M(H) - M(H^e0) [rho = 0]", MH - Me),
                    ("M(H) + M(H^e0) [rho infinite]", MH + Me)):
        for f, m in sp.factor_list(p.as_expr())[1]:
            out.setdefault(str(f), set()).add(name)
    return out


SPECIAL_FACTORS = {"lam", "lam - 1", "lam + 1", "lam + 3"}
fano_MH, fano_classes = POLYS["Fano"]
(fe0, fano_Me), = fano_classes.values()
fano_exc = exceptional_factors(fano_MH, fano_Me)
res = {"Fano exceptional factors (irreducible over Q)": {k: sorted(v) for k, v in fano_exc.items()}}
accidental = [f for f in fano_exc if f not in SPECIAL_FACTORS]
splice_exc = [exceptional_factors(POLYS["13-point splice"][0], Me) for e0, Me in POLYS["13-point splice"][1].values()]
cover = {}
for f in accidental:
    roots = sp.Poly(sp.sympify(f), lam).count_roots()
    cover[f] = {"real roots": roots, "splice classes not exceptional there": [j + 1 for j, ex in enumerate(splice_exc) if f not in ex]}
res["accidental factors of the Fano atom and the splice classes that cover them"] = cover
res["factors exceptional for every atom"] = sorted(set(fano_exc).intersection(*splice_exc))
check("6 real couplings: every irreducible factor where the Fano atom degenerates (rho in {0, 1, -1, oo}), other than lam = 0, 1, -1, is "
      "covered by a splice atom that does not degenerate there; the factors common to all atoms are the special ones",
      all(v["splice classes not exceptional there"] for v in cover.values()) and set(res["factors exceptional for every atom"]) <= SPECIAL_FACTORS,
      res)

# ------------------------------------------------------------------------------------------------ 7. multiplicative independence
def divisor(MH, Me):
    num, den = (MH - Me).as_expr(), (MH + Me).as_expr()
    d = {}
    for f, m in sp.factor_list(num)[1]:
        d[str(f)] = d.get(str(f), 0) + m
    for f, m in sp.factor_list(den)[1]:
        d[str(f)] = d.get(str(f), 0) - m
    d["oo"] = sp.degree(den, lam) - sp.degree(num, lam)
    return d


dF = divisor(fano_MH, fano_Me)
res = {"Fano divisor": dF}
indep = []
for j, (e0, Me) in enumerate(POLYS["13-point splice"][1].values()):
    dS = divisor(POLYS["13-point splice"][0], Me)
    keys = sorted(set(dF) | set(dS))
    rank = sp.Matrix([[dF.get(k, 0) for k in keys], [dS.get(k, 0) for k in keys]]).rank()
    indep.append(rank == 2)
    res[f"splice class {j + 1} divisor"] = dS
res["rank 2 (no relation rho_F^a rho_S^b = const) for every splice class"] = indep
check("7 the Fano and splice ratios are multiplicatively independent (their divisors have rank 2)", all(indep), res)

# ------------------------------------------------------------------------------------------------ 8. the dimer coupling lam = -3
res = {}
for name in ("Fano", "13-point splice"):
    H = SYSTEMS[name]
    pm = A.pm_count(A.incidence_graph(H))
    res[name] = {"M(H; -3)": A.evaluate(H, -3), "(-2)^|P| #PM": (-2) ** len(A.points(H)) * pm, "#PM": pm, "|det|": abs(A.signed_det(H))}
for name in ("K4^(3) (cube)", "6-prism system"):
    H = SYSTEMS[name]
    pm = A.pm_count(A.incidence_graph(H))
    res[name + " (colourable control)"] = {"M(H; -3)": A.evaluate(H, -3), "(-2)^|P| #PM": (-2) ** len(A.points(H)) * pm, "#PM": pm,
                                           "|det|": abs(A.signed_det(H))}
# a signed knot's class: K4^(3) with the Pfaffian negation set found in section 5
pm = A.pm_count(A.incidence_graph(K4))
res["K4^(3) with a Pfaffian signing"] = {"M(H, kappa; -3)": A.evaluate(K4, -3, frozenset(found)), "|det of the plain matrix| (-2)^|P|":
                                         abs(A.signed_det(K4)) * 2 ** 4, "#PM": pm}
ok = (all(v["M(H; -3)"] == v["(-2)^|P| #PM"] for v in res.values() if "M(H; -3)" in v)
      and all(v["#PM"] == v["|det|"] for k, v in res.items() if k in ("Fano", "13-point splice"))
      and all(v["#PM"] != v["|det|"] for k, v in res.items() if "control" in k)
      and abs(res["K4^(3) with a Pfaffian signing"]["M(H, kappa; -3)"]) == res["K4^(3) with a Pfaffian signing"]["|det of the plain matrix| (-2)^|P|"])
check("8 the dimer coupling lam = -3 (u = oo): M(H; -3) = (-2)^|P| #PM of the incidence graph for plain systems, a determinant on the "
      "knot's spaces (#PM = |det|) but not on the colourable controls; with a Pfaffian signing it is (-2)^|P| det of the plain matrix "
      "up to sign", ok, res)

# ------------------------------------------------------------------------------------------------ 9. correction of the scan's lane B
src = LANE_B.read_text()
src = src[:src.index("# ------------------------------------------------------------------------------------------------ 1.")]
ns = {"__file__": str(LANE_B), "__name__": "laneB"}
exec(compile(src, str(LANE_B), "exec"), ns)
x = ns["x"]
sq = lambda n: {('sq', n, k) for k in range(4)}  # noqa: E731
cubeS = ns["squares_of"](ns["PAGES"]["cube"])[0]
SHAPES = [("6-prism", ("cube", "cube")), ("6-prism", ("cube", "6-prism")), ("truncated octahedron", ("cube", "cube"))]


def two_square_page(name):
    g = ns["PAGES"][name]
    sqs = ns["squares_of"](g)
    return g, sqs[0], next(T for T in sqs if not set(T) & set(sqs[0]))


def depth_two_parts(tag, page, kids, n_parent, n_child):
    g, S1, S2 = two_square_page(page)
    out = [(tag, g, [S1, S2], [n_parent, n_child])]
    for j, k in enumerate(kids):
        out.append((tag + str(j), ns["PAGES"][k], [ns["squares_of"](ns["PAGES"][k])[0]], [n_child]))
    return out


res = {}
for (pq, kq), (pr, kr) in itertools.combinations_with_replacement(SHAPES, 2):
    parts = [('h', ns["PAGES"]["cube"], [cubeS], [0])] + depth_two_parts('q', pq, kq, 0, 1) + depth_two_parts('r', pr, kr, 0, 2)
    leaves, Gg = ns["glue"](parts)
    kappa = ns["TW"].kasteleyn_tree_signing(leaves)
    tags = lambda t: {v for v in Gg if isinstance(v[0], str) and v[0].startswith(t)}  # noqa: E731
    BQ, S = ns["branch_graph"](Gg, 0, tags('q') | sq(1))
    BR, _ = ns["branch_graph"](Gg, 0, tags('r') | sq(2))
    W = ns["junction"](ns["branch_tensor"](BQ, S, kappa), ns["branch_tensor"](BR, S, kappa))
    d = max(sp.degree(v, x) for v in W.values() if v != 0)
    m = sp.expand(ns["mgi"](W))
    res[f"{pq}{list(kq)} x {pr}{list(kr)}"] = {"MGI identically 0": m == 0, "max entry degree": d,
                                               "degree of MGI": None if m == 0 else sp.degree(m, x),
                                               "vanishes at u = oo (degree < 2 max)": m == 0 or sp.degree(m, x) < 2 * d}
check("9 correction of NEXT-DIRECTION-SCAN-20261031-001B: every deep-branch junction also satisfies the matchgate identity at u = oo, the "
      "dimer coupling, so the couplings common to the breaking junctions are the counting point, the affine ones and u = oo",
      all(v["vanishes at u = oo (degree < 2 max)"] for v in res.values()), res)

# ------------------------------------------------------------------------------------------------ 10. controls
al_c, be_c = A.rho_parts(K4, A.incidences(K4)[0], 0)
rho_F = lambda v: (lambda a, b: (a - b) / (a + b))(*A.rho_parts(A.FANO, (0, 0), v))  # noqa: E731
even_on_O = A.decorate(A.decorate(K4, found[0], A.FANO, (0, 0), 'e1'), (found[0][0], ('e1', 0)), A.FANO, (0, 0), 'e2')
for j, e in enumerate(found[1:]):
    even_on_O = A.decorate(even_on_O, e, A.FANO, (0, 0), ('f', j))
controls = {"a colourable atom (K4^(3) minus an incidence) is not a negation at lam = 0 (alpha != 0)": al_c != 0,
            "an even chain on one negation-set edge leaves the class (colourable)": A.evaluate(even_on_O, 0) != 0,
            "rho_Fano at lam = 1/2 is not 0 or +-1": rho_F(Fraction(1, 2)) not in (0, 1, -1),
            "rho_Fano(1/2)": str(rho_F(Fraction(1, 2)))}
check("10 controls fire", all(v for k, v in controls.items() if not k.startswith("rho_Fano(")), controls)

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
