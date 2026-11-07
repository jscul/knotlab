"""A pendant point in a local configuration, for PENDANT-LINE-20261106-001B.

The pendant point b sits on one new not-all-equal line (b, s + sig_s, u + sig_u) through two local points s, u (on the gluing line, as
literals, or near classes). It is an extra near class of the local engine of ticket A: a value of b is compatible with a slot unless the
slot's literals of s and u both equal it.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PENDANT-LINE-20261106-001A/PENDANT-LINE-20261106-001A-P001_creation_is_decided_at_the_gluing_line"))
import local_lib as LL  # noqa: E402


class PendLocal(LL.Local):
    """ticket A's local configuration with one more near class b (point 3 + k), on the line NAE(b, s + sig[0], u + sig[1])"""

    def __init__(self, k, farrel, mfar, s, u, sig):
        super().__init__(k, farrel, mfar)
        self.b = 3 + k
        self.su = (s, u, sig)
        self.npts = 3 + k + 1 + mfar
        self.N = list(range(3, 3 + k)) + [self.b]
        self.C = list(range(3 + k + 1, 3 + k + 1 + mfar))

    def kind(self, p):
        return "Y" if p < 3 else ("N" if p <= self.b else "C")

    def mask(self, pts, vals):
        s, u, sig = self.su
        m = 0
        for i in range(6):
            if any(p < 3 and LL.PY[i][p] != v for p, v in zip(pts, vals)):
                continue
            fp = [(p - self.b - 1, v) for p, v in zip(pts, vals) if p > self.b]
            if fp and not any(all(f[j] == v for j, v in fp) for ii, f in self.far if ii == i):
                continue
            for t in range(self.T):
                if not all(((t >> (p - 3)) & 1) == v for p, v in zip(pts, vals) if 3 <= p < self.b):
                    continue
                bv = [v for p, v in zip(pts, vals) if p == self.b]
                if bv:
                    ls = (LL.PY[i][s] if s < 3 else (t >> (s - 3)) & 1) ^ sig[0]
                    lu = (LL.PY[i][u] if u < 3 else (t >> (u - 3)) & 1) ^ sig[1]
                    if ls == lu == bv[0]:
                        continue
                m |= 1 << (i * self.T + t)
        return np.uint64(m)


def implication(L, rel):
    """for each relation: (non-degenerate, every crossing knot off b reached, some crossing knot through b not reached)"""
    A = L.analyse(rel)
    ok = A["ok"]
    R = L.two_rounds(A)
    off = np.ones(len(rel), dtype=bool)
    thr = np.zeros(len(rel), dtype=bool)
    through = 0
    for tri in A["knot"]:
        if not A["cross"][tri]:
            continue
        kk = A["knot"][tri]
        if L.b in tri:
            thr |= kk & ~R[tri]
            through += int((ok & kk).sum())
        else:
            off &= ~kk | R[tri]
    return ok, off, thr, through
