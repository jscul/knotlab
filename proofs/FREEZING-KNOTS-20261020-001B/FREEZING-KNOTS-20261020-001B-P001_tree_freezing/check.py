#!/usr/bin/env python3
"""Checks for FREEZING-KNOTS-20261020-001B-P001: star knots stop being native at the tree's freezing threshold.

Arithmetic is exact (fractions) for every certificate.

- Below the threshold (d = d_f - 1): h(p) = (Phi(p) - p) / p is negative on
  [0, 1]. This is certified by Bernstein coefficients, with subdivision at the
  midpoint when needed. So Phi(p) < p on (0, 1], and p* = 0.
- At the threshold (d = d_f): a rational r with Phi(r) >= r, so p* >= r. This
  gives an exact upper bound on the star knot's nativity there.
- Monotonicity in d (proved by coupling in proof.md) is spot-checked on a grid.
- The star relation (q-tuples that do not use all q colours) passes K1-K3 for
  q = 3, 4, 5.
- The nativity formula, computed here, agrees with the tree table of
  FREEZING-KNOTS-20261020-001A-E001.

Mutations: certifying one degree lower as frozen, or the threshold degree as
unfrozen, must fail.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPERIMENT = ROOT / "artifacts/FREEZING-KNOTS-20261020-001A/FREEZING-KNOTS-20261020-001A-E001_freezing_census/result.json"
THRESHOLDS = {3: 6, 4: 10, 5: 15}


def binom_poly(c, k):
    """Coefficients of (1 - c p)^k."""
    return [Fraction(comb(k, i)) * (-c) ** i for i in range(k + 1)]


def cover_poly(need, k, total):
    """Coefficients (in p) of sum_j (-1)^j C(need, j) (1 - j p / total)^k."""
    out = [Fraction(0)] * (k + 1)
    for j in range(need + 1):
        for i, a in enumerate(binom_poly(Fraction(j, total), k)):
            out[i] += (-1) ** j * comb(need, j) * a
    return out


def evaluate(coeffs, p):
    return sum(a * p ** i for i, a in enumerate(coeffs))


def phi(q, d):
    return cover_poly(q - 1, d - 1, q - 1)


def bernstein(coeffs):
    m = len(coeffs) - 1
    return [sum(Fraction(comb(k, i), comb(m, i)) * coeffs[i] for i in range(k + 1)) for k in range(m + 1)]


def split(b):
    left, right, row = [b[0]], [b[-1]], list(b)
    while len(row) > 1:
        row = [(x + y) / 2 for x, y in zip(row, row[1:])]
        left.append(row[0])
        right.append(row[-1])
    return left, right[::-1]


def certify_negative(b, depth=0, max_depth=14):
    """True if the polynomial with Bernstein coefficients b is negative on its whole interval."""
    if max(b) < 0:
        return True
    if b[0] >= 0 or b[-1] >= 0 or depth == max_depth:
        return False
    left, right = split(b)
    return certify_negative(left, depth + 1, max_depth) and certify_negative(right, depth + 1, max_depth)


def below_certificate(q, d):
    """Certify Phi(p) < p on (0, 1] for this (q, d)."""
    f = phi(q, d)
    f[1] -= 1
    if f[0] != 0:
        return False
    h = f[1:]
    return certify_negative(bernstein(h))


def witness(q, d, grid=1000):
    """The largest r = k/grid with Phi(r) >= r, or None."""
    f = phi(q, d)
    for k in range(grid - 1, 0, -1):
        r = Fraction(k, grid)
        if evaluate(f, r) >= r:
            return r
    return None


def star_bound(q, d, r):
    """Upper bound on the star nativity when p* >= r: max((1 - r)^q, (1 - mu(r))^q)."""
    mu = evaluate(cover_poly(q - 2, d - 1, q - 1), r)
    return max((1 - r) ** q, (1 - mu) ** q)


def star_formula(q, d, iters=20000):
    p = 1.0
    for _ in range(iters):
        p = sum((-1) ** j * comb(q - 1, j) * (1 - j * p / (q - 1)) ** (d - 1) for j in range(q))
    p = max(p, 0.0)
    mu = sum((-1) ** j * comb(q - 2, j) * (1 - j * p / (q - 1)) ** (d - 1) for j in range(q - 1))
    zeta = sum((-1) ** j * comb(q - 1, j) * (1 - j * p / (q - 1)) ** (d - q) for j in range(q)) if d - q >= q - 1 else 0.0
    return (1 - p) ** q * (1 - zeta) + (1 - mu) ** q * zeta, p


def knot_finite(rows, q, k):
    rows = set(rows)
    full = q ** k
    if not rows or len(rows) == full:
        return False
    return all(len({r[:i] + r[i + 1:] for r in rows}) == q ** (k - 1) for i in range(k))


def run():
    checks, controls, failures = {}, {}, []
    certs = {}
    for q, df in THRESHOLDS.items():
        below = below_certificate(q, df - 1)
        r = witness(q, df)
        bound = star_bound(q, df, r) if r is not None else None
        grid = [Fraction(k, 50) for k in range(51)]
        monotone = all(evaluate(phi(q, d), p) <= evaluate(phi(q, d + 1), p) for d in range(max(q, df - 3), df + 2) for p in grid)
        certs[q] = {"threshold": df, "below_certified_at": df - 1, "below_certificate": below,
                    "witness_at_threshold": str(r) if r is not None else None,
                    "witness_float": float(r) if r is not None else None,
                    "star_nativity_bound_at_threshold": float(bound) if bound is not None else None,
                    "monotone_in_d_on_grid": monotone}
        if not (below and r is not None and monotone):
            failures.append(f"threshold certificate for q = {q}")
    checks["thresholds"] = {str(q): v for q, v in certs.items()}

    star_rel = {}
    for q in (3, 4, 5):
        rows = [t for t in product(range(q), repeat=q) if len(set(t)) < q]
        extend = all(any(z not in t for z in range(q)) for t in rows)
        star_rel[str(q)] = {"tuples": len(rows), "knot": knot_finite(rows, q, q), "every_tuple_extends": extend}
        if not (star_rel[str(q)]["knot"] and extend):
            failures.append(f"star relation for q = {q}")
    checks["star_relation"] = star_rel

    tree = json.loads(EXPERIMENT.read_text())["tree"]
    agree = {}
    for key, row in tree.items():
        s, p = star_formula(row["q"], row["d"])
        agree[key] = abs(s - row["star_native"]) < 1e-9 and abs(p - row["p_star"]) < 1e-9
    checks["formula_matches_experiment_tree_table"] = {"rows": len(agree), "agree": sum(agree.values())}
    if not all(agree.values()):
        failures.append("star formula disagrees with the experiment's tree table")
    nativity = {}
    for q, df in THRESHOLDS.items():
        below_s, _ = star_formula(q, df - 1)
        at_s, at_p = star_formula(q, df)
        nativity[str(q)] = {"below": below_s, "at": at_s, "p_star_at": at_p}
        if not (abs(below_s - 1) < 1e-12 and at_s < 1e-3):
            failures.append(f"nativity jump for q = {q}")
    checks["nativity_jump"] = nativity

    controls["one_degree_lower_has_no_witness"] = {str(q): witness(q, df - 1) is None for q, df in THRESHOLDS.items()}
    controls["one_degree_lower_has_no_witness"]["rejected"] = all(v for k, v in controls["one_degree_lower_has_no_witness"].items())
    controls["threshold_degree_not_certified_unfrozen"] = {str(q): not below_certificate(q, df) for q, df in THRESHOLDS.items()}
    controls["threshold_degree_not_certified_unfrozen"]["rejected"] = all(
        v for k, v in controls["threshold_degree_not_certified_unfrozen"].items())
    controls["all_q_colour_tuples_added_breaks_k1"] = {"rejected": not knot_finite(list(product(range(3), repeat=3)), 3, 3)}
    for name, control in controls.items():
        if not control.get("rejected"):
            failures.append(f"control not rejected: {name}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
