"""The knot closure as resolution, for TWO-ROUND-BRIDGE-20261106-001A.

A knot {a, b, c} of a complement-closed relation misses exactly one complementary pair of patterns {v, not v}; as clauses it is the
pair of 3-clauses forbidding v and not v (a signed not-all-equal constraint). Two knots A, B sharing two classes h, s are
sign-compatible when their forbidden patterns relate h and s differently (one forbids h = s, the other h != s, in literal terms).
Exactly then do the two clause pairs have width-3 resolvents: eliminating h gives the knot on (A | B) - h, eliminating s the knot on
(A | B) - s. Incompatible pairs have no resolvent of width 3 (every pair of their clauses clashes on both shared variables or on none).

Part 1 extends PENDANT-LINE A's local engine (local_lib.Local) with forbidden-pattern types and the sign-compatible two-round rule.
Part 2 computes, on small relations, which crossing knots resolution derives from the one-sided implicates on at most three
variables, at each width.
"""
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PENDANT-LINE-20261106-001A/PENDANT-LINE-20261106-001A-P001_creation_is_decided_at_the_gluing_line"))
import local_lib as LL  # noqa: E402

PY = LL.PY


# ------------------------------------------------------------------------------------------------ part 1: the local engine with types
class Bridge(LL.Local):
    def types(self, rel, A):
        """for every knot triple and every pair in it: boolean array 'the forbidden pattern takes the pair equal' (meaningful on knots)"""
        eq = {}
        for tri in A["knot"]:
            miss = {}
            for v in itertools.product((0, 1), repeat=3):
                if v[0]:
                    continue
                nv = tuple(1 - b for b in v)
                m1, m2 = self.mask(tri, v), self.mask(tri, nv)
                miss[v] = ((rel & m1) == 0) & ((rel & m2) == 0)
            for i, j in itertools.combinations(range(3), 2):
                acc = np.zeros(len(rel), dtype=bool)
                for v, mm in miss.items():
                    if v[i] == v[j]:
                        acc |= mm
                eq[(tri, tri[i], tri[j])] = acc
            # a non-degenerate knot misses exactly one class
            cnt = sum(mm.astype(np.int8) for mm in miss.values())
            eq[(tri, "count")] = cnt
        return eq

    def two_rounds_nr(self, A, eq, mode="compatible"):
        """the two-round rule with every step required sign-compatible (mode 'compatible') or, as a mutation control, required
        incompatible (mode 'incompatible'); also returns the number of compatible steps whose conclusion is not a knot"""
        knot = A["knot"]
        K = lambda *p: knot[tuple(sorted(p))]  # noqa: E731

        def E(t, a, b):
            t = tuple(sorted(t))
            return eq[(t, a, b) if (t, a, b) in eq else (t, b, a)]

        def ok(t1, t2, a, b):
            c = E(t1, a, b) ^ E(t2, a, b)
            return c if mode == "compatible" else ~c

        n = len(A["ok"])
        zero = np.zeros(n, dtype=bool)
        bad = np.zeros(n, dtype=bool)
        R, r1 = {}, {}
        for c in self.C:
            for x in self.N:
                for y in self.Y:
                    acc = zero.copy()
                    for z in self.Y:
                        if z != y:
                            step = K(c, y, z) & K(x, y, z) & ok((c, y, z), (x, y, z), y, z)
                            acc |= step
                            bad |= step & ~K(c, x, y) & (mode == "compatible")
                    r1[(c, x, y)] = K(c, x, y) & acc
                    R[tuple(sorted((c, x, y)))] = r1[(c, x, y)]
            for x, w in itertools.combinations(self.N, 2):
                acc = zero.copy()
                for y in self.Y:
                    step = r1[(c, x, y)] & r1[(c, w, y)] & ok((c, x, y), (c, w, y), c, y)
                    acc |= step
                    bad |= step & ~K(c, x, w) & (mode == "compatible")
                R[tuple(sorted((c, x, w)))] = K(c, x, w) & acc
        for c, c2 in itertools.combinations(self.C, 2):
            for x in self.N:
                acc = zero.copy()
                for y in self.Y:
                    g, a1, a2 = K(c, c2, y), r1[(c, x, y)], r1[(c2, x, y)]
                    step = (g & a1 & ok((c, c2, y), (c, x, y), c, y)) | (g & a2 & ok((c, c2, y), (c2, x, y), c2, y)) | \
                           (a1 & a2 & ok((c, x, y), (c2, x, y), x, y))
                    acc |= step
                    bad |= step & ~K(c, c2, x) & (mode == "compatible")
                R[tuple(sorted((c, c2, x)))] = K(c, c2, x) & acc
        return R, bad

    def incompatible_witness(self, A, eq):
        """crossing knots {c, x, y} for which the semantic round one has a witness z whose two knots are sign-incompatible"""
        knot = A["knot"]
        K = lambda *p: knot[tuple(sorted(p))]  # noqa: E731
        n = len(A["ok"])
        out = np.zeros(n, dtype=np.int64)
        for c in self.C:
            for x in self.N:
                for y in self.Y:
                    for z in self.Y:
                        if z == y:
                            continue
                        t1, t2 = tuple(sorted((c, y, z))), tuple(sorted((x, y, z)))
                        e1 = eq[(t1, y, z) if (t1, y, z) in eq else (t1, z, y)]
                        e2 = eq[(t2, y, z) if (t2, y, z) in eq else (t2, z, y)]
                        out += (A["ok"] & K(c, x, y) & K(c, y, z) & K(x, y, z) & ~(e1 ^ e2)).astype(np.int64)
        return out


# ------------------------------------------------------------------------------------------------ part 2: widths on small relations
def implicates(rows, cols, maxw):
    """all clauses of width <= maxw over the variables cols (global indices) that every row satisfies, as (pos, neg) bitmasks; rows
    are tuples indexed like cols"""
    out = set()
    for w in range(1, maxw + 1):
        for U in itertools.combinations(range(len(cols)), w):
            seen = {tuple(r[i] for i in U) for r in rows}
            for v in itertools.product((0, 1), repeat=w):
                if v in seen:
                    continue
                # the clause forbidding cols[U] = v: literal x != v_i, i.e. positive when v_i = 0
                pos = sum(1 << cols[i] for i, b in zip(U, v) if b == 0)
                neg = sum(1 << cols[i] for i, b in zip(U, v) if b == 1)
                out.add((pos, neg))
    return out


def popcount(m):
    return bin(m).count("1")


def saturate(axioms, w, targets, pivots=None):
    """the width-w resolution closure of axioms (all clauses of width <= w), resolving only on variables in the bitmask pivots when it
    is given; stops early once every target is subsumed. Returns the targets subsumed by a derived clause, each with the depth at which
    it was first subsumed"""
    def subsumed(t, S):
        tp, tn = t
        return any((p & ~tp) == 0 and (n & ~tn) == 0 for p, n in S)

    S = {c for c in axioms if popcount(c[0] | c[1]) <= w}
    done = {t: 0 for t in targets if subsumed(t, S)}
    frontier = set(S)
    depth = 0
    while frontier and len(done) < len(targets):
        depth += 1
        new = set()
        allc = list(S)
        for (p1, n1) in frontier:
            for (p2, n2) in allc:
                clash = (p1 & n2) | (n1 & p2)
                if clash == 0 or clash & (clash - 1) or (pivots is not None and not clash & pivots):
                    continue
                p, n = (p1 | p2) & ~clash, (n1 | n2) & ~clash
                if p & n or popcount(p | n) > w:
                    continue
                c = (p, n)
                if c not in S and c not in new:
                    new.add(c)
        S |= new
        frontier = new
        for t in targets:
            if t not in done and subsumed(t, S):
                done[t] = depth
    return done


def knot_clauses(rows, tri):
    """the two clauses of the knot on tri (global indices; rows indexed globally), or None if tri is not constrained"""
    seen = {tuple(r[p] for p in tri) for r in rows}
    miss = [v for v in itertools.product((0, 1), repeat=3) if v not in seen]
    if not miss:
        return None
    out = []
    for v in miss:
        pos = sum(1 << p for p, b in zip(tri, v) if b == 0)
        neg = sum(1 << p for p, b in zip(tri, v) if b == 1)
        out.append((pos, neg))
    return out
