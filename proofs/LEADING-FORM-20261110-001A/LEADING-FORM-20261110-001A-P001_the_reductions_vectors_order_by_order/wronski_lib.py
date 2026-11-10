"""Library for LEADING-FORM-20261110-001A: the Wronskian form of the cut-open torus's family at its eigenvalue parameters (sides 2^m).

W(A, B) = A(k) B(k + 1) + B(k) A(k + 1), a polynomial in Y = k^2 + k; G the monic least polynomial at a, k = h - deg G, J = ceil(k/2).
Builds on CHAIN-ORDERS-20261110-001A's orders_lib (the family, its reduction, the Y-expansion)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/CHAIN-ORDERS-20261110-001A/CHAIN-ORDERS-20261110-001A-P001_the_reduced_form_at_every_order"))
import orders_lib as OL  # noqa: E402

CH, BL, RL = OL.CH, OL.BL, OL.RL


def pad(v, h):
    v = np.array(v, dtype=np.int64)
    return np.concatenate([v, np.zeros(max(0, h - len(v)), dtype=np.int64)])[:max(h, len(v))]


def wronskian(F, A, B):
    """W(A, B) as k-coefficients (a tau-invariant polynomial)"""
    A = np.array(A, dtype=np.int64)
    B = np.array(B, dtype=np.int64)
    w = BL.poly_mul(F, A, BL.shift_poly(B)) ^ BL.poly_mul(F, B, BL.shift_poly(A))
    return w


def to_Y_exact(F, w):
    """a tau-invariant polynomial given by k-coefficients, as Y-coefficients (exact)"""
    return OL.to_Y(F, np.array(w, dtype=np.int64), len(w))[: len(w) // 2 + 1]


def second_solution(F, a, m, G, k):
    """Theorem 3: a G' of degree <= h + k - 1 - 2J with Z_0 G' = 0 mod k^(h-J-1), outside G F[Y]; returns it (least degree)"""
    h = 1 << (m - 1)
    J = (k + 1) // 2
    Z0 = CH.coefficients(F, a, m, 1)[0]
    D = h + k - 1 - 2 * J
    rows = Z0[: h - J - 1][:, : D + 1]
    ns = BL.nullspace(F, rows)
    best = None
    for v in ns:
        if wronskian(F, G, v).any():
            d = int(np.nonzero(v)[0][-1])
            if best is None or d < best[0]:
                best = (d, v)
    return None if best is None else pad(best[1], h)
