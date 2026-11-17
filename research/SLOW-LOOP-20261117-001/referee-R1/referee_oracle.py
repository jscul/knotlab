"""SLOW-LOOP-R1 referee oracle: the referee's own code, written from the definitions only (no code of the study).

A signed knot (a, b, c) with signs (sa, sb, sc) is violated iff x_a ^ sa, x_b ^ sb, x_c ^ sc are all equal.
A tie (p, q, par) holds iff x_p == x_q ^ par in every allowed state.
"""
from __future__ import annotations

import numpy as np


def allowed(n: int, kv, ks=None) -> np.ndarray:
    """Every allowed state of n distinctions under the signed knots (kv, ks), by full enumeration of 2^n states.
    Returns an array (#allowed, n) of 0/1 values, rows in increasing integer order (bit v of the row index = x_v)."""
    kv = np.asarray(kv, dtype=np.int64).reshape(-1, 3)
    ks = np.zeros_like(kv) if ks is None else np.asarray(ks, dtype=np.int64).reshape(-1, 3)
    if n > 24:
        raise ValueError("brute force limited to n <= 24")
    N = 1 << n
    ints = np.arange(N, dtype=np.uint32)
    bit = {}

    def b(v):
        if v not in bit:
            bit[v] = ((ints >> np.uint32(v)) & np.uint32(1)).astype(np.uint8)
        return bit[v]

    ok = np.ones(N, dtype=bool)
    # drop exact duplicate knots (same members and signs) only to save time; the set of constraints is unchanged
    rows = {(int(a), int(bb), int(c), int(sa), int(sb), int(sc)) for (a, bb, c), (sa, sb, sc) in zip(kv, ks)}
    for (a, bb, c, sa, sb, sc) in rows:
        ea = b(a) ^ np.uint8(sa)
        eb = b(bb) ^ np.uint8(sb)
        ec = b(c) ^ np.uint8(sc)
        ok &= ~((ea == eb) & (eb == ec))
    idx = np.nonzero(ok)[0].astype(np.int64)
    return ((idx[:, None] >> np.arange(n, dtype=np.int64)[None, :]) & 1).astype(np.uint8)


def sat_rows(X: np.ndarray, kv, ks=None) -> np.ndarray:
    """For each row of X (states), whether it satisfies every signed knot."""
    kv = np.asarray(kv, dtype=np.int64).reshape(-1, 3)
    ks = np.zeros_like(kv) if ks is None else np.asarray(ks, dtype=np.int64).reshape(-1, 3)
    X = np.atleast_2d(np.asarray(X, dtype=np.int64))
    if len(kv) == 0:
        return np.ones(len(X), dtype=bool)
    e = X[:, kv] ^ ks[None, :, :]
    s = e.sum(axis=2)
    return np.all((s == 1) | (s == 2), axis=1)


def tie_witness(A: np.ndarray, p: int, q: int, par: int):
    """None if x_p == x_q ^ par in every row of A, else the first row where it fails."""
    bad = np.nonzero((A[:, p] ^ A[:, q]) != (par & 1))[0]
    return None if len(bad) == 0 else A[bad[0]]


def shadow_witness(A: np.ndarray, a, b, c, sa, sb, sc):
    """None if the signed knot holds in every row of A, else the first row where it is violated."""
    ea, eb, ec = A[:, a] ^ (sa & 1), A[:, b] ^ (sb & 1), A[:, c] ^ (sc & 1)
    bad = np.nonzero((ea == eb) & (eb == ec))[0]
    return None if len(bad) == 0 else A[bad[0]]


def as_set(X: np.ndarray) -> set:
    return {bytes(np.asarray(r, dtype=np.uint8)) for r in X}


def map_knot(root, rpar, members, signs):
    """The image of one signed knot under x_v = y_root(v) ^ rpar(v): returns (classes, effective signs) with
    y-variables named by root id."""
    r = [int(root[v]) for v in members]
    s = [int(si) ^ int(rpar[v]) for v, si in zip(members, signs)]
    return r, s


def classify_image(r, s):
    """'kept' if three distinct classes (then also the canonical form: members sorted, signs xor first sign),
    'always' if the image holds for every y, 'contra' if it fails for every y, 'binding2' if two members share a
    class with equal effective signs (it then forces the third class: a constraint between two classes)."""
    if len(set(r)) == 3:
        order = sorted(range(3), key=lambda j: r[j])
        rr = tuple(r[j] for j in order)
        ss = [s[j] for j in order]
        ss = tuple(x ^ ss[0] for x in ss)
        return "kept", (rr, ss)
    if r[0] == r[1] == r[2]:
        return ("contra" if s[0] == s[1] == s[2] else "always"), None
    for p, q in ((0, 1), (0, 2), (1, 2)):
        if r[p] == r[q]:
            return ("always" if s[p] != s[q] else "binding2"), None
    raise AssertionError


def lift(B: np.ndarray, roots: np.ndarray, root: np.ndarray, rpar: np.ndarray) -> np.ndarray:
    """States B over the class roots (column j = root id roots[j]) lifted to every original distinction."""
    n0 = len(root)
    col = np.full(n0, -1, dtype=np.int64)
    col[np.asarray(roots, dtype=np.int64)] = np.arange(len(roots))
    cj = col[np.asarray(root, dtype=np.int64)]
    if np.any(cj < 0):
        raise ValueError("a root is not among the listed roots")
    return (B[:, cj] ^ np.asarray(rpar, dtype=np.uint8)[None, :]).astype(np.uint8)
