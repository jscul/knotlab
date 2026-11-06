"""The faces around an attachment point and the claim rule, for FACE-CLAIM-20261103-001A.

A plane knot space H split at a point z (transfer_lib.Split) has three ports, one per line through z, in the order of those lines. The
three faces at z merge into one face F0 whose boundary is three arcs: the arc A(i, j) is the old face at z between the lines of ports i
and j. Along an arc, the ports' raw values differ by the arc constant kappa (the sum of the sign differences at its corners plus its number
of corners) plus the number of skips on it; the constants of the three arcs add to 1. The pattern e with e_i + e_j = kappa(A(i, j)) + 1 is
the ports' 'all agree' pattern: it would need a skip on every arc, so it and its complement never occur. Every other port pattern has an
odd port k (its class): F0's single skip lies on the arc opposite k."""
import collections
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HALO-FORCING-20261103-001B/HALO-FORCING-20261103-001B-P001_heights_compute_the_transfer"))
import transfer_lib as TL  # noqa: E402


class Geometry:
    """the point split of H at z with its arcs, arc constants, all-agree pattern, opposite faces and own faces (original face indices)"""

    def __init__(self, H, s, n, z):
        self.H, self.s, self.n, self.z = H, [list(x) for x in s], n, z
        self.Q = TL.Split(H, self.s, n, z)
        self.faces, self.corners = TL.faces_with_corners(H)
        self.through = [k for k, L in enumerate(H) if z in L]
        self.atz = sorted({fi for (k, fi, p, q) in self.corners if z in (p, q)})
        self.arc = {fi: tuple(sorted(self.through.index(k) for (k, f, p, q) in self.corners if f == fi and z in (p, q))) for fi in self.atz}
        assert sorted(self.arc.values()) == [(0, 1), (0, 2), (1, 2)]
        self.face_of_arc = {a: fi for fi, a in self.arc.items()}

        def sg(k, p):
            return self.s[k][H[k].index(p)]
        self.kappa = {}
        for fi in self.atz:
            cs = [(k, p, q) for (k, f, p, q) in self.corners if f == fi]
            self.kappa[self.arc[fi]] = (sum(sg(k, p) ^ sg(k, q) for k, p, q in cs) + len(cs)) % 2
        assert sum(self.kappa.values()) % 2 == 1
        self.e = (0, self.kappa[(0, 1)] ^ 1, self.kappa[(0, 2)] ^ 1)
        assert self.e[1] ^ self.e[2] == self.kappa[(1, 2)] ^ 1
        self.opp = {i: next(fi for (k, fi, p, q) in self.corners if k == self.through[i] and z not in (p, q)) for i in range(3)}
        self.own = {i: {fi for fi in self.atz if i in self.arc[fi]} for i in range(3)}
        self.lfaces = {j: {fi for (k, fi, p, q) in self.corners if k == j} for j in range(len(H))}
        near_pts = {q for k in self.through for q in H[k]}
        self.beyond = [j for j, L in enumerate(H) if not (set(L) & near_pts)]

    def port_class(self, w):
        """the odd port of a port pattern (raw values of the split's ports), or None for the all-agree pattern and its complement"""
        d = [a ^ b for a, b in zip(w, self.e)]
        if sum(d) in (0, 3):
            return None
        return d.index(1) if sum(d) == 1 else d.index(0)

    def barred(self, k):
        """faces barred by class k: the face opposite port k and the two own arcs at port k"""
        return {self.opp[k]} | self.own[k]


def solutions(lines, signs, n, skip=None, chunk=1 << 22):
    """all solutions (rows of raw values) of the signed knot system on n points, minus line `skip`, by chunked bit-vector enumeration"""
    out = []
    for start in range(0, 1 << n, chunk):
        c = np.arange(start, min(start + chunk, 1 << n), dtype=np.int64)
        ok = np.ones(len(c), dtype=bool)
        for i, (L, sg) in enumerate(zip(lines, signs)):
            if i == skip:
                continue
            v = [((c >> q) & 1) ^ sg[j] for j, q in enumerate(L)]
            ok &= ~((v[0] == v[1]) & (v[1] == v[2]))
            if not ok.any():
                break
        out.append(c[ok])
    codes = np.concatenate(out)
    return ((codes[:, None] >> np.arange(n)) & 1).astype(np.int8)


def frozen_form(T):
    """(y1, y2, b1, b2) if the pattern set T has two patterns with two positions fixed, else None"""
    if len(T) != 2:
        return None
    fixed = [i for i in range(3) if len({t[i] for t in T}) == 1]
    if len(fixed) != 2:
        return None
    y1, y2 = fixed
    t0 = next(iter(T))
    return y1, y2, t0[y1], t0[y2]


def claim_rule_at(hs, L, R, Hand):
    """the claim rule for one removal (handle solutions Hand) at gluing line L with transfer R: True if a pair of handle points freezes L
    (two patterns, two points fixed) and each single point of the pair still allows L's claim at either fixed value; False if no pair
    freezes L in that form and none squeezes it otherwise; 'other' if some pair squeezes L to at most two patterns in another form"""
    img = collections.defaultdict(set)
    for w, t in R:
        img[w].add(t)
    rows = [(tuple(int(r[q]) for q in hs.ports), r) for r in Hand]
    other = False
    for p, a in itertools.combinations(hs.hpts, 2):
        if len({(int(r[p]), int(r[a])) for w, r in rows}) < 4:
            continue
        for pv, av in itertools.product((0, 1), repeat=2):
            P = {w for w, r in rows if int(r[p]) == pv and int(r[a]) == av}
            T = set().union(*[img[w] for w in P if w in img]) if P else set()
            if not T or len(T) > 2:
                continue
            ff = frozen_form(T)
            if ff is None:
                other = True
                continue
            y1, y2, b1, b2 = ff
            ok = True
            for x, xv in ((p, pv), (a, av)):
                rel = set().union(*[img[w] for w, r in rows if int(r[x]) == xv and w in img])
                if not any(t[y1] == b1 and t[y2] != b2 for t in rel) or not any(t[y2] == b2 and t[y1] != b1 for t in rel):
                    ok = False
            if ok:
                return True
    return "other" if other else False
