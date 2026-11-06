#!/usr/bin/env python3
"""Independent check of PC-DEGREE-20261020-001A-E001.

- Carving width recomputed by a different algorithm (memoized top-down threshold search: a set is buildable at
  width k if its cut is at most k and it is a vertex or splits into two buildable parts) on every roster graph
  with at most 12 vertices.
- PC_bal (balanced binomials, reduced convention) and PC_SC (clause polynomials, standard convention)
  recomputed by plain sparse linear algebra over F3, using no binomial structure: the degree-d closure is
  grown by intersecting the current span with the coordinate subspace of monomials that may be multiplied by
  y_e and adding the products, until stable. Done on every roster graph with at most 12 edges, for every
  degree up to min(4, value + 1).
- The predictions and controls recounted from raw_rows.jsonl.

Writes check_output.txt next to result.json. Exit status 0 when everything agrees.
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "PC-DEGREE-20261020-001A" / HERE.name


def popcount(x):
    return bin(x).count("1")


def carving_width_topdown(n, edges):
    def cut(U):
        return sum(1 for a, b in edges if (U >> a & 1) != (U >> b & 1))

    full = (1 << n) - 1
    for k in range(0, len(edges) + 1):
        @lru_cache(maxsize=None)
        def buildable(S):
            if cut(S) > k:
                return False
            if S & (S - 1) == 0:
                return True
            low = S & -S
            sub = (S - 1) & S
            while sub:
                if sub & low and buildable(sub) and buildable(S ^ sub):
                    return True
                sub = (sub - 1) & S
            return False

        if any(buildable(S) and buildable(full ^ S) for S in range(1, full) if S & 1):
            return k
    return None


def la_refutes(n, edges, d, axioms, convention, p=3):
    m = len(edges)
    star = [0] * n
    for i, (a, b) in enumerate(edges):
        star[a] |= 1 << i
        star[b] |= 1 << i
    deg = [popcount(s) for s in star]
    need = max((x + 1) // 2 for x in deg) if axioms == "balanced" else max(deg)
    if need > d:
        return False
    rows = {}

    def reduce(vec, table, key=None):
        vec = dict(vec)
        while vec:
            top = max(vec, key=key) if key else max(vec)
            if top not in table:
                return vec
            f = vec[top]
            for mono, c in table[top].items():
                val = (vec.get(mono, 0) - f * c) % p
                if val:
                    vec[mono] = val
                else:
                    vec.pop(mono, None)
        return vec

    def insert(vec, table, key=None):
        vec = reduce({k: v % p for k, v in vec.items() if v % p}, table, key)
        if not vec:
            return False
        top = max(vec, key=key) if key else max(vec)
        inv = pow(vec[top], p - 2, p)
        table[top] = {k: v * inv % p for k, v in vec.items()}
        return True

    for v in range(n):
        s = -1 if v == 0 else 1
        E = star[v]
        if axioms == "balanced":
            bits = [i for i in range(m) if E >> i & 1]
            A = sum(1 << i for i in bits[:(len(bits) + 1) // 2])
            insert({A: 1, E ^ A: -s}, rows)
        else:
            # clause polynomials of v in the +-1 basis: indicator of each violating assignment beta of E(v),
            # prod over e in E(v) of (1 + beta_e y_e) / 2 with beta_e = +-1 and prod beta_e = -s
            bits = [i for i in range(m) if E >> i & 1]
            for signs in range(1 << len(bits)):
                beta = [(-1) ** (signs >> j & 1) for j in range(len(bits))]
                prod = 1
                for b in beta:
                    prod *= b
                if prod != -s:
                    continue
                poly = {}
                for sub in range(1 << len(bits)):
                    mono, coef = 0, 1
                    for j in range(len(bits)):
                        if sub >> j & 1:
                            mono |= 1 << bits[j]
                            coef *= beta[j]
                    poly[mono] = poly.get(mono, 0) + coef      # times 2^-deg, a unit, dropped
                insert(poly, rows)
    while True:
        if not reduce({0: 1}, rows):
            return True
        grown = False
        basis = list(rows.values())
        for e in range(m):
            bit = 1 << e
            if convention == "R":
                eligible = lambda mono: popcount(mono ^ bit) <= d
            else:
                eligible = lambda mono: popcount(mono) <= d - 1
            key = lambda mono: (0 if eligible(mono) else 1, mono)
            local = {}
            for row in basis:
                insert(row, local, key)
            for top, row in list(local.items()):
                if eligible(top):
                    if insert({mono ^ bit: c for mono, c in row.items()}, rows):
                        grown = True
        if not grown:
            return not reduce({0: 1}, rows)


def main() -> int:
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    result = json.loads((ARTIFACT / "result.json").read_text())
    out = []
    cvw_checked = cvw_bad = 0
    la_checked = la_bad = 0
    for r in rows:
        n, edges = r["n"], [tuple(e) for e in r["edges"]]
        if n <= 12:
            cvw_checked += 1
            if carving_width_topdown(n, edges) != r["cvw"]:
                cvw_bad += 1
                out.append(f"carving width differs: {r['group']} {edges}")
        if len(edges) <= 12:
            for key, axioms, convention in (("PC_bal", "balanced", "R"), ("PC_SC", "clause", "S")):
                value = r[key]
                top = min(4, value + 1 if value is not None else 4)
                for d in range(1, top + 1):
                    expect = value is not None and d >= value
                    la_checked += 1
                    if la_refutes(n, edges, d, axioms, convention) != expect:
                        la_bad += 1
                        out.append(f"linear algebra differs: {key} d={d} {r['group']} {edges}")
    recount = {
        "P1": all(r["P1"] for r in rows) and all((r["cvw"] + 1) // 2 <= r["PC_bal"] <= r["cvw"] // 2 + 1 for r in rows),
        "P2": all(r["PC_Rstd"] == max(r["maxdegree"], r["PC_bal"]) for r in rows),
        "P3": all(max(r["maxdegree"], r["PC_bal"]) <= r[k] <= max(r["maxdegree"], r["PC_bal"]) + 1
                  for r in rows for k in ("PC_SC", "PC_SB")),
        "P4": all(r["P4"] for r in rows if "P4" in r),
        "P5": any(r["cvw"] % 2 == 0 and r["PC_bal"] == r["cvw"] // 2 for r in rows) and
              any(r["cvw"] % 2 == 0 and r["PC_bal"] == r["cvw"] // 2 + 1 for r in rows),
        "control_even_charge": not any(r.get("control_even_charge_refuted") for r in rows),
    }
    agrees_with_result = all(result["predictions"][k]["holds"] == v for k, v in recount.items() if k.startswith("P"))
    ok = cvw_bad == 0 and la_bad == 0 and all(recount.values()) and agrees_with_result
    summary = {"carving_width_rechecked": cvw_checked, "carving_width_mismatches": cvw_bad,
               "linear_algebra_cases": la_checked, "linear_algebra_mismatches": la_bad,
               "recount": recount, "agrees_with_result_json": agrees_with_result, "passed": ok}
    out.append(json.dumps(summary, sort_keys=True))
    (ARTIFACT / "check_output.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out[-5:]))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
