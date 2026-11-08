"""Networks of rings joined by shared contacts (SEPARATE-20261108-001A), for paths and cycles of rings.

A network has rings of given sizes, each with an elementary linear rule (LIN of NATIVE-PATH-20261108-001A's path_lib), and contacts:
a contact is a cell of two rings, (ring a, position on a, ring b, position on b), with a self-blind law reading, on each of its two
rings, its left neighbour (12), its right neighbour (10) or both (6). Bits: contacts first, then each ring's own cells, ring by ring;
a ring's block is its own non-contact cells, as in path_lib. A cut contact is frozen: its law is replaced by c <- c, so it reads
nothing. Every verdict is read from row sequences of M^T (NATIVE-PATH-20261108-001A, Theorem 2)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences"))
import path_lib as PL  # noqa: E402

LIN, ULIN = PL.LIN, PL.ULIN


def layout(sizes, contacts):
    """rings as lists of bit positions, N, and blocks {ring: (start, length)}"""
    special = [dict() for _ in sizes]
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        special[ra][pa] = c
        special[rb][pb] = c
    pos = len(contacts)
    rings, blocks = [], {}
    for i, m in enumerate(sizes):
        start, R = pos, []
        for j in range(m):
            if j in special[i]:
                R.append(special[i][j])
            else:
                R.append(pos)
                pos += 1
        rings.append(R)
        blocks[i] = (start, pos - start)
    return rings, pos, blocks


def matrix(sizes, rules, contacts, cut=()):
    rings, N, blocks = layout(sizes, contacts)
    rows = [0] * N
    ncon = len(contacts)
    for R, rule in zip(rings, rules):
        l, s, r = LIN[rule]
        for j, b in enumerate(R):
            if b >= ncon:
                rows[b] = (l << R[j - 1]) ^ (s << b) ^ (r << R[(j + 1) % len(R)])
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        if c in cut:
            rows[c] = 1 << c
            continue
        v = 0
        for ring, p, u in ((ra, pa, law[0]), (rb, pb, law[1])):
            R = rings[ring]
            x, y = ULIN[u]
            v ^= (x << R[p - 1]) ^ (y << R[(p + 1) % len(R)])
        rows[c] = v
    return rows, N, blocks


def mask(blocks, ring):
    s, n = blocks[ring]
    return ((1 << n) - 1) << s


def orbit(rows, start, cap=10 ** 6):
    """(seq, T1, p) as in RECUR-PATH-20261108-001A's recur_lib: seq[t - 1] is the row at lag t, lags T1 .. T1 + p - 1 the cycle"""
    seen, seq, r, T = {}, [], start, 0
    while T < cap:
        v, x = 0, r
        while x:
            low = x & -x
            v ^= rows[low.bit_length() - 1]
            x ^= low
        r, T = v, T + 1
        if r in seen:
            return seq, seen[r], T - seen[r]
        seen[r] = T
        seq.append(r)
    return None


def row_at(o, T):
    seq, T1, p = o
    return seq[T - 1] if T - 1 < len(seq) else seq[T1 - 1 + (T - T1) % p]


def needs(sizes, rules, contacts, contact, ring, horizon, cut=()):
    """the lags 1 .. horizon at which a contact's value depends on a ring's first row"""
    rows, N, blocks = matrix(sizes, rules, contacts, cut)
    o = orbit(rows, 1 << contact)
    m = mask(blocks, ring)
    return [T for T in range(1, horizon + 1) if row_at(o, T) & m]


def mirror(sizes, rules, contacts, ring):
    """mirror one ring (cell j -> -j): rule 60 <-> 102, every contact on it moves from p to -p and swaps its left and right reads there"""
    rules = list(rules)
    rules[ring] = {60: 102, 102: 60}[rules[ring]]
    swap = {10: 12, 12: 10, 6: 6}
    out = []
    for (ra, pa, rb, pb, law) in contacts:
        law = list(law)
        if ra == ring:
            pa, law[0] = (-pa) % sizes[ring], swap[law[0]]
        if rb == ring:
            pb, law[1] = (-pb) % sizes[ring], swap[law[1]]
        out.append((ra, pa, rb, pb, tuple(law)))
    return tuple(sizes), tuple(rules), out


def state_map(sizes, rules, contacts, cut=()):
    """the full dynamics from the rules' and laws' truth tables, independent of matrix(): state -> next state"""
    import numpy as np
    rings, N, blocks = layout(sizes, contacts)
    ncon = len(contacts)
    u = np.arange(1 << N, dtype=np.int64)
    val = {b: ((u >> b) & 1).astype(np.uint8) for b in range(N)}
    out = np.zeros(1 << N, dtype=np.int64)
    for R, rule in zip(rings, rules):
        t = PL.P.table(rule)
        for j, b in enumerate(R):
            if b >= ncon:
                out |= t[(val[R[j - 1]] << 2) | (val[b] << 1) | val[R[(j + 1) % len(R)]]].astype(np.int64) << b
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        if c in cut:
            out |= val[c].astype(np.int64) << c
            continue
        v = np.zeros(1 << N, dtype=np.uint8)
        for ring, p, w in ((ra, pa, law[0]), (rb, pb, law[1])):
            R = rings[ring]
            t = PL.P.table(w, 4)
            v ^= t[(val[R[p - 1]] << 1) | val[R[(p + 1) % len(R)]]]
        out |= v.astype(np.int64) << c
    return out, N, blocks


def needs_full(sizes, rules, contacts, contact, ring, horizon, cut=()):
    """needs() read off the full state space: the lags at which the contact's value, as a function of the first row, depends on the
    ring's block (PROCESS-CHAIN-20261108-001A's blockwise test)"""
    import numpy as np
    nxt, N, blocks = state_map(sizes, rules, contacts, cut)
    cur = np.arange(len(nxt), dtype=np.int64)
    out = []
    for T in range(1, horizon + 1):
        cur = nxt[cur]
        F = ((cur >> contact) & 1).astype(np.uint8)
        if PL.C.depends_on_block(F, *blocks[ring], N):
            out.append(T)
    return out
