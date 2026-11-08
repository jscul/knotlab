"""Paths whose rings may be hybrid, each cell with its own linear rule (PATH-HYBRID-20261108-001B), on NATIVE-PATH-20261108-001A's
path_lib. A ring's rule is an int (uniform) or a list with one rule per cell; entries at contact cells are ignored, so contacts on a
hybrid ring take self-blind laws only. The layout, laws and verdicts are path_lib's."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences"))
import path_lib as PL  # noqa: E402

W, C, P, LIN, ULIN = PL.W, PL.C, PL.P, PL.LIN, PL.ULIN


def cell_rule(rule, j):
    return rule if isinstance(rule, int) else rule[j]


def linear_matrix(rules, sizes, ks, laws):
    rings, N, blocks = PL.layout(sizes, ks)
    n = len(sizes)
    rows = [0] * N
    contacts = set(range(n - 1))
    for R, rule in zip(rings, rules):
        for j, b in enumerate(R):
            if b in contacts:
                continue
            l, s, r = LIN[cell_rule(rule, j)]
            rows[b] = (l << R[j - 1]) ^ (s << b) ^ (r << R[(j + 1) % len(R)])
    for c, ((ia, ja), (ib, jb)) in enumerate(PL.contact_sites(n, ks)):
        law = laws[c]
        Ra, Rb = rings[ia], rings[ib]
        if law[0] == "proposals":
            assert isinstance(rules[ia], int) and isinstance(rules[ib], int), "proposal laws need uniform rings"
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
    """the full dynamics, for verification (self-blind laws on hybrid rings)"""
    rings, N, blocks = PL.layout(sizes, ks)
    n = len(sizes)
    u = np.arange(1 << N, dtype=np.int64)
    vals = {b: ((u >> b) & 1).astype(np.uint8) for b in range(N)}
    out = np.zeros(1 << N, dtype=np.int64)
    contacts = set(range(n - 1))
    for R, rule in zip(rings, rules):
        for j, b in enumerate(R):
            if b in contacts:
                continue
            t = P.table(cell_rule(rule, j))
            out |= t[(vals[R[j - 1]] << 2) | (vals[R[j]] << 1) | vals[R[(j + 1) % len(R)]]].astype(np.int64) << b
    for c, ((ia, ja), (ib, jb)) in enumerate(PL.contact_sites(n, ks)):
        law = laws[c]
        Ra, Rb = rings[ia], rings[ib]
        if law[0] == "proposals":
            ta, tb = P.table(rules[ia]), P.table(rules[ib])
            v = (ta[(vals[Ra[ja - 1]] << 2) | (vals[Ra[ja]] << 1) | vals[Ra[(ja + 1) % len(Ra)]]]
                 ^ tb[(vals[Rb[jb - 1]] << 2) | (vals[Rb[jb]] << 1) | vals[Rb[(jb + 1) % len(Rb)]]])
        else:
            _, ua, ub = law
            pa, pb = P.table(ua, 4), P.table(ub, 4)
            v = pa[(vals[Ra[ja - 1]] << 1) | vals[Ra[(ja + 1) % len(Ra)]]] ^ pb[(vals[Rb[jb - 1]] << 1) | vals[Rb[(jb + 1) % len(Rb)]]]
        out |= v.astype(np.int64) << c
    return out, N, blocks


def analyze(rules, sizes, ks, laws):
    """path_lib.analyze on a hybrid path"""
    rows, N, blocks = linear_matrix(rules, sizes, ks, laws)
    n = len(sizes)
    m = [PL.mask(blocks, f"R{i}") for i in range(n)]
    L = PL.light_cone(sizes, ks)
    seqs = [W.row_orbit(rows, 1 << c) for c in range(n - 1)]
    persists = [W.holds_from(s, T1, p, 1, lambda r, a=m[c], b=m[c + 1]: bool(r & a) and bool(r & b)) for c, (s, T1, p) in enumerate(seqs)]
    sl, T1l, pl = seqs[-1]
    s0, T10, p0 = seqs[0]
    return {"persists": persists, "all persist": all(persists),
            "ends at the last contact": W.holds_from(sl, T1l, pl, L, lambda r: bool(r & m[0]) and bool(r & m[-1])),
            "ends at the first contact": W.holds_from(s0, T10, p0, L, lambda r: bool(r & m[0]) and bool(r & m[-1])),
            "last contact binds every ring": W.holds_from(sl, T1l, pl, L, lambda r: all(r & x for x in m)),
            "light cone": L, "periods": [s[2] for s in seqs]}
