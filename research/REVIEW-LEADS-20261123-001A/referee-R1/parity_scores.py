"""Maximize the four correlations with exact integer arithmetic."""
from fractions import Fraction
import math

import numpy as np

W = np.zeros((2, 8), dtype=np.int64)
F = np.zeros((2, 15, 8), dtype=np.int64)
for setting in (0, 1):
    for old in range(8):
        bits = ((old >> 2), (old >> 1) & 1, old & 1)
        for fresh in (0, 1):
            if bits[0] == bits[1 + setting] == fresh:
                continue
            W[setting, old] += 1
            for mask in range(1, 16):
                record = (old << 1) | fresh
                F[setting, mask-1, old] += (-1)**((record & mask).bit_count())


def check_hiding(matrix):
    for m in (matrix, matrix.T):
        z = (W @ m).tolist()
        if any(x * sum(z[1]) != y * sum(z[0]) for x, y in zip(*z)):
            return False
    return True


def exact_score(m):
    # The largest raw numerator is at most four times the number of old words.
    assert 4*sum(map(int, m.flat)) < 2**62
    totals = W @ m @ W.T
    den = math.lcm(*map(int, totals.flat))
    arithmetic = np.int64 if 4*den < 2**62 else object
    e = {}
    for a in (0, 1):
        for b in (0, 1):
            numerator = (F[a] @ m @ F[b].T).astype(arithmetic)
            e[a, b] = numerator * (den // int(totals[a, b]))
    best = 0
    for relative_sign in (-1, 1):
        # Alice fixes two masks. Bob can maximize the two absolute sums independently.
        u = np.abs(e[0, 0][:, None] + relative_sign * e[1, 0][None, :]).max(axis=2)
        v = np.abs(e[0, 1][:, None] - relative_sign * e[1, 1][None, :]).max(axis=2)
        best = max(best, int((u + v).max()))
    return Fraction(best, den)
