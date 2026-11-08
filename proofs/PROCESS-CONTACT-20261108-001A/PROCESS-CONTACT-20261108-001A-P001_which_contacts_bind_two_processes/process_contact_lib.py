"""Two processes joined by one contact (PROCESS-CONTACT-20261108-001).

Two rings, each running an elementary cellular automaton (Wolfram's numbering: a cell's new value is bit 4l + 2s + r of the rule,
for its left, own and right values), and one contact cell c. Everything is written as one space-time law, whose allowed states are
the trajectories; the first row is free and every later value is a function of it.

- **Listening contact** (ticket A). Ring A has cells a_0..a_{m-1} and ring B cells b_0..b_{n-1}, each closed on itself. The contact
  reads a_0 and b_0 and may read itself: c(t + 1) = g(a_0(t), c(t), b_0(t)), g a three-input table (bit 4a + 2c + b). It feeds
  nothing back. The joint first row is bit j < m for a_j, bit m + j for b_j, and bit m + n for c(0).
- **Shared contact** (ticket B). The two rings share the cell c: ring A is c, a_1, .., a_{m-1} and ring B is c, b_1, .., b_{n-1},
  each closed through c. A non-contact cell updates by its ring's rule; the contact takes each ring's proposal, the ring's rule on
  its two ring neighbours and itself, and combines them: c(t + 1) = g(f_A(a_{m-1}, c, a_1), f_B(b_{n-1}, c, b_1)), g a two-input
  table (bit 2p + q). The joint first row is bit 0 for c(0), bits 1..m-1 for a_1..a_{m-1}, bits m..m+n-2 for b_1..b_{n-1}.

The contact *binds both rings at lag T* when every minimally decisive set of c(T) over the joint first row meets both rings'
own cells. By TIME-KNOTS-20261107-001A's Theorem 1 these sets, with c(T), are the knots of its two-time law (a single deciding cell
would give a tie); a binding contact has no tie. Truth tables are numpy uint8 arrays indexed by the joint first row."""
from __future__ import annotations

import itertools

import numpy as np

PARITIES = (0b0110, 0b1001)                 # XOR and XNOR as two-input tables (bit 2p + q)
TWO_INPUT = tuple(range(16))


def bits_of(n):
    u = np.arange(1 << n, dtype=np.int64)
    return ((u[:, None] >> np.arange(n)[None, :]) & 1).astype(np.uint8)


def table(rule, k=8):
    return np.array([(rule >> j) & 1 for j in range(k)], dtype=np.uint8)


def ring_step(state, rule):
    """one step of a ring (columns are cells, closed on itself)"""
    t = table(rule)
    return t[(np.roll(state, 1, axis=1) << 2) | (state << 1) | np.roll(state, -1, axis=1)]


# ---------------------------------------------------------------------- the listening contact
def listening_maps(rule_a, m, rule_b, n, g, T):
    """c(1), .., c(T) as truth tables over the joint first row (m + n + 1 bits), for the contact law g (three-input table)"""
    u = bits_of(m + n + 1)
    a, b, c = u[:, :m].copy(), u[:, m:m + n].copy(), u[:, m + n].copy()
    gt = table(g)
    out = []
    for _ in range(T):
        c = gt[(a[:, 0] << 2) | (c << 1) | b[:, 0]]
        a, b = ring_step(a, rule_a), ring_step(b, rule_b)
        out.append(c.copy())
    return out


def memoryless(g2):
    """the three-input law of a two-input contact law that does not read itself"""
    return sum(((g2 >> (2 * a + b)) & 1) << (4 * a + 2 * c + b) for a in (0, 1) for b in (0, 1) for c in (0, 1))


def ring_contact_history(rule, m, T):
    """a_0(0), .., a_0(T - 1) for every first row of a ring of m cells (rows: first rows, columns: times)"""
    s = bits_of(m)
    hist = []
    for _ in range(T):
        hist.append(s[:, 0].copy())
        s = ring_step(s, rule)
    return np.stack(hist, axis=1)


def listening_sides(m, n):
    """the first-row bits of ring A and of ring B, and the contact's own bit"""
    return (1 << m) - 1, ((1 << n) - 1) << m, 1 << (m + n)


def listening_state_map(rule_a, m, rule_b, n, g):
    """the joint dynamics of the listening contact on its 2^(m + n + 1) states (encoded as the first row): state -> next state"""
    u = bits_of(m + n + 1)
    a, b, c = u[:, :m], u[:, m:m + n], u[:, m + n]
    nc = table(g)[(a[:, 0] << 2) | (c << 1) | b[:, 0]]
    na, nb = ring_step(a, rule_a), ring_step(b, rule_b)
    nxt = nc.astype(np.int64) << (m + n)
    for j in range(m):
        nxt |= na[:, j].astype(np.int64) << j
    for j in range(n):
        nxt |= nb[:, j].astype(np.int64) << (m + j)
    return nxt


def lags_exactly(nxt, contact_bit, test, cap=1 << 16):
    """iterate the finite dynamics until its T-step map repeats; returns (verdicts for T = 1..T2, T1, period) where the T-step maps
    for T >= T1 repeat with the period, so the verdict at any lag T >= T1 equals the verdict at T1 + (T - T1) mod period"""
    cur = np.arange(len(nxt), dtype=np.int64)
    seen = {}
    verdicts = []
    for T in range(1, cap + 1):
        cur = nxt[cur]
        key = cur.tobytes()
        if key in seen:
            T1 = seen[key]
            return verdicts, T1, T - T1
        seen[key] = T
        verdicts.append(test(((cur >> contact_bit) & 1).astype(np.uint8)))
    raise RuntimeError("no repeat within the cap")


def at_every_lag(verdicts, T1, period, start=1):
    """the verdict holds at every lag T >= start: the lags from min(start, T1) to T1 + period - 1 stand for all of them"""
    return all(verdicts[min(start, T1) - 1:T1 + period - 1])


# ---------------------------------------------------------------------- the shared contact
def shared_maps(rule_a, m, rule_b, n, g2, T):
    """c(1), .., c(T) over the joint first row (m + n - 1 bits) of two rings sharing the contact cell"""
    N = m + n - 1
    u = bits_of(N)
    c = u[:, 0].copy()
    A = u[:, 1:m].copy()                    # a_1 .. a_{m-1}
    B = u[:, m:N].copy()                    # b_1 .. b_{n-1}
    ta, tb, tg = table(rule_a), table(rule_b), table(g2, 4)
    out = []
    for _ in range(T):
        ring_a = np.concatenate([c[:, None], A], axis=1)          # c, a_1, .., a_{m-1}, closed
        ring_b = np.concatenate([c[:, None], B], axis=1)
        na = ta[(np.roll(ring_a, 1, axis=1) << 2) | (ring_a << 1) | np.roll(ring_a, -1, axis=1)]
        nb = tb[(np.roll(ring_b, 1, axis=1) << 2) | (ring_b << 1) | np.roll(ring_b, -1, axis=1)]
        c = tg[(na[:, 0] << 1) | nb[:, 0]]
        A, B = na[:, 1:], nb[:, 1:]
        out.append(c.copy())
    return out


def shared_sides(m, n):
    N = m + n - 1
    return ((1 << m) - 1) & ~1, ((1 << N) - 1) & ~((1 << m) - 1), 1


def shared_state_maps(rule_a, m, rule_b, n, g2):
    """the joint dynamics of the shared contact on its 2^(m + n - 1) states, as one array: state -> next state"""
    N = m + n - 1
    u = bits_of(N)
    c = u[:, 0]
    A, B = u[:, 1:m], u[:, m:N]
    ta, tb, tg = table(rule_a), table(rule_b), table(g2, 4)
    ring_a = np.concatenate([c[:, None], A], axis=1)
    ring_b = np.concatenate([c[:, None], B], axis=1)
    na = ta[(np.roll(ring_a, 1, axis=1) << 2) | (ring_a << 1) | np.roll(ring_a, -1, axis=1)]
    nb = tb[(np.roll(ring_b, 1, axis=1) << 2) | (ring_b << 1) | np.roll(ring_b, -1, axis=1)]
    nc = tg[(na[:, 0] << 1) | nb[:, 0]]
    nxt = nc.astype(np.int64)
    for j in range(1, m):
        nxt |= na[:, j].astype(np.int64) << j
    for j in range(1, n):
        nxt |= nb[:, j].astype(np.int64) << (m - 1 + j)
    return nxt


# ---------------------------------------------------------------------- binding
def side_decides(F, side, n):
    """whether some setting of the bits in `side` (a mask) makes F constant over the other bits"""
    u = np.arange(1 << n, dtype=np.int64)
    key = u & side
    order = np.argsort(key, kind="stable")
    k, f = key[order], F[order]
    starts = np.flatnonzero(np.r_[True, k[1:] != k[:-1]])
    mins = np.minimum.reduceat(f, starts)
    maxs = np.maximum.reduceat(f, starts)
    return bool((mins == maxs).any())


def binds(F, side_a, side_b, own, n):
    """the contact binds both rings: neither ring's first row with the contact's own first value decides F"""
    if F.min() == F.max():
        return False
    return not side_decides(F, side_a | own, n) and not side_decides(F, side_b | own, n)


def binds_by_knots(F, side_a, side_b, n, knots_across_time):
    """the same, read directly from the minimally decisive sets (TIME-KNOTS-20261107-001A's machinery)"""
    kn, ties, const = knots_across_time(F, n)
    if const:
        return False
    md = kn + ties
    return all(S & side_a and S & side_b for S in md)


def binds_by_histories(G, HA, HB):
    """binding read through the rings' contact histories only: G(c0, hA, hB) for hA in HA, hB in HB (sets of tuples)"""
    for c0 in (0, 1):
        for h in HA:
            if len({G(c0, h, k) for k in HB}) < 2:
                return False
        for k in HB:
            if len({G(c0, h, k) for h in HA}) < 2:
                return False
    return True


def contact_value(g, c0, ha, hb):
    """c(T) from the contact's first value and the two rings' contact histories (three-input law g)"""
    c = c0
    for a, b in zip(ha, hb):
        c = (g >> (4 * a + 2 * c + b)) & 1
    return c


# ---------------------------------------------------------------------- linear rings
# offsets of the cells whose sum is the new value, as powers of X: the left neighbour is X, the right one X^-1
LINEAR = {0: (), 204: (0,), 240: (1,), 170: (-1,), 60: (0, 1), 102: (0, -1), 90: (1, -1), 150: (1, 0, -1)}
AFFINE = {255: 0, 51: 204, 15: 240, 85: 170, 195: 60, 153: 102, 165: 90, 105: 150}   # the output's negation: the linear rule plus one


def ring_poly(offsets, m):
    """p modulo X^m - 1 as a bitmask of ring positions"""
    p = 0
    for o in offsets:
        p ^= 1 << (o % m)
    return p


def poly_mul_mod(a, b, m):
    """a * b modulo X^m - 1 over GF(2), both bitmasks of ring positions"""
    out = 0
    for i in range(m):
        if a >> i & 1:
            out ^= ((b << i) | (b >> (m - i))) & ((1 << m) - 1) if i else b
    return out


def poly_ring_power(offsets, t, m):
    """the support of p^t modulo X^m - 1 over GF(2), as a bitmask of ring positions"""
    p, out = ring_poly(offsets, m), 1
    for _ in range(t):
        out = poly_mul_mod(out, p, m)
    return out


def nilpotency_index(offsets, m):
    """the least t with p^t = 0 modulo X^m - 1, or None when the powers of p cycle without reaching 0 (decided exactly)"""
    p, cur, t, seen = ring_poly(offsets, m), 1, 0, set()
    while cur not in seen:
        seen.add(cur)
        t += 1
        cur = poly_mul_mod(cur, p, m)
        if cur == 0:
            return t
    return None


def nilpotent_by_radical(offsets, m):
    """p is nilpotent modulo X^m - 1 exactly when X^m' - 1 divides it, m' the odd part of m (X^m' - 1 is squarefree)"""
    return ring_poly(offsets, odd_part(m)) == 0


def odd_part(m):
    while m % 2 == 0:
        m //= 2
    return m


def two_input_name(g2):
    names = {0: "0", 15: "1", 0b1100: "p", 0b0011: "not p", 0b1010: "q", 0b0101: "not q", 0b1000: "and", 0b1110: "or",
             0b0110: "xor", 0b1001: "xnor", 0b0111: "nand", 0b0001: "nor", 0b0100: "p and not q", 0b0010: "q and not p",
             0b1101: "p or not q", 0b1011: "q or not p"}
    return names[g2]


def canalizing_two_input(g2):
    """some value of one input fixes g2 (constants and one-input laws included)"""
    f = lambda p, q: (g2 >> (2 * p + q)) & 1
    return any(f(v, 0) == f(v, 1) for v in (0, 1)) or any(f(0, v) == f(1, v) for v in (0, 1))


def cnf_listening(rule_a, m, rule_b, n, g, T):
    """the space-time law of the listening contact as CNF clauses over named cells (for knotlab check)"""
    def rule_clauses(out, ins, k, tab):
        cl = []
        for vals in itertools.product((0, 1), repeat=k):
            idx = sum(v << (k - 1 - i) for i, v in enumerate(vals))
            lits = [(f"~{x}" if v else x) for x, v in zip(ins, vals)]
            lits.append(out if (tab >> idx) & 1 else f"~{out}")
            cl.append(" ".join(lits))
        return cl
    cl = []
    for t in range(T):
        cl += rule_clauses(f"c{t + 1}", [f"a{t}_0", f"c{t}", f"b{t}_0"], 3, g)
        if t == T - 1:
            break                           # c(T) reads the rings at T - 1, so their cells at T are not needed
        for i in range(m):
            cl += rule_clauses(f"a{t + 1}_{i}", [f"a{t}_{(i - 1) % m}", f"a{t}_{i}", f"a{t}_{(i + 1) % m}"], 3, rule_a)
        for i in range(n):
            cl += rule_clauses(f"b{t + 1}_{i}", [f"b{t}_{(i - 1) % n}", f"b{t}_{i}", f"b{t}_{(i + 1) % n}"], 3, rule_b)
    return cl
