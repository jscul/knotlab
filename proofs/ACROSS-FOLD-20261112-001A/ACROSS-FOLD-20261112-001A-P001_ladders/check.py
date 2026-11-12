#!/usr/bin/env python3
"""Exact checks for ACROSS-FOLD-20261112-001A-P001: travelling ladders on base 16 bound bond distance across the fold.

Sheared frame of base 16 (as in FOLD-20261112-001A-P001): knot kinds {0, (0,1), (1,0)} and {0, (0,2), (1,2)}. For y >= 2 the ladder
L_y in column 0 is the triple {0, 1, 2} with the rungs 4, 6, ..., y (y even), or the triple {-1, 0, 1} with the rungs 3, 5, ..., y (y
odd); it contains row 0. The claim: for every k >= 3, L_y with (k, y) is a bond, of size floor((y+1)/2) + 3. (At k = 1 the set holds
a knot.)

  C1. Forcing: a ladder all equal to a in column x forces the same ladder all equal to the opposite value in column x + 1 (exhaustive
      over the column rule on the ladder's rows, in a window of rows and columns).
  C2. Freeness, every k >= 3, y = 2 .. 8: every proper part of L_y u {(k, y)} takes all its patterns, realized by states periodic in y
      with period m (exact: bi-infinite walks in the transfer graph of columns of period m; the reachable sets of columns are eventually
      periodic in k, so a finite run decides every k). Periods m from y + 3 to 11.
  C3. Mutation: with the rung below the top removed (y >= 4), the set is free at k = 3 (every pattern carried by a periodic state):
      the chain needs every rung.
  C4. The core lemma (proof, step 2), exhaustively on row sets A within rows -2 .. 5 of size 1 to 5, every pattern a, every y in A, at
      k = |A| and |A| + 2: if y is in core(a), no periodic state carries the opposite value at (k, y) (consistency); if not, periodic
      states carry both values (completeness, certified).

Usage: check.py [--write]   (the workspace .venv)
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
KINDS = [((0, 0), (0, 1), (1, 0)), ((0, 0), (0, 2), (1, 2))]
YS = range(2, 9)


def ladder(y):
    return [0, 1, 2] + list(range(4, y + 1, 2)) if y % 2 == 0 else [-1, 0, 1] + list(range(3, y + 1, 2))


def window(X0, X1, Y0, Y1):
    cells = [(x, r) for x in range(X0, X1 + 1) for r in range(Y0, Y1 + 1)]
    idx = {c: i + 1 for i, c in enumerate(cells)}
    cl = []
    for (x, r) in cells:
        for kind in KINDS:
            pts = [(x + a, r + b) for a, b in kind]
            if all(p in idx for p in pts):
                cl += [[idx[p] for p in pts], [-idx[p] for p in pts]]
    return idx, cl


def c1():
    bad = []
    for y in YS:
        L = ladder(y)
        idx, cl = window(0, 1, min(L) - 3, max(L) + 3)
        with Minisat22(bootstrap_with=cl) as s:
            for a in (0, 1):
                assum = [idx[(0, r)] * (1 if a else -1) for r in L]
                for r in L:      # each rung of column 1 must be forced to the opposite value
                    if s.solve(assumptions=assum + [idx[(1, r)] * (1 if a else -1)]):
                        bad.append((y, a, r))
    return {"violations": bad, "holds": not bad}


class Strip:
    """Columns of period m; a column c is followed by d when the column rule holds between them."""

    def __init__(self, m):
        self.m = m
        n = 1 << m
        b = self.bit
        self.succ = [[d for d in range(n)
                      if all(not (b(c, r) == b(c, r + 1) and b(d, r) == b(c, r)) and not (b(c, r) == b(c, r + 2) and b(d, r + 2) == b(c, r))
                             for r in range(m))] for c in range(n)]
        pred = [[] for _ in range(n)]
        for c in range(n):
            for d in self.succ[c]:
                pred[d].append(c)
        fut = set(range(n))
        while True:
            new = {c for c in fut if any(d in fut for d in self.succ[c])}
            if new == fut:
                break
            fut = new
        past = set(range(n))
        while True:
            new = {d for d in past if any(c in past for c in pred[d])}
            if new == past:
                break
            past = new
        self.fut, self.past = fut, past

    def bit(self, c, r):
        return (c >> (r % self.m)) & 1

    def carries(self, cells, p):
        """cells (x, r) with values p: some bi-infinite state of period m carries them (exact for period m)."""
        x0 = min(x for x, _ in cells)
        by = {}
        for (x, r), v in zip(cells, p):
            by.setdefault(x - x0, []).append((r, v))
        cur = {c for c in self.past if all(self.bit(c, r) == v for r, v in by.get(0, []))}
        for step in range(1, max(by) + 1):
            nxt = set()
            for c in cur:
                nxt.update(self.succ[c])
            cur = {d for d in nxt if all(self.bit(d, r) == v for r, v in by.get(step, []))}
            if not cur:
                return False
        return bool(cur & self.fut)

    def realized_for_all_k(self, near, far_row):
        """near: [(row, value)] in column 0; far_row: (row, value) in column k or None. Returns the set of k >= 1 (as 'all', or a
        finite description) for which a bi-infinite state of period m carries the pattern: computed until the reachable sets repeat."""
        start = frozenset(c for c in self.past if all(self.bit(c, r) == v for r, v in near))
        if not start:
            return "never"
        if far_row is None:
            return "always" if any(c in self.fut for c in start) else "never"
        r, v = far_row
        seen, seq = {}, []
        cur = start
        k = 0
        while True:
            k += 1
            nxt = set()
            for c in cur:
                nxt.update(self.succ[c])
            cur = frozenset(nxt)
            ok = any(self.bit(d, r) == v and d in self.fut for d in cur)
            if cur in seen:
                k0 = seen[cur]
                period = k - k0
                return {"seq": seq, "k0": k0, "period": period}
            seen[cur] = k
            seq.append(ok)


KMIN = 3


def realized_every_k(strips, near, far_row):
    """True when, for every k >= KMIN, some strip carries the pattern; decided over k = 1 .. K0 + lcm(periods), beyond which the union
    of the strips' eventually periodic answers repeats."""
    import math
    res = [st.realized_for_all_k(near, far_row) for st in strips]
    if any(r == "always" for r in res):
        return True, None
    rs = [r for r in res if r != "never"]
    if not rs:
        return False, 1
    K0 = max(r["k0"] for r in rs)
    L = 1
    for r in rs:
        L = L * r["period"] // math.gcd(L, r["period"])
    failing = []
    for k in range(KMIN, K0 + L + 1):
        hit = False
        for r in rs:
            seq, k0, p = r["seq"], r["k0"], r["period"]
            kk = k if k <= len(seq) else k0 + (k - k0) % p
            if seq[kk - 1]:
                hit = True
                break
        if not hit:
            failing.append(k)
    if not failing:
        return True, None
    # failing k beyond K0 recur with period L: report them as "k <= max" when all lie below K0
    return False, {"failing k": failing, "recur beyond": any(k > K0 for k in failing), "K0": K0, "L": L}


def c2():
    out = {}
    bad = []
    cache = {}
    for y in YS:
        L = ladder(y)
        strips = [cache.setdefault(m, Strip(m)) for m in range(max(3, y - min(L) + 3), 12)]
        parts = [([r for r in L if r != drop], True) for drop in L] + [(L, False)]
        fails = 0
        for rows, with_far in parts:
            for p in itertools.product((0, 1), repeat=len(rows) + (1 if with_far else 0)):
                near = list(zip(rows, p[:len(rows)]))
                far = (y, p[-1]) if with_far else None
                ok, k = realized_every_k(strips, near, far)
                if not ok:
                    fails += 1
                    bad.append((y, rows, with_far, p, k))
        fk = sorted({kk for b in bad if b[0] == y for kk in b[4]["failing k"]})
        rec = any(b[4]["recur beyond"] for b in bad if b[0] == y)
        out[y] = {"size": len(L) + 1, "periods m": [st.m for st in strips], "unrealized": fails, "failing k": fk,
                  "bond for every k >": (max(fk) if fk and not rec else (None if rec else KMIN - 1))}
    return {"by y": out, "first failures": bad[:5], "holds": all(v["bond for every k >"] is not None for v in out.values())}


def c3():
    """Without the rung below the top, the set is free at k = 3: every pattern carried by a periodic state (certified; a window that
    refutes nothing would not show it). Window SAT is reported alongside."""
    res = {}
    strips = [Strip(m) for m in range(3, 12)]
    for y in range(4, 9):
        L = ladder(y)
        L2 = [r for r in L if r != L[-2]]
        idx, cl = window(-1, 4, min(L) - 4, max(L) + 4)
        S = [(0, r) for r in L2] + [(3, y)]
        with Minisat22(bootstrap_with=cl) as s:
            refuted = any(not s.solve(assumptions=[idx[c] * (1 if b else -1) for c, b in zip(S, p)])
                          for p in itertools.product((0, 1), repeat=len(S)))
        free = all(any(st.carries(S, list(p)) for st in strips) for p in itertools.product((0, 1), repeat=len(S)))
        res[y] = {"refuted in a window": refuted, "certified free": free}
    return {"without the rung below the top, at k = 3": res, "holds": all(v["certified free"] for v in res.values())}


def core(rows, a):
    """The largest T within rows whose every r has r + 1 or r - 2 in T with the same value."""
    T = dict(zip(rows, a))
    while True:
        drop = [r for r, v in T.items() if T.get(r + 1) != v and T.get(r - 2) != v]
        if not drop:
            return set(T)
        for r in drop:
            del T[r]


def c4():
    strips = [Strip(m) for m in range(3, 12)]
    tally = {"core, opposite carried (bad)": 0, "core, consistent": 0, "not core, both carried": 0, "not core, uncertified": 0}
    bad = []
    rows_all = range(-2, 6)
    for size in range(1, 6):
        for rows in itertools.combinations(rows_all, size):
            for a in itertools.product((0, 1), repeat=size):
                T = core(list(rows), a)
                for y in rows:
                    for k in (size, size + 2):
                        cells = [(0, r) for r in rows] + [(k, y)]
                        val = {}
                        for b in (0, 1):
                            val[b] = any(st.carries(cells, list(a) + [b]) for st in strips)
                        if y in T:
                            forced = (a[rows.index(y)] + k) % 2
                            key = "core, consistent" if not val[1 - forced] else "core, opposite carried (bad)"
                        else:
                            key = "not core, both carried" if val[0] and val[1] else "not core, uncertified"
                        tally[key] += 1
                        if key in ("core, opposite carried (bad)", "not core, uncertified") and len(bad) < 5:
                            bad.append((rows, a, y, k, key))
    return {"tally": tally, "first exceptions": bad,
            "holds": tally["core, opposite carried (bad)"] == 0 and tally["not core, uncertified"] == 0}


def main():
    out = {"C1": c1(), "C2": c2(), "C3": c3(), "C4": c4()}
    out["failures"] = [k for k in ("C1", "C2", "C3", "C4") if not out[k]["holds"]]
    print(json.dumps(out, indent=1, default=str))
    if "--write" in sys.argv:
        manifest = json.loads((HERE / "manifest.json").read_text())
        result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
                  "proof": manifest["proof"], "status": "passed" if not out["failures"] else "failed", "claim": manifest["claim"], **out}
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    return 0 if not out["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
