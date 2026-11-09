"""The doubling network's reach (GROW-HORIZON-20261109-001A), on SEPARATE-20261108-001A's net_lib.

The square tube of rule-60 rings with law (12, 12) contacts, as in GROW-CHOOSE-20261109-001A-E001's choose_lib, with row and column labels
that are positions in the original lattice's units (fractions): a doubling puts a band at every cut with the fresh split, a new row
between consecutive rows r and r' at (r + r')/2 (the last at (r + first + m)/2), likewise for columns. Every cell holds the set, as a bit
mask, of the original rings' own first-row cells its value depends on (born cells hold none; the dynamics is linear, so this is the
original-row part of the whole-history dependence). A contact needs ring X when that set meets X's own cells."""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import net_lib as N  # noqa: E402

LAW = (12, 12)


class Net:
    def __init__(self, cols, rows, g, period):
        self.cols, self.rows, self.g, self.period = list(cols), list(rows), g, period
        rings = [(i, r) for r in self.rows for i in self.cols]
        idx = {R: k for k, R in enumerate(rings)}
        nr = {r: self.rows[(k + 1) % len(self.rows)] for k, r in enumerate(self.rows)}
        nc = {i: self.cols[(k + 1) % len(self.cols)] for k, i in enumerate(self.cols)}
        names, contacts = [], []
        for r in self.rows:
            for i in self.cols:
                names.append(('h', i, r))
                contacts.append((idx[(i, r)], 0, idx[(nc[i], r)], 2 * g, LAW))
                names.append(('v', i, r))
                contacts.append((idx[(i, r)], g, idx[(i, nr[r])], 3 * g, LAW))
        sizes = tuple(4 * g for _ in rings)
        self.M, Nb, blocks = N.matrix(sizes, (60,) * len(rings), contacts)
        lay, _, _ = N.layout(sizes, contacts)
        keys = [None] * Nb
        for c, nm in enumerate(names):
            keys[c] = ('c',) + nm
        for k, R in enumerate(rings):
            for p, b in enumerate(lay[k]):
                if b >= len(contacts):
                    keys[b] = ('o', R, p)
        self.rings, self.contacts, self.keys, self.names = rings, contacts, keys, names
        self.ncon = len(contacts)


def position(net, c):
    """a contact's position: the midpoint of its two rings, in original units (the second ring lifted next to the first)"""
    kind, i, r = net.names[c]
    n, m = net.period
    if kind == 'h':
        j = net.cols.index(i)
        i2 = net.cols[(j + 1) % len(net.cols)] + (n if j + 1 == len(net.cols) else 0)
        return ((i + i2) / 2, r)
    j = net.rows.index(r)
    r2 = net.rows[(j + 1) % len(net.rows)] + (m if j + 1 == len(net.rows) else 0)
    return (i, (r + r2) / 2)


def taxicab(p, q, period):
    n, m = period
    dx = abs(p[0] - q[0]) % n
    dy = abs(p[1] - q[1]) % m
    return min(dx, n - dx) + min(dy, m - dy)


class Run:
    def __init__(self, n, m, g):
        self.net = Net([Fraction(i) for i in range(n)], [Fraction(r) for r in range(m)], g, (n, m))
        self.t = 0
        self.ringbits = {}
        state, v = [], 0
        for k in self.net.keys:
            if k[0] == 'o':
                state.append(1 << v)
                self.ringbits[k[1]] = self.ringbits.get(k[1], 0) | (1 << v)
                v += 1
            else:
                state.append(0)
        self.state = state
        self.origin = {R: R for R in self.net.rings}

    def step(self):
        s, new = self.state, []
        for row in self.net.M:
            v, x = 0, row
            while x:
                low = x & -x
                v ^= s[low.bit_length() - 1]
                x ^= low
            new.append(v)
        self.state = new
        self.t += 1

    def double(self):
        old = self.net
        val = {k: self.state[b] for b, k in enumerate(old.keys)}
        n, m = old.period

        def mids(labels, period):
            out = []
            for j, a in enumerate(labels):
                b = labels[(j + 1) % len(labels)] + (period if j + 1 == len(labels) else 0)
                out.append(a)
                mid = (a + b) / 2
                out.append(mid - period if mid >= period else mid)
            return sorted(out)
        new = Net(mids(old.cols, n), mids(old.rows, m), old.g, old.period)
        # own cells keep their values; every contact and every new ring's cell is born (holding no original cell)
        self.state = [val[k] if (k[0] == 'o' and k in val) else 0 for k in new.keys]
        self.net = new

    def reach(self, X):
        """(the largest taxicab distance from X to a contact needing X, the number of such contacts)"""
        mask = self.ringbits[X]
        best, count = None, 0
        for c in range(self.net.ncon):
            if self.state[c] & mask:
                d = taxicab(position(self.net, c), X, self.net.period)
                best = d if best is None or d > best else best
                count += 1
        return best, count

    def own_cells_hearing_others(self):
        """own cells whose value depends on another ring's original cells"""
        bad = 0
        for b, k in enumerate(self.net.keys):
            if k[0] == 'o':
                R = k[1]
                own = self.ringbits.get(R, 0)
                if self.state[b] & ~own:
                    bad += 1
        return bad


def heard(run, X):
    """the original rings, other than X, one of whose own cells depends now on X's own first-row cells"""
    mask = run.ringbits[X]
    out = set()
    for b, k in enumerate(run.net.keys):
        if k[0] == 'o' and k[1] in run.ringbits and k[1] != X and run.state[b] & mask:
            out.add(k[1])
    return out
