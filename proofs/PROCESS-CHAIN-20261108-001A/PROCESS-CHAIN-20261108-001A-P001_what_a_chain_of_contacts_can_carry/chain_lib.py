"""Chains of three rings joined by two contacts (PROCESS-CHAIN-20261108-001), on SHARED-CONTACT-20261108-001A's library.

Ring A is c1, a_1, .., a_{mA-1}; ring B is b_0 = c1, b_1, .., b_{mB-1} with c2 = b_k; ring C is c2, e_1, .., e_{mC-1}. Each ring is
closed, every non-contact cell updates by its ring's elementary rule, and both contacts are shared: each is a cell of the two rings
it joins, and both of them read it. A contact combines its two rings' views by one law of either family of SHARED-CONTACT:
- **proposals**: g(f(left, c, right) in one ring, f(left, c, right) in the other), g a two-input table;
- **self-blind**: u(left, right in one ring) + u(left, right in the other), u a two-input table (the same u on both sides).

The joint first row is bit 0 for c1(0), bit 1 for c2(0), then ring A's own cells, ring B's own cells (b_j, j not 0 or k) and ring
C's own cells, each block contiguous. A contact *binds* two rings X and Y at lag T when every minimally decisive set of its value
meets both X's and Y's own cells: equivalently, neither the cells outside X nor the cells outside Y decide it."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SHARED-CONTACT-20261108-001A/SHARED-CONTACT-20261108-001A-P001_when_a_shared_contact_binds_at_the_first_step"))
import shared_contact_lib as S  # noqa: E402

P = S.P


def layout(mA, mB, mC, k):
    """bit positions: (c1, c2, A cells, B cells by index j, C cells) and the blocks as (start, length)"""
    a = list(range(2, 2 + mA - 1))
    bj = [j for j in range(1, mB) if j != k]
    b = {j: 2 + mA - 1 + i for i, j in enumerate(bj)}
    c = list(range(2 + mA - 1 + len(bj), 2 + mA - 1 + len(bj) + mC - 1))
    N = 2 + (mA - 1) + len(bj) + (mC - 1)
    blocks = {"A": (2, mA - 1), "B": (2 + mA - 1, len(bj)), "C": (2 + mA - 1 + len(bj), mC - 1)}
    return a, b, c, N, blocks


def _contact(family, law, left1, c, right1, left2, right2, f1, f2):
    if family == "proposals":
        p = f1[(left1 << 2) | (c << 1) | right1]
        q = f2[(left2 << 2) | (c << 1) | right2]
        return P.table(law, 4)[(p << 1) | q]
    u = P.table(law, 4)
    return u[(left1 << 1) | right1] ^ u[(left2 << 1) | right2]


def chain_state_map(rule, mA, mB, mC, k, family, law):
    """the joint dynamics on its 2^N states: state -> next state"""
    a, b, c, N, _ = layout(mA, mB, mC, k)
    u = np.arange(1 << N, dtype=np.int64)
    bit = lambda pos: ((u >> pos) & 1).astype(np.uint8)
    c1, c2 = bit(0), bit(1)
    A = [c1] + [bit(p) for p in a]                                  # ring A, index 0 is c1
    B = [c1 if j == 0 else (c2 if j == k else bit(b[j])) for j in range(mB)]
    C = [c2] + [bit(p) for p in c]
    f = P.table(rule)
    step = lambda R, i: f[(R[(i - 1) % len(R)] << 2) | (R[i] << 1) | R[(i + 1) % len(R)]]
    n1 = _contact(family, law, A[-1], c1, A[1], B[-1], B[1], f, f)
    n2 = _contact(family, law, B[k - 1], c2, B[(k + 1) % mB], C[-1], C[1], f, f)
    nxt = n1.astype(np.int64) | (n2.astype(np.int64) << 1)
    for i, p in enumerate(a, start=1):
        nxt |= step(A, i).astype(np.int64) << p
    for j, p in b.items():
        nxt |= step(B, j).astype(np.int64) << p
    for i, p in enumerate(c, start=1):
        nxt |= step(C, i).astype(np.int64) << p
    return nxt


def chain_maps(rule, mA, mB, mC, k, family, law, T):
    """(c1(t), c2(t)) for t = 1..T by direct simulation of the three rings as arrays (a second implementation, for checks)"""
    a, b, c, N, _ = layout(mA, mB, mC, k)
    bits = P.bits_of(N)
    c1, c2 = bits[:, 0].copy(), bits[:, 1].copy()
    RA = np.concatenate([c1[:, None], bits[:, a]], axis=1)
    cols = []
    for j in range(mB):
        cols.append(c1 if j == 0 else (c2 if j == k else bits[:, b[j]]))
    RB = np.stack(cols, axis=1)
    RC = np.concatenate([c2[:, None], bits[:, c]], axis=1)
    f = P.table(rule)
    out = []
    for _ in range(T):
        n1 = _contact(family, law, RA[:, -1], RA[:, 0], RA[:, 1], RB[:, -1], RB[:, 1], f, f)
        n2 = _contact(family, law, RB[:, k - 1], RB[:, k], RB[:, (k + 1) % mB], RC[:, -1], RC[:, 1], f, f)
        nA = f[(np.roll(RA, 1, axis=1) << 2) | (RA << 1) | np.roll(RA, -1, axis=1)]
        nB = f[(np.roll(RB, 1, axis=1) << 2) | (RB << 1) | np.roll(RB, -1, axis=1)]
        nC = f[(np.roll(RC, 1, axis=1) << 2) | (RC << 1) | np.roll(RC, -1, axis=1)]
        nA[:, 0] = n1
        nB[:, 0] = n1
        nB[:, k] = n2
        nC[:, 0] = n2
        RA, RB, RC = nA, nB, nC
        out.append((n1.copy(), n2.copy()))
    return out


def decides_outside(F, start, length, N):
    """some setting of the cells outside the block [start, start + length) makes F constant: the block alone cannot move F"""
    G = F.reshape(1 << (N - start - length), 1 << length, 1 << start)
    return bool((G.min(axis=1) == G.max(axis=1)).any())


def binds(F, blocks, names, N):
    """every minimally decisive set of F meets each named block's cells"""
    if F.min() == F.max():
        return False
    return not any(decides_outside(F, *blocks[x], N) for x in names)


def depends_on_block(F, start, length, N):
    """F depends on some cell of the block"""
    G = F.reshape(1 << (N - start - length), 1 << length, 1 << start)
    return bool((G.min(axis=1) != G.max(axis=1)).any())


def ring_distance(k, mB):
    return min(k, mB - k)


# ---------------------------------------------------------------------- the listening chain (Theorem 1)
def listening_chain_maps(rule, mA, mB, mC, k, g, T):
    """three rings closed on themselves; c1 reads a_0 and b_0, c2 reads b_k and e_0 (three-input law g on (x, c, y)); nothing
    reads the contacts. First row: c1, c2, ring A (mA cells), ring B (mB cells), ring C (mC cells)."""
    N = 2 + mA + mB + mC
    bits = P.bits_of(N)
    c1, c2 = bits[:, 0].copy(), bits[:, 1].copy()
    RA, RB, RC = bits[:, 2:2 + mA].copy(), bits[:, 2 + mA:2 + mA + mB].copy(), bits[:, 2 + mA + mB:].copy()
    gt = P.table(g)
    out = []
    for _ in range(T):
        c1, c2 = gt[(RA[:, 0] << 2) | (c1 << 1) | RB[:, 0]], gt[(RB[:, k] << 2) | (c2 << 1) | RC[:, 0]]
        RA, RB, RC = P.ring_step(RA, rule), P.ring_step(RB, rule), P.ring_step(RC, rule)
        out.append((c1.copy(), c2.copy()))
    return out, N
