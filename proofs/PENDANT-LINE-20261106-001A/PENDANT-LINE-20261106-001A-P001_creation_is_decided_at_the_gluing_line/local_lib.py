"""Local configurations of a splice at its gluing line, for PENDANT-LINE-20261106-001A.

The gluing line's points Y are taken as literals (signs zero, by complementing points), so the near side shows on Y exactly the six
non-constant patterns P_Y. A local configuration is
- a near relation: a complement-closed set of (Y-pattern, values of k further near classes) showing all six Y-patterns, and
- m far classes of a census far side, through the far gadget's own relation to Y.
Their join is the projection of a splice onto Y, the k near classes and the m far classes. Everything below is computed for every near
relation at once (numpy over uint64 bitmasks: slot i * 2^k + t holds Y-pattern i with near values t).

Points are numbered: 0, 1, 2 = Y; 3 .. 3+k-1 = near classes; then the far classes.
"""
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/TWO-BIT-SCREEN-20261105-001A/TWO-BIT-SCREEN-20261105-001A-P001_hidden_points_and_the_two_bit_screening_lemma"))
import screen_lib as SL  # noqa: E402

PY = [t for t in itertools.product((0, 1), repeat=3) if len(set(t)) == 2]   # 001 010 011 100 101 110
COMP = {i: PY.index(tuple(1 - b for b in PY[i])) for i in range(6)}


# ------------------------------------------------------------------------------------------------ far sides in the literal frame
def far_gadget(F):
    """the far side F split at a point with ports on a zero-sign line: (far point labels, rows (Y-pattern index, far values))"""
    HS, sS, nS = [(0, 1, 2)], [[0, 0, 0]], 3
    lines, signs, far, AF = SL.J.far_side(SL.G, HS, sS, nS, 0, *F)
    rows = set()
    for r in AF:
        y = tuple(int(v) for v in r[len(far):])
        rows.add((PY.index(y), tuple(int(v) for v in r[:len(far)])))
    assert {i for i, f in rows} == set(range(6))
    return far, sorted(rows)


def far_classes(F):
    """far points up to ties among themselves; drop points tied to a Y point (none occur) and record free ones"""
    far, rows = far_gadget(F)
    m = len(far)
    reps = []
    for a in range(m):
        tied = None
        for b in reps:
            vals = {(f[a], f[b]) for i, f in rows}
            if len(vals) < 4:
                tied = b
        for y in range(3):
            vals = {(f[a], PY[i][y]) for i, f in rows}
            assert len(vals) == 4, "a far point tied to the gluing line"
        if tied is None:
            reps.append(a)
    return reps, rows


def far_relation(rows, cols):
    """the far gadget's relation restricted to the chosen far points: set of (Y index, tuple of their values)"""
    return sorted({(i, tuple(f[c] for c in cols)) for i, f in rows})


# ------------------------------------------------------------------------------------------------ near relations
def near_relations(k):
    """every complement-closed near relation on Y and k classes showing the six Y-patterns, as uint64 masks"""
    T = 1 << k
    reps = [0, 1, 2]                                   # Y-patterns 001, 010, 011; their complements are 5, 4, 3
    subsets = np.arange(1, 1 << T, dtype=np.uint64)    # nonempty subsets of the 2^k near values
    out = np.zeros(len(subsets) ** 3, dtype=np.uint64)
    comp_t = [(~t) & (T - 1) for t in range(T)]
    cache = {}
    for idx, i in enumerate(reps):
        ci = COMP[i]
        vals = np.zeros(len(subsets), dtype=np.uint64)
        for t in range(T):
            hit = ((subsets >> np.uint64(t)) & np.uint64(1)).astype(bool)
            vals[hit] |= np.uint64(1) << np.uint64(i * T + t)
            vals[hit] |= np.uint64(1) << np.uint64(ci * T + comp_t[t])
        cache[idx] = vals
    n = len(subsets)
    a = cache[0][:, None, None] | cache[1][None, :, None] | cache[2][None, None, :]
    return a.reshape(-1)


# ------------------------------------------------------------------------------------------------ the local engine
class Local:
    """the projection, onto Y, k near classes and the chosen far classes, of every near relation joined with the far relation"""

    def __init__(self, k, farrel, mfar):
        self.k, self.m = k, mfar
        self.T = 1 << k
        self.far = farrel                       # list of (Y index, far values tuple)
        self.npts = 3 + k + mfar
        self.Y = [0, 1, 2]
        self.N = list(range(3, 3 + k))
        self.C = list(range(3 + k, 3 + k + mfar))

    def kind(self, p):
        return "Y" if p < 3 else ("N" if p < 3 + self.k else "C")

    def mask(self, pts, vals):
        """near slots compatible with the given values on the given points (for far points: some far row with those values on Y)"""
        m = 0
        for i in range(6):
            ok = True
            for p, v in zip(pts, vals):
                if p < 3 and PY[i][p] != v:
                    ok = False
            if not ok:
                continue
            fp = [(p - 3 - self.k, v) for p, v in zip(pts, vals) if p >= 3 + self.k]
            if fp and not any(all(f[j] == v for j, v in fp) for ii, f in self.far if ii == i):
                continue
            for t in range(self.T):
                if all(((t >> (p - 3)) & 1) == v for p, v in zip(pts, vals) if 3 <= p < 3 + self.k):
                    m |= 1 << (i * self.T + t)
        return np.uint64(m)

    def count(self, rel, pts):
        """number of value patterns occurring on pts, for every relation"""
        c = np.zeros(len(rel), dtype=np.int8)
        for vals in itertools.product((0, 1), repeat=len(pts)):
            mk = self.mask(pts, vals)
            if mk:
                c += ((rel & mk) != 0).astype(np.int8)
        return c

    def analyse(self, rel):
        """returns dict with: 'ok' (non-degenerate: no two local points tied), 'knot'[triple], 'cross'[triple], 'base'[triple]"""
        pts = range(self.npts)
        ok = np.ones(len(rel), dtype=bool)
        for a, b in itertools.combinations(pts, 2):
            if self.kind(a) == "Y" and self.kind(b) == "Y":
                continue
            ok &= self.count(rel, (a, b)) == 4
        knot, cross, base = {}, {}, {}
        for tri in itertools.combinations(pts, 3):
            kinds = [self.kind(p) for p in tri]
            knot[tri] = self.count(rel, tri) < 8
            cr = ("C" in kinds) and ("N" in kinds)
            cross[tri] = cr
            base[tri] = knot[tri] & (not cr)
        return {"ok": ok, "knot": knot, "cross": cross, "base": base}

    def two_rounds(self, A, drop=()):
        """the two-round rule. Round 1: {c, x, y} (c far, x near off Y, y on Y) is reached when it is a knot and some z on Y makes {c, y, z}
        a far base knot and {x, y, z} a near knot. Round 2: {c, x, w} is reached when it is a knot and some y on Y has {c, x, y} and
        {c, w, y} reached; {c, c', x} is reached when it is a knot and some y on Y has two of {c, c', y} (far base), {c, x, y}, {c', x, y}
        (reached). drop names rule parts to switch off (mutation controls): 'round 1', 'pairs', 'two far'."""
        knot = A["knot"]
        K = lambda *p: knot[tuple(sorted(p))]  # noqa: E731
        n = len(A["ok"])
        zero = np.zeros(n, dtype=bool)
        R, r1 = {}, {}
        for c in self.C:
            for x in self.N:
                for y in self.Y:
                    acc = zero.copy()
                    for z in self.Y:
                        if z != y:
                            acc |= K(c, y, z) & K(x, y, z)
                    r1[(c, x, y)] = zero if "round 1" in drop else (K(c, x, y) & acc)
                    R[tuple(sorted((c, x, y)))] = r1[(c, x, y)]
            for x, w in itertools.combinations(self.N, 2):
                acc = zero.copy()
                for y in self.Y:
                    acc |= r1[(c, x, y)] & r1[(c, w, y)]
                R[tuple(sorted((c, x, w)))] = zero if "pairs" in drop else (K(c, x, w) & acc)
        for c, c2 in itertools.combinations(self.C, 2):
            for x in self.N:
                acc = zero.copy()
                for y in self.Y:
                    g, a1, a2 = K(c, c2, y), r1[(c, x, y)], r1[(c2, x, y)]
                    acc |= (g & a1) | (g & a2) | (a1 & a2)
                R[tuple(sorted((c, c2, x)))] = zero if "two far" in drop else (K(c, c2, x) & acc)
        return R

    def criterion(self, A):
        """the two-level rule: Y-sets by switch rules, then near-pair and two-far faces; returns {triple: reached} for crossing triples"""
        knot = A["knot"]
        K = lambda *p: knot[tuple(sorted(p))]  # noqa: E731
        n = len(A["ok"])
        R = {}
        Yset = {}
        for c in self.C:
            for x in self.N:
                for y in self.Y:
                    Yset[(c, x, y)] = np.zeros(n, dtype=bool)
            for _ in range(4):
                for x in self.N:
                    for y in self.Y:
                        cand = K(c, x, y)
                        acc = np.zeros(n, dtype=bool)
                        for z in self.Y:
                            if z == y:
                                continue
                            a, f, nn = K(c, y, z), Yset[(c, x, z)], K(y, z, x)
                            acc |= (a & f) | (a & nn) | (f & nn)
                        Yset[(c, x, y)] |= cand & acc
            for x in self.N:
                for y in self.Y:
                    R[tuple(sorted((c, x, y)))] = Yset[(c, x, y)]
            for x, w in itertools.combinations(self.N, 2):
                acc = np.zeros(n, dtype=bool)
                for y in self.Y:
                    yx, yw, nn = Yset[(c, x, y)], Yset[(c, w, y)], K(y, x, w)
                    acc |= (yx & (yw | nn)) | (yw & nn)
                R[tuple(sorted((c, x, w)))] = K(c, x, w) & acc
        for c, c2 in itertools.combinations(self.C, 2):
            for x in self.N:
                acc = np.zeros(n, dtype=bool)
                for y in self.Y:
                    g, r1, r2 = K(c, c2, y), Yset[(c, x, y)], Yset[(c2, x, y)]
                    acc |= (g & r1) | (g & r2) | (r1 & r2)
                R[tuple(sorted((c, c2, x)))] = K(c, c2, x) & acc
        return R, Yset

    def closure_violations(self, A, R):
        """for every four points and every eliminated point h: the triple avoiding h is a crossing knot, two triples through h are knots
        in (reached or base), yet the triple avoiding h is not reached. Returns {(h kind, produced triple): count} and the total."""
        knot, cross, base = A["knot"], A["cross"], A["base"]
        n = len(A["ok"])
        inS = {}
        for tri in knot:
            inS[tri] = base[tri] | (R[tri] if (cross[tri] and tri in R) else np.zeros(n, dtype=bool))
        viol = {}
        for Q in itertools.combinations(range(self.npts), 4):
            for h in Q:
                F = tuple(p for p in Q if p != h)
                if not cross[F]:
                    continue
                through = [tuple(sorted(set(Q) - {p})) for p in Q if p != h]
                cnt = sum((knot[t] & inS[t]).astype(np.int8) for t in through)
                reachedF = R.get(F, np.zeros(n, dtype=bool))
                bad = A["ok"] & knot[F] & (cnt >= 2) & ~reachedF
                s = int(bad.sum())
                if s:
                    viol[(self.kind(h), F)] = viol.get((self.kind(h), F), 0) + s
        return viol
