"""Exact refactoring of BD.run_family's start, middle, and closing maps.

All node values remain pairs of frozensets.  Compiled finite-map images only
memoize the set comprehensions in advance; no state quotient is taken.
"""

import importlib.util
import itertools
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BD_PATH = ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py"
RECORD_PATH = ROOT / "artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/runs_merged.jsonl"
_spec = importlib.util.spec_from_file_location("proved_rate_bd", BD_PATH)
BD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BD)
INF = BD.INF
SMAX = BD.SMAX


def frozen_defs(defs):
    return tuple((k, l, tuple((c, tuple(a)) for c, a in calls)) for k, l, calls in defs)


class FamilyDP:
    def __init__(self, defs):
        self.defs = defs
        _, _, Gd = BD.L.depth_sequence(defs, BD.L.TOP)
        G = [Gd[0]]
        self.okM, self.rayM, self.V, self.port, self.out = BD.tables(defs, G, last=False)
        self.okE, _, _, self.portE, _ = BD.tables(defs, G, last=True)
        loc = list(range(3, self.V))
        l = self.V - 3
        self.subsets_mid = [list(c) for n in range(l + 1) for c in itertools.combinations(loc, n)]
        self.subsets_first = [list(c) for n in range(1, self.V + 1)
                              for c in itertools.combinations(range(self.V), n)
                              if any(x < 3 for x in c)]
        self.subsets_last = [list(c) for n in range(1, l + 1) for c in itertools.combinations(loc, n)]
        self.cacheM, self.cacheE = {}, {}
        self.compiled = {}
        self.sets_by_bits = {0: frozenset()}
        self._start = None

    def trans(self, ok, W, alpha_bits, last, forget=None):
        # This is BD.run_family.trans, with closure variables made explicit.
        sel = ok.copy()
        a = np.arange(2 ** self.V)
        for i, w in enumerate(W):
            if forget is not None and i == forget:
                continue
            sel &= ((a >> w) & 1) == ((alpha_bits >> i) & 1)
        T = [0] * 8
        for sg in range(8):
            m = sel & (self.port == sg)
            if last:
                T[sg] = 1 if m.any() else 0
            else:
                T[sg] = int(np.bitwise_or.reduce(1 << self.out[m])) if m.any() else 0
        return T

    @staticmethod
    def step(R, T):
        r = 0
        for sg in range(8):
            if (R >> sg) & 1:
                r |= T[sg]
        return r

    def tabs(self, W, last):
        key = tuple(W)
        cache = self.cacheE if last else self.cacheM
        if key not in cache:
            ok = self.okE if last else self.okM
            full = [self.trans(ok, W, a, last) for a in range(2 ** len(W))]
            forg = [[self.trans(ok, W, a, last, forget=i)
                     for a in range(2 ** len(W))] for i in range(len(W))]
            cache[key] = (full, forg)
        return cache[key]

    def advance_literal(self, F, Gf, W, last):
        """Verbatim advance set comprehensions from BD, for validation."""
        full, forg = self.tabs(W, last)
        nF = frozenset(self.step(R, T) for R in F for T in full)
        nG = set(self.step(R, T) for R in Gf for T in full)
        for i in range(len(W)):
            for R in F:
                for T in forg[i]:
                    nG.add(self.step(R, T))
        return nF, frozenset(nG)

    def compile_tabs(self, W, last):
        key = (tuple(W), last)
        if key not in self.compiled:
            full, forg = self.tabs(W, last)
            # Each integer bitset represents precisely a finite set of output
            # masks.  Union therefore evaluates the advance comprehensions.
            ft = tuple(set(tuple(T) for T in full))
            gt = tuple(set(tuple(T) for ts in forg for T in ts))
            fbits = tuple(sum(1 << x for x in {self.step(R, T) for T in ft}) for R in range(256))
            gbits = tuple(sum(1 << x for x in {self.step(R, T) for T in gt}) for R in range(256))
            self.compiled[key] = (fbits, gbits, {}, {})
        return self.compiled[key]

    @staticmethod
    def image(S, table, cache):
        v = cache.get(S)
        if v is None:
            v = 0
            for R in S:
                v |= table[R]
            cache[S] = v
        return v

    def as_frozenset(self, bits):
        out = self.sets_by_bits.get(bits)
        if out is None:
            rest = bits
            values = []
            while rest:
                low = rest & -rest
                values.append(low.bit_length() - 1)
                rest -= low
            out = frozenset(values)
            self.sets_by_bits[bits] = out
        return out

    def advance(self, F, Gf, W, last):
        fbits, gbits, fc, gc = self.compile_tabs(W, last)
        nF = self.image(F, fbits, fc)
        nG = self.image(Gf, fbits, fc) | self.image(F, gbits, gc)
        return self.as_frozenset(nF), self.as_frozenset(nG)

    def start_nodes(self):
        if self._start is None:
            START = (frozenset([255]), frozenset())
            layer = {}
            for W in self.subsets_first:
                st = self.advance(*START, W, last=False)
                if st not in layer or layer[st] > len(W):
                    layer[st] = len(W)
            self._start = layer
        return dict(self._start)

    def middle(self, node):
        return [(W, self.advance(*node, W, last=False), len(W)) for W in self.subsets_mid]

    def close(self, node):
        best = INF
        for W in self.subsets_last:
            F, Gf = self.advance(*node, W, last=True)
            if 0 in F and 0 not in Gf and len(W) < best:
                best = len(W)
        return best


@lru_cache(maxsize=1)
def _context(key):
    return FamilyDP(key)


def start_nodes(defs):
    return _context(frozen_defs(defs)).start_nodes()


def middle(defs, node):
    return _context(frozen_defs(defs)).middle(node)


def close(defs, node):
    return _context(frozen_defs(defs)).close(node)
