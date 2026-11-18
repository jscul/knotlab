"""Bond distance (freedom) against the correlation readings (FREE-READ-20261118-001B).

A bond is a set S of distinctions on which the allowed states, every other variable forgotten, form a knot: some joint value of S
never occurs (K1) and every set of |S| - 1 of them takes all joint values (K2). Bond distance is the size of the least bond holding
both distinctions, minus one (the glossary's definition, read from the allowed states alone)."""
import itertools
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/TREE-STEPS-20261118-001B/TREE-STEPS-20261118-001B-E001_trees"))
import treelib as T  # noqa: E402  (unchanged; brings cumlib)

L = T.L


class Supports:
    def __init__(self, states, n):
        a = np.array(states, dtype=np.int64)
        self.bits = np.stack([(a >> i) & 1 for i in range(n)], axis=1).astype(np.int64)
        self.n = n
        self._cache = {}

    def full(self, S):
        """Does the projection onto S take all 2^|S| joint values?"""
        S = tuple(sorted(S))
        v = self._cache.get(S)
        if v is None:
            codes = self.bits[:, list(S)] @ (1 << np.arange(len(S)))
            v = len(np.unique(codes)) == (1 << len(S))
            self._cache[S] = v
        return v

    def is_bond(self, S):
        return (not self.full(S)) and all(self.full(T_) for T_ in itertools.combinations(S, len(S) - 1))

    def bond_distance(self, x, y, smax):
        others = [z for z in range(self.n) if z not in (x, y)]
        for m in range(2, smax + 1):
            for extra in itertools.combinations(others, m - 2):
                if self.is_bond((x, y) + extra):
                    return m - 1
        return None
