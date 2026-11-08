"""Knots across time (ticket TIME-KNOTS-20261107-001A).

A deterministic local dynamics written as its space-time law: one Boolean variable per cell and time step, the first row free and
every later cell equal to the update rule of the cells below it. Its allowed states are the trajectories. For an elementary
cellular automaton (rule number 0..255, Wolfram's numbering: new value of a cell = bit 4a + 2b + c of the rule, where a, b, c are
the left, own and right values), the value y of cell 0 after T steps is a function F_T of the 2T + 1 cells -T..T of the first row.

A set S of first-row cells is *decisive* when some setting of S fixes F_T (F_T is constant on every completion), and *minimally
decisive* when no proper subset of S is decisive. The theorem of the ticket: the knots (K1-K3) on S + {y} with S in the first row
are exactly the minimally decisive S with |S| >= 2; a decisive single cell gives a tie.

Truth tables are numpy arrays indexed by the integer whose bit j is cell j - T (cell -T is bit 0)."""
from __future__ import annotations

import itertools
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


# ---------------------------------------------------------------------- dynamics
def step_rows(rows, rule):
    """one step of an elementary automaton on an array of rows (shape: inputs x width); the width shrinks by 2"""
    a, b, c = rows[:, :-2], rows[:, 1:-1], rows[:, 2:]
    idx = (a.astype(np.uint8) << 2) | (b.astype(np.uint8) << 1) | c.astype(np.uint8)
    table = np.array([(rule >> k) & 1 for k in range(8)], dtype=np.uint8)
    return table[idx]


def t_step_map(rule, T):
    """F_T as a truth table over the 2T + 1 cells -T..T of the first row"""
    n = 2 * T + 1
    u = np.arange(1 << n, dtype=np.int64)
    rows = ((u[:, None] >> np.arange(n)[None, :]) & 1).astype(np.uint8)
    for _ in range(T):
        rows = step_rows(rows, rule)
    assert rows.shape[1] == 1
    return rows[:, 0].copy()


def life_map():
    """Conway's Life at T = 1: the centre's next value from its 3 x 3 block (bit j is cell j in row-major order, centre bit 4)"""
    u = np.arange(1 << 9, dtype=np.int64)
    bits = (u[:, None] >> np.arange(9)[None, :]) & 1
    centre = bits[:, 4]
    neighbours = bits.sum(axis=1) - centre
    return ((neighbours == 3) | ((centre == 1) & (neighbours == 2))).astype(np.uint8)


def life_map_T2():
    """Life at T = 2: the centre's value two steps on, from its 5 x 5 block (bit 5r + c)"""
    u = np.arange(1 << 25, dtype=np.int64)
    out = np.zeros(1 << 25, dtype=np.uint8)
    # the 3 x 3 block of values after one step, each from its own 3 x 3 window of the 5 x 5 block
    mid = []
    for r in range(3):
        for c in range(3):
            s = np.zeros(1 << 25, dtype=np.int64)
            for dr in range(3):
                for dc in range(3):
                    if dr == 1 and dc == 1:
                        continue
                    s += (u >> (5 * (r + dr) + (c + dc))) & 1
            centre = (u >> (5 * (r + 1) + (c + 1))) & 1
            mid.append(((s == 3) | ((centre == 1) & (s == 2))).astype(np.uint8))
    s = sum(mid[k].astype(np.int64) for k in range(9) if k != 4)
    out = ((s == 3) | ((mid[4] == 1) & (s == 2))).astype(np.uint8)
    return out


# ---------------------------------------------------------------------- decisive sets
def decisive_table(F, n):
    """for every subset S of the n inputs (bitmask), whether some setting of S makes F constant"""
    cube = F.reshape((2,) * n)            # axis k of the reshaped array is bit n - 1 - k of the index
    dec = np.zeros(1 << n, dtype=bool)
    for S in range(1 << n):
        axes = [n - 1 - j for j in range(n) if S >> j & 1]
        rest = [a for a in range(n) if a not in axes]
        A = np.transpose(cube, axes + rest).reshape(1 << len(axes), -1)
        dec[S] = bool(((A.min(axis=1) == A.max(axis=1))).any())
    return dec


def minimal_decisive(dec, n):
    """the minimally decisive sets: decisive, and no subset one smaller is decisive"""
    out = []
    for S in range(1 << n):
        if dec[S] and not any(dec[S & ~(1 << j)] for j in range(n) if S >> j & 1):
            out.append(S)
    return out


def knots_across_time(F, n):
    """(knots: minimally decisive sets of size >= 2, ties: decisive single cells, constant: F constant)"""
    if F.min() == F.max():
        return [], [], True
    dec = decisive_table(F, n)
    md = minimal_decisive(dec, n)
    return [S for S in md if bin(S).count("1") >= 2], [S for S in md if bin(S).count("1") == 1], False


def depends(F, n):
    """the inputs F depends on (bitmask)"""
    cube = F.reshape((2,) * n)
    m = 0
    for j in range(n):
        ax = n - 1 - j
        a0 = np.take(cube, 0, axis=ax)
        a1 = np.take(cube, 1, axis=ax)
        if (a0 != a1).any():
            m |= 1 << j
    return m


# ---------------------------------------------------------------------- symmetry of elementary rules
def reflect(rule):
    return sum(((rule >> (4 * a + 2 * b + c)) & 1) << (4 * c + 2 * b + a) for a in (0, 1) for b in (0, 1) for c in (0, 1))


def complement(rule):
    return sum((1 - ((rule >> (7 - k)) & 1)) << k for k in range(8))


def classes():
    """the 88 classes of elementary rules under reflection and complement, each by its least member"""
    seen, reps = set(), []
    for r in range(256):
        if r in seen:
            continue
        orbit = {r, reflect(r), complement(r), reflect(complement(r))}
        seen |= orbit
        reps.append(min(orbit))
    return sorted(reps)


# ---------------------------------------------------------------------- linear rules
def poly_power_support(p, T):
    """the support of p(X)^T over GF(2), p given by its coefficient set (offsets)"""
    cur = {0}
    for _ in range(T):
        nxt = {}
        for e in cur:
            for o in p:
                nxt[e + o] = nxt.get(e + o, 0) ^ 1
        cur = {e for e, v in nxt.items() if v}
    return cur


# ---------------------------------------------------------------------- the generic knot test, for cross-checks
def relation_of_map(F, n):
    """the graph of F as rows over n inputs and the output (bit n), for the generic K1-K3 enumerator"""
    return [u | (int(F[u]) << n) for u in range(1 << n)]
