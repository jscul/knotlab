"""Readings of a growing plane on large tubes (ROUND-READ-20261110-001A-E001), vectorized with numpy, written afresh.

Geometry as in CONF-METRIC-20261110-001A: rings (i, r) of 4g cells on a square torus of side S; position 0 of ring (i, r) is the
contact h(i, r), shared with position 2g of ring (i + 1, r); position g is the contact v(i, r), shared with position 3g of (i, r + 1);
the rest are own cells. Rule 60 (an own cell becomes itself plus its left neighbour) and law (12, 12) (a contact becomes the sum of its
two left neighbours). Doubling: ring (i, r) becomes (2i, 2r) keeping its own cells; everything else is born open.

Four readings from ring (0, 0), each the first lag at which the original ring at v is reached:
- T: a route from any of (0, 0)'s first-row own cells reaches any own cell of the ring (reach: OR over the cells a cell reads);
- T1: a route from (0, 0)'s position-1 cell reaches the ring's position-1 cell;
- L: an own cell of the ring depends on (0, 0)'s first-row own cells (plain dependence: XOR, one bit per first-row own cell);
- L1: the ring's position-1 cell depends on (0, 0)'s position-1 cell."""
import numpy as np


def stage(S, g):
    L = 4 * g
    own_pos = np.array([p for p in range(L) if p % g])
    no = len(own_pos)
    pidx = -np.ones(L, dtype=np.int64)
    pidx[own_pos] = np.arange(no)
    nown = S * S * no
    I, R = np.meshgrid(np.arange(S), np.arange(S), indexing="ij")
    I, R = I.ravel(), R.ravel()

    def own(i, r, p):
        return ((i % S) * S + (r % S)) * no + pidx[p % L]

    def h(i, r):
        return nown + 2 * ((i % S) * S + (r % S))

    def v(i, r):
        return nown + 2 * ((i % S) * S + (r % S)) + 1

    def cell(i, r, p):
        p = p % L
        if p == 0:
            return h(i, r)
        if p == g:
            return v(i, r)
        if p == 2 * g:
            return h(i - 1, r)
        if p == 3 * g:
            return v(i, r - 1)
        return own(i, r, p)
    N = nown + 2 * S * S
    A = np.empty(N, dtype=np.int64)
    B = np.empty(N, dtype=np.int64)
    for p in own_pos:
        c = own(I, R, p)
        A[c] = c
        B[c] = cell(I, R, p - 1)
    A[h(I, R)], B[h(I, R)] = cell(I, R, -1), cell(I + 1, R, 2 * g - 1)
    A[v(I, R)], B[v(I, R)] = cell(I, R, g - 1), cell(I, R + 1, 3 * g - 1)
    return {"S": S, "A": A, "B": B, "N": N, "no": no, "own_pos": own_pos, "own": own, "nown": nown}


def double_map(st, st2):
    """for every own cell of the old stage, its index in the doubled stage (ring (i, r) -> (2i, 2r), same position)"""
    S, no = st["S"], st["no"]
    idx = np.arange(st["nown"])
    ring, j = idx // no, idx % no
    i, r = ring // S, ring % S
    return ((2 * i) * (2 * S) + 2 * r) * no + j


def readings(n, g, runs):
    st = stage(2 * n, g)
    N = st["N"]
    no = st["no"]
    src_cells = st["own"](0, 0, st["own_pos"])
    src1 = st["own"](0, 0, 1)
    R = np.zeros(N, dtype=bool)
    R[src_cells] = True
    R1 = np.zeros(N, dtype=bool)
    R1[src1] = True
    X = np.zeros(N, dtype=np.uint32)
    X[src_cells] = (np.uint32(1) << np.arange(no, dtype=np.uint32))
    X1 = np.zeros(N, dtype=np.uint8)
    X1[src1] = 1
    first = {"T": {}, "T1": {}, "L": {}, "L1": {}}
    t, D = 0, []
    origs = [(a, b) for a in range(n) for b in range(n) if (a, b) != (0, 0)]
    oa = np.array([Y[0] for Y in origs])
    ob = np.array([Y[1] for Y in origs])
    got = {key: np.zeros(len(origs), dtype=np.int64) for key in first}
    for P in runs:
        k = st["S"] // n
        cells = np.stack([st["own"](oa * k, ob * k, p) for p in st["own_pos"]], axis=1)
        cell1 = st["own"](oa * k, ob * k, 1)
        A, B = st["A"], st["B"]
        for _ in range(P):
            R = R[A] | R[B]
            R1 = R1[A] | R1[B]
            X = X[A] ^ X[B]
            X1 = X1[A] ^ X1[B]
            t += 1
            for key, hit in (("T", R[cells].any(axis=1)), ("T1", R1[cell1]), ("L", (X[cells] != 0).any(axis=1)),
                             ("L1", X1[cell1] != 0)):
                new = hit & (got[key] == 0)
                got[key][new] = t
        st2 = stage(2 * st["S"], g)
        m = double_map(st, st2)
        nown = st["nown"]
        def carry(arr):
            out = np.zeros(st2["N"], dtype=arr.dtype)
            out[m] = arr[:nown]
            return out
        R, R1, X, X1 = carry(R), carry(R1), carry(X), carry(X1)
        st = st2
        D.append(t)
    for key in first:
        first[key] = {origs[j]: int(got[key][j]) for j in range(len(origs)) if got[key][j]}
    return first, D, t


def conformal(D):
    def phi(t):
        k, s, prev = 0, 0.0, 0
        for d in D:
            if d >= t:
                break
            s += (min(d, t) - prev) * 2.0 ** -k
            prev, k = d, k + 1
        s += (t - prev) * 2.0 ** -k
        return s
    return phi
