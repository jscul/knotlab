"""The halo of an opened handle on large plane pieces, for HALO-FORCING-20261103-001C.

A Fano plane minus a line (the handle) is spliced into a point z of a plane knot space H2 (as glue_lib.splice does: the line's i-th point
joins the i-th line through z). For a removal M inside the handle and a plane gluing line L, creation at L is decided by the route
criterion of ticket A over pairs of handle points, which reads the plane piece only through the transfer R(L) between the ports and L;
R(L) is computed by heights (ticket B). Nothing on the plane side is enumerated."""
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HALO-FORCING-20261103-001B/HALO-FORCING-20261103-001B-P001_heights_compute_the_transfer"))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-LOCALITY-20261103-001B/HANDLE-LOCALITY-20261103-001B-P001_where_creation_happens"))
import transfer_lib as TL  # noqa: E402
import join_lib as J  # noqa: E402


def fast_splice(H1, s1, n1, li, H2, s2, n2, pt):
    """glue_lib.splice's construction, with the twist chosen by theory instead of by enumeration: the splice fails iff the ports' consistent
    pair (H2's signs at pt, shifted by the twist) is the line's all-equal pair, so the twist is the first (in product order) equal to
    H2's signs at pt XOR the line's signs, or their complement."""
    Lp = H1[li]
    sL = list(s1[li])
    rest1 = [(l, s) for i, (l, s) in enumerate(zip(H1, s1)) if i != li]
    relabel, k = {}, 0
    for p in range(n2):
        if p != pt:
            relabel[p] = n1 + k
            k += 1
    through = [(l, s) for l, s in zip(H2, s2) if pt in l]
    others = [(l, s) for l, s in zip(H2, s2) if pt not in l]
    sorig = [s[list(l).index(pt)] for l, s in through]
    good = {tuple(a ^ b for a, b in zip(sorig, sL)), tuple(1 ^ a ^ b for a, b in zip(sorig, sL))}
    tw = next(t for t in itertools.product((0, 1), repeat=3) if t in good)
    lines = [tuple(l) for l, _ in rest1] + [tuple(relabel[q] for q in l) for l, _ in others]
    signs = [list(s) for _, s in rest1] + [list(s) for _, s in others]
    for i, (l, s) in enumerate(through):
        keep = [(relabel[q], s[j]) for j, q in enumerate(l) if q != pt]
        lines.append(tuple(q for q, _ in keep) + (Lp[i],))
        signs.append([sg for _, sg in keep] + [tw[i]])
    return lines, signs, n1 + n2 - 1, relabel, tw, sorig, len(rest1), len(others)


class HaloSpace:
    """the Fano plane (lines HF, signs sF) minus its line li spliced into point z of the plane knot space (H2, s2, n2)"""

    def __init__(self, HF, sF, li, H2, s2, n2, z, G):
        self.G = G
        self.lines, self.signs, self.n, self.relabel, self.tw, self.sorig, self.nh, self.no = fast_splice(HF, sF, len({q for L in HF for q in L}), li, H2, s2, n2, z)
        self.nF = len({q for L in HF for q in L})
        self.ports = list(HF[li])
        self.hpts = [q for q in range(self.nF) if q not in self.ports]
        self.Q = TL.Split(H2, [list(x) for x in s2], n2, z)
        # map the split's labels to the splice's: H2's points by relabel, the split's ports (in the order of lines through z) to the line's points
        self.qmap = dict(self.relabel)
        for i in range(3):
            self.qmap[n2 + i] = self.ports[i]
        self.delta = {self.ports[i]: self.tw[i] ^ self.sorig[i] for i in range(3)}
        # the split's line index for each plane line of the splice
        self.qline = {}
        for k in range(self.nh, len(self.lines)):
            pts = set(self.lines[k])
            self.qline[k] = next(j for j, L in enumerate(self.Q.lines) if {self.qmap[q] for q in L} == pts)

    def handle(self, M):
        """solutions of the handle minus M on the Fano points (the ports among them)"""
        keep = [i for i in range(self.nh) if i != M]
        return J.solve(self.G, [self.lines[i] for i in keep], [self.signs[i] for i in keep], list(range(self.nF)))

    def transfer(self, L):
        """R(L) in the splice's raw values: {(port pattern, L pattern in the splice's point order)}"""
        j = self.qline[L]
        QL = list(self.Q.lines[j])
        X = list(self.lines[L])
        out = set()
        for w, t in self.Q.transfer(j):
            val = {self.qmap[q]: b for q, b in zip(QL, t)}
            w2 = tuple(b ^ self.delta[self.ports[i]] for i, b in enumerate(w))
            for q in X:
                if q in self.delta:
                    val[q] = val[q] ^ self.delta[q]
            out.add((w2, tuple(val[q] for q in X)))
        return out


def creates(hs, M, L, F, Hand=None, R=None):
    """does an opened handle (removal M) create at the plane gluing line L with far side F? (route criterion over handle pairs)"""
    G = hs.G
    X = list(hs.lines[L])
    if R is None:
        R = hs.transfer(L)
    if Hand is None:
        Hand = hs.handle(M)
    pcol = hs.ports
    Jh = {tuple(int(r[q]) for q in pcol) for r in Hand}
    joint = [(r, t) for r in Hand for (w, t) in R if tuple(int(r[q]) for q in pcol) == w]
    I = {t for (r, t) in joint}
    if len(I) != 6:
        return None
    HF, sF, nF = F
    lines, signs, far, AF = J.far_side(G, hs.lines, hs.signs, hs.n, L, HF, sF, nF)
    TF = {(c, g): {tuple(int(v) for v in r[len(far):]) for r in AF[AF[:, far.index(c)] == g]} for c in far for g in (0, 1)}
    ctied = {c for c in far if any(len({(int(r[far.index(c)]), int(r[len(far) + i])) for r in AF}) == 2 for i in range(3))}

    def T_of(cond):
        return {t for (r, t) in joint if cond(r)}

    def tied(p):
        return {X[i] for i in range(3) if len({(int(r[p]), t[i]) for (r, t) in joint}) == 2}
    ties = {p: tied(p) for p in hs.hpts}
    for p, a in itertools.combinations(hs.hpts, 2):
        if len({(int(r[p]), int(r[a])) for (r, t) in joint}) < 4:
            continue                                   # p and a tied: not a candidate pair
        for pv, av in itertools.product((0, 1), repeat=2):
            T = T_of(lambda r: int(r[p]) == pv and int(r[a]) == av)
            Tp = T_of(lambda r: int(r[p]) == pv)
            Ta = T_of(lambda r: int(r[a]) == av)
            for c in far:
                if c in ctied:
                    continue
                for g in (0, 1):
                    if T & TF[(c, g)] or not (Tp & TF[(c, g)]) or not (Ta & TF[(c, g)]):
                        continue
                    Excl = I - TF[(c, g)]
                    if not routed(joint, ties, X, I, T, Excl, [(p, pv), (a, av)]):
                        return True
    return False


def routed(joint, ties, X, I, T, Excl, cand):
    allowed_far = I - Excl
    for i in range(3):
        a = {t[i] for t in T}
        b = {t[i] for t in allowed_far}
        if len(a) == 1 and len(b) == 1 and a != b:
            return True
    for (r, rv) in cand:
        rel = {t for (row, t) in joint if int(row[r]) == rv}
        for i, j in itertools.permutations(range(3), 2):
            y, yp = X[i], X[j]
            for b, bp in itertools.product((0, 1), repeat=2):
                if not all(t[i] == b for t in T):
                    continue
                block = {t for t in I if t[i] == b and t[j] == bp}
                if not block or not block <= Excl:
                    continue
                if y in ties[r] and all(t[j] == bp for t in T):
                    return True
                if y not in ties[r] and yp not in ties[r] and not any(t[i] == b and t[j] == 1 - bp for t in rel):
                    return True
    return False
