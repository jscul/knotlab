"""Library for WEAVE-LAWS-20261117-001B-E001: three-place knot laws on the six-regular weave.

A law is a pair of excluded sets of joint states, one for the weave's up knots (v(i,j), v(i+1,j), v(i,j+1)) and one for its down
knots (v(i+1,j), v(i,j+1), v(i+1,j+1)), in that place order.  The row transfer matrix T[a, b] is 1 when rows a (row j) and b
(row j+1) satisfy every up and down knot between them.  Its eigenvalues give the count of states per row (lambda_0) and the
transfer gap log_3(lambda_0 / |lambda_1|), lambda_1 the largest modulus below the top one.
The census part enumerates the relations a law's knots allow on n labelled distinctions (closure from the full relation) and
asks whether N, the single counts and the pair (disagreement) counts determine the relation."""
import itertools

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigs

LAWS = {
    "NAE": ({(0, 0, 0), (1, 1, 1)},) * 2,
    "signed NAE, place 2 odd (consistent signs)": ({(0, 1, 0), (1, 0, 1)},) * 2,
    "signed NAE, place 1 odd": ({(1, 0, 0), (0, 1, 1)},) * 2,
    "signed NAE, place 3 odd": ({(0, 0, 1), (1, 1, 0)},) * 2,
    "NAE up, place 1 odd down": ({(0, 0, 0), (1, 1, 1)}, {(1, 0, 0), (0, 1, 1)}),
    "NAE up, place 3 odd down": ({(0, 0, 0), (1, 1, 1)}, {(0, 0, 1), (1, 1, 0)}),
    "OR": ({(0, 0, 0)},) * 2,
    "not-exactly-two": ({(0, 1, 1), (1, 0, 1), (1, 1, 0)},) * 2,
    "parity": ({(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)},) * 2,
    "distance-two, place 1 odd": ({(0, 0, 0), (0, 1, 1)},) * 2,
    "distance-two, place 2 odd": ({(0, 0, 0), (1, 0, 1)},) * 2,
    "distance-two, place 3 odd": ({(0, 0, 0), (1, 1, 0)},) * 2,
}

# The weave's bond kinds by place: up knot (1,2) = e1, (1,3) = e2, (2,3) = e3; down knot (1,2) = e3, (1,3) = e2, (2,3) = e1.
UP_BONDS = {(0, 1): "e1", (0, 2): "e2", (1, 2): "e3"}
DOWN_BONDS = {(0, 1): "e3", (0, 2): "e2", (1, 2): "e1"}


def consistent_signs(law):
    """For a law whose knots each exclude one complementary pair {p, p-bar}: the Ising sign of each bond is
    -1 when p agrees on its two places and +1 otherwise.  Consistent (flat) when the up and down knots give each
    bond kind the same sign; then the weave is gauge-equivalent to the triangular antiferromagnet up to holonomy.
    Returns None for laws outside the class."""
    up, down = law
    def signs(excl, bonds):
        if len(excl) != 2:
            return None
        p, q = sorted(excl)
        if tuple(1 - x for x in p) != q:
            return None
        return {bonds[k]: (-1 if p[k[0]] == p[k[1]] else 1) for k in bonds}
    su, sd = signs(up, UP_BONDS), signs(down, DOWN_BONDS)
    if su is None or sd is None:
        return None
    return su == sd


def transfer(width, law):
    up, down = law
    R = 1 << width
    bits = (np.arange(R)[:, None] >> np.arange(width)[None, :]) & 1
    ok = np.ones((R, R), dtype=bool)
    for i in range(width):
        a, a1 = bits[:, i][:, None], bits[:, (i + 1) % width][:, None]
        b, b1 = bits[:, i][None, :], bits[:, (i + 1) % width][None, :]
        for p in up:
            ok &= ~((a == p[0]) & (a1 == p[1]) & (b == p[2]))
        for p in down:
            ok &= ~((a1 == p[0]) & (b == p[1]) & (b1 == p[2]))
    return ok


def live_part(ok):
    """Rows and columns that lie on an infinite path (repeatedly drop rows with no successor and columns with no
    predecessor); the nonzero spectrum lives there.  Added after the freeze, before any read-out, when ARPACK failed on a
    degenerate matrix (see the decision note)."""
    keep = np.ones(len(ok), dtype=bool)
    while True:
        sub = ok[np.ix_(keep, keep)]
        good = sub.any(axis=1) & sub.any(axis=0)
        if good.all():
            return ok[np.ix_(keep, keep)]
        idx = np.flatnonzero(keep)
        keep[idx[~good]] = False
        if not keep.any():
            return ok[:0, :0]


def spectrum(width, law, k=10):
    ok = live_part(transfer(width, law))
    if len(ok) == 0:
        ev = np.array([0.0])
    elif len(ok) <= 1024:
        ev = np.linalg.eigvals(ok.astype(np.float64))
    else:
        M = sp.csr_matrix(ok.astype(np.float64))
        try:
            ev = eigs(M, k=min(k, len(ok) - 2), which="LM", return_eigenvectors=False, tol=1e-12, maxiter=20000,
                      v0=np.ones(len(ok)))
        except Exception:
            ev = np.linalg.eigvals(ok.astype(np.float64))
    mags = np.sort(np.abs(ev))[::-1]
    out = {"width": width, "lambda0": float(mags[0]) if mags[0] > 0 else 0.0, "nonzero": bool(mags[0] > 1e-12)}
    if mags[0] > 1e-12:
        top = int(np.sum(mags > mags[0] * (1 - 1e-9)))
        out["top_multiplicity"] = top
        if top < len(mags) and mags[top] > 1e-12:
            out["lambda1_abs"] = float(mags[top])
            out["gap_log3"] = float(np.log(mags[0] / mags[top]) / np.log(3))
        else:
            out["lambda1_abs"] = 0.0
            out["gap_log3"] = float("inf")
        out["per_site"] = float(mags[0] ** (1 / width))
    full = transfer(width, law)
    out["live_rows"] = int(len(ok))
    out["torus_states"] = int(np.trace(np.linalg.matrix_power(full.astype(object), width))) if width <= 6 else None
    return out


# ---------- census ----------

def knot_mask(n, places, excluded):
    return sum(1 << s for s in range(1 << n) if tuple((s >> u) & 1 for u in places) not in excluded)


def law_knots(n, excluded, all_orders):
    out = []
    for t in itertools.combinations(range(n), 3):
        orders = set(itertools.permutations(t)) if all_orders else {t}
        for o in orders:
            out.append(knot_mask(n, o, excluded))
    return sorted(set(out))


def relations(n, masks, cap=None):
    full = (1 << (1 << n)) - 1
    seen, frontier = {full}, [full]
    while frontier:
        nxt = []
        for r in frontier:
            for m in masks:
                q = r & m
                if q and q not in seen:
                    seen.add(q)
                    nxt.append(q)
                    if cap and len(seen) > cap:
                        return None
        frontier = nxt
    return seen


def pair_key(n, r):
    sts = [s for s in range(1 << n) if r >> s & 1]
    singles = tuple(sum((s >> u) & 1 for s in sts) for u in range(n))
    pairs = tuple(sum(((s >> u) ^ (s >> v)) & 1 for s in sts) for u, v in itertools.combinations(range(n), 2))
    return (len(sts), singles, pairs)


def axis_correlation(width, law, rmax=24):
    """Connected (Pearson) correlation of distinction (0, 0) with (0, r) on the infinite cylinder of the given width,
    from the leading right and left eigenvectors of the row transfer matrix; dense, width <= 12."""
    T = sp.csr_matrix(transfer(width, law).astype(np.float64))
    v0 = np.ones(T.shape[0])
    vals, R = eigs(T, k=1, which="LM", tol=1e-13, maxiter=50000, v0=v0)
    valsL, Lv = eigs(T.T.tocsr(), k=1, which="LM", tol=1e-13, maxiter=50000, v0=v0)
    lam = vals[0].real
    r = np.abs(R[:, 0].real)
    l = np.abs(Lv[:, 0].real)
    norm = l @ r
    R0 = 1 << width
    x0 = ((np.arange(R0) >> 0) & 1).astype(np.float64)
    m = (l * x0) @ r / norm
    var = m * (1 - m)
    out = []
    v = x0 * r
    for d in range(1, rmax + 1):
        v = T @ v / lam
        both = (l * x0) @ v / norm
        out.append(float((both - m * m) / var) if var > 0 else None)
    return {"width": width, "mean": float(m), "correlation": out}
