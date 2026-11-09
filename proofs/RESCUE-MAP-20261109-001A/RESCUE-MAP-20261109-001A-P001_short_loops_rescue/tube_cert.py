"""Tube certificates: exact distances and route parities on an infinite tube, proved by local conditions checked on a finite window.

For the tube T/<v>, v primitive, a contact (t, p) is read at position det(v, p) along the tube. A candidate (d, c) is read off a
breadth-first search, extended beyond a window by its period, and accepted only if it satisfies, at every contact, the local conditions
that characterise the true distances and shortest-route parities to the target:
  (i) d = 0 exactly at the target, d >= 0;  (ii) d(x) <= d(y) + 1 on every arc x -> y;  (iii) every x but the target has an arc x -> y
  with d(y) = d(x) - 1;  (iv) c(target) = 1 and c(x) = sum of c(y) over arcs x -> y with d(y) = d(x) - 1, mod 2.
Beyond the window every condition at x is the condition at x shifted by one period, since d shifts by a constant and c not at all, so the
conditions on the window and one period past it hold everywhere."""
from __future__ import annotations

import rescue_lib as R  # noqa: E402


def det(v, p):
    return v[0] * p[1] - v[1] * p[0]


class Tube:
    def __init__(self, kind, v):
        self.kind, self.v = kind, v
        self.Q = R.Quotient([v])
        g, s, t = R.egcd(*v)
        assert g == 1
        self.u = (-t, s)

    def pos(self, p):
        return det(self.v, p)

    def point(self, j):
        return (j * self.u[0], j * self.u[1])

    def contact(self, c):
        return (c[0], self.pos(c[1]))

    def outs(self, x):
        t, j = x
        return [self.contact(c) for c in R.out_arcs(self.kind, (t, self.point(j)))]

    def ring_slots(self, rk, j):
        return [self.contact(c) for c in R.slots(self.kind, rk, self.point(j))]

    def width(self):
        """the largest change of position along an arc or within a ring"""
        w = 0
        for t in range(R.TYPES[self.kind]):
            for y in self.outs((t, 0)):
                w = max(w, abs(y[1]))
        for rk in R.rings_of(self.kind):
            ps = [c[1] for c in self.ring_slots(rk, 0)]
            w = max(w, max(ps) - min(ps))
        return w


def certificate(kind, v, t0, W=160, radius=700):
    tube = Tube(kind, v)
    dist, cnt = R.bfs_counts(kind, tube.Q, (t0, (0, 0)), radius)
    tab = {}
    for (t, p), d in dist.items():
        j = tube.pos(p)
        if abs(j) <= W:
            tab[(t, j)] = (d, cnt[(t, p)])
    types = range(R.TYPES[kind])
    assert all((t, j) in tab for t in types for j in range(-W, W + 1)), "window not covered by the radius"
    w = tube.width()
    found = None
    for P in range(1, 13):
        for F in range(1, 40):
            ok = True
            DR = tab[(0, F + P)][0] - tab[(0, F)][0]
            DL = tab[(0, -F - P)][0] - tab[(0, -F)][0]
            for t in types:
                for j in range(F, W - P + 1):
                    a, b = tab[(t, j)], tab[(t, j + P)]
                    if b[0] - a[0] != DR or a[1] != b[1]:
                        ok = False
                        break
                    a, b = tab[(t, -j)], tab[(t, -j - P)]
                    if b[0] - a[0] != DL or a[1] != b[1]:
                        ok = False
                        break
                if not ok:
                    break
            if ok and DR > 0 and DL > 0:
                found = (P, F, DR, DL)
                break
        if found:
            break
    assert found, "no period found"
    P, F, DR, DL = found

    def val(x):
        t, j = x
        if -F <= j <= F:
            return tab[(t, j)]
        if j > F:
            k, r = divmod(j - F, P)
            d, c = tab[(t, F + r)]
            return d + k * DR, c
        k, r = divmod(-F - j, P)
        d, c = tab[(t, -F - r)]
        return d + k * DL, c

    # the local conditions on the window and one period past it on each side
    lo, hi = -F - w - P - 1, F + w + P + 1
    bad = []
    for t in types:
        for j in range(lo, hi + 1):
            x = (t, j)
            d, c = val(x)
            outs = tube.outs(x)
            dy = [val(y) for y in outs]
            if (t, j) == (t0, 0):
                if (d, c) != (0, 1):
                    bad.append(("target", x))
                continue
            if d <= 0:
                bad.append(("(i)", x))
            if any(d > e + 1 for e, _ in dy):
                bad.append(("(ii)", x))
            down = [ce for (e, ce) in dy if e == d - 1]
            if not down:
                bad.append(("(iii)", x))
            if sum(down) % 2 != c:
                bad.append(("(iv)", x))
    # agreement with the search on the whole window
    agree = all(val(x) == tab[x] for x in tab)
    return {"tube": tube, "val": val, "P": P, "F": F, "DR": DR, "DL": DL, "w": w, "bad": bad, "agree": agree}


def rings(cert, rk, j):
    """(least distance, closest slots, parity of each closest slot) of the ring of kind rk at position j, or None if it holds the target"""
    tube, val = cert["tube"], cert["val"]
    sl = tube.ring_slots(rk, j)
    vals = [val(x) for x in sl]
    if any(d == 0 for d, _ in vals):
        return None
    d = min(x[0] for x in vals)
    close = tuple(i for i in range(len(sl)) if vals[i][0] == d)
    return d, close, tuple(vals[i][1] for i in close)


def quotient_conditions(cert, rk="R"):
    """Q1-Q3 for the quotients <v, N u> of the tube: the side profiles of the rings' least distances and closest slots, and the least
    N1 beyond which two lifts on one side never tie"""
    P, F, w = cert["P"], cert["F"], cert["w"]
    span = F + 3 * w + 3 * P
    prof = {j: rings(cert, rk, j) for j in range(-span - 4 * P, span + 4 * P + 1)}
    held = [j for j, x in prof.items() if x is None]
    right = [j for j in prof if prof[j] is not None and j > 0]
    left = [j for j in prof if prof[j] is not None and j <= 0]
    # Q3: every closest slot has an odd count
    q3 = all(all(par) for x in prof.values() if x is not None for par in [x[2]])
    # strict growth beyond a point on each side (checked over one period past the window, so everywhere by periodicity)
    r = {j: prof[j][0] for j in prof if prof[j] is not None}
    edge = F + w + P
    grow_right = all(r[j + 1] > r[j] for j in range(edge, span + 3 * P))
    grow_left = all(r[j - 1] > r[j] for j in range(-span - 3 * P, -edge + 1)[::-1] if j - 1 in r)
    # Q2: the families of closest-slot sets on the two sides share no set (mid rings counted on both sides)
    sets_r = {prof[j][1] for j in right}
    sets_l = {prof[j][1] for j in left}
    q2 = not (sets_r & sets_l)
    # N1: two lifts on one side N >= N1 apart never tie
    central = [j for j in r if abs(j) <= edge]
    N1 = edge + 1
    while True:
        def rr(j):
            x = rings(cert, rk, j)
            return None if x is None else x[0]
        ok = all((rr(j + N1) is None or rr(j + N1) > r[j]) for j in central if j > 0) and \
             all((rr(j - N1) is None or rr(j - N1) > r[j]) for j in central if j <= 0)
        if ok:
            break
        N1 += 1
    return {"Q2": q2, "Q3": q3, "grow right": grow_right, "grow left": grow_left, "N1": N1, "held": held,
            "sets right": sorted(sets_r), "sets left": sorted(sets_l)}
