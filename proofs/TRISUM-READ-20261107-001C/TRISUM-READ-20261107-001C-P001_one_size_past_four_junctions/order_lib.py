"""Exact rows with a fixed enumeration order, for TRISUM-READ-20261107-001C.

Ticket B's lean enumerator walks the points in breadth-first order from point 0 of the space minus the removed line. On ticket C's
four-junction space that order keeps up to 34 lines open at once for most rows (20 for row 0), and the partial assignments explode.
Here one order serves every row: breadth-first through the whole space from the start point that keeps the fewest lines open over
all rows (ties to the smaller point), at most 19 on ticket C's space. The solutions do not depend on the order, and the result is
sorted by code as before, so exact_row returns what map_lib.exact_row returns.
"""
import collections
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2] if (HERE.parents[2] / "AGENTS.md").exists() else Path.cwd()
sys.path.insert(0, str(ROOT / "proofs/TRISUM-READ-20261107-001B/TRISUM-READ-20261107-001B-P001_frozen_predictions_on_larger_trisum_spaces"))
import map_lib as ML  # noqa: E402

TR = ML.TR
CHUNK = ML.CHUNK


def bfs_order(lines, n, start):
    adj = collections.defaultdict(set)
    for L in lines:
        for p in L:
            adj[p] |= set(L) - {p}
    order, seen = [], set()
    for s0 in [start] + list(range(n)):
        if s0 in seen:
            continue
        seen.add(s0)
        queue = [s0]
        while queue:
            p = queue.pop(0)
            order.append(p)
            for q in sorted(adj[p]):
                if q not in seen:
                    seen.add(q)
                    queue.append(q)
    return order


def open_lines(order, lines):
    pos = {p: i for i, p in enumerate(order)}
    spans = [(min(pos[p] for p in L), max(pos[p] for p in L)) for L in lines]
    return max(sum(1 for a, b in spans if a <= i < b) for i in range(len(order)))


def fixed_order(lines, n):
    """(width, start, order): the full space's breadth-first order from the start keeping the fewest lines open over every row"""
    best = None
    for s in range(n):
        o = bfs_order(lines, n, s)
        w = max(open_lines(o, [L for i, L in enumerate(lines) if i != M]) for M in range(len(lines)))
        if best is None or w < best[0]:
            best = (w, s, o)
    return best


def lean_solutions(lines, signs, n, skip, order):
    """ML.lean_solutions with the given point order"""
    act = [(L, s) for i, (L, s) in enumerate(zip(lines, signs)) if i != skip]
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


def exact_row(H, n, M, order):
    TL = TR.engine().TL
    AN = lean_solutions([tuple(l) for l in H], [(0, 0, 0)] * len(H), n, M, order)
    out = {}
    for L in range(len(H)):
        if L != M:
            Y = list(H[L])
            mm = TR.fast_masks(AN, Y, (0, 0, 0), [q for q in range(n) if q not in Y])
            out[L] = None if mm is None else TL.verdict_from_masks(*mm)
    return out, len(AN)
