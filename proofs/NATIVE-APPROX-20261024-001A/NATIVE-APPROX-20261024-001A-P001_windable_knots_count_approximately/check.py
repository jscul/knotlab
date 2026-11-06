#!/usr/bin/env python3
"""Check of NATIVE-APPROX-20261024-001A-P001 (standard library only).

Definitions (McQuillan, arXiv:1301.2880):
- strictly terraced: F(x) = 0 implies F(x + e_i) = F(x + e_j) for all i, j;
- windable: there are B(x, y, M) >= 0, for x, y in {0,1}^J and M a partition of the set where x and y differ into pairs and singletons,
  with (1) sum_M B(x, y, M) = F(x) F(y) and (2) B(x, y, M) = B(x + S, y + S, M) for every block S of M.
Checks:
- every one of the 34 knots, both pins and the free unary function are strictly terraced; every relation on three bits whose excluded
  tuples are pairwise non-adjacent is;
- windability of each knot decided twice: by McQuillan's inequality for three-place functions (his Theorem 6), and directly, by exact
  linear feasibility of conditions (1) and (2) (phase-one simplex over fractions on orbit variables); the two agree;
- the census: 26 knots windable; the 8 that are not are exactly the knots excluding three tuples; two of those are the topological
  no-lone-value knots.
Controls: McQuillan's example relation {000, 100, 010, 101, 011} is windable, as his paper states; not-all-equal is windable (his
#ParityNAE); the soft equality with weights 2 on 000 and 111 and 1 elsewhere is not windable (4 > 3) and the feasibility test also
rejects it; the perfect-matching relation (exactly one 1) is not strictly terraced.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUBE = list(itertools.product((0, 1), repeat=3))


def knots():
    out = []
    for m in range(256):
        R = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def as_function(R):
    return {x: Fraction(int(x in R)) for x in CUBE}


def strictly_terraced(F, k):
    pts = list(itertools.product((0, 1), repeat=k))
    for x in pts:
        if F[x] == 0:
            vals = {F[tuple(b ^ (i == j) for j, b in enumerate(x))] for i in range(k)}
            if len(vals) > 1:
                return False
    return True


def inequality_windable(F):
    """McQuillan's Theorem 6 criterion for three-place functions"""
    def c(b):
        return 1 - b
    for x1, x2, x3 in CUBE:
        lhs = F[(x1, x2, x3)] * F[(c(x1), c(x2), c(x3))]
        rhs = (F[(x1, x2, c(x3))] * F[(c(x1), c(x2), x3)] + F[(x1, c(x2), x3)] * F[(c(x1), x2, c(x3))]
               + F[(x1, c(x2), c(x3))] * F[(c(x1), x2, x3)])
        if lhs > rhs:
            return False
    return True


def partitions(D):
    """partitions of the list D into pairs and singletons"""
    if not D:
        return [[]]
    first, rest = D[0], D[1:]
    out = [[(first,)] + p for p in partitions(rest)]
    for i, other in enumerate(rest):
        for p in partitions(rest[:i] + rest[i + 1:]):
            out.append([(first, other)] + p)
    return out


def flip(x, S):
    return tuple(b ^ (i in S) for i, b in enumerate(x))


def windability_system():
    """orbit variables and, for each (x, y), the list of orbit indices of its terms"""
    orbit_of, terms = {}, {}
    for x in CUBE:
        for y in CUBE:
            D = [i for i in range(3) if x[i] != y[i]]
            terms[(x, y)] = []
            for M in partitions(D):
                key = (x, y, tuple(sorted(M)))
                if key not in orbit_of:
                    # orbit under flipping any union of blocks of M (applied to both x and y)
                    idx = len(set(orbit_of.values()))
                    for r in range(len(M) + 1):
                        for blocks in itertools.combinations(M, r):
                            S = set(i for b in blocks for i in b)
                            orbit_of[(flip(x, S), flip(y, S), tuple(sorted(M)))] = idx
                terms[(x, y)].append(orbit_of[key])
    return terms, len(set(orbit_of.values()))


def feasible(A, b):
    """is there z >= 0 with A z = b (A list of rows, b list), by phase-one simplex with Bland's rule over fractions"""
    m, n = len(A), len(A[0])
    rows = []
    for i in range(m):
        row = [Fraction(v) for v in A[i]]
        rhs = Fraction(b[i])
        if rhs < 0:
            row = [-v for v in row]
            rhs = -rhs
        rows.append(row + [Fraction(int(j == i)) for j in range(m)] + [rhs])
    basis = [n + i for i in range(m)]
    N = n + m
    cost = [Fraction(0)] * n + [Fraction(1)] * m

    def reduced(j):
        return cost[j] - sum(cost[basis[i]] * rows[i][j] for i in range(m))
    while True:
        enter = next((j for j in range(N) if reduced(j) < 0), None)
        if enter is None:
            break
        ratios = [(rows[i][-1] / rows[i][enter], basis[i], i) for i in range(m) if rows[i][enter] > 0]
        if not ratios:
            return False
        _, _, r = min(ratios)
        piv = rows[r][enter]
        rows[r] = [v / piv for v in rows[r]]
        for i in range(m):
            if i != r and rows[i][enter] != 0:
                f = rows[i][enter]
                rows[i] = [a - f * c for a, c in zip(rows[i], rows[r])]
        basis[r] = enter
    value = sum(cost[basis[i]] * rows[i][-1] for i in range(m))
    return value == 0


TERMS, NVAR = windability_system()
PAIRS = sorted(TERMS)


def lp_windable(F):
    A, b = [], []
    for (x, y) in PAIRS:
        row = [0] * NVAR
        for k in TERMS[(x, y)]:
            row[k] += 1
        A.append(row)
        b.append(F[x] * F[y])
    return feasible(A, b)


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    K = knots()
    unary = {"pin 0": {(0,): Fraction(1), (1,): Fraction(0)}, "pin 1": {(0,): Fraction(0), (1,): Fraction(1)},
             "free": {(0,): Fraction(1), (1,): Fraction(1)}}
    coind = []
    for m in range(1, 256):
        R = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        Z = [t for t in CUBE if t not in R]
        if all(sum(a != c for a, c in zip(s, t)) != 1 for s in Z for t in Z):
            coind.append(R)
    terraced = {"all 34 knots": all(strictly_terraced(as_function(R), 3) for R in K),
                "pins and the free unary function": all(strictly_terraced(F, 1) for F in unary.values()),
                "all co-independent relations on three bits": all(strictly_terraced(as_function(R), 3) for R in coind),
                "co-independent relations tested": len(coind)}
    rows = []
    for R in K:
        F = as_function(R)
        Z = sorted("".join(map(str, t)) for t in CUBE if t not in R)
        sym = all(tuple(t[p] for p in perm) in R for t in R for perm in itertools.permutations(range(3)))
        rows.append({"excluded": Z, "inequality": inequality_windable(F), "feasibility": lp_windable(F), "symmetric": sym})
    non = [r for r in rows if not r["inequality"]]
    census = {"orbit variables in the windability system": NVAR,
              "inequality and feasibility agree on every knot": all(r["inequality"] == r["feasibility"] for r in rows),
              "windable knots": sum(r["inequality"] for r in rows),
              "knots not windable (excluded tuples)": [r["excluded"] for r in non],
              "the non-windable knots are exactly those excluding three tuples":
                  sorted(map(tuple, (r["excluded"] for r in non))) == sorted(tuple(r["excluded"]) for r in rows if len(r["excluded"]) == 3),
              "symmetric among them (the topological no-lone-value knots)": [r["excluded"] for r in non if r["symmetric"]]}
    mcq = frozenset({(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 0, 1), (0, 1, 1)})
    nae = frozenset(t for t in CUBE if 0 < sum(t) < 3)
    soft = {x: Fraction(2) if x in ((0, 0, 0), (1, 1, 1)) else Fraction(1) for x in CUBE}
    pm = frozenset(t for t in CUBE if sum(t) == 1)
    controls = {
        "McQuillan's example relation is windable (both tests)": inequality_windable(as_function(mcq)) and lp_windable(as_function(mcq)),
        "not-all-equal is windable (both tests)": inequality_windable(as_function(nae)) and lp_windable(as_function(nae)),
        "the soft equality [2,1,1,2] is rejected by both tests": not inequality_windable(soft) and not lp_windable(soft),
        "the perfect-matching relation is not strictly terraced": not strictly_terraced(as_function(pm), 3),
    }
    ok = (terraced["all 34 knots"] and terraced["pins and the free unary function"] and terraced["all co-independent relations on three bits"]
          and census["inequality and feasibility agree on every knot"] and census["windable knots"] == 26
          and census["the non-windable knots are exactly those excluding three tuples"]
          and sorted(census["symmetric among them (the topological no-lone-value knots)"]) == [["001", "010", "100"], ["011", "101", "110"]]
          and all(controls.values()))
    result["checks"] = {"strictly terraced": terraced, "windability census": census, "knots": rows}
    result["controls"] = controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "terraced": terraced, "census": census, "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
