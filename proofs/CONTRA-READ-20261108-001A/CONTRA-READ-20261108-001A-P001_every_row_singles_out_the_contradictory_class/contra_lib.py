"""Signed trisum glues, their switching classes and the rows of creation between glue lines (CONTRA-READ-20261108-001).

A class is read off as its parities on the fundamental cycles of a spanning tree of the glue's incidence graph; its representative signs
exactly the off-tree incidences of odd parity. Row a of a signing is creation in the signed glue with line a removed, at every other
line (SWITCH-PROOF-20261108-001A's signed_row, with far-side verdicts memoized by their masks). By SWITCH-PROOF's theorem applied to the
glue without line a, row a depends only on the signing's class there."""
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/SWITCH-PROOF-20261108-001A/SWITCH-PROOF-20261108-001A-P001_creation_between_glue_lines_sees_only_the_switching_class"))
import proof_lib as PL  # noqa: E402

TR = PL.TR
_MEMO = {}


def free(v):
    return None if v is None else (bool(v[0]), bool(v[2]), bool(v[3]))


def verdict(mm):
    if mm is None:
        return None
    k = (frozenset(mm[0]), frozenset(mm[1]))
    if k not in _MEMO:
        _MEMO[k] = free(TR.engine().TL.verdict_from_masks(*mm))
    return _MEMO[k]


class Glue:
    def __init__(self, seed, run):
        self.seed = seed
        self.lines = [tuple(l) for l in run["glue"]]
        self.minimal = [tuple(x) for x in run["minimal"]]
        self.g = len(self.lines)
        self.n = 1 + max(max(l) for l in self.lines)
        self.G = PL.SW.incidence_of_glue(self.lines)
        T = nx.minimum_spanning_tree(self.G)
        key = lambda e: tuple(sorted(e, key=str))  # noqa: E731
        self.off = sorted({key(e) for e in self.G.edges()} - {key(e) for e in T.edges()}, key=str)
        idx = {frozenset(e): k for k, e in enumerate(self.off)}
        self.fund = []
        for u, w in self.off:
            p = nx.shortest_path(T, u, w)
            self.fund.append({frozenset(e) for e in zip(p, p[1:])} | {frozenset((u, w))})

        def cyc_vec(cyc):
            v = 0
            for u, w in zip(cyc, cyc[1:] + cyc[:1]):
                k = idx.get(frozenset((u, w)))
                if k is not None:
                    v ^= 1 << k
            return v
        self.basis = []
        for a in range(self.g):
            Ga = self.G.copy()
            Ga.remove_node(("L", a))
            self.basis.append([cyc_vec(c) for c in nx.cycle_basis(Ga)])
        self.N = 1 << len(self.off)

    def signing(self, mask):
        return [([v for v in e if v[0] == "L"][0][1], [v for v in e if v[0] == "P"][0][1]) for k, e in enumerate(self.off) if mask >> k & 1]

    def mask_of(self, S):
        E = {frozenset((("L", i), ("P", p))) for i, p in S}
        return sum((len(E & C) & 1) << k for k, C in enumerate(self.fund))

    def restr(self, a, m):
        """the class of the signing on the glue without line a: its parities on a cycle basis of that glue"""
        return tuple(bin(m & v).count("1") & 1 for v in self.basis[a])

    def solutions(self, m, skip=None):
        TL = TR.engine().TL
        return TL.solutions(self.lines, PL.signs_of(self.lines, self.signing(m)), self.n, skip=skip)

    def row(self, a, m):
        """row a of the class m, and whether line a's three points are tied in the glue without a (two complementary patterns)"""
        signs = PL.signs_of(self.lines, self.signing(m))
        AN = self.solutions(m, skip=a)
        out = [verdict(TR.fast_masks(AN, list(self.lines[b]), signs[b], [q for q in range(self.n) if q not in self.lines[b]]))
               if len(AN) else None for b in range(self.g) if b != a]
        pats = {tuple(int(x) for x in r) for r in AN[:, list(self.lines[a])]} if len(AN) else set()
        return out, len(pats) == 2

    def partners(self, a):
        """the lines sharing two points with line a"""
        return [b for b in range(self.g) if b != a and len(set(self.lines[a]) & set(self.lines[b])) == 2]
