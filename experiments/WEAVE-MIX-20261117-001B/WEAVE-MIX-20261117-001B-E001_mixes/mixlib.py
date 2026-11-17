"""Library for WEAVE-MIX-20261117-001B-E001: arrangements of not-all-equal-class knots on the six-regular weave.

The four not-all-equal-class knots exclude {p, p-bar} for p in P = (000, 100, 010, 001), in place order.  An arrangement gives each
up knot U(i, j) = (v(i,j), v(i+1,j), v(i,j+1)) and down knot D(i, j) = (v(i+1,j), v(i,j+1), v(i+1,j+1)) one of them, periodic
with column period pc (in i) and row period pr (in j): arr[(i % pc, j % pr, 'U' or 'D')] = index into P.
Bond signs: a knot excluding {p, p-bar} reads the bond between two of its places as -1 (antiferromagnetic) when p agrees on
them, +1 otherwise.  A bond is inconsistent when its two knots give it different signs."""
import itertools

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigs

P = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
UP_BONDS = {(0, 1): "e1", (0, 2): "e2", (1, 2): "e3"}      # e1 = (i,j)-(i+1,j), e2 = (i,j)-(i,j+1), e3 = (i+1,j)-(i,j+1)
DOWN_BONDS = {(0, 1): "e3", (0, 2): "e2", (1, 2): "e1"}    # down: e3 of cell (i,j), e2 at (i+1,j), e1 at (i,j+1)


def excluded(k):
    p = P[k]
    return {p, tuple(1 - x for x in p)}


def sign(k, a, b):
    p = P[k]
    return -1 if p[a] == p[b] else 1


def inconsistent_bonds(arr, pc, pr):
    """Inconsistent bonds per unit cell (pc x pr cells), averaged per cell.
    e1 at (i,j): U(i,j) places (0,1) and D(i,j-1) places (1,2).  e2 at (i,j): U(i,j) places (0,2) and D(i-1,j) places (0,2).
    e3 of cell (i,j): U(i,j) places (1,2) and D(i,j) places (0,1)."""
    bad = 0
    for i in range(pc):
        for j in range(pr):
            u = arr[(i, j, "U")]
            if sign(u, 0, 1) != sign(arr[(i, (j - 1) % pr, "D")], 1, 2):
                bad += 1
            if sign(u, 0, 2) != sign(arr[((i - 1) % pc, j, "D")], 0, 2):
                bad += 1
            if sign(u, 1, 2) != sign(arr[(i, j, "D")], 0, 1):
                bad += 1
    return bad / (pc * pr)


def transfer_rows(width, arr, pc, pr):
    """Transfer matrices T_j (row j to row j+1) for j = 0..pr-1."""
    R = 1 << width
    bits = (np.arange(R)[:, None] >> np.arange(width)[None, :]) & 1
    Ts = []
    for j in range(pr):
        ok = np.ones((R, R), dtype=bool)
        for i in range(width):
            a, a1 = bits[:, i][:, None], bits[:, (i + 1) % width][:, None]
            b, b1 = bits[:, i][None, :], bits[:, (i + 1) % width][None, :]
            for p in excluded(arr[(i % pc, j, "U")]):
                ok &= ~((a == p[0]) & (a1 == p[1]) & (b == p[2]))
            for p in excluded(arr[(i % pc, j, "D")]):
                ok &= ~((a1 == p[0]) & (b == p[1]) & (b1 == p[2]))
        Ts.append(ok)
    return Ts


def live_part(M):
    keep = np.ones(M.shape[0], dtype=bool)
    while True:
        sub = M[np.ix_(keep, keep)]
        good = (sub != 0).any(axis=1) & (sub != 0).any(axis=0)
        if good.all():
            return sub
        idx = np.flatnonzero(keep)
        keep[idx[~good]] = False
        if not keep.any():
            return M[:0, :0]


def spectrum(width, arr, pc, pr, k=10):
    """Spectrum of the product of one row period of transfer matrices; quantities are per row (the pr-th root)."""
    Ts = transfer_rows(width, arr, pc, pr)
    M = Ts[0].astype(np.float64)
    for T in Ts[1:]:
        M = M @ T.astype(np.float64)
    L = live_part(M)
    if len(L) == 0:
        return {"width": width, "empty": True, "per_site": 0.0}
    if len(L) <= 1024:
        ev = np.linalg.eigvals(L)
    else:
        try:
            ev = eigs(sp.csr_matrix(L), k=min(k, len(L) - 2), which="LM", return_eigenvectors=False, tol=1e-12,
                      maxiter=20000, v0=np.ones(len(L)))
        except Exception:
            ev = np.linalg.eigvals(L)
    mags = np.sort(np.abs(ev))[::-1]
    if mags[0] < 1e-12:
        return {"width": width, "empty": True, "per_site": 0.0}
    lam0 = mags[0] ** (1 / pr)
    top = int(np.sum(mags > mags[0] * (1 - 1e-9)))
    out = {"width": width, "empty": False, "live": int(len(L)), "per_site": float(lam0 ** (1 / width)), "top_multiplicity": top}
    if top < len(mags) and mags[top] > 1e-12:
        out["gap_log3"] = float(np.log(mags[0] / mags[top]) / np.log(3) / pr)
    else:
        out["gap_log3"] = float("inf")
    return out


def torus_count(L, arr, pc, pr):
    Ts = transfer_rows(L, arr, pc, pr)
    M = np.eye(1 << L, dtype=object)
    for j in range(L):
        M = M.dot(Ts[j % pr].astype(object))
    return int(np.trace(M))


def inconsistent_set(arr, pc, pr):
    """The inconsistent bonds of one period cell, as (kind, i, j), and the parity of each site's degree in them."""
    bad = set()
    for i in range(pc):
        for j in range(pr):
            u = arr[(i, j, "U")]
            if sign(u, 0, 1) != sign(arr[(i, (j - 1) % pr, "D")], 1, 2):
                bad.add(("e1", i, j))
            if sign(u, 0, 2) != sign(arr[((i - 1) % pc, j, "D")], 0, 2):
                bad.add(("e2", i, j))
            if sign(u, 1, 2) != sign(arr[(i, j, "D")], 0, 1):
                bad.add(("e3", i, j))
    deg = {(i, j): 0 for i in range(pc) for j in range(pr)}
    for kind, i, j in bad:          # e1: (i,j)-(i+1,j); e2: (i,j)-(i,j+1); e3: (i+1,j)-(i,j+1)
        ends = {"e1": [(i, j), (i + 1, j)], "e2": [(i, j), (i, j + 1)], "e3": [(i + 1, j), (i, j + 1)]}[kind]
        for a, b in ends:
            deg[(a % pc, b % pr)] += 1
    return sorted(bad), all(d % 2 == 0 for d in deg.values())


def sector_spectrum(width, arr, pc, pr):
    """Per-row spectrum split by the global flip (every knot here is closed under it): top flip-even eigenvalue,
    second flip-even (energy gap) and top flip-odd (spin gap), from one row period's product."""
    Ts = transfer_rows(width, arr, pc, pr)
    Mx = Ts[0].astype(np.float64)
    for T in Ts[1:]:
        Mx = Mx @ T.astype(np.float64)
    R = 1 << width
    full = R - 1
    alive = np.ones(R, dtype=bool)
    while True:
        sub = Mx[np.ix_(alive, alive)]
        good = (sub != 0).any(axis=1) & (sub != 0).any(axis=0)
        if good.all():
            break
        idx = np.flatnonzero(alive)
        alive[idx[~good]] = False
        if not alive.any():
            return {"width": width, "empty": True, "per_site": 0.0}
    reps = [a for a in range(R) if alive[a] and a < (a ^ full)]
    comp = [a ^ full for a in reps]
    A = Mx[np.ix_(reps, reps)]
    B = Mx[np.ix_(reps, comp)]
    def top(mat, k):
        n = mat.shape[0]
        if n <= 1024:
            ev = np.linalg.eigvals(mat)
        else:
            try:
                ev = eigs(sp.csr_matrix(mat), k=min(k, n - 2), which="LM", return_eigenvectors=False, tol=1e-12,
                          maxiter=20000, v0=np.ones(n))
            except Exception:
                ev = np.linalg.eigvals(mat)
        return np.sort(np.abs(ev))[::-1]
    even, odd = top(A + B, 4), top(A - B, 2)
    if even[0] < 1e-12:
        return {"width": width, "empty": True, "per_site": 0.0}
    lam0 = even[0]
    out = {"width": width, "empty": False, "live": int(alive.sum()), "per_site": float(lam0 ** (1 / (pr * width))),
           "even_top_multiplicity": int(np.sum(even > lam0 * (1 - 1e-9)))}
    lo = odd[0] if len(odd) else 0.0
    out["spin_gap"] = float(np.log(lam0 / lo) / np.log(3) / pr) if lo > 1e-12 else float("inf")
    sec = [x for x in even if x < lam0 * (1 - 1e-9)]
    out["energy_gap"] = float(np.log(lam0 / sec[0]) / np.log(3) / pr) if sec and sec[0] > 1e-12 else float("inf")
    return out
