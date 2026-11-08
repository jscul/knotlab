"""The square torus of rings (LATTICE-NET-20261108-001A), on LOOP-NET-20261108-001A's loopnet_lib.

Rings sit at the points p = (i, j) of Z_n x Z_n, each with four contacts in counterclockwise order E, N, W, S: h(p) joins p and p + e1,
v(p) joins p and p + e2. Contacts are equally spaced, g cells apart, so every corner weighs omega = z a^(g - 1). The contact graph reads
h(p) <- v(p - e2), v(p + e1) and v(p) <- h(p), h(p - e1 + e2). Laurent polynomials over GF(2) on Z_n x Z_n are 0/1 arrays indexed
[i % n, j % n]. Walk counts are read as bitsets: row c of A^k is the set of contacts d with an odd number of walks of length k from d
to c."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns"))
import loopnet_lib as LN  # noqa: E402

N = LN.N


def torus(n, g):
    """the network, its rotation and edges, and the indices: ring index of point p, contact index of h(p) and v(p)"""
    rot, edges = LN.square_torus(n)
    sizes, contacts = LN.network(rot, edges, g)
    verts = sorted(rot, key=repr)
    ring = {v: i for i, v in enumerate(verts)}
    hidx, vidx = {}, {}
    for e, (u, w) in enumerate(edges):
        if (w[0] - u[0]) % n == 1 and w[1] == u[1]:
            hidx[u] = e
        else:
            vidx[u] = e
    return sizes, contacts, rot, edges, ring, hidx, vidx


def ring_contacts(rot, edges, ring):
    return {ring[v]: set(rot[v]) for v in rot}


def in_sets(sizes, contacts, cut=()):
    """for each contact, the bitset of contacts it reads through a corner (empty when cut: a cut contact reads only itself)"""
    ins = [0] * len(contacts)
    for d, e, r, l in LN.corners(sizes, contacts):
        ins[e] ^= 1 << d
    for c in cut:
        ins[c] = 0
    return ins


def reach(ins, c):
    """rows c of A^0, A^1, ... until the next row lies in the span of the earlier ones (the Krylov space); every later row is a sum of
    these, so their supports already hold every contact ever reached. Returns (union bitset, first length k with each contact, the rows,
    the dimension)"""
    row, union, first, rows, basis = 1 << c, 0, {}, [], {}
    while True:
        x = row
        while x:
            top = x.bit_length() - 1
            if top not in basis:
                break
            x ^= basis[top]
        if not x:
            return union, first, rows, len(rows)
        basis[x.bit_length() - 1] = x
        k = len(rows)
        rows.append(row)
        new = row & ~union
        while new:
            low = new & -new
            first[low.bit_length() - 1] = k
            new ^= low
        union |= row
        nxt, y = 0, row
        while y:
            low = y & -y
            nxt ^= ins[low.bit_length() - 1]
            y ^= low
        row = nxt


def rings_needed(union, rc, cut=()):
    """rings with an uncut contact in the reach"""
    reached = union & ~sum(1 << c for c in set(cut))
    return {r for r, cs in rc.items() if any(reached >> d & 1 for d in cs)}


# ---------- Laurent polynomials on Z_n x Z_n
def mono(n, terms):
    a = np.zeros((n, n), dtype=np.uint8)
    for i, j in terms:
        a[i % n, j % n] ^= 1
    return a


def mul(a, b):
    n = a.shape[0]
    out = np.zeros_like(a)
    for i, j in zip(*np.nonzero(a)):
        out ^= np.roll(np.roll(b, i, 0), j, 1)
    return out


def L(n):
    return mono(n, [(1, 0), (-1, 0), (0, 1), (0, -1)])


def powers(n):
    """L^0, L^1, ... until they repeat: (list, (start, period))"""
    cur, seen, out, k = mono(n, [(0, 0)]), {}, [], 0
    Ln = L(n)
    while cur.tobytes() not in seen:
        seen[cur.tobytes()] = k
        out.append(cur)
        cur, k = mul(Ln, cur), k + 1
    return out, (seen[cur.tobytes()], k - seen[cur.tobytes()])


def diagonal(n, a, b):
    return (a - b) % n == 0 or (a + b) % n == 0
