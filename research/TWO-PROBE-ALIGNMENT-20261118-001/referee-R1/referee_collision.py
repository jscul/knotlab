"""Referee R1 for TWO-PROBE-ALIGNMENT-20261118-001: the hand collision, from scratch (no study or predecessor code imported).

  ../../../.venv/bin/python -B referee_collision.py > referee_collision.json      (from this directory)

The eight originals are the points of {0,1}^3 (distinction k = the point with bits of k); the allowed rows are the two constants and
the three coordinate cuts with their complements.  The root junction on r = 000 adds fresh u, v with r xor u xor v = 0.  A test on
permanent a, b adds fresh p, q with B(p, a, q) and B(p, b, q): opposed ends allow every row; equal ends need a = b = that value.
Bond distance: the least size of a minimal non-free projection containing both, minus one (infinite if none).  The table's
automorphisms are found by refinement and backtracking (the referee's own).
"""
import itertools
import json
import math
import sys

import numpy as np


def originals():
    rows = {0, 255}
    for c in range(3):
        cut = sum(1 << k for k in range(8) if (k >> c) & 1)
        rows |= {cut, 255 ^ cut}
    return rows


def root(rows, r=0, width=8):
    """r xor u xor v = 0 with u = width, v = width + 1."""
    out = set()
    for row in rows:
        for u in (0, 1):
            v = ((row >> r) & 1) ^ u
            out.add(row | (u << width) | (v << (width + 1)))
    return out


def test(rows, a, b, width):
    out = set()
    for row in rows:
        for left, right in itertools.product((0, 1), repeat=2):
            if left != right or (((row >> a) & 1) == ((row >> b) & 1) == left):
                out.add(row | (left << width) | (right << (width + 1)))
    return out


def bond_table(rows, n):
    st = np.array(sorted(rows), dtype=np.int64)
    free = np.zeros(1 << n, dtype=bool)
    for m in range(1 << n):
        code = np.zeros(len(st), dtype=np.int64)
        k = 0
        for v in range(n):
            if (m >> v) & 1:
                code |= ((st >> v) & 1) << k
                k += 1
        free[m] = len(np.unique(code)) == (1 << k)
    D = [[0 if i == j else math.inf for j in range(n)] for i in range(n)]
    for m in range(1, 1 << n):
        if free[m] or not all(free[m & ~(1 << i)] for i in range(n) if (m >> i) & 1):
            continue
        vs = [i for i in range(n) if (m >> i) & 1]
        for x, y in itertools.combinations(vs, 2):
            D[x][y] = D[y][x] = min(D[x][y], len(vs) - 1)
    return D


def automorphisms(D):
    """Every permutation of the distinctions preserving the whole table (backtracking with row signatures)."""
    n = len(D)
    sig = [tuple(sorted(D[i][j] for j in range(n) if j != i)) for i in range(n)]
    out = []

    def go(img):
        k = len(img)
        if k == n:
            out.append(tuple(img))
            return
        for t in range(n):
            if t in img or sig[t] != sig[k]:
                continue
            if all(D[k][j] == D[t][img[j]] for j in range(k)):
                go(img + [t])
    go([])
    return out


def case(name, first, second):
    rows = root(originals())
    rows = test(rows, *first, 10)
    rows = test(rows, *second, 12)
    n = 14
    D = bond_table(rows, n)
    aut = automorphisms(D)
    p2, q2 = 12, 13
    orbit = sorted({g[p2] for g in aut} | {g[q2] for g in aut})
    six = [k for k in range(8) if k not in second]
    sym = set(six) | {p2, q2}
    # every permutation of the second test's ends and the six originals it does not test, fixing everything else (8! = 40,320)
    fixed_ok = 0
    names = sorted(sym)
    for perm in itertools.permutations(names):
        g = list(range(n))
        for a, b in zip(names, perm):
            g[a] = b
        fixed_ok += all(D[i][j] == D[g[i]][g[j]] for i in range(n) for j in range(n))
    hist = {}
    for i, j in itertools.combinations(range(n), 2):
        hist[str(D[i][j])] = hist.get(str(D[i][j]), 0) + 1
    return {"case": name, "rows": len(rows), "distinctions": n, "automorphisms": len(aut),
            "images of the second test's ends": [("orig " + format(k, "03b")) if k < 8 else ("u", "v", "p1", "q1", "p2", "q2")[k - 8]
                                                 for k in orbit],
            "permutations of {p2, q2} and the six untouched originals preserving every entry (of 40,320)": fixed_ok,
            "distance histogram": hist}


if __name__ == "__main__":
    out = [case("tests (111, u) and (000, 111)", (7, 8), (0, 7)),
           case("comparison: tests (011, u) and (000, 011)", (3, 8), (0, 3))]
    print(json.dumps(out, indent=1))
