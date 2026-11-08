"""Paths of n rings joined by n - 1 shared contacts (NATIVE-PATH-20261108-001), on AFFINE-WIRE-20261108-001A's library.

Rings R_0 .. R_(n-1). Contact c_i (i = 1 .. n-1) joins R_(i-1) and R_i: it is index 0 of R_i, and in R_(i-1) it is index 0 when
i - 1 = 0 and index k_(i-1) otherwise. So a middle ring R_i holds c_i at index 0 and c_(i+1) at index k_i, d_i = min(k_i, m_i - k_i)
apart. Every non-contact cell updates by its ring's elementary rule. Each contact has its own law, as in wire_lib: ("proposals",)
or ("self-blind", u_first, u_second), the first ring being R_(i-1). The joint first row is bit i - 1 for c_i(0), then each ring's
own cells as one contiguous block, R_0 first. For n = 3 this is exactly wire_lib's (and chain_lib's) layout."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/AFFINE-WIRE-20261108-001A/AFFINE-WIRE-20261108-001A-P001_persistent_composition_is_about_row_sequences"))
import wire_lib as W  # noqa: E402

C, P = W.C, W.P
LIN, ULIN = W.LIN, W.ULIN


def layout(sizes, ks):
    """rings as lists of bit positions, N, and blocks {"R0": (start, length), ...}"""
    n = len(sizes)
    pos = n - 1                                        # contacts take bits 0 .. n-2
    rings, blocks = [], {}
    for i, m in enumerate(sizes):
        if i == 0:
            special = {0: 0}                           # c_1 at index 0
        elif i == n - 1:
            special = {0: n - 2}                       # c_(n-1) at index 0
        else:
            special = {0: i - 1, ks[i - 1]: i}         # c_i at index 0, c_(i+1) at index k_i
        start = pos
        R = []
        for j in range(m):
            if j in special:
                R.append(special[j])
            else:
                R.append(pos)
                pos += 1
        rings.append(R)
        blocks[f"R{i}"] = (start, pos - start)
    return rings, pos, blocks


def contact_sites(n, ks):
    """for contact c_i: (ring index and position in R_(i-1)), (ring index and position in R_i)"""
    out = []
    for i in range(1, n):
        first = (i - 1, 0 if i - 1 == 0 else ks[i - 2])
        out.append((first, (i, 0)))
    return out


def linear_matrix(rules, sizes, ks, laws):
    rings, N, blocks = layout(sizes, ks)
    n = len(sizes)
    rows = [0] * N
    contacts = set(range(n - 1))
    for R, rule in zip(rings, rules):
        l, s, r = LIN[rule]
        for j, b in enumerate(R):
            if b in contacts:
                continue
            rows[b] = (l << R[j - 1]) ^ (s << b) ^ (r << R[(j + 1) % len(R)])
    for c, ((ia, ja), (ib, jb)) in enumerate(contact_sites(n, ks)):
        law = laws[c]
        Ra, Rb = rings[ia], rings[ib]
        if law[0] == "proposals":
            v = 0
            for R, j, rule in ((Ra, ja, rules[ia]), (Rb, jb, rules[ib])):
                l, s, r = LIN[rule]
                v ^= (l << R[j - 1]) ^ (s << c) ^ (r << R[(j + 1) % len(R)])
        else:
            _, ua, ub = law
            v = 0
            for R, j, u in ((Ra, ja, ua), (Rb, jb, ub)):
                x, y = ULIN[u]
                v ^= (x << R[j - 1]) ^ (y << R[(j + 1) % len(R)])
        rows[c] = v
    return rows, N, blocks


def mixed_state_map(rules, sizes, ks, laws):
    """the full dynamics, any rules and laws (proposals combine by XOR), for verification: state -> next state"""
    rings, N, blocks = layout(sizes, ks)
    n = len(sizes)
    u = np.arange(1 << N, dtype=np.int64)
    vals = {b: ((u >> b) & 1).astype(np.uint8) for b in range(N)}
    tabs = [P.table(r) for r in rules]
    step = lambda R, t, j: t[(vals[R[j - 1]] << 2) | (vals[R[j]] << 1) | vals[R[(j + 1) % len(R)]]]
    out = np.zeros(1 << N, dtype=np.int64)
    contacts = set(range(n - 1))
    for R, t in zip(rings, tabs):
        for j, b in enumerate(R):
            if b not in contacts:
                out |= step(R, t, j).astype(np.int64) << b
    for c, ((ia, ja), (ib, jb)) in enumerate(contact_sites(n, ks)):
        law = laws[c]
        Ra, Rb = rings[ia], rings[ib]
        if law[0] == "proposals":
            v = step(Ra, tabs[ia], ja) ^ step(Rb, tabs[ib], jb)
        else:
            _, ua, ub = law
            ta, tb = P.table(ua, 4), P.table(ub, 4)
            v = ta[(vals[Ra[ja - 1]] << 1) | vals[Ra[(ja + 1) % len(Ra)]]] ^ tb[(vals[Rb[jb - 1]] << 1) | vals[Rb[(jb + 1) % len(Rb)]]]
        out |= v.astype(np.int64) << c
    return out, N, blocks


def mask(blocks, name):
    s, n = blocks[name]
    return ((1 << n) - 1) << s


def light_cone(sizes, ks):
    """the first lag at which the last contact can depend on ring R_0: d_1 + .. + d_(n-2) + 1"""
    return sum(min(k, m - k) for k, m in zip(ks, sizes[1:-1])) + 1


def analyze(rules, sizes, ks, laws, cap=None):
    """exact verdicts by row sequences: each contact persists (binds its two rings at every lag); the last contact binds the end
    rings at every lag from the light cone on; the first contact does the same; the last contact binds every ring from then on"""
    rows, N, blocks = linear_matrix(rules, sizes, ks, laws)
    n = len(sizes)
    m = [mask(blocks, f"R{i}") for i in range(n)]
    L = light_cone(sizes, ks)
    seqs = []
    for c in range(n - 1):
        if cap is None:
            seqs.append(W.row_orbit(rows, 1 << c))
        else:
            seqs.append(capped_orbit(rows, 1 << c, cap))
    if any(s[1] is None for s in seqs):
        return None
    persists = [W.holds_from(s, T1, p, 1, lambda r, a=m[c], b=m[c + 1]: bool(r & a) and bool(r & b)) for c, (s, T1, p) in enumerate(seqs)]
    sl, T1l, pl = seqs[-1]
    s0, T10, p0 = seqs[0]
    ends_last = W.holds_from(sl, T1l, pl, L, lambda r: bool(r & m[0]) and bool(r & m[-1]))
    ends_first = W.holds_from(s0, T10, p0, L, lambda r: bool(r & m[0]) and bool(r & m[-1]))
    every_last = W.holds_from(sl, T1l, pl, L, lambda r: all(r & x for x in m))
    return {"persists": persists, "all persist": all(persists), "ends at the last contact": ends_last,
            "ends at the first contact": ends_first, "last contact binds every ring": every_last, "light cone": L,
            "periods": [s[2] for s in seqs]}


def capped_orbit(rows, start, cap):
    seen, out, r, T = {}, [], start, 0
    while T < cap:
        v, x = 0, r
        while x:
            low = x & -x
            v ^= rows[low.bit_length() - 1]
            x ^= low
        r, T = v, T + 1
        if r in seen:
            return out, seen[r], T - seen[r]
        seen[r] = T
        out.append(r)
    return out, None, None
