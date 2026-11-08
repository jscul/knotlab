"""Intermittent composition in chains of three rings (INTERMITTENT-NET-20261108-001), on PROCESS-CHAIN-20261108-001A's library.

A chain composes at lag T when its far contact c2 binds the end rings A and C at T (every minimally decisive set of c2(T) meets
both). The profile of a chain records, for every lag up to the first repeat of its T-step map, five verdicts: composition, c2
depending on ring A, c2 depending on ring C, c1 binding A and B, and c2 binding B and C."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PROCESS-CHAIN-20261108-001A/PROCESS-CHAIN-20261108-001A-P001_what_a_chain_of_contacts_can_carry"))
import chain_lib as C  # noqa: E402

S, P = C.S, C.P
FIELDS = ("compose", "depends on A", "depends on C", "c1 binds A and B", "c2 binds B and C")


def verdicts_at(cur, blocks, N):
    F1, F2 = (cur & 1).astype(np.uint8), ((cur >> 1) & 1).astype(np.uint8)
    return (C.binds(F2, blocks, ("A", "C"), N), C.depends_on_block(F2, *blocks["A"], N), C.depends_on_block(F2, *blocks["C"], N),
            C.binds(F1, blocks, ("A", "B"), N), C.binds(F2, blocks, ("B", "C"), N))


def profile(rule, mA, mB, mC, family, law, cap=4096):
    """(per-lag verdict tuples for T = 1..T2 - 1, T1, period) with the T-step map repeating at T2 = T1 + period, or (rows, None,
    None) when it has not repeated within cap lags; repeats are found by 16-byte digests and confirmed by recomputation"""
    k = mB // 2
    a, b, c, N, blocks = C.layout(mA, mB, mC, k)
    nxt = C.chain_state_map(rule, mA, mB, mC, k, family, law)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, rows = {}, []
    for T in range(1, cap + 1):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            back = np.arange(len(nxt), dtype=np.int64)
            for _ in range(seen[key]):
                back = nxt[back]
            if not (back == cur).all():
                raise RuntimeError("digest collision")
            return rows, seen[key], T - seen[key]
        seen[key] = T
        rows.append(verdicts_at(cur, blocks, N))
    return rows, None, None


def cycle(rows, T1, period):
    """the verdict tuples of the eventual cycle, lags T1..T1 + period - 1"""
    return rows[T1 - 1:T1 + period - 1]
