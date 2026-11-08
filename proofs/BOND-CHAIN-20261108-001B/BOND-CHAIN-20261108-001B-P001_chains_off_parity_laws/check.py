#!/usr/bin/env python3
"""Check for BOND-CHAIN-20261108-001B-P001: chains of knots off parity laws.

    python3 -B check.py            (writes result.json beside this file; standard library only)

Knots are read from allowed states by brute force: a set of at least three distinctions whose projection is constrained while
every projection forgetting one of them is full (K1-K3).
  1. The three-place knots: 34 relations, 5 classes up to permuting and negating variables.
  2. Every gluing of two three-place knots at one shared distinction b (R1 on x, a, b; R2 on b, c, y; the 34 are closed under
     permutation, so every placement of b occurs): 1,156 laws. A gluing is *gated* when one value of b frees both relations (each,
     with b fixed to it, allows all four values of its other two distinctions). Claim: a knot contains x and y exactly when the
     gluing is not gated, and then the least such knot has four distinctions.
  3. Chains of single clauses: T clauses on (s0, a1, s1), ..., (s(T-1), aT, sT), each with any signs (8^T laws), T = 2, 3, 4. Claim:
     a knot contains s0 and sT exactly when every shared s_t is read with opposite signs by its two clauses (the clauses chain as
     implications); otherwise the only knots crossing a gated s_t are none.
  4. Two threads of T = 5 clauses: the atom thread w(t-1) and L(t) imply w(t), where a knot of T + 2 distinctions contains w0 and
     wT (bond distance T + 1, as LOGIC-AXIS-20261107-001A proved), and the NAND thread not(s(t-1) and a(t) and s(t)), whose only
     knots are its T clauses, so bond distance between s0 and sT is infinite while a chain of T knots joins them."""
from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def knots_of(n, allowed):
    allowed = list(allowed)

    def full(S):
        return len({tuple(s[i] for i in S) for s in allowed}) == 2 ** len(S)
    fr = {}
    for k in range(1, n + 1):
        for S in itertools.combinations(range(n), k):
            fr[S] = full(S)
    return [frozenset(S) for k in range(3, n + 1) for S in itertools.combinations(range(n), k)
            if not fr[S] and all(fr[tuple(v for v in S if v != w)] for w in S)]


def three_place_knots():
    out = []
    for mask in range(1, 255):
        R = frozenset(t for i, t in enumerate(itertools.product((0, 1), repeat=3)) if mask >> i & 1)
        if all(len({(t[a], t[b]) for t in R}) == 4 for a, b in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def canon(R):
    return min(tuple(sorted(tuple(t[p[i]] ^ g[i] for i in range(3)) for t in R))
               for p in itertools.permutations(range(3)) for g in itertools.product((0, 1), repeat=3))


def frees(R, pos, v):
    others = [i for i in range(3) if i != pos]
    return len({tuple(t[i] for i in others) for t in R if t[pos] == v}) == 4


def clause_chain(signs):
    """signs[t] = (e0, e1, e2): clause t forbids (s(t-1), a(t), s(t)) = (e0, e1, e2); variables s0, a1, s1, a2, s2, ..."""
    T = len(signs)
    n = 2 * T + 1
    allowed = [s for s in itertools.product((0, 1), repeat=n)
               if all((s[2 * t], s[2 * t + 1], s[2 * t + 2]) != signs[t] for t in range(T))]
    return n, allowed


def main():
    res = {"checks": {}, "controls": {}, "census": {}}
    rels = three_place_knots()
    classes = Counter(canon(R) for R in rels)
    res["census"]["three-place knots, classes and their sizes"] = [len(rels), len(classes), sorted(classes.values())]
    res["controls"]["34 three-place knots in 5 classes (PINNING-20261031-001's count)"] = (len(rels), len(classes)) == (34, 5)
    # 2. gluings of two three-place knots
    tally = Counter()
    sizes = Counter()
    gate_classes = Counter()
    for R1 in rels:
        for R2 in rels:
            allowed = [s for s in itertools.product((0, 1), repeat=5) if (s[0], s[1], s[2]) in R1 and (s[2], s[3], s[4]) in R2]
            K = knots_of(5, allowed)
            through = [k for k in K if 0 in k and 4 in k]
            gated = any(frees(R1, 2, v) and frees(R2, 0, v) for v in (0, 1))
            tally[("knot through the ends" if through else "none through the ends", "gated" if gated else "not gated")] += 1
            if through:
                sizes[min(len(k) for k in through)] += 1
    for R in rels:
        if any(frees(R, p, v) for p in range(3) for v in (0, 1)):
            gate_classes[len([S for S in rels if canon(S) == canon(R)])] += 1
    res["census"]["gluings: (knot through the ends?, gated?)"] = {f"{a}, {b}": n for (a, b), n in sorted(tally.items())}
    res["census"]["gluings with a knot through the ends: size of the least one"] = dict(sizes)
    res["census"]["three-place knots with a gate (a position and value freeing the other two), by class size"] = dict(gate_classes)
    res["checks"]["a knot joins the far ends exactly when the gluing is not gated (1,084 of 1,156; 72 gated)"] = (
        tally[("knot through the ends", "not gated")] == 1084 and tally[("none through the ends", "gated")] == 72 and len(tally) == 2)
    res["checks"]["when one does, the least has four distinctions"] = set(sizes) == {4}
    # 3. chains of single clauses
    rows = {}
    ok3 = True
    for T in (2, 3, 4):
        agree = total = spans = 0
        for signs in itertools.product(list(itertools.product((0, 1), repeat=3)), repeat=T):
            n, allowed = clause_chain(signs)
            K = knots_of(n, allowed)
            span = any(0 in k and n - 1 in k for k in K)
            # s_t is read by clause t at position 2 and by clause t+1 at position 0; opposite signs = the clauses chain
            arrows = all(signs[t][2] != signs[t + 1][0] for t in range(T - 1))
            total += 1
            spans += span
            agree += span == arrows
        rows[T] = {"laws": total, "a knot spans the chain": spans, "agrees with: every shared distinction read with opposite signs": agree}
        ok3 &= agree == total
    res["census"]["chains of single clauses"] = rows
    res["checks"]["a knot spans a chain of single clauses exactly when its clauses chain as implications (T = 2, 3, 4)"] = ok3
    # 4. two threads of five clauses
    T = 5
    n, allowed = clause_chain([(1, 1, 0)] * T)      # atom thread: forbids w(t-1) = 1, L(t) = 1, w(t) = 0
    K = knots_of(n, allowed)
    ends = [k for k in K if 0 in k and n - 1 in k]
    res["census"]["atom thread of 5 clauses: least knot through w0 and w5"] = min(map(len, ends)) if ends else None
    res["checks"]["atom thread: bond distance between w0 and w5 is 6 (T + 1)"] = bool(ends) and min(map(len, ends)) == T + 2
    n, allowed = clause_chain([(1, 1, 1)] * T)      # NAND thread
    K = knots_of(n, allowed)
    clauses = {frozenset((2 * t, 2 * t + 1, 2 * t + 2)) for t in range(T)}
    res["census"]["NAND thread of 5 clauses: knots"] = len(K)
    res["checks"]["NAND thread: its only knots are its five clauses, so no knot joins s0 and s5"] = set(K) == clauses
    ok = all(res["checks"].values()) and all(res["controls"].values())
    res["status"] = "passed" if ok else "failed"
    res["failures"] = [k for k, v in {**res["checks"], **res["controls"]}.items() if not v]
    (HERE / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
