"""Memory-lean exact rows for TRISUM-READ-20261107-001B.

lean_solutions returns the same array as CHAIN-TRANSFER A's TL.solutions (every solution, rows in ascending code): the same point order and
line checks, but whenever the partial assignments exceed CHUNK rows they are split and finished one part at a time, so memory stays
bounded; the final sort by code makes the result independent of the split. exact_row is ticket A's tr_lib.exact_row with it in place of
TL.solutions. Eight of the ten test maps were computed with it (the first two with tr_lib.exact_row); check 2 recomputes sample rows
with both.
"""
import collections
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
A = HERE.parents[1] / "TRISUM-READ-20261107-001A" / "TRISUM-READ-20261107-001A-P001_junctions_in_the_native_creation_map"
sys.path.insert(0, str(A))
import tr_lib as TR  # noqa: E402  (ticket A's library, bound by hash in its frozen predictions)

CHUNK = 1 << 16


def lean_solutions(lines, signs, n, skip=None):
    act = [(L, s) for i, (L, s) in enumerate(zip(lines, signs)) if i != skip]
    adj = collections.defaultdict(set)
    for L, s in act:
        for p in L:
            adj[p] |= set(L) - {p}
    order, seen = [], set()
    for start in range(n):
        if start in seen:
            continue
        seen.add(start)
        queue = [start]
        while queue:
            p = queue.pop(0)
            order.append(p)
            for q in sorted(adj[p]):
                if q not in seen:
                    seen.add(q)
                    queue.append(q)
    pos = {p: i for i, p in enumerate(order)}
    done_at = collections.defaultdict(list)
    for L, s in act:
        done_at[max(pos[p] for p in L)].append((L, s))
    finished = []
    stack = [(np.zeros((1, 0), dtype=np.int8), 0)]
    while stack:
        rows, i0 = stack.pop()
        for i in range(i0, len(order)):
            rows = np.concatenate([np.concatenate([rows, np.full((len(rows), 1), v, dtype=np.int8)], axis=1) for v in (0, 1)])
            for L, s in done_at[i]:
                lit = [rows[:, pos[q]] ^ s[j] for j, q in enumerate(L)]
                rows = rows[~((lit[0] == lit[1]) & (lit[1] == lit[2]))]
            if len(rows) > CHUNK and i + 1 < len(order):
                half = len(rows) // 2
                stack.append((rows[half:], i + 1))
                rows = rows[:half]
        finished.append(rows)
    rows = np.concatenate(finished) if finished else np.zeros((0, len(order)), dtype=np.int8)
    out = np.zeros((len(rows), n), dtype=np.int8)
    for p in range(n):
        out[:, p] = rows[:, pos[p]]
    codes = np.zeros(len(out), dtype=np.int64)
    for p in range(n):
        codes |= out[:, p].astype(np.int64) << p
    return out[np.argsort(codes, kind="stable")]


def exact_row(H, n, M):
    TL = TR.engine().TL
    AN = lean_solutions([tuple(l) for l in H], [(0, 0, 0)] * len(H), n, skip=M)
    out = {}
    for L in range(len(H)):
        if L != M:
            Y = list(H[L])
            mm = TR.fast_masks(AN, Y, (0, 0, 0), [q for q in range(n) if q not in Y])
            out[L] = None if mm is None else TL.verdict_from_masks(*mm)
    return out, len(AN)
