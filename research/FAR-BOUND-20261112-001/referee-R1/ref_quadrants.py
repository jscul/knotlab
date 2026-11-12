#!/usr/bin/env python3
"""Referee FAR-BOUND-R1, ticket B rerun with the referee's own code (no import of the epic's check.py or census.py, or of
TRAVEL-READ's census): sample 24 at r = 3, kinds {0, (0,1), (1,2)}, {0, (1,-4), (2,0)}, {0, (0,4), (2,2)} on Z^2 (standard
coordinates, from the proof's statement), frame t' = (1, 2), u = (0, 1): (alpha, y) is alpha t' + y u = (alpha, 2 alpha + y).

  C1  in a window, the pattern 000 on T_0 = {(0,0), (0,1), (0,2)} (frame) leaves value 0 impossible at every cell of T_0 + t' and of
      T_0 + 4u (a window refutation, sound for the infinite base);
  C2  every pattern on T_0 is carried by a certificate;
  C3  for every representative x of the quadrant alpha >= 1, y >= 0 and every j in {0, -1, -2} with (y - j) mod 4 in {0, 1, 2}, every
      pattern on pi + {x} (pi a pair of T_j) is carried, the value at x read at its representative;
  C4  without the kind {0, (0,4), (2,2)}, 000 on T_0 no longer forces T_0 + 4u (a certified state with a 0 there).

The certificate (derived here): a state on Z^2 equal to a word Z on the window [a0 - 2p, a1 + 2p) x [b0 - 2q, b1 + 2q) (frame), with
Z repeating with period p along in both tails (two blocks each side, constrained equal) and with period q across in both tails, and
extended by that repetition. Every edge of Z^2 is moved by multiples of p along and q across, staying inside a tail when it starts in
one, into the window, provided p >= the kinds' along-span (2) and q >= their across-span (6); so the word's edges inside the window are
all that must hold. Two parameter sets: the proof's (core [-2, 2) x [-4, 4), p = 4, q = 8) and the referee's own (core [-3, 3) x
[-6, 6), p = 6, q = 16). With q a multiple of 4, y and its representative agree mod 4, as C1's condition needs; travel along 4u
complements the pattern at each step, so a repetition across must be a multiple of 8 (a first try with q = 12 failed for that reason,
kept in the output), and travel along t' complements at each step, so p must be even.

    python3 -B ref_quadrants.py      (writes result_quadrants.json)"""
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
STD = [((0, 0), (0, 1), (1, 2)), ((0, 0), (1, -4), (2, 0)), ((0, 0), (0, 4), (2, 2))]


def to_frame(v):
    i, j = v
    return (i, j - 2 * i)


def frame_kinds(std):
    return [tuple(to_frame(v) for v in k) for k in std]


def spans(kinds):
    sa = max(max(v[0] for v in k) - min(v[0] for v in k) for k in kinds)
    sy = max(max(v[1] for v in k) - min(v[1] for v in k) for k in kinds)
    return sa, sy


class Window:
    """NAE on every edge inside the box; optional tail equalities"""

    def __init__(self, kinds, A, B, tails=None):
        (self.a_lo, self.a_hi), (self.b_lo, self.b_hi) = A, B
        self.var = {}
        cl = []
        for a in range(self.a_lo, self.a_hi):
            for b in range(self.b_lo, self.b_hi):
                self.var[a, b] = len(self.var) + 1
        for (a, b) in list(self.var):
            for k in kinds:
                cells = [(a + d[0], b + d[1]) for d in k]
                if all(c in self.var for c in cells):
                    t = [self.var[c] for c in cells]
                    cl += [t, [-x for x in t]]
        if tails:
            a0, a1, p, b0, b1, q = tails
            for (a, b), v in self.var.items():
                if (a1 <= a < a1 + p) or (a0 - 2 * p <= a < a0 - p):
                    w = self.var.get((a + p, b))
                    if w:
                        cl += [[-v, w], [v, -w]]
                if (b1 <= b < b1 + q) or (b0 - 2 * q <= b < b0 - q):
                    w = self.var.get((a, b + q))
                    if w:
                        cl += [[-v, w], [v, -w]]
        self.s = Solver(name="cadical153", bootstrap_with=cl)

    def sat(self, pattern):
        return self.s.solve(assumptions=[self.var[c] if val else -self.var[c] for c, val in pattern.items()])

    def close(self):
        self.s.delete()


def certificate(kinds, params):
    a0, a1, p, b0, b1, q = params
    sa, sy = spans(kinds)
    assert p >= sa and q >= sy and q % 4 == 0
    return Window(kinds, (a0 - 2 * p, a1 + 2 * p), (b0 - 2 * q, b1 + 2 * q), tails=params)


def rep(x, params):
    a0, a1, p, b0, b1, q = params
    a, y = x
    ra = a if a < a1 else a1 + (a - a1) % p
    ry = y if y < b1 else b1 + (y - b1) % q
    return (ra, ry)


def T(j):
    return [(0, j), (0, j + 1), (0, j + 2)]


def main():
    t0 = time.time()
    kinds = frame_kinds(STD)
    out = {"frame kinds": kinds, "spans (along, across)": spans(kinds)}
    # C1: window refutations
    win = Window(kinds, (-8, 9), (-30, 31))
    base = {c: 0 for c in T(0)}
    forced = {}
    for name, cells in (("T_0 + t'", [(1, 0), (1, 1), (1, 2)]), ("T_0 + 4u", [(0, 4), (0, 5), (0, 6)])):
        forced[name] = all(not win.sat({**base, c: 0}) and win.sat({**base, c: 1}) for c in cells)
    win.close()
    out["C1 000 on T_0 forces 111 on"] = forced
    for label, params in (("proof's parameters", (-2, 2, 4, -4, 4, 8)), ("referee's parameters", (-3, 3, 6, -6, 6, 16)),
                          ("referee's first try, q = 12 (not a multiple of 8)", (-3, 3, 6, -6, 6, 12))):
        a0, a1, p, b0, b1, q = params
        cert = certificate(kinds, params)
        c2 = all(cert.sat(dict(zip(T(0), pat))) for pat in itertools.product((0, 1), repeat=3))
        reps = sorted({rep((a, y), params) for a in range(1, a1 + 2 * p) for y in range(0, b1 + 2 * q)})
        cases = fails = 0
        failed = []
        for x in reps:
            assert x[0] >= 1 and all(x != c for j in (0, -1, -2) for c in T(j))
            js = [j for j in (0, -1, -2) if (x[1] - j) % 4 in (0, 1, 2)]
            ok_some_j = False
            for j in js:
                good = True
                for pi in itertools.combinations(T(j), 2):
                    for pat in itertools.product((0, 1), repeat=3):
                        if pat[0] == 1:          # up to complement (the base is closed under the flip)
                            continue
                        cases += 1
                        if not cert.sat({pi[0]: pat[0], pi[1]: pat[1], x: pat[2]}):
                            good = False
                            fails += 1
                            failed.append([list(x), j, [list(c) for c in pi], list(pat)])
                ok_some_j |= good
            if not ok_some_j:
                failed.append(["no j works", list(x)])
        cert.close()
        out[label] = {"core and periods": params, "C2 T_0 free": c2, "representatives": len(reps), "cases (rep, j, pair, pattern up to flip)": cases,
                      "cases not carried": fails, "every representative has a j with all cases carried": not any(f[0] == "no j works" for f in failed),
                      "failed (first 10)": failed[:10]}
        print(label, out[label]["C2 T_0 free"], len(reps), cases, fails, round(time.time() - t0), "s", flush=True)
    # C4: drop the third kind
    k2 = kinds[:2]
    cert = certificate(k2, (-3, 3, 6, -6, 6, 16))
    out["C4 without the third kind: 000 on T_0 with a 0 on T_0 + 4u carried"] = {str(c): cert.sat({**base, c: 0}) for c in [(0, 4), (0, 5), (0, 6)]}
    out["C4 without the third kind: T_0 + t' still forced (window)"] = None
    cert.close()
    w2 = Window(k2, (-8, 9), (-30, 31))
    out["C4 without the third kind: T_0 + t' still forced (window)"] = all(not w2.sat({**base, c: 0}) for c in [(1, 0), (1, 1), (1, 2)])
    w2.close()
    (HERE / "result_quadrants.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items()}, indent=1)[:3000])


if __name__ == "__main__":
    main()
