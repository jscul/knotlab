"""Shared contacts (SHARED-CONTACT-20261108-001), on top of PROCESS-CONTACT-20261108-001A's library.

Two rings share the contact cell c: ring A is c, a_1, .., a_{m-1} and ring B is c, b_1, .., b_{n-1}, each closed through c, and
every non-contact cell updates by its ring's elementary rule (so both rings read c). The joint first row is bit 0 for c(0), bits
1..m-1 for a_1..a_{m-1} and bits m..m+n-2 for b_1..b_{n-1}, as in process_contact_lib.

Two contact families:
- **proposals** (assumption A31): c(t + 1) = g(f_A(a_{m-1}, c, a_1), f_B(b_{n-1}, c, b_1)), g a two-input table (bit 2p + q);
- **self-blind**: c(t + 1) = h(a_{m-1}, a_1, b_{n-1}, b_1), h a four-input table (bit 8 a_{m-1} + 4 a_1 + 2 b_{n-1} + b_1), which
  does not read c; its parities are h = u(a_{m-1}, a_1) + v(b_{n-1}, b_1), u and v two-input tables (bit 2x + y)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PROCESS-CONTACT-20261108-001A/PROCESS-CONTACT-20261108-001A-P001_which_contacts_bind_two_processes"))
import process_contact_lib as P  # noqa: E402

NONCONSTANT_TWO = tuple(g for g in range(16) if g not in (0, 15))
AFFINE_TWO = (0b1100, 0b0011, 0b1010, 0b0101, 0b0110, 0b1001)      # x, not x, y, not y, x + y, x + y + 1


def parity_table(u, v):
    """h = u(a_{m-1}, a_1) + v(b_{n-1}, b_1) as a four-input table"""
    return sum((((u >> (2 * x + y)) & 1) ^ ((v >> (2 * z + w)) & 1)) << (8 * x + 4 * y + 2 * z + w)
               for x in (0, 1) for y in (0, 1) for z in (0, 1) for w in (0, 1))


def _rings(u, m, n):
    N = m + n - 1
    bits = P.bits_of(N)
    c = bits[:, 0]
    return np.concatenate([c[:, None], bits[:, 1:m]], axis=1), np.concatenate([c[:, None], bits[:, m:N]], axis=1)


def _step_rings(ring_a, ring_b, ta, tb):
    na = ta[(np.roll(ring_a, 1, axis=1) << 2) | (ring_a << 1) | np.roll(ring_a, -1, axis=1)]
    nb = tb[(np.roll(ring_b, 1, axis=1) << 2) | (ring_b << 1) | np.roll(ring_b, -1, axis=1)]
    return na, nb


def selfblind_state_map(rule_a, m, rule_b, n, h):
    """the joint dynamics of the self-blind contact on its 2^(m + n - 1) states: state -> next state"""
    ring_a, ring_b = _rings(None, m, n)
    na, nb = _step_rings(ring_a, ring_b, P.table(rule_a), P.table(rule_b))
    th = P.table(h, 16)
    nc = th[(ring_a[:, m - 1].astype(np.int64) << 3) | (ring_a[:, 1].astype(np.int64) << 2)
            | (ring_b[:, n - 1].astype(np.int64) << 1) | ring_b[:, 1]]
    nxt = nc.astype(np.int64)
    for j in range(1, m):
        nxt |= na[:, j].astype(np.int64) << j
    for j in range(1, n):
        nxt |= nb[:, j].astype(np.int64) << (m - 1 + j)
    return nxt


def selfblind_maps(rule_a, m, rule_b, n, h, T):
    """c(1), .., c(T) over the joint first row, by direct simulation (a second implementation, for checks)"""
    ring_a, ring_b = _rings(None, m, n)
    ta, tb, th = P.table(rule_a), P.table(rule_b), P.table(h, 16)
    out = []
    for _ in range(T):
        c = th[(ring_a[:, m - 1] << 3) | (ring_a[:, 1] << 2) | (ring_b[:, n - 1] << 1) | ring_b[:, 1]]
        na, nb = _step_rings(ring_a, ring_b, ta, tb)
        ring_a = np.concatenate([c[:, None], na[:, 1:]], axis=1)
        ring_b = np.concatenate([c[:, None], nb[:, 1:]], axis=1)
        out.append(c.copy())
    return out


def fast_binds(F, m, n):
    """process_contact_lib.binds for the shared layout, by reshaping: bits 0 (c0), 1..m-1 (ring A), m..m+n-2 (ring B)"""
    if F.min() == F.max():
        return False
    G = F.reshape(1 << (n - 1), 1 << m)                    # rows: ring B's cells; columns: c0 and ring A's cells
    if (G.min(axis=0) == G.max(axis=0)).any():            # some setting of ring A and c0 fixes F
        return False
    H = F.reshape(1 << (n - 1), 1 << (m - 1), 2)          # (ring B, ring A, c0)
    if (H.min(axis=1) == H.max(axis=1)).any():            # some setting of ring B and c0 fixes F
        return False
    return True


def lags_capped(nxt, test, cap):
    """process_contact_lib.lags_exactly with a cap: (verdicts, T1, period), or (verdicts, None, None) when the T-step map has not
    repeated within cap lags"""
    cur = np.arange(len(nxt), dtype=np.int64)
    seen = {}
    verdicts = []
    for T in range(1, cap + 1):
        cur = nxt[cur]
        key = cur.tobytes()
        if key in seen:
            return verdicts, seen[key], T - seen[key]
        seen[key] = T
        verdicts.append(test((cur & 1).astype(np.uint8)))
    return verdicts, None, None


def classify(verdicts, T1, period):
    if T1 is None:
        return "undecided"
    cyc, pre = verdicts[T1 - 1:T1 + period - 1], verdicts[:T1 - 1]
    if all(verdicts):
        return "binds at every lag"
    if all(cyc):
        return "binds from some lag on"
    if any(cyc):
        return "binds at recurring lags only"
    if any(pre):
        return "binding decays"
    return "never binds"


# ---------------------------------------------------------------------- the lag-1 criteria (ticket A)
def centre_canalizing(rule):
    f = lambda l, s, r: (rule >> (4 * l + 2 * s + r)) & 1
    return any(len({f(l, s, r) for l in (0, 1) for r in (0, 1)}) == 1 for s in (0, 1))


def proposals_bind_at_lag1(rule_a, rule_b, g2):
    """Theorem 1: a parity combiner, and neither rule canalizing at its centre"""
    return g2 in P.PARITIES and not centre_canalizing(rule_a) and not centre_canalizing(rule_b)


def selfblind_binds_at_lag1(h):
    """Theorem 2: no setting of one ring's pair makes h constant in the other's pair"""
    M = [[(h >> (4 * x + y)) & 1 for y in range(4)] for x in range(4)]
    return all(len(set(row)) == 2 for row in M) and all(len({M[x][y] for x in range(4)}) == 2 for y in range(4))


def affine_contact_row(nxt, N, lags):
    """for an affine state map, the support of the contact's row of M^T for T = 1..lags (None if the map is not affine)"""
    base = int(nxt[0])
    cols = [int(nxt[1 << j]) ^ base for j in range(N)]
    u = np.arange(1 << N, dtype=np.int64)
    lin = np.zeros(1 << N, dtype=np.int64)
    for j in range(N):
        lin ^= np.where((u >> j) & 1, cols[j], 0)
    if not ((lin ^ base) == nxt).all():
        return None
    def apply(c):
        v, j = 0, 0
        while c:
            if c & 1:
                v ^= cols[j]
            c >>= 1
            j += 1
        return v
    Mt = [1 << j for j in range(N)]
    rows = []
    for _ in range(lags):
        Mt = [apply(c) for c in Mt]
        rows.append(sum(((Mt[j] >> 0) & 1) << j for j in range(N)))
    return rows
