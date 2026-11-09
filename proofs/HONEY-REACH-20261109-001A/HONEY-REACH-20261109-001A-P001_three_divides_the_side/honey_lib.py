"""The honeycomb torus of rings (HONEY-REACH-20261109-001A), on LOOP-NET-20261108-001A's loopnet_lib.

Rings sit at A(p) and B(p), p = (i, j) in Z_n x Z_n (loopnet_lib.honeycomb_torus): A(p) holds the contacts e0(p), e1(p), e2(p) in
counterclockwise order, and B(p) holds e0(p), e1(p + x), e2(p + y), where e0(p) joins A(p) to B(p), e1(p) joins A(p) to B(p - x) and
e2(p) joins A(p) to B(p - y). Edge 3(i n + j) + k of honeycomb_torus is e_k(i, j). A contact reads the contact before it on each of its
rings, so the contact graph has the arcs e0(p) -> e1(p), e1(p) -> e2(p), e2(p) -> e0(p) round A(p) and e0(p) -> e1(p + x),
e1(p + x) -> e2(p + y), e2(p + y) -> e0(p) round B(p).

Laurent polynomials over GF(2) on Z_n x Z_n are 0/1 arrays indexed [i % n, j % n]; the coefficient of a polynomial F at q is F[q]. One
step from type k to type k + 1 multiplies by T_01 = 1 + x, T_12 = 1 + y/x, T_20 = 1 + 1/y, so three steps between contacts of one type
multiply by M = T_01 T_12 T_20 = x + 1/x + y + 1/y + y/x + x/y, the six-neighbour sum of the triangular lattice of A rings."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns"))
sys.path.insert(0, str(ROOT / "proofs/LATTICE-NET-20261108-001A/LATTICE-NET-20261108-001A-P001_odd_tori_compose_rings_of_cuts_separate"))
import loopnet_lib as LN  # noqa: E402
import lattice_lib as T  # noqa: E402

N = LN.N

UNITS = ((1, 0), (-1, 0), (0, 1), (0, -1), (-1, 1), (1, -1))
STEP = {0: (1, 0), 1: (-1, 1), 2: (0, -1)}  # T_k(k+1) = 1 + x^STEP[k]
NBHD = ((0, 0),) + UNITS                    # A(p) never needs A(0) iff Z0 contains p + NBHD
HEX = ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 1), (1, -1))  # B(p) never needs A(0) iff Z0 contains p + HEX
MIRRORS = ((1, 1), (-2, 1), (1, -2))        # directions of the three mirrors through A(0)


def ring_contacts_model(kind, p, n):
    """contacts of A(p) or B(p) as (type, position)"""
    i, j = p
    if kind == "A":
        return [(0, (i % n, j % n)), (1, (i % n, j % n)), (2, (i % n, j % n))]
    return [(0, (i % n, j % n)), (1, ((i + 1) % n, j % n)), (2, (i % n, (j + 1) % n))]


def network(n, g):
    """the library network and its indices: ring index of A(p), B(p); contact index of e_k(p)"""
    rot, edges = LN.honeycomb_torus(n)
    sizes, contacts = LN.network(rot, edges, g)
    verts = sorted(rot, key=repr)
    ring = {v: i for i, v in enumerate(verts)}
    cidx = {(k, (i, j)): 3 * (i * n + j) + k for i in range(n) for j in range(n) for k in range(3)}
    return rot, edges, sizes, contacts, ring, cidx


# ---------- polynomials
def mono(n, terms):
    a = np.zeros((n, n), dtype=np.uint8)
    for i, j in terms:
        a[i % n, j % n] ^= 1
    return a


def mul(a, b):
    out = np.zeros_like(a)
    for i, j in zip(*np.nonzero(a)):
        out ^= np.roll(np.roll(b, i, 0), j, 1)
    return out


def times_M(a):
    out = np.zeros_like(a)
    for i, j in UNITS:
        out ^= np.roll(np.roll(a, i, 0), j, 1)
    return out


def M(n):
    return mono(n, UNITS)


def P(n, i, j):
    """the polynomial of the shortest type path i -> j: product of the steps T_i(i+1) ... T_(j-1)j"""
    out, k = mono(n, [(0, 0)]), i
    while k != j:
        out = mul(out, mono(n, [(0, 0), STEP[k]]))
        k = (k + 1) % 3
    return out


def krylov(start):
    """start, start M, start M^2, ... until the next lies in the span of the earlier ones: (basis rows as arrays, count). Every later
    power is a sum of these, so their supports hold every point any power reaches; exact, no cutoff."""
    n = start.shape[0]
    cur, basis, rows = start.copy(), {}, []
    while True:
        v = int.from_bytes(np.packbits(cur.ravel()).tobytes(), "big")
        x = v
        while x:
            top = x.bit_length() - 1
            b = basis.get(top)
            if b is None:
                break
            x ^= b
        if not x:
            return rows
        basis[x.bit_length() - 1] = x
        rows.append(cur)
        cur = times_M(cur)


def union(rows, n):
    u = np.zeros((n, n), dtype=bool)
    for r in rows:
        u |= r.astype(bool)
    return u


def zero_set(n):
    """Z0: the points where every power M^k, k >= 0, vanishes"""
    return ~union(krylov(mono(n, [(0, 0)])), n)


def mirror_lines(n):
    L = np.zeros((n, n), dtype=bool)
    for s in range(1, n):
        for a, b in MIRRORS:
            L[(s * a) % n, (s * b) % n] = True
    L[0, 0] = False
    return L


def window_all(Z, offsets):
    """points p with Z true at every p + offset"""
    out = np.ones_like(Z)
    for a, b in offsets:
        out &= np.roll(np.roll(Z, -a, 0), -b, 1)
    return out


def never_need_A0(n, Z=None):
    """rings that never need A(0), by the window lemma: (A points, B points)"""
    if Z is None:
        Z = zero_set(n)
    a, b = window_all(Z, NBHD), window_all(Z, HEX)
    return ([(int(i), int(j)) for i, j in zip(*np.nonzero(a))], [(int(i), int(j)) for i, j in zip(*np.nonzero(b))])


def reach_sets(n):
    """R[(i, j)]: offsets q such that some power reaches e_j(s + q) from e_i(s), i.e. the union over the Krylov basis F of supp(P_ij F)"""
    base = krylov(mono(n, [(0, 0)]))
    R = {}
    for i in range(3):
        for j in range(3):
            Pij = P(n, i, j)
            R[(i, j)] = union([mul(Pij, F) for F in base], n)
    return R


def never_needs_model(n, src, R=None):
    """the set of rings (kind, p) none of whose contacts is reached from a contact of ring src = (kind, p), by the nine reach sets"""
    if R is None:
        R = reach_sets(n)
    S = ring_contacts_model(src[0], src[1], n)
    out = set()
    for kind in "AB":
        for i in range(n):
            for j in range(n):
                hit = False
                for (ti, tp) in ring_contacts_model(kind, (i, j), n):
                    for (si, sp) in S:
                        if R[(si, ti)][(tp[0] - sp[0]) % n, (tp[1] - sp[1]) % n]:
                            hit = True
                if not hit:
                    out.add((kind, (i, j)))
    return out


def predicted_misses(n):
    """the census formula: 0 when 3 | n; else 2(N - 1)(N - 2) + 1 with N = 2^(v2(n) + 1), or 2^(v2(n) - 1) when n is a power of two"""
    if n % 3 == 0:
        return 0
    s, m = 0, n
    while m % 2 == 0:
        m //= 2
        s += 1
    Nn = 2 ** (s + 1) if m > 1 else 2 ** (s - 1)
    return 2 * (Nn - 1) * (Nn - 2) + 1
