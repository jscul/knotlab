#!/usr/bin/env python3
"""Check for BOND-CHAIN-20261108-001A-P001: chains of knots on parity laws.

    python3 -B check.py            (writes result.json beside this file)

On finite windows of the parity laws measured since 2026-11-07 (LOGIC-AXIS-20261107-001A's axis_lib: the gauge law and Tseitin's
law on boxes, Ledrappier's triangle), with knots read from allowed states (a knot is a set of at least three distinctions whose
columns sum to zero with rank one less than its size):
  1. the union lemma: for every two knots of at most S_MAX distinctions that meet, and every x in the first only and y in the second
     only that are not parallel, some knot inside their union contains x and y;
  2. chains counted in knots collapse: every two distinctions that are not parallel and are joined by a chain of knots lie on a
     common knot (searched up to the window's size).
Control: on a law that is not a parity law, two single clauses not(s0 and a1 and s1), not(s1 and a2 and s2) sharing s1, the same
union test finds no knot through s0 and s2 (the generic test, by brute force on allowed states, can fail)."""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location(
    "axis_lib", ROOT / "proofs/LOGIC-AXIS-20261107-001A/LOGIC-AXIS-20261107-001A-P001_rulers_without_ends/axis_lib.py")
AX = importlib.util.module_from_spec(spec)
sys.modules["axis_lib"] = AX
spec.loader.exec_module(AX)
S_MAX = 6


def knots_up_to(law, smax):
    out = set()
    for u in law.vars:
        out |= AX.all_knots_through(law, u, smax)
    return out


def parallel(law, x, y):
    return law.col[x] == law.col[y]


def components(law, knots):
    parent = {v: v for v in law.vars}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    for k in knots:
        k = list(k)
        for v in k[1:]:
            parent[find(v)] = find(k[0])
    return find


def check_law(name, law):
    knots = knots_up_to(law, S_MAX)
    small = [k for k in knots if len(k) <= S_MAX]
    tests = fails = 0
    for c1, c2 in itertools.combinations(small, 2):
        if not (c1 & c2):
            continue
        union = list(c1 | c2)
        for x in c1 - c2:
            for y in c2 - c1:
                if parallel(law, x, y):
                    continue
                tests += 1
                if law.smallest_knot(x, y, len(union), candidates=union) is None:
                    fails += 1
    find = components(law, knots)
    pairs = misses = 0
    for x, y in itertools.combinations(law.vars, 2):
        if find(x) != find(y) or parallel(law, x, y) or law.col[x] == 0 or law.col[y] == 0:
            continue
        pairs += 1
        if law.smallest_knot(x, y, len(law.vars)) is None:
            misses += 1
    return {"law": name, "distinctions": len(law.vars), "knots of at most %d" % S_MAX: len(small),
            "union lemma: cases tested, failures": [tests, fails], "pairs joined by a chain: tested, with no common knot": [pairs, misses]}


def brute_knots(n, allowed):
    def full(S):
        return len({tuple(s[i] for i in S) for s in allowed}) == 2 ** len(S)
    fr = {S: full(S) for k in range(1, n + 1) for S in itertools.combinations(range(n), k)}
    return [set(S) for k in range(3, n + 1) for S in itertools.combinations(range(n), k)
            if not fr[S] and all(fr[tuple(v for v in S if v != w)] for w in S)]


def main():
    laws = [("gauge law, 4 x 4 box", AX.gauge_law((4, 4))), ("gauge law, 3 x 5 box", AX.gauge_law((3, 5))),
            ("Tseitin, 3 x 4 box", AX.tseitin_law((3, 4))), ("Tseitin, 2 x 2 x 2 box", AX.tseitin_law((2, 2, 2))),
            ("Ledrappier triangle, n = 5", AX.ledrappier_triangle(5))]
    rows = [check_law(n, l) for n, l in laws]
    res = {"laws": rows, "checks": {}, "controls": {}}
    res["checks"]["the union lemma holds on every tested pair of meeting knots"] = all(
        r["union lemma: cases tested, failures"][1] == 0 and r["union lemma: cases tested, failures"][0] > 0 for r in rows)
    res["checks"]["every pair joined by a chain of knots lies on a common knot"] = all(
        r["pairs joined by a chain: tested, with no common knot"][1] == 0 and r["pairs joined by a chain: tested, with no common knot"][0] > 0
        for r in rows)
    # control: two NAND clauses sharing s1, variables (s0, a1, s1, a2, s2)
    allowed = [s for s in itertools.product((0, 1), repeat=5) if not (s[0] and s[1] and s[2]) and not (s[2] and s[3] and s[4])]
    K = brute_knots(5, allowed)
    res["controls"]["two single clauses sharing a distinction: the knots are the two clauses, none through both far ends"] = (
        sorted(map(sorted, K)) == [[0, 1, 2], [2, 3, 4]])
    ok = all(res["checks"].values()) and all(res["controls"].values())
    res["status"] = "passed" if ok else "failed"
    res["failures"] = [k for k, v in {**res["checks"], **res["controls"]}.items() if not v]
    (HERE / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
