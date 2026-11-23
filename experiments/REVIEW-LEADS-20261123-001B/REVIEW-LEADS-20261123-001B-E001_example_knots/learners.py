"""Learners of REVIEW-LEADS-20261123-001B-E001: features, L1 / L1+ (parity example knots), L2 (not-all-equal), C1.

The memory is a set of two-valued distinctions, one per feature (`m_j`).  A rewarded training image adds ONE knot over
the memory distinctions of its odd features (the constant feature is always odd): the parity of those distinctions
equals the image's label (T = 1, L = 0).  A test image is answered only when the knots force its label, i.e. when its
own knot is determined in every allowed memory word; with no allowed word nothing is answered.

No learner here sees a test label: `fit` takes training pixels and labels, `answer` takes a pixel string only.
"""

import importlib.util
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SIDE = 8

# --- features -----------------------------------------------------------------------------------------------------
FAMILIES = (((2, 2),), ((1, 3), (3, 1)), ((2, 3), (3, 2)), ((3, 3),))
FAMILY_NAMES = ("F0", "F1", "F2", "F3")


def _family_sizes():
    return [sum((1 << (h * w)) - 1 for h, w in fam) for fam in FAMILIES]


FAMILY_SIZES = _family_sizes()                                   # 15, 14, 126, 511
FAMILY_OFFSETS = [1 + sum(FAMILY_SIZES[:k]) for k in range(4)]   # bit 0 is the constant
N_FEATURES = [1 + sum(FAMILY_SIZES[:k + 1]) for k in range(4)]   # 16, 30, 156, 667

_cache = {}


def window_parities(pixels, h, w):
    """Parity of the count of each non-blank h-by-w window pattern over every window that overlaps the image.

    The image is padded with (h-1, w-1) blank cells on each side, so a count never depends on where the drawing
    sits (for 2x2 this is the one-cell border and 9x9 = 81 windows of the pre-registration)."""
    ph, pw = h - 1, w - 1
    H, W = SIDE + 2 * ph, SIDE + 2 * pw
    grid = [[0] * W for _ in range(H)]
    for r in range(SIDE):
        for c in range(SIDE):
            grid[r + ph][c + pw] = int(pixels[SIDE * r + c])
    counts = [0] * (1 << (h * w))
    for r in range(H - h + 1):
        for c in range(W - w + 1):
            idx = 0
            for dr in range(h):
                row = grid[r + dr]
                for dc in range(w):
                    idx = (idx << 1) | row[c + dc]
            counts[idx] += 1
    return [counts[j] & 1 for j in range(1, 1 << (h * w))]


def family_bits(pixels, k):
    """Bits of family k only, placed at its offsets."""
    key = (pixels, k)
    if key not in _cache:
        bits, pos = 0, FAMILY_OFFSETS[k]
        for h, w in FAMILIES[k]:
            for parity in window_parities(pixels, h, w):
                if parity:
                    bits |= 1 << pos
                pos += 1
        _cache[key] = bits
    return _cache[key]


def feature_mask(pixels, level):
    """Constant plus families F0..F<level> as one integer."""
    mask = 1
    for k in range(level + 1):
        mask |= family_bits(pixels, k)
    return mask


def popcount(x):
    return x.bit_count()


# --- L1 / L1+ : parity example knots ----------------------------------------------------------------------------
class ParityLearner:
    """One memory distinction per feature of families F0..F<level>; one parity knot per rewarded example."""

    def __init__(self, level):
        self.level = level
        self.n = N_FEATURES[level]
        self.knots = []
        self._rebuild()

    def fit(self, pixels_list, labels):
        self.knots = [(feature_mask(px, self.level), int(lab)) for px, lab in zip(pixels_list, labels, strict=True)]
        self._rebuild()
        return self

    def _rebuild(self):
        self.basis = {}
        self.consistent = True
        self.n_new = self.n_implied = self.n_contradicting = 0
        for mask, sign in self.knots:
            m, s = mask, sign
            while m:
                h = m.bit_length() - 1
                if h in self.basis:
                    bm, bs = self.basis[h]
                    m ^= bm
                    s ^= bs
                else:
                    break
            if m == 0:
                if s:
                    self.consistent = False
                    self.n_contradicting += 1
                else:
                    self.n_implied += 1
            else:
                self.basis[m.bit_length() - 1] = (m, s)
                self.n_new += 1

    @property
    def rank(self):
        return len(self.basis)

    def answer_mask(self, mask):
        if not self.consistent:
            return None
        m, s = mask, 0
        while m:
            h = m.bit_length() - 1
            if h not in self.basis:
                return None
            bm, bs = self.basis[h]
            m ^= bm
            s ^= bs
        return s

    def answer(self, pixels):
        return self.answer_mask(feature_mask(pixels, self.level))

    # exchange / clearing of the kept knots
    def export_knots(self):
        return list(self.knots)

    def load_knots(self, knots):
        self.knots = list(knots)
        self._rebuild()

    def clear(self):
        self.load_knots([])


def knot_sizes(pixels_list, level):
    return [popcount(feature_mask(px, level)) for px in pixels_list]


def fit_plus(pixels_list, labels):
    """L1+: F0; while the knots allow no memory word, add the next family and rebuild.  Returns (learner or None, levels tried)."""
    tried = []
    for level in range(4):
        learner = ParityLearner(level).fit(pixels_list, labels)
        tried.append((FAMILY_NAMES[level], learner.consistent, learner.rank, learner.n))
        if learner.consistent:
            return learner, tried
    return None, tried


# --- second implementation of the forcing test (dense GF(2) rank, no basis dictionary) --------------------------
def _gf2_rank(M):
    M = M.copy()
    rows, cols = M.shape
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0:
            continue
        p = nz[0] + r
        if p != r:
            M[[r, p]] = M[[p, r]]
        sel = M[:, c].astype(bool)
        sel[r] = False
        M[sel] ^= M[r]
        r += 1
    return r


def _bits(mask, n):
    return np.array([(mask >> j) & 1 for j in range(n)], dtype=np.uint8)


def dense_forced(knots, n, masks):
    """For each feature mask: forced label (0/1) or None, by testing whether adding (f, y) keeps the system solvable."""
    if not knots:
        return {mk: None for mk in masks}
    A = np.array([_bits(m, n) for m, _ in knots], dtype=np.uint8)
    s = np.array([sg for _, sg in knots], dtype=np.uint8).reshape(-1, 1)
    Aug = np.hstack([A, s])
    if _gf2_rank(A) != _gf2_rank(Aug):
        return {mk: None for mk in masks}                              # no allowed word
    out = {}
    for mk in masks:
        f = _bits(mk, n).reshape(1, -1)
        ok = []
        for y in (0, 1):
            A2 = np.vstack([A, f])
            Aug2 = np.hstack([A2, np.vstack([s, np.array([[y]], dtype=np.uint8)])])
            ok.append(_gf2_rank(A2) == _gf2_rank(Aug2))
        out[mk] = None if all(ok) else (0 if ok[0] else 1)
    return out


# --- enumeration of the 65,536 memory words of F0 (checks L1 at F0 and runs L2) ----------------------------------
_WORDS = np.arange(1 << 16, dtype=np.uint32)
_PAR = np.zeros(1 << 16, dtype=np.uint8)
for _b in range(16):
    _PAR ^= ((_WORDS >> _b) & 1).astype(np.uint8)


def enum_allowed_parity(knots):
    allowed = np.ones(1 << 16, dtype=bool)
    for mask, sign in knots:
        allowed &= _PAR[_WORDS & mask] == sign
    return allowed


def enum_forced_parity(knots, masks):
    allowed = enum_allowed_parity(knots)
    ws = _WORDS[allowed]
    out = {}
    for mk in masks:
        if ws.size == 0:
            out[mk] = None
            continue
        v = _PAR[ws & mk]
        out[mk] = int(v[0]) if (v == v[0]).all() else None
    return out, int(allowed.sum())


class NaeLearner:
    """L2: the knot of an example is not-all-equal over its odd memory distinctions and its label value, by enumeration."""

    def fit(self, pixels_list, labels):
        allowed = np.ones(1 << 16, dtype=bool)
        for px, lab in zip(pixels_list, labels, strict=True):
            f = np.uint32(feature_mask(px, 0))
            all_equal = (_WORDS & f) == (f if lab else np.uint32(0))        # every odd distinction equals the label
            allowed &= ~all_equal
        self.words = _WORDS[allowed]
        return self

    @property
    def n_allowed(self):
        return int(self.words.size)

    def answer(self, pixels):
        if self.words.size == 0:
            return None
        f = np.uint32(feature_mask(pixels, 0))
        sub = self.words & f
        all_one = bool((sub == f).all())          # every allowed word has all of them 1: label 1 would be all-equal -> impossible
        all_zero = bool((sub == 0).all())
        if all_one and not all_zero:
            return 0
        if all_zero and not all_one:
            return 1
        return None


# --- comparator C1: the recorded count reader of PIXEL-LETTERS-20261122-001 (integer implementation) -----------------
C1_SOURCE = ROOT / "experiments/PIXEL-LETTERS-20261122-001/PIXEL-LETTERS-20261122-001-E001_letters/conventional.py"


def _load_c1():
    spec = importlib.util.spec_from_file_location("pixel_letters_conventional", C1_SOURCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CountReader:
    """IntegerMeans trained by the same emitted-guess-and-correctness protocol as the first letter study."""

    def __init__(self):
        self.mod = _load_c1()
        self.model = self.mod.IntegerMeans()

    @staticmethod
    def bits(pixels):
        return [int(ch) for ch in pixels]

    def fit(self, pixels_list, labels):
        for px, lab in zip(pixels_list, labels, strict=True):
            b = self.bits(px)
            guess = self.model.predict(b)
            self.model.learn(b, guess, guess == int(lab))
        return self

    def costs(self, pixels):
        h = self.mod.histogram(self.bits(pixels))
        out = []
        for row in self.model.totals:
            count = sum(row) // 81
            out.append(sum((x - Fraction(y, count)) ** 2 for x, y in zip(h, row)) if count else None)
        return out

    def decide(self, pixels):
        return self.model.predict(self.bits(pixels))

    def decide_with_margin(self, pixels):
        c0, c1 = self.costs(pixels)
        g = self.decide(pixels)
        assert g == (0 if c0 <= c1 else 1)
        return g, abs(c1 - c0)
