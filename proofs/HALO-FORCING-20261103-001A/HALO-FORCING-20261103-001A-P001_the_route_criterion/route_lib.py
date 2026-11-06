"""The route criterion for three-point crossing knots, for HALO-FORCING-20261103-001A.

A crossing knot K = {r, o, c} at a gluing line L: near points r, o (values rho, omega) leave the set T of L's patterns; the far point c
at value gamma excludes the set E of L's patterns (T lies inside E). K has a route when one of these holds.
- One port: some point of L takes one value on all of T and the other on every pattern the far point allows.
- (i): r is tied to a point y of L, T fixes y = b and another point y' = b', and E contains every pattern with (y, y') = (b, b').
- (ii): r is tied to neither y nor y', T fixes y = b, the near set {r, y, y'} excludes (rho, b, not b'), and E contains every pattern
  with (y, y') = (b, b').
(The roles of r and o may be exchanged.) Each route builds K by eliminations from one-sided knots: (i) eliminate y' from {r, o, y'} and
{y, y', c}, then use the tie; (ii) eliminate y' from {r, y, y'} and {y, y', c}, then y from {r, o, y} and the result."""
import itertools

import numpy as np


def route(AN, tie, X, I, T, Excl, cand):
    """AN: near solutions; tie: point -> tie class; X: L's points; I: L's six patterns; T, Excl: as above; cand: [(r, rho)] candidates for
    the near end"""
    allowed_far = I - Excl
    for i in range(3):
        a = {t[i] for t in T}
        b = {t[i] for t in allowed_far}
        if len(a) == 1 and len(b) == 1 and a != b:
            return "one port"
    for (r, rv) in cand:
        for i, j in itertools.permutations(range(3), 2):
            y, yp = X[i], X[j]
            for b, bp in itertools.product((0, 1), repeat=2):
                if not all(t[i] == b for t in T):
                    continue
                block = {t for t in I if t[i] == b and t[j] == bp}
                if not block or not block <= Excl:
                    continue
                if y in tie[r] and r != y and all(t[j] == bp for t in T):
                    return "(i)"
                if r != y and r != yp and y not in tie[r] and yp not in tie[r] and \
                        not np.any((AN[:, r] == rv) & (AN[:, y] == b) & (AN[:, yp] == 1 - bp)):
                    return "(ii)"
    return None
