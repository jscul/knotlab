#!/usr/bin/env python3
"""Finite checks for RULER-20261111-001A-P001: bond distance is graph distance plus one in the plane.

The proof (proof.md) covers every site and distance. These checks support it:
  C1. The height criterion (Lemma 4) agrees with SAT on a disc for every pattern on every set of at most 4 sites within distance 2
      of the origin, and on the explicit bonds of C2 to distance 4.
  C2. The side-and-apex set S(d, j) is a bond, by the criterion, for every distance d = 1..8 and direction j = 0..d; by SAT on a disc
      for d <= 4.
  C3. No bond of at most d + 1 sites contains (0,0) and (d, j), among sites within distance d of both, for d <= 4 (criterion).
  C4. R1 in a box: every pair (0,0), p with p within distance 4 is free; a triple within distance 2 of the origin is non-free exactly
      when it is a triangle (criterion and SAT).
  C5. R3: at the flat three-class state, for a site of each class, SAT on a disc finds a state equal to it outside distance 4 of the
      site and differing at the site.
  C6. Mutation: the criterion with D replaced by graph distance disagrees with SAT (so C1 can fail).

Usage: check.py [--write]   (run with the workspace .venv, which has pysat)
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent


def D(x, y):
    d1, d2 = y[0] - x[0], y[1] - x[1]
    return d1 + d2 + 3 * max(0, -d1, -d2)


def hexd(x, y):
    d1, d2 = y[0] - x[0], y[1] - x[1]
    return max(abs(d1), abs(d2)) if d1 * d2 >= 0 else abs(d1) + abs(d2)


def residue(x, s):
    c = (x[0] + x[1]) % 3
    return next(v for v in range(6) if v % 3 == c and v % 2 == s)


def extendable(S, spins, dist=D):
    n = len(S)
    r = [residue(S[i], spins[i]) for i in range(n)]
    w = [[0 if i == j else (dist(S[i], S[j]) - r[j] + r[i]) // 6 for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if w[i][k] + w[k][j] < w[i][j]:
                    w[i][j] = w[i][k] + w[k][j]
    return all(w[i][i] >= 0 for i in range(n))


def free(S, dist=D):
    return all(extendable(S, p, dist) for p in itertools.product((0, 1), repeat=len(S)))


def is_bond(S):
    return len(S) >= 3 and not free(S) and all(free([x for x in S if x != y]) for y in S)


class Disc:
    """NAE on every triangle of the disc of radius R around a centre, by SAT."""

    def __init__(self, R, centre=(0, 0)):
        self.sites = [(centre[0] + a, centre[1] + b) for a in range(-R - 1, R + 2) for b in range(-R - 1, R + 2)
                      if hexd(centre, (centre[0] + a, centre[1] + b)) <= R]
        self.idx = {p: i + 1 for i, p in enumerate(self.sites)}
        cl = []
        for x in self.sites:
            for tri in ((x, (x[0] + 1, x[1]), (x[0] + 1, x[1] + 1)), (x, (x[0], x[1] + 1), (x[0] + 1, x[1] + 1))):
                if all(p in self.idx for p in tri):
                    a, b, c = (self.idx[p] for p in tri)
                    cl += [[a, b, c], [-a, -b, -c]]
        self.s = Minisat22(bootstrap_with=cl)

    def extendable(self, S, spins):
        return self.s.solve(assumptions=[self.idx[p] if v else -self.idx[p] for p, v in zip(S, spins)])

    def free(self, S):
        return all(self.extendable(S, p) for p in itertools.product((0, 1), repeat=len(S)))


def side_and_apex(d, j):
    return [(0, y) for y in range(j - d, j + 1)] + [(d, j)]


def run():
    out = {}
    disc = Disc(8)
    near = [p for p in disc.sites if hexd((0, 0), p) <= 2]
    mism = 0
    total = 0
    for k in range(1, 5):
        for S in itertools.combinations(near, k):
            for p in itertools.product((0, 1), repeat=k):
                total += 1
                if extendable(list(S), p) != disc.extendable(S, p):
                    mism += 1
    for d in range(1, 5):
        for j in range(d + 1):
            S = side_and_apex(d, j)
            for p in itertools.product((0, 1), repeat=len(S)):
                total += 1
                if extendable(S, p) != disc.extendable(S, p):
                    mism += 1
    out["C1"] = {"patterns compared": total, "mismatches": mism, "pass": mism == 0}
    c2 = {}
    for d in range(1, 9):
        for j in range(d + 1):
            S = side_and_apex(d, j)
            ok = is_bond(S) and (0, 0) in S and hexd((0, 0), (d, j)) == d and len(S) == d + 2
            if d <= 4:
                ok = ok and not disc.free(S) and all(disc.free([x for x in S if x != y]) for y in S)
            c2[f"{d},{j}"] = ok
    out["C2"] = {"pass": all(c2.values()), "cases": len(c2)}
    c3 = {}
    for d in range(1, 5):
        for j in range(d + 1):
            v = (d, j)
            box = [(x, y) for x in range(-d, 2 * d + 1) for y in range(-d, 2 * d + 1)
                   if (x, y) not in ((0, 0), v) and hexd((0, 0), (x, y)) <= d and hexd(v, (x, y)) <= d]
            smaller = any(is_bond([(0, 0), v] + list(e)) for k in range(1, d) for e in itertools.combinations(box, k))
            c3[f"{d},{j}"] = not smaller
    out["C3"] = {"pass": all(c3.values()), "cases": len(c3)}
    pairs_free = all(free([(0, 0), p]) for p in disc.sites if 0 < hexd((0, 0), p) <= 4)
    tri = set()
    for x in near:
        for t in ((x, (x[0] + 1, x[1]), (x[0] + 1, x[1] + 1)), (x, (x[0], x[1] + 1), (x[0] + 1, x[1] + 1))):
            tri.add(tuple(sorted(t)))
    r1 = True
    for S in itertools.combinations(near, 3):
        nonfree = not free(list(S))
        if nonfree != (tuple(sorted(S)) in tri) or nonfree != (not disc.free(S)):
            r1 = False
    out["C4"] = {"pairs free": pairs_free, "triples": r1, "pass": pairs_free and r1}
    c5 = {}
    for b in ((0, 0), (1, 0), (2, 0)):
        d8 = Disc(9, centre=b)
        flat = {p: 1 if (p[0] + p[1]) % 3 == 1 else 0 for p in d8.sites}
        outside = [p for p in d8.sites if hexd(b, p) >= 5]
        S = outside + [b]
        spins = [flat[p] for p in outside] + [1 - flat[b]]
        c5[f"class {(b[0] + b[1]) % 3}"] = d8.extendable(S, spins)
    out["C5"] = {"pass": all(c5.values()), **c5}
    mut = sum(1 for S in itertools.combinations(near, 3) for p in itertools.product((0, 1), repeat=3)
              if extendable(list(S), p, dist=hexd) != disc.extendable(S, p))
    out["C6"] = {"mismatches under the mutation": mut, "pass": mut > 0}
    out["failures"] = [k for k in ("C1", "C2", "C3", "C4", "C5", "C6") if not out[k]["pass"]]
    return out


def main():
    outcome = run()
    print(json.dumps(outcome, indent=1))
    if "--write" in sys.argv:
        manifest = json.loads((HERE / "manifest.json").read_text())
        result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
                  "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
                  "claim": manifest["claim"], **outcome}
        (HERE / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    return 0 if not outcome["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
