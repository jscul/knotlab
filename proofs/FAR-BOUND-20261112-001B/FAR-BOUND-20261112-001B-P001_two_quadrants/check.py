#!/usr/bin/env python3
"""Exact finite checks for FAR-BOUND-20261112-001B-P001: on the selected base, bond distance at most 3 on two quadrants.

The base: COMMON-FOLD-20261112-001A-E001 sample 24 at r = 3, kinds {0,(0,1),(1,2)}, {0,(1,-4),(2,0)}, {0,(0,4),(2,2)}, selected by
FAR-BOUND's frozen rule (the first base, r ascending then sample index, that the recheck classes bounded across). Frame: t' = (1, 2),
u = (0, 1); a distinction a t' + b u has along-count a and across-count b. T_j = the three distinctions (0, j), (0, j+1), (0, j+2).

  C1. Travel along t' and along 4u: the pattern 000 on T_0 forces 111 on T_0 + t' and 111 on T_0 + 4u (window refutations).
  C2. T_0 is free: each of its patterns is carried by an eventually periodic strip (sound certificate of a state).
  C3. Uniform freeness of the parts: for x = (alpha, y) with alpha >= 1 and y >= 0, some j in {0, -1, -2} has T_j forcing x (by C1,
      when (y - j) mod 4 is 0, 1 or 2) and every pattern of every part pi u {x} (pi a pair of T_j) carried by one of a fixed list of
      eventually periodic strips (across period Q, tail period P from along-count 1). A strip's value at x depends only on
      ((alpha - 1) mod P, y mod Q), so x's residue modulo (lcm of the P, lcm of the Q) decides every check: all residues are checked.
  C4. Mutation: with the kind {0,(0,4),(2,2)} removed, T_0's pattern no longer forces T_0 + 4u (that kind carries the travel across).
Usage: check.py [--write]
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("fb", ROOT / "experiments/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/census.py")
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
T = F.T
from pysat.solvers import Minisat22  # noqa: E402

KINDS = [((0, 0), (0, 1), (1, 2)), ((0, 0), (1, -4), (2, 0)), ((0, 0), (0, 4), (2, 2))]
FR = T.Frame(KINDS, (1, 2), (0, 1))


def tri(j, a=0):
    return [FR.cell(a, j + i) for i in range(3)]


def forces(kinds, given, target_vals):
    fr = T.Frame(kinds, (1, 2), (0, 1))
    idx, cl = fr.window(-10, 12, -24, 24)
    with Minisat22(bootstrap_with=cl) as s:
        assum = [idx[c] * (1 if v else -1) for c, v in given]
        if not s.solve(assumptions=assum):
            return False
        return all(not s.solve(assumptions=assum + [idx[c] * (-1 if v else 1)]) for c, v in target_vals)


def c1():
    g = [(c, 0) for c in tri(0)]
    along = forces(KINDS, g, [(FR.cell(1, i), 1) for i in range(3)])
    across = forces(KINDS, g, [(FR.cell(0, 4 + i), 1) for i in range(3)])
    return {"travels along t'": along, "travels along 4u": across, "holds": along and across}


def certs(Q, P):
    s = F.along_span(FR)
    assert P >= s
    return F.Eventual(FR, -2, 1, Q, P)


def c2(Q=12, P=4):
    e = certs(Q, P)
    ok = all(e.carries(tri(0), (0,) + q) for q in itertools.product((0, 1), repeat=2))
    e.close()
    return {"Q": Q, "P": P, "holds": ok}


class Eventual2:
    """States repeating with period P along outside [X0, X1) and with period Q across outside [Y0, Y1): the SAT window holds two
    copies of each tail block, constrained equal, in both directions (P, Q at least the kinds' spans), so every solution extends
    to a state of the base and every knot of the extension is a translate of one inside the window."""

    def __init__(self, X0, X1, Y0, Y1, P, Q):
        self.X0, self.X1, self.Y0, self.Y1, self.P, self.Q = X0, X1, Y0, Y1, P, Q
        A = range(X0 - 2 * P, X1 + 2 * P)
        B = range(Y0 - 2 * Q, Y1 + 2 * Q)
        idx = {(a, b): i + 1 for i, (a, b) in enumerate(itertools.product(A, B))}
        cl = []
        for a, b in idx:
            z = FR.cell(a, b)
            for k in KINDS:
                pts = [FR.co((z[0] + dx, z[1] + dy)) for dx, dy in k]
                if all(q in idx for q in pts):
                    v = [idx[q] for q in pts]
                    cl += [v, [-w for w in v]]
        for a0 in (X0 - 2 * P, X1):
            for a in range(a0, a0 + P):
                for b in B:
                    x, y = idx[(a, b)], idx[(a + P, b)]
                    cl += [[x, -y], [-x, y]]
        for b0 in (Y0 - 2 * Q, Y1):
            for b in range(b0, b0 + Q):
                for a in A:
                    x, y = idx[(a, b)], idx[(a, b + Q)]
                    cl += [[x, -y], [-x, y]]
        self.idx = idx
        self.s = Minisat22(bootstrap_with=cl)
        self.ok = self.s.solve()

    def red(self, a, b):
        if a >= self.X1:
            a = self.X1 + (a - self.X1) % self.P
        if b >= self.Y1:
            b = self.Y1 + (b - self.Y1) % self.Q
        return (a, b)

    def carries(self, cells_ab, p):
        lits = [self.idx[self.red(a, b)] * (1 if v else -1) for (a, b), v in zip(cells_ab, p)]
        return not any(-l in lits for l in lits) and self.s.solve(assumptions=lits)


X0, X1, Y0, Y1 = -2, 2, -4, 4
P2, Q2 = 4, 8


def c3():
    """Every x = (alpha, y), alpha >= 1, y >= 0, by its representative: alpha in [1, X1) or X1 + residue mod P2, y in [0, Y1) or
    Y1 + residue mod Q2 (the strip's value at x is the value at its representative)."""
    assert P2 >= F.along_span(FR) and Q2 >= 8
    e = Eventual2(X0, X1, Y0, Y1, P2, Q2)
    assert e.ok
    pats = [(0,) + q for q in itertools.product((0, 1), repeat=2)]
    reps_a = list(range(1, X1)) + [X1 + i for i in range(P2)]
    reps_b = list(range(0, Y1)) + [Y1 + i for i in range(Q2)]
    bad, n = [], 0
    for a in reps_a:
        for b in reps_b:
            # the residue of y mod 4 is that of b (Q2 is a multiple of 4)
            cover = []
            for j in (0, -1, -2):
                if (b - j) % 4 not in (0, 1, 2):
                    continue
                Tj = [(0, j + i) for i in range(3)]
                good = True
                for pi in itertools.combinations(Tj, 2):
                    for p in pats:
                        n += 1
                        if not e.carries(list(pi) + [(a, b)], p):
                            good = False
                if good:
                    cover.append(j)
            if not cover:
                bad.append((a, b))
    e.s.delete()
    return {"strip": [X0, X1, Y0, Y1, P2, Q2], "representatives": [len(reps_a), len(reps_b)], "checks": n,
            "representatives without a covering triple": bad[:10], "n bad": len(bad), "holds": not bad}


def c4():
    g = [(c, 0) for c in tri(0)]
    mut = forces(KINDS[:2], g, [(FR.cell(0, 4 + i), 1) for i in range(3)])
    return {"travels along 4u without the third kind": mut, "holds": not mut}


def main():
    out = {"C1": c1(), "C2": c2(8, 4), "C3": c3(), "C4": c4()}
    out["failures"] = [k for k in ("C1", "C2", "C3", "C4") if not out[k]["holds"]]
    print(json.dumps(out, indent=1, default=str))
    if "--write" in sys.argv:
        m = json.loads((HERE / "manifest.json").read_text())
        res = {"schema_version": 3, "artifact_id": m["artifact_id"], "kind": "proof", "ticket": m["ticket"], "proof": m["proof"],
               "status": "passed" if not out["failures"] else "failed", "claim": m["claim"], **out}
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    return 0 if not out["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
