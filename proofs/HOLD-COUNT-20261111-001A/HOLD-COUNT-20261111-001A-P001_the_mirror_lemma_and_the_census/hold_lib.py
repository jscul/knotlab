"""What it takes to hold a count (research/HOLD-COUNT-20261111-001/preregistration.md, ticket A).

The spaces are PARITY-NEEDS-20261111-001's (needs_lib): every simple lattice torus up to 20 points and the random knot spaces of n = 8,
10, 12, 14 points steered to genus 1, 2, 3 (seeds 0 to 99), every class, all floor states enumerated by brute force (unate_lib).

A reading: three held points T = (a, b, c), optionally one reference point r held at 0, and output points read at the floor. It is
total when every one of T's 8 patterns occurs among the floor states (with r = 0 when there is a reference), and a point is decided when
its value is the same in every such floor state with the same pattern; its table is then 8 bits, bit k at pattern k = 4a + 2b + c.
A pair of decided points (o1, o2) holds the count mod m when, for some choice of literals (eps, 3 bits), the pair's value at pattern k
is a function of popcount(k ^ eps) mod m that takes different values on different residues. A single decided point holds the count
mod 2 when its table is parity or its negation."""
import itertools
import signal
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PARITY-NEEDS-20261111-001A/PARITY-NEEDS-20261111-001A-P001_the_parity_gadget_refereed"))
import needs_lib as N  # noqa: E402

U, SL = N.U, N.SL
SPACE_CAP = 300
PATTERNS = np.arange(8)
PARITY = sum(((bin(k).count("1") & 1) << k) for k in range(8))
MASK8 = 255


def _holds_table(m):
    """H[t1, t2]: the pair with tables t1, t2 holds the count of three literals mod m, for some eps"""
    H = np.zeros((256, 256), dtype=bool)
    for eps in range(8):
        res = [bin(k ^ eps).count("1") % m for k in range(8)]
        for t1 in range(256):
            for t2 in range(256):
                code = [((t1 >> k) & 1) * 2 + ((t2 >> k) & 1) for k in range(8)]
                ok = all((res[k] == res[j]) == (code[k] == code[j]) for k in range(8) for j in range(k))
                H[t1, t2] |= ok
    return H


HOLD = {}


def holds(m):
    if m not in HOLD:
        HOLD[m] = _holds_table(m)
    return HOLD[m]


def is_parity(t):
    return t == PARITY or t == (PARITY ^ MASK8)


def majorities():
    out = set()
    for eps in range(8):
        out.add(sum((int(bin(k ^ eps).count("1") >= 2) << k) for k in range(8)))
    return out


MAJ = majorities()


def decided_tables(rows, T):
    """for floor states `rows` (uint8, states x points) and held triple T: None if not total, else {point: table} of decided points"""
    if len(rows) == 0:
        return None
    key = rows[:, T[0]].astype(np.int64) * 4 + rows[:, T[1]] * 2 + rows[:, T[2]]
    order = np.argsort(key, kind="stable")
    ks = key[order]
    starts = np.searchsorted(ks, PATTERNS)
    if len(np.unique(ks)) < 8:
        return None
    R = rows[order]
    lo = np.minimum.reduceat(R, starts, axis=0)
    hi = np.maximum.reduceat(R, starts, axis=0)
    dec = np.all(lo == hi, axis=0)
    tab = (lo.astype(np.int64) << PATTERNS[:, None]).sum(axis=0)
    return {int(o): int(tab[o]) for o in np.nonzero(dec)[0] if o not in T}


def read_class(rows, n, tally, first, where):
    """tally every reading of this class's floor states; `first` keeps the first instance of each kind"""
    H3, H4 = holds(3), holds(4)

    def note(kind, inst):
        tally[kind] += 1
        first.setdefault(kind, dict(where, **inst))

    def pairs(tabs, H):
        pts = sorted(tabs)
        for i, o1 in enumerate(pts):
            for o2 in pts[i + 1:]:
                if H[tabs[o1], tabs[o2]] or H[tabs[o2], tabs[o1]]:
                    return (o1, o2)
        return None

    for T in itertools.combinations(range(n), 3):
        tabs = decided_tables(rows, T)
        if tabs is None:
            continue
        par = [o for o, t in tabs.items() if is_parity(t)]
        maj = [o for o, t in tabs.items() if t in MAJ]
        tally["total parity interfaces (control)"] += len(par)
        tally["total majority interfaces (control)"] += len(maj)
        if par:
            note("parity, no reference", {"held": T, "out": par[0]})
        if maj:
            note("majority, no reference", {"held": T, "out": maj[0]})
        if par and maj:
            note("full adder, no reference", {"held": T, "out": (par[0], maj[0])})
        p3 = pairs(tabs, H3)
        if p3:
            note("mod 3, no reference", {"held": T, "out": p3})
        p4 = pairs(tabs, H4)
        if p4:
            note("mod 4, no reference", {"held": T, "out": p4})
    for r in range(n):
        sub = rows[rows[:, r] == 0]
        if len(sub) == 0:
            continue
        for T in itertools.combinations([p for p in range(n) if p != r], 3):
            tabs = decided_tables(sub, T)
            if tabs is None:
                continue
            tabs.pop(r, None)
            if any(is_parity(t) for t in tabs.values()):
                note("parity, one reference", {"held": T, "reference": r})
            p3 = pairs(tabs, H3)
            if p3:
                note("mod 3, one reference", {"held": T, "reference": r, "out": p3})
            p4 = pairs(tabs, H4)
            if p4:
                note("mod 4, one reference", {"held": T, "reference": r, "out": p4})


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def read_space(K, cap=SPACE_CAP):
    """(tally, first instances, floor-state counts per class) over every class, or None if over the cap"""
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    try:
        tally, first, sizes = Counter(), {}, []
        for ci, s in enumerate(U.all_classes(K)):
            rows = U.floor_states(K, s)
            sizes.append(int(len(rows)))
            read_class(rows, K.n, tally, first, {"class index": ci, "floor states": int(len(rows))})
        signal.alarm(0)
        return tally, first, sizes
    except Timeout:
        return None


def export(K, label):
    """the space as plain data for referee.py: lines (three points each) and every class's signing (3 signs per line)"""
    return {"label": label, "n": K.n, "lines": [list(map(int, p)) for p in K.pt],
            "classes": [list(map(int, s)) for s in U.all_classes(K)]}
