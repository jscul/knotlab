"""Small circuits of a splice from its two sides, for HANDLE-LOCALITY-20261103-001B.

A splice T joins a near side (here a knot space S minus a removed line M, with its line L kept) to a far side (a knot space split at a
point, whose three lines through the point carry L's points as ports). At a removal where L shows six patterns, the far side admits exactly
L's six patterns, so T's solutions restricted to S's points are those of S minus M. By the join lemma (HANDLE-EMERGENCE B, Lemma 1), a
pattern (u, v) on a near set U and a far set V occurs in T iff some port pattern is compatible with both. So every set of up to maxsize
points can be tested from the two sides' solution sets alone, without enumerating T."""
import itertools

import numpy as np


def _codes(A, cols):
    c = np.zeros(len(A), dtype=np.int64)
    for i, q in enumerate(cols):
        c |= A[:, q].astype(np.int64) << i
    return c


def port_masks(A, cols, pcode):
    """for each pattern u on the columns, the bitmask of port patterns compatible with it (0 if u never occurs)"""
    out = np.zeros(1 << len(cols), dtype=np.int64)
    np.bitwise_or.at(out, _codes(A, cols), np.int64(1) << pcode)
    return out


def circuits(AN, near, AF, far, nports, maxsize):
    """minimal constrained sets of up to maxsize points of the splice, as frozensets of point labels.
    AN: near solutions (columns = near labels); near: near labels (ports included); nports: the three port labels (near labels);
    AF: far solutions with columns far + nports (in that order); far: far labels."""
    pN = _codes(AN, list(nports))
    fcols = {q: i for i, q in enumerate(far)}
    pF = _codes(AF, [len(far) + i for i in range(3)])
    cacheN, cacheF = {}, {}

    def tn(U):
        if U not in cacheN:
            cacheN[U] = port_masks(AN, list(U), pN)
        return cacheN[U]

    def tf(V):
        if V not in cacheF:
            cacheF[V] = port_masks(AF, [fcols[q] for q in V], pF)
        return cacheF[V]

    def constrained(K):
        U = tuple(q for q in K if q not in fcols)
        V = tuple(q for q in K if q in fcols)
        if not V:
            return bool((tn(U) == 0).any())
        if not U:
            return bool((tf(V) == 0).any())
        a, b = tn(U), tf(V)
        return bool(((a[:, None] & b[None, :]) == 0).any())

    pts = sorted(near) + sorted(far)
    flags = {}
    found = []
    for r in range(1, maxsize + 1):
        for K in itertools.combinations(pts, r):
            sub = any(flags.get(K[:i] + K[i + 1:], False) for i in range(r)) if r > 1 else False
            if sub:
                flags[K] = True
                continue
            c = constrained(K)
            flags[K] = c
            if c:
                found.append(frozenset(K))
    return found


def solve(G, lines, signs, pts):
    """solutions of a signed system on the listed points (columns in that order)"""
    idx = {p: i for i, p in enumerate(pts)}
    return G.states(len(pts))[G.sat_matrix([tuple(idx[q] for q in L) for L in lines], signs, len(pts)).all(axis=1)]


def far_side(G, HS, sS, nS, L, HF, sF, nF, pt=0):
    """the far side of splicing line L of HS into point pt of HF, with the twist that glue_lib.splice chooses: the first twist (in
    product order) whose port patterns are exactly L's six patterns, which is the first that keeps the splice unsatisfiable, since HS
    minus L forces L's points to its all-equal pair. Returns (far lines, far signs, far labels, solutions with columns far + ports)."""
    X = list(HS[L])
    sig = tuple(sS[L])
    nae = {t for t in itertools.product((0, 1), repeat=3) if t not in (sig, tuple(1 - b for b in sig))}
    relabel, k = {}, 0
    for p in range(nF):
        if p != pt:
            relabel[p] = nS + k
            k += 1
    through = [(l, s) for l, s in zip(HF, sF) if pt in l]
    others = [(l, s) for l, s in zip(HF, sF) if pt not in l]
    far = sorted(relabel.values())
    for tw in itertools.product((0, 1), repeat=3):
        lines = [tuple(relabel[q] for q in l) for l, _ in others]
        signs = [list(s) for _, s in others]
        for i, (l, s) in enumerate(through):
            keep = [(relabel[q], s[j]) for j, q in enumerate(l) if q != pt]
            lines.append(tuple(q for q, _ in keep) + (X[i],))
            signs.append([sg for _, sg in keep] + [tw[i]])
        AF = solve(G, lines, signs, far + X)
        if {tuple(int(b) for b in r[len(far):]) for r in AF} == nae:
            return lines, signs, far, AF
    return None


def splice_pieces(G, A, B, li, pt):
    """splice A's line li into B's point pt (glue_lib.splice), carrying piece labels of lines and points"""
    H1, s1, n1, l1, p1 = A
    H2, s2, n2, l2, p2 = B
    ls, ss, n, side, ports = G.splice(H1, s1, n1, li, H2, s2, n2, pt)
    through = [i for i, l in enumerate(H2) if pt in l]
    others = [i for i, l in enumerate(H2) if pt not in l]
    lines_lab = [l1[i] for i in range(len(H1)) if i != li] + [l2[i] for i in others] + [l2[i] for i in through]
    pts_lab = list(p1) + [p2[p] for p in range(n2) if p != pt]
    return (ls, ss, n, lines_lab, pts_lab)


def new_knots(E, G, AN, HS, sS, nS, L, F, maxsize):
    """the new crossing knots (raw bitmasks) of splicing HS minus a removal (solutions AN) at line L into the far space F, exact up
    to maxsize points (closure up to ties; a derivation never uses a knot larger than its target)"""
    HF, sF, nF = F
    X = list(HS[L])
    lines, signs, far, AF = far_side(G, HS, sS, nS, L, HF, sF, nF)
    n = nS + nF - 1
    cs = circuits(AN, list(range(nS)), AF, far, X, maxsize)
    masks = [sum(1 << q for q in K) for K in cs]
    rep = E.tie_classes(n, [m for m in masks if bin(m).count("1") == 2])
    knots = [m for m in masks if bin(m).count("1") >= 3]
    inner = sum(1 << q for q in range(nS) if q not in X)
    outer = sum(1 << q for q in far)
    can = {m: E.canon(m, rep) for m in knots}
    cross = {m: bool(m & inner and m & outer) for m in knots}
    gen = E.closure(set(can.values()), {can[m] for m in knots if not cross[m]}, n)
    return [m for m in knots if cross[m] and can[m] not in gen], rep, far, AF
