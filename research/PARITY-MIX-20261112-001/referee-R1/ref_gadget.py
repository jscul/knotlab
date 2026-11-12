#!/usr/bin/env python3
"""Referee PARITY-MIX-R1, A78's buildability: an explicit gadget for the flip-blind parity knot from not-all-equal knots alone (three
distinct members per knot, no constants, hidden distinctions), checked by exhaustive projection.

  EQ(p, q):  the Fano configuration with one of its seven lines removed, p and q two points of that line; its other six lines as
             not-all-equal knots (5 hidden). Every proper 2-colouring of them makes the removed line one colour, so EQ is p = q.
  NE(p, q):  EQ(u, p) and NAE(u, q, p), u hidden: NAE(p, q, p) is p != q.
  clause:    (l1 or l2 or l3) relative to a reference r read as 0: NAE(l1, l2, t), NE(t, t'), NAE(t', l3, r) (t, t' hidden); a negated
             literal is a hidden copy x' with NE(x, x').
  XOR4(x, y, z, r): the four clauses of x xor y xor z = 0 relative to r. Every knot is not-all-equal, so the gadget is closed under
             the flip of all its distinctions, and with r = 1 it reads x xor y xor z = 1: together, x xor y xor z xor r = 0.
Also the advisor's route as written, NAE(a, b, e), NE(e, e'), NAE(e', c, r): it projects to 4-member not-all-equal, not to parity.

    python3 -B ref_gadget.py      (writes result_gadget.json)"""
import itertools
import json
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
FANO = [(1, 2, 4), (2, 3, 5), (3, 4, 6), (4, 5, 7), (5, 6, 1), (6, 7, 2), (7, 1, 3)]


class G:
    def __init__(self, visible):
        self.n = 0
        self.knots = []
        self.vis = {v: self.new() for v in visible}

    def new(self):
        self.n += 1
        return self.n

    def nae(self, a, b, c):
        assert len({a, b, c}) == 3
        self.knots.append((a, b, c))

    def eq(self, p, q):
        pts = {1: p, 2: q}
        for k in range(3, 8):
            pts[k] = self.new()
        for line in FANO[1:]:          # the line (1, 2, 4) removed
            self.nae(*(pts[k] for k in line))

    def ne(self, p, q):
        u = self.new()
        self.eq(u, p)
        self.nae(u, q, p)

    def clause(self, l1, l2, l3, r):
        t, t2 = self.new(), self.new()
        self.nae(l1, l2, t)
        self.ne(t, t2)
        self.nae(t2, l3, r)

    def projection(self, names):
        cl = [c for a, b, c3 in self.knots for c in ([a, b, c3], [-a, -b, -c3])]
        out = []
        with Glucose4(bootstrap_with=cl) as s:
            for vals in itertools.product((0, 1), repeat=len(names)):
                if s.solve(assumptions=[self.vis[nm] if v else -self.vis[nm] for nm, v in zip(names, vals)]):
                    out.append(vals)
        return out


def main():
    res = {}
    g = G(["p", "q"])
    g.eq(g.vis["p"], g.vis["q"])
    res["EQ"] = {"projection": g.projection(["p", "q"]), "knots": len(g.knots), "hidden": g.n - 2}
    g = G(["p", "q"])
    g.ne(g.vis["p"], g.vis["q"])
    res["NE"] = {"projection": g.projection(["p", "q"]), "knots": len(g.knots), "hidden": g.n - 2}
    g = G(["x", "y", "z", "r"])
    x, y, z, r = (g.vis[k] for k in "xyzr")
    neg = {}
    for v in (x, y, z):
        neg[v] = g.new()
        g.ne(v, neg[v])
    for lits in ((neg[x], y, z), (x, neg[y], z), (x, y, neg[z]), (neg[x], neg[y], neg[z])):
        g.clause(*lits, r)
    proj = g.projection(["x", "y", "z", "r"])
    res["XOR4"] = {"projection": proj, "is even parity": sorted(proj) == sorted(t for t in itertools.product((0, 1), repeat=4) if sum(t) % 2 == 0),
                   "knots": len(g.knots), "hidden": g.n - 4}
    g = G(["a", "b", "c", "r"])
    a, b, c, r = (g.vis[k] for k in "abcr")
    e, e2 = g.new(), g.new()
    g.nae(a, b, e)
    g.ne(e, e2)
    g.nae(e2, c, r)
    proj = g.projection(["a", "b", "c", "r"])
    res["advisor's NAE4 route"] = {"projection": proj,
                                   "is 4-member not-all-equal": sorted(proj) == sorted(t for t in itertools.product((0, 1), repeat=4) if 0 < sum(t) < 4),
                                   "is even parity": sorted(proj) == sorted(t for t in itertools.product((0, 1), repeat=4) if sum(t) % 2 == 0)}
    # plain parity is not complement-closed, so no not-all-equal gadget gives it: check closure of the flip-blind one and not of plain
    res["plain parity x xor y xor z = 0 complement-closed"] = all(
        tuple(1 - v for v in t) in {s for s in itertools.product((0, 1), repeat=3) if sum(s) % 2 == 0}
        for t in itertools.product((0, 1), repeat=3) if sum(t) % 2 == 0)
    (HERE / "result_gadget.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "projection"} if isinstance(v, dict) else v) for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    main()
