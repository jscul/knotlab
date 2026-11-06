#!/usr/bin/env python3
"""Checks for PARITY-CORRECTION-20261031-001A: parity's coupling family is #P-hard except at six points.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (sympy)."""
import hashlib
import itertools
import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import parity_lib as L  # noqa: E402
from parity_lib import GQ  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings and upstream results
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
check("0 dependency artifacts bound by hash", not bad, {"parents": len(manifest["parent_bindings"]), "mismatched": bad})
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(("/manifest.json", "/result.json"))}
msb = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001B/manifest.json").read_text())
corrected = "its whole coupling family [1, lam, 1, lam] is a generalized equality (affine) for every lam"
check("1 upstream proofs are Proved and their checks passed; the corrected record (lane B) states the claim withdrawn here",
      all(s in ("Proved", "passed", "Complete") for s in status.values()) and corrected in msb["claim"],
      {"statuses": status, "withdrawn sentence (lane B manifest)": corrected})

# ------------------------------------------------------------------------------------------------ 2. the error
lam, x = sp.symbols("lam x")
f = [1, lam, 1, lam]                                  # parity's line weight by Hamming weight
cube = list(itertools.product((0, 1), repeat=3))
fhat = {s: sp.expand(sum(f[sum(v)] * (-1) ** sum(si * vi for si, vi in zip(s, v)) for v in cube)) for s in cube}
eq3 = {v: 1 if v in ((0, 0, 0), (1, 1, 1)) else 0 for v in cube}
eqhat = {s: sp.Rational(1, 8) * sum(eq3[v] * (-1) ** sum(si * vi for si, vi in zip(s, v)) for v in cube) for s in cube}
line_ok = all(fhat[s] == 0 for s in cube if s not in ((0, 0, 0), (1, 1, 1))) and fhat[(0, 0, 0)] == 4 * (1 + lam) \
    and sp.expand(fhat[(1, 1, 1)] - 4 * (1 - lam)) == 0
point_ok = all(eqhat[s] == (sp.Rational(1, 4) if sum(s) % 2 == 0 else 0) for s in cube)
check("2a the Hadamard change of basis makes each line a generalized equality but each point an even-parity check, not an equality",
      line_ok and point_ok, {"line [1, lam, 1, lam] becomes": {"000": str(fhat[(0, 0, 0)]), "111": str(fhat[(1, 1, 1)]), "others": 0},
                             "point equality becomes (inverse transform)": {"even weight": "1/4", "odd weight": 0},
                             "lane B's error": "it transformed the lines only; with the points transformed too the count is a code "
                                               "weight enumerator, not a product of generalized equalities"})

census = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
graphs = [(int(n), [tuple(l) for l in row["lines"]]) for n, block in sorted(census.items(), key=lambda kv: int(kv[0]))
          for row in block["rows"]]
rng = random.Random(20261031)


def poly_coeffs(expr, deg):
    p = sp.Poly(sp.expand(expr), lam)
    return [int(p.coeff_monomial(lam ** k)) for k in range(deg + 1)]


tested, mismatches, not_two_term = 0, [], 0
for n, lines in graphs:
    signings = [[0] * n] + [[rng.randint(0, 1) for _ in range(n)] for _ in range(3)]
    D = L.reduce_basis(L.line_masks_of_points(lines))
    r = len(D)
    kb = L.kernel_basis(lines)
    kernel = [0]
    for v in kb:
        kernel += [w ^ v for w in kernel]
    assert len(kernel) == 2 ** (n - r)
    for signs in signings:
        b = sum(bit << i for i, bit in enumerate(signs))
        dist = L.distribution(lines, signs)
        coset = [0] * (n + 1)
        for d in L.span(D):
            coset[L.popcount(d ^ b)] += 2 ** (n - r)
        dual = poly_coeffs(sum((-1) ** (L.popcount(s & b) & 1) * (1 + lam) ** (n - L.popcount(s)) * (1 - lam) ** L.popcount(s)
                               for s in kernel), n)
        tested += 1
        if not (dist == coset == dual):
            mismatches.append((n, lines, signs))
    # what lane B implicitly used: points unchanged by the transform, i.e. the code {nothing, all lines} instead of ker N
    two_term = poly_coeffs((1 + lam) ** n + (1 - lam) ** n, n)
    true = L.distribution(lines)
    not_two_term += any(true[k] * two_term[0] != two_term[k] * true[0] for k in range(n + 1))
check("2b on every census graph (60, n <= 8) with four signings each, the count is the coset and the dual weight enumerator: "
      "M = 2^(n-r) sum_{d in b+D} lam^|d| = sum_{s in ker N} (-1)^(b.s) (1+lam)^(n-|s|) (1-lam)^|s|",
      not mismatches and tested == 240, {"systems x signings": tested, "mismatches": mismatches[:2]})
check("2c the one-sided transform's prediction (proportional to (1+lam)^n + (1-lam)^n) is wrong on every census graph",
      not_two_term == len(graphs), {"graphs where the true count is not proportional to the two-term prediction": not_two_term,
                                     "graphs": len(graphs), "Fano": {"true": "(1+lam)^7 + 7 (1+lam)^3 (1-lam)^4",
                                                                      "lane B's implicit": "(1+lam)^7 + (1-lam)^7"}})

# ------------------------------------------------------------------------------------------------ 3. Fan and Cai, Theorem 2.2
X = [sp.Integer(1), lam, sp.Integer(1), lam]
degenerate = sp.solve([X[0] * X[2] - X[1] ** 2, X[1] * X[3] - X[2] ** 2, X[0] * X[3] - X[1] * X[2]], lam, dict=True)
case2 = sp.solve([X[1], X[2]], lam, dict=True)
case3a = sp.solve([X[1], X[3], X[0] - X[2]], lam, dict=True)
case3b = sp.solve([X[0], X[2], X[1] - X[3]], lam, dict=True)
deg_set = sorted(d[lam] for d in degenerate)
ok3 = deg_set == [-1, 1] and case2 == [] and case3a == [{lam: 0}] and case3b == []
check("3a Fan-Cai Theorem 2.2 (nonnegative [x0, x1, x2, x3] with (=3)): for lam >= 0, [1, lam, 1, lam] is tractable only at lam = 1 "
      "(degenerate) and lam = 0 (case 3, affine); #P-hard for every real lam > 0, lam != 1", ok3,
      {"degenerate at": [str(v) for v in deg_set], "case 2 (x1 = x2 = 0)": "never", "case 3": "lam = 0 only",
       "source": "arXiv 2011.09110, Theorem 2.2 (PDF p. 5) and Lemma 4.2 case 3 (PDF p. 8)"})
# gadget G4 of Lemma 4.2 case 3: two (=3) circles, each joined to all three squares [1, a, 1, a]; one dangling edge per square
G4 = []
for xs in cube:
    G4.append(sp.expand(sum(sp.Mul(*[(lam if (u + v + xi) % 2 else 1) for xi in xs]) for u in (0, 1) for v in (0, 1))))
G4_sym = [G4[0], G4[1], G4[3], G4[7]]                  # weights 0, 1, 2, 3 (inputs 000, 100, 110, 111)
expected = [2 + 2 * lam ** 3, 2 * lam + 2 * lam ** 2, 2 * lam + 2 * lam ** 2, 2 + 2 * lam ** 3]
symmetric = all(sp.expand(G4[i] - G4_sym[sum(cube[i])]) == 0 for i in range(8))
aprime = sp.simplify((2 * lam + 2 * lam ** 2) / (2 + 2 * lam ** 3))
check("3b their gadget G4 is the theta substitution read on one line, with signature [2+2a^3, 2a+2a^2, 2a+2a^2, 2+2a^3]; Lemma 4.1's "
      "parameter a' = a/(a^2 - a + 1) is 0 or 1 only at a = 0 or 1",
      symmetric and all(sp.expand(g - e) == 0 for g, e in zip(G4_sym, expected))
      and sp.simplify(aprime - lam / (lam ** 2 - lam + 1)) == 0
      and sorted(sp.solve(sp.numer(sp.together(aprime - 1)), lam)) == [1] and sp.solve(sp.numer(sp.together(aprime)), lam) == [0],
      {"signature": [str(g) for g in G4_sym], "a'": str(sp.factor(aprime)),
       "shape": "squares = the three new lines {x_i, u, v}; circles = the two new points u, v"})

# ------------------------------------------------------------------------------------------------ 4. the theta substitution
lp = lam + 1 / lam - 1
per_line = []
for xs in cube:
    val = sp.expand(sum(sp.Mul(*[(lam if (u + v + xi) % 2 else 1) for xi in xs]) for u in (0, 1) for v in (0, 1)))
    mono = len(set(xs)) == 1
    per_line.append(sp.simplify(val - 2 * lam * (1 + lam) * (lp if mono else 1)) == 0)
u_nae = sp.simplify((lp - 1) / (lp + 3) - ((lam - 1) / (lam + 1)) ** 2)
check("4a per line: sum over the two new points of the three parity weights = 2 lam (1+lam) times lam' on a monochromatic line, "
      "1 otherwise, with lam' = lam + 1/lam - 1; in the knot's even-form variable u = (lam'-1)/(lam'+3) = ((lam-1)/(lam+1))^2",
      all(per_line) and u_nae == 0, {"lam'": "lam + 1/lam - 1 = (lam^2 - lam + 1)/lam",
                                      "u(lam')": "((lam - 1)/(lam + 1))^2, the square of parity's Hadamard ratio"})


def splice13():
    """the 13-point Fano splice of KNOT-COUPLING-20261031-001A (point splice of Fano at its line (0,1,2) into Fano at point 0)"""
    F = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
    M, out, k = F[0], [], 0
    for l in F:
        if 0 in l:
            out.append(tuple(("s", M[k]) if q == 0 else ("a", q) for q in l))
            k += 1
        else:
            out.append(tuple(("a", q) for q in l))
    out += [tuple(("s", q) for q in l) for l in F if tuple(l) != tuple(M)]
    labels = {p: i for i, p in enumerate(sorted({p for l in out for p in l}))}
    return [tuple(labels[p] for p in l) for l in out]


FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
SPLICE = splice13()
struct_bad = [lines for n, lines in graphs
              if not (L.is_cubic(L.theta(lines)) and L.is_simple(L.theta(lines)) and not L.has_repeated_lines(L.theta(lines))
                      and L.is_connected(L.theta(lines)) == L.is_connected(lines))]
check("4b theta maps every census graph, and the knot's spaces Fano and the 13-point splice, to a connected simple cubic system "
      "without repeated lines; the two knot's spaces fail not-all-equal",
      not struct_bad and all(L.is_cubic(L.theta(H)) and L.is_simple(L.theta(H)) and not L.has_repeated_lines(L.theta(H))
                             and L.is_connected(L.theta(H)) for H in (FANO, SPLICE))
      and L.m_nae(FANO, Fraction(0), L.brute) == 0 and L.m_nae(SPLICE, Fraction(0), L.brute) == 0,
      {"census graphs": len(graphs), "bad": struct_bad[:1], "splice lines": len(SPLICE)})

LAMS = [Fraction(2), Fraction(1, 3), Fraction(-2), Fraction(5, 7), GQ(1, 1), GQ(Fraction(-3, 2), Fraction(1, 2))]
hosts = [(f"census n={n} #{i}", lines) for i, (n, lines) in enumerate(graphs) if n <= 7] + [("Fano", FANO), ("splice", SPLICE)]
theta_bad, theta_n = [], 0
for name, H in hosts:
    T = L.theta(H)
    for lv in LAMS:
        lhs = L.m_par(T, lv)
        rhs = (2 * lv * (1 + lv)) ** len(H) * L.m_nae(H, lv + 1 / lv - 1, L.brute)
        theta_n += 1
        if not lhs == rhs:
            theta_bad.append((name, L.show(lv), L.show(lhs), L.show(rhs)))
sample = {L.show(lv): L.show(L.m_par(L.theta(FANO), lv)) for lv in LAMS[:2]}
check("4c theta identity M_par(theta H; lam) = (2 lam (1+lam))^n M_nae(H; lam + 1/lam - 1), exact, on all census graphs with n <= 7, "
      "Fano and the splice, at four real and two complex couplings", not theta_bad and theta_n == len(hosts) * len(LAMS),
      {"evaluations": theta_n, "failures": theta_bad[:2], "Fano sample M_par(theta Fano; lam)": sample,
       "method": "left side by variable elimination on theta H (up to 39 points); right side by brute force on H"})

# ------------------------------------------------------------------------------------------------ 5. the six easy points
easy_bad, easy_n = [], 0
for n, lines in graphs:
    for signs in [[0] * n] + [[rng.randint(0, 1) for _ in range(n)] for _ in range(3)]:
        dist = L.distribution(lines, signs)
        D = L.reduce_basis(L.line_masks_of_points(lines))
        r = len(D)
        b = sum(bit << i for i, bit in enumerate(signs))
        ones = (1 << n) - 1
        at = {"0": dist[0] == 2 ** (n - r) * L.in_span(D, b),
              "1": sum(dist) == 2 ** n,
              "-1": sum((-1) ** k * c for k, c in enumerate(dist)) == 0,
              "oo (top coefficient)": dist[n] == 2 ** (n - r) * L.in_span(D, b ^ ones)}
        for sign in (1, -1):
            direct = sum((c * (sign * L.I) ** k for k, c in enumerate(dist)), GQ(0))
            at[f"{'' if sign == 1 else '-'}i (Gauss sum over ker N)"] = L.m_par_at_i(lines, signs, sign) == direct
        easy_n += 1
        if not all(at.values()):
            easy_bad.append((n, lines, signs, at))
form_bad = 0
for t in range(300):
    k = rng.randint(1, 8)
    a = [rng.randint(0, 3) for _ in range(k)]
    c = [[0] * k for _ in range(k)]
    for j, l in itertools.combinations(range(k), 2):
        c[j][l] = c[l][j] = rng.randint(0, 1)
    brute = sum((L.I ** sum(a[j] * u[j] for j in range(k)) * (-1) ** sum(c[j][l] * u[j] * u[l] for j, l in itertools.combinations(range(k), 2))
                 for u in itertools.product((0, 1), repeat=k)), GQ(0))
    form_bad += not (L.gauss_sum(a, c) == brute)
affine_ok = all((1 if sum(v) % 2 == 0 else s * L.I) == (s * L.I) ** sum(v) * (-1) ** (v[0] * v[1] + v[0] * v[2] + v[1] * v[2])
                for v in cube for s in (1, -1))
check("5 the six easy points: lam = 0 and oo (2^(n-r) or 0, Gaussian elimination), 1 (2^n), -1 (0), and +-i (affine: [1, i, 1, i] = "
      "i^(x+y+z) (-1)^(xy+xz+yz); evaluated by a polynomial Gauss sum over a basis of ker N), checked on every census graph with "
      "four signings, and the Gauss sum on 300 random quadratic forms",
      not easy_bad and easy_n == 240 and form_bad == 0 and affine_ok,
      {"systems x signings": easy_n, "failures": easy_bad[:1], "random forms failing": form_bad, "affine form of [1, +-i, 1, +-i]": affine_ok})

# ------------------------------------------------------------------------------------------------ 6. the case analysis
cases = {}
for c, label in ((0, "2-colourings (lam' = 0)"), (1, "trivial (lam' = 1)"), (-1, "lam' = -1 (easy for the knot)"),
                 (-3, "dimer (lam' = -3)")):
    cases[label] = sorted((sp.nsimplify(s) for s in sp.solve(lam ** 2 - (c + 1) * lam + 1, lam)), key=str)
zeros = sorted(sp.solve(2 * lam * (1 + lam), lam))
omega = sp.exp(sp.I * sp.pi / 3)
ok6 = cases["trivial (lam' = 1)"] == [1] and sorted(cases["lam' = -1 (easy for the knot)"], key=str) == sorted([sp.I, -sp.I], key=str) \
    and cases["dimer (lam' = -3)"] == [-1] and zeros == [-1, 0] \
    and set(cases["2-colourings (lam' = 0)"]) == {sp.expand_complex(omega), sp.expand_complex(sp.conjugate(omega))}
check("6 case analysis: lam' = lam + 1/lam - 1 is an easy point of the knot's coupling ({1, -1, -3, oo}) or 0 exactly when lam is in "
      "{1}, {i, -i}, {-1}, {0, oo} or {e^(+-i pi/3)}; the factor 2 lam (1+lam) vanishes only at 0, -1. So: lam' outside "
      "{0, 1, -1, -3, oo} -> #P-hard by KNOT-COUPLING (knot's spaces); lam = e^(+-i pi/3) -> lam' = 0, #P-hard by PLAIN-COUNT A "
      "(2-colourings); the rest are the six easy points", ok6,
      {"solutions": {k: [str(s) for s in v] for k, v in cases.items()}, "2 lam (1+lam) = 0 at": [str(z) for z in zeros],
       "easy points": ["0", "1", "-1", "i", "-i", "oo"]})

# ------------------------------------------------------------------------------------------------ 7. controls
wrong = L.m_par(L.theta(FANO), Fraction(2)) == (2 * 2 * 3) ** 7 * L.m_nae(FANO, Fraction(2), L.brute)
check("7 controls: the theta identity fails with lam' = lam (Fano, lam = 2); the one-sided transform fails (check 2c)", not wrong,
      {"theta with lam' = lam holds": wrong})

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
