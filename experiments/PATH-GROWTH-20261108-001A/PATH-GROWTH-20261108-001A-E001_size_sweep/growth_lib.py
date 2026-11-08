"""Families of paths that grow (PATH-GROWTH-20261108-001A), on NATIVE-PATH-20261108-001A's path_lib.

A family fixes each ring's linear rule and each contact's law, and a schedule says how the path grows:
- "antipodal": four rings of s cells each, s = 3 .. 9, the middle rings' contacts antipodal: c2 at index k of ring B and c3 at
  index k of ring C, with k = s // 2 (variant 0) or s - s // 2 (variant 1), chosen per middle ring;
- "two apart": four rings of s cells, s = 4 .. 9, the middle rings' contacts two apart: k = 2 (variant 0) or s - 2 (variant 1);
- "longer": n rings, n = 4 .. 9, end rings of 3 cells and middle rings of 5, every middle ring with the same rule and its contacts
  at the same position k = 2 (variant 0) or 3 (variant 1); the end contacts have their own laws and every inner contact the same law.
native() decides a path exactly by the row-sequence reduction, as path_lib.analyze does, but stops at the first lag that fails."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences"))
import path_lib as PL  # noqa: E402

SIZES = {"antipodal": range(3, 10), "two apart": range(4, 10), "longer": range(4, 10)}


def shape(schedule, s, variant):
    """sizes and positions of a family's path at size s (ring size, or number of rings for "longer")"""
    vB, vC = variant
    if schedule == "antipodal":
        k = lambda v: s // 2 if v == 0 else s - s // 2
        return (s, s, s, s), [k(vB), k(vC)]
    if schedule == "two apart":
        k = lambda v: 2 if v == 0 else s - 2
        return (s, s, s, s), [k(vB), k(vC)]
    assert schedule == "longer" and vB == vC
    return (3,) + (5,) * (s - 2) + (3,), [2 if vB == 0 else 3] * (s - 2)


def path(schedule, s, rules, laws, variant):
    """rules and laws of a family at size s: for "longer", rules = (first, middle, last) and laws = (first, inner, last)"""
    sizes, ks = shape(schedule, s, variant)
    if schedule == "longer":
        rules = (rules[0],) + (rules[1],) * (s - 2) + (rules[2],)
        laws = (laws[0],) + (laws[1],) * (s - 3) + (laws[2],)
    return tuple(rules), sizes, ks, tuple(laws)


def _step(rows, r):
    v = 0
    while r:
        low = r & -r
        v ^= rows[low.bit_length() - 1]
        r ^= low
    return v


def _tables(rows):
    n = len(rows)
    tabs = []
    for c in range(0, n, 8):
        t = [0] * 256
        for b in range(1, 256):
            low = b & -b
            j = c + low.bit_length() - 1
            t[b] = t[b ^ low] ^ (rows[j] if j < n else 0)
        tabs.append(t)
    return tabs


def _step_tab(tabs, r):
    v, c = 0, 0
    while r:
        v ^= tabs[c][r & 255]
        r >>= 8
        c += 1
    return v


def contact_ok(rows, start, test_always, test_late, L, cap):
    """True when test_always holds at every lag from 1 and test_late at every lag from L, False at the first lag that fails, None
    when the row sequence does not repeat within cap lags"""
    seen, seq, r, T = {}, [], start, 0
    tabs = None
    while T < cap:
        if T == 64:
            tabs = _tables(rows)
        r = _step(rows, r) if tabs is None else _step_tab(tabs, r)
        T += 1
        if r in seen:
            T1 = seen[r]
            # lags T1 .. T - 1 recur forever, so the late test must also hold at those of them before L
            return all(test_late(seq[t - 1]) for t in range(T1, min(L, T)))
        if not test_always(r) or (T >= L and not test_late(r)):
            return False
        seen[r] = T
        seq.append(r)
    return None


def native(rules, sizes, ks, laws, cap=200000):
    """"native", "not native" or "undecided": every contact binds its two rings at every lag, and the last contact binds the end
    rings at every lag from the light cone on"""
    rows, N, blocks = PL.linear_matrix(rules, sizes, ks, laws)
    n = len(sizes)
    m = [PL.mask(blocks, f"R{i}") for i in range(n)]
    L = PL.light_cone(sizes, ks)
    undecided = False
    for c in [n - 2] + list(range(n - 2)):
        a, b = m[c], m[c + 1]
        late = (lambda r: bool(r & m[0]) and bool(r & m[-1])) if c == n - 2 else (lambda r: True)
        ok = contact_ok(rows, 1 << c, lambda r, a=a, b=b: bool(r & a) and bool(r & b), late, L, cap)
        if ok is False:
            return "not native"
        undecided |= ok is None
    return "undecided" if undecided else "native"
