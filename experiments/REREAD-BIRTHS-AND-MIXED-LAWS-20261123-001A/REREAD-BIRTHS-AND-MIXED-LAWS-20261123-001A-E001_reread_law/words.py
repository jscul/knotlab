"""Exact enumeration of allowed words and of their extension by one round (test (a)).

A stage is a list of stars (the distinctions each knot holds).  Every assignment of the stage's distinctions is
enumerated as bit planes: 64 assignments per machine word, the first six distinctions inside the word, the others
across words.  A knot of parity law allows an assignment when its values have even parity; of not-all-equal law
when they are not all equal.  Parity: even parity at every knot, as in the recorded counting code.
"""
import numpy as np

ALL = np.uint64(0xFFFFFFFFFFFFFFFF)
ZERO = np.uint64(0)
INNER = [np.uint64(p) for p in (0xAAAAAAAAAAAAAAAA, 0xCCCCCCCCCCCCCCCC, 0xF0F0F0F0F0F0F0F0,
                                0xFF00FF00FF00FF00, 0xFFFF0000FFFF0000, 0xFFFFFFFF00000000)]


def planes_for(names):
    """Bit planes of every assignment of `names` (at most 6 + 26 of them)."""
    names = list(names)
    inner, outer = names[:6], names[6:]
    words = 1 << len(outer)
    idx = np.arange(words, dtype=np.uint64)
    lanes = 1 << len(inner)
    valid = ALL if lanes == 64 else np.uint64((1 << lanes) - 1)
    planes = {}
    for j, v in enumerate(inner):
        planes[v] = np.full(words, INNER[j] & valid, dtype=np.uint64)
    for j, v in enumerate(outer):
        planes[v] = np.where((idx >> np.uint64(j)) & np.uint64(1), valid, ZERO).astype(np.uint64)
    return planes, np.full(words, valid, dtype=np.uint64)


def law_plane(law, cols):
    if law == "parity":
        r = cols[0]
        for c in cols[1:]:
            r = r ^ c
        return ~r
    o = cols[0]
    n = cols[0]
    for c in cols[1:]:
        o = o | c
        n = n & c
    return o & ~n


def popcount(a):
    return int(np.unpackbits(a.view(np.uint8)).sum())


def allowed(stars, law, planes, valid):
    ok = valid.copy()
    for s in stars:
        ok &= law_plane(law, [planes[d] for d in s])
    return ok


class Stage:
    """The allowed words of one stage, enumerated once; `extends` checks one round of births against them."""

    def __init__(self, stars, law):
        self.law = law
        self.names = sorted({d for s in stars for d in s})
        self.planes, self.valid = planes_for(self.names)
        self.ok = allowed(stars, law, self.planes, self.valid)
        self.n_ok = popcount(self.ok)

    def extends(self, births):
        """births: [(taken old distinctions, number of fresh)].  Returns (words that fail to extend, failing births)."""
        every = self.ok.copy()
        failing = 0
        zero = np.zeros_like(self.valid)
        for taken, f in births:
            cols_old = [self.planes[d] for d in taken]
            reach = zero.copy()
            for a in range(1 << f):
                cols = cols_old + [self.valid if (a >> j) & 1 else zero for j in range(f)]
                reach |= law_plane(self.law, cols) & self.valid
            if (self.ok & ~reach).any():
                failing += 1
            every &= reach
        return self.n_ok - popcount(every), failing


def extension_check(old_stars, births, law):
    """old_stars: the stage; births: list of (taken old distinctions, number of fresh distinctions).
    Returns (allowed old words, words that fail to extend, per-birth failing counts)."""
    names = sorted({d for s in old_stars for d in s})
    planes, valid = planes_for(names)
    ok = allowed(old_stars, law, planes, valid)
    n_ok = popcount(ok)
    every = ok.copy()
    per_birth = []
    for taken, f in births:
        cols_old = [planes[d] for d in taken]
        reach = np.zeros_like(ok)
        for a in range(1 << f):
            cols = cols_old + [valid if (a >> j) & 1 else np.zeros_like(valid) for j in range(f)]
            reach |= law_plane(law, cols) & valid
        bad = ok & ~reach
        per_birth.append(popcount(bad))
        every &= reach
    return n_ok, n_ok - popcount(every), per_birth


def projection_check(old_stars, new_stars, law):
    """Full enumeration of the next stage: is the set of its allowed words, forgotten onto the old distinctions,
    exactly the set of allowed old words?  Returns (allowed old, allowed new, old words reached)."""
    old_names = sorted({d for s in old_stars for d in s})
    new_names = old_names + sorted({d for s in new_stars for d in s} - set(old_names))
    planes, valid = planes_for(new_names)
    ok_new = allowed(old_stars + new_stars, law, planes, valid)
    ok_old_in_new = allowed(old_stars, law, planes, valid)
    # assignments of the new names, grouped by the old values: old names come first in new_names, so the old values
    # are the low bits of the assignment index.  Reached old words: old assignments with some allowed extension.
    m_old = len(old_names)
    total = len(new_names)
    bits = np.unpackbits(ok_new.view(np.uint8), bitorder="little").astype(bool)
    index = np.nonzero(bits)[0]
    # assignment index within word w and lane l: inner names are lanes, outer names are word bits.
    w, lane = index // 64, index % 64
    n_inner = min(6, total)
    assign = lane.astype(np.int64) | (w.astype(np.int64) << n_inner)
    reached = np.unique(assign & ((1 << m_old) - 1))
    bits_old = np.unpackbits(ok_old_in_new.view(np.uint8), bitorder="little").astype(bool)
    idx_old = np.nonzero(bits_old)[0]
    a_old = (idx_old % 64).astype(np.int64) | ((idx_old // 64).astype(np.int64) << n_inner)
    allowed_old = np.unique(a_old & ((1 << m_old) - 1))
    return len(allowed_old), int(len(index)), len(reached), bool(np.array_equal(allowed_old, reached))
