"""Affine chains of three rings (AFFINE-WIRE-20261108-001), on PROCESS-CHAIN-20261108-001A's layout.

A chain is rings A, B and C, each with its own elementary rule, ring B holding contact c1 at index 0 and contact c2 at index k. The
joint first row uses chain_lib.layout's bits (c1, c2, ring A's own cells, ring B's own cells, ring C's own cells). Each contact has
its own law:
- ("proposals",): the contact combines its two rings' proposals by XOR: f_X(left, c, right) + f_Y(left, c, right);
- ("self-blind", uX, uY): uX(left, right in its first ring) + uY(left, right in its second ring), u a two-input table (bit 2x + y,
  x the left neighbour).
For linear rules and linear laws the dynamics is s -> M s over GF(2); a row of M is kept as the bitmask of the cells that a cell's
next value reads. Affine rules and laws differ from linear ones by constants, which change no dependence or binding."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PROCESS-CHAIN-20261108-001A/PROCESS-CHAIN-20261108-001A-P001_what_a_chain_of_contacts_can_carry"))
import chain_lib as C  # noqa: E402

S, P = C.S, C.P
LIN = {0: (0, 0, 0), 204: (0, 1, 0), 240: (1, 0, 0), 170: (0, 0, 1), 60: (1, 1, 0), 102: (0, 1, 1), 90: (1, 0, 1), 150: (1, 1, 1)}
ULIN = {0b1100: (1, 0), 0b1010: (0, 1), 0b0110: (1, 1)}               # u(x, y) = x, y, x + y as tables (bit 2x + y)


def rings_of(mA, mB, mC, k):
    """the three rings as lists of bit positions (index 0 of ring A and ring B is c1, index k of ring B and index 0 of ring C is c2)"""
    a, b, c, N, blocks = C.layout(mA, mB, mC, k)
    RA = [0] + a
    RB = [0 if j == 0 else (1 if j == k else b[j]) for j in range(mB)]
    RC = [1] + c
    return RA, RB, RC, N, blocks


def linear_matrix(rules, sizes, k, law1, law2):
    """rows of M as bitmasks, for linear rules (keys of LIN) and linear laws"""
    rA, rB, rC = rules
    mA, mB, mC = sizes
    RA, RB, RC, N, blocks = rings_of(mA, mB, mC, k)
    rows = [0] * N
    def ring_rows(R, rule):
        l, s, r = LIN[rule]
        for i in range(1, len(R)):
            if R[i] in (0, 1):
                continue
            rows[R[i]] = (l << R[i - 1]) ^ (s << R[i]) ^ (r << R[(i + 1) % len(R)])
    ring_rows(RA, rA)
    for j in range(1, mB):
        if j == k:
            continue
        l, s, r = LIN[rB]
        rows[RB[j]] = (l << RB[j - 1]) ^ (s << RB[j]) ^ (r << RB[(j + 1) % mB])
    ring_rows(RC, rC)
    def contact(law, X, iX, ruleX, Y, iY, ruleY, pos):
        left = lambda R, i: R[(i - 1) % len(R)]
        right = lambda R, i: R[(i + 1) % len(R)]
        if law[0] == "proposals":
            v = 0
            for R, i, rule in ((X, iX, ruleX), (Y, iY, ruleY)):
                l, s, r = LIN[rule]
                v ^= (l << left(R, i)) ^ (s << pos) ^ (r << right(R, i))
            return v
        _, uX, uY = law
        v = 0
        for R, i, u in ((X, iX, uX), (Y, iY, uY)):
            x, y = ULIN[u]
            v ^= (x << left(R, i)) ^ (y << right(R, i))
        return v
    rows[0] = contact(law1, RA, 0, rA, RB, 0, rB, 0)
    rows[1] = contact(law2, RB, k, rB, RC, 0, rC, 1)
    return rows, N, blocks


def row_orbit(rows, start):
    """the row vectors r_T = e M^T for T = 1, 2, ... up to the first repeat: (list r_1..r_{T2-1}, T1, period)"""
    seen = {}
    out = []
    r = start
    T = 0
    while True:
        v = 0
        x = r
        while x:
            low = x & -x
            v ^= rows[low.bit_length() - 1]
            x ^= low
        r = v
        T += 1
        if r in seen:
            return out, seen[r], T - seen[r]
        seen[r] = T
        out.append(r)


def block_mask(blocks, name):
    s, n = blocks[name]
    return ((1 << n) - 1) << s


def holds_from(seq, T1, period, start, test):
    """test holds for r_T at every lag T >= start (the computed lags stand for all)"""
    lo = min(start, T1)
    return all(test(seq[T - 1]) for T in range(lo, T1 + period)) and all(test(seq[T - 1]) for T in range(start, len(seq) + 1))


def analyze(rules, sizes, k, law1, law2):
    rows, N, blocks = linear_matrix(rules, sizes, k, law1, law2)
    mA, mB, mC = sizes
    d = C.ring_distance(k, mB)
    mA_, mB_, mC_ = (block_mask(blocks, x) for x in "ABC")
    s1, T1a, p1 = row_orbit(rows, 1 << 0)
    s2, T1b, p2 = row_orbit(rows, 1 << 1)
    c1_persists = holds_from(s1, T1a, p1, 1, lambda r: bool(r & mA_) and bool(r & mB_))
    c2_persists = holds_from(s2, T1b, p2, 1, lambda r: bool(r & mB_) and bool(r & mC_))
    composes = holds_from(s2, T1b, p2, d + 1, lambda r: bool(r & mA_) and bool(r & mC_))
    composes_c1 = holds_from(s1, T1a, p1, d + 1, lambda r: bool(r & mA_) and bool(r & mC_))
    return {"c1 persists": c1_persists, "c2 persists": c2_persists, "c2 composes": composes, "c1 composes": composes_c1,
            "periods": (p1, p2), "d": d}


# ---------------------------------------------------------------------- the full state space, for verification
def mixed_state_map(rules, sizes, k, law1, law2):
    """the joint dynamics of a chain with any rules (one per ring) and laws, as state -> next state (proposals with any
    combiner g are ('proposals', g); the linear search uses g = XOR)"""
    mA, mB, mC = sizes
    RA, RB, RC, N, blocks = rings_of(mA, mB, mC, k)
    u = np.arange(1 << N, dtype=np.int64)
    bit = lambda pos: ((u >> pos) & 1).astype(np.uint8)
    vals = {pos: bit(pos) for pos in range(N)}
    tabs = [P.table(r) for r in rules]
    def nxt_ring(R, t, i):
        return t[(vals[R[(i - 1) % len(R)]] << 2) | (vals[R[i]] << 1) | vals[R[(i + 1) % len(R)]]]
    out = np.zeros(1 << N, dtype=np.int64)
    for R, t in ((RA, tabs[0]), (RB, tabs[1]), (RC, tabs[2])):
        for i in range(len(R)):
            if R[i] in (0, 1):
                continue
            out |= nxt_ring(R, t, i).astype(np.int64) << R[i]
    def contact(law, X, iX, tX, Y, iY, tY):
        if law[0] == "proposals":
            g = P.table(law[1] if len(law) > 1 else 0b0110, 4)
            return g[(nxt_ring(X, tX, iX) << 1) | nxt_ring(Y, tY, iY)]
        _, uX, uY = law
        ux, uy = P.table(uX, 4), P.table(uY, 4)
        return ux[(vals[X[(iX - 1) % len(X)]] << 1) | vals[X[(iX + 1) % len(X)]]] ^ uy[(vals[Y[(iY - 1) % len(Y)]] << 1) | vals[Y[(iY + 1) % len(Y)]]]
    out |= contact(law1, RA, 0, tabs[0], RB, 0, tabs[1]).astype(np.int64)
    out |= contact(law2, RB, k, tabs[1], RC, 0, tabs[2]).astype(np.int64) << 1
    return out, N, blocks
